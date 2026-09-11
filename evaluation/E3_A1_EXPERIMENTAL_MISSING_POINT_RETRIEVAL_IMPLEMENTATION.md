# E3-A1 Implementation Report: Experimental Missing-Point Targeted Retrieval

**Status:** COMPLETE
**Verdict:** COMPLETE / PASS / EXPERIMENTAL_MISSING_POINT_TARGETED_RETRIEVAL_IMPLEMENTED
**Starting Baseline HEAD:** `6d0515e0c30ac3038546a3139ddf8916c6d606b0`
**Authoritative Contract:** `evaluation/E3_A0_MISSING_POINT_TARGETED_RETRIEVAL_CONTRACT.md`

---

## 1. Implemented Architectural Seams

1. **Mode Isolation & Public Invariance:**
   - E3 triggers strictly when `answer_point_coverage_mode == "runtime_e1_v2"`.
   - `DEFAULT_ANSWER_POINT_MODE = "legacy_question_core"` and `shadow_e1_v2` remain completely unaffected and never trigger E3.
   - Public schema invariants preserved: `QAResult`, `ClaimCitation`, and `QAStatus` are unchanged. Internal `e3_trace` is exposed only via detailed diagnostics.
   - Zero runtime import of `global_candidate_pool.py` or `evaluation/c8_global_treatment.py`.
2. **Strict Trigger Contract:**
   - Triggers only if all trigger conditions hold: mode is `runtime_e1_v2`, first coverage review is structurally valid, `coverage_evaluable == True`, `missing_answer_point_ids` is non-empty, all missing IDs belong to runtime points, no version conflict, `missing_point_retrieval_count == 0`, and `revision_count == 0`.
3. **Retrieval Objective vs. Global Reranker Query:**
   - **Targeted collection query:** `<original_question> + Target missing question aspects: - <point text>` in original declaration order. Excludes Gold answers/sources, review reasons, draft claims, and unsupported claim prose.
   - **Global reranker query:** `original_question` ONLY (Sentinel 1). Prevents facet double-weighting and preserves strong initial evidence.
4. **Plan Preservation & Dedicated Budget:**
   - Frozen `deepcopy` snapshot of original `RetrievalPlan` (locked repositories, versions, symbols, source budgets).
   - Dedicated counter `missing_point_retrieval_count <= 1` is consumed *prior* to external dispatch, semantically distinct from pre-answer `retrieval_count`.
5. **Candidate Capture & Cross-Pass Global Fusion:**
   - Private opt-in `capture_candidates=True` on `Retriever.retrieve()` captures raw channel rankings with zero duplicate retrieval/model calls (Sentinel 3).
   - Cross-pass candidates (initial, optional pre-answer targeted, and E3 targeted) deduplicated by `object_id`.
   - Bounded weighted RRF (`RRF_K=60`, exact 2.0, dense 1.0, sparse 1.0, paper 1.15, workflow 1.2, graph 0.8; tie-break lexical `object_id`) takes best rank per channel across passes. Retained as experimental candidate, not validated optimal.
   - Strict payload content identity check (`source_id`, `source_version_id`, `locator`, `text`, `object_type`, `title`); mismatch aborts update.
6. **Single Global Rerank & Authoritative Evidence Selection:**
   - Targeted pass performs 0 local reranks (Sentinel 2). Exactly 1 global rerank is executed on top candidates.
   - Reuses shared `_prioritize_and_select_evidence` (`select_final_evidence`) respecting source budgets, symbols, and diversity.
7. **Atomic Evidence Update & Exception / Honest No-Gain Bound:**
   - Bundle evidence is updated only upon successful selection of at least one newly admitted object.
   - Single structured `try...except` boundary: on exception, consistency failure, empty targeted pool, or zero new objects, retains prior bundle with `atomic_update_status: "no_gain"` / `"failure"`.
   - Linear progression: continues through `revise -> verify -> finalize` with 0 retry; `revision_count <= 1`.
8. **Narrow Retained-Support Claims Ledger:**
   - Protects only unchanged, previously verified supported claims whose cited evidence was displaced by global re-selection.
   - Exact structural matching (`claim_id`, `claim_text`, `evidence_ids`, point mappings).
   - New or modified claims are strictly rejected from citing ledger-only evidence.
   - Normal deterministic checks (version, locator, identifier) remain enforced without waiver.
   - In `_finalize`, actually cited retained evidence is appended in deterministic sorted order.

---

## 2. Review History & Defect Corrections

- **Staffer Delegation History (5 AGY development worker jobs; model: Gemini 3.8 Flash (High)):**
  - Initial Implementation Worker: `staffer-mtw5cmk3-36aaeedb`
  - Independent Review Worker: `staffer-mtw5zhmy-18dea665` (initially reported PASS; host inspection identified defects requiring remediation)
  - Fix Remediation Worker: `staffer-mtw67dh1-de69edab` (remediated 8 host-identified defect areas)
  - Final Review Worker: `staffer-mtwvvisa-d3b6dc77` (completed: bounded corrections and independent review; no remaining actionable findings)
  - Lifecycle Documentation Worker: `staffer-mtwvw2jm-24f28949`
- **Specific Host-Identified Corrections Remediated:**
  1. Attempt consumed before external calls and assigned to state immediately.
  2. Structured `try...except` exception boundary ensuring honest no-gain continuation without retry.
  3. Early guard against empty targeted pools (`atomic_update_status: "no_gain"`).
  4. Private opt-in `capture_candidates: bool = False` preventing unwanted sidecars in legacy/production.
  5. List iteration order preserved for cited evidence with deterministic sorted retained evidence.
  6. Payload content comparison ignoring channel scores and channel lists.
  7. Shared `_prioritize_and_select_evidence` seam extracted without synthetic plan budgets.
  8. Exact RRF sorting by global best rank and exact structured ledger comparison without whitespace stripping.
- **Final Corrections and Acceptance:** Removed catch-and-retry on `TypeError`, preserved legacy/shadow retrieval signatures, checked missing snapshots before E3 collection, and removed test-only Agent state. Host inspected the final targeted diffs and ran the final focused suite successfully.

---

## 3. Focused Verification & Test Accounting

Final host verification used deterministic fakes only:

```powershell
$env:PYTHONPATH = 'src;tests/unit'
python -m pytest tests/unit/test_e3_missing_point_retrieval.py tests/unit/test_e2_a1_answer_point_coverage.py tests/unit/test_qa.py tests/unit/test_retrieval.py tests/unit/test_retrieval_trace.py tests/unit/test_c8_a0_targeted_merge_semantics.py -q
```

Result: **189 passed, 9 subtests passed**. E3 accounts for 42 tests (T1-T20,
three sentinels, and 19 defect regressions); the other 147 are affected neighboring
tests. This is focused development verification, not the full unit suite or science.
Earlier worker runs: initial 23 E3 tests and 127 neighbors; first review 23 E3 and
99 neighbors; repairs 36 E3 plus 99 neighbors; final review 141 tests across E3,
E2 coverage, QA and C8 merge semantics. Counts overlap and are not additive.

T1-T20 and all three sentinels PASS. Fake successful E3 recovery uses zero local
targeted reranks and one global rerank, with the original question as its query.
Static changed-path/default/import checks and `git diff --check` also PASS.

PANDA scientific/evaluation calls = 0; tokens = 0; new scientific QA executions = 0;
new scientific judge calls = 0. AGY usage is separate development delegation:
five completed jobs, each runner log reports `gemini-3.8-flash-high` and `SUCCESS`.
No claim of zero AGY cost is made; no billing amount was measured.

---
## 4. Concrete Limitations & Next Task

1. **Runtime Experimental Scope Only:** E3 operates exclusively under explicit `runtime_e1_v2` selection. Normal legacy QA is unchanged.
2. **Single Bounded Attempt:** `missing_point_retrieval_count <= 1` and `revision_count <= 1`. No multi-turn retrieval or repair loops.
3. **Static Retained Ledger Scope:** Ledger applies only to verbatim identical supported claims; new/revised claims receive no ledger support.
4. **No Scientific Benefit Claim:** Implementation verification only; does not establish benchmark/novel QA quality improvement.
5. **Next Roadmap Task:** **E3-A2 — Targeted Missing-Point Recovery Validation** (`NEXT_TASK_EXECUTION_AUTHORIZED = false`). No A2 cohort or acceptance threshold is frozen here.

## 5. Internal Trace

Trace records trigger/reason, question-derived missing points/objective, independent counters,
pre-E3 and targeted pass provenance, object/channel ranks, fusion and selected IDs,
new admissions/displacement, retained cited support, atomic update outcome and failure reason.
Recovery is counted only after an evaluable second coverage review; failed or unrun review
never establishes recovery. Candidate payloads stay internal and are not serialized into the public DTO.
