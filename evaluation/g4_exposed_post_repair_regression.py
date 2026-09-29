"""Read-only exposed G4 comparison, optionally selecting an authorized target rerun."""
from __future__ import annotations
import argparse
import json
from panda_agent.evaluation import aggregate_metrics
from collections import Counter
from pathlib import Path

OLD_RUN = 'g3-evidence-admission-audit-novel-dev-v1'
NEW_RUN = 'g4-r2-post-repair-novel-dev-regression-v1'
TARGET_RERUN = 'g4-r2-post-repair-n002-n018-rerun-v1'
LINEAGE = 'a22c8f70eeebe4a53490e11a4b6852561ca8afa6'
OLD_LINEAGE = 'a0106bd5eff93646f34f5e50e161e8be8a49d680'
TARGET_OBJECTS = {
    'n002': ['object.a45779701b982aff3e7554da', 'object.03af96b1110e782792253a18'],
    'n006': ['object.2914485ff398f61e994c46d6'],
    'n017': ['object.015bff352e03a5f5ee88c307', 'object.10bfbd3c5c5a222bcdf5904d'],
}
CATEGORIES = ['ANSWERED_COMPLETE', 'ANSWERED_INCOMPLETE', 'INSUFFICIENT_EVIDENCE', 'VERSION_CONFLICT', 'OTHER_ERROR']

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def snapshot(record):
    result = record.get('result', {})
    diag = record.get('diagnostics', {})
    audit = diag.get('answer_point_audit', {})
    canonical = {p['answer_point_id'] for p in audit.get('answer_points', [])}
    covered = set(audit.get('covered_answer_point_ids') or []) & canonical
    validation = audit.get('coverage_validation') or {}
    coverage = len(covered) / len(canonical) if canonical else None
    missing = sorted(canonical - covered)
    complete = (coverage == 1.0 and not missing and audit.get('coverage_complete') is True
                and validation.get('status') == 'VALID' and not validation.get('whole_review_rejected'))
    checks = {(p['answer_point_id'], r.get('relation_id')): r
              for p in (audit.get('answer_point_coverage') or [])
              for r in p.get('required_relation_checks', [])}
    states = {(p['answer_point_id'], r.get('relation_id')): r.get('state')
              for p in validation.get('point_results', []) for r in p.get('relations', [])}
    missing_relations = []
    for point in audit.get('answer_points', []):
        for relation in point.get('required_relations', []):
            key = (point['answer_point_id'], relation['relation_id'])
            if point['answer_point_id'] not in covered and not checks.get(key, {}).get('satisfied'):
                missing_relations.append({'answer_point_id':key[0], 'relation_id':key[1],
                    'validation_state':states.get(key), 'admission_state':checks.get(key, {}).get('admission_state')})
    status = result.get('status', 'error')
    category = ('ANSWERED_COMPLETE' if complete else 'ANSWERED_INCOMPLETE') if status == 'answered' else {
        'insufficient_evidence': 'INSUFFICIENT_EVIDENCE', 'version_conflict': 'VERSION_CONFLICT'
    }.get(status, 'OTHER_ERROR')
    pool = diag.get('rerank_pool_entries')
    reasons = Counter(p['reason'] for p in pool or [])
    metrics = record.get('metrics', {})
    cited = {eid for c in result.get('claims', []) for eid in c.get('evidence_ids', [])}
    evidence = [{k: e.get(k) for k in ['evidence_id', 'object_id', 'source_id', 'source_version_id', 'locator']}
                | {'cited': e.get('evidence_id') in cited} for e in result.get('evidence', [])]
    final_claim_ids = {c['claim_id'] for c in result.get('claims', [])}
    reviews = [e for e in diag.get('qa_stage_trace', {}).get('events', [])
               if e['stage'] in ['V1_OUTPUT', 'V2_OUTPUT'] and e['status'] == 'CAPTURED']
    response = reviews[-1]['payload'].get('response', {}) if reviews else None
    runtime_unsupported = sorted(final_claim_ids & set(response.get('unsupported_claim_ids', []))) if response else None
    return {
        'status': status, 'category': category, 'expected_status': record.get('expected_status'),
        'expected_status_correct': metrics.get('expected_status_correct'),
        'runtime_answer_point_coverage': coverage, 'runtime_covered_point_ids': sorted(covered),
        'runtime_missing_required_point_ids': missing, 'runtime_coverage_validation': validation.get('status'),
        'runtime_missing_relations': missing_relations,
        'runtime_final_claims_flagged_unsupported': runtime_unsupported,
        'verification_errors': result.get('verification_errors', []),
        'metrics': {k:metrics.get(k) for k in ['citation_integrity',
            'hallucinated_identifiers', 'identifier_mentions', 'wrong_version_evidence', 'forbidden_evidence',
            'required_source_coverage', 'final_evidence_recall', 'critical_final_evidence_recall']},
        'pool_observed': pool is not None, 'pool_reason_counts': dict(reasons),
        'frontier_used': (reasons['policy_role_frontier'] > 0) if pool is not None else None, 'trace_capture_status': diag.get('qa_stage_trace', {}).get('capture_status'),
        'evidence': evidence, 'selected_evidence_ids': diag.get('selected_evidence_ids', []),
        'exception': record.get('exception'),
    }

def safety(rows):
    output = {}
    for name, key in [('citation_failure', 'citation_integrity'), ('identifier_hallucination', 'hallucinated_identifiers'),
                      ('wrong_version', 'wrong_version_evidence'), ('forbidden_evidence', 'forbidden_evidence'),
                      ('required_source_failure', 'required_source_coverage')]:
        ids = [id for id,r in rows.items() if (r['metrics'][key] is False if key in ['citation_integrity','required_source_coverage'] else bool(r['metrics'][key]))]
        output[name] = {'case_count':len(ids), 'case_ids':sorted(ids)}
    mentions = sum(len(r['metrics']['identifier_mentions'] or []) for r in rows.values())
    hallucinations = sum(len(r['metrics']['hallucinated_identifiers'] or []) for r in rows.values())
    output['identifier_hallucination_rate'] = {'hallucinated_mentions':hallucinations,'total_mentions':mentions,'rate':hallucinations/mentions if mentions else 0.0}
    output['gold_semantic_metrics'] = {k:{'value':None,'reason':'Not measured by qa mode without external judge'} for k in [
        'answer_point_coverage','critical_answer_points_missing','unsupported_claim_ids','major_unsupported_claim_ids','minor_unsupported_claim_ids','contradictions']}
    output['runtime_missing_required_points'] = {'total':sum(len(r['runtime_missing_required_point_ids']) for r in rows.values()),
        'case_ids':sorted(id for id,r in rows.items() if r['runtime_missing_required_point_ids'])}
    output['runtime_final_claims_flagged_unsupported'] = {id:r['runtime_final_claims_flagged_unsupported'] for id,r in rows.items() if r['runtime_final_claims_flagged_unsupported']}
    return output

def collateral_pool_loss(root):
    old_dir=root/'data/evaluation/runs'/OLD_RUN
    new_dir=root/'data/evaluation/runs'/NEW_RUN
    if not (new_dir/'records/n024.json').exists():
        return None
    obj='object.d6ef560b88c3926ecb32d3e1'
    a,b=read(old_dir/'records/n024.json'),read(new_dir/'records/n024.json')
    old_entry=next(e for e in read(old_dir/'traces/n024.json')['fused_candidates'] if e['object_id']==obj)
    new_entry=next(e for e in read(new_dir/'traces/n024.json')['fused_candidates'] if e['object_id']==obj)
    return {'object_id':obj,'locator':old_entry['locator'],'all_channel_rankings_identical':a['diagnostics']['rankings']==b['diagnostics']['rankings'],
        'old_fused_trace_entry':old_entry,'new_fused_trace_entry':new_entry,
        'old_reranked_rank_1based':a['diagnostics']['reranked_object_ids'].index(obj)+1,
        'old_in_final_evidence':obj in [e['object_id'] for e in a['result']['evidence']],
        'new_in_pool':obj in [e['object_id'] for e in b['diagnostics']['rerank_pool_entries']],
        'new_in_final_evidence':obj in [e['object_id'] for e in b['result']['evidence']],
        'new_pool_counts':dict(Counter(e['reason'] for e in b['diagnostics']['rerank_pool_entries'])),
        'cause':'R2: relevant ordinary RRF rank 18 is displaced by the bounded frontier offer; final analytic-helix explanation is missing',
        'pool_displacement_confidence':'HIGH: identical channel rankings and identical authoritative RRF trace entry; actual new pool excludes it',
        'qa_causal_limit':'Observed QA transition is not a deterministic paired causal effect estimate; no new reranker/answer counterfactual was run'}

def analyze(root, rerun_run_id=None):
    runs = root/'data/evaluation/runs'
    old_manifest, new_manifest = read(runs/OLD_RUN/'manifest.json'), read(runs/NEW_RUN/'manifest.json')
    old = {p.stem: snapshot(read(p)) for p in (runs/OLD_RUN/'records').glob('*.json')}
    selected_paths = {p.stem:p for p in (runs/NEW_RUN/'records').glob('*.json')}
    initial_rows = {id:snapshot(read(path)) for id,path in selected_paths.items()}
    rerun_manifest = None
    if rerun_run_id:
        assert rerun_run_id == TARGET_RERUN, 'Only the reviewed, explicitly authorized target rerun is supported'
        rerun_manifest = read(runs/rerun_run_id/'manifest.json')
        assert set(rerun_manifest['case_ids']) == {'n002', 'n018'}
        assert rerun_manifest['mode'] == 'qa' and rerun_manifest['split'] == 'novel_dev'
        assert rerun_manifest['capture_stage_trace'] and not rerun_manifest['official'] and not rerun_manifest.get('candidate_id')
        for key in ['source_manifest_hash','normalized_manifest_hash','normalized_output_hashes','index_identity',
                    'index_identity_payload','gold_dataset_hash','gold_benchmark_version','prompt_hash',
                    'generation_model_id','embedding_model_id','retrieval_policy_hash','query_expansion_hash','package_versions']:
            assert rerun_manifest[key] == new_manifest[key], key
        replacement_paths = {p.stem:p for p in (runs/rerun_run_id/'records').glob('*.json')}
        assert set(replacement_paths) == {'n002', 'n018'}
        selected_paths.update(replacement_paths)
    new = {id:snapshot(read(path)) for id,path in selected_paths.items()}
    expected_ids = old_manifest['case_ids']
    for row in new.values():
        row['production_category'] = row['category']
        row['manual_critical_answer_points_missing'] = []
    if 'n006' in new and new['n006']['status'] == 'answered':
        # Bounded human review: independently adjudicated suffix literals are absent.
        # This narrows the production success label; raw evaluator records stay intact.
        new['n006']['manual_critical_answer_points_missing'] = ['p2']
        new['n006']['category'] = 'ANSWERED_INCOMPLETE'
        new['n006']['manual_review_ref'] = 'analyst_review.n006; novel_dev.yaml#n006.p2; prior G4 answerability review'
    if rerun_run_id and new['n018']['status'] == 'answered':
        # Bounded rerun review: the saved answer omits null checking and full-tree
        # preparation required by the unchanged Gold and its cited tutorial.
        new['n018']['manual_critical_answer_points_missing'] = ['p1', 'p2']
        new['n018']['category'] = 'ANSWERED_INCOMPLETE'
        new['n018']['manual_review_ref'] = 'analyst_review.n018; novel_dev.yaml#n018.p1,p2; rerun cited MC truth tutorial'

    assert set(new) <= set(expected_ids) and len(expected_ids) == 28
    assert new_manifest['repository_identity'] == {'commit':LINEAGE, 'dirty':False}
    assert new_manifest['capture_stage_trace'] and not new_manifest['official'] and not new_manifest.get('candidate_id')
    keys = ['source_manifest_hash','normalized_manifest_hash','normalized_output_hashes','index_identity','gold_dataset_hash',
            'gold_benchmark_version','prompt_hash','generation_model_id','embedding_model_id','retrieval_policy_hash','query_expansion_hash']
    matches = {k:old_manifest[k] == new_manifest[k] for k in keys}
    assert all(matches.values())
    matrix = {a:{b:0 for b in CATEGORIES} for a in CATEGORIES}
    cases=[]
    for id in sorted(new):
        a,b=old[id],new[id];matrix[a['category']][b['category']]+=1
        cases.append({'id':id,'old':{k:v for k,v in a.items() if k not in ['evidence','selected_evidence_ids']},'new':{k:v for k,v in b.items() if k not in ['evidence','selected_evidence_ids']},'old_record_ref':str((runs/OLD_RUN/'records'/f'{id}.json').relative_to(root)),
            'new_record_ref':str(selected_paths[id].relative_to(root))})
    attempts=[json.loads(line) for line in (runs/NEW_RUN/'attempts.jsonl').read_text(encoding='utf-8').splitlines() if line]
    initial_attempts = list(attempts)
    rerun_attempts = []
    if rerun_run_id:
        rerun_attempts = [json.loads(line) for line in (runs/rerun_run_id/'attempts.jsonl').read_text(encoding='utf-8').splitlines() if line]
        attempts.extend(rerun_attempts)
    usage={k:sum(a.get('model_call_breakdown',{}).get('runtime',{}).get(k,0) for a in attempts) for k in ['generation_calls','embedding_calls']}
    usage.update(model_calls=sum(a.get('model_calls',0) for a in attempts),token_usage=sum(a.get('token_usage',0) for a in attempts),
        external_judge_calls=sum(a.get('model_call_breakdown',{}).get('judge',{}).get('model_calls',0) for a in attempts))
    invocation_path=root/'data/evaluation/g4-post-repair-invocations.jsonl'
    invocations=[json.loads(line) for line in invocation_path.read_text(encoding='utf-8').splitlines() if line]
    if rerun_run_id:
        invocations.extend(json.loads(line) for line in (root/'data/evaluation/g4-target-rerun-invocations.jsonl').read_text(encoding='utf-8').splitlines() if line)
        assert any(item['run_id'] == rerun_run_id for item in invocations)
    completed = [id for id,r in new.items() if not r['exception']]
    previously_complete=[id for id,r in old.items() if r['expected_status']=='answered' and r['category']=='ANSWERED_COMPLETE'
        and r['metrics']['citation_integrity'] is True and not any(r['metrics'][k] for k in ['hallucinated_identifiers','wrong_version_evidence','forbidden_evidence'])]
    worsened=[id for id in previously_complete if id in new and new[id]['category']!='ANSWERED_COMPLETE']
    old_safety,new_safety=safety(old),safety(new)
    new_safety_ids={k:sorted(set(v['case_ids'])-set(old_safety[k]['case_ids'])) for k,v in new_safety.items() if isinstance(v,dict) and 'case_count' in v}
    new_point_misses=sorted(id for id in new if new[id]['runtime_missing_required_point_ids'] and not old[id]['runtime_missing_required_point_ids'])
    frontier_counts={id:r['pool_reason_counts'].get('policy_role_frontier',0) for id,r in new.items() if r['frontier_used']}
    cross={side:{c:0 for c in CATEGORIES} for side in ['frontier_used','frontier_not_used','receipt_unobserved']}
    for r in new.values():cross['receipt_unobserved' if r['frontier_used'] is None else ('frontier_used' if r['frontier_used'] else 'frontier_not_used')][r['category']]+=1
    detail={}
    for id,objects in TARGET_OBJECTS.items():
        if id not in new:continue
        record=read(selected_paths[id]);s=new[id]
        pool=record.get('diagnostics',{}).get('rerank_pool_entries',[])
        final={e['object_id'] for e in s['evidence']};cited={e['object_id'] for e in s['evidence'] if e['cited']}
        detail[id]={'old':{k:old[id][k] for k in ['status','category','runtime_answer_point_coverage']},'new':{k:s[k] for k in ['status','category','production_category','runtime_answer_point_coverage','runtime_missing_required_point_ids','runtime_missing_relations','manual_critical_answer_points_missing','evidence']},'rerank_pool_entries':pool,'historically_lost_objects':[{'object_id':obj,
            'pool_entry':next((p for p in pool if p['object_id']==obj),None),'in_final_evidence':obj in final,'cited':obj in cited,'channel_ranks_1based':{k:(v.index(obj)+1 if obj in v else None) for k,v in record.get('diagnostics',{}).get('rankings',{}).items()},'reranked_rank_1based':(record.get('diagnostics',{}).get('reranked_object_ids',[]).index(obj)+1 if obj in record.get('diagnostics',{}).get('reranked_object_ids',[]) else None)} for obj in objects]}
    output = {
        'schema_version':'g4-exposed-post-repair-regression-v1','run_id':NEW_RUN,'old_run_id':OLD_RUN,
        'start_head':LINEAGE,'evaluated_product_behavior_lineage':LINEAGE,'old_product_behavior_lineage':OLD_LINEAGE,
        'old_manifest':old_manifest,'new_manifest':new_manifest,'preflight_ref':'data/evaluation/g4-post-repair-preflight.json',
        'identity_match':matches,'model_config_identity_match':matches['generation_model_id'] and matches['embedding_model_id'],'product_identity':read(root/'data/evaluation/g4-post-repair-preflight.json')['product'] | {'active_gold':'m6-benchmark-v2.11','active_calibration':read(root/'data/evaluation/g4-post-repair-preflight.json')['active_calibration_id']},'observed_semantic_verification_model_ids':sorted({read(p).get('diagnostics',{}).get('model_roles',{}).get('semantic_verification_model') for p in selected_paths.values()} - {None}),'package_version_differences':{k:{'old':old_manifest['package_versions'].get(k),'new':v} for k,v in new_manifest['package_versions'].items() if v!=old_manifest['package_versions'].get(k)},
        'pairwise_causal_interpretation':'NONDETERMINISTIC_EXPOSED_REGRESSION','provider_run_nondeterminism':'present as a methodological limitation',
        'runner_final_state':read(runs/NEW_RUN/'run_status.json'),'completion':{'expected':28,'completed':len(completed),'terminal_records':sum(not r['exception'] or not r['exception'].get('retryable') for r in new.values()),'incomplete_ids':sorted(id for id in expected_ids if id not in new or (new[id]['exception'] and new[id]['exception'].get('retryable'))),'nonretryable_exception_case_ids':sorted(id for id,r in new.items() if r['exception'] and not r['exception'].get('retryable')),
            'runner_invocations':len(invocations),'invocations':invocations,'case_attempts':len(attempts),
            'retryable_infrastructure_attempts':sum(bool(a.get('exception',{}).get('retryable')) for a in attempts),
            'nonretryable_exception_attempts':sum(bool(a.get('exception')) and not a['exception'].get('retryable') for a in attempts),
            'attempts_per_case':dict(sorted(Counter(a['id'] for a in attempts).items()))},
        'usage':usage,'old_evaluator_aggregate':{k:v for k,v in aggregate_metrics([read(p) for p in (runs/OLD_RUN/'records').glob('*.json')]).items() if k not in ['per_intent','latency_ms']},'new_evaluator_aggregate':{k:v for k,v in aggregate_metrics([read(p) for p in selected_paths.values()]).items() if k not in ['per_intent','latency_ms']},'old_status_counts':dict(Counter(r['status'] for r in old.values())),
        'new_status_counts':dict(Counter(r['status'] for r in new.values())),
        'old_category_counts':{c:sum(r['category']==c for r in old.values()) for c in CATEGORIES},
        'new_production_category_counts':{c:sum(r['production_category']==c for r in new.values()) for c in CATEGORIES},'new_category_counts':{c:sum(r['category']==c for r in new.values()) for c in CATEGORIES},
        'expected_answered_category_counts':{c:sum(r['category']==c and r['expected_status']=='answered' for r in new.values()) for c in CATEGORIES},
        'abstention_cases':{id:{'expected':r['expected_status'],'old_status':old[id]['status'],'new_status':r['status'],'old_correct':old[id]['expected_status_correct'],'new_correct':r['expected_status_correct']} for id,r in new.items() if r['expected_status']!='answered'},
        'coverage_definition':'Ratio of existing validated production covered canonical point IDs to all canonical points; VALID complete receipt required for ANSWERED_COMPLETE. Gold-weighted judge coverage is not measured. Bounded human review narrows n006 to ANSWERED_INCOMPLETE because independently adjudicated critical Gold p2 suffix literals are absent; no raw metric is overwritten.',
        'runtime_coverage_distribution':dict(Counter(str(r['runtime_answer_point_coverage']) for r in new.values())),
        'transition_matrix':matrix,'cases':cases,'r2_target_details':detail,
        'other_historical_insufficient':{id:{'old':{k:old[id][k] for k in ['status','category','runtime_answer_point_coverage']},'new':{k:new[id][k] for k in ['status','category','runtime_answer_point_coverage','verification_errors']} if id in new else None,'prior_owner':owner} for id,owner in [('n001','Q1'),('n010','UNRESOLVED Q1/R1'),('n019','UNRESOLVED R2/Q2')]},
        'collateral_pool_loss_n024':collateral_pool_loss(root), 'old_safety':old_safety,'new_safety':new_safety,'new_safety_failure_ids':new_safety_ids,
        'previously_complete_cases':sorted(previously_complete),'previously_complete_cases_worsened':sorted(worsened),
        'previously_complete_definition':'Expected answered; complete VALID production coverage; citation integrity; no identifier, version, forbidden-evidence failure. Independent Gold semantic validity not scored.',
        'new_runtime_point_miss_cases':new_point_misses,'new_answered_manually_verified_critical_point_miss_cases':sorted(id for id,r in new.items() if r['manual_critical_answer_points_missing']),'answered_manual_critical_miss_count_lower_bound':sum(len(r['manual_critical_answer_points_missing']) for r in new.values()),
        'frontier':{'cases_with_policy_role_frontier':len(frontier_counts),'total_policy_role_frontier_entries':sum(frontier_counts.values()),
            'frontier_entry_count_definition':'Sum of case-level entries; repeated objects across cases are counted per case','frontier_entries_per_case':frontier_counts,'cases_with_structured_supplemental':sum(r['pool_reason_counts'].get('structured_supplemental',0)>0 for r in new.values()),
            'cases_ordinary_rrf_only':sum(bool(r['pool_reason_counts']) and set(r['pool_reason_counts'])=={'ordinary_rrf'} for r in new.values()),
            'receipt_missing_case_ids':sorted(id for id,r in new.items() if not r['pool_observed']),'outcome_cross_tab':cross},
        'historical_crosschecks':{'g3_completion_result_completed':read(root/'evaluation/G3_SCOPED_AUDIT_COMPLETION_RESULT.json')['qa_cases_completed'],'g3_completion_product_lineage':read(root/'evaluation/G3_SCOPED_AUDIT_COMPLETION_RESULT.json')['product_behavior_lineage'],'g3_review_overlay_decision':read(root/'evaluation/G3_SCOPED_AUDIT_COMPLETION_REVIEW_OVERLAY.json')['primary_decision']},'trace_capture_counts':dict(Counter(str(r['trace_capture_status']) for r in new.values())),
        'protected_boundary':dict.fromkeys(['novel_validation_content_access','novel_validation_outcome_access','holdout_content_access','holdout_outcome_access','protected_leakage'],0),
        'evidence_boundary':{'exposed_cohort':True,'fresh_confirmation':False,'fresh_generalization_evidence':False,'novel_validation_evidence':False,'release_evidence':False},
        'deterministic_controls':{'accepted_normal_r2_control_count':17,'accepted_g4_control_count':18,'rerun_in_this_task':False,'ref':'evaluation/G4_R2_NORMAL_PRODUCT_POOL_INTEGRATION_CORRECTION.md'},'changes':dict.fromkeys(['product_source_change','prompt_change','config_change','schema_change','dataset_change','gold_change','calibration_change'],False),
    }
    if rerun_run_id:
        def attempt_usage(rows):
            return {'model_calls':sum(a.get('model_calls',0) for a in rows),
                'token_usage':sum(a.get('token_usage',0) for a in rows),
                'generation_calls':sum(a.get('model_call_breakdown',{}).get('runtime',{}).get('generation_calls',0) for a in rows),
                'embedding_calls':sum(a.get('model_call_breakdown',{}).get('runtime',{}).get('embedding_calls',0) for a in rows),
                'external_judge_calls':sum(a.get('model_call_breakdown',{}).get('judge',{}).get('model_calls',0) for a in rows)}
        output.update(schema_version='g4-exposed-post-repair-regression-v2',
            analysis_kind='DIAGNOSTIC_COMPOSITE_WITH_EXPLICIT_TARGET_RERUN',
            component_run_ids=[NEW_RUN,rerun_run_id],rerun_run_id=rerun_run_id,rerun_manifest=rerun_manifest,
            rerun_start_head=rerun_manifest['repository_identity']['commit'],
            rerun_runner_final_state=read(runs/rerun_run_id/'run_status.json'),
            full_cohort_gate_passed=False,
            selection_policy='Keep 26 original QA records; replace n002/n018 with the one explicitly authorized rerun, regardless of outcome. No best-of selection.',
            rerun_identity_match={key:rerun_manifest[key] == new_manifest[key] for key in [
                'source_manifest_hash','normalized_manifest_hash','normalized_output_hashes','index_identity',
                'index_identity_payload','gold_dataset_hash','gold_benchmark_version','prompt_hash',
                'generation_model_id','embedding_model_id','retrieval_policy_hash','query_expansion_hash','package_versions']},
            initial_completion={'completed':sum(not r['exception'] for r in initial_rows.values()),'case_attempts':len(initial_attempts),
                'nonretryable_exception_case_ids':sorted(id for id,r in initial_rows.items() if r['exception'] and not r['exception'].get('retryable'))},
            initial_usage=attempt_usage(initial_attempts),rerun_usage=attempt_usage(rerun_attempts),
            target_rerun_transitions={id:{'initial':initial_rows[id],'rerun':new[id]} for id in ['n002','n018']})
        output['coverage_definition'] += ' Authorized n018 rerun is also narrowed to ANSWERED_INCOMPLETE: critical Gold p1 null checking and p2 composite typing/EvtGen PDG initialization are absent, although its production receipt is complete.'
    return output

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--project-root',type=Path,default=Path.cwd());parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--review',type=Path,help='Bounded human-review JSON, or the committed result containing analyst_review')
    parser.add_argument('--rerun-run-id',help='Read-only n002/n018 replacement run; never overwrites the initial run')
    args=parser.parse_args();root=args.project_root.resolve()
    assert not args.output.resolve().is_relative_to(root/'data/evaluation/runs'), 'analysis output must not overwrite a raw run store'
    result=analyze(root,args.rerun_run_id)
    if args.review:
        review=json.loads(args.review.read_text(encoding='utf-8-sig'));review=review.get('analyst_review',review)
        result['analyst_review']=review;result['outcome']=review['outcome'];result['verification_status']=review['verification_status']
        result['remaining_false_insufficiency_candidates']=[{'id':c['id'],'answerability':review.get(c['id'],{}).get('answerability','NOT_INDEPENDENTLY_ESTABLISHED'),
            'earliest_plausible_owner':review.get(c['id'],{}).get('earliest_plausible_owner','UNRESOLVED'),'finding':review.get(c['id'],{}).get('finding','Requires bounded review')}
            for c in result['cases'] if c['new']['status']=='insufficient_evidence']
        result['lifecycle']={'phase_g':'IN_PROGRESS / G4_EXPOSED_POST_REPAIR_SAFETY_REGRESSION_REVIEW_REQUIRED','g4':'DETERMINISTIC HARNESS COMPLETE / EXPOSED DEVELOPMENT DIAGNOSTIC COMPLETE / GENERIC R2 FALSE_INSUFFICIENCY MECHANISM ESTABLISHED / R2 REPAIR IMPLEMENTED IN NORMAL PRODUCT PATH / NORMAL-PRODUCTION DETERMINISTIC RED→GREEN PASS / EXPOSED POST-REPAIR REGRESSION ATTEMPT TERMINATED / 26 OF 28 QA RESULTS / SAFETY REGRESSION / FRESH GENERALIZATION BENEFIT NOT_ESTABLISHED','next_task_recommendation':review['next_task_recommendation'],'next_task_execution_authorized':False,'fresh_lane_b':review['fresh_lane_b']}
        if args.rerun_run_id:
            result['lifecycle']['g4']=result['lifecycle']['g4'].replace('EXPOSED POST-REPAIR REGRESSION ATTEMPT TERMINATED / 26 OF 28 QA RESULTS',
                f"EXPOSED POST-REPAIR TARGET RERUN COMPLETE / {result['completion']['completed']} OF 28 SELECTED QA RESULTS / DIAGNOSTIC COMPOSITE; ORIGINAL COHORT INCOMPLETE")
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'qa_results':result['completion']['completed'],'terminal_records':result['completion']['terminal_records'],'case_attempts':result['completion']['case_attempts'],'outcome':result.get('outcome'),'categories':result['new_category_counts'],'usage':result['usage']},indent=2))
