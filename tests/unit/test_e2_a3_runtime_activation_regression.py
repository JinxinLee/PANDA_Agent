"""Frozen selector, blinded regression and canonical scoring contracts."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import pytest
s=importlib.util.spec_from_file_location('a3_eval',Path(__file__).resolve().parents[2]/'evaluation/run_e2_a3_runtime_activation_regression.py')
m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)

def fixtures():
    manifest=m.read(m.MANIFEST);cs=manifest['qa_cases'];raw=[];judged=[]
    for i,c in enumerate(cs):
        for mode in (m.LEGACY,m.RUNTIME):
            runtime=mode==m.RUNTIME;n=3 if c.get('pair_id')=='e1a2.pair09' else 2
            points=[dict(answer_point_id=f'point.{j+1}',text=f'Need {j+1}') for j in range(n)]
            diag=dict(plan={},verification_errors=[],revision_count=0)
            if runtime:diag.update(question_decomposition=dict(points=points),answer_point_audit=dict(answer_points=points,claim_mappings=[],covered_answer_point_ids=[],missing_answer_point_ids=[p['answer_point_id'] for p in points],coverage_evaluable=True,coverage_complete=True))
            result=dict(status=c.get('expected_status','answered'),answer='Answer',claims=[],evidence=[],resolved_versions={},verification_errors=[])
            events=[dict(stage='qa_answer',logical_calls=1,adapter_requests=1,returned_model_calls=1,tokens=5)]
            if runtime:events.append(dict(stage='decomposition',logical_calls=1,adapter_requests=1,returned_model_calls=1,tokens=5))
            raw.append(dict(execution_id=c['id']+'.'+mode,case_id=c['id'],mode=mode,state='COMPLETE',diagnostic=dict(result=result,diagnostics=diag,node_timings_ms=dict(workflow=10,question_decomposition=2)),usage=events,trace=['retrieval','verify'],reviews=[]))
        judged.append(dict(execution_id=c['id'],state='COMPLETE',judgment=dict(preferred='equivalent',critical_regression=False,A_supported=True,B_supported=True,reason='same'),usage=[]))
    boot=[dict(execution_id=cid,retrieval_metrics=dict(metrics={'Recall@5':1.,'Recall@10':1.,'Recall@20':1.,'MRR':1.}),usage=[]) for cid in manifest['retrieval_case_ids']]
    return manifest,boot,raw,judged

def test_selector_calibration_counts():
    manifest=m.read(m.MANIFEST);boot,cs=m.validate(manifest)
    assert len(boot)==24 and len(cs)==28
    assert sum(c.get('expected_status')=='answered' for c in cs)==12
    assert sum(c.get('expected_status') in ('insufficient_evidence','version_conflict') for c in cs)==4
    assert 'g105' in manifest['retrieval_case_ids']
    assert len({eid for eid,_ in m.order(cs)})==56
    assert m.order(cs)[0][1]['mode']==m.LEGACY and m.order(cs)[2][1]['mode']==m.RUNTIME

def test_blind_allowlist_and_balanced_assignment():
    manifest,_,raw,_=fixtures();c=manifest['qa_cases'][0];pair={r['mode']:r for r in raw if r['case_id']==c['id']}
    p=m.judge_input(c,pair,0)
    assert set(p)=={'question','approved_reference','A','B'}
    assert set(p['A'])=={'status','answer','claims','evidence'}
    assert all(word not in json.dumps(p) for word in ('answer_point_audit','runtime_e1_v2','legacy_question_core','coverage_complete'))
    assert m.labels(0)['A']==m.LEGACY and m.labels(1)['A']==m.RUNTIME

def test_perfect_score_and_canonical_roundtrip():
    score=m.score(*fixtures())
    assert score['verdict']=='PASS' and all(score['gates'].values())
    assert json.loads(json.dumps(score))==score

def runtime(raw,idx=0):return [r for r in raw if r['mode']==m.RUNTIME][idx]

@pytest.mark.parametrize('gate,change',[
 ('Q2',lambda r:r['diagnostic']['result'].update(status='insufficient_evidence')),
 ('Q7',lambda r:r['diagnostic']['diagnostics']['verification_errors'].append('incomplete code citation e1')),
 ('Q11',lambda r:r['usage'][0].update(adapter_requests=100)),
 ('Q12',lambda r:r['diagnostic']['diagnostics'].update(revision_count=2)),
 ('Q13',lambda r:r['trace'].append('retrieval')),
])
def test_failure_gates(gate,change):
    args=fixtures();change(runtime(args[2]));out=m.score(*args)
    assert not out['gates'][gate] and out['verdict']=='FAIL'

def test_false_answer_and_false_refusal():
    args=fixtures();runtime(args[2],12)['diagnostic']['result']['status']='answered'
    assert not m.score(*args)['gates']['Q3']
    args=fixtures()
    for i in (0,1):runtime(args[2],i)['diagnostic']['result']['status']='insufficient_evidence'
    assert not m.score(*args)['gates']['Q4']

def test_quality_direction_and_ties():
    args=fixtures();args[3][0]['judgment'].update(preferred='A',critical_regression=True)
    out=m.score(*args);assert out['counts']['worse']==1 and out['counts']['equivalent']==27 and not out['gates']['Q5']
    args=fixtures()
    for i in range(3):args[3][i]['judgment']['preferred']='A' if i%2==0 else 'B'
    assert not m.score(*args)['gates']['Q6']

@pytest.mark.parametrize('gate,field',[('Q9','coverage_evaluable'),('Q10','coverage_complete')])
def test_novel_sentinel(gate,field):
    args=fixtures();runtime(args[2],16)['diagnostic']['diagnostics']['answer_point_audit'][field]=False
    assert not m.score(*args)['gates'][gate]

def test_pair09_exact_three():
    args=fixtures();r=next(r for r in args[2] if r['mode']==m.RUNTIME and r['case_id']=='e1a2.b09')
    r['diagnostic']['diagnostics']['question_decomposition']['points'].pop()
    assert not m.score(*args)['gates']['PAIR09']

def test_infrastructure_inconclusive():
    args=fixtures();args[3][0]['error']='timeout'
    assert m.score(*args)['verdict']=='INCONCLUSIVE'

def test_retrieval_canonical_first_rank_metrics():
    out=m.retrieval_from_ranks([1,7,None,15])
    assert out=={'Recall@5':.25,'Recall@10':.5,'Recall@20':.75,'MRR':1.}

@pytest.mark.parametrize('change',[dict(preferred='runtime'),dict(preferred='equivalent',critical_regression=True)])
def test_judge_strict(change):
    v=dict(preferred='A',critical_regression=False,A_supported=True,B_supported=True,reason='supported difference');v.update(change)
    with pytest.raises(ValueError):m.validated_judge(v)

def test_retrieval_model_guard():
    v=object.__new__(m.Meter);v.retrieval_only=True
    with pytest.raises(ValueError):v.generate_json(json.dumps(dict(task='create_atomic_evidence_bound_claims')), {})
