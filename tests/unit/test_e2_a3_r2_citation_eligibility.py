"""Offline evidence admission and preregistered scorer guardrails."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import sys

import pytest

from panda_agent import qa

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('r2_validation_tests', ROOT / 'evaluation/run_e2_a3_r2_citation_eligibility_validation.py')
r2 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = r2
spec.loader.exec_module(r2)


@pytest.mark.parametrize('missing', [None, 'url', 'snapshot_date', 'section_path'])
def test_sphinx_contract(missing):
    evidence = dict(source_id='project_sphinx', locator=dict(url='https://example.invalid/a', snapshot_date='2000-01-01', section_path=['A', 'B']))
    if missing:
        evidence['locator'][missing] = [] if missing == 'section_path' else None
    assert qa._is_public_claim_citation_eligible(evidence) == (missing is None)


@pytest.mark.parametrize('source', ['code', 'paper', 'curated_domain'])
@pytest.mark.parametrize('locator', [None, {}, {'path': 'file.h'}])
def test_non_sphinx_admission_unchanged(source, locator):
    assert qa._is_public_claim_citation_eligible(dict(source_id=source, locator=locator))


def test_answer_revision_auxiliary_mapping_and_original_bundle():
    result = r2.admission_probe()
    assert result['answer_ids'] == result['revision_ids'] == ['section', 'code']
    assert result['revision_requirement_ids'] == ['section', 'code']
    assert result['original_bundle_unchanged']
    assert any('incomplete web citation' in error for error in result['verifier_errors'])


def test_complete_frozen_reconciliation_and_exact_scope():
    result = r2.static_result()
    assert all(result['gates'].values())
    assert (result['selected_sphinx_occurrences'], result['complete'], result['ineligible_excluded']) == (144, 106, 38)
    assert result['eligible_incorrectly_excluded'] == 0
    assert (result['claim_edges'], result['complete_claim_edges'], len(result['invalid_claim_edges'])) == (27, 24, 3)
    assert result['final_claim_edges'] == result['final_complete_claim_edges'] == 18


def fake_science():
    cases = [dict(id=cid, expected_status='answered') for cid in r2.IDS]
    raw, judged = [], []
    for i, c in enumerate(cases):
        for mode in (r2.LEGACY, r2.RUNTIME):
            usage = [dict(stage='qa_answer', logical_calls=1, adapter_requests=1, returned_model_calls=1, response={'claims': []})]
            if mode == r2.RUNTIME:
                usage.append(dict(stage='decomposition', logical_calls=1, adapter_requests=1, returned_model_calls=1))
            raw.append(dict(execution_id=c['id'] + ':' + mode, case_id=c['id'], mode=mode, state='COMPLETE', usage=usage,
                            admissions=[dict(task='create_atomic_evidence_bound_claims', evidence_ids=[], requirement_evidence_ids={})],
                            trace=['retrieval', 'verify'], reviews=[],
                            diagnostic=dict(result=dict(status='answered', answer='Supported.', claims=[], evidence=[], resolved_versions={}, verification_errors=[]),
                                            diagnostics=dict(selected_evidence=[], revision_count=0, question_decomposition={'points': [dict(answer_point_id='point.1', text='Describe input.')]},
                                                             answer_point_audit=dict(coverage_evaluable=True, coverage_complete=True)))))
        judged.append(dict(execution_id=c['id'], state='COMPLETE', judgment=dict(preferred='equivalent', critical_regression=False, A_supported=True, B_supported=True, reason='Equal supported answers.'), usage=[]))
    return {'qa_cases': cases}, raw, judged, {'gates': {f'S{i}': True for i in range(1, 14)}}


def test_noncritical_worse_is_diagnostic_but_unsupported_equivalent_fails():
    m, raw, judges, static = fake_science()
    judges[0]['judgment']['preferred'] = 'A'
    result = r2.score(m, raw, judges, static)
    assert result['verdict'] == 'PASS'
    assert result['counts']['worse'] == 1
    judges[0]['judgment'].update(preferred='equivalent', B_supported=False)
    result = r2.score(m, raw, judges, static)
    assert result['verdict'] == 'FAIL' and not result['gates']['P10']


@pytest.mark.parametrize('stage', ['qa_answer', 'qa_revision'])
@pytest.mark.parametrize('mode', [r2.LEGACY, r2.RUNTIME])
def test_all_response_stages_and_both_arms_enforce_eligibility(stage, mode):
    m, raw, judges, static = fake_science()
    record = next(r for r in raw if r['case_id'] == 'g013' and r['mode'] == mode)
    page = dict(evidence_id='page', source_id='sphinx', locator=dict(url='https://example.invalid', snapshot_date='2000-01-01', section_path=[]))
    record['diagnostic']['diagnostics']['selected_evidence'] = [page]
    record['usage'].append(dict(stage=stage, logical_calls=1, response={'claims': [dict(claim_id='bad', claim_text='Public claim.', evidence_ids=['page'])]}))
    record['admissions'].append(dict(task=stage, evidence_ids=[], requirement_evidence_ids={}))
    result = r2.score(m, raw, judges, static)
    assert result['verdict'] == 'FAIL' and not result['gates']['P2']
    assert len(result['invalid_public_claim_edges']) == 1


def test_early_review_errors_are_not_hidden_by_clean_final_review():
    m, raw, judges, static = fake_science()
    raw[1]['reviews'] = [dict(errors=['claim: incomplete web citation']), dict(errors=[])]
    result = r2.score(m, raw, judges, static)
    assert not result['gates']['P3'] and not result['gates']['P7']
    assert result['verdict'] == 'FAIL'


def test_provider_or_judge_missing_is_inconclusive():
    m, raw, judges, static = fake_science()
    judges[0]['error'] = 'Provider unavailable'
    assert r2.score(m, raw, judges, static)['verdict'] == 'INCONCLUSIVE'


def test_admission_capture_must_match_projection_and_auxiliary_ids():
    m, raw, judges, static = fake_science()
    raw[0]['admissions'][0]['requirement_evidence_ids'] = {'requirement': ['not-admitted']}
    result = r2.score(m, raw, judges, static)
    assert not result['gates']['P2']


def test_judge_boundary_is_public_allowlist():
    m, raw, judges, static = fake_science()
    case = dict(m['qa_cases'][0], source='Gold', question='Describe input.', gold=dict(required_answer_points=[], allowed_source_versions=[]))
    pair = {r['mode']: r for r in raw if r['case_id'] == 'g013'}
    payload = r2.a3.judge_input(case, pair, 0)
    assert set(payload) == {'question', 'approved_reference', 'A', 'B'}
    assert set(payload['A']) == set(payload['B']) == {'status', 'answer', 'claims', 'evidence'}
    assert 'runtime_e1_v2' not in str(payload)
