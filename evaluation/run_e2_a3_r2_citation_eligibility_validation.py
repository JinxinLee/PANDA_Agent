"""R2 offline admission reconciliation and separately committed prospective phases."""
from __future__ import annotations

import argparse
import ast
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
spec = importlib.util.spec_from_file_location('r2_r1_helpers', EV / 'run_e2_a3_r1_targeted_revalidation.py')
r1 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = r1
spec.loader.exec_module(r1)
a3, h = r1.a3, r1.h
START = 'ee719bde5331f4102c9d79dd929e31a8063fc9ae'
IDS = ['g013', 'g027', 'g112', 'g002', 'g044', 'g110']
LEGACY, RUNTIME = a3.LEGACY, a3.RUNTIME
MANIFEST = EV / 'e2_a3_r2_citation_eligibility_manifest.json'
STATIC = EV / 'e2_a3_r2_citation_eligibility_static_result.json'
RAW = EV / 'e2_a3_r2_targeted_paired_raw.json'
JUDGED = EV / 'e2_a3_r2_targeted_paired_judged.json'
RESULT = EV / 'e2_a3_r2_targeted_revalidation_result.json'
PREREG = EV / 'E2_A3_R2_CITATION_ELIGIBLE_EVIDENCE_PREREGISTRATION.md'
HISTORY = [
    ('A3', '8ba275addf44a5c7e96bf83a292c6737fbe07b38', 'e2_a3_paired_runtime_raw.json'),
    ('R1', '4092209a11f57ac757502b01e2c55332b88a0519', 'e2_a3_r1_targeted_paired_raw.json'),
]
FROZEN = ['src', 'configs', 'prompts', 'tests', 'data', 'corpus', 'AGENTS.md',
          'evaluation/' + MANIFEST.name, 'evaluation/' + STATIC.name, 'evaluation/' + PREREG.name,
          'evaluation/run_e2_a3_r2_citation_eligibility_validation.py',
          'evaluation/run_e2_a3_r1_targeted_revalidation.py',
          'evaluation/run_e2_a3_runtime_activation_regression.py',
          'evaluation/run_e2_a2_targeted_claim_mapping_validation.py',
          'evaluation/e2_a3_runtime_activation_manifest.json',
          *['evaluation/' + name for _, _, name in HISTORY]]


def eligible(items):
    return [e for e in items if qa._is_public_claim_citation_eligible(e)]


def admission_probe():
    """Fake-only calls through the actual answer, revision and verifier seams."""
    class Fake:
        def __init__(self):
            self.payloads = []

        def generate_json(self, prompt, schema, **kwargs):
            p = json.loads(prompt)
            self.payloads.append(p)
            if p['task'] == 'review_claim_support_and_relevance':
                return dict(supported=True, unsupported_claim_ids=[], irrelevant_claim_ids=[],
                            missing_requirement_ids=[], reason='')
            return {'claims': []}

    common = dict(source_version_id='sphinx@test', text='Factory acceptance input.', score=1,
                  retrieval_channels=['dense'], authority_level='primary')
    section = dict(common, evidence_id='section', object_id='s', source_id='sphinx',
                   locator=dict(url='https://example.invalid/#section', snapshot_date='2000-01-01', section_path=['A', 'B']))
    page = deepcopy(section)
    page.update(evidence_id='page', object_id='p')
    page['locator']['section_path'] = []
    code = dict(common, evidence_id='code', object_id='c', source_id='code', source_version_id='code@test',
                locator=dict(path='input.h', start_line=1, end_line=2, section_path=[]))
    bundle = dict(evidence=[section, page, code], plan=dict(intent='usage', resolved_versions={},
                  target_repositories=[], required_source_types=[], symbols=[], concepts=[]))
    before = deepcopy(bundle)
    agent = object.__new__(qa.QAAgent)
    agent.vertex = Fake()
    state = dict(question='Describe factory acceptance input.', bundle=bundle, sufficient=True,
                 draft={'claims': []}, answer_point_coverage_mode=LEGACY, errors=[],
                 answer_requirements=[dict(id='factory_composition', description='Describe factory composition.')],
                 missing_requirement_ids=['factory_composition'])
    agent._answer(state)
    agent._revise(state)
    answer, revision = agent.vertex.payloads[:2]
    bad = dict(claim_id='bad', claim_text='Factory acceptance input.', evidence_ids=['page'], answer_point_ids=['question_core'])
    rejected = agent._verify({**state, 'draft': {'claims': [bad]}, 'answer_requirements': [], 'missing_requirement_ids': []})
    return dict(answer_ids=[e['evidence_id'] for e in answer['untrusted_evidence']],
                revision_ids=[e['evidence_id'] for e in revision['untrusted_evidence']],
                revision_requirement_ids=[e['evidence_id'] for es in revision['requirement_evidence'].values() for e in es],
                original_bundle_unchanged=bundle == before,
                verifier_errors=rejected['errors'])


def exact_scope():
    old = ast.parse(h.git('show', START + ':src/panda_agent/qa.py'))
    tree = ast.parse((ROOT / 'src/panda_agent/qa.py').read_text(encoding='utf-8'))
    helper = '_is_public_claim_citation_eligible'
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == helper]
    expected = ast.parse('''def _is_public_claim_citation_eligible(evidence: dict[str, Any]) -> bool:
    """Apply the existing Sphinx citation contract at claim evidence admission."""
    if "sphinx" in evidence["source_id"]:
        locator = evidence.get("locator") or {}
        return bool(locator.get("url") and locator.get("snapshot_date") and locator.get("section_path"))
    return True
''').body[0]
    predicate_exact = len(nodes) == 1 and ast.dump(nodes[0]) == ast.dump(expected)
    tree.body = [n for n in tree.body if n not in nodes]
    projections, uses = [], []
    for method in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name in ('_answer', '_revise')]:
        for n in list(method.body):
            if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id == 'claim_evidence':
                expected_projection = ast.parse('[item for item in state["bundle"]["evidence"] if _is_public_claim_citation_eligible(item)]', mode='eval').body
                if ast.dump(n.value) == ast.dump(expected_projection):
                    projections.append(method.name)
                    method.body.remove(n)
        class Reverse(ast.NodeTransformer):
            def visit_Name(self, node):
                if node.id == 'claim_evidence':
                    uses.append(method.name)
                    return ast.parse('state["bundle"]["evidence"]', mode='eval').body
                return node
        Reverse().visit(method)
    exact = predicate_exact and projections == ['_answer', '_revise'] and Counter(uses) == {'_answer': 1, '_revise': 2} and ast.dump(tree) == ast.dump(old)
    changed = h.git('diff', START, '--name-only', '--', 'src', 'configs', 'prompts', 'data', 'corpus').splitlines()
    return exact, changed == ['src/panda_agent/qa.py']


def claim_edges(record, final_only=False):
    evidence = {e['evidence_id']: e for e in record['diagnostic']['diagnostics']['selected_evidence']}
    claims = list(record['diagnostic']['result']['claims'])
    if not final_only:
        claims += [c for event in record['usage'] if event['stage'] in ('qa_answer', 'qa_revision')
                   for c in event.get('response', {}).get('claims', [])]
    seen = set()
    edges = []
    for c in claims:
        if qa._internal_claim_reason(c):
            continue
        key = json.dumps([c.get('claim_id'), c.get('claim_text'), c.get('evidence_ids', [])])
        if key in seen:
            continue
        seen.add(key)
        for eid in c.get('evidence_ids', []):
            e = evidence.get(eid)
            if e and 'sphinx' in e['source_id']:
                edges.append(dict(claim_id=c['claim_id'], evidence_id=eid,
                                  eligible=qa._is_public_claim_citation_eligible(e)))
    return edges


def static_result():
    rows, edges, final_edges = [], [], []
    unchanged = True
    non_sphinx = 0
    for experiment, commit, name in HISTORY:
        records = json.loads(h.git('show', commit + ':evaluation/' + name))['records']
        for r in records:
            items = r['diagnostic']['diagnostics']['selected_evidence']
            before = deepcopy(items)
            projected = eligible(items)
            unchanged &= items == before and [e for e in projected if 'sphinx' not in e['source_id']] == [e for e in items if 'sphinx' not in e['source_id']]
            non_sphinx += sum('sphinx' not in e['source_id'] for e in items)
            context = dict(experiment=experiment, case_id=r['case_id'], mode=r['mode'])
            for e in items:
                if 'sphinx' in e['source_id']:
                    loc = e.get('locator') or {}
                    rows.append(dict(context, evidence_id=e['evidence_id'], object_id=e['object_id'],
                                     eligible=qa._is_public_claim_citation_eligible(e),
                                     empty_section_only=bool(loc.get('url') and loc.get('snapshot_date') and not loc.get('section_path')),
                                     retained=e in projected))
            edges.extend(dict(context, **edge) for edge in claim_edges(r))
            final_edges.extend(dict(context, **edge) for edge in claim_edges(r, True))
    invalid = [e for e in edges if not e['eligible']]
    complete = sum(e['eligible'] for e in rows)
    excluded = sum(not e['retained'] for e in rows)
    probe = admission_probe()
    exact, protected = exact_scope()
    sentinel = {(e['experiment'], e['case_id'], e['mode'], e['evidence_id']) for e in invalid}
    expected = {('A3', 'g013', mode, 'evidence.258612f18040b81459f72d3b') for mode in (LEGACY, RUNTIME)}
    expected.add(('R1', 'g027', RUNTIME, 'evidence.d452f25b295c0ce037b92b26'))
    sentinel_ok = sentinel == expected and all(not e['retained'] for e in rows if (e['experiment'], e['case_id'], e['mode'], e['evidence_id']) in expected)
    gates = dict(S1=exact, S2=probe['answer_ids'] == ['section', 'code'],
                 S3=probe['revision_ids'] == ['section', 'code'] and probe['revision_requirement_ids'] == ['section', 'code'],
                 S4=exact and any('incomplete web citation' in e for e in probe['verifier_errors']),
                 S5=sentinel_ok, S6=sentinel_ok,
                 S7=len(rows) == 144 and complete == 106 and excluded == 38 and sum(e['empty_section_only'] for e in rows) == 38 and len(edges) == 27 and len(invalid) == 3 and len(final_edges) == 18 and all(e['eligible'] for e in final_edges),
                 S8=all(e['retained'] for e in rows if e['eligible']),
                 S9=unchanged and exact, S10=protected and exact and probe['original_bundle_unchanged'],
                 S11=exact, S12=exact and protected, S13=qa.DEFAULT_ANSWER_POINT_MODE == LEGACY)
    return dict(starting_head=START, historical_sources=HISTORY, rule='Sphinx: URL AND snapshot_date AND nonempty section_path; all non-Sphinx unchanged',
                gates=gates, selected_sphinx_occurrences=len(rows), complete=complete, ineligible=len(rows)-complete,
                ineligible_excluded=excluded, eligible_incorrectly_excluded=sum(e['eligible'] and not e['retained'] for e in rows),
                claim_edges=len(edges), complete_claim_edges=len(edges)-len(invalid), invalid_claim_edges=invalid,
                final_claim_edges=len(final_edges), final_complete_claim_edges=sum(e['eligible'] for e in final_edges),
                non_sphinx_occurrences=non_sphinx, non_sphinx_unchanged=unchanged, admission_probe=probe,
                exact_production_scope=exact, retrieval_implementation_unchanged=protected,
                selected_sphinx=rows, scientific_calls_before_freeze=0)


def selected_cases():
    source = json.loads(h.git('show', START + ':evaluation/e2_a3_runtime_activation_manifest.json'))
    by_id = {c['id']: c for c in source['qa_cases']}
    return [by_id[cid] for cid in IDS]


class Meter(a3.Meter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.admissions = []

    def generate_json(self, prompt, schema, **kwargs):
        p = json.loads(prompt)
        if p.get('task') in ('create_atomic_evidence_bound_claims', 'revise_unsupported_claims_once'):
            self.admissions.append(dict(task=p['task'], evidence_ids=[e['evidence_id'] for e in p['untrusted_evidence']],
                                       requirement_evidence_ids={k: [e['evidence_id'] for e in es] for k, es in p.get('requirement_evidence', {}).items()}))
        return super().generate_json(prompt, schema, **kwargs)


def validate(candidate):
    m = h.read(MANIFEST)
    h.require(m['starting_head'] == START and m['qa_cases'] == selected_cases(), 'manifest identity/cohort')
    h.require(m['provider'] == asdict(h.settings()), 'provider drift')
    h.require(m['order'] == a3.canonical(a3.order(m['qa_cases'])), 'order drift')
    h.require(qa.DEFAULT_ANSWER_POINT_MODE == LEGACY, 'default drift')
    h.require(all(h.read(STATIC)['gates'].values()), 'static gates failed')
    h.require(candidate and not h.git('diff', candidate, '--', *FROZEN), 'frozen code/protocol drift')
    h.git('merge-base', '--is-ancestor', candidate, 'HEAD')
    h.committed(MANIFEST)
    return m


def score(m, raw, judged, static):
    # Reuse the frozen all-review integrity, status, mapping and boundary accounting.
    old_static = {'gates': {f'S{i}': True for i in range(1, 13)}}
    base = r1.score(m, raw, judged, old_static)
    rows, counts = base['per_case'], Counter(base['counts'])
    records = {(r['case_id'], r['mode']): r for r in raw}
    judge_map = {j['execution_id']: j for j in judged}
    invalid_claims, web_errors, admission_errors, colon_errors = [], [], [], []
    for record in raw:
        if not record.get('diagnostic'):
            continue
        evidence = record['diagnostic']['diagnostics']['selected_evidence']
        by_id = {e['evidence_id']: e for e in evidence}
        allowed = [e['evidence_id'] for e in eligible(evidence)]
        admissions = record.get('admissions', [])
        call_count = sum(e['stage'] in ('qa_answer', 'qa_revision') for e in record.get('usage', []))
        if len(admissions) != call_count:
            admission_errors.append(record['execution_id'] + ':missing admission capture')
        for admission in admissions:
            auxiliary = [eid for es in admission['requirement_evidence_ids'].values() for eid in es]
            if admission['evidence_ids'] != allowed or not set(auxiliary) <= set(allowed):
                admission_errors.append(record['execution_id'] + ':admission differs from eligible projection')
        for event in record.get('usage', []):
            if event['stage'] not in ('qa_answer', 'qa_revision'):
                continue
            for claim in event.get('response', {}).get('claims', []):
                if qa._internal_claim_reason(claim):
                    continue
                for eid in claim.get('evidence_ids', []):
                    if eid in by_id and not qa._is_public_claim_citation_eligible(by_id[eid]):
                        invalid_claims.append(dict(execution_id=record['execution_id'], stage=event['stage'], claim_id=claim['claim_id'], evidence_id=eid))
        for review in record.get('reviews', []):
            for error in review.get('errors', []):
                if 'incomplete web citation' in error.lower():
                    web_errors.append(dict(execution_id=record['execution_id'], error=error))
                if record['case_id'] == 'g112' and record['mode'] == RUNTIME and 'unsupported identifier' in error.lower() and 'PndLmdDataReader::fillData:' in error:
                    colon_errors.append(error)
    good = [row for row in rows if row['scoreable']]
    for row in good:
        i = IDS.index(row['id'])
        j = a3.validated_judge(judge_map[row['id']]['judgment'])
        for label, mode in a3.labels(i).items():
            arm = 'legacy' if mode == LEGACY else 'runtime'
            row[arm + '_supported'] = j[label + '_supported']
            counts[arm + '_supported'] += j[label + '_supported']
        row['judge_reason'] = j['reason']
        row['critical_runtime_regression'] = j['critical_regression'] and row['quality'] == 'worse'
        row['complete_sphinx_selected'] = {}
        for mode in (LEGACY, RUNTIME):
            rec = records[(row['id'], mode)]
            row['complete_sphinx_selected'][mode] = [e['evidence_id'] for e in rec['diagnostic']['diagnostics']['selected_evidence'] if 'sphinx' in e['source_id'] and qa._is_public_claim_citation_eligible(e)]
    sentinels = [row for row in good if row['id'] in ('g013', 'g027')]
    guard = next((row for row in good if row['id'] == 'g112'), {})
    expected = {c['id']: c['expected_status'] for c in m['qa_cases']}
    guards = ('decomposition_valid', 'coverage_evaluable', 'coverage_complete')
    gates = dict(
        P1=len(raw) == 12 and len(judged) == 6 and len(good) == 6,
        P2=not invalid_claims and not admission_errors,
        P3=not web_errors,
        P4=len(sentinels) == 2 and all(row['legacy_status'] == row['runtime_status'] == expected[row['id']] and all(row[k] for k in guards) and not row['structural_review'] and not {'incomplete_citation', 'structural_review'} & (set(row['legacy_integrity']) | set(row['runtime_integrity'])) for row in sentinels),
        P5=bool(guard) and not colon_errors and all(guard[k] for k in guards),
        P6=bool(good) and counts['runtime_correct'] >= counts['legacy_correct'] and not counts['new_false_answer'] and not counts['new_false_refusal'],
        P7=bool(good) and all(not row['new_integrity'] for row in good),
        P8=bool(good) and all(row['legacy_decomposition_calls'] == 0 and row['runtime_decomposition_calls'] == 1 and row['runtime_revision_count'] is not None and row['runtime_revision_count'] <= 1 and row['post_verify_retrieval'] == 0 for row in good) and all(a3.post_verify_retrieval(r) == 0 for r in raw),
        P9=base['mean_additional_generation_calls'] is not None and base['mean_additional_generation_calls'] <= 2,
        P10=len(good) == 6 and counts['runtime_supported'] == 6 and not counts['critical_runtime_regressions'],
        P11=all(static['gates'][k] for k in ('S9', 'S10', 'S11', 'S12', 'S13')),
    )
    violations = base['zero_tolerance_violations']
    verdict = 'FAIL' if violations else 'INCONCLUSIVE' if not gates['P1'] else 'PASS' if all(gates.values()) and all(static['gates'].values()) else 'FAIL'
    return dict(verdict=verdict, gates=gates, static_gates=static['gates'], counts=dict(counts), per_case=rows,
                invalid_public_claim_edges=invalid_claims, incomplete_web_review_errors=web_errors,
                admission_errors=admission_errors, historical_colon_errors=colon_errors,
                zero_tolerance_violations=violations, mean_additional_generation_calls=base['mean_additional_generation_calls'],
                overhead_numerator=base['overhead_numerator'], overhead_denominator=base['overhead_denominator'],
                usage=base['usage'], embedding_tokens='unavailable', scientific_calls_before_candidate_freeze=0,
                historical_P6_FAIL_preserved=True, P6_waiver_granted=False, noncritical_worse_is_gate=False, runtime_activated=False)


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
            v = Meter(h.settings())
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
        h.run_records(JUDGED, {**meta, 'raw_commit': rc}, [(c['id'], dict(index=i)) for i, c in enumerate(cs)], execute)
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
