"""Frozen fourteen-pair activation assessment; no product repair or live reruns."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys

from panda_agent import qa
from panda_agent.evaluation import (load_gold_dataset, load_product_language_calibration,
                                    calibration_compatibility, english_product_case_ids)

ROOT = Path(__file__).resolve().parents[1]
EV = ROOT / 'evaluation'
spec = importlib.util.spec_from_file_location('r3_r2_helpers', EV / 'run_e2_a3_r2_citation_eligibility_validation.py')
r2 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = r2
spec.loader.exec_module(r2)
a3, h = r2.a3, r2.h
PRODUCT = 'fd0aed4c7e491a569bf39271825cc0950630863d'
LEGACY, RUNTIME = a3.LEGACY, a3.RUNTIME
EXCLUDED = ['g013', 'g027', 'g112', 'g002', 'g044', 'g110']
MANIFEST = EV / 'e2_a3_r3_activation_manifest.json'
READINESS = EV / 'e2_a3_r3_activation_readiness.json'
RAW = EV / 'e2_a3_r3_activation_paired_raw.json'
JUDGED = EV / 'e2_a3_r3_activation_paired_judged.json'
RESULT = EV / 'e2_a3_r3_runtime_activation_result.json'
PREREG = EV / 'E2_A3_R3_RUNTIME_ACTIVATION_PREREGISTRATION.md'
GOLD = EV / 'benchmarks/v2_6/gold_questions.yaml'
GATES = dict(G1='14+14 QA and 14 authoritative judgments', G2='runtime_correct>=legacy_correct',
             G3=0, G4=0, G5=0, G6=0, G7='14 valid decompositions; answered applicable coverage complete',
             G8='runtime revisions<=1; legacy decomposition=0; postverify retrieval=0',
             G9=14, G10=0, G11=dict(worse_max=1, better_equivalent_min=13), G12=2.0,
             G13='product and compatibility unchanged; default legacy before verdict')
PRODUCT_PATHS = ['src', 'configs', 'prompts', 'schemas', 'corpus', 'data', 'index']
FROZEN = [*PRODUCT_PATHS, 'tests', 'AGENTS.md', 'evaluation/benchmarks/v2_6',
          a3.CAL.relative_to(ROOT).as_posix(),
          'evaluation/run_e2_a3_r3_runtime_activation.py',
          *['evaluation/' + p.name for p in (MANIFEST, READINESS, PREREG)],
          'evaluation/run_e2_a3_r2_citation_eligibility_validation.py',
          'evaluation/run_e2_a3_r1_targeted_revalidation.py',
          'evaluation/run_e2_a3_runtime_activation_regression.py',
          'evaluation/run_e2_a2_targeted_claim_mapping_validation.py']


def choose(pool):
    """Intent round-robin within status; answered selection precedes controls."""
    answered = a3.select_round_robin([c for c in pool if c.expected_status.value == 'answered'], len(pool))
    controls = a3.select_round_robin([c for c in pool if c.expected_status.value != 'answered'], len(pool))
    chosen = answered[:10] + controls[:4]
    chosen += (answered[10:] + controls[4:])[:max(0, 14-len(chosen))]
    return chosen, answered, controls


def cohort():
    dataset = load_gold_dataset(GOLD)
    approval = h.read(GOLD.with_name('benchmark_manifest.json'))
    h.require(approval['status'] == 'approved_exposed_development_benchmark_v2_6' and approval['benchmark_version'] == dataset.benchmark_version, 'Gold approval')
    cal = load_product_language_calibration(ROOT)
    h.require(cal and calibration_compatibility(cal, dataset)['compatible'], 'reviewed language calibration')
    # Carry forward the established A3 language-input identity check, without
    # invoking A3 source_cohorts (which also loads unrelated novel material).
    cal_commit = h.git('log', '-1', '--format=%H', '--', a3.CAL.relative_to(ROOT).as_posix())
    old = a3.yaml.safe_load(h.git('show', cal_commit + ':' + GOLD.relative_to(ROOT).as_posix()))
    current = a3.yaml.safe_load(GOLD.read_text(encoding='utf-8'))
    fields = ('id', 'query', 'language', 'split', 'review_status')
    h.require([{k: c.get(k) for k in fields} for c in old['questions']] == [{k: c.get(k) for k in fields} for c in current['questions']], 'reviewed language inputs changed')
    approved = set(english_product_case_ids(dataset, 'dev', cal))
    pool = [c for c in dataset.questions if c.id in approved - set(EXCLUDED)]
    selected, answered, controls = choose(pool)
    h.require(len(selected) == len({c.id for c in selected}) == 14, '14 unique approved cases required')
    cases = [dict(id=c.id, source='Gold', question=c.query, expected_status=c.expected_status.value,
                  intent=c.intent, split=c.split, gold=c.model_dump(mode='json')) for c in selected]
    accounting = dict(approved_english_dev=len(approved), approved_ids=sorted(approved), excluded_ids=EXCLUDED,
                      excluded_present=sorted(approved & set(EXCLUDED)), eligible_after_exclusion=len(pool),
                      answered_pool=len(answered), nonanswered_pool=len(controls),
                      answered_round_robin=[c.id for c in answered], nonanswered_round_robin=[c.id for c in controls],
                      selected_ids=[c.id for c in selected], expected_status_counts=dict(Counter(c.expected_status.value for c in selected)),
                      intent_distribution=dict(Counter(c.intent for c in selected)),
                      algorithm='sorted intent round-robin; IDs ascending within intent; first 10 answered then first 4 controls; fill shortage from remaining answered then controls',
                      prior_quality_outcomes_used=False, language_calibration=cal['calibration_id'],
                      dataset_version=dataset.benchmark_version, protected_access=0)
    return a3.canonical(cases), a3.canonical(accounting)


def order(cases):
    # Canonical JSON representation is used both before and after persistence.
    return a3.canonical([(eid, {**context, 'expected_status': cases[context['index']]['expected_status'],
                               'intent': cases[context['index']]['intent']}) for eid, context in a3.order(cases)])


def prepare(tests_passed):
    cases, accounting = cohort()
    manifest = dict(product_candidate_commit=PRODUCT, qa_cases=cases, selection=accounting,
                    order=order(cases), labels=[a3.labels(i) for i in range(14)], provider=asdict(h.settings()),
                    gates=GATES, judge_schema=a3.Judgment.model_json_schema(), judge_prompt=a3.JUDGE_PROMPT,
                    scientific_provider_calls_before_protocol_freeze=0, protected_access=0,
                    activation='PASS only; selector only; after committed result; no further live calls')
    h.save(MANIFEST, a3.canonical(manifest))
    no_product_delta = not h.git('diff', PRODUCT, '--', *PRODUCT_PATHS)
    h.git('merge-base', '--is-ancestor', PRODUCT, 'HEAD')
    gates = dict(F1=h.git('rev-parse', 'HEAD') == PRODUCT, F2=no_product_delta,
                 F3=len(cases) == 14 and not set(accounting['selected_ids']) & set(EXCLUDED),
                 F4=manifest['provider'] == asdict(h.settings()), F5=PREREG.exists() and manifest['gates'] == GATES,
                 F6=qa.DEFAULT_ANSWER_POINT_MODE == LEGACY, F7=no_product_delta,
                 F8=tests_passed > 0, F9=True, F10=not RAW.exists() and not JUDGED.exists())
    result = dict(product_candidate_commit=PRODUCT, gates=gates, focused_tests_passed=tests_passed,
                  selection=accounting, scientific_provider_calls_before_protocol_freeze=0, protected_access=0)
    h.save(READINESS, result)
    h.require(all(gates.values()), 'BLOCKED / PREREGISTRATION_OR_CANDIDATE_INTEGRITY_FAILURE')
    print(json.dumps(dict(readiness=gates, selection=accounting['selected_ids'])))


def validate(protocol):
    m = h.read(MANIFEST)
    cases, accounting = cohort()
    h.require(m['product_candidate_commit'] == PRODUCT, 'product identity')
    h.require(a3.canonical(m['qa_cases']) == cases and a3.canonical(m['selection']) == accounting, 'selection drift')
    h.require(a3.canonical(m['order']) == order(cases) and m['labels'] == [a3.labels(i) for i in range(14)], 'order/labels drift')
    h.require(m['provider'] == asdict(h.settings()) and m['gates'] == GATES, 'provider/gates drift')
    h.require(m['judge_schema'] == a3.Judgment.model_json_schema() and m['judge_prompt'] == a3.JUDGE_PROMPT, 'judge drift')
    h.require(qa.DEFAULT_ANSWER_POINT_MODE == LEGACY and not h.git('diff', PRODUCT, '--', *PRODUCT_PATHS), 'product/default drift')
    h.require(protocol and not h.git('diff', protocol, '--', *FROZEN), 'frozen protocol drift')
    h.require(h.committed(MANIFEST) == protocol and all(h.read(READINESS)['gates'].values()), 'protocol commit/readiness')
    h.git('merge-base', '--is-ancestor', PRODUCT, protocol)
    h.git('merge-base', '--is-ancestor', protocol, 'HEAD')
    return m


def citation_accounting(raw):
    invalid, errors, admissions = [], [], []
    for r in raw:
        if not r.get('diagnostic'):
            continue
        selected = r['diagnostic']['diagnostics']['selected_evidence']
        evidence = {e['evidence_id']: e for e in selected}
        allowed = [e['evidence_id'] for e in r2.eligible(selected)]
        captured = r.get('admissions', [])
        if len(captured) != sum(e['stage'] in ('qa_answer', 'qa_revision') for e in r.get('usage', [])):
            admissions.append(r['execution_id'] + ':missing capture')
        for item in captured:
            aux = [eid for ids in item['requirement_evidence_ids'].values() for eid in ids]
            if item['evidence_ids'] != allowed or not set(aux) <= set(allowed):
                admissions.append(r['execution_id'] + ':projection mismatch')
        for event in r.get('usage', []):
            if event['stage'] not in ('qa_answer', 'qa_revision'):
                continue
            for c in event.get('response', {}).get('claims', []):
                if qa._internal_claim_reason(c):
                    continue
                for eid in c.get('evidence_ids', []):
                    if eid in evidence and not qa._is_public_claim_citation_eligible(evidence[eid]):
                        invalid.append(dict(execution_id=r['execution_id'], stage=event['stage'], claim_id=c['claim_id'], evidence_id=eid))
        errors.extend(dict(execution_id=r['execution_id'], error=e) for review in r.get('reviews', []) for e in review.get('errors', []) if 'incomplete web citation' in e.lower())
    return invalid, errors, admissions


def score(m, raw, judged, readiness):
    # Reuse numerical accounting, not historical R1 gates or sentinel decisions.
    base = r2.r1.score(m, raw, judged, {'gates': {f'S{i}': True for i in range(1, 13)}})
    rows, counts = base['per_case'], Counter(base['counts'])
    js = {j['execution_id']: j for j in judged}
    cases = {c['id']: c for c in m['qa_cases']}
    by_record = {(r['case_id'], r['mode']): r for r in raw}
    for row in rows:
        if not row['scoreable']:
            continue
        i = [c['id'] for c in m['qa_cases']].index(row['id'])
        j = a3.validated_judge(js[row['id']]['judgment'])
        for label, mode in a3.labels(i).items():
            arm = 'legacy' if mode == LEGACY else 'runtime'
            row[arm + '_supported'] = j[label + '_supported']
            counts[arm + '_supported'] += j[label + '_supported']
        row['expected_status'] = cases[row['id']]['expected_status']
        row['coverage_applicable'] = row['expected_status'] == row['runtime_status'] == 'answered'
        row['judge_reason'] = j['reason']
        row['critical_runtime_regression'] = row['quality'] == 'worse' and j['critical_regression']
        row['legacy_generation_calls'] = a3.generation_calls(by_record[(row['id'], LEGACY)])
        row['runtime_generation_calls'] = a3.generation_calls(by_record[(row['id'], RUNTIME)])
    good = [r for r in rows if r['scoreable']]
    applicable = [r for r in good if r['coverage_applicable']]
    invalid, web_errors, admission_errors = citation_accounting(raw)
    violations = base['zero_tolerance_violations']
    unknown_points = [r['id'] for r in good if 'unknown_answer_point' in r['runtime_integrity']]
    gates = dict(G1=len(raw) == 28 and len(judged) == 14 and len(good) == 14,
                 G2=bool(good) and counts['runtime_correct'] >= counts['legacy_correct'],
                 G3=not counts['new_false_answer'], G4=not counts['new_false_refusal'],
                 G5=all(not r['new_integrity'] for r in good),
                 G6=not invalid and not web_errors and not admission_errors,
                 G7=len(good) == 14 and all(r['runtime_decomposition_calls'] == 1 and r['decomposition_valid'] for r in good) and all(r['coverage_evaluable'] and r['coverage_complete'] and not r['structural_review'] and not {'unknown_answer_point', 'structural_review'} & set(r['runtime_integrity']) for r in applicable),
                 G8=all(r['legacy_decomposition_calls'] == 0 and r['runtime_revision_count'] is not None and r['runtime_revision_count'] <= 1 for r in good) and all(a3.post_verify_retrieval(r) == 0 for r in raw),
                 G9=counts['runtime_supported'] == 14, G10=not counts['critical_runtime_regressions'],
                 G11=counts['worse'] <= 1 and counts['better'] + counts['equivalent'] >= 13,
                 G12=base['mean_additional_generation_calls'] is not None and base['mean_additional_generation_calls'] <= 2,
                 G13=all(readiness['gates'][k] for k in ('F1', 'F2', 'F6', 'F7')))
    # A missing judge cannot erase an independently observable product failure.
    observed_failures = list(violations)
    if invalid or web_errors or admission_errors:
        observed_failures.append('CITATION_ADMISSION_OR_WEB_INTEGRITY')
    for cid, case in cases.items():
        l, r = by_record.get((cid, LEGACY), {}), by_record.get((cid, RUNTIME), {})
        if not all(x.get('diagnostic') and not x.get('error') for x in (l, r)):
            continue
        ls, rs = l['diagnostic']['result']['status'], r['diagnostic']['result']['status']
        if set(a3.integrity(r)) - set(a3.integrity(l)):
            observed_failures.append(cid + ':NEW_RUNTIME_INTEGRITY')
        if (case['expected_status'] == 'answered' and ls == 'answered' and rs != 'answered') or (case['expected_status'] != 'answered' and ls != 'answered' and rs == 'answered'):
            observed_failures.append(cid + ':NEW_STATUS_ERROR')
    if any(not row['runtime_supported'] for row in good):
        observed_failures.append('UNSUPPORTED_RUNTIME')
    if counts['critical_runtime_regressions'] or counts['worse'] > 1:
        observed_failures.append('OBSERVED_QUALITY_FAILURE')
    verdict = 'FAIL' if observed_failures else 'INCONCLUSIVE' if not gates['G1'] else 'PASS' if all(gates.values()) and all(readiness['gates'].values()) else 'FAIL'
    # Explicit zeros are useful in final reporting without weakening any gate.
    for k in ('worse', 'better', 'equivalent', 'new_false_answer', 'new_false_refusal', 'critical_runtime_regressions', 'legacy_supported', 'runtime_supported'):
        counts[k] += 0
    return a3.canonical(dict(verdict=verdict, gates=gates, readiness_gates=readiness['gates'], counts=dict(counts),
                            per_case=rows, invalid_sphinx_claim_edges=invalid, incomplete_web_review_errors=web_errors,
                            admission_errors=admission_errors, runtime_unknown_point_cases=unknown_points,
                            zero_tolerance_violations=violations, observed_product_failures=observed_failures, coverage_applicable_count=len(applicable),
                            overhead_numerator=base['overhead_numerator'], overhead_denominator=base['overhead_denominator'],
                            mean_additional_generation_calls=base['mean_additional_generation_calls'],
                            legacy_generation_calls=sum(a3.generation_calls(r) for r in raw if r['mode'] == LEGACY),
                            runtime_generation_calls=sum(a3.generation_calls(r) for r in raw if r['mode'] == RUNTIME),
                            usage=base['usage'], latency={mode: a3.latency([r['diagnostic']['node_timings_ms']['workflow'] for r in raw if r['mode'] == mode and r.get('diagnostic')]) for mode in (LEGACY, RUNTIME)},
                            scientific_provider_calls_before_protocol_freeze=0, embedding_tokens='unavailable',
                            product_candidate_commit=PRODUCT, historical_failures_preserved=True, P6_waiver_granted=False,
                            post_freeze_repair_performed=False, activation_at_scientific_result=False))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('phase', choices=['prepare', 'paired', 'judge', 'score'])
    p.add_argument('--protocol')
    p.add_argument('--tests-passed', type=int, default=0)
    args = p.parse_args()
    if args.phase == 'prepare':
        prepare(args.tests_passed)
        return
    m = validate(args.protocol)
    cs = m['qa_cases']
    meta = dict(product_candidate_commit=PRODUCT, protocol_commit=args.protocol)
    target = RAW if args.phase == 'paired' else JUDGED
    if args.phase in ('paired', 'judge') and target.exists():
        prior = h.read(target)
        h.require(all(prior.get(k) == v for k, v in meta.items()), 'persisted identity mismatch')
    if args.phase == 'paired':
        def execute(r):
            v = r2.Meter(h.settings())
            agent = None
            try:
                agent = a3.Capture(ROOT, vertex=v)
                r['diagnostic'] = agent._run_detailed(r['question'], mode=r['mode'])
            except ValueError as exc:
                if v.events and 'response' in v.events[-1] and not v.events[-1].get('error'):
                    r['product_violation'] = str(exc)
                raise
            finally:
                r['usage'], r['admissions'] = v.events, v.admissions
                if agent:
                    r['trace'], r['reviews'] = agent.trace, agent.review_records
        h.run_records(RAW, meta, order(cs), execute)
    elif args.phase == 'judge':
        rc = h.committed(RAW)
        raw = h.read(RAW)
        h.require(all(raw.get(k) == v for k, v in meta.items()) and [r['execution_id'] for r in raw['records']] == [x[0] for x in order(cs)], 'raw identity/order')
        pairs = defaultdict(dict)
        for r in raw['records']:
            pairs[r['case_id']][r['mode']] = r
        def execute(r):
            c = cs[r['index']]
            pair = pairs[c['id']]
            h.require(len(pair) == 2 and all(v.get('diagnostic') and not v.get('error') for v in pair.values()), 'unscoreable raw pair; no judge call')
            v = a3.Meter(h.settings().for_generation_model(h.settings().evaluation_judge_model), judge=True)
            r['input'] = a3.judge_input(c, pair, r['index'])
            try:
                r['judgment'] = a3.validated_judge(v.generate_json(json.dumps(r['input'], ensure_ascii=False), a3.Judgment.model_json_schema(), system_instruction=a3.JUDGE_PROMPT, temperature=0))
            finally:
                r['usage'] = v.events
        h.run_records(JUDGED, {**meta, 'raw_commit': rc}, [(c['id'], dict(index=i)) for i, c in enumerate(cs)], execute)
    else:
        rc, jc = h.committed(RAW), h.committed(JUDGED)
        raw, judged = h.read(RAW), h.read(JUDGED)
        h.require(all(raw.get(k) == judged.get(k) == v for k, v in meta.items()) and judged['raw_commit'] == rc, 'science identity')
        h.require([r['execution_id'] for r in raw['records']] == [x[0] for x in order(cs)], 'raw identity/order')
        h.require([r['execution_id'] for r in judged['records']] == [c['id'] for c in cs], 'judge identity/order')
        result = {**meta, 'raw_commit': rc, 'judged_commit': jc, **score(m, raw['records'], judged['records'], h.read(READINESS))}
        if RESULT.exists():
            h.require(h.read(RESULT) == result, 'canonical score mismatch')
        else:
            h.save(RESULT, result)
        print(json.dumps(dict(verdict=result['verdict'], gates=result['gates'])))


if __name__ == '__main__':
    main()
