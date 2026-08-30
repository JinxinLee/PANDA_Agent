# PANDA Agent — ND-0C: Generalization Diagnosis and D2-A3 Handoff Report

> Status: `ND-0C = COMPLETE / GENERALIZATION_DIAGNOSIS_AND_D2_A3_HANDOFF` (2026-08-30).
Diagnosis and handoff only: no repair, no resolver execution on novel_dev, no
production change, zero model/API calls. ND-0 closes with this report.

## 1. Evidence and lifecycle boundary

- Inputs: the immutable ND-0B first-exposure package
  (`evaluation/novel/v1/nd0/`, run `nd0b-first-novel-dev-retrieval-20260830`,
  measurement HEAD `348dd0d`) plus the frozen ND-0A preregistration for the
  diagnosis taxonomy. Raw results/traces/run manifest byte-unchanged.
- Offline analysis only: group-stage matching reuses the evaluator's own
  frozen matcher (`_matched_evidence_groups`) over the immutable record
  diagnostics and the local normalized lookup; no Qdrant/PostgreSQL/Vertex
  access (`NEW_MODEL_CALLS = 0`, `NOVEL_DEV_RETRIEVAL_CASES_RUN = 0`).
- Primary ND-0B metrics are unchanged and remain case-level macro means.

## 2. Measurement validity / known dataset defect

`measurement_execution_valid = true`; `dataset_structural_valid = false` with
exactly one known pre-exposure defect: n023.e1 (`EXPECTED_EVIDENCE_MAPPING_ISSUE`,
`tracking/PndFtsTrackFinder/README.MD` matches no corpus object). That miss is
**not** counted as a system retrieval failure anywhere below; n023.e2 (valid
selector) is diagnosed separately as a system-retrieval target.

## 3. Pipeline funnel (group-level diagnostic accounting)

Denominator: the **49 structurally valid required-evidence groups** of the 27
ordinary-applicable (answered-expected) cases. Distinct from the primary
case-level macro metrics.

| Stage | Groups | Share of 49 |
| --- | --- | --- |
| valid expected groups | 49 | 1.0000 |
| recalled by any executed channel | 37 | 0.7551 |
| present in combined candidate pool | 37 | 0.7551 |
| present in top-20 | 27 | 0.5510 |
(top-5 reference point: 23 groups) | | |
| finally selected | 26 | 0.5306 |

**Why combined candidate recall 0.8117 while Recall@20 is 0.6173:** 10 valid
groups were recalled into the combined candidate pool but did not survive into
top-20 (9 cases: n002, n003, n006, n009, n010, n017, n023, n025, n028). The
frozen traces cannot isolate reranking from fusion/ranking for these (the
reranker stage is not separately attributable), so they are diagnosed
`FUSION_OR_RANKING_FAILURE` per the frozen criterion; `RERANK_FAILURE = 0`.

## 4. Case-level failure-stage accounting (27 applicable cases)

| Primary failure stage (mutually exclusive) | Cases | Case IDs |
| --- | --- | --- |
| NONE (full success) | 12 | n001, n004, n007, n008, n015, n018, n019, n024, n026, n027, n030, n031 |
| CHANNEL_RECALL_FAILURE | 8 | n005, n009, n010, n014, n020, n021, n022, n029 |
| FUSION_OR_RANKING_FAILURE | 7 | n002, n003, n006, n017, n023, n025, n028 |
| FINAL_SELECTOR_FAILURE (primary) | 0 | — (n022's selector loss is secondary to its channel loss) |

## 5. Taxonomy summary (overlapping case counts, frozen labels only)

| Label | Cases | Groups affected |
| --- | --- | --- |
| CHANNEL_RECALL_FAILURE | 8 | 12 |
| FUSION_OR_RANKING_FAILURE | 9 | 10 |
| RERANK_FAILURE | 0 | — |
| FINAL_SELECTOR_FAILURE | 1 | 1 |
| SOURCE_SCOPE_FAILURE | 0 | — |
| VERSION_SCOPE_FAILURE | 0 | — |
| ENTITY_OR_TERMINOLOGY_RELATED | 11 |  |
| EXACT_IDENTIFIER_FAILURE | 3 |  |
| DESCRIPTIVE_TERMINOLOGY_FAILURE | 8 |  |
| CROSS_REPOSITORY_FAILURE | 1 |  |
| MULTI_EVIDENCE_FAILURE | 12 |  |
| CORPUS_OR_INDEX_COVERAGE_FAILURE | 0 | — |
| EXPECTED_EVIDENCE_MAPPING_ISSUE | 1 | 1 |
| EVALUATION_CASE_ISSUE | 0 | — |
| INFRASTRUCTURE_FAILURE | 0 | — |
| UNCLASSIFIED | 0 | — |

Zero-count stages are backed by trace evidence: excluded-candidate reasons
contain no scope/version rejections; no corpus-coverage gap beyond the known
mapping defect; 28/28 completion excludes infrastructure failure; no
additional static case defects were provable, so `additional
EVALUATION_CASE_ISSUE = 0`. Overlapping labels are not summed as mutually
exclusive; only primary stages are.

## 6. Stratified diagnosis (preregistered strata only)

- **Required-evidence count** (single 11 / multi 17): all five all-group
  channel-recall failures with ≥2 groups are multi-evidence cases; the only
  all-groups-missed case is n029 (2 groups). Single-evidence failures (n002,
  n017, n021.e1-side aside) are ranking losses. The aggregate
  single-vs-multi gap is real at case level but the per-case ledger shows two
  distinct mechanisms (channel absence for descriptive multi-group cases vs
  ranking loss), so the correlation alone is not root-cause proof.
- **Repository scope** (single 25 / cross 1 / paper_only 2): the single
  cross_repository case n021 lost its PandaRoot-side group at candidate
  generation while the LuminosityFit side matched (`CROSS_REPOSITORY_FAILURE`,
  1 case — no generalization from this cell).
- **Intent**: losses concentrate in `usage` (n005/n021/n028),
  `algorithm_implementation` (n010/n025/n029), and `data_flow`/`api`/
  `module_structure` singletons; `troubleshooting` (2 cases) fully succeeded.
- **Representativeness**: the two exploratory cases (n028/n029) both failed;
  counts reported without comparative claims (small cells).
- **Source scope** (single_source/cross_source) and family cells add no
  mechanism beyond the per-case ledger above.

## 7. n016 insufficient-evidence diagnosis (separate)

n016 expects `insufficient_evidence`; retrieval returned 12 final evidence
items and the final evidence **fully matches the required group (group recall
1.0 — the targeted Docker pages were selected)**. There is no retrieval recall
failure and no scope/version rejection trace. The refusal expectation belongs
to the QA/answer-layer abstention boundary, which retrieval-only ND-0B does
not exercise. Retrieval-level `answered` is not equivalent to final QA answer
quality. `primary_failure_stage = NONE`; no taxonomy label applies to the
retrieval path for this case.

## 8. Entity/terminology relevance analysis

| D2 relevance | Cases | Failed groups in DIRECT cases |
| --- | --- | --- |
| DIRECT | 7 (n005, n009, n010, n014, n020, n022, n029) | 13 (all lost) |
| INDIRECT | 7 (n002, n003, n006, n017, n023, n025, n028) | — |
| NONE | 14 (12 successes + n016 + n021) | — |

Aggregation rule (ND-0C-R1, deterministic and machine-readable): consider only
system-failed structurally valid groups; case relevance = DIRECT if any such
group is DIRECT, else INDIRECT if any is INDIRECT, else NONE. Group-level
relevance: DIRECT 11 / INDIRECT 10 / NONE 2 (n021.e2 cross-repository
assembly; n022.e3 final-selector loss). Under the now-explicit rule n022 moved
INDIRECT → DIRECT (n022.e1 is a descriptive candidate-generation failure);
counts before the rule was explicit were 6 / 8 / 14. n022 is counted exactly
once in the descriptive-topology accounting below.

- **DIRECT** = descriptively identified governed targets lost at candidate
  generation (n005, n009, n010, n020, n029 — Tier D descriptive context) or an
  exact governed surface whose target never entered any channel pool (n014 —
  exact/structural mechanism, Tier G/S context, explicitly NOT Tier D
  descriptive). Subtype rationale confidence MEDIUM; the underlying stage facts
  are HIGH (trace-shown absence).
- **INDIRECT** = terminology/entity understanding is contextually present but
  the observed loss is primarily ranking (n002, n003, n006, n017, n023, n025,
  n028) or split channel+selector (n022). Candidates were recalled; identity
  mapping was not the failing step.
- **NONE** includes successes, n016 (no retrieval loss), and n021 (cross-
  repository assembly).
- **Descriptive cases** (8: n002, n005, n009, n010, n017, n020, n022, n029):
  observed failure stages are 5 pure candidate-generation losses (n005, n009,
  n010, n020, n029), 2 ranking-loss cases (n002, n017), and 1 mixed channel +
  final-selector case (n022) — 8 cases each accounted exactly once; ambiguity
  vs absence is **absence**, not competition. **Exact-identifier cases** (3 strict: n014, n025, n028; plus
  surface-variation n023): strong identity cues did not prevent 1 channel
  loss and 4 ranking losses — exact-identifier presence does not guarantee
  survival, and this must not be read as resolver activation would fix them.

## 9. D2-A2 vs ND-0 evidence separation

D2-A2 remains the **only direct resolver-efficacy evidence**: descriptive
positives 3/6 resolved / 3/6 ambiguous / 0 wrong-confident; explicit
wrong-confident hazard C16 (whole-question fallback after version/scope
rejection; formal FPR 1/8). ND-0 measured production retrieval with the D2
resolver **shadow / not production-consumed**, so ND-0C classifies
topological/contextual relevance only. No claim of the form "Tier D works",
"Tier D fails", or "D2 should be production-authoritative" is made from
novel retrieval outcomes. The D2 resolver was **not** executed on novel_dev
(`no_d2_resolver_execution_on_novel_dev = true`).

## 10. D2-A3 handoff matrix

Machine-readable: `nd0c_d2_a3_handoff.json`. Summary (wording per the frozen
handoff semantics — evidence supports consideration of / does not establish):

| Mechanism | D2-A2 direct evidence | ND-0C contextual evidence | A3 implication |
| --- | --- | --- | --- |
| Tier G exact governed identity | evidence-bounded: all observed applicable Tier-G behaviors in D2-A2 were correct (explicit canonicalization 1/1; source-native safety 3/3; zero observed false canonicalizations) — observed-sample success, not a global reliability claim | no novel identity-mapping failure; exact/structural case n014 lost its target at candidate generation | evidence does not establish production need from ND-0; A3 must decide |
| Tier S exact structural identity | exact symbol/path cases correct where applicable (C05/C06); conservative competition/version-scope behavior | n014 is the Tier G/S contextual case; n023 is alias/surface-variation context whose actual loss was ranking | observed cases passed; does not establish global safety; A3 must decide |
| Tier D descriptive inference | direct A2 efficacy: 6 descriptive positives — 3 correct / 3 ambiguous / 0 wrong-confident | contextual applicability only: pure descriptive candidate-generation losses n005/n009/n010/n020/n029; later losses n002/n017 (ranking), n022 (mixed channel + final selector); n014 is NOT Tier D context | efficacy UNEVALUATED from ND-0; A3 must decide on D2-A2 + design |
| corrective terms | C08 correct (non-authoritative) | no novel corrective topology | D2-A2 remains primary |
| SAME_AS | no accepted edges; applicability 0 | no novel topology | UNEVALUATED |
| RESOLVED_MULTIPLE | representable; applicability 0 | no novel topology | UNEVALUATED |
| whole-question fallback | C16 is the one valid wrong-confident resolution in the A2 accounting (FPR 1/8); C10/C14 are CASE_INVALID — qualitative observation only, excluded from direct evidence | not observable in production traces (not production-wired) | evaluate fallback safety as a separate mechanism; KEEP_SHADOW vs bounded activation is A3's decision |

## 11. Limitations

- Single small cohort (28 questions / 49 valid groups) — diagnostic
  localization, not statistical estimation; several strata are small cells.
- Reranking is not separately attributable in the frozen traces, so
  `RERANK_FAILURE = 0` is an honesty boundary, not a clean bill.
- Group-stage matching reuses the evaluator's frozen matcher; channel/combined
  stages are new computations over immutable inputs (cross-checked against the
  frozen per-stage provenance where present).
- The n023.e1 dataset defect is excluded from system accounting but n023's
  case-level metrics still include it (primary measurement unchanged).
- The historical Gold comparison remains contextual only; no causal attribute
  is drawn from it.

## 12. Next stage

**D2-A3 — Resolver Role Decision** (NOT_STARTED; decision belongs to D2-A3).
ND-0 closes: `ND-0 = COMPLETE / FIRST_NOVEL_DEV_GENERALIZATION_BASELINE_CLOSED`.
