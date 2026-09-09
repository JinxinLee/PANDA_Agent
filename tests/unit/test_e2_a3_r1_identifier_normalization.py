"""R1 normalization, actual verifier, frozen impact, and prospective score gates."""
import importlib.util
from pathlib import Path
import sys

import pytest
from panda_agent import qa
from test_e2_a1_answer_point_coverage import agent, state, claim, Vertex, review
from test_qa import bundle_for, code_evidence
from test_e2_a3_runtime_activation_regression import fixtures

spec = importlib.util.spec_from_file_location('r1_eval', Path(__file__).resolve().parents[2] / 'evaluation/run_e2_a3_r1_targeted_revalidation.py')
r1 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = r1
spec.loader.exec_module(r1)


@pytest.mark.parametrize('token,expected', list(r1.MATRIX.items()))
def test_exact_normalization(token, expected):
    assert qa._normalise_rejected_identifier_token(token) == expected


@pytest.mark.parametrize('token,error', [('Class::method:', None), ('Other::method:', 'unsupported identifier Other::method')])
def test_actual_verifier_generic_token(tmp_path, token, error):
    a = agent(tmp_path, Vertex(reviews=[review({'c1':['point.1']}, missing=['point.2'])]),
              bundle_for(code_evidence(text='void Class::method() {}', path='method.h')))
    out = a._verify(state(a, [claim(text=token)]))
    errors = [e for e in out['errors'] if e.startswith('unsupported identifier')]
    assert errors == ([error] if error else [])


def test_complete_frozen_repaired_code_scan():
    out = r1.static_result()
    assert all(out['gates'].values())
    assert out['snapshots_by_mode'] == {r1.LEGACY:81, r1.RUNTIME:76}
    assert out['previously_accepted_newly_rejected'] == 0


def data():
    manifest, _, raw, judged = fixtures()
    cs = r1.selected_cases()
    raw = [next(r for r in raw if r['case_id'] == c['id'] and r['mode'] == mode)
           for c in cs for mode in (r1.LEGACY, r1.RUNTIME)]
    for r in raw:
        if r['mode'] == r1.RUNTIME:
            audit = r['diagnostic']['diagnostics']['answer_point_audit']
            audit['covered_answer_point_ids'] = [p['answer_point_id'] for p in audit['answer_points']]
            audit['missing_answer_point_ids'] = []
    judged = [next(j for j in judged if j['execution_id'] == c['id']) for c in cs]
    return dict(qa_cases=cs), raw, judged, dict(gates={f'S{i}':True for i in range(1,13)})


def test_perfect_and_canonical():
    out = r1.score(*data())
    assert out['verdict'] == 'PASS' and all(out['gates'].values())
    assert r1.a3.canonical(out) == out


@pytest.mark.parametrize('gate,mutate', [
    ('P2', lambda r:r['reviews'].append({'errors':['unsupported identifier Other::method'], 'audit':None})),
    ('P3', lambda r:r['diagnostic']['diagnostics']['answer_point_audit'].update(coverage_complete=False)),
    ('P4', lambda r:r['diagnostic']['result'].update(status='insufficient_evidence')),
    ('P7', lambda r:r['diagnostic']['diagnostics'].update(revision_count=2)),
    ('P8', lambda r:r['usage'][0].update(adapter_requests=99)),
])
def test_gate_failure(gate, mutate):
    args = data()
    mutate(args[1][1])
    out = r1.score(*args)
    assert not out['gates'][gate] and out['verdict'] == 'FAIL'


def test_strict_quality_and_blind_order():
    args = data()
    args[2][0]['judgment'].update(preferred='A', critical_regression=True)
    out = r1.score(*args)
    assert not out['gates']['P5'] and not out['gates']['P6']
    args = data()
    args[2][1]['judgment']['preferred'] = 'A'
    assert r1.score(*args)['counts']['better'] == 1
    assert [v[1]['mode'] for v in r1.a3.order(args[0]['qa_cases'])][:4] == [r1.LEGACY,r1.RUNTIME,r1.RUNTIME,r1.LEGACY]


def test_infrastructure_and_protocol_precedence():
    args = data()
    args[2][0]['error'] = 'provider timeout'
    assert r1.score(*args)['verdict'] == 'INCONCLUSIVE'
    args[1][1]['trace'].append('retrieval')
    assert r1.score(*args)['verdict'] == 'FAIL'


def test_judge_payload_excludes_treatment():
    args = data()
    pair = {r['mode']:r for r in args[1] if r['case_id'] == 'g112'}
    p = r1.a3.judge_input(args[0]['qa_cases'][0], pair, 0)
    assert set(p) == {'question','approved_reference','A','B'}
    assert set(p['A']) == {'status','answer','claims','evidence'}
    assert all(set(c) == {'claim_id','claim_text','evidence_ids'} for c in p['A']['claims'])
