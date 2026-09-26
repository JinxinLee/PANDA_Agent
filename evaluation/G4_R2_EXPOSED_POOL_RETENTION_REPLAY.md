# G4 R2 Exposed Offline Pool-Retention Replay

## Scope and method

This is a non-gating exposed diagnostic over only `n002`, `n006`, and `n017` from the frozen G3 run. It was executed after the generic R2 rule and deterministic controls were fixed. `python -m evaluation.g4_r2_offline_pool_replay` reconstructs the channel rankings and plan from each saved retrieval trace, invokes the current production global consolidation/pool constructor with a no-op final selector and no model client, and compares the result with the historical trace's fused top-30 IDs. Each case has one recorded initial retrieval and zero targeted retrievals. No structured-supplement receipt is present in these traces, so the reconstruction supplies an empty supplemental list.

The saved traces retain candidate identity, source/version, locator, object type, and channel rank, but omit candidate title/text and workflow/graph branch-origin bits. The helper supplies a non-ranking placeholder title/text solely for the current payload-presence check. Specialized occurrences without origin bits cannot claim frontier preference. The five reviewed targets all came from the ordinary dense channel, so this limitation does not affect their frontier eligibility. The replay does not re-query storage or invoke a reranker.

| Case | Previously lost object | Historical best rank | Old fused top 30 | New offered pool | Entry reason |
|---|---|---:|---|---|---|
| n002 | `object.a45779701b982aff3e7554da` | dense 7 | no | yes | `policy_role_frontier` |
| n002 | `object.03af96b1110e782792253a18` | dense 8 | no | yes | `policy_role_frontier` |
| n006 | `object.2914485ff398f61e994c46d6` | dense 9 | no | yes | `policy_role_frontier` |
| n017 | `object.015bff352e03a5f5ee88c307` | dense 7 | no | yes | `policy_role_frontier` |
| n017 | `object.10bfbd3c5c5a222bcdf5904d` | dense 8 | no | yes | `policy_role_frontier` |

`REPLAY_COMPATIBILITY = PARTIAL`: single-pass channel/plan metadata and the historical fused pool are available; full canonical text/title, explicit supplemental eligibility, and specialized origin bits are not persisted. The observed result establishes only new deterministic **offered-pool** membership for these exposed objects under the available frozen metadata. Historical reranker output cannot rank objects it never saw. No final selection, answer, QA status, independent generalization, or empirical false-insufficiency benefit is inferred. No implementation parameter was changed after this replay.
