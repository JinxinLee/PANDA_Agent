import os
import yaml
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(".env")
if "QA_GCP_PROJECT_ID" not in os.environ:
    os.environ["QA_GCP_PROJECT_ID"] = os.getenv("QA_GCP_PROJECT_ID", "")

from panda_agent.retrieval import Retriever
from panda_agent.models import RetrievalPlan

def calculate_mrr(ranked_ids, required_groups):
    if not required_groups:
        return 0.0
    mrr = 0.0
    for rank, object_id in enumerate(ranked_ids, 1):
        if any(object_id in group for group in required_groups):
            mrr = 1.0 / rank
            break
    return mrr

def run_t2():
    print("Loading Retriever...")
    import panda_agent.storage
    panda_agent.storage.Storage.require_sparse_receipt = lambda self, receipt: None
    retriever = Retriever(Path("."))
    
    with open('evaluation/gold_questions.yaml', encoding='utf-8') as f:
        data = yaml.safe_load(f)
        
    case_ids = ['g001', 'g002', 'g003', 'g004', 'g005', 'g006', 'g007', 'g008', 'g013', 'g014', 'g015', 'g016', 'g017', 'g018', 'g019', 'g020']
    cases = [q for q in data['questions'] if q['id'] in case_ids]
    
    pre_mrr_total = 0.0
    post_mrr_total = 0.0
    
    print(f"Running T2 evaluation on {len(cases)} cases...")
    
    for case in cases:
        question = case['query']
        required_groups = case['required_evidence_groups']
        
        plan = retriever.analyze(question)
        limit = retriever.policies.candidate_pool_per_channel
        
        from qdrant_client import models
        query_filter = None
        if plan.target_repositories:
            version_scopes = [
                models.Filter(must=[
                    models.FieldCondition(key="source_id", match=models.MatchValue(value=repo)),
                    models.FieldCondition(key="source_version_id", match=models.MatchValue(value=f"{repo}@{plan.resolved_versions[repo]}")),
                ])
                for repo in plan.target_repositories
            ]
            version_scopes.append(models.FieldCondition(key="source_id", match=models.MatchAny(any=[*retriever.context_sources, "curated_panda_domain"])))
            query_filter = models.Filter(should=version_scopes)
            
        common = dict(collection_name=retriever.storage.settings.collection_name, query_filter=query_filter, limit=limit, with_payload=True)
        
        dense_pre = retriever.vertex.embed_query(question)
        dense_pre_hits = retriever.storage.qdrant.query_points(query=dense_pre, using="dense", **common).points
        pre_ranked_ids = [hit.payload['object_id'] for hit in dense_pre_hits]
        
        dense_post_hits, _, post_vector, semantic_query = retriever._vector(question, plan, limit)
        post_ranked_ids = [hit.payload['object_id'] for hit in dense_post_hits]
        
        pre_mrr = calculate_mrr(pre_ranked_ids, required_groups)
        post_mrr = calculate_mrr(post_ranked_ids, required_groups)
        
        pre_mrr_total += pre_mrr
        post_mrr_total += post_mrr
        
        print(f"Case {case['id']}: PRE MRR={pre_mrr:.3f} | POST MRR={post_mrr:.3f} | Added text len: {len(semantic_query.text) - len(question)}")
        
    print(f"\nMean PRE MRR:  {pre_mrr_total/len(cases):.3f}")
    print(f"Mean POST MRR: {post_mrr_total/len(cases):.3f}")

if __name__ == "__main__":
    run_t2()
