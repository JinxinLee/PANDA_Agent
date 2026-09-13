# F6-A2-GR1-R1 — Gold Successor Provenance Reconciliation

Decision: **F6-A2-GR1-R1 = COMPLETE / PASS / UNJUSTIFIED_V2_7_DELTA_RETIRED_FORWARD_ONLY.**

g016.e1 disposition: **REJECT_UNJUSTIFIED_V2_7_DELTA** → forward-only successor
**m6-benchmark-v2.8** created; v2.7 becomes a historical provisional successor;
v2.8 is the stabilized forward-only Gold authority for future attempts.

```text
PANDA scientific/evaluation calls = 0
PANDA scientific/evaluation tokens = 0
```

## 1. Starting state

Starting HEAD `9c9593eccefa6db9eb600f248d70aeff3213607f`
("Record Gold contract adjudication closeout"); worktree clean. The original
GR1 adjudication commit history and v2.7 creation commit history are untouched
and remain historical evidence.

## 2. Original inconsistency (why this task exists)

1. **g016.e1** was included in the v2.7 accepted change set, but it is a
   **title-form** group (`source_id = pandaroot_sphinx_2023_08_25_dev`,
   `title_contains = "DPMGenerator"`) — neither one of the five primary
   adjudication targets nor one of the documented path-form sweep pairs, and
   therefore never received the independent adjudication the GR1 rule
   requires before entering the change set.
2. **g022.e2** is a valid path-form pair
   (`sphinx/Tutorials/tut_02_02_analysis_pid.html` ↔
   `docs/Tutorials/tut_02_02_analysis_pid.rst`) but was omitted from the
   textual consistency-sweep enumeration in the GR1 artifact.

## 3. g016.e1 independent adjudication

Deterministic evidence:

- **Repo identity**: `docs/EventGenerators/DPMGenerator.rst` in the frozen
  pandaroot snapshot is a **96-byte doxygen stub** — exactly:

  ```rst
  DPMGenerator
  ============
  .. doxygenclass:: PndDpmDirect
      :members:
      :undoc-members:
  ```

  Its three indexed objects total 165 characters / 7 word types; no sentence
  content. It carries no DPM documentation substance.
- **Sphinx identity**: the rendered page
  `EventGenerators/DPMGenerator.html` (3,596 characters across 3 objects) is
  the doxygen API rendering of class `PndDpmDirect` ("The PndDpmDirect
  generates DPM event using the DPM fortran code and inserts the tracks into
  the PndStack via the FairPrimaryGenerator. Derived from FairGenerator…")
  — its content is generated from the **code annotations**, not from the
  rst file. The build lineage (stub → rendered API page) is real, but the
  stub itself is not a content-bearing equivalent of the page.
- **Role check**: the group role `dpmgenerator_documentation` requires
  documentation substance; a 96-byte pointer cannot serve as evidence for
  that role.
- **Candidate-outcome-independence test**: *Would we add
  `docs/EventGenerators/DPMGenerator.rst` if Attempt 2 had never produced a
  g016 failure?* No — the GR1 equivalence rule requires "materially
  equivalent content for the required evidence role", and this stub fails
  that requirement on its face; the only motivation to add it was the
  mechanical application of the path-isomorphism rule to a title-form group
  plus the Attempt-2 outcome. The contrast with the accepted extensions is
  sharp: `Install_PandaRoot.rst` (5,886 bytes) / `Install_Developers.rst`
  (6,029 bytes) / `tut_02_02_analysis_pid.rst` (9,838 bytes) are
  content-bearing documents with verified overlap against their rendered
  pages.

**Disposition: REJECT_UNJUSTIFIED_V2_7_DELTA** (not forced to acceptance to
avoid creating v2.8 — the evidence decides).

## 4. Path-form consistency sweep — exact reconciled set

Reconstructed deterministically from v2.6 (groups whose sphinx selectors use
explicit rendered-page paths), matching the expected structure exactly —
**12 path-form case-group pairs**:

```text
primary path-form adjudicated group:
  g014.e2                       (Tools/PndMasterTasks/PndMasterTasks.html, Running/Running.html)
additional path-form groups:
  g008.e2                       (Installation/Install_PandaRoot.html)
  g013.e1                       (Running/Macros.html, Running/MasterTasks.html, Tools/PndMasterTasks/PndMasterRunSim.html)
  g013.e2                       (Tools/PndMasterTasks/PndMasterRunSim.html)
  g015.e1                       (Tools/PndMasterTasks/PndMasterRunSim.html)
  g016.e2                       (Tools/PndMasterTasks/PndMasterRunSim.html)
  g022.e2                       (Tutorials/tut_02_02_analysis_pid.html)
  g089.e1                       (Tools/PndMasterTasks/PndMasterRunSim.html)
  g101.e1                       (Running/Running.html)
  g101.e3                       (Tools/PndMasterTasks/PndMasterTasks.html)
  g106.e1                       (Tools/PndMasterTasks/PndMasterTasks.html)
  g109.e1                       (Running/Running.html)
```

**g022.e2 is confirmed part of the original bounded path-form sweep**; the
omission was bookkeeping-only (its v2.7 extension —
`docs/Tutorials/tut_02_02_analysis_pid.rst`, 9,838 bytes of substantive
tutorial documentation — is independently valid under the equivalence rule
and is retained).

`g016.e1` is **not** a path-form sweep correction; after this reconciliation
it is recorded separately as an **independently adjudicated title-form
source-equivalence case with a rejected delta**.

## 5. Deterministic validation finding recorded (outside this task's authority)

While validating the v2.7 additions, one additional stub was identified:
`docs/Tools/PndMasterTasks/PndMasterRunSim.rst` is a **105-byte doxygen
stub** (`.. doxygenclass:: PndMasterRunSim`) added by the v2.7 path-form
sweep to g013.e1, g013.e2, g015.e1, g016.e2, and g089.e1. Its retirement is
**outside the GR1-R1 authorization** (which covers g016.e1 only) and is
recorded verbatim in the v2.8 change report as an open finding for the next
benchmark-governance task. By contrast, `docs/Running/Macros.rst` (added to
g013.e1) is an include-aggregation stub whose targets
(`macro/master/mastermacros.rst` and friends) live inside the indexed corpus,
so its content-equivalence chain closes within the corpus; it is retained.

## 6. Benchmark authority after reconciliation

```text
v2.6 = historical authority for Attempts 1 and 2 (byte-unchanged)
v2.7 = historical provisional successor; NOT used for any scientific release attempt
v2.8 = STABILIZED_FORWARD_ONLY_GOLD_AUTHORITY_FOR_FUTURE_ATTEMPTS
       evaluation/benchmarks/v2_8/ (derived from v2.7; the only governance
       repair is the removal of the unjustified g016.e1 repo-source selector;
       every other accepted v2.7 change preserved)
       dataset_sha256 = 67c992ce9556995ae01efc17e72038a477a341b621d0ebf590e6f42f2eff34eb
       base = v2.7 (4dcc9d066a275269d01b094aefa69b4e7794f18ad6a6dfce4d88d94ad3977b56)
       changed cases = [g016] only; patch + change report + manifest created
```

## 7. Calibration and selector

```text
phase_b_t3_product_language_scope_v5 (mechanical carry-forward from v4,
  bound to the v2.8 dataset SHA; predecessor v4 recorded; no fresh human
  language review claimed) — authoritative
compatibility: verified (version + file SHA + split + overrides + declared/derived ID equality)
formal-English selector: 59 IDs, sha256 e27ef67a866274b4a8441b789ca78fc3ccb7e022eed537c7442e15230777a0e5,
  membership identical to v3/v4 (derived, not assumed)
```

## 8. Historical attempt integrity

```text
Attempt 1 remains evaluated against v2.6
Attempt 2 remains evaluated against v2.6
Attempt-2 FAIL unchanged (COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED)
no retroactive rescoring; no hypothetical v2.7/v2.8 scores computed
```

## 9. Integrity

```text
PANDA scientific/evaluation calls = 0
PANDA scientific/evaluation tokens = 0
product behavior changes = 0
evaluator behavior changes = 0
novel_validation = PRISTINE_FOR_CURRENT_LINEAGE
holdout access = 0
protected-content leakage = 0
```

## 10. Next action

```text
NEXT_TASK_RECOMMENDATION =
F6-A2-FR2 / BOUNDED PRODUCT REPAIR AND NEW CANDIDATE DEVELOPMENT
(product repair must use v2.8 as the stabilized Gold authority; the
PndMasterRunSim.rst stub finding should be taken up by the next
benchmark-governance task)
NEXT_TASK_EXECUTION_AUTHORIZED = false
```
