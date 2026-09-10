"""Offline recovery lineage, authority completeness and original gate tests."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys

import pytest
from test_e2_a3_r3_runtime_activation import fixture as r3_fixture

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('recovery_tests', ROOT/'evaluation/run_e2_a3_r3_r1_recovery.py')
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)
IDS = ['g059','g047','g028','g001','g105','g113','g014','g060','g050','g029','g057','g041','g007','g108']


def fixture():
    manifest, raw, judged, _ = r3_fixture()
    replacements = {c['id']: IDS[i] for i,c in enumerate(manifest['qa_cases'])}
    for case in manifest['qa_cases']:
        case['id'] = replacements[case['id']]
    for record in raw:
        record['case_id'] = replacements[record['case_id']]
        record['execution_id'] = record['case_id']+'.'+record['mode']
    for record in judged:
        record['execution_id'] = replacements[record['execution_id']]
    manifest['labels'] = [m.a3.labels(i) for i in range(14)]
    manifest['order'] = m.r3.order(manifest['qa_cases'])
    ready = {'gates':{f'R-F{i}':True for i in range(1,12)}}
    return manifest, raw, judged, ready, []


def arm(raw, cid='g059', mode=m.RUNTIME):
    return next(r for r in raw if r['case_id']==cid and r['mode']==mode)


def test_original_authority_and_infrastructure_only_selection():
    manifest,raw,judged,result=m.history()
    assert result['verdict']=='INCONCLUSIVE'
    assert manifest['gates']==m.r3.GATES
    assert len(raw['records'])==28 and len(judged['records'])==14
    assert m.historical_unchanged()
    assert not m.h.git('diff',m.PRODUCT,'--',*m.r3.PRODUCT_PATHS)


def test_original_indices_order_and_labels_not_reindexed():
    manifest,*_=fixture()
    order=m.recovery_order(manifest)
    assert [(x[1]['case_id'],x[1]['mode'],x[1]['original_r3_index']) for x in order]==[
        ('g059',m.LEGACY,0),('g059',m.RUNTIME,0),('g047',m.RUNTIME,1),('g047',m.LEGACY,1),('g001',m.RUNTIME,3),('g001',m.LEGACY,3)]
    assert json.loads(json.dumps(order))==order
    assert manifest['labels'][3]=={'A':m.RUNTIME,'B':m.LEGACY}


def test_compose_exact_eleven_plus_three_no_old_partial_arms():
    manifest,raw,judged,ready,_=fixture()
    fresh=[deepcopy(r) for r in raw if r['case_id'] in m.RECOVER]
    fresh_j=[deepcopy(j) for j in judged if j['execution_id'] in m.RECOVER]
    for r in fresh:r['origin_marker']='fresh'
    cr,cj,provenance=m.compose(manifest,raw,judged,fresh,fresh_j,'new-raw','new-judge')
    assert len(cr)==28 and len(cj)==14
    assert all(r.get('origin_marker')=='fresh' for r in cr if r['case_id'] in m.RECOVER)
    assert [r for r in cr if r['case_id'] not in m.RECOVER]==[r for cid in m.CARRY for _,ctx in manifest['order'] for r in raw if ctx['case_id']==cid and r['case_id']==cid and r['mode']==ctx['mode']]
    assert sum(p['authority_source']=='original_r3' for p in provenance)==11
    assert all(p['raw_commit']=='new-raw' for p in provenance if p['case_id'] in m.RECOVER)
    fresh.pop(0)
    cr,cj,p=m.compose(manifest,raw,judged,fresh,fresh_j,'new-raw','new-judge')
    assert len(cr)==27
    result=m.score(manifest,cr,cj,ready,p)
    assert result['verdict']=='INCONCLUSIVE'
    assert result['gates']['G1']['state']=='NOT_EVALUABLE'
    assert result['gates']['G6']['state']=='NOT_EVALUABLE'
    assert result['gates']['G12']['state']=='NOT_EVALUABLE' and result['mean_additional_generation_calls'] is None


def test_complete_gate_authority_and_refusal_exception():
    result=m.score(*fixture())
    assert result['verdict']=='PASS'
    assert all(g['state']=='PASS' and g['authority_complete'] and not g['observed_violation'] for g in result['gates'].values())
    assert result['overhead_denominator']==14 and result['overhead_numerator']==14
    assert result['counts']['authoritative_pairs']==14


@pytest.mark.parametrize('gate',['G2','G3','G4','G5','G6','G7','G8','G9','G10','G11','G12','G13'])
def test_product_gate_failures(gate):
    manifest,raw,judged,ready,provenance=fixture();r=arm(raw)
    if gate in ('G2','G4'):r['diagnostic']['result']['status']='insufficient_evidence'
    elif gate=='G3':arm(raw,'g057')['diagnostic']['result']['status']='answered'
    elif gate=='G5':r['reviews']=[{'errors':['unsupported identifier Other::method']},{'errors':[]}]
    elif gate=='G6':raw[0]['reviews']=[{'errors':['incomplete web citation']},{'errors':[]}]
    elif gate=='G7':r['diagnostic']['diagnostics']['answer_point_audit']['coverage_complete']=False
    elif gate=='G8':r['diagnostic']['diagnostics']['revision_count']=2
    elif gate=='G9':judged[0]['judgment']['B_supported']=False
    elif gate=='G10':judged[0]['judgment'].update(preferred='A',critical_regression=True)
    elif gate=='G11':judged[0]['judgment']['preferred']='A';judged[1]['judgment']['preferred']='B'
    elif gate=='G12':r['usage'][0]['adapter_requests']=30
    else:ready['gates']['R-F1']=False
    result=m.score(manifest,raw,judged,ready,provenance)
    assert result['verdict']=='FAIL' and result['gates'][gate]['state']=='FAIL'


@pytest.mark.parametrize('failure',['unsupported','second_worse','citation','status','coverage','new_integrity'])
def test_independent_failure_precedes_unrelated_infrastructure(failure):
    manifest,raw,judged,ready,p=fixture()
    arm(raw,'g001')['error']='ConnectionTimeout'
    arm(raw,'g001').pop('diagnostic')
    judged[3]['error']='unscoreable'
    if failure=='unsupported':judged[0]['judgment']['B_supported']=False
    elif failure=='second_worse':judged[0]['judgment']['preferred']='A';judged[9]['judgment']['preferred']='B'
    elif failure=='citation':arm(raw)['reviews']=[{'errors':['incomplete web citation']}]
    elif failure=='status':arm(raw)['diagnostic']['result']['status']='insufficient_evidence'
    elif failure=='coverage':arm(raw)['diagnostic']['diagnostics']['answer_point_audit']['coverage_complete']=False
    else:arm(raw)['reviews']=[{'errors':['unsupported identifier Other::method']}]
    result=m.score(manifest,raw,judged,ready,p)
    assert result['verdict']=='FAIL' and result['gates']['G1']['state']=='NOT_EVALUABLE'


def test_one_worse_carried_forward_leaves_zero_recovery_worse_budget():
    manifest,raw,judged,ready,p=fixture()
    judged[9]['judgment']['preferred']='B'  # g029 index 9: B legacy
    assert m.score(manifest,raw,judged,ready,p)['verdict']=='PASS'
    judged[3]['judgment']['preferred']='B'  # recovery g001 index 3: B legacy
    result=m.score(manifest,raw,judged,ready,p)
    assert result['gates']['G11']['state']=='FAIL' and result['counts']['worse']==2


@pytest.mark.parametrize('missing',['judge','citation_context','review','admission'])
def test_no_pass_without_gate_specific_authority(missing):
    manifest,raw,judged,ready,p=fixture();r=arm(raw)
    if missing=='judge':judged.pop(0)
    elif missing=='citation_context':r['diagnostic']['diagnostics'].pop('selected_evidence')
    elif missing=='review':r.pop('reviews')
    else:r.pop('admissions')
    result=m.score(manifest,raw,judged,ready,p)
    assert result['verdict']=='INCONCLUSIVE'
    gate='G9' if missing=='judge' else 'G6'
    assert result['gates'][gate]['state']=='NOT_EVALUABLE'


def test_partial_failure_retains_independently_known_citation_violation():
    r=dict(state='COMPLETE',error='provider failure',selected_evidence_snapshot=[dict(evidence_id='page',source_id='sphinx',locator=dict(url='u',snapshot_date='d',section_path=[]))],
           usage=[dict(stage='qa_answer',response={'claims':[dict(claim_id='c',claim_text='Public claim',evidence_ids=['page'])]})],admissions=[],reviews=[])
    c=m.citation(r)
    assert not c['authority_complete'] and len(c['invalid_edges'])==1


def test_blind_input_uses_original_g001_index():
    manifest,raw,_,_,_=fixture();c=manifest['qa_cases'][3]
    c['gold']=dict(required_answer_points=[],allowed_source_versions=[])
    pair={mode:deepcopy(arm(raw,'g001',mode)) for mode in (m.LEGACY,m.RUNTIME)}
    pair[m.RUNTIME]['diagnostic']['result']['answer']='Runtime marker'
    payload=m.a3.judge_input(c,pair,3)
    assert payload['A']['answer']=='Runtime marker'
    assert set(payload)=={'question','approved_reference','A','B'}


def test_ambiguous_record_not_replayed(tmp_path):
    p=tmp_path/'raw.json';m.h.save(p,{'records':[{'execution_id':'x','state':'STARTED'}]})
    with pytest.raises(ValueError,match='ambiguous'):
        m.h.run_records(p,{},[('x',{})],lambda _:pytest.fail('replayed'))


@pytest.mark.parametrize('stage',['_answer','_revise'])
def test_capture_keeps_original_evidence_when_provider_fails(tmp_path,stage):
    from test_qa import FakeRetriever, bundle_for, code_evidence
    class Broken:
        events=[]
        def generate_json(self,*args,**kwargs):
            raise RuntimeError('provider failed')
    bundle=bundle_for(code_evidence(text='Input is a record.'))
    before=deepcopy(bundle)
    agent=m.Capture(tmp_path,retriever=FakeRetriever(bundle),vertex=Broken())
    state=dict(question='Describe input.',bundle=bundle,sufficient=True,draft={'claims':[]},errors=[])
    with pytest.raises(RuntimeError,match='provider failed'):
        getattr(agent,stage)(state)
    assert agent.selected_snapshot==bundle['evidence'] and bundle==before
