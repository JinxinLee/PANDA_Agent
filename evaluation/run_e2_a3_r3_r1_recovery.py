"""Supplemental full-pair recovery with explicit fourteen-pair gate authority."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys

from panda_agent import qa

ROOT = Path(__file__).resolve().parents[1]
EV = ROOT / 'evaluation'
spec = importlib.util.spec_from_file_location('recovery_r3', EV / 'run_e2_a3_r3_runtime_activation.py')
r3 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = r3
spec.loader.exec_module(r3)
a3, h = r3.a3, r3.h
START = '29bc2864a95b797ecfc07d3824711c5dc855ff95'
PRODUCT = r3.PRODUCT
OLD_PROTOCOL = '0a276a40968ed67fb784c37676d172314fb1210d'
OLD_RAW = '6d760be1eae1e803d8f6c4ff6b374a13dbed4713'
OLD_JUDGED = '77388ec9c2564cce82d0db24ef97a15da62d4779'
RECOVER = ['g059', 'g047', 'g001']
CARRY = ['g028', 'g105', 'g113', 'g014', 'g060', 'g050', 'g029', 'g057', 'g041', 'g007', 'g108']
LEGACY, RUNTIME = r3.LEGACY, r3.RUNTIME
MANIFEST = EV / 'e2_a3_r3_r1_recovery_manifest.json'
READY = EV / 'e2_a3_r3_r1_recovery_readiness.json'
RAW = EV / 'e2_a3_r3_r1_recovery_paired_raw.json'
JUDGED = EV / 'e2_a3_r3_r1_recovery_paired_judged.json'
RESULT = EV / 'e2_a3_r3_r1_activation_completion_result.json'
PREREG = EV / 'E2_A3_R3_R1_INFRASTRUCTURE_RECOVERY_PREREGISTRATION.md'
HISTORICAL = [(OLD_PROTOCOL, r3.MANIFEST), (OLD_PROTOCOL, r3.PREREG),
              (OLD_RAW, r3.RAW), (OLD_JUDGED, r3.JUDGED), (START, r3.RESULT)]
FROZEN = list(dict.fromkeys([*r3.FROZEN, 'evaluation/run_e2_a3_r3_r1_recovery.py',
                            *[p.relative_to(ROOT).as_posix() for p in (MANIFEST, READY, PREREG)],
                            *[p.relative_to(ROOT).as_posix() for _, p in HISTORICAL]]))


def frozen_json(commit, path):
    return json.loads(h.git('show', commit + ':' + path.relative_to(ROOT).as_posix()))


def complete(record):
    return bool(record and record.get('state') == 'COMPLETE' and record.get('diagnostic') and not record.get('error'))


def judgment(record):
    if not record or record.get('state') != 'COMPLETE' or record.get('error'):
        return None
    try:
        return a3.validated_judge(record['judgment'])
    except (KeyError, ValueError):
        return None


def history():
    manifest = frozen_json(OLD_PROTOCOL, r3.MANIFEST)
    raw = frozen_json(OLD_RAW, r3.RAW)
    judges = frozen_json(OLD_JUDGED, r3.JUDGED)
    result = frozen_json(START, r3.RESULT)
    h.require(raw['product_candidate_commit'] == manifest['product_candidate_commit'] == PRODUCT, 'historical product')
    h.require(raw['protocol_commit'] == judges['protocol_commit'] == OLD_PROTOCOL and judges['raw_commit'] == OLD_RAW, 'historical chain')
    h.require(result['verdict'] == 'INCONCLUSIVE' and result['raw_commit'] == OLD_RAW and result['judged_commit'] == OLD_JUDGED, 'historical result')
    pairs = defaultdict(dict)
    for record in raw['records']:
        pairs[record['case_id']][record['mode']] = record
    js = {r['execution_id']: r for r in judges['records']}
    incomplete = []
    carried = []
    for case in manifest['qa_cases']:
        pair = pairs[case['id']]
        if len(pair) == 2 and all(complete(r) for r in pair.values()) and judgment(js.get(case['id'])):
            carried.append(case['id'])
        else:
            incomplete.append(case['id'])
    h.require(incomplete == RECOVER and carried == CARRY, 'infrastructure-only recovery/cohort identity')
    failures = [(r['case_id'], r['mode'], r.get('error', '')) for r in raw['records'] if r.get('error')]
    expected = {('g059', LEGACY): 'ConnectionTimeout', ('g059', RUNTIME): 'ConnectionTimeout',
                ('g047', RUNTIME): 'ConnectionTimeout', ('g001', LEGACY): '429 RESOURCE_EXHAUSTED'}
    h.require(len(failures) == 4 and all((cid, mode) in expected and expected[(cid, mode)] in error for cid, mode, error in failures), 'not exclusively approved infrastructure failures')
    h.require(all(not judgment(js.get(cid)) for cid in RECOVER), 'recovery would replace an authoritative judgment')
    return manifest, raw, judges, result


def recovery_order(old_manifest):
    return a3.canonical([(eid, {**context, 'original_r3_index': context['index']})
                         for eid, context in old_manifest['order'] if context['case_id'] in RECOVER])


def historical_unchanged():
    return all(not h.git('diff', commit, '--', path.relative_to(ROOT).as_posix()) for commit, path in HISTORICAL)


def prepare(tests_passed):
    old, raw, judges, _ = history()
    indices = {c['id']: i for i, c in enumerate(old['qa_cases'])}
    m = dict(starting_head=START, product_candidate_commit=PRODUCT, original_protocol_commit=OLD_PROTOCOL,
             original_raw_commit=OLD_RAW, original_judged_commit=OLD_JUDGED, original_result_commit=START,
             recovery_ids=RECOVER, carried_ids=CARRY, qa_cases=[c for c in old['qa_cases'] if c['id'] in RECOVER],
             order=recovery_order(old), labels={cid: old['labels'][indices[cid]] for cid in RECOVER},
             provider=old['provider'], gates=old['gates'], judge_schema=old['judge_schema'], judge_prompt=old['judge_prompt'],
             composition='original complete R3 pair and judgment for carried IDs; ONLY fresh recovery pair and judgment for recovery IDs; preserve original fourteen-case order',
             gate_states=['PASS', 'FAIL', 'NOT_EVALUABLE'], scientific_provider_calls_before_protocol_freeze=0,
             protected_access=0, activation='committed combined PASS only; selector only; no subsequent live calls')
    no_delta = not h.git('diff', PRODUCT, '--', *r3.PRODUCT_PATHS)
    gates = {'R-F1': no_delta, 'R-F2': historical_unchanged(), 'R-F3': [c['id'] for c in m['qa_cases']] == RECOVER,
             'R-F4': True, 'R-F5': True, 'R-F6': asdict(h.settings()) == old['provider'],
             'R-F7': old['gates'] == r3.GATES and old['judge_prompt'] == a3.JUDGE_PROMPT and old['judge_schema'] == a3.Judgment.model_json_schema(),
             'R-F8': qa.DEFAULT_ANSWER_POINT_MODE == LEGACY, 'R-F9': tests_passed > 0,
             'R-F10': True, 'R-F11': not RAW.exists() and not JUDGED.exists()}
    h.require(h.git('rev-parse', 'HEAD') == START, 'starting identity')
    h.save(MANIFEST, a3.canonical(m))
    h.save(READY, dict(gates=gates, starting_head=START, product_candidate_commit=PRODUCT,
                       focused_tests_passed=tests_passed, protected_access=0, scientific_provider_calls_before_protocol_freeze=0))
    h.require(PREREG.exists() and all(gates.values()), 'BLOCKED / RECOVERY_READINESS_FAILURE')
    print(json.dumps(gates))


def validate(protocol):
    old, _, _, _ = history()
    m = h.read(MANIFEST)
    h.require(m['starting_head'] == START and m['product_candidate_commit'] == PRODUCT, 'candidate identity')
    h.require(m['recovery_ids'] == RECOVER and m['carried_ids'] == CARRY, 'composition drift')
    h.require(m['qa_cases'] == [c for c in old['qa_cases'] if c['id'] in RECOVER] and a3.canonical(m['order']) == recovery_order(old), 'case/order drift')
    h.require(m['labels'] == {c['id']: old['labels'][i] for i, c in enumerate(old['qa_cases']) if c['id'] in RECOVER}, 'blind mapping drift')
    h.require(m['provider'] == old['provider'] == asdict(h.settings()) and m['gates'] == old['gates'] == r3.GATES, 'provider/gate drift')
    h.require(m['judge_schema'] == old['judge_schema'] == a3.Judgment.model_json_schema() and m['judge_prompt'] == old['judge_prompt'] == a3.JUDGE_PROMPT, 'judge drift')
    h.require(historical_unchanged() and not h.git('diff', PRODUCT, '--', *r3.PRODUCT_PATHS), 'BLOCKED / PRODUCT_CANDIDATE_DRIFT')
    h.require(qa.DEFAULT_ANSWER_POINT_MODE == LEGACY, 'activation before verdict')
    h.require(protocol and h.committed(MANIFEST) == protocol and not h.git('diff', protocol, '--', *FROZEN), 'protocol identity/drift')
    h.git('merge-base', '--is-ancestor', protocol, 'HEAD')
    h.require(all(h.read(READY)['gates'].values()), 'readiness incomplete')
    return m, old


class Capture(a3.Capture):
    """Keep evaluator-only citation context even if generation terminally fails."""
    def __init__(self, *args, **kwargs):
        self.selected_snapshot = None
        super().__init__(*args, **kwargs)

    def _answer(self, state):
        self.selected_snapshot = deepcopy(state['bundle']['evidence'])
        return super()._answer(state)

    def _revise(self, state):
        self.selected_snapshot = deepcopy(state['bundle']['evidence'])
        return super()._revise(state)


def compose(old_manifest, old_raw, old_judged, recovery_raw, recovery_judged, raw_commit, judged_commit):
    combined_raw, combined_judged, provenance = [], [], []
    for case in old_manifest['qa_cases']:
        cid = case['id']
        recover = cid in RECOVER
        source_raw = recovery_raw if recover else old_raw
        source_judged = recovery_judged if recover else old_judged
        chosen = [r for r in source_raw if r['case_id'] == cid]
        h.require(len({r['mode'] for r in chosen}) == len(chosen) and all(r['mode'] in (LEGACY, RUNTIME) for r in chosen), 'duplicate/invalid arm')
        by_mode = {r['mode']: r for r in chosen}
        for _, context in old_manifest['order']:
            if context['case_id'] == cid and context['mode'] in by_mode:
                combined_raw.append(deepcopy(by_mode[context['mode']]))
        js = [j for j in source_judged if j['execution_id'] == cid]
        h.require(len(js) <= 1, 'duplicate judgment')
        combined_judged.extend(deepcopy(js))
        provenance.append(dict(case_id=cid, authority_source='r3_r1_recovery' if recover else 'original_r3',
                               raw_commit=raw_commit if recover else OLD_RAW,
                               judged_commit=judged_commit if recover else OLD_JUDGED,
                               execution_ids=[r['execution_id'] for r in chosen]))
    return combined_raw, combined_judged, provenance


def citation(record):
    diagnostic = record.get('diagnostic') or {}
    items = diagnostic.get('diagnostics', {}).get('selected_evidence', record.get('selected_evidence_snapshot'))
    events = [e for e in record.get('usage', []) if e['stage'] in ('qa_answer', 'qa_revision')]
    admissions = record.get('admissions', [])
    errors = [e for review in record.get('reviews', []) for e in review.get('errors', []) if 'incomplete web citation' in e.lower()]
    bad, mismatches = [], []
    evidence = {e['evidence_id']: e for e in items or []}
    allowed = [e['evidence_id'] for e in r3.r2.eligible(items or [])]
    context_available = items is not None or not events
    for event in events:
        for claim in event.get('response', {}).get('claims', []):
            if qa._internal_claim_reason(claim):
                continue
            for eid in claim.get('evidence_ids', []):
                if eid in evidence and not qa._is_public_claim_citation_eligible(evidence[eid]):
                    bad.append(dict(claim_id=claim['claim_id'], evidence_id=eid, stage=event['stage']))
    if context_available:
        for admission in admissions:
            auxiliary = [eid for ids in admission['requirement_evidence_ids'].values() for eid in ids]
            if admission['evidence_ids'] != allowed or not set(auxiliary) <= set(allowed):
                mismatches.append(admission['task'])
    authority = complete(record) and context_available and 'reviews' in record and 'admissions' in record and len(events) == len(admissions) and all('response' in e and not e.get('error') for e in events)
    return dict(authority_complete=authority, invalid_edges=bad, incomplete_web_errors=errors, admission_mismatches=mismatches)


def score(manifest, raw, judged, readiness, provenance):
    pairs = defaultdict(dict)
    for r in raw:
        pairs[r['case_id']][r['mode']] = r
    js = {j['execution_id']: j for j in judged}
    counts = Counter()
    rows, violations = [], []
    for i, case in enumerate(manifest['qa_cases']):
        cid = case['id']
        pair = pairs[cid]
        l, r = pair.get(LEGACY, {}), pair.get(RUNTIME, {})
        lc, rc = complete(l), complete(r)
        j = judgment(js.get(cid))
        row = dict(case_id=cid, expected_status=case['expected_status'], legacy_complete=lc,
                   runtime_complete=rc, judgment_authoritative=j is not None, pair_complete=lc and rc,
                   legacy_status=(l.get('diagnostic') or {}).get('result', {}).get('status'),
                   runtime_status=(r.get('diagnostic') or {}).get('result', {}).get('status'),
                   citations={mode: citation(pair.get(mode, {})) for mode in (LEGACY, RUNTIME)})
        counts['legacy_complete'] += lc
        counts['runtime_complete'] += rc
        counts['judgments'] += j is not None
        counts['authoritative_pairs'] += lc and rc and j is not None
        counts['legacy_correct'] += lc and row['legacy_status'] == case['expected_status']
        counts['runtime_correct'] += rc and row['runtime_status'] == case['expected_status']
        row['new_false_answer'] = lc and rc and case['expected_status'] != 'answered' and row['runtime_status'] == 'answered' and row['legacy_status'] != 'answered'
        row['new_false_refusal'] = lc and rc and case['expected_status'] == 'answered' and row['runtime_status'] != 'answered' and row['legacy_status'] == 'answered'
        counts['new_false_answer'] += row['new_false_answer']
        counts['new_false_refusal'] += row['new_false_refusal']
        row['legacy_integrity'], row['runtime_integrity'] = a3.integrity(l), a3.integrity(r)
        row['new_integrity'] = sorted(set(row['runtime_integrity'])-set(row['legacy_integrity'])) if lc and rc else None
        diag = (r.get('diagnostic') or {}).get('diagnostics', {})
        points = diag.get('question_decomposition', {}).get('points', [])
        audit = diag.get('answer_point_audit') or {}
        row.update(runtime_decomposition_calls=a3.decom_calls(r), legacy_decomposition_calls=a3.decom_calls(l),
                   decomposition_valid=bool(points) and len(points) <= 5 and [p.get('answer_point_id') for p in points] == [f'point.{n+1}' for n in range(len(points))] and all(isinstance(p.get('text'), str) and p['text'].strip() for p in points),
                   coverage_applicable=rc and case['expected_status'] == row['runtime_status'] == 'answered',
                   coverage_evaluable=audit.get('coverage_evaluable') is True, coverage_complete=audit.get('coverage_complete') is True,
                   structural_review=any((review.get('audit') or {}).get('review_error') for review in r.get('reviews', [])),
                   runtime_revision_count=diag.get('revision_count'), post_verify_retrieval=sum(a3.post_verify_retrieval(x) for x in (l, r)),
                   legacy_generation_calls=a3.generation_calls(l), runtime_generation_calls=a3.generation_calls(r))
        row['additional_generation_calls'] = row['runtime_generation_calls'] - row['legacy_generation_calls'] if lc and rc else None
        row['runtime_coverage_failure'] = rc and (row['runtime_decomposition_calls'] != 1 or not row['decomposition_valid'] or (row['coverage_applicable'] and (not row['coverage_evaluable'] or not row['coverage_complete'] or row['structural_review'] or bool({'unknown_answer_point','structural_review'} & set(row['runtime_integrity'])))))
        row['runtime_boundary_failure'] = row['legacy_decomposition_calls'] != 0 or row['post_verify_retrieval'] != 0 or (row['runtime_revision_count'] is not None and row['runtime_revision_count'] > 1)
        if j:
            quality = 'equivalent' if j['preferred'] == 'equivalent' else 'better' if manifest['labels'][i][j['preferred']] == RUNTIME else 'worse'
            support = {mode: j[label + '_supported'] for label, mode in manifest['labels'][i].items()}
            row.update(quality=quality, legacy_supported=support[LEGACY], runtime_supported=support[RUNTIME],
                       critical_runtime_regression=quality == 'worse' and j['critical_regression'], judge_reason=j['reason'])
            counts[quality] += 1
            counts['legacy_supported'] += support[LEGACY]
            counts['runtime_supported'] += support[RUNTIME]
            counts['critical_runtime_regressions'] += row['critical_runtime_regression']
        for record in (l, r):
            if record.get('product_violation'):
                violations.append(cid + ':PRODUCT_CONTRACT:' + record['product_violation'])
            d = record.get('diagnostic') or {}
            if d:
                try:
                    qa.QAResult.model_validate(d['result'])
                except Exception:
                    violations.append(cid + ':PUBLIC_DTO')
            audits = [v.get('audit') for v in record.get('reviews', [])] + [d.get('diagnostics', {}).get('answer_point_audit')]
            for audit_item in filter(None, audits):
                known = {p['answer_point_id'] for p in audit_item.get('answer_points', [])}
                accepted = set(audit_item.get('covered_answer_point_ids', [])) | set(audit_item.get('missing_answer_point_ids', []))
                accepted |= {p for x in audit_item.get('claim_mappings', []) for p in x.get('verified_answer_point_ids', [])}
                if not accepted <= known:
                    violations.append(cid + ':UNKNOWN_POINT_ACCEPTED')
                if any(x.get('supported') and qa._internal_claim_reason(x) for x in audit_item.get('claim_mappings', [])):
                    violations.append(cid + ':INTERNAL_CLAIM_CREDITED')
        rows.append(row)
    all_qa = counts['legacy_complete'] == counts['runtime_complete'] == 14
    all_judged = counts['judgments'] == 14
    full = all_qa and all_judged and counts['authoritative_pairs'] == 14
    all_reviews = all(r['pair_complete'] and all('reviews' in pairs[r['case_id']][mode] for mode in (LEGACY, RUNTIME)) for r in rows)
    all_citations = all(c['authority_complete'] for row in rows for c in row['citations'].values())
    numerator = sum(row['additional_generation_calls'] for row in rows) if all_qa else None
    mean = numerator / 14 if numerator is not None else None
    def gate(authority, failure):
        return dict(state='FAIL' if failure else 'PASS' if authority else 'NOT_EVALUABLE',
                    authority_complete=bool(authority), observed_violation=bool(failure))
    gates = dict(
        G1=gate(full, False),
        G2=gate(all_qa, all_qa and counts['runtime_correct'] < counts['legacy_correct']),
        G3=gate(all(row['pair_complete'] for row in rows if row['expected_status'] != 'answered'), counts['new_false_answer'] > 0),
        G4=gate(all(row['pair_complete'] for row in rows if row['expected_status'] == 'answered'), counts['new_false_refusal'] > 0),
        G5=gate(all_reviews, any(row['new_integrity'] for row in rows)),
        G6=gate(all_citations, any(c['invalid_edges'] or c['incomplete_web_errors'] or c['admission_mismatches'] for row in rows for c in row['citations'].values())),
        G7=gate(counts['runtime_complete'] == 14, any(row['runtime_coverage_failure'] for row in rows)),
        G8=gate(all_qa and all('trace' in record and 'usage' in record for record in raw), any(row['runtime_boundary_failure'] for row in rows)),
        G9=gate(all_judged, any(row.get('runtime_supported') is False for row in rows)),
        G10=gate(all_judged, counts['critical_runtime_regressions'] > 0),
        G11=gate(all_judged, counts['worse'] > 1 or (all_judged and counts['better'] + counts['equivalent'] < 13)),
        G12=gate(all_qa, mean is not None and mean > 2),
        G13=gate(all(readiness['gates'].values()), not all(readiness['gates'].values())),
    )
    verdict = 'FAIL' if violations or any(g['state'] == 'FAIL' for g in gates.values()) else 'INCONCLUSIVE' if not full or any(g['state'] == 'NOT_EVALUABLE' for g in gates.values()) else 'PASS'
    for key in ('better','equivalent','worse','legacy_supported','runtime_supported','new_false_answer','new_false_refusal','critical_runtime_regressions'):
        counts[key] += 0
    return a3.canonical(dict(verdict=verdict, gates=gates, counts=dict(counts), pair_provenance=provenance,
                            per_case=rows, zero_tolerance_violations=sorted(set(violations)),
                            authoritative_legacy_generation_calls=sum(row['legacy_generation_calls'] for row in rows) if all_qa else None,
                            authoritative_runtime_generation_calls=sum(row['runtime_generation_calls'] for row in rows) if all_qa else None,
                            overhead_numerator=numerator, overhead_denominator=14, mean_additional_generation_calls=mean,
                            combined_selected_usage={arm: h.usage_sum([r for r in raw if r['mode'] == mode]) for arm, mode in [('legacy',LEGACY),('runtime',RUNTIME)]} | {'judge':h.usage_sum(judged)},
                            combined_usage_authority_complete=full,
                            historical_r3_remains_inconclusive=True, historical_A3_R1_failures_preserved=True,
                            P6_waiver=False, product_repair=False, activation_before_result=False))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('phase', choices=['prepare', 'paired', 'judge', 'score'])
    p.add_argument('--protocol')
    p.add_argument('--tests-passed', type=int, default=0)
    args = p.parse_args()
    if args.phase == 'prepare':
        prepare(args.tests_passed)
        return
    m, old = validate(args.protocol)
    meta = dict(starting_head=START, product_candidate_commit=PRODUCT, protocol_commit=args.protocol)
    target = RAW if args.phase == 'paired' else JUDGED
    if args.phase in ('paired','judge') and target.exists():
        h.require(all(h.read(target).get(k) == v for k, v in meta.items()), 'persisted identity mismatch')
    if args.phase == 'paired':
        def execute(record):
            vertex = r3.r2.Meter(h.settings())
            agent = None
            try:
                agent = Capture(ROOT, vertex=vertex)
                record['diagnostic'] = agent._run_detailed(record['question'], mode=record['mode'])
            except ValueError as exc:
                if vertex.events and 'response' in vertex.events[-1] and not vertex.events[-1].get('error'):
                    record['product_violation'] = str(exc)
                raise
            finally:
                record['usage'], record['admissions'] = vertex.events, vertex.admissions
                if agent:
                    record['trace'], record['reviews'] = agent.trace, agent.review_records
                    record['selected_evidence_snapshot'] = agent.selected_snapshot
        h.run_records(RAW, meta, m['order'], execute)
    elif args.phase == 'judge':
        rc = h.committed(RAW)
        raw = h.read(RAW)
        h.require(all(raw.get(k) == v for k,v in meta.items()) and [r['execution_id'] for r in raw['records']] == [x[0] for x in m['order']], 'raw identity/order')
        pairs = defaultdict(dict)
        for r in raw['records']:
            pairs[r['case_id']][r['mode']] = r
        def execute(record):
            index = record['original_r3_index']
            case = old['qa_cases'][index]
            pair = pairs[case['id']]
            h.require(len(pair) == 2 and all(complete(r) for r in pair.values()), 'unscoreable recovery pair; no judge call')
            vertex = a3.Meter(h.settings().for_generation_model(h.settings().evaluation_judge_model), judge=True)
            record['input'] = a3.judge_input(case, pair, index)
            try:
                record['judgment'] = a3.validated_judge(vertex.generate_json(json.dumps(record['input'],ensure_ascii=False), a3.Judgment.model_json_schema(), system_instruction=a3.JUDGE_PROMPT, temperature=0))
            finally:
                record['usage'] = vertex.events
        work = [(c['id'],dict(original_r3_index=i)) for i,c in enumerate(old['qa_cases']) if c['id'] in RECOVER]
        h.run_records(JUDGED, {**meta,'raw_commit':rc}, work, execute)
    else:
        rc, jc = h.committed(RAW), h.committed(JUDGED)
        raw, judged = h.read(RAW), h.read(JUDGED)
        h.require(all(raw.get(k) == judged.get(k) == v for k,v in meta.items()) and judged['raw_commit'] == rc, 'scientific identity')
        h.require([r['execution_id'] for r in raw['records']] == [x[0] for x in m['order']] and [j['execution_id'] for j in judged['records']] == RECOVER, 'recovery identity/order')
        _, old_raw, old_judged, old_result = history()
        cr, cj, provenance = compose(old,old_raw['records'],old_judged['records'],raw['records'],judged['records'],rc,jc)
        result = {**meta,'raw_commit':rc,'judged_commit':jc,**score(old,cr,cj,h.read(READY),provenance),
                  'original_r3_historical_usage':old_result['usage'],
                  'original_failed_attempt_usage':h.usage_sum([r for r in old_raw['records'] if r.get('error')]),
                  'original_superseded_partial_pairs_usage':h.usage_sum([r for r in old_raw['records'] if r['case_id'] in RECOVER]),
                  'recovery_usage':{arm:h.usage_sum([r for r in raw['records'] if r['mode']==mode]) for arm,mode in [('legacy',LEGACY),('runtime',RUNTIME)]} | {'judge':h.usage_sum(judged['records'])},
                  'recovery_errors':[dict(execution_id=r['execution_id'],error=r['error']) for r in raw['records'] if r.get('error')],
                  'scientific_provider_calls_before_protocol_freeze':0,'embedding_tokens':'unavailable'}
        if RESULT.exists():
            h.require(h.read(RESULT) == result, 'canonical score mismatch')
        else:
            h.save(RESULT,result)
        print(json.dumps(dict(verdict=result['verdict'], gates={k:v['state'] for k,v in result['gates'].items()})))


if __name__ == '__main__':
    main()
