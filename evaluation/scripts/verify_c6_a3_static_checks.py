"""Static verification for C6-A3 frozen production-role decision (no outcome measurements)."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFESTS = ROOT / "evaluation/baselines/manifests"

a2 = json.loads((MANIFESTS / "phase_c_c6_a2_frozen_fusion_policy_comparison_v1.json").read_text(encoding="utf-8"))
audit = json.loads((MANIFESTS / "phase_c_c6_a2_critical_miss_semantics_audit_v1.json").read_text(encoding="utf-8"))
a3 = json.loads((MANIFESTS / "phase_c_c6_a3_frozen_production_role_decision_v1.json").read_text(encoding="utf-8"))

checks = []


def check(name, ok, detail=""):
    checks.append((name, bool(ok), detail))


head = subprocess.run(
    ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True
).stdout.strip()
head_subject = subprocess.run(
    ["git", "log", "--format=%s", "-1"], cwd=ROOT, capture_output=True, text=True
).stdout.strip()
check(
    "source HEAD matches expected (or the A3 decision commit)",
    a3["source_head"] == "200d8d51c2dce164de5d027751be97b371551fc3"
    and (head == "200d8d51c2dce164de5d027751be97b371551fc3"
         or head_subject == "C6 A3 frozen fusion production role decision"),
    head,
)
check("A2 manifest says PASS", a2["a2_methodology_result"] == "PASS")
check("critical-miss audit says PASS", audit["critical_miss_semantics_audit"] == "PASS")
check(
    "corrected global passing set = P3 only",
    audit["corrected_global_passing_policy_set"] == ["P3_SPARSE_HEAVY"]
    and a2["global_passing_policy_set"] == ["P3_SPARSE_HEAVY"],
)
check(
    "SemanticDense conclusion INSUFFICIENT / KEEP_DISABLED",
    a2["semantic_decision_tree"]["SEMANTIC_CONTRIBUTION"] == "INSUFFICIENT"
    and a2["semantic_decision_tree"]["semantic_production_role_evidence"] == "KEEP_DISABLED"
    and a3["role_decisions"]["SemanticDense"]["role"] == "KEEP_DISABLED",
)
check(
    "intent-aware eligible = true",
    a2["intent_diagnostics"]["INTENT_AWARE_ELIGIBLE"] is True
    and audit["corrected_INTENT_AWARE_ELIGIBLE"] is True,
)
mapping_a2 = a2["intent_diagnostics"]["C6_INTENT_AWARE_V1"]
check(
    "intent mapping matches authoritative audit",
    mapping_a2 == audit["corrected_C6_INTENT_AWARE_V1"]
    and mapping_a2["installation"] == "P3_SPARSE_HEAVY"
    and mapping_a2["troubleshooting"] == "P2_EXACT_HEAVY"
    and all(v == "P0_CURRENT" for k, v in mapping_a2.items() if k not in ("installation", "troubleshooting")),
)
check(
    "novel_replay_status = ABSENT",
    a2["novel_gate"]["novel_replay_status"] == "ABSENT" and a3["novel_replay_status"] == "ABSENT",
)
check(
    "production activation authorization = false",
    a2["production_activation_authorized"] is False
    and a3["production_activation_authorized"] is False
    and a2["novel_gate"]["NEW_PRODUCTION_POLICY_ACTIVATION"] == "NOT_AUTHORIZED_BY_C6_A2_ALONE",
)

status = subprocess.run(
    ["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True
).stdout.splitlines()
prod_changed = [l for l in status if l.strip().endswith(tuple(f"/{f}" for f in (
    "retrieval.py", "fusion_replay.py", "entity_resolution.py", "evaluation.py",
    "evaluation_runner.py", "c4_sparse_evaluation.py", "knowledge_store.py",
))) or any(l.strip().endswith(suffix) for suffix in (".py",)) and l[3:].startswith("src/")]
check("production files unchanged", not prod_changed, "; ".join(prod_changed))

untracked = [l[3:].strip() for l in status if l.startswith("??")]
allowed_new_files = {
    "evaluation/baselines/manifests/phase_c_c6_a3_frozen_production_role_decision_v1.json",
    "evaluation/scripts/verify_c6_a3_static_checks.py",  # this checker itself
}
new_outcome_files = [f for f in untracked if f not in allowed_new_files]
check("no new evaluation outcome files", not new_outcome_files, "; ".join(new_outcome_files))

# A3 artifact internal coherence
check(
    "A3 artifact role set complete",
    set(a3["role_decisions"]) == {
        "P0_CURRENT", "P1_RAW_DENSE_CENTERED", "P2_EXACT_HEAVY", "P3_SPARSE_HEAVY",
        "P4_SEMANTIC_AUXILIARY_25", "P5_SEMANTIC_EXPANSION_ONLY", "SemanticDense",
        "C6_INTENT_AWARE_V1",
    },
)
check(
    "A3 verdict PASS / C6 COMPLETE / next C7",
    a3["c6_a3_verdict"] == "PASS"
    and a3["c6_closeout"]["c6_lifecycle_status"] == "COMPLETE"
    and a3["next_roadmap_owner"]["status"] == "NEXT_ELIGIBLE / NOT_STARTED"
    and a3["next_roadmap_owner"]["task"].startswith("C7"),
)
check(
    "A3 records no new measurements and unchanged production",
    a3["no_new_outcome_measurement"] is True
    and a3["production_state_after_a3"]["production_fusion_changed"] is False
    and a3["production_state_after_a3"]["production_code_changed"] is False,
)

diff_check = subprocess.run(
    ["git", "diff", "--check"], cwd=ROOT, capture_output=True, text=True
)
check("git diff --check clean", diff_check.returncode == 0, diff_check.stdout.strip())

# C6 lifecycle wording must not regress to ACTIVE in any current-status section
# (historical records predate C6 and never carry a C6 status phrase).
import re

status_phrase = re.compile(
    r"C6 is `ACTIVE`"
    r"|Multi-channel fusion evaluation is `ACTIVE`"
    r"|Multi-channel fusion evaluation\*\*: `ACTIVE`"
)
roadmap_text = (ROOT / "docs/GENERALIZATION_ROADMAP.md").read_text(encoding="utf-8")
status_text = (ROOT / "docs/EVALUATION_STATUS.md").read_text(encoding="utf-8")
stale = status_phrase.findall(roadmap_text) + status_phrase.findall(status_text)
check("no stale C6 ACTIVE status wording in current docs", not stale, str(stale))
phase_c_status = roadmap_text.split("## Phase C status", 1)[-1]
m = re.search(r"C6 — Multi-channel fusion evaluation is `([A-Z_]+)`", phase_c_status)
check(
    "Phase C status summary: C6 must be COMPLETE",
    m is not None and m.group(1) == "COMPLETE",
    m.group(1) if m else "phrase missing",
)

failed = [c for c in checks if not c[1]]
for name, ok, detail in checks:
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail and not ok else ""))
print(f"\n{len(checks) - len(failed)}/{len(checks)} checks passed")
sys.exit(1 if failed else 0)
