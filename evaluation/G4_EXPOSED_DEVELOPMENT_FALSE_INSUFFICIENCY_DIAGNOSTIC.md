# G4 Exposed Development False-Insufficiency Diagnostic

## Decision and integrity sequence

**Primary decision: `GENERIC_FALSE_INSUFFICIENCY_MECHANISM_ESTABLISHED`, scoped
to exposed development evidence.** A repeatable `R2` channel-to-fusion loss
of obligation-bearing code evidence is supported by three independent
`curation_family_id` values. The six selected cases do not measure prevalence,
provide fresh confirmation, or authorize product repair. G3's admission
`NO_CHANGE` remains unchanged.

The [rubric](G4_EXPOSED_DEVELOPMENT_ANSWERABILITY_RUBRIC.md) was committed at
`476abd069cb54ded4779b8b4e6269bd314a4147c` before any of these six
case-level questions, Gold annotations, locked-source files, or production
traces were opened. The fixed IDs were `n001`, `n002`, `n006`, `n010`, `n017`,
and `n019`, all already known to have returned `insufficient_evidence`.
After the freeze, the independent [answerability record](G4_EXPOSED_DEVELOPMENT_ANSWERABILITY_REVIEW.json)
was written from question, reviewed Gold, and locked source evidence before
joining the production traces. Selection and reviewer exposure are explicit;
this is no claim of blinding. No matched answered controls were needed.

The [result record](G4_EXPOSED_DEVELOPMENT_FALSE_INSUFFICIENCY_RESULT.json)
contains per-case evidence IDs, compatible artifact references, competing
explanations, and counts. The G3 [completion result](G3_SCOPED_AUDIT_COMPLETION_RESULT.json)
and run manifest retain their original historical meaning.

## Independent answerability

The review compared the six English questions with `novel-v1-dev-0.3.0` Gold
and directly inspected the exact locked source commits declared by
`data/manifests/source_manifest.json`: RestgasDetermination
`11f1edc49dcbaeb61d707491a6d3bbec390fcd42`, LuminosityFit
`ddd83dcd1a74093bf48ef259a2849a67f9413f32`, and PandaRoot
`18c09e91100db27867ded30e708b4dae95bd8357`. Each source checkout HEAD
matched its manifest commit. File paths and line locators are recorded for
every independent obligation in the review JSON. Gold expected status alone
was not treated as proof.

| Case | State | Main independent locked-source basis | Material uncertainty |
|---|---|---|---|
| `n001` | `ANSWERABLE` | `configSettings.sh:2-11` identifies nominal pairs, placeholder paths, exports, and as-written shell syntax. | Gold p1/p2 asserts branch execution, but `bash -n` reports a syntax error at line 3. The accurate source-cited answer describes parse failure before input-dependent execution; the Gold discrepancy needs separate forward-only review. |
| `n002` | `ANSWERABLE` | `luminosityfit/requirements.txt:1-12` contains the complete declared package list. | None affecting answerability. |
| `n006` | `ANSWERABLE` | `PndFileNameCreator.h:1-49` and `.cxx:6-71,136-157,214-249` establish derivation and suffix literals. | None affecting answerability. |
| `n010` | `ANSWERABLE` | `PndFastSim.cxx:865-866,1022-1130,1367-1473`, `PndFsmAbsDet.h:49-89`, `PndFsmDetFactory.cxx:88-214`, and `PndFsmResponse.h:40-169` cover the response pipeline and its components. | None affecting answerability. |
| `n017` | `ANSWERABLE` | `PndTrack.h:23-57,110-122` defines the persistent class, fitted endpoints, candidate links and metadata. | None affecting answerability. |
| `n019` | `ANSWERABLE` | `PndRecoKalmanTask.h:43-59` and `.cxx:52-225` cover setup, hypothesis choice, fitting and persisted output. | None affecting answerability. |

The `n001` conflict concerns historical Gold correctness, not absence of a
source-supported answer to the user's question. The reviewed Gold file was
not changed. No second independent reviewer participated; the conflict is
explicitly retained for a later authorized Gold review. All six independent
answerability judgments are `ANSWERABLE`; `UNANSWERABLE=0`, `UNKNOWN=0`.

## Artifact qualification and production overlay

The six saved QA records and retrieval traces have matching case and G3 run
IDs, product repository identity, Gold hash, index identity, prompt version,
and `COMPLETE` QA stage capture. The G3 manifest declares non-formal `qa`,
`novel_dev`, the locked source-manifest identity, and prompt fingerprint
`5147f85c09a933609d91f4fa4e7bf3d8fbfa530684a3ecea4d3aaed72c3e04ce`;
the G3 completion result records product lineage
`a0106bd5eff93646f34f5e50e161e8be8a49d680`.
Captured telemetry is used only for pipeline diagnosis, not for answerability.

| Case | Production status / stages | Screening candidate | Earliest causal owner and confidence | Remaining limitation |
|---|---|---|---|---|
| `n001` | `insufficient_evidence`; pre-answer sufficiency guard stopped A0/admission/V1 | Yes | `Q1`, high: `FairSoft` was misread as an unavailable bare code class even though the exact script was selected. | Downstream stages are `NOT_APPLICABLE`; Gold conflict is separate. |
| `n002` | `insufficient_evidence`; V1 `VALID`, both points missing | Yes | `R2`, high: complete `requirements.txt` chunks appeared at dense ranks 7/8, then disappeared before the fused top 30. | No exact finalization receipt needed for upstream ownership. |
| `n006` | `insufficient_evidence`; V1 `VALID`, suffix point missing | Yes | `R2`, high: constructor suffix literals appeared at dense rank 9, then disappeared before fusion. | Selected documentation covered the helper relation, not the full literals. |
| `n010` | `insufficient_evidence`; V1 `VALID`, building-block point missing | Yes | `UNRESOLVED`: `Q1` versus `R1`. | Required pipeline/interface chunks were absent from channel candidates; the plan's `module_structure` interpretation may have contributed. |
| `n017` | `insufficient_evidence`; V1 `VALID`, all three points missing | Yes | `R2`, high: `PndTrack.h` chunks appeared at dense ranks 7/8, then disappeared before fusion. | Selected ambiguous backing and a citation error are downstream of losing the required header. |
| `n019` | `insufficient_evidence`; V1 `VALID`, transformation relation missing | Yes | `UNRESOLVED`: `Q2` versus `R2`. | Sparse implementation-body chunks were lost before fusion, but the plan also broadened explicit PandaRoot scope to three repositories; necessity of that earlier step is unproved. |

For the three attributed `R2` cases, the independent obligations, correct
target repository/version, and source-type constraints were present upstream.
The same-run ordered channel and fused lists show the first loss. Selected
evidence did not contain the missing required facts, so a valid V1 incomplete
disposition, no A1 target, and final insufficiency are expected downstream
effects. A selected-but-unadmitted item in `n006` or `n017` is not silently
promoted to an admission-policy defect. `n001` did not reach admission or
verification; absence of those events is not a V1 failure. No case supports
`FINALIZATION_CONSERVATISM` or a valid V1 semantic false rejection.

## Mechanism gate and opposing safety

`G4-R2-CHANNEL-EVIDENCE-LOSS` is an **established generic mechanism** on the
exposed development record: three different information needs and independent
families (`nf002`, `nf006`, `nf017`) each had necessary, source-compatible code
evidence recalled near the top of a channel and lost at the R2 fusion boundary.
The generic owning seam is candidate retention/ranking across channel-to-fused
evidence, with no case identifiers, symbols, paths, or expected answer phrases
needed as product logic. The n019 trace is consistent with this pattern but
does not count toward establishment because earlier scope broadening remains
unresolved. `G4-Q1-BARE-CLASS-PREMISE` is a separate one-case mechanism
candidate; it does not establish a generic Q1 repair mandate.

The six selected cases offer no unanswerable denominator or false-answer
prevalence estimate. The existing G4 18/18 T0 paired should-answer and
must-abstain baseline supplies the opposing safety contract; it was not rerun.
Any later R2 design must retain correct abstention, every required point and
relation, claim support, citation/admission provenance, and version safety,
and specify generic R2 controls before implementation. G3's 19 historical
ambiguous-backing decisions and `NO_CHANGE` verdict remain untouched;
`ADMISSION_REOPENING_CANDIDATES=0` here.

Counts for this **outcome-conditioned subset only**: `LANE_A_CASES=6`,
`FALSE_INSUFFICIENCY_CANDIDATES=6`,
`ATTRIBUTED_FALSE_INSUFFICIENCY=4`,
`CAUSALLY_UNRESOLVED_ANSWERABLE_INSUFFICIENT=2`,
`CORRECT_ABSTENTION=0`, `GENERIC_MECHANISM_CANDIDATES=2`, and
`ESTABLISHED_GENERIC_MECHANISMS=1`. Primary owner counts are `Q1=1`,
`R2=3`, `UNRESOLVED=2`; all other primary owner counts are zero. These
counts are **not** a `novel_dev` population rate or independent confirmation.

## Next action and accounting

**Single next recommendation:** `G4 R2 FUSION EVIDENCE-RETENTION REPAIR
DESIGN`, separately authorized. It should define a generic R2 control and a
minimal repair seam, including the opposing safety checks. A fresh reviewed
and outcome-blind Lane B cohort does not currently exist; additional
`novel_dev` curation/freeze is required before post-repair empirical
comparison where practical. This report neither curates it nor implements
any repair. The n001 Gold discrepancy merits forward-only review but is not
used to alter the R2 decision.

Current-task scientific calls, tokens, QA runs, retrieval runs and external
judge calls were all zero. Exactly six exposed primary case contents and six
Gold annotations were accessed; matched-control and new-case access were
zero. `novel_validation` content/outcome and holdout content/outcome access
were zero, with zero protected leakage. Product source, tests, prompts,
schemas, trace/manifest schemas, Gold, datasets, calibration, and behavior
were unchanged. No model or retrieval rerun was performed.

`NEXT_TASK_EXECUTION_AUTHORIZED = false`.
