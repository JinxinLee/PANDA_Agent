# E2-A3-R2: Citation-Eligible Evidence Selection Repair

## Current scientific outcome

**E2-A3-R2 = COMPLETE / PASS /
CITATION_ELIGIBLE_EVIDENCE_SELECTION_REPAIR_VALIDATED.**

All S1-S13 and P1-P11 pass. Twelve fresh QA executions and six authoritative
blinded judgments completed without scientific infrastructure failures. No
ineligible Sphinx citation occurred in any initial/revision model response;
no review reported incomplete web citation. Runtime activation did not occur.

| Provenance boundary | Commit |
| --- | --- |
| Starting HEAD | `ee719bde5331f4102c9d79dd929e31a8063fc9ae` |
| Candidate and preregistration | `85ec7e353a65c31f0f1b491d5e00bad59b044c58` |
| All raw outputs, before judging | `12ae8138bd8268e9246d4d477a1d9f07cafc854f` |
| All judgments, before scoring | `5992cd1e7b354583cd395fd7e7552f509ce03b75` |
| Scientific closeout | Commit introducing `e2_a3_r2_targeted_revalidation_result.json`, titled `E2-A3-R2 close citation-eligible evidence validation` |

The closeout commit identifies itself through Git history rather than a
self-referential SHA. The final user delivery records its full SHA. No frozen
product, test, manifest, protocol, runner or historical science file changed
after candidate freeze. Raw/judged records were frozen before outcome inspection.

## Prospective findings

| Case | Legacy / runtime status | Runtime decomposition / evaluable / complete | Revisions legacy / runtime | Runtime minus legacy generation calls | Blinded preference |
| --- | --- | --- | --- | --- | --- |
| g013 | answered / answered | valid / true / true | 0 / 1 | 3 | runtime better |
| g027 | answered / answered | valid / true / true | 0 / 0 | 1 | equivalent |
| g112 | answered / answered | valid / true / true | 0 / 0 | 1 | equivalent |
| g002 | answered / answered | valid / true / true | 1 / 1 | 1 | equivalent |
| g044 | answered / answered | valid / true / true | 0 / 0 | 1 | equivalent |
| g110 | answered / answered | valid / true / true | 0 / 0 | 1 | equivalent |

Both arms achieved expected status 6/6 and supported judgments 6/6. Runtime
better/equivalent/worse = **1/5/0**; critical runtime regressions = **0**.
Noncritical worse is not an R2 gate. Historical P6 FAIL preserved: yes.
P6 waiver granted: no. P6 product repair introduced: no.

All 12 executions retained 12 selected evidence items in diagnostics. Fresh
selected Sphinx occurrences total 38: 26 complete and 12 ineligible. The initial
answer projections retained all 26 complete occurrences and excluded all 12
ineligible occurrences. Three revisions used the same rule, producing 15
total captured admission payloads. Non-Sphinx items and their order were retained.
These fresh occurrence counts are separate from the historical 144/106/38 scan.

g013 selected eight Sphinx items per arm, of which seven were complete and one
ineligible; the latter was excluded. Runtime initially missed point.3 and used
its one revision to reach complete coverage; no structural or citation failure.
g027 selected three ineligible Sphinx items in each arm and retained those items
in diagnostics; neither arm received them as citable evidence. Existing code
evidence supported the answer without extra retrieval or synthesized sections.
g112 had no unsupported-identifier errors, including the historical colon class.

g002 retained four complete Sphinx sections per arm and excluded one incomplete
page per arm. Web citation integrity remained clean and runtime final coverage
was complete. Both arms initially received `unsupported identifier
SIMPATH/bin/cmake`, both revised once, and both final reviews were clean. This
shared existing category is not a new runtime category. The judge rated the
pair equivalent and both outputs supported. No Spack/CVMFS or other prompt tuning
was performed. Final verification errors were empty in all 12 outputs.

| Gate | Result | Evidence |
| --- | --- | --- |
| P1 | PASS | 6 legacy, 6 runtime, 6 scoreable pairs, 6 authoritative judgments |
| P2 | PASS | 0 invalid public citation edges; all 15 admission captures match the projection |
| P3 | PASS | 0 incomplete-web errors over every review |
| P4 | PASS | g013/g027 correct in both arms; runtime valid/evaluable/complete; no structural/incomplete-citation category |
| P5 | PASS | g112 historical colon errors 0; valid/evaluable/complete |
| P6 | PASS | Correct 6/6 each; new false answers 0, new false refusals 0 |
| P7 | PASS | New runtime critical verifier categories 0 |
| P8 | PASS | Decomposition legacy 0/runtime 6; runtime revision >1 cases 0; post-verify retrieval 0 |
| P9 | PASS | Additional generation calls 8/6 = 1.333333, below 2.0 |
| P10 | PASS | Critical runtime regressions 0; runtime supported 6/6 |
| P11 | PASS | Frozen public/compatibility/default/retrieval boundaries unchanged |

Zero-tolerance violations: 0. Protected/holdout access, exposed-case/page logic,
fabricated locators, verifier relaxation, prompt/schema/Gold changes, post-freeze
product edits, selective reruns, E3 calls, DTO changes, compatibility removal and
runtime activation were not performed. Fresh retrieval naturally varied across
arms; unchanged retrieval means implementation and original bundle preservation,
not an assertion of identical stochastic fresh rankings.

## Scientific usage and cost

| Arm | Logical operations | Returned model responses | Adapter attempts | Observable tokens |
| --- | ---: | ---: | ---: | ---: |
| Legacy QA | 38 | 32 | 32 | 520,395 |
| Runtime QA | 46 | 40 | 40 | 570,002 |
| Blinded judge | 6 | 6 | 6 | 180,548 |
| Total | **90** | **78** | **78** | **1,270,945** |

Logical operations include 12 retrieval operations. Returned responses and
adapter attempts include 12 embeddings: 66 generation responses plus 12 embedding
responses. Embedding token usage is **unavailable**, not zero; the observable
token total is the returned generation token counter. No monetary cost is
available. Per-stage counts and tokens are in the canonical result JSON.
Generation-only overhead uses 34 runtime versus 26 legacy adapter attempts,
excluding embedding and retrieval. Scientific calls before candidate freeze: 0.

A repeated Qdrant client 1.19.0/server 1.15.5 compatibility warning was observed;
all scientific operations nevertheless completed. No dependency/configuration
change was made. The separate AGY review infrastructure failure is documented
in the frozen candidate record below and is not a scientific provider failure.

## Closeout and remaining boundary

Historical E2-A3 = COMPLETE / FAIL / Q7, E2-A3-R1 = COMPLETE / FAIL / P2_P6,
the colon repair, and the no-P6-product-repair decision remain authoritative.

```text
E2-A3-R2 = COMPLETE / PASS / CITATION_ELIGIBLE_EVIDENCE_SELECTION_REPAIR_VALIDATED
E2 = IN_PROGRESS / RUNTIME_ACTIVATION_FAILED / FINAL_ACTIVATION_REASSESSMENT_PENDING
normal default = legacy_question_core
Phase E = IN_PROGRESS / E2
E3 = NOT_STARTED
NEXT_TASK_RECOMMENDATION = E2-A3-R3 — Bounded Runtime Activation Reassessment
NEXT_TASK_EXECUTION_AUTHORIZED = false
```

PASS is limited to this admission repair and six exposed paired cases. It does
not establish broad generalization, erase historical failures or activate
runtime. R3 must independently justify and preregister its cohort and gates;
the earlier possible 14-case design is not frozen here. No subsequent task ran.

Changed files: `src/panda_agent/qa.py`;
`tests/unit/test_e2_a3_r2_citation_eligibility.py`;
`evaluation/run_e2_a3_r2_citation_eligibility_validation.py`;
`evaluation/e2_a3_r2_citation_eligibility_static_result.json`;
`evaluation/e2_a3_r2_citation_eligibility_manifest.json`;
`evaluation/E2_A3_R2_CITATION_ELIGIBLE_EVIDENCE_PREREGISTRATION.md`;
this report; `evaluation/e2_a3_r2_targeted_paired_raw.json`;
`evaluation/e2_a3_r2_targeted_paired_judged.json`;
`evaluation/e2_a3_r2_targeted_revalidation_result.json`;
`docs/EVALUATION_STATUS.md`; `docs/GENERALIZATION_ROADMAP.md`.

## Frozen candidate report (historical, before scientific execution)

Starting HEAD: `ee719bde5331f4102c9d79dd929e31a8063fc9ae`.
Status: candidate preparation; no prospective verdict yet.
Scientific calls before candidate freeze: **0** in every scientific stage.

The only production change is `src/panda_agent/qa.py`: one private Sphinx
citation-eligibility predicate and projections into initial answer evidence,
revision evidence and the existing revision requirement-evidence helper input.
Sphinx eligibility requires URL, snapshot date and nonempty section path.
All non-Sphinx admission semantics are unchanged. Original selected evidence,
ranking, retrieval diagnostics, page objects and verifier checks remain intact.
No backfill or substitute metadata is introduced when evidence is insufficient.
Rejected draft/error references remain diagnostic; the verifier still rejects
an invalid page if a model nevertheless cites it.

Full-module AST reconciliation reverses only the approved admission changes
and recovers the starting module exactly, preserving prompts/schema, verifier,
normalizer, E1/E2 mapping/coverage, compatibility helpers and public API/DTO.
Other production/configuration/corpus files have no changes. The default stays
`legacy_question_core`; runtime activation is not authorized in this task.

## Static reconciliation and T0

The scanner reads committed historical A3 (56) and R1 (10) executions. It
recomputes 144 selected Sphinx occurrences: 106 complete, 38 empty-section.
All 38 are excluded from the derived projection; all 106 complete items remain.
The 27 candidate citation edges contain 24 complete and three invalid edges;
all 18 final public edges are complete. The three invalid edges are A3 g013
legacy/runtime and R1 g027 runtime, with exact IDs in the static JSON.
Historical outputs are preserved, not retroactively repaired.

Actual-method fake probes confirm initial answer and revision receive the
eligible section plus code item, including the revision auxiliary map. The
original three-item bundle is unchanged. A malicious invalid-page claim still
receives the verifier's incomplete-web-citation error. S1-S13 all PASS.

Focused T0: 24 new admission/reconciliation/scorer tests; 89 QA, E2 coverage and
dual-mode regression tests; 13 normalizer/actual-verifier tests (10 historical
R1 tests intentionally deselected). Total: **126 passed**. Historical candidate
scope tests are not rewritten for a newer candidate. One initial command named
a nonexistent test file and ran no tests; the corrected explicit selection
passed. No full suite or live model call was used in T0.

AGY abstract static review was attempted via the required shared runner as job
`staffer-mtukcaxe-295e8ec9`. It crashed before worker start with Windows state-lock
rename EPERM and produced no stored result. Configured route was
gemini-3.8-flash-high; actual runtime model/effort and review completion were not
observed. No repository evidence was sent in the abstract prompt. Host review,
exact-scope checks and focused tests provide the recorded verification.

## Prospective protocol

See `E2_A3_R2_CITATION_ELIGIBLE_EVIDENCE_PREREGISTRATION.md` and
`e2_a3_r2_citation_eligibility_manifest.json`. Fixed cohort:
g013, g027, g112, g002, g044, g110; alternating arm order and blinded A/B labels.
Twelve fresh QA executions, then raw commit, six paired judgments, judgment
commit, deterministic scoring and closeout. P1-P11 and S1-S13 are fixed before
live execution. Noncritical worse is diagnostic only; unsupported runtime or
critical regression fails P10. Historical P6 is not waived.

## Limitations and lifecycle boundary

This exposed six-case repair experiment cannot establish broad generalization
or final activation quality. Same-model-family judgments are bounded support
evidence. Complete sections may not suffice for all requirements; existing
insufficiency behavior is retained. No additional retrieval is authorized.
Historical A3 FAIL/Q7 and R1 FAIL/P2_P6 remain unchanged. No g002 product tuning.
E2 remains in progress; E3, T3, T5 and runtime activation remain unauthorized.
The scientific result and lifecycle will be appended only after raw and
judgment commits, without changing the frozen candidate or protocol.
