# F6-A2-GR1-R2 — Doxygen-Stub Evidence-Selector Audit

Audit artifact (created and committed BEFORE any benchmark mutation).
Companion JSON: `evaluation/f6_a2_gr1_r2_doxygen_stub_selector_audit.json`.

```text
PANDA scientific/evaluation calls = 0
PANDA scientific/evaluation tokens = 0
```

## 1. Starting state

Starting HEAD `deab588872fb39a8db8b300beb76e7c7881a007d`
("Create Gold v2.8 forward-only successor"); worktree clean.

## 2. Audit universe (mechanically derived, not copied from prose)

Derived as the set-difference of `source_id=pandaroot, path=docs/…` selectors
between the v2.6 and v2.7 Gold datasets: **22 (case, group, path) triples
over 11 unique paths**. One of them — `docs/EventGenerators/DPMGenerator.rst`
(g016.e1) — was already retired forward-only by GR1-R1 in v2.8 and is outside
the inherited v2.8 universe; it is recorded as background only. The v2.8
inherited audit universe is therefore **21 triples over 10 unique paths**.

## 3. Classification methodology

Every underlying repository file was read in full from the frozen source
snapshot; sizes recorded; include/toctree targets traced and checked against
the indexed corpus (`knowledge_objects`, `source_id=pandaroot`). Classes per
the authorized contract:

- **A. CONTENT_BEARING_DOCUMENT** — the file itself carries substantive
  documentation for the Gold role.
- **B. INCLUDE_AGGREGATOR_WITH_CLOSED_CORPUS_TARGETS** — limited own text,
  but explicit include/toctree targets inside the frozen indexed corpus that
  jointly close the documentation-content chain for the rendered role.
- **C. DOXYGEN_OR_EMPTY_POINTER_STUB** — a pointer whose substantive rendered
  content is generated from code annotations; build lineage alone is
  insufficient.

The independent evidence rule applied to every selector: *can this object —
itself or through a closed in-corpus include chain — provide the evidence
needed by this exact Gold group role?* Attempt-2 outcomes, hypothetical
scores, and filename similarity were not used.

## 4. Classification results

### CONTENT_BEARING_DOCUMENT (class A) — KEEP

| path | size | used by |
| ---- | ---- | ------- |
| docs/Installation/Install_Developers.rst | 6,029 B | g001.installation, g011.e1 |
| docs/Installation/Install_PandaRoot.rst | 5,886 B | g001.installation, g008.e2, g011.e1 |
| docs/Running/MasterTasks.rst | 10,878 B | g013.e1 |
| docs/Running/Running_Sequence.rst | 1,746 B | g014.e2 |
| docs/Tutorials/tut_02_02_analysis_pid.rst | 9,838 B | g022.e2 |

### INCLUDE_AGGREGATOR_WITH_CLOSED_CORPUS_TARGETS (class B) — KEEP

| path | size | targets | used by |
| ---- | ---- | ------- | ------- |
| docs/Installation/Installation.rst | 523 B | toctree: Install_PandaRoot, Install_Developers, Install_GSI, Troubleshooting, CVMFS, Building_Documentation, Building_ExternalPackage — all inside docs/Installation/ in the corpus | g001.installation |
| docs/Running/Macros.rst | 331 B | `.. include:: macro/macro.rst`, `macro/master/Readme.md`, `macro/master/mastermacros.rst`, `macro/run/runmacros.rst` — **all four verified IN CORPUS** | g013.e1 |
| docs/Running/Running.rst | 4,069 B | toctree: Running_Sequence, MasterTasks, Logging — inside docs/Running/; plus own substantive overview text | g014.e2, g101.e1, g109.e1 |
| docs/Tools/PndMasterTasks/PndMasterTasks.rst | 709 B | own substantive introduction (master tasks = default task set for simulation, digitization, reconstruction, pid) + toctree of the PndMasterTasks pages inside the corpus | g014.e2, g101.e3, g106.e1 |

The g013 special care (§9) is satisfied: `g013.e1` keeps
`docs/Running/Macros.rst` (closed include chain — its targets include exactly
the `macro/master/mastermacros.rst` content the Attempt-2 answer cited) and
`docs/Running/MasterTasks.rst` (content-bearing); only the doxygen stub is
removed.

### DOXYGEN_OR_EMPTY_POINTER_STUB (class C) — REMOVE_FORWARD_ONLY

| path | size | content | used by |
| ---- | ---- | ------- | ------- |
| docs/Tools/PndMasterTasks/PndMasterRunSim.rst | 105 B | header + `.. doxygenclass:: PndMasterRunSim` only; rendered content generated from code annotations | g013.e1, g013.e2, g015.e1, g016.e2, g089.e1 |

It cannot independently satisfy any group role: a 105-byte pointer carries no
documentation substance, and the rendered page's content lives in the class
code annotations. The affected groups retain their original sphinx selectors,
their actual code selectors (`tools/MasterTasks/PndMasterRunSim.h` /
`.cxx` in g013.e2 / g016.e2), README/documentation selectors, and — for
g013.e1 — the two valid repo-documentation selectors above. No group becomes
empty and no legitimate coverage is weakened.

Background (already retired, outside this audit's universe):
`docs/EventGenerators/DPMGenerator.rst` (96-byte doxygen stub, g016.e1) was
removed forward-only by GR1-R1 in v2.8.

## 5. Candidate-outcome independence

Every classification rests on file content, size, and in-corpus target
closure — facts that hold regardless of any candidate's answers. The single
removal is justified identically to the GR1-R1 DPMGenerator rejection; no
selector is retired because a candidate failed, and none is kept because a
candidate passed.

## 6. Governance decision

Exactly one invalid selector remains in v2.8
(`docs/Tools/PndMasterTasks/PndMasterRunSim.rst`, 5 groups) → a forward-only
successor **m6-benchmark-v2.9** is authorized, derived directly from v2.8,
removing only that selector from the five affected groups and changing
nothing else. No new selectors are added; no question text, expected status,
answer point, criticality, source obligation, threshold, or evaluator
semantics change.
