# F6 Formal Repeat Eligibility and Stochastic Attempt Policy

## Decision

`SAME_PRODUCT_LINEAGE_FORMAL_REPEAT = PROHIBITED`

A terminal formal F6-A result closes that product-behavior lineage for ordinary
single-attempt validation. Provider-hosted model randomness does not create a new
candidate identity and does not justify another formal exposed-Gold attempt.

A fixed replicate block may be scientifically valid only when its complete
protocol is preregistered before the first scientific call. The block then forms
one formal evaluation with one aggregate terminal result; its scheduled runs are
not separate attempts. A replicate protocol cannot be introduced after a
terminal result or after case-level outcomes have been inspected.

No replicate count or aggregation rule is established here. Current evidence
does not justify inventing either. Therefore this policy does not create a
replicate route for the current lineage.

## Scientific rationale

Repeatedly running the same stochastic candidate on exposed Gold and stopping
on the first PASS selects a favorable realization. The same problem applies to
reporting the best run, discarding failed runs, changing the scheduled count
after seeing outcomes, or tuning product behavior between runs. These practices
are optional stopping and pass chasing, not independent validation.

The lifecycle prevents them by treating the first complete terminal formal
result as the end of ordinary eligibility for that lineage. Infrastructure
recovery may complete an interrupted run under the exact frozen run and
candidate identity, but successful cases are not rerun for quality and all
failed-attempt usage remains recorded.

Repeated exposure also increases governance risk even when source code is
unchanged. Model stochastic replication estimates variability only when the
replicate schedule and aggregate decision are fixed in advance. Inspecting
exposed failures and then modifying the product is development against exposed
Gold; it requires a materially new candidate and fresh preregistration rather
than another draw from the old candidate.

## Product-behavior lineage

A product-behavior lineage is defined by the complete behavior-affecting
identity, not by the latest Git commit alone. It includes:

- production source code and behavior-affecting runtime packages;
- generation, revision, verification, and composition prompts and logic;
- retrieval, reranking, source-budget, and query-expansion policy;
- corpus, chunking, embedding, and index identities where they affect results;
- generation and verification model identities;
- runtime mode and behavior-affecting configuration.

Documentation, lifecycle records, receipt formatting, execution bookkeeping,
and tests that do not alter deployed behavior do not create a new product
lineage.

## Material product change

A material product change is an independently justified, behavior-affecting
change relevant to the evaluation hypothesis. It must be stated without relying
on a favorable rerun and must be frozen and preregistered before formal calls.
It need not guarantee improvement, but it must be capable of changing product
outputs or the evidence path that produces them.

Infrastructure robustness that only prevents or records execution failures is
not a material product change when successful-case behavior is unchanged. A Git
commit is neither necessary nor sufficient by itself; the bound behavior
identity determines lineage.

## Material-change decision matrix

| Change category | Material product change? | New candidate lineage? | Fresh F6-A attempt? | Preregistration requirement |
|---|---|---|---|---|
| 1. Product source-code behavior change | Yes | Yes | Yes | Bind the changed behavior, hypothesis, tests, and complete frozen identity. |
| 2. Prompt change | Yes | Yes | Yes | Bind prompt hashes/versions and explain the general behavior hypothesis. |
| 3. Retrieval-policy change | Yes | Yes | Yes | Bind policy/configuration, index compatibility, and affected retrieval hypothesis. |
| 4. Query-expansion behavior change | Yes when runtime queries can change | Yes when behavior-affecting | Yes when material | Bind expansion identity and justify the general rule independently of exposed cases. |
| 5. Generation-model identity change | Yes when explicitly configured and reproducibly distinguishable | Yes | Yes | Bind model/version/serving identity and justify the change as a candidate decision, not a retry. |
| 6. Verification-model identity change | Yes when explicitly configured and reproducibly distinguishable | Yes | Yes | Bind verification model identity and preserve generation/verifier separation. |
| 7. Embedding/index change | Depends | Depends | Depends | A model, dimension, embedding-text, corpus, chunking, or behavior-affecting index change creates a new lineage; an identical deterministic rebuild does not. Bind all affected identities. |
| 8. Gold forward-only governance change | No | No | Depends | Declare a contract-reconciliation evaluation against the successor Gold. Prefer offline rescore when stored outputs suffice; define applicability before execution. |
| 9. Evaluator bug fix | No, unless it changes online product behavior | No for offline evaluation | Depends | Preserve the old verdict. Offline rescore first; a fresh run requires a preregistered reconciliation reason when stored outputs are insufficient or online inputs change. |
| 10. Receipt/finalization infrastructure-only fix | No | No | No | May recover an incomplete run under its exact identity; does not reset a terminal lineage. |
| 11. Documentation-only change | No | No | No | Record provenance only; no fresh formal attempt. |
| 12. Test-only change | No | No | No | Verification evidence only. If it accompanies a real production change, classify that production change separately. |

## Model identity

An explicitly configured generation or verification model name/version change
can constitute a material candidate change when it is reproducibly bound and
independently justified. A reproducible provider serving revision may also
qualify when it is observable, freezeable, and behavior-relevant.

Invisible provider-side updates, sampling variation, or different outputs under
the same frozen model identity do not silently create a new lineage. They remain
stochastic variation within the existing candidate.

## Gold and evaluator successors

Historical attempts remain bound to their original Gold, calibration, selector,
thresholds, and evaluator authority. A successor contract never retroactively
converts a historical FAIL into PASS.

When a forward-only Gold or evaluator correction is applicable to an old
candidate:

1. preserve the historical result;
2. use an offline rescore with new provenance when stored outputs contain all
   required information;
3. label any necessary fresh calls as contract-reconciliation evaluation, not a
   new product-candidate attempt;
4. preregister applicability, identities, cohort, and decision semantics before
   execution;
5. do not use the reconciliation path to obtain another stochastic draw when
   stored outputs were sufficient.

## Predeclared replicate blocks

A future candidate may use a replicate design only if a separate protocol is
scientifically justified and completed before replicate 1. It must freeze the
candidate/product lineage, Gold, calibration, selector, models, prompts,
thresholds, fixed replicate count or deterministic pre-outcome count-selection
rule, run identities, completion rule, aggregate decision rule, infrastructure
failure treatment, usage accounting, and no-peeking rule.

All scheduled replicates must be preregistered before the first call. No product,
prompt, threshold, Gold, or evaluator edit is permitted inside the block; no
selective rerun or unfavorable-result removal is permitted. Retryable
infrastructure failures may be recovered under the exact scheduled run identity
with all attempt usage retained. Zero-tolerance hard gates may not be weakened
merely to permit replication.

`REPLICATE_PROTOCOL_STATUS = NOT_ESTABLISHED`

## Current lineage decision

- Product-behavior lineage HEAD:
  `d3a1b274b2784399a7dc51b094a17e466d208b50`
- Attempt 4 is terminal `COMPLETE / FAIL /
  EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED`.
- Post-A4 changes repaired gate bootstrap and stage-receipt metadata only.
- No material product-behavior change has been accepted.
- Attempt-4 case-level outcomes have already been inspected, so a replicate
  block cannot be introduced retroactively for this lineage.

`EXECUTION_INFRASTRUCTURE_READY = true`

`FORMAL_REPEAT_SCIENTIFICALLY_ELIGIBLE = false`

`ATTEMPT_5_ELIGIBILITY = NOT_ELIGIBLE`

The next formal F6-A attempt requires a materially new product candidate or a
separately governed forward-only contract-reconciliation evaluation whose need
cannot be satisfied by offline rescore. No product change should be manufactured
merely to regain eligibility.

## Protected state and accounting

- `PANDA scientific/evaluation calls = 0`
- `PANDA scientific/evaluation tokens = 0`
- `novel_validation = PRISTINE_FOR_CURRENT_LINEAGE`
- `holdout access = 0`
- `protected-content leakage = 0`
- `F6-B execution = 0`
- `candidate frozen = false`
- `Attempt 5 preregistered = false`
- `Attempt 5 executed = false`
