# F6-A2-GR1 — Forward-Only Gold Contract Adjudication

Decision: **adjudication complete; forward-only corrections accepted for 13
cases; successor benchmark v2.7 authorized.** Companion JSON:
`evaluation/f6_a2_gr1_forward_only_gold_contract_adjudication.json`.

```text
PANDA scientific/evaluation calls = 0
PANDA scientific/evaluation tokens = 0
```

## 1. Governing principle applied

Every disposition answers: *would this correction still be justified if
Attempt 2 had never produced its particular answer?* Corrections rest on
deterministic evidence (document lineage, content overlap, question
entailment), never on the candidate's outcome. Attempt-2 FAIL under v2.6 is
immutable; v2.7 is a forward-only successor authority.

## 2. Established equivalence rule (deterministic evidence)

The locked sphinx web snapshot and the frozen PandaRoot repository carry the
same documentation in two representations with a mechanical whole-tree
mapping:

```text
pandaroot_sphinx_2023_08_25_dev/raw/~pandacc/documentation/2023-08-25-dev/sphinx/<Section>/<Page>.html
↔ docs/<Section>/<Page>.rst   (source_id pandaroot)
```

Evidence (not filename similarity alone):

- path structure is isomorphic across the verified sections
  (Installation/, Docker/, Running/, Tools/PndMasterTasks/,
  EventGenerators/, Tutorials/);
- content verification for `Install_PandaRoot` (sphinx 12 objects / 31,754
  chars vs repo 55 objects / 11,213 chars): 308 of 357 repo word types (86%)
  occur in the sphinx page; 19 of 40 sampled repo sentences occur verbatim;
  the key installation content (SIMPATH, FAIRROOTPATH, cmake, make install)
  is present in both; divergence is rst markup vs rendered-page boilerplate;
- `Running.html` renders the docs/Running/ toctree (its own contents list
  Running Sequence / Event Generator / Transport / Digitizer /
  Reconstruction / MasterTasks / …) whose section sources are the repo
  rst files, including `Running_Sequence.rst` for the "Running Sequence"
  section;
- both sides sit in the same 2023-08-25-dev documentation generation.

Consequence: a group that accepts only the rendered sphinx form while
rejecting the same documentation's repository source form is narrower than
its own evidential role requires; the rendered/repo distinction is not
entailed by any reviewed query.

## 3. Case decisions

### g001 — evidence contract: BROADEN_SEMANTICALLY_EQUIVALENT_EVIDENCE (accepted)

- Current: `g001.installation` accepts only sphinx titles
  "Installation —" / "Installation of PandaRoot for Developers".
- Finding: the answer need ("How do I install the locked PandaRoot
  development snapshot?") is documentation-need, not representation-need.
  Repository `docs/Installation/Installation.rst`, `Install_Developers.rst`,
  `Install_PandaRoot.rst` carry the same documentation (verified lineage and
  content above).
- Change: add repo source-path selectors; sphinx selectors preserved.

### g001 — p1: REVISE_ANSWER_POINT_SCOPE (accepted)

- Current critical point: "Use the locked 2023-dev installation
  documentation and state that repository behavior is commit-specific."
- Finding: the commit-specificity statement is not entailed by "How do I
  install the locked PandaRoot development snapshot?" — a complete
  installation answer does not require it; it is author elaboration.
- Change: reword to "Use the locked 2023-dev installation documentation
  (rendered pages or their repository source files) to describe how to
  install the development snapshot."; criticality retained (documented
  installation guidance is the core of the query).

### g005 — p1: REVISE_ANSWER_POINT_SCOPE (accepted)

- Current critical point: "Distinguish developing inside the container from
  merely running an image."
- Finding: the authoritative documentation
  (`docs/Docker/DevelopingInContainer.rst` / its rendered page — the
  g005.e1 target) contains no such contrast. Its sections are TL;DR / Why? /
  How? / Detailed Steps / Remote Containers / Make / Extensions / Drawbacks /
  SSH access; no "merely running an image" contrast exists anywhere in the
  6,153-character document, and the query asks how a developer environment
  is used, not for a usage contrast. The point as written cannot be answered
  from the required evidence at all.
- Change: reword to "Describe how PandaRoot development is performed inside
  the documented Docker container workflow."; criticality retained.

### g011 — evidence contract: BROADEN_SEMANTICALLY_EQUIVALENT_EVIDENCE (accepted)

- Same rule as g001: add `docs/Installation/Install_PandaRoot.rst` and
  `docs/Installation/Install_Developers.rst` as selectors. The
  native-vs-container two-path semantic requirement is untouched (it is
  question-entailed: the query explicitly asks for both paths
  "in the locked documentation").

### g014 — g014.e2: BROADEN_SEMANTICALLY_EQUIVALENT_EVIDENCE (accepted)

- Current selectors: sphinx `Tools/PndMasterTasks/PndMasterTasks.html`
  (section) and `Running/Running.html`.
- Finding: `docs/Tools/PndMasterTasks/PndMasterTasks.rst`,
  `docs/Running/Running.rst`, and `docs/Running/Running_Sequence.rst` are
  the same documentation's source forms; `Running_Sequence.rst` is the
  direct source of the sphinx page's "Running Sequence" section — the exact
  content the query ("simulation-to-analysis sequence") targets.
- Change: add the three repo source-path selectors; sphinx selectors
  preserved.

### g044 — g044.e1: KEEP_AS_IS (decided; no change)

- The group deliberately anchors the theory role to pflueger_2017 pages
  57/58/62; `required_source_types = ['paper']` and p1 ("using the thesis,
  not source-code inference") are carried by any paper, but the evidence
  group intentionally tests the specific theoretical source. li_2026's
  semantic equivalence for this role is not established (no corresponding
  theory passage was located; its angular-acceptance material sits in
  different chapters with different framing). The only direct motivation to
  broaden would be Attempt-2's answer choice — prohibited as a rationale.
- Attempt-2's g044 failure is therefore attributed to the product dropping
  an already-selected satisfying object (FR1), not to the contract.

### Consistency sweep results (§16)

Mechanical scan of all 120 cases for the same pattern
(sphinx-form-only selector where the isomorphic repo rst exists):

- path-form pattern: 12 case-group pairs, including the adjudicated ones.
  Additional affected groups beyond the five primary cases:
  g008.e2, g013.e1, g013.e2, g015.e1, g016.e2, g089.e1, g101.e1, g101.e3,
  g106.e1, g109.e1 → same correction applied in v2.7 (additive only).
- title-form groups without demonstrated failure (g002.e1, g003.e1,
  g004.e1, g005.e1, g006.e1, g007.e1, g008.e1, g009.e1, g010.e1, g011.e2,
  g012.e1, g014.e1, g022.e1, g023.e1/e2, g024.e1, g094.e1, g101.e2):
  KEEP_AS_IS — extending them all would exceed the bounded sweep and
  redesign the benchmark; they are recorded here for any future
  comprehensive contract review.

## 4. Accepted forward-only change set

- Evidence-group extensions (additive; original selectors preserved):
  g001.installation, g008.e2, g011.e1, g013.e1, g013.e2, g014.e2, g015.e1,
  g016.e1, g016.e2, g022.e2, g089.e1, g101.e1, g101.e3, g106.e1, g109.e1.
- Answer-point rewording: g001 p1, g005 p1 (criticality retained).
- Changed cases: g001, g005, g008, g011, g013, g014, g015, g016, g022,
  g089, g101, g106, g109 (13).
- Everything else: preserved byte-exact from v2.6.
- No expected_status change, no threshold change, no evaluator change, no
  gate-semantics change, no Gold question text change.

## 5. Candidate-outcome independence

The equivalence rule rests on deterministic document lineage and content
facts that hold regardless of any candidate's answers. The two
answer-point rewordings rest on question entailment (neither the
commit-specificity statement nor the container-usage contrast is required
by its query, and the g005 contrast is absent from the required evidence
itself). g044/g060 source locks are retained despite candidate benefit,
demonstrating the firewall works in both directions.
