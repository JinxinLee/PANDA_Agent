# E1-R2 — Prospective Cohort Human Review

Status: DRAFT_PENDING_HUMAN_REVIEW. No scientific model outputs exist.

These newly authored English questions are synthetic exploratory reconstruction/software needs, not factual assertions about available PANDA implementations. They are not protected or representative novel data. They were authored after the E1-R1 implementation commit; no runtime repair may use their outcomes. Review all questions, equivalent paraphrases, reference granularity and domain relevance before live acceptance. Reference needs are not answer facts. Reordered paraphrases intentionally test semantic slots rather than literal IDs.

Human reviewer: pending. Review of this document approves the exact manifest questions and references only when explicitly recorded; automated review does not count as human approval.

## r2p01 — independent_locations (2 obligations)

Base: In the reconstruction code, which file defines the track seed builder, and which file defines the hit filter?

Paraphrase: Identify the source file for the hit filter as well as the source file for the track seed builder.

Reference obligations:

1. Locate the track seed builder definition.
2. Locate the hit filter definition.

## r2p02 — independent_locations (2 obligations)

Base: For the geometry loader and the calibration reader, give their respective implementation entry points.

Paraphrase: Name the implementation entry point of the calibration reader; also name the entry point of the geometry loader.

Reference obligations:

1. Identify the geometry loader implementation entry point.
2. Identify the calibration reader implementation entry point.

## r2p03 — independent_contributions (2 obligations)

Base: What role does the residual calculator play in the fit, and what role does the outlier mask play?

Paraphrase: Explain the outlier mask's contribution to the fit and the residual calculator's contribution.

Reference obligations:

1. Explain the residual calculator's contribution to the fit.
2. Explain the outlier mask's contribution to the fit.

## r2p04 — independent_contributions (2 obligations)

Base: Explain the separate contributions of the alignment constants and the timing offsets to event reconstruction.

Paraphrase: In reconstructing an event, what is contributed by the timing offsets? What is contributed by the alignment constants?

Reference obligations:

1. Explain the alignment constants' contribution to event reconstruction.
2. Explain the timing offsets' contribution to event reconstruction.

## r2p05 — single_comparison (1 obligations)

Base: How does a weighted track fit differ from an unweighted track fit?

Paraphrase: Compare weighted and unweighted track fitting.

Reference obligations:

1. Compare weighted and unweighted track fitting.

## r2p06 — single_comparison (1 obligations)

Base: Contrast the failure behavior of a strict configuration parser with that of a permissive parser.

Paraphrase: What differences in failure behavior distinguish strict and permissive configuration parsing?

Reference obligations:

1. Compare strict and permissive configuration parsing failure behavior.

## r2p07 — single_flow (1 obligations)

Base: Describe the path of an event record from the input reader to the output writer.

Paraphrase: How does an event record travel from the input reader through to the output writer?

Reference obligations:

1. Describe event-record flow from input reader to output writer.

## r2p08 — single_flow (1 obligations)

Base: How are detector coordinates transformed into the coordinate system used by the track fit?

Paraphrase: Explain the transformation from detector coordinates to the track fit's coordinate system.

Reference obligations:

1. Explain coordinate transformation from detector space to track-fit space.

## r2p09 — mixed_three (3 obligations)

Base: What does a fit residual mean, how is it different from a pull, and where is the residual calculation implemented?

Paraphrase: Locate the residual calculation, define a fit residual, and compare a residual with a pull.

Reference obligations:

1. Define a fit residual.
2. Compare a fit residual with a pull.
3. Locate the residual calculation implementation.

## r2p10 — mixed_three (3 obligations)

Base: Which component reads the run configuration, what happens when a required field is absent, and why are defaults disallowed for that field?

Paraphrase: Explain why that required configuration field cannot use a default, identify the component reading the run configuration, and describe the behavior if the field is missing.

Reference obligations:

1. Identify the component reading the run configuration.
2. Describe behavior when a required configuration field is absent.
3. Explain why defaults are disallowed for the required field.

## r2p11 — four_obligations (4 obligations)

Base: Define an event time window, state its unit, identify the component that applies it, and explain why its upper boundary is excluded.

Paraphrase: For an event time window, explain the exclusion of the upper boundary, name the component applying the window, give the unit, and provide a definition.

Reference obligations:

1. Define an event time window.
2. State the event time window unit.
3. Identify the component applying the event time window.
4. Explain the event time window's excluded upper boundary.

## r2p12 — five_obligations (5 obligations)

Base: For the hit cache, give its purpose, the key format, the eviction condition, the behavior on a miss, and the location of its implementation.

Paraphrase: Where is the hit cache implemented, what happens on a cache miss, when are entries evicted, how is a key structured, and what purpose does the cache serve?

Reference obligations:

1. Explain the hit cache purpose.
2. Describe the hit cache key format.
3. State the hit cache eviction condition.
4. Describe hit cache miss behavior.
5. Locate the hit cache implementation.


