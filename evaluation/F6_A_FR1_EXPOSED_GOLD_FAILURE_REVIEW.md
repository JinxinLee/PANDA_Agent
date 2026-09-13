# F6-A-FR1 — Exposed Gold Failure Review (Root-Cause Matrix)

Development review artifact. Source evidence: frozen formal run
`data/evaluation/runs/f6a-rc1-gold-formal-full-20260913` (59/59), corrected
gate matrix `evaluation/f6a_gold_gate_matrix_r1_r1_r1.json`, Gold v2.6
questions, and product code at HEAD `557327e`.

```text
PANDA scientific/evaluation calls (FR1) = 0
PANDA scientific/evaluation tokens (FR1) = 0
```

## 1. Review principle applied

The 9 failed gates are downstream symptoms, not 9 independent bugs. The
failure decomposition separates ROOT CAUSE → case-level product behavior →
derived metric failures. Two generic root causes (RC1, RC2) explain all eight
status-mismatch cases and, through them, every failed gate metric.

## 2. Case inventory (Stage R0)

| case | gold status | actual status | observed behavior |
| ---- | ----------- | ------------- | ----------------- |
| g005 | answered | insufficient_evidence | "unsupported requested symbol: PandaRoot" |
| g013 | answered | insufficient_evidence | "unsupported requested symbol: PandaRoot" |
| g027 | answered | insufficient_evidence | "unsupported requested symbol: PandaRoot" (question also names RestgasDetermination) |
| g034 | answered | insufficient_evidence | "unsupported requested symbol: LuminosityFit" |
| g059 | answered | insufficient_evidence | "unsupported requested symbol: LuminosityFit" |
| g060 | answered | insufficient_evidence | "unsupported requested symbol: LuminosityFit" |
| g012 | version_conflict | insufficient_evidence | zero evidence; requested commit `deadbeef` never compared to the locked commit |
| g026 | version_conflict | answered | `cafebabe` request silently ignored; locked snapshot answered as ordinary usage |

## 3. Root-cause matrix

### RC1 — repository display names treated as requested bare class symbols

- **Cases:** g005, g013, g027, g034, g059, g060 (all six false refusals).
- **Code path (evidence):** every query contains a request/definition context
  term ("How is", "Where is", "How do", "How does", "Where is ... defined"),
  so `_requested_bare_class_symbols` (qa.py) adds every compound-cased token.
  The repository display names "PandaRoot" and "LuminosityFit" are
  PascalCase compound tokens and are extracted. `_answerability_guard` checks
  them against the locked catalog (`_locked_symbols`: object `locator.symbol`,
  `locator.path`, and `class/struct/enum` declarations from object text). The
  catalog has no reason to contain repository identities — they are neither
  code symbols nor paths — so the guard returns
  `unsupported requested symbol: <repo display name>` and the pipeline
  refuses.
- **Corroborating contradiction:** the deterministic refusal text asserts
  "The locked corpus does not define PandaRoot/LuminosityFit" while citing
  locked files *inside those repositories* (`docs/Docker/DevelopingInContainer.rst`,
  `ui/PndLmdFitFacade.cxx`, `model/PndLmdSmearingConvolutionModel2D.cxx`,
  ...). This is possibility (F) of the authorized investigation: the guard is
  applied to a token that should not be treated as a bare class symbol. The
  analyzer itself had already classified the token correctly — e.g. g005
  provenance: `target_repositories=["pandaroot"]`,
  `rule=manifest_repo_id, source=explicit_query_reference` — two product
  authorities disagreed about the same token.
- **Secondary effects (derived metrics):** six
  Gold-ANSWERED→insufficient_evidence mismatches (expected_status_accuracy),
  missing final/critical evidence (final_evidence_recall,
  critical_final_evidence_recall), missing answer points
  (answer_point_coverage, critical_answer_point_miss_count), unmet
  required-source coverage (required_source_coverage_answered), the single
  dual-source-required case g060 failing paper+code
  (paper_code_dual_source_rate = 0.0), and — from the contradiction between
  the refusal text and the cited evidence — all 4 `contradictions`
  (g005/g013/g034/g059) and the 1 `major_unsupported_claim_count`
  (g034, `unsupported_symbol_context`).
- **Fix surface:** `Retriever.is_repository_reference(token)` (new, reusing
  the exact `_has_explicit_repository_reference` matching semantics the
  analyzer already uses) + `_answerability_guard` skips repository identities
  before refusing. Generic: no case IDs, no repo hard-coding, manifest-driven.

### RC2 — prepositional commit requests never reach version-conflict detection

- **Cases:** g012, g026.
- **Code path (evidence):** both queries request an explicit commit
  ("Install PandaRoot **from commit deadbeef** instead of the locked corpus
  commit.", "Run LuminosityFit **from requested commit cafebabe** rather
  than the locked master snapshot."). `deadbeef`/`cafebabe` match the
  explicit-SHA extraction (`[0-9a-f]{7,40}`). Binding then requires
  `_has_explicit_version_repository_binding`, whose patterns demand the
  qualifier (`commit|sha|version|ref`) directly adjacent to the repository
  name. The preposition "from" (and g026's modifier "requested") breaks the
  adjacency, binding fails, the SHA lands in `unbound_version_tokens`
  (visible in g012 diagnostics), and no `version_conflicts` entry is produced.
  The requested-version comparison (`requested not in {locked, locked[:7],
  fixed_refs}`) never runs. Downstream, the plan has zero conflicts, so
  status is decided by evidence sufficiency alone: g012 (zero retrieved
  evidence) → INSUFFICIENT_EVIDENCE; g026 (evidence available) → ANSWERED
  with the locked snapshot, silently ignoring the version request.
- **Status-precedence audit (authorized §12):** the existing precedence is
  correct and was not the defect — `plan.version_conflicts` is checked before
  evidence sufficiency and before the answerability guard
  (`_sufficiency` returns conflicts first; the finalize path maps
  conflicts → VERSION_CONFLICT; conflicts block revision). With RC2 fixed at
  the binding layer, the conflict propagates to VERSION_CONFLICT through the
  existing precedence in both evidence states. New regression test locks:
  conflict + zero evidence must stay VERSION_CONFLICT, never degrade.
- **Secondary effects (derived metrics):** two Gold VERSION_CONFLICT status
  mismatches (expected_status_accuracy), plus the evidence/recall misses on
  the refused g012.
- **Fix surface:** `_has_explicit_version_repository_binding` gains a bounded
  connector between repository and qualifier: one preposition
  (from/at/using/with/of/in/for) plus an optional article/modifier
  (the/a/requested/specific/given). Generic parsing fix; existing adjacent
  syntax (`repo commit sha`, `repo@sha`, `commit sha for/of/in repo`), the
  bare-SHA-stays-unbound rule, and the multi-repository no-bind rule are
  preserved by regression tests.

## 4. Gates explained

| failed gate | explained by |
| ----------- | ------------ |
| expected_status_accuracy | RC1 (6 cases) + RC2 (2 cases) = all 8 status mismatches |
| final_evidence_recall / critical_final_evidence_recall | RC1 refusals + RC2 g012 refusal |
| answer_point_coverage / critical_answer_point_miss_count | RC1 refusals (+ RC2 g012) |
| required_source_coverage_answered | RC1 refusals |
| paper_code_dual_source_rate | RC1 g060 refusal (no standalone fix) |
| contradiction_count (4) | RC1 refusal text vs cited evidence (g005/g013/g034/g059) |
| major_unsupported_claim_count (1) | RC1 (g034) |

No gate required an evaluator change; no downstream metric filter was added.

## 5. Fix provenance

- Generic rule; no case-ID branch; no benchmark-specific literal; no fixed
  locator; no release-threshold logic in product code.
- Conservative refusal behavior preserved and regression-locked: genuinely
  uncataloged class-shaped tokens, exact future-runtime requests, deleted
  artifact reconstruction, universal proof requests, and genuine version
  conflicts all keep their existing refusals (existing F2-A4/F2-A5 suites
  pass unchanged).
- Companion machine-readable matrix:
  `evaluation/f6_a_fr1_exposed_gold_failure_review.json`.
