# F3 — Fixed Locator / Fallback Cleanup Closeout

Lifecycle identity: Phase F → F3 — Incremental Shortcut Removal → PF-LR1 bounded
fixed-locator/fallback package (`F3_FIXED_LOCATOR_PACKAGE` = R03 + R05 + R06).

Decision: **COMPLETE / PASS / FIXED_LOCATOR_FALLBACK_SHORTCUTS_RETIRED.**

All PANDA scientific/evaluation calls and tokens are zero. Zero protected-data
access. Deterministic localized production cleanup only; unit tests with fake
evidence/analyzer/storage were the only executed verification.

## 1. Starting state

- Starting HEAD: `a7109e3039a3829ef8fa1c611cf4f1b24c1072ea`
  ("Repair F2-A5 source obligation matching") — matched the expected baseline
  exactly; verified, not assumed.
- Worktree: clean before editing.
- Baseline: F2-A5-R1 / F2-A5 / F2 COMPLETE/PASS; F3 NOT_STARTED;
  Phase F = IN_PROGRESS / F2_COMPLETE_F3_NOT_STARTED; normal default
  `legacy_question_core`; runtime_e1_v2 explicit-selection-only; promotion DEFERRED.
- Unrelated user work: none present; nothing was reset, checked out, amended,
  squashed, or force-moved.

## 2. Residual reproduction at starting HEAD

- **R03** — `src/panda_agent/retrieval.py:1199-1202` (`Retriever.analyze`):
  `if intent == "algorithm_theory" and any(term in lowered for term in
  ("feed back", "feedback", "reconstructed restgas profile")) and "li_2026" in
  paper_page_hints: paper_page_hints["li_2026"] = [141, 149, 151]`. A question
  phrase + intent combination directly overrode an already-contributed page-hint
  set with the exact thesis pages. Code origin is independent of D4 even though
  the same page set appears in the reviewed rule
  `reconstructed_profile_to_acceptance`.
- **R05** — `src/panda_agent/qa.py:2578-2591` (`QAAgent._finalize`
  unsupported-API branch): the inline evidence selector's third condition
  `str((item.get("locator") or {}).get("path") or "").endswith("PndPidCorrelator.h")`
  cited the historical header even when the requested API belonged to a
  different class; the optional claim additionally assumed the evidence is a
  header ("cannot be verified from the available header").
- **R06** — `src/panda_agent/qa.py:2614-2640` (`QAAgent._finalize`
  deleted-runtime branch): after the (correct, generic) guard error
  "runtime artifact records cannot be reconstructed from source code alone",
  the finalizer hard-coded a lookup for `macro/target/ana_dpm.C`, cited it with
  the fixed claim "The source defines the event_poca schema and production
  logic, ...", and the base refusal unconditionally said "the source can only
  verify the event_poca schema and production logic" — so a deleted-runtime
  request for any other artifact was answered with event_poca presentation.

## 3. D4 ownership boundary

`configs/query_expansions.yaml` is D4-owned and was READ-ONLY in F3. The page
set `[141, 149, 151]` legitimately remains in the reviewed rule
`reconstructed_profile_to_acceptance` (triggers: "reconstructed rho",
"reconstructed rho(z)", "acceptance calculation", "effective acceptance",
"restgas density"); the bare substring "ana_dpm" legitimately remains in
`qa.py` line ~520 (unrelated requirement vocabulary, no locator authority) and
in the YAML. Shared literal values do not transfer ownership and were not
globally removed. R20 remains D4_OWNED_EXCLUDED; D4 remains
PAUSED / ROADMAP_RECONCILIATION with overall completion UNDECIDED; D4 was not
reopened and no D4-A11 was created. F3 cleanup is code-origin specific.

## 4. Before/after matrix

| Residual | Before | After |
| -------- | ------ | ----- |
| R03 | phrase+intent → exact thesis pages `[141,149,151]` forced over contributed hints | reviewed expansion / ordinary retrieval only; no Python page injection |
| R05 | requested owner OR fixed `PndPidCorrelator.h` header fallback | requested/query-grounded API basis only (owner-in-path / owner==symbol) |
| R06 | generic guard → fixed `ana_dpm.C` citation + unconditional `event_poca` wording | generic guard → query-grounded optional basis (`deleted_runtime` kind) / artifact-neutral wording |

## 5. R03 repair (retrieval.py)

Deleted the four-line feedback page override in `Retriever.analyze` (former
lines 1199-1202). Nothing else changed in the file: `lowered` remains in use by
the version/doc check, the `algorithm_implementation` page-hint cap
(remaining=3) and the non-theory/non-implementation clearing block are intact,
and `select_final_evidence` / `_preparse` / expansion consumption are
byte-identical. Resulting page-hint authority: ordinary reviewed
query-expansion semantics only. If no reviewed expansion matches the live
question, no page set is injected — that is the accepted behavior (Case A).
When a reviewed expansion does match, its pages (including
`li_2026: [141, 149, 151]` from `reconstructed_profile_to_acceptance`) appear
with reviewed-expansion provenance via `matched_expansion_rules` (Case B). No
Python phrase→page branch, hidden fixed-page helper, new YAML rule, or D4
modification replaced the retired branch.

## 6. R05 repair (qa.py)

In the unsupported-API finalizer branch, removed only the third selector
condition (`endswith("PndPidCorrelator.h")`); the first two generic conditions
(requested owner appears in the locator path; requested owner equals the
locator symbol) are preserved byte-identically. The optional claim now uses
generic evidence-backed wording: "The cited locked code at <location> documents
<owner>, but does not establish the exact requested API signature <requested>."
where owner is derived from the structured error (`requested.rsplit("::", 1)[0]
.split("::", 1)[-1]`) and location from `_refusal_basis_location`. No header
relationship is invented; header-specific wording is gone. If no
owner-relevant selected evidence exists, the refusal remains valid with
`claims = []` and `evidence = []` — unrelated evidence is never cited to enrich
the refusal. The base answer ("The locked corpus does not declare the exact API
signature <requested>; the request is therefore insufficiently evidenced.") is
unchanged, and the generic unsupported-API guard itself is untouched.

## 7. R06 repair (qa.py)

The generic impossibility guard `_answerability_guard` (deleted/removed +
recover/reconstruct/restore + runtime/source-code artifact requests) is
preserved byte-identically. The finalizer's fixed `macro/target/ana_dpm.C`
lookup was removed and replaced by `_refusal_basis_evidence(state,
kind="deleted_runtime")` — a bounded new kind in the existing generic
refusal-basis selector that operates only over the already-selected evidence
bundle (no retrieval, no storage, no model calls), admits only
code/workflow evidence whose search text overlaps an identifier-like artifact
anchor from the live question (`{token for token in question_anchors if "_" in
token}`, e.g. `event_poca`, `sensor_hits`), ranks purely by question-anchor
overlap, has no fixed path preference, and returns `None` when nothing is
relevant. When a basis exists, the narrow claim reads "The cited locked code at
<location> documents <subject>, but source code does not contain deleted
runtime records." with `<subject>` from `_refusal_basis_subject` (the longest
question anchor present in the evidence). The base refusal is now
artifact-neutral: "Deleted runtime records cannot be reconstructed from source
code alone." `event_poca` appears only when the question itself concerns
`event_poca` (or the evidence plus question-grounded subject establishes that
context); every deleted-runtime request is no longer inferred to be an
event_poca request. Existing kinds (`future_runtime`, `universal_proof`,
`unsupported_symbol`) keep their exact admission/ranking semantics; the
unknown-kind `ValueError` is unchanged; plan-only symbols cannot make
unrelated evidence relevant (question-only anchors, like `unsupported_symbol`).

## 8. Proof: no replacement fixed locator introduced

- R03: the deleted branch is gone; `grep`/static test
  `test_no_python_branch_maps_feedback_terms_to_fixed_pages` asserts
  `"141, 149, 151"` does not occur in `retrieval.py` source. No new phrase→page
  mapping, fixed page set, YAML rule, or special-case trigger was added
  (diff-audited: the only `retrieval.py` change is the 4-line deletion).
- R05: static test `test_no_fixed_header_authority_in_source` asserts
  `"PndPidCorrelator.h"` does not occur in `qa.py` source; no other exact
  header, fixed path, or new locator framework was introduced (diff-audited).
- R06: static test `test_no_fixed_macro_authority_in_source` asserts
  `"macro/target/ana_dpm.C"` does not occur in `qa.py` source; the
  `deleted_runtime` kind contains no path literal, no `event_poca` preference,
  and no historical-path ranking (diff-audited).
- No new configuration, no model calls, no new retrieval were added.

## 9. D4 YAML zero-diff confirmation

`git diff -- configs/query_expansions.yaml` is empty;
`git status --porcelain configs/` outputs nothing; sentinel test
`test_d4_owned_yaml_rule_unchanged` asserts the
`reconstructed_profile_to_acceptance` rule still carries
`paper_page_hints == {"li_2026": [141, 149, 151]}`. `configs/retrieval_policies.yaml`
untouched.

## 10. R14 zero-diff confirmation

`select_final_evidence` and all shared selector semantics have zero diff (the
production diff contains no occurrence of `select_final_evidence`; the only
`retrieval.py` change is the R03 deletion). R14 remains
PHASE_F_SHARED_BOUNDARY_REVIEW / NO_CHANGE_CURRENTLY_JUSTIFIED.

## 11. F2 preservation

All accepted F2 outcomes preserved: F2-A1/A1-R1 (generic verifier semantics),
F2-A2 (pointer normalization), F2-A3/A3-R1 (coverage-mode authority),
F2-A4/A4-R1 (generic premise/refusal handling, `_refusal_basis_evidence`
kinds, structured unsupported-symbol errors, no speculative replacement
claims), F2-A5/A5-R1 (question-grounded source obligations). The pre-existing
F2-A4 finalizer tests `test_nonexistent_api_guard_keeps_verified_alternative`
and `test_runtime_artifact_guard_keeps_schema_without_filler` pass UNMODIFIED
through the generic mechanisms (owner-in-path match; `event_poca` identifier
anchor overlap respectively). F3 did not reopen F2.

## 12. E3 boundary

No E3 surface was modified: `_check_e3_trigger`, missing-point retrieval,
consolidation, reranking, the retained-support ledger, and the second verify
are untouched. R05/R06 are refusal/finalization changes and R03 is an analysis
page-hint change; neither justifies reopening E3. The historical 49-test E3
suite was not run (no shared-selection semantics were modified); no E3-adjacent
full-path test required execution because full-path service behavior was not
affected.

## 13. Adversarial contract results (T1–T24)

New test classes: `TestFixedFeedbackPageOverrideRetirement`
(tests/unit/test_retrieval.py) and `TestFixedRefusalLocatorRetirement`
(tests/unit/test_qa.py).

| Test | Contract | Result |
| ---- | -------- | ------ |
| T1 | feedback-worded theory question keeps reviewed `longitudinal_efficiency` pages `[138,142,147]` (no `[141,149,151]` override); override-trigger wording without a page-hint expansion injects nothing | PASS (`test_reviewed_expansion_pages_survive_feedback_wording`, `test_feedback_question_without_reviewed_expansion_gets_no_injected_pages`) |
| T2 | question matching `reconstructed_profile_to_acceptance` still receives `[141,149,151]` with reviewed-expansion provenance (`matched_expansion_rules`) | PASS (`test_reviewed_expansion_remains_page_hint_authority`) |
| T3 | YAML rule unchanged (shared literal not globally deleted) | PASS (`test_d4_owned_yaml_rule_unchanged`) |
| T4 | unrelated theory question receives no page-hint behavior | PASS (`test_unrelated_theory_question_gets_no_page_hints`) |
| T5 | implementation page-hint cap unchanged (merged hints capped at 3, first reviewed anchor set wins) | PASS (`test_implementation_hint_limiting_unchanged`) |
| T6 | owner-relevant evidence may be cited for unsupported API; claim states location/owner/signature, no header assumption | PASS (`test_unsupported_api_owner_relevant_evidence_may_be_cited`) |
| T7 | `ImaginaryController::missingMethod` + only `PndPidCorrelator.h` → no claim, no evidence citation (central sentinel) | PASS (`test_unseen_api_owner_gets_no_historical_header_citation`) |
| T8 | unseen owner + matching `SensorGhostBuilder` evidence → generic citation allowed | PASS (`test_unseen_api_with_matching_owner_evidence_may_be_cited`) |
| T9 | unsupported API + unrelated evidence → zero optional claims/citations | PASS (`test_unsupported_api_without_relevant_evidence_cites_nothing`) |
| T10 | locked-catalog supported API not refused; unsupported API still refused | PASS (`test_locked_catalog_api_guard_boundary_unchanged`) |
| T11 | deleted `event_poca` question + genuinely relevant `ana_dpm.C` evidence → generic citation (not via fixed path branch) | PASS (`test_deleted_runtime_relevant_producer_context_may_be_cited`) |
| T12 | unseen `sensor_hits.root` question + only unrelated `ana_dpm.C` → generic refusal, zero claims/citations, no `event_poca` in answer (central sentinel) | PASS (`test_unseen_deleted_runtime_artifact_gets_generic_refusal`) |
| T13 | unseen artifact + genuinely relevant producer evidence → generic evidence-backed context allowed | PASS (`test_unseen_artifact_with_relevant_producer_evidence_may_be_cited`) |
| T14 | no relevant evidence → exact bare generic refusal | PASS (`test_deleted_runtime_without_relevant_evidence_is_bare_refusal`) |
| T15 | deleted-runtime guard unchanged and artifact-neutral (event_poca and sensor_hits.root both detected) | PASS (`test_deleted_runtime_guard_genericity_unchanged`) |
| T16 | static: no active Python branch maps feedback terms to `[141,149,151]` | PASS (`test_no_python_branch_maps_feedback_terms_to_fixed_pages`) |
| T17 | static: no fixed-header authority in `qa.py` | PASS (`test_no_fixed_header_authority_in_source`) |
| T18 | static: no fixed-macro authority in `qa.py` | PASS (`test_no_fixed_macro_authority_in_source`) |
| T19 | generic deleted-runtime request emits no `event_poca` unless question/evidence relevance establishes it | PASS (asserted inside T12) |
| T20 | F2-A4 refusal kinds (future_runtime, universal_proof, unsupported_symbol) preserved | PASS (pre-existing test_qa.py suites, full-file run) |
| T21 | F2-A5 source-obligation tests preserved | PASS (pre-existing test_retrieval.py suites, full-file run) |
| T22 | `select_final_evidence` zero semantic modification | PASS (diff audit) |
| T23 | `configs/query_expansions.yaml` zero diff | PASS (git diff + T3 sentinel) |
| T24 | zero PANDA scientific/evaluation work | PASS (by construction; unit tests with fakes only) |

## 14–15. Scientific / evaluation cost

PANDA scientific/evaluation calls: **0**. PANDA scientific/evaluation tokens:
**0**. No T2/T3/T4/T5/release evaluation, LLM judge, protected holdout,
benchmark QA evaluation, or promotion evaluation was run.

## 16. Default / promotion state

Normal default remains `legacy_question_core`; `runtime_e1_v2` remains
VALIDATED_EXPERIMENTAL_PATH / EXPLICIT_SELECTION_ONLY; default promotion
remains DEFERRED. PF-LR1 classifies R03/R05/R06 as LOCAL_NON_MATERIAL, so F3
completion alone creates no promotion-relevant material candidate; PE-LR1 was
not reopened and no promotion evaluation was run.

## 17. Per-residual final disposition

| Residual | Starting status | Final status | Production surface | Replacement |
| -------- | --------------- | ------------ | ------------------ | ----------- |
| R03 | active fixed shortcut | RETIRED | retrieval analyze | reviewed generic retrieval (ordinary reviewed expansion semantics) |
| R05 | active fixed fallback | RETIRED | API finalizer | query/requested-owner basis (generic owner matching + evidence-backed wording) |
| R06 | active fixed fallback | RETIRED | deleted-runtime finalizer | generic query-grounded basis (`deleted_runtime` kind) + artifact-neutral wording |

## 18. F3 aggregate decision

COMPLETE / PASS / FIXED_LOCATOR_FALLBACK_SHORTCUTS_RETIRED — all three
residuals retired, no replacement fixed locator introduced, D4 YAML untouched,
R14 untouched, generic guards preserved, adversarial contract T1–T24 and
focused suites pass.

## 19. Phase-F state

Phase F = IN_PROGRESS / F3_COMPLETE_F4_NOT_STARTED. F2 = COMPLETE / PASS /
A1_A2_A3_A4_A5_COMPLETE. F4/F5/F6 remain; Phase F is not marked complete.

## 20. Next recommendation

F4 — Separate Answer-Generation and Semantic-Verification Roles.
Recommendation only; not started.

## 21. Execution authorization

NEXT_TASK_EXECUTION_AUTHORIZED = false

## Verification record

- `PYTHONPATH=src python -m pytest tests/unit/test_retrieval.py -q` → 59 passed,
  27 subtests passed (includes all pre-existing F2-A5 tests).
- `PYTHONPATH=src python -m pytest tests/unit/test_qa.py -q` → 111 passed,
  19 subtests passed (includes all pre-existing F2-A4/F2-A5 tests).
- Integrated focused run
  `PYTHONPATH=src python -m pytest tests/unit/test_retrieval.py tests/unit/test_qa.py -q`
  → 170 passed, 46 subtests passed.
- Static: `git diff --check` clean; `git status --short` shows exactly the four
  authorized files; `git diff -- configs/query_expansions.yaml` empty;
  `select_final_evidence` zero-diff.
- No SHA256/hash bookkeeping was generated.

## Scope limitation

Only the PF-LR1 F3 package (R03/R05/R06) is retired by this task. This is NOT a
claim that "all benchmark shortcuts are removed": R01/R02/R04/R14/R15/R07/R20
and the D4-owned YAML locator pattern are outside F3 and keep their recorded
dispositions.
