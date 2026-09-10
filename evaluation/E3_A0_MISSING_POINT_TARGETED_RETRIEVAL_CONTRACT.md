# E3-A0 Missing-Point Targeted Retrieval Architecture and Dependency Contract

## 0. Executive Summary and Task Identity

- **Task ID:** `E3-A0`
- **Task Title:** Missing-Point Targeted Retrieval Architecture and Dependency Contract
- **Lifecycle Status:** `COMPLETE / PASS / MISSING_POINT_TARGETED_RETRIEVAL_CONTRACT_ESTABLISHED`
- **Parent Phase:** `Phase E — Answer Generalization` (`IN_PROGRESS / E2_CORE_COMPLETE / E3_IN_PROGRESS`)
- **Next Recommended Task:** `E3-A1 — Experimental Missing-Point Targeted Retrieval Implementation` (`NOT AUTHORIZED`)
- **Scope:** Static architecture, dependency reconciliation, and verification contract only. PASS applies only to this static contract, not implementation or scientific acceptance.
- **Inspected baseline:** `351bf144986b06027f22f17629c2dc29ec78b9e4` (`Fix generic external type sanitization`). No product code implementation, no test code execution, no scientific validation.
- **Modifications:** Documentation only (`evaluation/E3_A0_MISSING_POINT_TARGETED_RETRIEVAL_CONTRACT.md`, `docs/EVALUATION_STATUS.md`, `docs/GENERALIZATION_ROADMAP.md`).
- **Resource Usage:** 0 product code changes, 0 test suite changes, 0 PANDA scientific calls, 0 PANDA evaluation tokens.

---

## 1. Reconstruction of Current QA Graph from Source

Source inspection of `src/panda_agent/qa.py` (lines 1020–2298) reveals the authoritative runtime state and graph topology:

### 1.1 State Definition (`QAState`)
```python
class QAState(TypedDict, total=False):
    question: str
    answer_point_coverage_mode: str  # "legacy_question_core" | "shadow_e1_v2" | "runtime_e1_v2"
    runtime_answer_points: list[dict[str, str]]
    missing_answer_point_ids: list[str]
    answer_point_audit: dict[str, Any]
    bundle: dict[str, Any]
    sufficient: bool
    draft: dict[str, Any]
    errors: list[str]
    supported_claims: list[dict[str, Any]]
    unsupported_claim_ids: list[str]
    missing_requirement_ids: list[str]
    answer_requirements: list[dict[str, str]]
    claim_audit: list[dict[str, Any]]
    revision_count: int
    retrieval_count: int
    node_timings_ms: dict[str, int]
    result: dict[str, Any]
```

### 1.2 Graph Construction and Execution Flow
```text
START
  │
  ▼
retrieve (calls self.retriever.retrieve(question))
  │
  ▼
sufficiency (inspects bundle, sets state["sufficient"])
  │
  ├─ sufficient == True ─────────────► answer
  ├─ sufficient == False
  │    ├─ retrieval_count < getattr(getattr(self.retriever, "policies", None), "max_targeted_retrievals", 1)
  │    │  and not version_conflicts ─► targeted_retrieve ──► sufficiency
  │    └─ otherwise ─────────────────► finalize
  ▼
answer (generates initial atomic claims, normalizes mappings)
  │
  ▼
verify (validates citations, runs claim review / answer-point coverage review)
  │
  ├─ errors present and revision_count < 1 ──► revise
  └─ otherwise ──────────────────────────────► finalize
  ▼
revise (revises unsupported claims / missing points using existing evidence)
  │
  ▼
verify (re-evaluates revised claims)
  │
  ▼
finalize (constructs QAResult from supported claims or refusal branches)
  │
  ▼
END
```

> [!IMPORTANT]
> **Key Runtime Property of `_revise` (`qa.py`, lines 1941–1949):**
> `_revise` merges supported claims and revised claims into `draft["claims"] = merged` and **explicitly clears `supported_claims: []`**.
> Consequently, when the second `_verify` executes, `state["supported_claims"]` is empty; `_verify` re-evaluates all claims from `draft["claims"]`. To prevent regression or claim text/citation/mapping tampering, an immutable snapshot of previously supported claims is mandatory alongside the evidence ledger.

---

## 2. Current Targeted Retrieval vs. E3 Missing-Point Targeted Retrieval

The codebase already contains a node named `_targeted_retrieve` (`qa.py`, lines 1085–1100). It is **not** E3. E3 addresses a completely distinct architectural stage and failure class.

| Dimension | Current Pre-Answer `_targeted_retrieve` | E3 Missing-Point Targeted Retrieval |
| :--- | :--- | :--- |
| **Pipeline Stage** | Pre-answer (between `retrieve` and `sufficiency`). | Post-answer / post-verify (after initial `_verify`). |
| **Trigger Mechanism** | `sufficiency` node marks `sufficient=False` based on missing required source types or retrieval errors. | `_verify` semantic review identifies non-empty `missing_answer_point_ids` in `runtime_e1_v2`. |
| **Objective Origin** | `plan["required_source_types"]` + sufficiency error strings (e.g. `symbol:...`). | Original user question + exact missing answer-point texts in question order. |
| **Answer Existence** | No draft answer or claims exist yet. | Draft answer and verified `supported_claims` already exist. |
| **Evidence Merge** | Evidence-level prepend: `[*extra["evidence"], *bundle["evidence"]]`, deduplicated by `evidence_id`, truncated to configured `final_evidence_limit` (currently 12). | Candidate-level consolidation across all pre-E3 passes and one E3 pass (`object_id` deduplication, best-rank RRF per channel, one global rerank, standard policy selection up to configured `final_evidence_limit`). |
| **Downstream Flow** | Returns to `sufficiency` -> `answer`. | Routes to `_revise` (never generates a fresh answer from scratch). |
| **Budget Counter** | `retrieval_count` (bounded by configured `policies.max_targeted_retrievals`, default 1; configurable `ge=0, le=2`). | Dedicated `missing_point_retrieval_count` (strictly hard-bounded `<= 1`). |

---

## 3. Current E2 Missing-Point Signal and the Architectural Gap

In Phase E2 (`runtime_e1_v2` / `shadow_e1_v2`), `_verify()` performs semantic answer-point coverage review via `ANSWER_POINT_COVERAGE_REVIEW_SYSTEM_PROMPT` and outputs:
- `missing_answer_point_ids`: list of semantic point IDs from the decomposed question that are not supported by any valid claim.
- `answer_point_audit`: audit record containing `coverage_evaluable`, `coverage_complete`, and `claim_mappings`.

When a genuine missing point is detected in E2:
```text
_verify finds missing_answer_point_ids
  │
  ▼
errors.extend(f"missing answer point {pid}" for pid in missing_points)
  │
  ▼
_revise prompt includes missing_answer_points, BUT only existing bundle["evidence"] is provided!
```

**The E3 Gap:** If the required evidence for the missing facet was not retrieved in the initial pass, `_revise` cannot invent facts from thin air. It either leaves the point uncovered or risks hallucination. The proposed E3 recovery addresses this gap by retrieving targeted evidence before revision; its benefit is not yet measured.

---

## 4. Reconciliation of Deferred C8 Dependency

### 4.1 Historical Status of C8
Authoritative manifest: `evaluation/baselines/manifests/phase_c_c8_a2_applicability_closeout_v1.json`
- **Status:** `C8 = DEFERRED / INSUFFICIENT_NATURAL_TARGETED_APPLICABILITY_FOR_PREREGISTERED_A3`
- **Reason:** Across the 80-case dev population, only 1 case (`g007`, 1.25%) naturally entered the old pre-answer targeted retrieval branch. The preregistered minimum cohort (6 natural cases) was not met.
- **Architectural vs. Scientific Reality:**
  - `ARCHITECTURAL_PROBLEM_IDENTIFIED`: **True** (evidence-level prepend/truncate without global reconsideration is suboptimal).
  - `TREATMENT_BENEFIT_DEMONSTRATED`: **False** (unevaluated on a natural cohort).
  - `C8_PRODUCTION_PROMOTION`: **DEFERRED**.
  - `GLOBAL_RECOMPUTATION_WIRED_TO_PRODUCTION`: **False**.

### 4.2 C8 Does Not Block E3
- **Decision D1:** C8 deferred status is **NOT** an architectural blocker for E3.
- **Rationale:** C8 suffered from natural trigger sparsity because the pre-answer sufficiency heuristic rarely failed. E3 introduces an independently justified Phase-E trigger: *verified missing semantic answer points in generated answers*. This is a new use case, not post-hoc recruitment for C8.
- **Boundary:** We do not reopen or rescore C8. We reuse C8's structural design principles without claiming C8 treatment validation.

### 4.3 C8 Design Principles Reused in E3
From `src/panda_agent/global_candidate_pool.py` and `evaluation/c8_global_treatment.py`:
1. **Candidate Identity:** `object_id` is the primary cross-pass key. `evidence_id` is occurrence/channel output provenance only.
2. **Provenance Preservation:** Track occurrences across all pre-E3 passes (initial and any pre-answer targeted passes) and the E3 targeted pass.
3. **Best-Rank Fusion:** For each object and executed channel, take the minimum rank across all executed passes:
   $$\text{rank}^*(o, c) = \min_{p \in \{\text{pre-E3 passes}, \text{E3 targeted}\}} \text{rank}_p(o, c)$$
4. **Weighted Reciprocal Rank Fusion (RRF):**
   $$\text{score}(o) = \sum_{c \in \text{channels}(o)} \frac{w_c}{60 + \text{rank}^*(o, c)}$$
   Weights: `exact: 2.0`, `dense: 1.0`, `sparse: 1.0`, `paper: 1.15`, `workflow: 1.2`, `graph: 0.8`.
5. **No Origin Bonus:** No bonus for `BOTH` origins or targeted pass.
6. **Deterministic Tie-Breaking:** Lexicographic order of `object_id`.
7. **Downstream Policy Selection:** Feed fused candidates into standard LLM reranker (top 30) and `select_final_evidence()`, preserving mandatory priority ordering (hinted/required source types, symbol matches), source/type diversity, backfill, source budgets, and configured `final_evidence_limit` (currently 12; policy-selected, not naive top-12).

### 4.4 Production Isolation Boundary
- `src/panda_agent/global_candidate_pool.py` is explicitly marked `UNWIRED / SHADOW-EVALUATION CONTRACT`. Production runtime must **not** import or call it.
- `evaluation/c8_global_treatment.py` is a frozen evaluation script. Production runtime must **not** import or call it.
- No monkeypatching evaluator harness in runtime.
- E3 targeted collection must **NOT** perform its own rerank before the single global rerank.
- E3-A1 will implement a lean, internal candidate-capture and consolidation seam directly inside `retrieval.py` / `qa.py`, avoiding external framework overhead.
- Deduplication: Dedup same object once with best rank per channel across passes; consistent payload/version across passes or abort update (fail closed); no fuzzy deduplication.

---

## 5. Primary E3 Trigger Contract (Decision D2)

A missing-point targeted retrieval may occur if and only if **ALL 7** conditions are satisfied:

1. **Explicit Experimental Mode:** `state.get("answer_point_coverage_mode") == "runtime_e1_v2"`.
2. **Structural Integrity:** First semantic coverage review completed structurally (JSON and schema valid, no parser exceptions).
3. **Evaluable Coverage:** `state.get("answer_point_audit", {}).get("coverage_evaluable") is True` (no unhandled review errors; review status is not `unknown` or `notrun`; `global_review_failure` is False).
4. **Non-Empty Missing Set:** `len(state.get("missing_answer_point_ids", [])) > 0`.
5. **Point Identity Validity:** Every ID in `missing_answer_point_ids` exists in `state["runtime_answer_points"]`.
6. **No Version Conflicts:** `not state["bundle"]["plan"].get("version_conflicts")`.
7. **Budget Available:** Dedicated `state.get("missing_point_retrieval_count", 0) == 0` and `state.get("revision_count", 0) == 0`. (Pre-answer `retrieval_count` is governed independently by configured `policies.max_targeted_retrievals`).

### Explicit Non-Triggers
E3 retrieval **MUST NOT** trigger on:
- Normal QA mode (`legacy_question_core`).
- Diagnostic shadow mode (`shadow_e1_v2`).
- Coverage review schema/structural failure.
- Unknown or invalid answer point IDs.
- Global reviewer failure or unevaluable review (`coverage_evaluable != True`, `unknown`, `notrun`).
- Gold benchmark requirements or obligations.
- Legacy `missing_requirement_ids` alone.
- Unsupported-claim verifier errors alone.
- Verifier reason prose.
- Benchmark case IDs or bespoke case rules.
- Second verification pass (`revision_count >= 1`).

---

## 6. Execution Path and Mode Governance (Decision D10)

- **No New Mode:** E3 uses the existing explicit runtime mode; no fourth answer-point mode is needed.
- **Proposed Path:** Future E3 missing-point targeted retrieval runs inside `runtime_e1_v2` under the explicit trigger contract.
- **Default Preservation:** `DEFAULT_ANSWER_POINT_MODE = "legacy_question_core"` remains unchanged. Standard production `run()` and `run_detailed()` are unaffected.
- **Shadow Preservation:** `shadow_e1_v2` remains a read-only diagnostic control path without E3 retrieval.

---

## 7. Retrieval Objective Specification (Decision D3)

The retrieval objective for E3 must be constructed strictly from question-derived obligations.

### 7.1 Allowed Inputs
1. The original user question (`state["question"]`).
2. The exact text of missing answer points resolved from `runtime_answer_points` corresponding to `missing_answer_point_ids`, preserved in original question order.

### 7.2 Format Specification
```text
<original user question>

Target missing question aspects:
- <exact missing answer point 1 text>
- <exact missing answer point 2 text>
```

### 7.3 Forbidden Inputs
The retrieval objective **MUST NOT** include:
- Gold answer text, Gold source IDs, or Gold relevance labels.
- Benchmark case IDs (e.g. `g007`, `pair09`).
- Legacy `missing_requirement_ids` or `answer_requirements` prose.
- Verifier reason prose or error strings.
- Model-generated draft answer text or claim text.
- Unsupported claim text from draft.
- Expected symbols, filenames, or PDF page numbers not present in the user question.

---

## 8. Original Plan Constraints and Version Safety (Decision D13)

The E3 targeted pass is a query refinement strictly bounded by the initial retrieval plan:
- **Explicit Original Plan Snapshot:** An explicit immutable snapshot of `bundle["plan"]` is frozen before any pre-answer targeted refinement and before E3.
- **Preserve ALL Plan Constraints:**
  - `source_budgets`
  - `required_source_types`
  - `version_conflicts`
  - `resolved_versions`
  - `target_repositories`
  - explicit user paths, symbols, concept scopes
- **No Prose Reanalysis:** The system **must not** re-extract or infer new repositories, versions, or plan constraints from generated draft prose or claims.
- **Version Safety:** If the original plan contained `version_conflicts`, E3 retrieval is suppressed immediately.

---

## 9. Budget and Total-Loop Boundary (Decisions D4, D5)

- **Dedicated Counter:** `missing_point_retrieval_count: int` (initialized to 0, incremented/consumed on attempt, strictly hard-bounded: `missing_point_retrieval_count <= 1`).
- **Attempt Consumed Before Calls:** `missing_point_retrieval_count` is incremented/consumed to 1 **before** dispatching external retrieval or model calls, preventing retry loops on failure.
- **Decoupled from Pre-Answer Retrieval:** Pre-answer targeted retrieval preserves its configured existing budget (`retrieval_count < getattr(policies, "max_targeted_retrievals", 1)`, default 1, configurable `ge=0, le=2`). Only E3 missing-point targeted retrieval and revision are strictly, unconditionally hard-bounded to `<= 1`.
- **Maximum Execution Trace:**
  ```text
  retrieve (retrieval_count=0)
    │
    ▼
  [optional pre-answer targeted_retrieve(s)] (retrieval_count < policies.max_targeted_retrievals)
    │
    ▼
  answer
    │
    ▼
  verify (first check)
    │
    ▼ [if missing_answer_point_ids and missing_point_retrieval_count == 0]
  missing_point_retrieve (missing_point_retrieval_count consumed -> 1)
    │
    ▼
  revise (revision_count consumed -> 1; clears supported_claims, sets draft["claims"] = merged)
    │
    ▼
  verify (second check: matches unchanged claims to retained snapshot; revision_count==1, missing_point_retrieval_count==1)
    │
    ▼ [cannot trigger missing_point_retrieve or revise]
  finalize
  ```
- **Loop Termination:** At most one E3 retrieval attempt and at most one revision attempt across the lifecycle. No cycles `retrieve -> answer -> verify -> retrieve` are permitted.

---

## 10. Post-Retrieval Generation Contract (Decisions D6, D7)

- **No Full Answer Re-Generation (D7):** E3 does **not** call `_answer`. Calling `_answer` would discard previously verified supported claims, increase latency, and invite regressions.
- **Direct Route to Revision (D6):** E3 routes directly from `missing_point_retrieve` to `_revise`.
- **Revision Role:** `_revise` receives:
  - `already_verified_claims_do_not_repeat`: unchanged claims from `retained_supported_claims` snapshot.
  - `untrusted_evidence`: updated globally selected evidence.
  - Provider review context includes exact cited support evidence as well as selected evidence; new/revised claims may use selected only.
  - Missing answer points and unsupported draft claims to address.
  - `_revise` merges supported and revised claims into `draft["claims"]` and clears `supported_claims: []`.

---

## 11. Supported-Claim Citation Displacement Resolution

### 11.1 The Displacement Problem
When E3 performs global candidate reconsideration, new targeted candidates enter the candidate pool. The policy-selected evidence (bounded by configured `final_evidence_limit`, currently 12; selected via mandatory/diversity/backfill, not naive top-12) may admit new evidence items that push out (displace) some evidence items from the initial selection.
If an already-verified claim from round 1 cited an evidence item that is displaced from the new selection, a naive re-verification in round 2 would fail the claim as `invalid evidence for <claim_id>`.

### 11.2 Rejection of Flawed Proposals
- **Reject Selection Pinning:** We must **not** force-pin all previously cited evidence into the new selection. That would displace strong candidates and defeat global ranking.
- **Reject Minimum Slot Inflation:** We must **not** expand the configured selection limit (e.g. 12 + 2 extra slots). Selection remains strictly bounded by configured `final_evidence_limit` (currently 12, not a newly hardcoded constant).

### 11.3 Architectural Solution: Retained-Support Evidence Ledger and Retained Supported Claims Snapshot
We introduce an internal, immutable **Retained-Support Evidence Ledger** paired with a **Retained Supported Claims Snapshot**:

1. **Retained-Support Evidence Ledger:**
   - At `missing_point_retrieve`, before updating `bundle["evidence"]`, inspect all claims in `state["supported_claims"]`.
   - Collect the exact evidence items cited by those supported claims:
     ```python
     cited_support_ids = {eid for c in state["supported_claims"] for eid in c.get("evidence_ids", [])}
     retained_support_evidence = {
         eid: evidence_lookup[eid]
         for eid in cited_support_ids
         if eid in evidence_lookup
     }
     ```
   - **Ledger Bound:** The ledger size is strictly bounded by the prior cited selected evidence count.
   - Original `evidence_id` and payload are preserved unmodified in `state["retained_support_evidence"]`.

2. **Explicit Immutable `retained_supported_claims` Snapshot:**
   - Because `_revise` clears `supported_claims: []` and returns `draft["claims"] = merged`, the system captures an explicit immutable snapshot before revision:
     ```python
     retained_supported_claims = [
         {
             "claim_id": c["claim_id"],
             "claim_text": c["claim_text"],
             "evidence_ids": list(c.get("evidence_ids", [])),
             "answer_point_ids": list(c.get("answer_point_ids", [])),
             "declared_answer_point_ids": list(c.get("declared_answer_point_ids", [])),
         }
         for c in state["supported_claims"]
     ]
     ```
   - Stored in `state["retained_supported_claims"]`. Captures exact original claim text, citation IDs, and point mappings (**not** `claim_id` only) to prevent tampering or drift.

3. **Atomic Bundle Update:**
   - `bundle["evidence"]` is updated **only** after complete, successful candidate capture, fusion, reranking, and selection.
   - If targeted retrieval fails, returns empty candidates, produces no gain, or errors out: retain prior usable bundle and support evidence intact.

4. **Policy Selection Stays Normal:**
   - The new `bundle["evidence"]` contains policy-selected evidence items bounded by configured `final_evidence_limit` (currently 12; applying mandatory priorities, source/type diversity, and backfill).

5. **Scoped Provider Context and Verification:**
   - **Provider Review Context:** When building review context, include exact cited support evidence from the ledger as well as newly selected evidence.
   - **Second `_verify` Matching:**
     - Matches unchanged claims in `draft["claims"]` against the `retained_supported_claims` snapshot (verifying exact claim text, citation IDs, and answer point mappings match).
     - For **retained unchanged claims**: evidence IDs may resolve against newly selected `bundle["evidence"]` OR `retained_support_evidence` ledger.
     - For **new or revised claims**: evidence IDs must resolve **only** against the newly selected `bundle["evidence"]`. New or revised claims cannot cite displaced support items from the ledger.
   - **Normal Verification Preserved (No Waiver):** Full verifier checks (code version pinning, locator completeness, identifier validation, deterministic checks, and semantic review) execute normally across all claims without waivers.

6. **Public Boundary Unchanged and Output Evidence Bound:**
   - In `_finalize`: `result.claims` emits verified claims. `result.evidence` emits only the evidence items actually cited by verified claims (`set(claim.evidence_ids)`).
   - **Output Bound:** Output cited union <= prior cited selected evidence count + configured `final_evidence_limit`.
   - Public `QAResult` schema remains strictly identical.

7. **Trace Transparency and Displaced Selected Distinction:**
   - Displaced selected IDs are **not** identical to the retained support subset:
     - `displaced_selected_evidence_ids`: all evidence items in the prior selection that dropped out of the new selection limit.
     - `retained_support_evidence_ids`: strictly the subset of prior evidence that was actually cited by round-1 supported claims and is retained in the ledger.

---

## 12. Global Candidate Reconsideration Contract (Decision D8)

E3 targeted retrieval rejects targeted-first append/truncate. It enforces global reconsideration across all pre-E3 passes (Pass 1 initial + any pre-answer targeted passes) and the E3 targeted pass:

```text
Pass 1 (Initial) Channels: exact, dense, sparse, paper, workflow, graph
[Pass 1b (Pre-Answer Targeted, if executed)] Channels: exact, dense, sparse, paper, workflow, graph
Pass 2 (E3 Targeted) Channels: exact, dense, sparse, paper, workflow, graph
                              │
                              ▼
               Consolidate Candidates by object_id
         (Consistent payload/version or abort; no fuzzy dedup)
                              │
                              ▼
   Compute Best-Rank per Channel: rank*(o, c) = min_p rank_p(o, c)
                              │
                              ▼
                 Weighted RRF Fusion (RRF_K=60)
         (No BOTH bonus; Lexicographic object_id tie-break)
                              │
                              ▼
                  Select Top-30 Rerank Pool
   (E3 targeted collection must NOT rerank before global rerank)
                              │
                              ▼
                  ONE Global LLM Reranker Call
                              │
                              ▼
            Authoritative Evidence Selection (select_final_evidence)
     (Mandatory hinted/required/symbol priorities, diversity, backfill,
      source caps, limit = configured final_evidence_limit [12])
                              │
                              ▼
        Atomic Update: bundle["evidence"] (Policy-Selected)
```

---

## 13. Internal Trace and Provenance Requirements

The internal diagnostic seam `_run_detailed(..., mode="runtime_e1_v2")`
must expose an `e3_trace`; ordinary `run_detailed()` retains the legacy default.
The following are required fields, not a new public schema or fabricated run:

| Fields | Meaning |
| --- | --- |
| triggered, trigger_reason | Eligibility decision, including suppression or attempt failure |
| missing_answer_point_ids, missing_answer_points | Exact IDs and question-derived texts, in original point order |
| retrieval_objective | Original question plus those exact texts only |
| missing_point_retrieval_count, pre_answer_retrieval_count | Separate E3 and existing pre-answer counters |
| baseline_candidates, targeted_candidates | Stable object IDs, bounded payload/version references, pass origins, executed channels and ranks |
| initial_evidence_ids, targeted_evidence_ids | Original selection and materialized targeted evidence; candidate-only collection may leave the latter empty |
| dedup_result | Object membership, all pass/channel occurrences, best ranks and consistency failures |
| globally_selected_evidence_ids | Policy selection result with object-ID mapping |
| newly_admitted, displaced | Object-ID differences with old/new evidence-ID mappings; channel-dependent ID changes alone are not new content |
| retained_support_evidence_ids, retained_supported_claims | Original cited evidence and unchanged claim snapshot, distinct from selection displacement |
| selected_evidence_count, selected_evidence_budget, retained_support_context_count | Selection budget and separate bounded support context |
| post_retrieval_missing_point_result | Second-review evaluability/status, remaining missing IDs and recovered IDs only when evaluable |

`_evidence()` derives `evidence_id` using
`stable_id(object_id, *sorted(channels), prefix="evidence")`; the result is an
opaque derived ID, not a literal path with channel suffixes. Deduplicate candidates
by `object_id`, preserve old citation IDs, and record any new ID for the same object.
An unknown, failed or unrun second review must not be reported as recovered.
Trace atomic update success/failure and unchanged-context no-gain outcomes.
No-gain means no newly selected object relative to the pre-E3 selection;
it is not a new model-based relevance gate.

---
## 14. Honest Failure and Refusal Precedence Contract (Decision D11)

If targeted retrieval recovers no relevant candidates, yields no gain, or revision cannot ground the missing point:
1. **Atomic Update Enforcement:** `bundle["evidence"]` is updated only after complete, successful global selection. Failed, empty, or no-gain retrieval retains the prior usable bundle and support intact.
2. **Attempt Consumed:** `missing_point_retrieval_count` is consumed before calls; no retry or secondary loops.
3. **Refusal Precedence Remains Absolute:**
   Partial `QAStatus.ANSWERED` is **not unconditional**. Existing refusal checks in `_finalize` strictly take precedence:
   - `bundle["plan"].get("version_conflicts")` -> `QAStatus.VERSION_CONFLICT`.
   - Future runtime outcomes / checksums -> refusal basis claim + refusal text.
   - Open-domain universal proofs -> refusal basis claim + refusal text.
   - Unsupported requested symbols (e.g. `PndUniversalRestgasDeconvolver`) -> refusal basis claim + refusal text.
   - Deleted runtime artifact records -> refusal basis claim + refusal text.
4. **Honest Outcome Determination:**
   - If no refusal applies, and previously supported claims survive: `_finalize` emits `QAStatus.ANSWERED` with those claims, and `answer_point_audit` accurately records the unrecovered missing points.
   - If no supported claims survive: `_finalize` emits `QAStatus.INSUFFICIENT_EVIDENCE`.
   - Never invent claims, requirements, or evidence.

---

## 15. Compatibility and Boundary Governance (Decision D12)

- **Legacy Requirements Parallelism:** Existing `_answer_requirements`, `missing_requirement_ids`, and deterministic checks run in parallel. They are not modified.
- **Non-Interference:** `missing_requirement_ids` alone does not trigger E3 retrieval.
- **Public API:** `QAResult`, `ClaimCitation`, and `QAStatus` schemas remain strictly unmodified.
- **Historical Invariance:** C8 and E2 historical evaluation verdicts and manifests remain frozen and unmodified.

---

## 16. Minimal E3-A1 Implementation Seam (Decision D9)

> [!IMPORTANT]
> **Authoritative Current Retriever Limitation:**
> The current `Retriever.retrieve()` returns `{"plan": ..., "evidence": [...]}` where `evidence` is already policy-selected. It does **not** return a full non-selected exact/paper/workflow/graph candidate payload registry.
> Therefore, on the explicit runtime path (`runtime_e1_v2`), the candidate capture seam must capture full bounded candidates and provenance across initial AND any pre-answer targeted passes.

### 16.1 Seam in `src/panda_agent/qa.py`
1. **Extend `QAState`:**
   ```python
   missing_point_retrieval_count: int
   retained_support_evidence: dict[str, dict[str, Any]]
   retained_supported_claims: list[dict[str, Any]]  # exact claim text + citation IDs + point mapping snapshot
   e3_trace: dict[str, Any]
   ```
2. **Frozen Plan Snapshot:**
   Snapshot `bundle["plan"]` before any pre-answer targeted refinement and before E3. Preserve all plan constraints (`source_budgets`, `required_source_types`, `version_conflicts`, `resolved_versions`, `target_repositories`, symbols, scopes). No reanalysis from generated prose.
3. **Update Graph Edges:**
   In `QAAgent.__init__`:
   ```python
   graph.add_node("missing_point_retrieve", self._timed_node("missing_point_retrieve", self._missing_point_retrieve))
   graph.add_conditional_edges(
       "verify",
       self._after_verify_route,
       {"missing_point_retrieve": "missing_point_retrieve", "revise": "revise", "finalize": "finalize"},
   )
   graph.add_edge("missing_point_retrieve", "revise")
   ```
4. **Route Logic (`_after_verify_route`):**
   ```python
   def _after_verify_route(self, state: QAState) -> str:
       if self._is_e3_trigger_eligible(state):
           return "missing_point_retrieve"
       if state.get("errors") and state.get("revision_count", 0) < 1:
           return "revise"
       return "finalize"
   ```
5. **Node Implementation (`_missing_point_retrieve`):**
   - Consume attempt: set `state["missing_point_retrieval_count"] = 1` immediately before external calls.
   - Capture immutable `retained_support_evidence` ledger (bound = prior cited selected evidence count).
   - Capture immutable `retained_supported_claims` snapshot (exact claim text + citation IDs + point mappings).
   - Builds question-derived objective from `state["question"]` + missing point texts in question order.
   - Union all pre-E3 passes (initial + any pre-answer targeted passes) plus one E3 targeted pass.
   - Call internal candidate capture; execute single global best-rank RRF, single global LLM rerank, and policy selection (`select_final_evidence`).
   - Atomic update: upon complete success, update `bundle["evidence"]`. On failure, retain prior usable bundle and support.
6. **Support Context Resolution in `_revise`, `_verify`, and `_finalize`:**
   - In `_revise`: provider review context includes exact cited support evidence as well as newly selected evidence. `_revise` merges claims into `draft["claims"]` and clears `supported_claims: []`.
   - In second `_verify`: match unchanged claims against `retained_supported_claims` snapshot. Unchanged claims may cite evidence from `retained_support_evidence` or newly selected evidence. New/revised claims may cite newly selected evidence only. Reverification runs normally without waivers.
   - In `_finalize`: emit cited evidence union (<= prior cited count + configured `final_evidence_limit`). Check refusal precedence before partial answer salvage.

### 16.2 Seam in `src/panda_agent/retrieval.py`
1. **Candidate Capture Seam:**
   - In `retrieve()`: when on explicit `runtime_e1_v2` path, capture bounded raw channel candidates and payloads across initial and pre-answer targeted passes in an internal structure.
2. **Cross-Pass Fusion Seam:**
   - Dedicated helper `consolidate_and_select_candidates()` reusing existing internal collection and selection logic.
   - Strictly **no imports or calls** to shadow-only `global_candidate_pool.py` or frozen `c8_global_treatment.py`.
   - No monkeypatching evaluator harness in runtime.
   - E3 targeted collection must **NOT** perform its own rerank before the single global rerank.
   - Dedup same object once with best rank per channel across all passes; verify consistent payload/version or abort update; no fuzzy dedup.

---

## 17. Focused A1 Test Contract (T1–T20)

> [!IMPORTANT]
> **Local Test Identification Notice:**
> T1–T20 are local deterministic test IDs (unit/mock/static test specifications), **NOT** evaluation tiers (such as T0–T5). None of T1–T20 were executed in A0 (A0 is architecture and contract only).

| Test ID | Objective | Expected Verification Outcome |
| :--- | :--- | :--- |
| **T1** | Legacy mode non-invocation | In `legacy_question_core`, missing answer points or errors never trigger `missing_point_retrieve`. |
| **T2** | Shadow mode non-invocation | In `shadow_e1_v2`, missing answer points do not trigger `missing_point_retrieve`. |
| **T3** | Complete coverage non-invocation | In `runtime_e1_v2`, when all points are covered (`missing_answer_point_ids == []`), E3 retrieval is skipped. |
| **T4** | Genuine missing-point invocation | In `runtime_e1_v2`, non-empty missing points trigger exactly one `missing_point_retrieve`. |
| **T5** | Exact objective text | The retrieval objective contains the exact string of the missing answer point text in question order. |
| **T6** | Clean objective isolation | The retrieval objective contains no Gold prose, `missing_requirement_ids`, review reasons, or draft claims. |
| **T7** | Non-evaluable suppression | Unhandled coverage review errors, unknown point IDs, or unevaluable/notrun states do not trigger E3 retrieval. |
| **T8** | Plan constraint preservation | E3 targeted retrieval strictly retains frozen original plan versions, repositories, source budgets, and symbols; no prose reanalysis. |
| **T9** | Multi-point composition | Multiple missing points are merged into a single bounded query in original question order. |
| **T10** | Global candidate reconsideration | Candidates from all pre-E3 passes and one E3 pass are pooled by `object_id` and fused via best-rank RRF; single global rerank. |
| **T11** | Strong initial evidence survival | High-scoring initial candidates survive targeted retrieval and remain in final selection. |
| **T12** | Useful targeted evidence admission | Relevant targeted candidates enter the policy-selected final evidence set. |
| **T13** | Duplicate candidate deduplication | Same `object_id` retrieved across passes contributes once per channel (best rank); consistent payload or abort; no fuzzy dedup. |
| **T14** | Supported claim preservation & negative new-claim check | Round-1 supported claim citing displaced evidence survives via retained snapshot and ledger; new or revised claim attempting to cite displaced evidence from the ledger is rejected as invalid evidence during the second verify pass. |
| **T15** | Bounded revision budget | `revision_count` never exceeds 1 across the recovery path. |
| **T16** | Bounded E3 retrieval budget | `missing_point_retrieval_count` never exceeds 1 across the execution trace (consumed before calls). |
| **T17** | Second verify termination | A second verification run (`revision_count == 1`) cannot trigger a second E3 retrieval. |
| **T18** | Honest failure & atomic retention | When targeted retrieval fails, yields no candidates or no gain, bundle update is aborted, prior usable bundle and support are retained, attempt is consumed, and execution terminates honestly without retry (refusal precedence or partial `ANSWERED`/`INSUFFICIENT_EVIDENCE`). |
| **T19** | Public DTO invariance | `result` conforms strictly to existing `QAResult` schema (no schema widening). |
| **T20** | Default configuration invariance | `DEFAULT_ANSWER_POINT_MODE` remains `legacy_question_core`. |

---

## 17.1 Future Science (NOT FROZEN)

Future authorized empirical evaluation of missing-point targeted retrieval will measure performance along seven primary dimensions:

1. **Applicability:** Frequency with which genuine missing answer points trigger E3 across diverse natural query distributions.
2. **Recovery:** Proportion of genuine missing answer points successfully grounded by targeted retrieval and covered by revised claims.
3. **Admission:** Rate at which relevant targeted candidates are admitted into the policy-selected final evidence set.
4. **Displacement:** Frequency and impact of initial evidence items displaced by newly admitted candidates.
5. **Final Coverage:** Net answer-point completeness of final verified answers compared to baseline QA.
6. **Unsupported Delta:** Change in unsupported claims relative to baseline; no numerical acceptance threshold is frozen here.
7. **Additional Retrieval / Model Cost:** Token usage, latency overhead, and external query counts incurred by the targeted pass and global rerank.

> [!CAUTION]
> **Non-Authorization Boundary:**
> Controlled and fresh development testing is possible in future authorized stages, but **NO evaluation cohort, benchmark dataset, numerical threshold, or execution authorization is active or frozen in E3-A0**.
> T1–T20 are local test specifications only. None were executed in A0.

---

## 18. Static Acceptance Mapping (A0-1 to A0-11)

| Requirement | Description | Status in Contract | Evidence Reference |
| :--- | :--- | :--- | :--- |
| **A0-1** | Current QA graph reconstructed from source | **PASS** | Section 1 (`src/panda_agent/qa.py`) |
| **A0-2** | Pre-answer targeted retrieval distinguished from E3 | **PASS** | Section 2 |
| **A0-3** | C8 historical status preserved accurately | **PASS** | Section 4.1 |
| **A0-4** | C8 dependency resolved without false validation | **PASS** | Section 4.2, Decision D1 |
| **A0-5** | Question-derived trigger/objective contract established | **PASS** | Sections 5, 7, Decisions D2, D3 |
| **A0-6** | One-attempt bounded recovery semantics established | **PASS** | Sections 9, 10, Decisions D4, D5, D6, D7 |
| **A0-7** | Global candidate reconsideration contract established | **PASS** | Sections 11, 12, Decision D8 |
| **A0-8** | Version/compatibility/default/public boundaries preserved | **PASS** | Sections 6, 8, 15, Decisions D10, D12, D13 |
| **A0-9** | Concrete minimal A1 seam identified | **PASS** | Section 16, Decision D9 |
| **A0-10** | Focused A1 test contract defined (T1–T20) | **PASS** | Section 17 |
| **A0-11** | No product implementation or scientific calls | **PASS** | Zero product code, zero scientific calls |

---

## 19. Required Decisions Summary (D1–D13)

- **D1: C8 Blocker Status:** No. C8 treatment status is deferred due to natural applicability shortfall. E3 uses an independent question-derived semantic trigger. Design principles are reused; C8 validation is not claimed.
- **D2: Genuine E3 Trigger:** Explicit `runtime_e1_v2`, structurally valid review, `coverage_evaluable == True` (not `unknown`/`notrun`), non-empty known `missing_answer_point_ids`, no version conflicts, `missing_point_retrieval_count == 0`, `revision_count == 0`.
- **D3: Retrieval Objective Inputs:** Original user question + exact missing answer-point texts in question order only. All Gold, error, reason, and draft text strictly forbidden.
- **D4: Dedicated E3 Budget:** Yes. `missing_point_retrieval_count <= 1`, incremented/consumed before external calls.
- **D5: Interaction with Pre-Answer Targeted Retrieval:** Independent counters and phases. Pre-answer operates under configured `retrieval_count < policies.max_targeted_retrievals` (default 1). Only E3 missing-point retrieval and revision are hard-bounded to `<= 1`. Total workflow loop is strictly bounded.
- **D6: E3 Execution Timing:** Before revision (`verify -> missing_point_retrieve -> revise`).
- **D7: Full Answer Regeneration:** No. E3 routes to `_revise`, preserving already verified `supported_claims`.
- **D8: Global Candidate Reconsideration:** Candidate pooling by `object_id` across all pre-E3 passes and one E3 pass, best-rank per channel RRF fusion, top-30 LLM rerank, and standard evidence selection. Retained-support evidence ledger and retained-supported-claims snapshot resolve citation displacement.
- **D9: Source Seam for A1:** Dedicated `_missing_point_retrieve` node in `qa.py` and lean cross-pass consolidation helper in `retrieval.py`.
- **D10: Authorized Execution Modes:** `runtime_e1_v2` only. `legacy_question_core` and `shadow_e1_v2` never execute E3. No new `runtime_e3` mode.
- **D11: Failure Behavior & Refusal Precedence:** Atomic bundle update upon success only; failed/empty/no-gain retains prior bundle and support intact; attempt consumed before calls, no retry. Existing refusal precedence strictly preserved (partial `ANSWERED` is not unconditional).
- **D12: Unchanged Invariants:** Default mode (`legacy_question_core`), public DTOs (`QAResult`), parallel legacy requirements, frozen C8/E2 historical statuses, selection limit (12), channel weights.
- **D13: Frozen Plan Constraints:** Original plan snapshot frozen before any pre-answer targeted pass and before E3. Preserve all plan constraints (`source_budgets`, `required_source_types`, `version_conflicts`, `resolved_versions`, `target_repositories`, symbols, scopes); no prose reanalysis.

---

## 20. Accounting and Scientific Boundary

- **Contract Status:** `COMPLETE / PASS`
- **PANDA Scientific / Model Calls:** 0
- **PANDA Scientific / Model Tokens:** 0
- **Product Code Modifications:** 0
- **Test Code Modifications:** 0
- **Evaluation Policy Modifications:** 0
- **Historical Manifest Modifications:** 0
