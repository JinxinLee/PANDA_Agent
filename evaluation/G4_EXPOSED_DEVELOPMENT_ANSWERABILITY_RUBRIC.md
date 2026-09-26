# G4 Exposed Development Answerability Rubric

## Integrity checkpoint and selection

Freeze this rubric before opening case-level questions, Gold annotations,
locked-source evidence, or production traces. The fixed primary IDs are
`n001`, `n002`, `n006`, `n010`, `n017`, and `n019`. Selection is
`EXPOSED / OUTCOME-CONDITIONED DEVELOPMENT DIAGNOSTIC`: all six are already
known to have returned `insufficient_evidence`. The reviewer is not blind to
this selection fact. No case-specific answerability judgment is made here.

Apply the same current locked corpus, source-version universe, and
`production_answer_obligations_v1` contract to every case. Record exactly one
high-level answerability state: `ANSWERABLE`, `UNANSWERABLE`, or `UNKNOWN`.
Reasons and per-obligation findings are fields, not additional verdict states.
Freeze the independent answerability record before consulting each case's
production trace for causal attribution.

## Independent answerability states

`ANSWERABLE` requires independent proof of **all** of the following:

1. The question is within the supported English PANDA product scope.
2. The intended mandatory answer points and required relations are valid,
   reconstructed from the question rather than copied from production
   decomposition.
3. Current locked authoritative corpus evidence sufficiently supports every
   mandatory point and relation.
4. Every required source is compatible with the requested version and the
   locked source identity.
5. Each required support chain has exact, citation-safe and
   admission-compatible provenance under the current contract.
6. A complete supported answer is possible while preserving G1 point and
   relation completeness, G2 local validity, G3 admission, claim support,
   correct abstention, and version safety.

For each mandatory obligation, record the independently verified source,
version, locator, support status, and citation/admission compatibility.
Gold `expected_status=answered`, a plausible remembered answer, or a
production-selected item alone proves none of these conditions.

`UNANSWERABLE` requires authoritative proof that at least one mandatory
condition cannot be met under this locked corpus and contract. Examples are
established corpus absence, an unsupported required relation, only unsafe
provenance, a source-version conflict, an unavailable future runtime fact, an
unsupported universal proof, or an out-of-scope request. A failed production
retrieval or verifier rejection is not proof of corpus absence.

`UNKNOWN` applies when neither conclusion is sufficiently established.
Record the missing proof, such as uncertain corpus-search completeness,
ambiguous obligation meaning, incomplete Gold/provenance, uncertain
source/version identity, or conflicting authoritative evidence. Do not force
an answerability verdict or silently treat `UNKNOWN` as `UNANSWERABLE`.

## Evidence authority and review sequence

Use this authority order for exposed development cases:

1. Human-reviewed Gold obligations and evidence, independently rechecked
   against the current locked source and version.
2. Direct locked-corpus inspection with exact source and locator provenance.
3. Deterministic source, code, or document search only as a discovery aid;
   verify any resulting assertion directly under item 2.
4. Production retrieved or selected evidence only as a later diagnostic
   observation, never as independent answerability authority.

Production QA status, answer text, decomposition, verifier disposition,
retrieval ranking, and model-generated claims have no independent
answerability authority. Gold wording is a measurement annotation, not a
product implementation specification.

For each fixed ID, read the question, reconstruct mandatory obligations,
inspect Gold, verify every material assertion against the locked corpus,
check scope/version/provenance, and save a separate answerability record.
Document exposure, reviewer and time, Gold/source references, per-obligation
support and uncertainty. Only after the answerability record is fixed may
the production outcome and compatible same-run traces be joined. If a
consequential ambiguity cannot be resolved without a genuinely independent
reviewer, use `UNKNOWN`; do not simulate a second review.

## Later diagnostic boundary

`ANSWERABLE + insufficient_evidence` is only a
`FALSE_INSUFFICIENCY_CANDIDATE`. Causal attribution needs compatible same-run
artifacts, the earliest necessary wrong transition, and exclusion of earlier
competing causes. `UNANSWERABLE + insufficient_evidence` requires a check of
whether the abstention accords with the independent reason. `UNKNOWN` stays
outside answerable and unanswerable denominators. The six selected outcomes
cannot estimate false-insufficiency prevalence in `novel_dev`.

Preserve the opposing G4 T0 safety contract: correct abstention, complete
required points and relations, supported claims, safe citations/provenance,
and version safety. Do not convert case wording, identifiers, symbols, or
source locations into product logic. This rubric authorizes no QA/retrieval
rerun, model call, new data curation, product repair, or protected-data access.
