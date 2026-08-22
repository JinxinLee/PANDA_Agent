"""C6-A1R2 provenance repair stage 1: freeze repair set, verify plans/identity.

Static/offline stage before any live retrieval: freezes the repair set,
validates the faithful C3-R3 full plans through the fail-fast provenance
guard, derives source_budgets from the current versioned intent policy,
checks capture identity against the original A1R2 record, verifies the v1
row population, and rechecks semantic activation purely.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "evaluation" / "scripts"))

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

import warnings  # noqa: E402

warnings.filterwarnings("ignore")

from plan_provenance import validate_executable_plan_payload  # noqa: E402
from panda_agent.config import load_retrieval_policies  # noqa: E402
from panda_agent.models import RetrievalPlan  # noqa: E402
from panda_agent.retrieval import (  # noqa: E402
    DenseQueryBundle,
    build_semantic_query,
)

C3R3 = (
    PROJECT_ROOT
    / "evaluation"
    / "baselines"
    / "manifests"
    / "phase_c_c3_r3_exhaustive_treatment_qualified_dense_evaluation_v1.json"
)
A1R2 = (
    PROJECT_ROOT
    / "evaluation"
    / "baselines"
    / "manifests"
    / "phase_c_c6_a1r2_current_plan_candidate_coverage_v1.json"
)
V1 = (
    PROJECT_ROOT
    / "evaluation"
    / "baselines"
    / "replay"
    / "phase_c_c6_current_plan_candidate_replay_v1.jsonl"
)
OUTPUT = PROJECT_ROOT / "data" / "tmp" / "c6_a1r2_repair_frozen_v1.json"

REPAIR_SET = ["g039", "g040", "g055", "g113", "g114", "g115"]
REPAIRED_CORE = ["g113", "g114", "g115"]
SUPPLEMENTAL = ["g039", "g040", "g055"]


def main() -> None:
    # 1. Faithful full plans from C3-R3 (guard-validated).
    c3r3 = json.loads(C3R3.read_text(encoding="utf-8"))
    holders: dict[str, tuple[str, dict]] = {}
    for sa in c3r3["stage_a_actual"]["screening_cases"]:
        if sa.get("retrieval_plan"):
            holders[sa["case_id"]] = ("stage_a_actual.screening_cases", sa)
    for cb in c3r3["stage_b_actual"].get("cohort_cases", []):
        if cb.get("retrieval_plan") or cb.get("plan"):
            holders.setdefault(cb["case_id"], ("stage_b_actual.cohort_cases", cb))

    policies = load_retrieval_policies(PROJECT_ROOT / "configs" / "retrieval_policies.yaml")
    plans: dict[str, dict] = {}
    provenance: dict[str, dict] = {}
    for case_id in REPAIR_SET:
        source, holder = holders[case_id]
        plan = dict(holder.get("retrieval_plan") or holder.get("plan"))
        validate_executable_plan_payload(plan)
        intent = plan["intent"]
        policy_budgets = dict(policies.intents[intent].source_budgets)
        budgets_changed = plan.get("source_budgets") != policy_budgets
        plan["source_budgets"] = policy_budgets  # faithful intent -> current versioned policy
        validate_executable_plan_payload(plan)
        RetrievalPlan.model_validate(plan)  # executable
        plans[case_id] = plan
        provenance[case_id] = {
            "full_plan_source": f"phase_c_c3_r3_exhaustive_treatment_qualified_dense_evaluation_v1.json#{source}[{case_id}]",
            "question": holder.get("query") or holder.get("raw_question") or holder.get("question"),
            "source_budgets_policy_derived": True,
            "source_budgets_policy_equals_c3r3_record": not budgets_changed,
        }

    # 2. Capture identity gate: current environment vs original A1R2 record.
    a1r2 = json.loads(A1R2.read_text(encoding="utf-8"))
    recorded = a1r2["capture_identity"]
    from qdrant_client import QdrantClient

    client = QdrantClient(url="http://127.0.0.1:6333", timeout=30)
    col = client.get_collection("panda_knowledge_v1")
    import psycopg
    import os

    conn = psycopg.connect(os.getenv("PANDA_DATABASE_URL"))
    fingerprint = conn.execute("SELECT fingerprint FROM index_identities").fetchone()[0]
    conn.close()
    from panda_agent.sparse import create_sparse_encoder
    from panda_agent.llm.vertex import VertexSettings

    _, receipt = create_sparse_encoder(PROJECT_ROOT)
    manifest = json.loads((PROJECT_ROOT / "data" / "manifests" / "source_manifest.json").read_text(encoding="utf-8"))
    locked = {r["repo_id"]: r["commit_sha"] for r in manifest["repositories"]}
    current_identity = {
        "qdrant_collection": "panda_knowledge_v1",
        "qdrant_points": col.points_count,
        "index_identity_fingerprint": fingerprint,
        "dense": f"size={col.config.params.vectors['dense'].size} distance={col.config.params.vectors['dense'].distance} name=dense",
        "sparse_vector": "name=sparse modifier=idf",
        "sparse_encoder_receipt": f"{receipt.model_name} {receipt.language} {receipt.vector_name} {receipt.modifier} fastembed {receipt.fastembed_version}",
        "embedding_model": VertexSettings.from_env().embedding_model,
        "candidate_pool_per_channel": policies.candidate_pool_per_channel,
        "locked_repositories": locked,
    }
    recorded_locked = recorded["source_manifest_repositories"]
    identity_match = (
        current_identity["qdrant_collection"]
        == "panda_knowledge_v1"
        and current_identity["index_identity_fingerprint"] == recorded["index_identity_fingerprint"]
        and current_identity["dense"] == recorded["dense_vector"]
        and current_identity["sparse_vector"] == "name=sparse modifier=idf"
        and current_identity["embedding_model"] == recorded["embedding_model"].split(" ")[0]
        and current_identity["candidate_pool_per_channel"] == recorded["candidate_pool_per_channel"]
        and current_identity["sparse_encoder_receipt"] == recorded["sparse_encoder_receipt"]
        and current_identity["qdrant_points"] == recorded["qdrant_points"]
        and current_identity["locked_repositories"] == recorded_locked
    )

    # 3. v1 row verification.
    v1_rows = [json.loads(line) for line in V1.read_text(encoding="utf-8").splitlines() if line.strip()]
    v1_ids = [row["case_id"] for row in v1_rows]
    invalid_rows = set(REPAIRED_CORE)
    reusable = [row for row in v1_rows if row["case_id"] not in invalid_rows]

    # 4. Semantic activation precheck (pure, faithful full plans).
    semantic_active: dict[str, bool] = {}
    for case_id in REPAIR_SET:
        plan = RetrievalPlan.model_validate(plans[case_id])
        question = provenance[case_id]["question"]
        bundle = DenseQueryBundle.from_semantic_query(question, build_semantic_query(question, plan))
        semantic_active[case_id] = bundle.semantic is not None

    payload = {
        "frozen_at": datetime.now(timezone.utc).isoformat(),
        "frozen_before_any_live_retrieval": True,
        "provenance_repair_set": REPAIR_SET,
        "repaired_core_cases": REPAIRED_CORE,
        "supplemental_repair_cases": SUPPLEMENTAL,
        "plan_by_case": plans,
        "plan_provenance_by_case": provenance,
        "identity_gate": {
            "recorded_identity": recorded,
            "current_identity": current_identity,
            "result": "MATCH" if identity_match else "BLOCKED",
        },
        "v1_check": {
            "v1_row_count": len(v1_rows),
            "v1_case_ids": v1_ids,
            "invalid_rows": sorted(invalid_rows),
            "reusable_row_count": len(reusable),
        },
        "semantic_active_by_case": semantic_active,
    }
    OUTPUT.write_text(json.dumps(payload, indent=1, default=str), encoding="utf-8")
    print(json.dumps({
        "identity_gate": payload["identity_gate"]["result"],
        "v1_rows": len(v1_rows),
        "reusable": len(reusable),
        "semantic_active": semantic_active,
        "budgets_policy_equals_c3r3": {c: provenance[c]["source_budgets_policy_equals_c3r3_record"] for c in REPAIR_SET},
    }, indent=1))


if __name__ == "__main__":
    main()
