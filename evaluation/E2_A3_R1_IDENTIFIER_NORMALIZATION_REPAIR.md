# E2-A3-R1 — Identifier Normalization Repair and Targeted Revalidation

## Candidate state before live execution

Historical E2-A3 = COMPLETE / FAIL / Q7. FR1 = COMPLETE / PASS /
Q7_VERIFIER_IDENTIFIER_NORMALIZATION_REPAIR_JUSTIFIED. Starting HEAD:
e5941c5f9aac45d98b739a48b245be53a41c6d80.

The production repair adds `_normalise_rejected_identifier_token` in qa.py and
uses it only in the unsupported-identifier rejecting loop. It retains terminal
period removal and removes one single terminal colon unless ending in ::.
Positive-support logic, regex, eligibility, matching, prompts, E1/E2, retrieval,
public API/DTO and legacy compatibility remain unchanged. Pre-verdict default
is legacy_question_core. No case-specific logic or allowlist was added.

Focused tests passed: 130 across the new R1 module and existing A3 runtime,
A3 evaluator, E2-A1 coverage, and QA modules. The complete repaired-code frozen
scan independently recomputed 56 executions, 299 serialized claim copies, and
157 snapshots (legacy 81/runtime 76). Exactly one rejection outcome changed:
g112 runtime initial claim_3, supported PndLmdDataReader::fillData with a trailing
prose colon. No genuinely unsupported base became accepted; no accepted check
became rejected. g110 prefix_pid.root/prefix_boost.root and g002 SIMPATH/bin/cmake
controls remained rejected. S1-S12 all PASS. Whole-module AST reversal verifies
that only the approved helper and one call differ from the starting QA code.

Static evidence: `e2_a3_r1_identifier_normalization_static_result.json`.
Protocol: `E2_A3_R1_TARGETED_REVALIDATION_PREREGISTRATION.md`.
Manifest: `e2_a3_r1_targeted_revalidation_manifest.json`.
Fixed cohort: g112, g110, g002, g044, g027, ten fresh executions and five blind
judgments after separate candidate/raw freezes. No retrieval bootstrap.

Scientific calls before candidate freeze: 0. Prospective verdict: NOT_RUN.
No runtime activation has occurred at this candidate boundary. Results will be
appended only after raw and judgments are independently committed.
