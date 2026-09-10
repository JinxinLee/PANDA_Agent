"""Fake-only R3 selector, frozen protocol and non-inferiority scorer tests."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('r3_tests', ROOT / 'evaluation/run_e2_a3_r3_runtime_activation.py')
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)


def fixture():
    cases = [dict(id=f'case{i:02}', source='Gold', question='Describe the input.', intent='usage', expected_status='answered' if i < 10 else 'insufficient_evidence') for i in range(14)]
    raw, judged = [], []
    for i, c in enumerate(cases):
        for mode in (m.LEGACY, m.RUNTIME):
            runtime = mode == m.RUNTIME
            usage = [dict(stage='qa_answer', logical_calls=1, adapter_requests=1, returned_model_calls=1, tokens=5, response={'claims': []})]
            if runtime:
                usage.append(dict(stage='decomposition', logical_calls=1, adapter_requests=1, returned_model_calls=1, tokens=5))
            raw.append(dict(execution_id=c['id']+'.'+mode, state='COMPLETE', case_id=c['id'], mode=mode, usage=usage, trace=['retrieval','verify'], reviews=[],
                            admissions=[dict(task='create_atomic_evidence_bound_claims', evidence_ids=[], requirement_evidence_ids={})],
                            diagnostic=dict(result=dict(status=c['expected_status'], answer='Answer', claims=[], evidence=[], resolved_versions={}, verification_errors=[]),
                                            node_timings_ms={'workflow': 10}, diagnostics=dict(selected_evidence=[], revision_count=0,
                                            question_decomposition={'points': [dict(answer_point_id='point.1', text='Describe input.')]},
                                            answer_point_audit=dict(coverage_evaluable=i<10, coverage_complete=i<10)))))
        judged.append(dict(execution_id=c['id'], state='COMPLETE', judgment=dict(preferred='equivalent', critical_regression=False, A_supported=True, B_supported=True, reason='Supported equivalent.'), usage=[]))
    return {'qa_cases': cases}, raw, judged, {'gates': {f'F{i}': True for i in range(1,11)}}


def runtime(raw, i=0):
    return next(r for r in raw if r['case_id'] == f'case{i:02}' and r['mode'] == m.RUNTIME)


def test_selected_cohort_approval_composition_and_determinism():
    cases, accounting = m.cohort()
    assert accounting['approved_english_dev'] == 59
    assert accounting['eligible_after_exclusion'] == 53
    assert [c['id'] for c in cases] == ['g059','g047','g028','g001','g105','g113','g014','g060','g050','g029','g057','g041','g007','g108']
    assert accounting['expected_status_counts'] == {'answered':10,'insufficient_evidence':3,'version_conflict':1}
    assert not {c['id'] for c in cases} & set(m.EXCLUDED)
    assert all(c['split']=='dev' and c['gold']['review_status']=='approved' for c in cases)


@pytest.mark.parametrize('na,nn,expected', [(20,2,(12,2)),(8,10,(8,6)),(10,4,(10,4))])
def test_shortage_fill_and_intent_round_robin(na, nn, expected):
    pool=[SimpleNamespace(id=f'{status}{i:02}',intent='z' if i%2 else 'a',expected_status=SimpleNamespace(value=status)) for status,n in [('answered',na),('insufficient_evidence',nn)] for i in range(n)]
    picked, _, _ = m.choose(pool[::-1])
    again, _, _ = m.choose(pool)
    assert [c.id for c in picked] == [c.id for c in again]
    assert (sum(c.expected_status.value=='answered' for c in picked),sum(c.expected_status.value!='answered' for c in picked))==expected
    assert len({c.id for c in picked})==14


def test_canonical_json_order_and_blind_labels():
    cases, _, _, _=fixture()
    order=m.order(cases['qa_cases'])
    assert json.loads(json.dumps(order))==order
    assert len(order)==28 and len({x[0] for x in order})==28
    assert [x[1]['mode'] for x in order[:4]]==[m.LEGACY,m.RUNTIME,m.RUNTIME,m.LEGACY]
    assert all(x[1]['expected_status'] in ('answered','insufficient_evidence') for x in order)
    assert m.a3.labels(0)=={'A':m.LEGACY,'B':m.RUNTIME}
    assert m.a3.labels(1)=={'A':m.RUNTIME,'B':m.LEGACY}


def test_perfect_and_refusal_coverage_exception():
    result=m.score(*fixture())
    assert result['verdict']=='PASS' and all(result['gates'].values())
    assert result['coverage_applicable_count']==10
    assert result['counts']['runtime_supported']==14
    assert result['mean_additional_generation_calls']==1
    assert result==json.loads(json.dumps(result))


@pytest.mark.parametrize('gate', ['G2','G3','G4','G5','G6','G7','G8','G9','G10','G11','G12','G13'])
def test_each_product_gate_can_fail(gate):
    manifest,raw,judged,ready=fixture();r=runtime(raw)
    if gate in ('G2','G4'):
        r['diagnostic']['result']['status']='insufficient_evidence'
    elif gate=='G3':
        runtime(raw,10)['diagnostic']['result']['status']='answered'
    elif gate=='G5':
        r['reviews']=[{'errors':['unsupported identifier Other::method']},{'errors':[]}]
    elif gate=='G6':
        raw[0]['reviews']=[{'errors':['incomplete web citation']},{'errors':[]}]
    elif gate=='G7':
        r['diagnostic']['diagnostics']['answer_point_audit']['coverage_complete']=False
    elif gate=='G8':
        r['diagnostic']['diagnostics']['revision_count']=2
    elif gate=='G9':
        judged[0]['judgment']['B_supported']=False
    elif gate=='G10':
        judged[0]['judgment'].update(preferred='A',critical_regression=True)
    elif gate=='G11':
        judged[0]['judgment']['preferred']='A';judged[1]['judgment']['preferred']='B'
    elif gate=='G12':
        r['usage'][0]['adapter_requests']=30
    elif gate=='G13':
        ready['gates']['F7']=False
    result=m.score(manifest,raw,judged,ready)
    assert result['verdict']=='FAIL' and not result['gates'][gate]


def test_one_noncritical_worse_allowed_two_fail():
    manifest,raw,judged,ready=fixture()
    judged[0]['judgment']['preferred']='A'
    result=m.score(manifest,raw,judged,ready)
    assert result['verdict']=='PASS' and result['counts']['worse']==1 and result['counts']['equivalent']==13
    judged[1]['judgment']['preferred']='B'
    assert m.score(manifest,raw,judged,ready)['verdict']=='FAIL'


@pytest.mark.parametrize('stage',['qa_answer','qa_revision'])
@pytest.mark.parametrize('mode',[m.LEGACY,m.RUNTIME])
def test_every_response_stage_and_arm_for_ineligible_citation(stage,mode):
    manifest,raw,judged,ready=fixture();r=next(x for x in raw if x['case_id']=='case00' and x['mode']==mode)
    r['diagnostic']['diagnostics']['selected_evidence']=[dict(evidence_id='page',source_id='sphinx',locator=dict(url='https://example.invalid',snapshot_date='2000-01-01',section_path=[]))]
    r['usage'].append(dict(stage=stage,logical_calls=1,response={'claims':[dict(claim_id='c',claim_text='Public claim',evidence_ids=['page'])]}))
    r['admissions'].append(dict(task=stage,evidence_ids=[],requirement_evidence_ids={}))
    result=m.score(manifest,raw,judged,ready)
    assert result['verdict']=='FAIL' and not result['gates']['G6']


@pytest.mark.parametrize('kind',['provider','malformed_judge','missing_judge'])
def test_infrastructure_prevents_authoritative_scoring(kind):
    manifest,raw,judged,ready=fixture()
    if kind=='provider':raw[0]['error']='Provider unavailable'
    elif kind=='malformed_judge':judged[0]['judgment']['extra']='forbidden'
    else:judged.pop()
    result=m.score(manifest,raw,judged,ready)
    assert result['verdict']=='INCONCLUSIVE' and not result['gates']['G1']


def test_ambiguous_started_record_is_not_replayed(tmp_path):
    p=tmp_path/'raw.json';m.h.save(p,{'records':[{'execution_id':'x','state':'STARTED'}]})
    with pytest.raises(ValueError,match='ambiguous'):
        m.h.run_records(p,{},[('x',{})],lambda _:pytest.fail('must not execute'))


def test_missing_judge_does_not_erase_observed_product_failure():
    manifest,raw,judged,ready=fixture()
    judged[0]['error']='Provider unavailable'
    runtime(raw)['reviews']=[{'errors':['unsupported identifier Other::method']}]
    result=m.score(manifest,raw,judged,ready)
    assert result['verdict']=='FAIL' and not result['gates']['G1']
    assert 'case00:NEW_RUNTIME_INTEGRITY' in result['observed_product_failures']


def test_frozen_product_is_exact_r2_and_repairs_active():
    assert not m.h.git('diff',m.PRODUCT,'--',*m.PRODUCT_PATHS)
    assert m.qa.DEFAULT_ANSWER_POINT_MODE==m.LEGACY
    assert m.qa._normalise_rejected_identifier_token('Class::method:')=='Class::method'
    assert not m.qa._is_public_claim_citation_eligible({'source_id':'sphinx','locator':{'url':'u','snapshot_date':'d','section_path':[]}})


def test_judge_uses_public_allowlist():
    manifest,raw,_,_=fixture();c=manifest['qa_cases'][0]
    c['gold']=dict(required_answer_points=[],allowed_source_versions=[])
    pair={r['mode']:r for r in raw if r['case_id']==c['id']}
    payload=m.a3.judge_input(c,pair,0)
    assert set(payload)=={'question','approved_reference','A','B'}
    assert set(payload['A'])==set(payload['B'])=={'status','answer','claims','evidence'}
    assert 'runtime_e1_v2' not in json.dumps(payload)
