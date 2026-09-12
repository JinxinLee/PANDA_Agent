# F2-A5 — Semantic Source Obligation Generalization

> **CORRECTION / SUPERSESSION NOTICE (F2-A5-R1).** This report's initial
> terminal `COMPLETE / PASS / QUESTION_GROUNDED_SOURCE_OBLIGATION_SEMANTICS_ESTABLISHED`
> closeout (and the aggregate `F2 = COMPLETE / PASS / A1_A2_A3_A4_A5_COMPLETE`)
> was subsequently found premature by an independent post-commit audit: the
> architecture below is valid and was preserved, but the question-grounded
> helper used unbounded substring matching — "hypothesis" triggered a hard
> paper obligation ("thesis" substring), "macroscopic" triggered a hard code
> obligation ("macro" substring), "paperless" triggered paper, and the
> ambiguous bare "which source" triggered code. Those boundaries are repaired
> by `evaluation/F2_A5_R1_SOURCE_OBLIGATION_BOUNDARY_REPAIR.md`
> (F2-A5-R1 = `COMPLETE / PASS / SOURCE_OBLIGATION_MATCHING_BOUNDARY_ESTABLISHED`),
> which is the authoritative final lifecycle record for this surface; the
> aggregate F2 closure is re-validated only after R1. The narrative below is
> preserved unchanged for historical transparency.

Status: `COMPLETE / PASS / QUESTION_GROUNDED_SOURCE_OBLIGATION_SEMANTICS_ESTABLISHED`
Type: bounded production cleanup + deterministic verification (PF-LR1 Group E).
Zero PANDA scientific/evaluation calls; zero protected-data access.

Task identity: F2-A5 — Semantic Source Obligation Generalization.
Traceability: PF-LR1 Group E / F1 residual R01 (provenance only).

## 1. Starting state

```text
HEAD = 79df30e840b3ad7c75d2f1c3ebe1b3e495beac1a (Repair F2-A4 premise question grounding)
F2-A1..F2-A4-R1 = all COMPLETE / PASS (see status)
F2 = IN_PROGRESS / A1_A2_A3_A4_COMPLETE
F3 = NOT_STARTED / UNEXECUTED
Phase F = IN_PROGRESS / F2_A4_COMPLETE
normal default = legacy_question_core
default promotion = DEFERRED
```

## 2. Historical R01 mechanism (verified at starting HEAD)

Authority chain: `configs/retrieval_policies.yaml` fixed intent mappings
(`algorithm_theory: required_sources: [paper]`; `algorithm_implementation:
[paper, code]`) → `Retriever.analyze` (`required_source_types=policy.required_sources`)
→ `RetrievalPlan.required_source_types` → consumers:
- retrieval: exact-paper priority ordering; `_paper` dedicated channel gate;
- selection: `required_first` ordering and required-source backfill inside
  `_prioritize_and_select_evidence` / `select_final_evidence`;
- sufficiency: `QAAgent._sufficiency` emits `missing required source: <type>`
  for any absent hard requirement (honest refusal on a fixed premise).
Provenance: `retrieval.py` carried the explicit "gold policy requires
literature" comment (F1 EXPLICIT provenance). R02 non-paper mappings
(installation/usage/api/data_flow/module_structure/troubleshooting) are F1
`HOLD_UNCERTAIN_PROVENANCE` and stay untouched.

## 3. Repair

1. **Question-grounded derivation** (`_question_grounded_source_obligations`,
   module helper, raw-question-only signature): bounded high-confidence
   vocabulary — paper: `paper/thesis/publication/literature/journal`; code:
   `source code/implementation/implemented/signature/which file/which
   source/macro`. Returns deterministic canonical order plus per-obligation
   support spans.
2. **Authority replacement at the source** (`Retriever.analyze`): for
   `_R01_SOURCE_OBLIGATION_INTENTS` the intent only selects the
   question-grounded regime and `required_source_types` comes from the raw
   question; all other (R02) intents keep `policy.required_sources`
   unchanged. A diagnostic receipt is written to
   `plan.analysis_diagnostics["source_obligations"]`
   (`mode=question_grounded_r01|retained_intent_policy_r02`,
   `authority=raw_question|intent_policy`, `required_source_types`,
   `matches`); internal only, no public-answer change.
3. **Config retirement**: the two R01 `required_sources` entries are now `[]`;
   all `source_budgets` and all six R02 mappings are byte-identical. The
   empty list is a valid outcome (retrieval channels, budgets, and
   verification continue; only the fixed source-class refusal disappears).
4. **Consumers unchanged**: every consumer keeps gating purely on the dynamic
   `plan.required_source_types` field (grep/inspect-audited: `_paper`,
   exact-paper priority, `_prioritize_and_select_evidence`,
   `select_final_evidence`, `_sufficiency` — none reads the intent for
   requirements). The same single derivation feeds the existing plan field.

## 4. R02 preservation matrix (NO CHANGE, config + runtime)

| Intent | required_sources |
|---|---|
| installation | documentation |
| usage | documentation + code |
| api | code |
| data_flow | workflow + code |
| module_structure | code + graph |
| troubleshooting | documentation + code |

Asserted exactly against the loaded config in
`SourceObligationTests.test_r02_mappings_exactly_preserved`; the R02-analyzer
probe additionally proves an R02 intent keeps its policy mapping even when the
question carries paper vocabulary.

## 5. Adversarial contract (T1–T24)

| Test | Contract | Result |
|---|---|---|
| T1 | theory question without source request → `[]` (fixed paper mapping retired) | PASS |
| T2 | implementation question without source request → `[]` (central sentinel) | PASS |
| T3 | explicit paper request → `["paper"]` with support span | PASS |
| T4 | explicit implementation/source request → `["code"]` | PASS |
| T5 | mixed request → `["paper", "code"]` | PASS |
| T6 | same intent (algorithm_theory), different questions → different obligations | PASS |
| T7/T8/T9 | analyzer/plan/expansion metadata cannot create obligations (structural: derivation signature is raw-question-only; receipt records `authority=raw_question`) | PASS |
| T10 | R02 mappings exactly preserved | PASS |
| T11 | source budgets exactly preserved (theory/implementation/usage) | PASS |
| T12 | `_paper` channel gates on the dynamic plan field, not intent | PASS |
| T13 | exact-paper priority follows the dynamic plan field | PASS |
| T14/T23 | required-first/backfill and selector consume the dynamic field; no intent-keyed logic; selector algorithm unchanged (diff-audited) | PASS |
| T15/T16 | sufficiency honors explicit paper/code obligations (`missing required source: paper|code`) | PASS |
| T17 | no-obligation question with valid evidence → sufficient (no source-class refusal) | PASS |
| T18 | zero evidence still refused (`no evidence`) | PASS |
| T19 | version conflict remains authoritative (existing test) | PASS |
| T20 | F2-A4 premise/refusal unchanged (existing tests) | PASS |
| T21 | F2-A3-R1 coverage authority unchanged (existing seam tests) | PASS |
| T22 | R03 fixed paper-page override untouched (diff-audited) | PASS |
| T24 | explicit source insufficiency still terminates pre-answer; no-obligation question keeps the normal answer/verify path (existing full-path tests with realistic catalog) | PASS |

## 6. Boundary audits

- R03 (fixed paper-page override): zero diff.
- R14 (`select_final_evidence`): zero algorithm diff; only its input list
  authority changed.
- R19 (paper taxonomy `li_2026`/`karavdina_2015`/`pflueger_2017`): untouched.
- D4/query expansions: untouched; page hints cannot create hard paper
  obligations (derivation never reads them).
- F2-A1/A1-R1, F2-A2, F2-A3/A3-R1, F2-A4/A4-R1: all preservation sentinels
  pass in the combined run.
- E3 (indirect via sufficiency): explicit source insufficiency still
  terminates pre-answer; no E3 code touched; E3 not reopened.
- Comments: the benchmark-shaped "gold policy requires literature" provenance
  comment is gone with the retired mapping; production comments now describe
  the question-grounded contract.

## 7. Verification

- `PYTHONPATH=src python -m pytest tests/unit/test_retrieval.py -q` → **47
  passed, 7 subtests** (13 new `SourceObligationTests`).
- `PYTHONPATH=src python -m pytest tests/unit/test_qa.py -q` → **91 passed,
  16 subtests** (includes the new sufficiency obligation tests).
- Combined focused run (`test_qa` + `test_retrieval` + E2-A1 42 + focused E3
  49 + `test_service` 13) → **249 passed, 25 subtests passed**.
- `git diff --check` PASS; static sentinels all clean (§4/§6).
- PANDA scientific/evaluation calls = 0; PANDA scientific/evaluation tokens = 0.

## 8. Limitations

- The obligation vocabulary is deliberately narrow (explicit paper terms;
  implementation/source-code terms); ordinary technical questions in R01
  intents now carry no hard source obligation and rely on soft budgets and
  ordinary retrieval.
- R02 non-paper mappings remain intent-level policy under their F1 HOLD
  disposition; generalizing them is not authorized.
- Only R01 is generalized; no claim is made that all source policies are
  generic.

## 9. F2 closure

PF-LR1 defines exactly five F2 groups. All five are now complete through
their accepted corrective repairs:

```text
Group A (R13):          F2-A1  = COMPLETE / PASS (closed by F2-A1-R1)
Group B (R10):          F2-A2  = COMPLETE / PASS
Group C (R08/R09/R11):  F2-A3  = COMPLETE / PASS (closed by F2-A3-R1)
Group D (R04):          F2-A4  = COMPLETE / PASS (closed by F2-A4-R1)
Group E (R01):          F2-A5  = COMPLETE / PASS
```

R12 (E3-reconciled), R14 (boundary review, no current change), R02 (HOLD),
and R03/R05/R06 (F3 package) are not unfinished F2 work.

```text
F2-A5  = COMPLETE / PASS / QUESTION_GROUNDED_SOURCE_OBLIGATION_SEMANTICS_ESTABLISHED
F2     = COMPLETE / PASS / A1_A2_A3_A4_A5_COMPLETE
F3     = NOT_STARTED / UNEXECUTED
Phase F = IN_PROGRESS / F2_COMPLETE_F3_NOT_STARTED
normal default = legacy_question_core (unchanged)
default promotion = DEFERRED (unchanged; promotion relevance != promotion authorization)
Future-applicability note: the accumulated F2 package (A1/A2/A3/A4 material
plus A5) may constitute a future promotion-relevant material candidate under
the PE-LR1 trigger; this records applicability only and authorizes nothing.
```

```text
NEXT_TASK_RECOMMENDATION = F3 — Fixed Locator/Fallback Cleanup
                           (PF-LR1 bounded package: R03, R05, R06)
NEXT_TASK_EXECUTION_AUTHORIZED = false
```
