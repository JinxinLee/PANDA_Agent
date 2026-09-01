# D3.5-A0 Structured Evidence-Link Reachability & Bridging Design

## 1. Executive design decision

`D3.5-A0 = COMPLETE / STRUCTURED_EVIDENCE_LINK_DESIGN_FROZEN` at base commit `6082fe8fadb3b89fc225f4b0daa91d17e3a57e69`.

D3.5 adopts three separate mechanisms:

1. **Mechanism A — Governed Structural Reachability:** a D2-resolved governed seed may reach provenance-bearing governed structure through a typed, bounded set of containment, accepted-relation, and curated-workflow transitions.
2. **Mechanism B — Evidence Provenance Materialization:** provenance on a reached governed object, accepted relation, or curated workflow may become a source-native candidate only after exact source/version/locator validation.
3. **Mechanism C — Genuine Evidence-Link Coverage:** genuinely absent provenance may be added only when independently source-grounded, version-grounded, reviewable, and reusable outside the motivating evaluation case.

The bridge is additive and nonauthoritative. It does not canonicalize evidence to the governed object it evidences, change D2 authority, widen repository scope, retune fusion, force selection, or activate production behavior.

This is a design and preregistration freeze only. Runtime/config changes, D1 changes, retrieval runs, model calls, database writes, Qdrant writes, and re-ingestion are all zero.

## 2. Stage boundary: D3 -> D3.5 -> D4

```text
D3
Small shortcut-migration experiment
COMPLETE / SHORTCUT_MIGRATION_EXPERIMENT_DECIDED
↓
D3.5
Structured Evidence-Link Reachability & Bridging
IN_PROGRESS
↓
D4
Incremental migration of appropriate query expansions
NOT_STARTED
```

D3 remains historically complete and is not reopened. Its formal verdict remains `PASS`, meaning the frozen experiment was valid and attributable, not that structured migration succeeded.

D4 now requires both:

- D3 complete with a valid shortcut-migration experiment; and
- the D3.5 structured evidence-link bridge validated by D3.5-A2.

D3.5 does not remove query expansions. D4 retains ownership of reversible, batch-by-batch migration while preserving true terminology and normalization.

## 3. Evidence from D3

The frozen problem statement is:

> The current structured path can resolve governed objects and traverse accepted D1 structure, but it does not yet provide a sufficiently generic, bounded, auditable bridge from resolved governed identity to retrieval-addressable source evidence.
>
> D3 exposed two distinct mechanism classes:
>
> A. governed evidence provenance already exists but is not reachable and/or not materialized into source-native retrieval candidates;
>
> B. the required governed evidence provenance does not yet exist.

The current A1 path already:

- derives Tier-G/Tier-S/Tier-D seeds from the D2 shadow receipt;
- traverses accepted non-`SAME_AS` relations in both stored and reverse direction;
- traverses curated workflow participants;
- materializes governed endpoint objects;
- contributes them additively through the existing graph channel.

It does not:

- consume `parent_object_id` during query-time traversal;
- apply a predicate/type policy beyond accepted/non-`SAME_AS` filtering;
- consume `evidence_object_ids`, `evidence_paths`, `evidence_source_ids`, or `source_version_ids` from relation provenance;
- convert governed provenance into a source-native candidate.

The repository seed state at the start of D3.5-A1 is `24` objects / `16` accepted relations / `1` curated workflow step (`D3_5_A1_STARTING_REPOSITORY_D1_IDENTITY`). The last observed deployed state was `22 / 16 / 0`. The drift was outcome-neutral for frozen D3, but it is not a valid starting point for D3.5-A1 validation.

### 3.1 Frozen motivating cases

`g036 / event_poca_handoff` is design evidence for **A + B**:

- `event_poca` resolves Tier S to `data_product.restgas.event_poca`;
- that object has governed parent `data_product.restgas.boost_root`;
- repository D1 contains accepted `first_pass_poca` dataflow relations whose provenance includes `macro/target/ana_dpm.C`;
- the frozen one-hop A1 traversal did not reach those relations; and
- A1 could not materialize their provenance even if reached.

`g021 / restgas_profile_workflow` is design evidence for **C**:

- `restgas_profile` resolves Tier S to `configuration.restgas_profile`;
- the required source evidence has no inspectable governed provenance in current D1; and
- A0 does not select a new relation, evidence path, or ontology shape from the evaluation expectation.

Neither case is executed in A0. Neither case supplies a runtime branch or answer-location map.

## 4. Mechanism A — governed structural reachability

Mechanism A is:

```text
D2-resolved governed object
-> existing governed structural context
-> provenance-bearing governed object/relation/workflow
```

Eligible primitives are:

- one validated child-to-parent `parent_object_id` transition;
- accepted relation traversal under the frozen predicate/type policy;
- reverse accepted relation traversal under the same policy;
- explicit curated workflow membership;
- workflow step entrypoint, inputs, and outputs.

Every transition is reachability only. No transition changes identity or increases the authority of the seed. Reached nodes may expose provenance, but provenance materialization is a separate Mechanism-B step.

## 5. Mechanism B — evidence provenance materialization

Mechanism B is:

```text
reached governed object / accepted relation / curated workflow
-> validated governed evidence provenance
-> retrieval-addressable source-native evidence candidate
```

The provenance origin and the source evidence remain distinct identities. For example, `workflow.restgas.first_pass_poca` is not co-referential with `macro/target/ana_dpm.C`; the latter may evidence the former without becoming its canonical identity.

Materialization is terminal. A materialized source object does not become a new graph frontier. This prevents a provenance path from turning into unbounded source-neighborhood expansion.

## 6. Mechanism C — genuine evidence-link coverage

Mechanism C owns genuine D1 coverage gaps only. A proposed link must be:

- grounded in independently inspected source evidence;
- independent of evaluation outcome labels and legacy payloads;
- semantically justified by the domain relationship;
- reviewable and accepted through normal D1 governance;
- tied to an explicit source version;
- reusable outside the motivating case.

The rejection test is:

> Would this governed link still make sense if the motivating evaluation case did not exist?

If not, reject it.

When an already correct governed object, relation, or workflow can carry the necessary provenance, add evidence provenance there. Do not invent an ontology predicate merely to attach an answer file. A0 deliberately does not preregister any g021-specific new relation or path.

## 7. Seed authority and D2 contract

| Resolver output | May seed reachability? | Frozen handling |
|---|---:|---|
| Tier G | Yes | Bounded governed identity seed; traversal begins at the matched governed object. |
| Tier S | Yes | Matched-record structure only; `canonical_object_id = null`; no cross-record canonicalization. |
| Tier D unique | Yes | Nonauthoritative additive advisory seed; cannot filter, scope, canonicalize, or override. |
| Tier D ambiguous | Yes, atomic and bounded | Admit and traverse the complete ambiguity set only when its size is at most `8` and the whole set fits the remaining global seed budget; otherwise preserve the full receipt and traverse none from that branch. |
| Corrective-only | No | Advisory candidate only; traversal requires an independent valid governed seed. |
| UNRESOLVED | No | No reachability and no negative filtering. |
| RESOLVED_MULTIPLE | No | Inactive and unevaluated. |
| SAME_AS | No | Inactive and unevaluated for this path. |
| Whole-question fallback | No | Prohibited. |

The shared seed cap is `8`. Independent Tier-G, Tier-S, and Tier-D-unique seeds are processed first in their existing authority order. A complete Tier-D ambiguity set is then admitted only as a whole when its size is at most `8` and the whole set fits the remaining global seed budget. If the set exceeds `8` or does not fit the remaining budget, the bridge preserves the full ambiguity receipt, traverses none from that branch, and emits `STRUCTURAL_PATH_AMBIGUOUS` with reason `AMBIGUITY_SET_EXCEEDS_SAFE_SEED_BUDGET`. It never truncates, samples, or selects a top-8 subset. Graph traversal and evidence materialization cannot resolve identity ambiguity.

## 8. Structural primitive semantics

| Primitive | Direction | Reachability | Identity authority | Candidate seed | May expose provenance | Governance/scope boundary |
|---|---|---:|---:|---:|---:|---|
| `parent_object_id` | child -> parent only | Yes | None | Yes | Yes | Validated governed parent; compatible containment types; plan scope; one transition maximum. |
| Accepted relation | subject -> object | Predicate/type gated | None | Yes | Yes | `review_status=accepted`; listed predicate; `SAME_AS` excluded; plan scope. |
| Accepted relation | object -> subject | Predicate/type gated | None | Yes | Yes | Original edge/predicate preserved; reverse eligibility explicit; plan scope. |
| Workflow entrypoint | step/workflow <-> entrypoint | Yes | None | Yes | Yes | Curated seed workflow and D1 workflow integrity. |
| Workflow inputs/outputs | input <-> step and output <-> producing step | Yes | None | Yes | Yes | Explicit declared participants only; plan scope. |
| Workflow containment | participant <-> owning curated workflow/declared step | Yes | None | Yes | Yes | Explicit representation only; no inferred membership. |
| Source-native provenance | terminal materialization | No further traversal | None | No | Yes | Accepted provenance plus exact source/version/locator resolution. |

## 9. Predicate and direction policy

All ordinary relations have `identity authority = false`. The default is deny unless the predicate is listed.

| Predicate class | Predicates | Forward | Reverse | Evidence exposure | Workflow/process expansion |
|---|---|---:|---:|---:|---:|
| Dataflow | `PRODUCES`, `CONSUMES`, `PRODUCES_INPUT_FOR` | Yes | Yes | Yes | Yes |
| Implementation/formalization | `IMPLEMENTS`, `FORMALIZES`, `IMPLEMENTED_AS_PIPELINE`, `THEORETICAL_BASIS_FOR` | Yes | Yes | Yes | `IMPLEMENTED_AS_PIPELINE` only |
| Workflow/parameterization | `PRODUCES_PROFILE_FOR`, `PARAMETERIZES`, `CORRECTS` | Yes | Yes | Yes | Yes |
| Documentation | `OPERATIONALLY_DOCUMENTS` | Yes | Yes | Yes | No |
| Repository provenance | `FORKED_FROM` | Yes | No | Yes | No |
| Identity | `SAME_AS` | No | No | No | No |

Forward or reverse traversal additionally requires compatible endpoint types under the governed predicate meaning. Reverse traversal finds the governed source of a stored relationship; it does not reverse, rewrite, or infer the stored predicate. Reverse traversal may reach a provenance-bearing relation or node, but only Mechanism B may create a source candidate from the relation provenance.

`FORKED_FROM` is forward-only and requires both repository versions already in RetrievalPlan/context scope. It can never widen repository scope.

## 10. Traversal budget and boundedness

Three options were considered:

1. raw graph-edge count — rejected because containment, workflow participation, and semantic relations are not interchangeable;
2. increasing global `max_relation_hops` to `2` — rejected because it widens ordinary graph behavior, is shaped by the motivating path, and still does not budget mixed primitives;
3. phased typed transitions — selected because the allowed composition and its cost are explicit.

The frozen A1 budget is:

```text
SEED
  up to 8 governed seeds
↓
CONTAINMENT_CONTEXT
  0 or 1 child->parent transition per root seed
↓
SEMANTIC_REACHABILITY
  0 or 1 accepted relation OR 1 curated workflow transition per path
↓
EVIDENCE_MATERIALIZATION
  terminal, no new frontier
```

Maximum nonterminal transitions per path are `2`. Relation and workflow transitions are alternatives within one path; they cannot be chained in A1. Reachable governed structures are capped at `32`, and bridged source-native candidates at `20`.

Budget exhaustion stops only the affected branch, emits `TRAVERSAL_BUDGET_EXHAUSTED`, preserves ordinary retrieval, and never widens the budget dynamically.

Overexpansion is additionally bounded by predicate semantics, endpoint types, source/version scope, seed authority, deterministic deduplication, and the candidate caps. The design is not a BFS over all accepted D1 adjacency.

Graph semantics define eligibility. Ordinary query/plan relevance may deterministically order already governed and reachable branches when a cap binds, but it cannot invent a relation, increase identity authority, override review state, widen scope, or use an LLM assertion as graph truth.

## 11. Evidence provenance eligibility

| Provenance form | Sufficient by itself? | Frozen contract |
|---|---:|---|
| `evidence_object_ids` | Conditional yes | Each ID must resolve exactly to an existing indexed source-native object within plan scope. |
| `evidence_paths` | No | Lookup key only; must resolve under the strict path contract before candidate creation. |
| `evidence_source_ids` | No | Source qualifier only. |
| `source_version_ids` | No | Version qualifier only. |
| Structured source locator | No | Requires explicit plan-consistent source/version and one exact indexed match. |
| Review/creation metadata | No | Governance validation and receipt only. |

Raw provenance strings never enter ranking. A curated domain object referenced by `evidence_object_ids` may remain an audit anchor, but it becomes a bridged candidate only if it also satisfies the source-native indexed-object contract.

## 12. Source-native candidate resolution

Path resolution uses:

```text
source_id
+ source_version_id
+ canonical repository-relative locator path
-> one exact indexed source-native object
```

Path normalization converts separators to `/`, removes one leading `./`, rejects absolute paths and parent-directory traversal, and preserves case. Matching is exact; basename, substring, fuzzy filename, semantic, and LLM matching are prohibited.

If `source_version_ids` is present, it must agree with the RetrievalPlan. Otherwise the plan's locked version for the evidence source is used. “Latest” is never inferred.

For path-only provenance, the target is the unique path-owning source-native container object. Arbitrary chunks or symbol descendants are not selected. A more specific governed locator or `evidence_object_id` may select a specific indexed descendant. The resolved `object_type` is preserved rather than coerced.

- zero matches -> `PROVENANCE_SOURCE_OBJECT_NOT_FOUND`; inject none;
- multiple coequal matches -> `PROVENANCE_SOURCE_OBJECT_AMBIGUOUS`; inject none and record all identities;
- one exact match -> continue to source/version validation.

## 13. Version/scope safety

Every bridged candidate preserves:

- `source_id`;
- `source_version_id`;
- canonical/source-native locator;
- `object_type`;
- governed provenance origin.

If provenance conflicts with the RetrievalPlan, the bridge emits `VERSION_SCOPE_CONFLICT`, injects nothing, leaves the plan unchanged, and preserves ordinary retrieval. A relation cannot introduce a repository absent from `target_repositories` or `context_sources`.

## 14. Candidate authority and retrieval integration

A bridged source object is a:

```text
GOVERNED_PROVENANCE_BACKED_ADDITIVE_RETRIEVAL_CANDIDATE
```

It has no identity authority and no independent cross-channel priority. It cannot hard-filter other channels, force final selection, globally override ranking, restrict scope, narrow scope, or suppress another channel.

The logical interface is a `structured_evidence` substream. Physically, it is deduplicated and prefixed into the existing graph candidate stream under the existing stable merge semantics, graph limit, and graph weight. This is explicit within-graph prefix precedence, so bridged candidates can displace ordinary graph candidates when the graph limit binds. It is not an independent cross-channel priority: the substream receives no extra RRF vote, new weight, or double vote. Other channels, global fusion weights, reranker prompt, selector, and production defaults remain unchanged.

The integration receipt must record `bridged_candidate_count`, `graph_candidates_before_bridge`, `graph_candidates_after_bridge`, `graph_candidates_displaced_by_prefix`, `displaced_object_ids`, `bridged_candidate_ids`, and `deduplicated_overlap_count`.

## 15. Provenance and diagnostics

Reachability and materialization use separate receipts.

`StructuredReachabilityReceipt` records at least:

- query-grounded seed mention;
- D2 resolution status;
- seed authority tier and seed object ID;
- root seed rank;
- node IDs, transition types, edge IDs, predicates, and directions;
- parent transitions;
- workflow/workflow-step IDs;
- budget consumed and remaining;
- reachability status.

`StructuredEvidenceBridgeReceipt` records at least:

- reachability receipt ID;
- provenance origin type and governed origin ID;
- evidence field used;
- review/creation metadata;
- lookup sources, versions, and locator;
- exact lookup match count;
- resolved candidate object ID, source, version, locator, and object type;
- candidate authority/advisory role;
- reason included and bridge status.

This makes the following stages independently inspectable without hidden chain-of-thought:

```text
seed resolved
-> structure reached
-> provenance found
-> source object resolved
-> candidate injected
```

The D3.5 engineering/focused-validation diagnostics are:

- `NO_ELIGIBLE_STRUCTURED_SEED`
- `STRUCTURAL_PATH_NOT_FOUND`
- `STRUCTURAL_PATH_AMBIGUOUS`
- `TRAVERSAL_BUDGET_EXHAUSTED`
- `GOVERNED_PROVENANCE_NOT_FOUND`
- `GOVERNED_PROVENANCE_INVALID`
- `PROVENANCE_SOURCE_OBJECT_NOT_FOUND`
- `PROVENANCE_SOURCE_OBJECT_AMBIGUOUS`
- `VERSION_SCOPE_CONFLICT`
- `BRIDGED_CANDIDATE_INJECTED`
- `BRIDGED_CANDIDATE_RANKED_OUT`
- `PROHIBITED_DIRECT_SHORTCUT_ATTEMPT`
- `CONTROL_OVEREXPANSION`

These do not replace or rewrite the frozen D3 formal taxonomy.

## 16. Anti-shortcut constraints

D3.5 must replace answer-location shortcuts with governed structural/evidence semantics, not move the shortcut from YAML into the graph.

Prohibited shapes include:

- `trigger phrase -> file`
- `rule_id -> file`
- `rule_id -> evidence_path`
- `case_id -> object`
- `case_id -> file`
- `question_id -> relation path`
- `bound_rule_id -> traversal route`
- `benchmark expected evidence -> D1 relation`
- `evaluation selector -> governed object`
- `legacy payload -> new structured map`
- an object-ID branch semantically equivalent to `if event_poca: return ana_dpm.C`

Runtime does not receive case IDs, question IDs, bound rule IDs, comparison roles, expected evidence, or evaluation selectors.

## 17. Runtime D1 materialization prerequisite

D3.5 distinguishes and freezes:

1. the starting repository-governed D1 identity (`D3_5_A1_STARTING_REPOSITORY_D1_IDENTITY`, currently `24` objects / `16` accepted relations / `1` curated workflow step);
2. the final approved post-A1 repository-governed D1 identity (`D3_5_A2_FINAL_REPOSITORY_D1_IDENTITY`), reflecting any independently approved Mechanism-C governance additions;
3. a separate isolated D3.5 dev/evaluation materialization identity, synchronized to exactly match the final approved repository D1 identity before A2 (`isolated_materialization_matches_final_repository_D1 = true`);
4. the deployed production materialization identity, whose last observed historical state was `22 / 16 / 0`.

A1 begins with a read-only comparison between the starting repository-governed D1 identity and the isolated evaluation identity. If the isolated state is stale, A1 may use the smallest existing isolation mechanism—such as a separate database, schema, configuration target, or fixture—to perform controlled ingestion into that isolated target only. If approved Mechanism-C changes occur during A1, the isolated state is resynchronized to match `D3_5_A2_FINAL_REPOSITORY_D1_IDENTITY` before pre-A2 freezes. The deployed target is not a synchronization target and `PRODUCTION_STRUCTURED_STATE_WRITES = 0`.

The isolated action must record target identity, exact counts, source configuration or relevant commit, and run/timestamp when repository conventions support them. It materializes only independently approved current D1 state, consumes no D3 outcomes or legacy payloads as knowledge, modifies no query expansion, alters no D2 authority, and remains setup/provenance work rather than a scientific treatment. Mechanism-C writes follow repository config -> review/freeze -> isolated evaluation materialization only.

If no isolated materialization is possible, A1 must stop before ingestion and report `D3.5-A1 BLOCKED / ISOLATED_MATERIALIZATION_UNAVAILABLE`; it must never silently rewrite the deployed database. No ingestion or deployed-state write occurs in A0-R1.

## 18. D3.5-A1 implementation contract

The exact next task is **D3.5-A1 — Bounded Structured Evidence-Link Bridging Prototype**.

A1 must first establish an isolated D3.5 evaluation target, initially synchronize only that target to starting approved repository D1 (`D3_5_A1_STARTING_REPOSITORY_D1_IDENTITY`, currently `24 / 16 / 1`), and implement and validate the bridge with synthetic, unit, or static fixtures. If approved Mechanism-C changes occur, A1 updates repository configs and resynchronizes the isolated target to match `D3_5_A2_FINAL_REPOSITORY_D1_IDENTITY` before freezes.

A1 may:

- choose the smallest existing isolation mechanism and synchronize only the isolated D3.5 dev/evaluation materialization under the prerequisite above;
- implement generic typed structural reachability;
- implement strict evidence-provenance materialization;
- add a narrowly justified Mechanism-C evidence link only after independent source inspection, version grounding, normal governance review, and the counterfactual gate;
- add focused deterministic T0 tests;
- emit separate reachability and bridge receipts;
- enforce anti-shortcut safeguards.

A1 may not:

- run formal g036/g021 recovery evaluation or inspect recovery metrics;
- run `g036`, `g021`, `n006`, `g041`, `g020`, or `n004` through the formal retrieval comparison;
- delete legacy shortcuts;
- activate production structured behavior;
- change D2 authority;
- perform broad D1 expansion;
- retune fusion, reranker, or selector behavior.

Before A2, all three freezes are required: `D3_5_A1_IMPLEMENTATION_FROZEN = true`, `D3_5_A2_FINAL_REPOSITORY_D1_IDENTITY_FROZEN = true`, and `D3_5_EVALUATION_D1_MATERIALIZATION_FROZEN = true` (with `isolated_materialization_matches_final_repository_D1 = true`). The A2 run manifest must record the A1 implementation commit SHA, starting repository D1 identity, final repository D1 identity, whether D1 changed during A1, change summary, final counts, stable object IDs, relation IDs/tuples, workflow IDs, isolated materialization identity, deterministic proof/accounting of match to final repository D1, deployed production materialization identity, and that production remained untouched (`true`).

## 19. D3.5-A2 focused validation contract

**D3.5-A2 — Focused Evidence-Link Recovery Validation** owns the first post-D3.5 outcome exposure.

The selected design is a focused four-arm paired comparison, all against one frozen A1 implementation and the same frozen synchronized isolated D1 materialization:

| Arm | Contract |
|---|---|
| `LEGACY` | The two selected legacy rules active; structured path and D3.5 bridge disabled. |
| `ABLATION` | The two selected legacy rules suppressed; structured path and D3.5 bridge disabled. |
| `STRUCTURED_UNBRIDGED` | The two selected legacy rules suppressed; existing frozen D3-A1 structured path enabled against final repository D1 (`D3_5_A2_FINAL_REPOSITORY_D1_IDENTITY`); D3.5 reachability/evidence bridge disabled. |
| `STRUCTURED_BRIDGED` | The two selected legacy rules suppressed; the same synchronized current structured path plus the frozen D3.5 bridge enabled against final repository D1. |

All four arms use the same frozen synchronized isolated evaluation materialization exactly matching `D3_5_A2_FINAL_REPOSITORY_D1_IDENTITY`. The historical D3 `STRUCTURED` arm used deployed `22 / 16 / 0`; it is therefore non-interchangeable with the current `STRUCTURED_UNBRIDGED` arm.

The preregistered contrasts are exact:

- `LEGACY - ABLATION = shortcut_dependency`;
- `STRUCTURED_UNBRIDGED - ABLATION = unbridged_structured_contribution` (measures the contribution of the final repository-governed D1 state and pre-D3.5 structured traversal path);
- `STRUCTURED_BRIDGED - STRUCTURED_UNBRIDGED = incremental_bridge_effect` (measures the incremental bridge effect beyond the final governed D1 state);
- `STRUCTURED_BRIDGED - LEGACY = final_legacy_parity`.

`STRUCTURED_BRIDGED - ABLATION` is the combined current structured-plus-bridge contribution and must not be described as a pure bridge effect.

Frozen interpretation examples:

- LEGACY succeeds, ABLATION fails, UNBRIDGED fails, BRIDGED succeeds: dependency is confirmed, the pre-D3.5 structured path does not recover under synchronized D1, and the bridge incrementally recovers behavior.
- LEGACY succeeds, ABLATION fails, UNBRIDGED succeeds, BRIDGED succeeds: dependency is confirmed, synchronized final D1 plus the pre-D3.5 structured path already recovers behavior, and an incremental bridge effect is not established.
- LEGACY succeeds, ABLATION fails, UNBRIDGED partially succeeds, BRIDGED fully succeeds: a pre-D3.5 contribution exists and the bridge adds incremental recovery.
- BRIDGED is worse than UNBRIDGED: bridge-introduced regression.

Positive cases are the already-exposed `g036` and `g021` only. Controls are frozen before A1:

| Case | Frozen role |
|---|---|
| `n006` | Nearby nontrigger control |
| `g041` | Ambiguity/abstention and negative control |
| `g020` | Same subsystem with no governed evidence bridge required |
| `n004` | Ordinary retrieval already succeeds |

This is `6 cases x 4 arms = 24` future retrieval executions, not a full `16 x 4` rerun. The frozen cases remain exactly `g036`, `g021`, `n006`, `g041`, `g020`, and `n004`. Selection uses already-exposed D3 roles, not treatment likelihood. No addition or substitution is allowed after A1 outcome exposure.

A2 applies the four frozen contrasts to required-evidence outcome, `Recall@5`, `Recall@10`, `Recall@20`, MRR, combined candidate recall, and final-evidence recall where applicable, using the same frozen retrieval metrics and no post-outcome thresholds. For each control, `STRUCTURED_BRIDGED` versus `STRUCTURED_UNBRIDGED` specifically checks new irrelevant candidates, graph-channel displacement, ambiguity collapse, abstention break, scope/version leakage, and final-evidence displacement.

## 20. D4 entry criteria

D4 remains `NOT_STARTED`. Its dependency is:

```text
D3 COMPLETE / valid shortcut-migration experiment
+
D3.5 structured evidence-link bridging mechanism validated by D3.5-A2
```

`D3 PASS` alone is insufficient. D4's role remains incremental migration of appropriate query-expansion batches with stable terminology retained, answer-location shortcuts removed only when a generic replacement is evidenced, and every batch reversible.

## 21. Lifecycle

After A0:

```text
D3 = COMPLETE / SHORTCUT_MIGRATION_EXPERIMENT_DECIDED
D3.5 = IN_PROGRESS
D3.5-A0 = COMPLETE / STRUCTURED_EVIDENCE_LINK_DESIGN_FROZEN
D3.5-A0-R1 = COMPLETE / EVALUATION_IDENTIFIABILITY_AND_RUNTIME_ISOLATION_REPAIRED
D3.5-A0-R2 = COMPLETE / POST_A1_D1_IDENTITY_AND_MATERIALIZATION_FREEZE_REPAIRED
D3.5-A1 = NOT_STARTED
D3.5-A2 = NOT_STARTED
D4 = NOT_STARTED
```

D3.5 success requires more than both motivating cases passing. The frozen criteria are:

- bounded, deterministic, auditable reachability;
- candidates derived only from accepted governed structure and validated provenance;
- zero evaluation-shaped mappings or legacy-payload reuse;
- g036-type existing provenance can become source-native when structurally reachable;
- g021-type coverage is independently source-grounded and reusable;
- no material overexpansion, abstention break, evidence displacement, or scope leakage on controls;
- unchanged D2 authority;
- exact source/version/locator validity;
- additive candidate authority only;
- unchanged production defaults, fusion, reranker, selector, query expansions, and production activation.
- bridge incremental effect identifiable separately from synchronized D1 and pre-D3.5 structured-path effects;
- no partial Tier-D ambiguity truncation;
- deployed production structured state untouched during A1/A2;
- measured and bounded graph-prefix displacement.

No implementation result or recovery result is claimed by A0. The exact next task is **D3.5-A1 — Bounded Structured Evidence-Link Bridging Prototype**.

## 22. D3.5-A0-R1 — Evaluation Identifiability & Runtime-Isolation Repair

R1 is a static contract repair to the accepted A0 design. It preserves Mechanisms A/B/C, `g036 = A + B`, `g021 = C`, D2 authority, child-to-parent-only containment, predicate/type-gated reverse traversal, the phased typed traversal budget, exact fail-closed source resolution, the additive/no-new-RRF-vote candidate boundary, and the D4 dependency.

R1 repairs only four defects and records why each repair is necessary:

1. A2 now has four synchronized isolated arms because historical D3 `STRUCTURED` used `22 / 16 / 0` and cannot replace a `24 / 16 / 1` synchronized-state `STRUCTURED_UNBRIDGED` counterfactual.
2. Tier-D ambiguity admission is atomic and fail closed because top-8 truncation would turn a safety budget into implicit identity selection.
3. repository, isolated evaluation, and deployed production materialization identities are distinct because synchronizing by overwriting the deployed graph would change ordinary/default retrieval state; production writes remain zero.
4. `structured_evidence` has explicit within-graph prefix precedence and displacement diagnostics because prefix-then-deduplicate-under-limit can displace ordinary graph candidates, even though it creates no independent cross-channel priority, extra vote, new weight, or identity authority.

R1 exposes no scientific outcome, performs no retrieval or ingestion, changes no runtime/config/D1 data, and does not authorize A1 or A2 execution.

## 23. D3.5-A0-R2 — Post-A1 D1 Identity & Materialization Freeze Repair

R2 is a single-issue contract repair to the accepted D3.5-A0 design. It addresses a specific defect in the post-A1 D1 identity specification: `24` objects / `16` accepted relations / `1` curated workflow step is the authoritative repository D1 state at the start of D3.5-A1, not the only possible A2 state.

During D3.5-A1, an independently justified Mechanism-C governed evidence linkage may be added if it passes the counterfactual governance gate. Furthermore, provenance-only metadata changes could alter semantic identity while keeping counts at `24 / 16 / 1`. Therefore, counts alone are required accounting metrics but are insufficient to define D1 semantic identity.

R2 establishes the following frozen contracts:

1. **Two Distinct Repository Identities:**
   - `D3_5_A1_STARTING_REPOSITORY_D1_IDENTITY`: the approved repository D1 state when A1 begins (starting baseline, currently `24` objects / `16` accepted relations / `1` curated workflow step).
   - `D3_5_A2_FINAL_REPOSITORY_D1_IDENTITY`: the final approved repository D1 state after all A1 implementation and any independently approved Mechanism-C governance additions, frozen before any A2 outcome exposure.

2. **Counts Are Accounting, Not Identity:**
   - Object, relation, and workflow step counts are required accounting but cannot substitute for semantic identity.
   - Identical counts can differ in relation provenance, metadata, evidence paths/IDs, source/version grounding, relation identity, or workflow step content.
   - Identity is anchored in normal repository state: Git SHA, authoritative config paths (`configs/seed_objects.yaml`, `configs/seed_relations.yaml`, `configs/seed_workflows.yaml`), stable object IDs, relation IDs or stable (subject, predicate, object) tuples, workflow step IDs, and relevant provenance fields without ad hoc hash inventories.

3. **Mechanism-C Governance Gate Unchanged:**
   - Genuine evidence-link coverage requires independent source grounding, version grounding, reviewable accepted status, semantic justification, and passing the counterfactual gate: *Would this linkage remain justified if the motivating evaluation case did not exist?* (Reject if no).
   - No g021 linkage is preregistered in A0/R2.

4. **Freeze Lifecycle & Three Pre-A2 Freezes:**
   - Sequence: starting repo D1 (currently `24 / 16 / 1`) -> A1 implementation -> optional approved Mechanism-C -> final approved repo D1 -> freeze final repo identity (`D3_5_A2_FINAL_REPOSITORY_D1_IDENTITY_FROZEN = true`) -> exact isolated materialization -> freeze isolated identity (`D3_5_EVALUATION_D1_MATERIALIZATION_FROZEN = true`, `isolated_materialization_matches_final_repository_D1 = true`) -> A2 execution.
   - Before A2 begins, all three flags must be `true`: `D3_5_A1_IMPLEMENTATION_FROZEN`, `D3_5_A2_FINAL_REPOSITORY_D1_IDENTITY_FROZEN`, and `D3_5_EVALUATION_D1_MATERIALIZATION_FROZEN`.

5. **Exact Isolated Materialization Matching Across All Four Arms:**
   - The isolated evaluation materialization must exactly match `D3_5_A2_FINAL_REPOSITORY_D1_IDENTITY`.
   - All four A2 evaluation arms (`LEGACY`, `ABLATION`, `STRUCTURED_UNBRIDGED`, `STRUCTURED_BRIDGED`) share the exact same A1 commit, final repository D1 identity, and isolated evaluation materialization. No arm-specific D1 state is permitted.

6. **Two-Stage A1 Synchronization:**
   - A1 may synchronize isolated state initially to the starting identity for implementation/T0 testing, and then resynchronize to the final approved repository D1 identity after approved Mechanism-C changes before freezes. Isolated state is never left stale.

7. **Post-Freeze Immutability:**
   - Once the final repository D1 identity is frozen, no further mutations are allowed. Any subsequent defect requires formal invalidation of the pre-exposure freeze, stopping execution, and a separately authorized repair.

8. **Zero Operational Footprint in R2:**
   - R2 performs 0 runtime/config/D1/query-expansion changes, 0 retrieval/model calls, 0 DB/Qdrant writes, 0 ingestion, and 0 scientific outcome exposure. Production structured state writes remain 0.
