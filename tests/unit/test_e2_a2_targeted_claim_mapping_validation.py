"""Offline E2-A2 boundaries and hand-computed scoring fixtures."""
from copy import deepcopy
import importlib.util
import json
import sys
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('e2a2',Path(__file__).resolve().parents[2]/'evaluation/run_e2_a2_targeted_claim_mapping_validation.py')
m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m)

def fixture(rep='rep1',i=0):
    points=[dict(answer_point_id='point.1',text='Input'),dict(answer_point_id='point.2',text='Output')]
    claims=[dict(claim_id='c1',claim_text='Input claim',evidence_ids=['e1']),dict(claim_id='c2',claim_text='Output claim',evidence_ids=['e2'])]
    mappings=[dict(claim_id=c['claim_id'],declared_answer_point_ids=[p['answer_point_id']],verified_answer_point_ids=[p['answer_point_id']],evidence_ids=c['evidence_ids'],supported=True,rendered=True) for c,p in zip(claims,points)]
    a=dict(answer_points=points,claim_mappings=mappings,covered_answer_point_ids=['point.1','point.2'],missing_answer_point_ids=[],coverage_evaluable=True,coverage_complete=True,review_error=None)
    raw=dict(execution_id=f'{i}.{rep}',repetition=rep,pair_id=m.PAIRS[i%6],source_case_id=m.SOURCE_IDS[i%6],variant='base',question='Input and output?',reviews=[],usage=[],
        final_state=dict(runtime_answer_points=points,answer_point_audit=a,result=dict(status='answered',claims=claims),bundle=dict(evidence=[]),draft=dict(claims=[{**c,'answer_point_ids':x['declared_answer_point_ids']} for c,x in zip(claims,mappings)])))
    judgment=dict(alignments=[dict(answer_point_id=p['answer_point_id'],reference_slot_id=f'slot.{i+1}') for i,p in enumerate(points)],missing_reference_slot_ids=[],extra_answer_point_ids=[],claim_mappings=[dict(claim_id=x['claim_id'],answer_point_ids=x['verified_answer_point_ids']) for x in mappings],covered_answer_point_ids=['point.1','point.2'],missing_answer_point_ids=[])
    return raw,dict(execution_id=raw['execution_id'],judgment=deepcopy(judgment),usage=[])

def test_source_and_identities():
    cs=m.validate_manifest(m.read(m.MANIFEST))
    assert len(cs)==12 and len(m.identities(cs))==24
    assert {c['pair_id'] for c in cs}==set(m.PAIRS)
    assert sum(len(c['reference_points']) for c in cs)==28

@pytest.mark.parametrize('key,value',[('repetitions',['rep1']),('protected_data_access',True),('implementation','wrong'),('source_path','forbidden'),('selected_pair_ids',[]),('source_case_ids',[])])
def test_manifest_rejects_drift(key,value):
    manifest=deepcopy(m.read(m.MANIFEST));manifest[key]=value
    with pytest.raises(ValueError):m.validate_manifest(manifest)

def test_judge_allowlist():
    r,j=fixture();c=dict(reference_points=[dict(reference_slot_id='slot.1',text='Input',facet_type='secret')])
    p=m.judge_input(r,c)
    assert set(p)=={'question','reference_slots','runtime_answer_points','claims'}
    assert all(set(c)=={'claim_id','claim_text'} for c in p['claims'])
    assert all(set(c)=={'answer_point_id','text'} for c in p['runtime_answer_points'])
    assert 'verified' not in json.dumps(p) and 'facet_type' not in json.dumps(p)

def payload(r):
    return dict(runtime_answer_points=r['final_state']['runtime_answer_points'],reference_slots=[dict(reference_slot_id='slot.1'),dict(reference_slot_id='slot.2')],claims=m.visible_claims(r))

def test_judge_good():
    r,j=fixture();assert m.validate_judge(j['judgment'],payload(r))==j['judgment']

@pytest.mark.parametrize('kind',['unknown_point','duplicate','missing_claim','overlap','unmatched','covered_unmapped'])
def test_bad_judge_is_infrastructure(kind):
    r,j=fixture();v=j['judgment']
    if kind=='unknown_point':v['claim_mappings'][0]['answer_point_ids']=['bad']
    if kind=='duplicate':v['claim_mappings'].append(v['claim_mappings'][0])
    if kind=='missing_claim':v['claim_mappings'].pop()
    if kind=='overlap':v['missing_answer_point_ids']=['point.1']
    if kind=='unmatched':v['missing_reference_slot_ids']=['slot.1']
    if kind=='covered_unmapped':v['claim_mappings'][1]['answer_point_ids']=[]
    with pytest.raises(ValueError):m.validate_judge(v,payload(r))

def test_applicability_reasons():
    r,j=fixture();assert m.applicability(r,j)==(True,'APPLICABLE')
    j['judgment']['extra_answer_point_ids']=['point.3'];assert m.applicability(r,j)[1]=='UPSTREAM_E1_INPUT_INVALID'
    j['error']='timeout';assert m.applicability(r,j)[1]=='JUDGE_INFRASTRUCTURE'
    r['reviews']=[dict(output=dict(answer_point_audit=dict(review_error='bad mapping')))];assert m.applicability(r,j)[1]=='COVERAGE_REVIEW_STRUCTURAL_INVALID'

def test_last_target_and_no_rewrite():
    r,j=fixture();entry=m.derive([r],[j])[0]
    assert entry['target']=='point.2' and entry['removed_claim_ids']==['c2']
    state=m.controlled_state(r,entry['retained_claim_ids'])
    assert state['draft']['claims']==r['final_state']['draft']['claims'][:1]
    assert state['bundle']==r['final_state']['bundle']
    assert 'target' not in state and 'baseline_truth' not in state

def test_shared_claim_disqualifies_all_its_points():
    r,j=fixture();j['judgment']['claim_mappings'][1]['answer_point_ids']=['point.1','point.2']
    assert m.derive([r],[j])[0]['reason']=='NO_ISOLATABLE_DROP_TARGET'

def test_last_nonempty_exclusive_target_and_rep1_only():
    r,j=fixture();j['judgment']['claim_mappings'][1]['answer_point_ids']=[]
    assert m.derive([r],[j])[0]['target']=='point.1'
    r['repetition']='rep2';assert m.derive([r],[j])==[]

@pytest.mark.parametrize('reason',['BASELINE_NOT_APPLICABLE','BASELINE_NOT_COMPLETE','LESS_THAN_TWO_POINTS'])
def test_drop_ineligibility(reason):
    r,j=fixture()
    if reason=='BASELINE_NOT_APPLICABLE':r['final_state']['answer_point_audit']['coverage_evaluable']=False
    if reason=='BASELINE_NOT_COMPLETE':j['judgment']['missing_answer_point_ids']=['point.1']
    if reason=='LESS_THAN_TWO_POINTS':r['final_state']['runtime_answer_points'].pop()
    assert m.derive([r],[j])[0]['reason']==reason

def experiment():
    pairs=[fixture(rep,i) for rep in ('rep1','rep2') for i in range(12)]
    raws=[r for r,j in pairs];judged=[j for r,j in pairs];drops=m.derive(raws,judged)
    controls=[dict(execution_id=e['execution_id'],output=dict(answer_point_audit=dict(missing_answer_point_ids=e['expected_missing_answer_point_ids'],answer_points=e['runtime_answer_points'])),usage=[]) for e in drops]
    return raws,judged,drops,controls

def test_full_hand_computed_pass():
    args=experiment();r=m.score(*args)
    assert r['verdict']=='PASS' and all(r['gates'].values())
    assert r['natural']['counts']['mapping_tp']==48 and r['controlled']['counts']['detected']==12

def test_micro_edge_precision_and_exact_sets():
    args=experiment();args[0][0]['final_state']['answer_point_audit']['claim_mappings'][0]['verified_answer_point_ids'].append('point.2')
    r=m.score(*args)
    assert r['natural']['N2']==48/49 and r['natural']['N3']==1 and r['natural']['N4']==47/48

def test_mapping_does_not_imply_coverage():
    args=experiment();args[1][0]['judgment']['covered_answer_point_ids']=['point.1'];args[1][0]['judgment']['missing_answer_point_ids']=['point.2']
    r=m.score(*args)
    assert r['natural']['N5']==47/48 and r['natural']['N6']==1
    assert r['natural']['counts']['false_covered']==1

def test_controlled_collateral_and_empty_metrics():
    args=experiment();args[3][0]['output']['answer_point_audit']['missing_answer_point_ids']=['point.1','point.2']
    args[3][1]['output']['answer_point_audit']['missing_answer_point_ids']=[]
    r=m.score(*args)
    assert r['controlled']['D2']==11/12 and r['controlled']['D3']==11/12 and r['controlled']['D4']==10/12
    assert r['controlled']['counts']['collateral']==1

def test_insufficiency_and_structural_failure_precedence():
    args=experiment();args[1][0]['error']='judge timeout';assert m.score(*args)['verdict']=='INCONCLUSIVE'
    args[0][0]['reviews']=[dict(output=dict(answer_point_audit=dict(review_error='invalid')))];assert m.score(*args)['verdict']=='FAIL'

def test_empty_denominator_not_perfect():
    assert m.ratio(0,0) is None

def test_controlled_guard():
    vertex=object.__new__(m.Meter);vertex.controlled=True;vertex.judge=False
    with pytest.raises(ValueError):vertex.generate_json(json.dumps(dict(task='create_atomic_evidence_bound_claims')), {})
    with pytest.raises(ValueError):vertex.embed_query('query')
    with pytest.raises(RuntimeError):m.ForbiddenRetriever().retrieve('query')

def test_resume_never_repeats_complete_or_ambiguous(tmp_path):
    path=tmp_path/'raw.json';calls=[]
    m.run_records(path,{},[('a',{})],lambda r:calls.append(1))
    m.run_records(path,{},[('a',{})],lambda r:calls.append(1));assert len(calls)==1
    m.save(path,dict(records=[dict(execution_id='a',state='STARTED')]))
    with pytest.raises(ValueError):m.run_records(path,{},[('a',{})],lambda r:calls.append(1))

def test_invariant_unknown_accepted_id():
    r,j=fixture();r['final_state']['answer_point_audit']['covered_answer_point_ids'].append('bad')
    assert m.invariant_violations([r],[])==['INVALID_POINT_IDS_ACCEPTED']


def test_capture_and_actual_controlled_review_seam(tmp_path):
    from test_e2_a1_answer_point_coverage import Vertex, QUESTION, review
    from test_qa import FakeRetriever, bundle_for, code_evidence
    v=Vertex();v.events=[]
    a=m.CaptureAgent(tmp_path,vertex=v,retriever=FakeRetriever(bundle_for(code_evidence(text="The input is a record. The output is a table.",path="input.h"))))
    a.run_answer_point_coverage_diagnostic(QUESTION)
    raw=dict(question=QUESTION,final_state=a.final_state,locked_identifiers={k:sorted(x) for k,x in a._locked_identifier_symbols.items()})
    json.dumps(raw)
    assert len(a.reviews)==1 and a.decomposition
    class ControlledVertex(Vertex):
        controlled=True
        def __init__(self):
            super().__init__(reviews=[review({'c1':['point.1']},missing=['point.2'])]);self.events=[]
        def generate_json(self,*args,**kwargs):
            self.events.append(dict(stage='controlled_review'))
            return super().generate_json(*args,**kwargs)
    cv=ControlledVertex()
    out=m.run_controlled(raw,dict(retained_claim_ids=['c1']),cv)
    assert out['missing_answer_point_ids']==['point.2']
    assert len(cv.calls)==1
