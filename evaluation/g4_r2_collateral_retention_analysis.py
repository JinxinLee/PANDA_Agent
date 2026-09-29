"""Read-only structural audit of saved exposed G4 pool construction.

No product imports, retrieval, model calls, semantic scoring or threshold search.
Trace metadata omits text and specialized origin sidecars; reconstruction is
conditional on usable channel payloads and records explicit provenance bounds.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import math
from pathlib import Path
from statistics import median

INITIAL = 'g4-r2-post-repair-novel-dev-regression-v1'
RERUN = 'g4-r2-post-repair-n002-n018-rerun-v1'
OLD = 'g3-evidence-admission-audit-novel-dev-v1'
CHANNELS = ['exact', 'dense', 'sparse', 'paper', 'workflow', 'graph']
WEIGHTS = dict(zip(CHANNELS, [2.0, 1.0, 1.0, 1.15, 1.2, 0.8]))
REGULAR = {'exact', 'dense', 'sparse', 'paper'}


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def source_role(item):
    # Metadata-only transcription of retrieval.py::_source_type_of.
    if item['source_id'] in {'li_2026', 'karavdina_2015', 'pflueger_2017'}:
        return 'paper'
    if 'sphinx' in item['source_id']:
        return 'documentation'
    path = (item.get('locator', {}).get('path') or '').replace('\\', '/').lower()
    if path.startswith(('docs/', 'doc/')):
        return 'documentation'
    if item['object_type'] in {'workflow', 'python_script', 'shell_script'}:
        return 'workflow'
    if item['object_type'] == 'readme_section':
        return 'readme'
    return 'code'


def distribution(values):
    return {'min':min(values), 'median':median(values), 'max':max(values),
            'frequencies':dict(sorted(Counter(map(str, values)).items()))}


def origin_fact(channel, items, required, entries, ranks):
    if not items:
        return {'state':'EMPTY', 'basis':'no occurrences'}
    if channel not in required:
        return {'state':'normal', 'basis':'current branch never returns generic fallback unless this channel is required'}
    fallback_types = {'workflow'} if channel == 'workflow' else {'document','repository','subsystem','concept'}
    if any(item['source_id'] != 'curated_panda_domain' or item['object_type'] not in fallback_types for item in items):
        return {'state':'normal', 'basis':'returned rows cannot originate from the branch-specific generic fallback query'}
    if any(entry['reason'] == 'policy_role_frontier' and set(ranks[entry['object_id']]) == {channel} for entry in entries):
        return {'state':'normal', 'basis':'specialized-only frontier receipt plus the current uniform branch-origin contract implies normal origin'}
    return {'state':'UNKNOWN', 'basis':'origin sidecar absent; metadata alone cannot distinguish the two branches'}


def metadata_queues(plan, ordinary, base_set, metadata, ranks, origins, context_sources, upper=False):
    active = set(plan['required_source_types']) | {r for r,b in plan['source_budgets'].items() if b > 0}
    roles = sorted(active, key=lambda r:(r not in plan['required_source_types'], -plan['source_budgets'].get(r,0), r))
    queues, ceilings, limits = {}, {}, {}
    for role in roles:
        rows = []
        for oid in ordinary:
            if oid in base_set:
                continue
            item = metadata[oid]
            source = item['source_id']
            if source in plan['target_repositories']:
                resolved = plan['resolved_versions'].get(source)
                if not resolved or item['source_version_id'] != f'{source}@{resolved}':
                    continue
            elif source not in context_sources and source != 'curated_panda_domain':
                continue
            eligible = []
            for channel,rank in ranks[oid].items():
                normal = channel in REGULAR or origins[channel]['state'] == 'normal' or (upper and origins[channel]['state'] == 'UNKNOWN')
                if normal and (source_role(item) == role or channel == role and role in {'workflow','graph'}):
                    eligible.append(rank)
            if eligible:
                rows.append((min(eligible), -item['rrf_score'], oid))
        rows.sort()
        queues[role] = [oid for _,_,oid in rows]
        budget = plan['source_budgets'].get(role,0)
        ceilings[role] = max(1,math.ceil(12 * budget)) if budget > 0 else 1
        limits[role] = min(ceilings[role],len(rows))
    return roles, queues, ceilings, limits


def reconstruct_frontier(roles, queues, limits, base_slots):
    cap = min(sum(limits.values()), max(0,(base_slots-1)//2))
    selected, charged = [], {}
    positions = dict.fromkeys(roles,0)
    used = dict.fromkeys(roles,0)
    while len(selected) < cap:
        added = False
        for role in roles:
            if used[role] >= limits[role]:
                continue
            queue = queues[role]
            while positions[role] < len(queue) and queue[positions[role]] in charged:
                positions[role] += 1
            if positions[role] == len(queue):
                continue
            oid = queue[positions[role]]
            positions[role] += 1
            selected.append(oid)
            charged[oid] = role
            used[role] += 1
            added = True
            if len(selected) == cap:
                break
        if not added:
            break
    return cap, selected, charged


def analyze(root):
    runs = root/'data/evaluation/runs'
    composite = read(root/'evaluation/G4_EXPOSED_NOVEL_DEV_POST_REPAIR_REGRESSION_RERUN_RESULT.json')
    source_manifest = read(root/'data/manifests/source_manifest.json')
    context_sources = {item['doc_id'] for item in source_manifest['papers'] + source_manifest['web_documents']}
    cases, displaced_all, frontier_all = [], [], []
    for comparison in composite['cases']:
        id = comparison['id']
        run = RERUN if id in {'n002','n018'} else INITIAL
        record, trace = read(runs/run/'records'/f'{id}.json'), read(runs/run/'traces'/f'{id}.json')
        plan, entries = record['diagnostics']['plan'], record['diagnostics']['rerank_pool_entries']
        metadata, ranks, scores = {}, {}, {}
        for channel in CHANNELS:
            items = trace['channel_candidates'].get(channel,[])
            assert [item['object_id'] for item in items] == record['diagnostics']['rankings'].get(channel,[])
            for item in items:
                oid, rank = item['object_id'], item['rank']
                metadata[oid] = item
                ranks.setdefault(oid,{})[channel] = rank
                scores[oid] = scores.get(oid,0) + WEIGHTS[channel]/(60+rank)
        ordinary = sorted(scores,key=scores.get,reverse=True)
        fused = sorted(trace['fused_candidates'],key=lambda x:x['rank'])
        assert ordinary[:30] == [item['object_id'] for item in fused]
        for item in fused:
            assert math.isclose(scores[item['object_id']],item['score'],rel_tol=1e-12)
        for oid,item in metadata.items():
            item['rrf_score'] = scores[oid]
        supp = [e['object_id'] for e in entries if e['reason']=='structured_supplemental']
        assert not supp, 'Observed cohort has no supplements; do not reinterpret supplement provenance'
        base_set = set(ordinary[:30])
        origins = {ch:origin_fact(ch,trace['channel_candidates'].get(ch,[]),plan['required_source_types'],entries,ranks) for ch in ['workflow','graph']}
        roles, queues, ceilings, limits = metadata_queues(plan,ordinary,base_set,metadata,ranks,origins,context_sources)
        upper_roles, upper_queues, _, upper_limits = metadata_queues(plan,ordinary,base_set,metadata,ranks,origins,context_sources,upper=True)
        cap, predicted, charged = reconstruct_frontier(roles,queues,limits,30)
        upper_cap, upper_predicted, _ = reconstruct_frontier(upper_roles,upper_queues,upper_limits,30)
        actual = [e['object_id'] for e in entries if e['reason']=='policy_role_frontier']
        backbone = [e['object_id'] for e in entries if e['reason']=='ordinary_rrf']
        assert backbone == ordinary[:30-len(actual)]
        assert len(entries) == 30 and len(backbone) > len(actual)
        old_record = read(runs/OLD/'records'/f'{id}.json')
        old_rankings = old_record['diagnostics']['rankings']
        old_final = {e['object_id'] for e in old_record['result'].get('evidence',[])}
        cited_ids = {eid for c in old_record['result'].get('claims',[]) for eid in c.get('evidence_ids',[])}
        old_cited = {e['object_id'] for e in old_record['result'].get('evidence',[]) if e['evidence_id'] in cited_ids}
        rankings_same = old_rankings == record['diagnostics']['rankings']
        displaced = []
        for rank,oid in enumerate(ordinary[:30],1):
            if oid in backbone:
                continue
            regular = sorted(set(ranks[oid]) & REGULAR)
            known = regular + [ch for ch in ['workflow','graph'] if ch in ranks[oid] and origins[ch]['state']=='normal']
            unknown = [ch for ch in ['workflow','graph'] if ch in ranks[oid] and origins[ch]['state']=='UNKNOWN']
            row = {'object_id':oid,'legacy_rrf_rank':rank,'rrf_score':scores[oid], 'channel_ranks':ranks[oid],
                'raw_channel_count':len(ranks[oid]),'known_qualifying_channels':sorted(known), 'known_qualifying_channel_count':len(known),
                'unknown_specialized_channels':unknown,'source_role':source_role(metadata[oid]),
                'source_id':metadata[oid]['source_id'],'locator':metadata[oid]['locator'],
                'historical_G3_final':oid in old_final,'historical_G3_cited':oid in old_cited,
                'all_channel_rankings_identical_to_G3':rankings_same}
            displaced.append(row)
            displaced_all.append({'case_id':id,**row})
        current = {'id':id,'selected_run_id':run,'record_ref':str((runs/run/'records'/f'{id}.json').relative_to(root)),
            'trace_ref':str((runs/run/'traces'/f'{id}.json').relative_to(root)),
            'active_roles':roles,'source_budgets':plan['source_budgets'],'required_roles':plan['required_source_types'],
            'role_policy_ceilings':ceilings,'eligible_challenger_counts_conditional_lower':{r:len(q) for r,q in queues.items()},
            'eligible_challenger_counts_conditional_upper':{r:len(q) for r,q in upper_queues.items()},
            'role_limits_conditional_lower':limits,'role_limits_conditional_upper':upper_limits,
            'sum_role_limits_conditional_lower':sum(limits.values()),'sum_role_limits_conditional_upper':sum(upper_limits.values()),
            'frontier_capacity_conditional_lower':cap,'frontier_capacity_conditional_upper':upper_cap,
            'selected_frontier_count':len(actual),'ordinary_backbone_count':len(backbone),
            'frontier_fraction_of_non_supplement_pool':len(actual)/30,
            'saturates_majority_bound':len(actual)==14,'specialized_origin_facts':origins,
            'metadata_reconstruction_matches_actual_lower':predicted==actual,
            'metadata_reconstruction_matches_actual_upper':upper_predicted==actual,
            'all_channel_rankings_identical_to_G3':rankings_same,
            'frontier_source_roles':dict(Counter(source_role(metadata[oid]) for oid in actual)),
            'frontier_charged_roles_conditional':dict(Counter(charged.values())) if predicted==actual else None,
            'displaced_legacy_candidates':displaced}
        if id=='n006':
            oid = 'object.2914485ff398f61e994c46d6'
            current['residual_target'] = {'object_id':oid,'source_role':source_role(metadata[oid]),'channel_ranks':ranks[oid],
                'role_queue_positions_conditional':{r:q.index(oid)+1 for r,q in queues.items() if oid in q},
                'code_policy_ceiling':ceilings['code'],'code_queue_limit':limits['code'],
                'code_queue_prefix':[{'object_id':x,'channel_ranks':ranks[x],'source_role':source_role(metadata[x]),'selected_frontier':x in actual,
                    'charged_role_conditional':charged.get(x)} for x in queues['code'][:10]],
                'in_pool':any(e['object_id']==oid for e in entries)}
        if id=='n024':
            oid = 'object.d6ef560b88c3926ecb32d3e1'
            # Characterize existing base witnesses, not a new exchange policy.
            current['collateral_target_rank_witness_observation'] = {
                'object_id':oid, 'code_policy_ceiling':ceilings['code'],
                'legacy_code_channel_ranks':{
                    channel:sorted(ranks[x][channel] for x in base_set
                        if source_role(metadata[x])=='code' and channel in ranks[x])
                    for channel in ['dense','sparse']},
                'target_code_channel_ordinals':{
                    channel:1+sum(ranks[x][channel]<ranks[oid][channel]
                        for x in base_set if source_role(metadata[x])=='code' and channel in ranks[x])
                    for channel in ['dense','sparse']}}
        if id in {'n002','n017'}:
            current['benefit_base_observation'] = {
                'code_policy_ceiling':ceilings['code'],
                'legacy_code_dense_ranks':sorted(ranks[x]['dense'] for x in base_set
                    if source_role(metadata[x])=='code' and 'dense' in ranks[x]),
                'legacy_workflow_payload_count':sum(source_role(metadata[x])=='workflow' for x in base_set),
                'workflow_role_active':'workflow' in roles,
                'legacy_workflow_graph_occurrences':sum('graph' in ranks[x] for x in base_set
                    if source_role(metadata[x])=='workflow')}
        for oid in actual:
            frontier_all.append({'case_id':id,'object_id':oid,'source_role':source_role(metadata[oid]),'channel_ranks':ranks[oid]})
        cases.append(current)
    assert len(cases)==28 and sum(c['selected_frontier_count'] for c in cases)==295
    return {'schema_version':'g4-r2-collateral-retention-analysis-v1',
        'start_head':'9caf7314e0fd908a71cb93520d482002756e1d4c',
        'product_behavior_lineage':'a22c8f70eeebe4a53490e11a4b6852561ca8afa6',
        'input_runs':[OLD,INITIAL,RERUN], 'analysis_kind':'READ_ONLY_STRUCTURAL_CHARACTERIZATION; NO_NEW_POLICY_SIMULATION',
        'metadata_limitations':['Full candidate text/title and aligned specialized origin sidecars are absent from public saved traces.',
            'Queue counts/capacities are conditional on usable channel payloads; source/version/metadata checks are applied.',
            'Specialized normal origins are inferred only from current branch contracts or necessary receipt implications; unknown origins stay bounded.',
            'Historical final/cited overlap is diagnostic, not runtime relevance authority; comparisons with changed channel rankings are not paired causal estimates.'],
        'summary':{'cases_analyzed':28,'cases_with_frontier':28,'frontier_total':295,
            'frontier_count':distribution([c['selected_frontier_count'] for c in cases]),
            'backbone_count':distribution([c['ordinary_backbone_count'] for c in cases]),
            'active_role_count':distribution([len(c['active_roles']) for c in cases]),
            'sum_role_limits_conditional':distribution([c['sum_role_limits_conditional_lower'] for c in cases]),
            'frontier_capacity_conditional':distribution([c['frontier_capacity_conditional_lower'] for c in cases]),
            'majority_bound_saturation_case_ids':[c['id'] for c in cases if c['saturates_majority_bound']],
            'metadata_exact_match_lower_count':sum(c['metadata_reconstruction_matches_actual_lower'] for c in cases),
            'metadata_exact_match_upper_count':sum(c['metadata_reconstruction_matches_actual_upper'] for c in cases),
            'unknown_origin_cases':[c['id'] for c in cases if any(v['state']=='UNKNOWN' for v in c['specialized_origin_facts'].values())],
            'displaced_candidate_occurrences':len(displaced_all),
            'displaced_rrf_ranks':distribution([d['legacy_rrf_rank'] for d in displaced_all]),
            'displaced_rrf_scores':distribution([d['rrf_score'] for d in displaced_all]),
            'displaced_raw_channel_counts':dict(sorted(Counter(d['raw_channel_count'] for d in displaced_all).items())),
            'displaced_known_qualifying_channel_counts':dict(sorted(Counter(d['known_qualifying_channel_count'] for d in displaced_all).items())),
            'displaced_channel_names':dict(Counter(ch for d in displaced_all for ch in d['channel_ranks'])),
            'displaced_source_roles':dict(Counter(d['source_role'] for d in displaced_all)),
            'displaced_historical_final_overlap':sum(d['historical_G3_final'] for d in displaced_all),
            'displaced_historical_cited_overlap':sum(d['historical_G3_cited'] for d in displaced_all),
            'cases_identical_rankings_to_G3':[c['id'] for c in cases if c['all_channel_rankings_identical_to_G3']],
            'identical_ranking_displaced_historical_cited_overlap':sum(d['historical_G3_cited'] and d['all_channel_rankings_identical_to_G3'] for d in displaced_all),
            'frontier_source_roles':dict(Counter(d['source_role'] for d in frontier_all))},
        'cases':cases,
        'scientific_accounting':dict.fromkeys(['qa_runs','retrieval_runs','scientific_calls','scientific_tokens','external_judge_calls'],0),
        'protected_boundary':dict.fromkeys(['novel_validation_content_access','novel_validation_outcome_access','holdout_content_access','holdout_outcome_access','protected_leakage'],0)}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root',type=Path,default=Path.cwd())
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    root=args.project_root.resolve()
    assert not args.output.resolve().is_relative_to(root/'data/evaluation/runs'), 'Never overwrite raw run stores'
    result=analyze(root)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({key:result['summary'][key] for key in [
        'cases_analyzed','cases_with_frontier','frontier_total',
        'majority_bound_saturation_case_ids','displaced_candidate_occurrences',
        'metadata_exact_match_lower_count','unknown_origin_cases']},indent=2))
