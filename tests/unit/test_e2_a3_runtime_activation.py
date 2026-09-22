"""Dual-mode candidate and selector-only activation checks, no providers."""
from copy import deepcopy
import inspect
import json
import subprocess
import sys
import types
import pytest
from panda_agent import qa, question_decomposition
from panda_agent.models import QAResult,ClaimCitation
from test_e2_a1_answer_point_coverage import agent,Vertex,claim,review,QUESTION,POINTS
START='ffedb2117f578515ea9d74eca92105956b8a3dcb'

def test_current_default_is_bounded_production_obligation_mode():
    assert qa.DEFAULT_ANSWER_POINT_MODE=='production_answer_obligations_v1'

def test_legacy_matches_starting_implementation(tmp_path):
    source=subprocess.check_output(['git','show',START+':src/panda_agent/qa.py'],text=True,encoding='utf-8')
    old=types.ModuleType('qa_pre_a3');sys.modules[old.__name__]=old;exec(compile(source,'qa_pre_a3','exec'),old.__dict__)
    rs={k:v for k,v in review().items() if k in qa.REVIEW_SCHEMA}
    rs={k:v for k,v in review().items() if k in qa.REVIEW_SCHEMA['required']}
    va=Vertex(answers=[claim(point='question_core')],reviews=[deepcopy(rs)])
    vb=Vertex(answers=[claim(point='question_core')],reviews=[deepcopy(rs)])
    a=agent(tmp_path,va);b=old.QAAgent(tmp_path,retriever=deepcopy(a.retriever),vertex=vb)
    out=a._run_detailed(QUESTION,mode='legacy_question_core');baseline=b.run_detailed(QUESTION)
    assert out['result']==baseline['result']
    assert all(key in out['diagnostics'] and out['diagnostics'][key]==value
               for key,value in baseline['diagnostics'].items())
    assert len(va.calls)==len(vb.calls)==2
    assert [call[2]['usage_stage'] for call in va.calls]==[
        'qa_generation', 'qa_semantic_verification',
    ]
    for current,historical in zip(va.calls,vb.calls):
        assert current[:2]==historical[:2]
        assert {key:value for key,value in current[2].items() if key!='usage_stage'}==historical[2]

def test_shadow_and_runtime_exact_semantic_path(tmp_path):
    a=agent(tmp_path);b=agent(tmp_path)
    shadow=a.run_answer_point_coverage_diagnostic(QUESTION);runtime=b._run_detailed(QUESTION,mode='runtime_e1_v2')
    assert a.vertex.calls==b.vertex.calls
    assert shadow['result']==runtime['result']
    sa=shadow['diagnostics']['answer_point_audit'];ra=runtime['diagnostics']['answer_point_audit']
    assert sa.pop('mode')=='shadow_e1_v2' and ra.pop('mode')=='runtime_e1_v2'
    assert sa==ra

@pytest.mark.parametrize('entry',['run','run_detailed'])
def test_runtime_default_selector_only(monkeypatch,tmp_path,entry):
    monkeypatch.setattr(qa,'DEFAULT_ANSWER_POINT_MODE','runtime_e1_v2')
    a=agent(tmp_path);out=getattr(a,entry)(QUESTION)
    assert [x[0]['task'] for x in a.vertex.calls].count('decompose_user_question')==1
    result=out['result'] if entry=='run_detailed' else out.model_dump(mode='json')
    assert set(result)==set(QAResult.model_fields)
    if entry=='run_detailed':assert out['diagnostics']['answer_point_audit']['mode']=='runtime_e1_v2'
    assert set(ClaimCitation.model_fields)=={'claim_id','claim_text','evidence_ids'}

def test_runtime_one_revision_without_retrieval(tmp_path):
    v=Vertex(answers=[claim()],reviews=[review({'c1':['point.1']},missing=['point.2']),review({'c1':['point.1'],'c2':['point.2']})],revisions=[claim('c2','point.2','The output is a table.')])
    a=agent(tmp_path,v);out=a._run_detailed(QUESTION,mode='runtime_e1_v2')
    assert a.retriever.calls==1 and out['diagnostics']['revision_count']==1
    assert out['diagnostics']['answer_point_audit']['coverage_complete']

def test_failure_no_fallback(tmp_path):
    a=agent(tmp_path)
    def failed(q):raise ValueError('decomposition failure')
    a.decompose_question=failed
    with pytest.raises(ValueError):a._run_detailed(QUESTION,mode='runtime_e1_v2')
    assert a.retriever.calls==0

def test_selector_not_public_api(tmp_path):
    assert list(inspect.signature(qa.QAAgent.run).parameters)==['self','question']
    assert list(inspect.signature(qa.QAAgent.run_detailed).parameters)==['self','question']
    with pytest.raises(ValueError):agent(tmp_path)._run_detailed(QUESTION,mode='invented')

def test_compatibility_modes_keep_v2_contract_separate_from_production():
    assert qa._ANSWER_POINT_MODES == {
        'legacy_question_core', 'shadow_e1_v2', 'runtime_e1_v2',
        'production_answer_obligations_v1',
    }
    for mode in qa._ANSWER_POINT_MODES:
        state = {'answer_point_coverage_mode': mode}
        assert qa._coverage_shadow(state) == (mode != 'legacy_question_core')
        assert qa._coverage_satisfaction_enabled(state) == (mode == 'production_answer_obligations_v1')
    assert question_decomposition.QUESTION_DECOMPOSITION_V2_PROMPT_VERSION == '2.0.0'
    assert question_decomposition.QUESTION_DECOMPOSITION_V2_SCHEMA_VERSION == 'e1.question_decomposition.v2'
    assert question_decomposition.QUESTION_DECOMPOSITION_SYSTEM_PROMPT.startswith(
        question_decomposition.QUESTION_DECOMPOSITION_V2_SYSTEM_PROMPT)
    assert question_decomposition.QUESTION_DECOMPOSITION_V2_SCHEMA is question_decomposition.QUESTION_DECOMPOSITION_SCHEMA
    v2_fields = qa.ANSWER_POINT_COVERAGE_REVIEW_SCHEMA['properties']['answer_point_coverage']['items']['properties']
    production_fields = qa.PRODUCTION_COVERAGE_SATISFACTION_REVIEW_SCHEMA['properties']['answer_point_coverage']['items']['properties']
    assert 'required_relation_checks' not in v2_fields
    assert 'required_relation_checks' in production_fields
