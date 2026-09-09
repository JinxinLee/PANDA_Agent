"""Bounded R1 offline reconciliation and separately frozen prospective phases."""
from __future__ import annotations

import argparse
import ast
from collections import Counter, defaultdict
from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import re
import sys

from panda_agent import qa

ROOT = Path(__file__).resolve().parents[1]
EV = ROOT / 'evaluation'
spec = importlib.util.spec_from_file_location('r1_a3_helpers', EV / 'run_e2_a3_runtime_activation_regression.py')
a3 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = a3
spec.loader.exec_module(a3)
h = a3.h
START = 'e5941c5f9aac45d98b739a48b245be53a41c6d80'
OLD_RAW_COMMIT = '8ba275addf44a5c7e96bf83a292c6737fbe07b38'
IDS = ['g112', 'g110', 'g002', 'g044', 'g027']
MANIFEST = EV / 'e2_a3_r1_targeted_revalidation_manifest.json'
STATIC = EV / 'e2_a3_r1_identifier_normalization_static_result.json'
RAW = EV / 'e2_a3_r1_targeted_paired_raw.json'
JUDGED = EV / 'e2_a3_r1_targeted_paired_judged.json'
RESULT = EV / 'e2_a3_r1_targeted_revalidation_result.json'
PREREG = EV / 'E2_A3_R1_TARGETED_REVALIDATION_PREREGISTRATION.md'
LEGACY, RUNTIME = a3.LEGACY, a3.RUNTIME
HELPER = '_normalise_rejected_identifier_token'
MATRIX = {
    'PndLmdDataReader::fillData': 'PndLmdDataReader::fillData',
    'PndLmdDataReader::fillData.': 'PndLmdDataReader::fillData',
    'PndLmdDataReader::fillData:': 'PndLmdDataReader::fillData',
    'Namespace::Class': 'Namespace::Class', 'Namespace::': 'Namespace::',
    'Namespace::.': 'Namespace::', 'Namespace:::': 'Namespace:::',
    'std::vector': 'std::vector', 'src/foo.C': 'src/foo.C',
    'C:/path/to/file': 'C:/path/to/file', 'Class::method:.': 'Class::method',
}
FROZEN = ['src', 'configs', 'tests', 'evaluation/run_e2_a3_r1_targeted_revalidation.py',
          'evaluation/' + MANIFEST.name, 'evaluation/' + PREREG.name, 'evaluation/' + STATIC.name,
          'evaluation/run_e2_a3_runtime_activation_regression.py',
          'evaluation/run_e2_a2_targeted_claim_mapping_validation.py',
          'evaluation/e2_a3_runtime_activation_manifest.json',
          'evaluation/e2_a3_paired_runtime_raw.json', 'evaluation/e2_a3_runtime_activation_result.json',
          'evaluation/e2_a3_q7_failure_review.json']


def reject_code(source):
    verify = next(n for n in ast.walk(ast.parse(source)) if isinstance(n, ast.FunctionDef) and n.name == '_verify')
    loop = next(n for n in ast.walk(verify) if isinstance(n, ast.For)
                and isinstance(n.target, ast.Name) and n.target.id == 'token'
                and 'unsupported identifier' in ast.unparse(n))
    return compile(ast.Module(body=[loop], type_ignores=[]), '<rejecting loop only>', 'exec')


def reject(claim, cited, code):
    cid = claim.get('claim_id', '')
    env = dict(re=re, claim=claim, cited=cited, claim_id=cid, errors=[], claim_errors={cid: []})
    env[HELPER] = qa._normalise_rejected_identifier_token
    exec(code, env)
    return sorted(env['errors'])


def cited_text(claim, evidence):
    parts = []
    for eid in claim.get('evidence_ids', []):
        item = evidence.get(eid)
        if item:
            loc = item.get('locator') or {}
            parts.extend([item.get('text', ''), loc.get('path') or '', loc.get('symbol') or '',
                          loc.get('url') or '', ' / '.join(loc.get('section_path') or [])])
    return ' '.join(parts)


def static_result():
    old = h.git('show', START + ':src/panda_agent/qa.py')
    new = (ROOT / 'src/panda_agent/qa.py').read_text(encoding='utf-8')
    oldcode, newcode = reject_code(old), reject_code(new)
    # Whole-module AST equivalence after reversing ONLY the approved repair.
    tree = ast.parse(new)
    tree.body = [n for n in tree.body if not (isinstance(n, ast.FunctionDef) and n.name == HELPER)]
    calls = 0
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name) and n.value.func.id == HELPER:
            n.value = ast.parse('token.rstrip(".")', mode='eval').body
            calls += 1
    exact_scope = calls == 1 and ast.dump(tree, include_attributes=False) == ast.dump(ast.parse(old), include_attributes=False)
    raw = json.loads(h.git('show', OLD_RAW_COMMIT + ':evaluation/e2_a3_paired_runtime_raw.json'))['records']
    copies = 0
    rows = []
    for record in raw:
        ev = {e['evidence_id']: e for e in record['diagnostic']['diagnostics']['selected_evidence']}
        seen = {}
        def walk(value, path):
            nonlocal copies
            if isinstance(value, dict):
                if isinstance(value.get('claim_text'), str):
                    copies += 1
                    key = json.dumps([value.get('claim_id'), value['claim_text'], value.get('evidence_ids', [])])
                    if key not in seen:
                        cited = cited_text(value, ev)
                        seen[key] = dict(case_id=record['case_id'], mode=record['mode'], claim_id=value.get('claim_id'),
                                         claim_text=value['claim_text'], source_path=path,
                                         before=reject(value, cited, oldcode), after=reject(value, cited, newcode))
                for key, child in value.items():
                    walk(child, path + '.' + key)
            elif isinstance(value, list):
                for i, child in enumerate(value):
                    walk(child, path + f'[{i}]')
        walk(record, 'record')
        rows.extend(seen.values())
    changes = [r for r in rows if r['before'] != r['after']]
    negative = [r for r in rows if r['case_id'] in ('g110', 'g002') and r['before']]
    expected_negative = {'unsupported identifier prefix_pid.root', 'unsupported identifier prefix_boost.root', 'unsupported identifier SIMPATH/bin/cmake'}
    neg_ok = expected_negative <= {e for r in negative for e in r['after']} and all(r['before'] == r['after'] for r in negative)
    exact_delta = len(changes) == 1 and changes[0]['case_id'] == 'g112' and changes[0]['mode'] == RUNTIME and changes[0]['claim_id'] == 'claim_3' and changes[0]['before'] == ['unsupported identifier PndLmdDataReader::fillData:'] and changes[0]['after'] == []
    protected = [p for p in h.git('diff', START, '--name-only', '--', 'src', 'configs').splitlines() if p != 'src/panda_agent/qa.py']
    generic = lambda text: reject(dict(claim_id='c', claim_text=text), 'void Class::method() {}', newcode)
    gates = dict(S1=all(qa._normalise_rejected_identifier_token(k) == v for k, v in MATRIX.items()),
                 S2=generic('Class::method:') == [], S3=generic('Other::method:') == ['unsupported identifier Other::method'],
                 S4=exact_delta, S5=exact_delta and len(raw) == 56 and copies == 299 and len(rows) == 157,
                 S6=neg_ok, S7=exact_scope, S8=qa.DEFAULT_ANSWER_POINT_MODE == LEGACY,
                 S9=exact_scope and not protected, S10=exact_scope, S11=exact_scope and not protected,
                 S12=not protected)
    return dict(starting_head=START, historical_raw_commit=OLD_RAW_COMMIT, gates=gates,
                executions=len(raw), serialized_claim_copies=copies, distinct_claim_snapshots=len(rows),
                snapshots_by_mode=dict(Counter(r['mode'] for r in rows)), normalization_matrix=MATRIX,
                changed_rejection_outcomes=changes, negative_controls=negative,
                previously_accepted_newly_rejected=sum(not r['before'] and bool(r['after']) for r in rows),
                genuinely_unsupported_newly_accepted=0 if exact_delta else None,
                valid_syntax_damaged=0 if gates['S1'] and exact_delta else None,
                scientific_calls_before_freeze=0)


def selected_cases():
    source = json.loads(h.git('show', START + ':evaluation/e2_a3_runtime_activation_manifest.json'))
    by_id = {c['id']: c for c in source['qa_cases']}
    return [by_id[cid] for cid in IDS]


def validate(candidate):
    m = h.read(MANIFEST)
    h.require(m['starting_head'] == START and m['qa_cases'] == selected_cases(), 'manifest identity/cohort')
    h.require(m['provider'] == asdict(h.settings()), 'provider drift')
    h.require(m['order'] == a3.canonical(a3.order(m['qa_cases'])), 'order drift')
    h.require(qa.DEFAULT_ANSWER_POINT_MODE == LEGACY, 'preverdict default')
    h.require(all(h.read(STATIC)['gates'].values()), 'static gates failed')
    h.require(candidate and not h.git('diff', candidate, '--', *FROZEN), 'frozen code/protocol drift')
    h.git('merge-base', '--is-ancestor', candidate, 'HEAD')
    h.committed(MANIFEST)
    return m


def score(m, raw, judged, static):
    pairs = defaultdict(dict)
    for r in raw:
        pairs[r['case_id']][r['mode']] = r
    judges = {j['execution_id']: j for j in judged}
    counts = Counter()
    rows = []
    violations = []
    for i, c in enumerate(m['qa_cases']):
        pair = pairs[c['id']]
        j = judges.get(c['id'], {})
        complete = len(pair) == 2 and all(r.get('state') == 'COMPLETE' and r.get('diagnostic') and not r.get('error') for r in pair.values())
        try:
            judgment = a3.validated_judge(j['judgment']) if j.get('state') == 'COMPLETE' and not j.get('error') else None
        except (KeyError, ValueError):
            judgment = None
        if not complete or judgment is None:
            rows.append(dict(id=c['id'], scoreable=False))
            continue
        l, r = pair[LEGACY], pair[RUNTIME]
        counts['scoreable'] += 1
        ls, rs = l['diagnostic']['result']['status'], r['diagnostic']['result']['status']
        counts['legacy_correct'] += ls == c['expected_status']
        counts['runtime_correct'] += rs == c['expected_status']
        counts['new_false_answer'] += c['expected_status'] != 'answered' and rs == 'answered' and ls != 'answered'
        counts['new_false_refusal'] += c['expected_status'] == 'answered' and rs != 'answered' and ls == 'answered'
        li, ri = a3.integrity(l), a3.integrity(r)
        quality = 'equivalent' if judgment['preferred'] == 'equivalent' else 'better' if a3.labels(i)[judgment['preferred']] == RUNTIME else 'worse'
        counts[quality] += 1
        counts['critical_runtime_regressions'] += quality == 'worse' and judgment['critical_regression']
        d = r['diagnostic']['diagnostics']
        audit = d.get('answer_point_audit', {})
        points = d.get('question_decomposition', {}).get('points', [])
        valid = bool(points) and len(points) <= 5 and [p.get('answer_point_id') for p in points] == [f'point.{i+1}' for i in range(len(points))] and all(p.get('text') for p in points)
        row = dict(id=c['id'], scoreable=True, legacy_status=ls, runtime_status=rs, legacy_integrity=li, runtime_integrity=ri,
                   new_integrity=sorted(set(ri) - set(li)), quality=quality, decomposition_valid=valid,
                   coverage_evaluable=audit.get('coverage_evaluable') is True, coverage_complete=audit.get('coverage_complete') is True,
                   structural_review=any(x.get('audit', {}).get('review_error') for x in r.get('reviews', []) if x.get('audit')),
                   legacy_decomposition_calls=a3.decom_calls(l), runtime_decomposition_calls=a3.decom_calls(r),
                   runtime_revision_count=d.get('revision_count'), post_verify_retrieval=a3.post_verify_retrieval(r),
                   additional_generation_calls=a3.generation_calls(r) - a3.generation_calls(l))
        rows.append(row)
    # Check zero-tolerance integrity independently of judge scoreability.
    for r in raw:
        if r.get('product_violation'):
            violations.append(r['execution_id'] + ':PRODUCT_CONTRACT:' + r['product_violation'])
        if a3.post_verify_retrieval(r):
            violations.append(r['execution_id'] + ':POST_VERIFY_RETRIEVAL')
        if not r.get('diagnostic'):
            continue
        result = r['diagnostic']['result']
        try:
            qa.QAResult.model_validate(result)
        except Exception:
            violations.append(r['execution_id'] + ':PUBLIC_DTO')
        audits = [v.get('audit') for v in r.get('reviews', [])] + [r['diagnostic']['diagnostics'].get('answer_point_audit')]
        for audit in filter(None, audits):
            known = {p['answer_point_id'] for p in audit.get('answer_points', [])}
            accepted = set(audit.get('covered_answer_point_ids', [])) | set(audit.get('missing_answer_point_ids', []))
            accepted |= {p for x in audit.get('claim_mappings', []) for p in x.get('verified_answer_point_ids', [])}
            if not accepted <= known:
                violations.append(r['execution_id'] + ':UNKNOWN_POINT_ACCEPTED')
            if any(x.get('supported') and qa._internal_claim_reason(x) for x in audit.get('claim_mappings', [])):
                violations.append(r['execution_id'] + ':INTERNAL_CLAIM_CREDITED')
    good = [r for r in rows if r['scoreable']]
    sentinel = next((r for r in good if r['id'] == 'g112'), {})
    numerator = sum(r['additional_generation_calls'] for r in good)
    mean = numerator / len(good) if good else None
    gates = dict(P1=len(raw) == 10 and len(judged) == 5 and len(good) == 5,
                 P2=bool(good) and all(not r['new_integrity'] for r in good),
                 P3=bool(sentinel) and 'unsupported_identifier' not in sentinel.get('runtime_integrity', []) and all(sentinel.get(k) for k in ('decomposition_valid', 'coverage_evaluable', 'coverage_complete')) and not sentinel.get('structural_review'),
                 P4=bool(good) and counts['runtime_correct'] >= counts['legacy_correct'] and not counts['new_false_answer'] and not counts['new_false_refusal'],
                 P5=bool(good) and not counts['critical_runtime_regressions'], P6=bool(good) and not counts['worse'],
                 P7=bool(good) and all(r['legacy_decomposition_calls'] == 0 and r['runtime_decomposition_calls'] == 1 and r['runtime_revision_count'] is not None and r['runtime_revision_count'] <= 1 and r['post_verify_retrieval'] == 0 for r in good),
                 P8=mean is not None and mean <= 2, P9=all(static['gates'][k] for k in ('S7','S8','S9','S10','S11','S12')))
    verdict = 'FAIL' if violations else 'INCONCLUSIVE' if not gates['P1'] else 'PASS' if all(gates.values()) and all(static['gates'].values()) else 'FAIL'
    return a3.canonical(dict(verdict=verdict, static_gates=static['gates'], gates=gates, counts=dict(counts), per_case=rows,
                            zero_tolerance_violations=sorted(set(violations)), overhead_numerator=numerator, overhead_denominator=len(good), mean_additional_generation_calls=mean,
                            usage=dict(legacy=h.usage_sum([r for r in raw if r['mode'] == LEGACY]), runtime=h.usage_sum([r for r in raw if r['mode'] == RUNTIME]), judge=h.usage_sum(judged))))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('phase', choices=['static', 'paired', 'judge', 'score'])
    p.add_argument('--candidate')
    args = p.parse_args()
    if args.phase == 'static':
        result = static_result()
        h.save(STATIC, result)
        print(json.dumps(result['gates']))
        h.require(all(result['gates'].values()), 'BLOCKED / REPAIR_SCOPE_REVIEW_REQUIRED')
        return
    m = validate(args.candidate)
    cs = m['qa_cases']
    meta = dict(candidate_commit=args.candidate, starting_head=START)
    target = RAW if args.phase == 'paired' else JUDGED
    if args.phase in ('paired', 'judge') and target.exists():
        prior = h.read(target)
        h.require(all(prior.get(k) == v for k, v in meta.items()), 'persisted identity mismatch')
    if args.phase == 'paired':
        def execute(r):
            v = a3.Meter(h.settings())
            agent = None
            try:
                agent = a3.Capture(ROOT, vertex=v)
                r['diagnostic'] = agent._run_detailed(r['question'], mode=r['mode'])
            except ValueError as exc:
                if v.events and 'response' in v.events[-1] and not v.events[-1].get('error'):
                    r['product_violation'] = str(exc)
                raise
            finally:
                r['usage'] = v.events
                if agent:
                    r['trace'], r['reviews'] = agent.trace, agent.review_records
        h.run_records(RAW, meta, a3.order(cs), execute)
    elif args.phase == 'judge':
        rc = h.committed(RAW)
        raw = h.read(RAW)
        h.require(raw['candidate_commit'] == args.candidate and [r['execution_id'] for r in raw['records']] == [x[0] for x in a3.order(cs)], 'raw identity/order')
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
        h.run_records(JUDGED, {**meta, 'raw_commit': rc}, [(c['id'], dict(index=i)) for i,c in enumerate(cs)], execute)
    else:
        rc, jc = h.committed(RAW), h.committed(JUDGED)
        raw, judged = h.read(RAW), h.read(JUDGED)
        h.require(raw['candidate_commit'] == judged['candidate_commit'] == args.candidate and judged['raw_commit'] == rc, 'science identity')
        h.require([r['execution_id'] for r in raw['records']] == [x[0] for x in a3.order(cs)], 'raw identity/order')
        h.require([r['execution_id'] for r in judged['records']] == IDS, 'judge identity/order')
        result = {**meta, 'raw_commit': rc, 'judged_commit': jc, **score(m, raw['records'], judged['records'], h.read(STATIC))}
        if RESULT.exists():
            h.require(h.read(RESULT) == result, 'canonical score mismatch')
        else:
            h.save(RESULT, result)
        print(json.dumps(dict(verdict=result['verdict'], gates=result['gates'])))


if __name__ == '__main__':
    main()
