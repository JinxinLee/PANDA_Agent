# E2-A3-R2: Citation-Eligible Evidence Selection Repair

## Candidate report (before scientific execution)

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
