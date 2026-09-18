"""Dual-mode candidate and selector-only activation checks, no providers."""
import ast
from copy import deepcopy
import inspect
import json
from pathlib import Path
import subprocess
import sys
import types
import pytest
from panda_agent import qa
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
    assert out['result']==baseline['result'] and out['diagnostics']==baseline['diagnostics']
    assert va.calls==vb.calls and len(va.calls)==2

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

def test_compatibility_graph_and_prompts_unchanged():
    root=Path(__file__).resolve().parents[2]
    old=ast.parse(subprocess.check_output(['git','show',START+':src/panda_agent/qa.py'],text=True,encoding='utf-8'))
    new=ast.parse((root/'src/panda_agent/qa.py').read_text(encoding='utf-8'))
    names={'_answer_requirements','_requirement_evidence','_deterministic_missing_requirement_ids','__init__','_retrieve','_sufficiency','_targeted_retrieve'}
    def nodes(tree):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name in names}
    assert nodes(old)==nodes(new)
    for path in ('src/panda_agent/prompts.py','src/panda_agent/models.py','src/panda_agent/question_decomposition.py','src/panda_agent/retrieval.py'):
        assert not subprocess.check_output(['git','diff',START,'--',path],text=True)
