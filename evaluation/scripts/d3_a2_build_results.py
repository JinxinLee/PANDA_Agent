"""Build the frozen D3-A2 result artifact from immutable runner records.

Metric tables are recomputed deterministically from ``records.jsonl`` (the
frozen evaluator semantics already applied per record); per-case/per-rule
mechanism attributions and decisions are authored inputs frozen here.  The
script performs internal consistency checks before writing the artifact.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

ARM_ORDER = ("LEGACY", "ABLATION", "STRUCTURED")
FROZEN_IMPLEMENTATION_SHA = "814a6183f8054e95f65452fc2a5ac4300a6082f5"
PREREGISTRATION_SHA = "b4adfbdc21c0fd959a26b96aad84fda5509329c96ad6083440594224a6dd7ca2"
RUN_ID = "d3_a2_frozen_20260831"

METRIC_LABELS = {
    "gold_recall_at_5": "Recall@5",
    "gold_recall_at_10": "Recall@10",
    "gold_recall_at_20": "Recall@20",
    "mrr": "MRR",
    "combined_candidate_recall": "combined candidate recall",
    "final_evidence_recall": "final evidence recall",
    "critical_final_evidence_recall": "critical evidence recall",
}

# Authored per-case mechanism analysis (D3-A2-R1 repaired interpretation).
# Layers are kept strictly separate:
#   failure_classification / secondary_failure_classifications: frozen D3-A0-R1
#     failure taxonomy values only (null when no frozen-taxonomy failure exists);
#   paired_outcome / dependency_interpretation: descriptive outcome layers;
#   diagnostic_subtype: interpretation-only refinement, not a taxonomy value.
CASE_ANALYSIS: dict[str, dict[str, Any]] = {
    "g029": {
        "primary_interpretation": "no legacy dependency observable (paraphrase case); all arms recover the required evidence; structured abstains correctly on the AMBIGUOUS PndLmdCombinedDataReader mention without collapsing it",
        "failure_classification": None,
        "secondary_failure_classifications": [],
        "paired_outcome": "STRUCTURED_PARITY",
        "dependency_interpretation": "NOT_ESTABLISHED",
        "diagnostic_subtype": None,
        "structured_candidate_contribution": False,
    },
    "n021": {
        "primary_interpretation": "no legacy dependency (paraphrase case); all arms miss the LuminosityFit orchestration group (preregistered preserved gap); structured contributes one neutral PandaRoot repository seed",
        "failure_classification": None,
        "secondary_failure_classifications": [],
        "paired_outcome": "STRUCTURED_PARITY",
        "dependency_interpretation": "NOT_ESTABLISHED",
        "diagnostic_subtype": None,
        "structured_candidate_contribution": True,
    },
    "g025": {
        "primary_interpretation": "negative control behaves identically in all arms; structured correctly abstains (runLmdFit mention stays AMBIGUOUS, no collapse, no injection)",
        "failure_classification": None,
        "secondary_failure_classifications": [],
        "paired_outcome": "STRUCTURED_PARITY",
        "dependency_interpretation": "NOT_ESTABLISHED",
        "diagnostic_subtype": None,
        "structured_candidate_contribution": False,
    },
    "g036": {
        "primary_interpretation": "legacy dependency confirmed: required macro/target/ana_dpm.C evidence enters only through the LEGACY exact channel (rule symbol payload macro/target/*.C) at fused rank 5, final rank 1; with the rule suppressed the macro file never enters any channel; STRUCTURED seeds data_product.restgas.event_poca, traverses the accepted relations around it, and injects four curated objects that rank very high (fused ranks 1-2), but the frozen A1 path materializes governed objects only and never converts relation-level evidence provenance into retrievable source candidates; the required selector (source_id restgas_determination, path macro/target/ana_dpm.C, object_type function/source_file) cannot be satisfied by any curated governed object",
        "failure_classification": "EVIDENCE_LINK_COVERAGE_GAP",
        "secondary_failure_classifications": ["LEGACY_DEPENDENCY_WITHOUT_STRUCTURED_RECOVERY"],
        "paired_outcome": "STRUCTURED_REGRESSION",
        "dependency_interpretation": "LEGACY_DEPENDENCY_CONFIRMED",
        "diagnostic_subtype": "EXISTING_PROVENANCE_NOT_MATERIALIZED",
        "structured_candidate_contribution": True,
    },
    "n022": {
        "primary_interpretation": "no legacy dependency (paraphrase case); all arms 2/3 groups; the e3 selected object differs between ABLATION and STRUCTURED (both objects match the group's any_of selectors) due to analyzer/reranker run variance, not structured contribution (zero seeds/injections for this case)",
        "failure_classification": None,
        "secondary_failure_classifications": [],
        "paired_outcome": "STRUCTURED_PARITY",
        "dependency_interpretation": "NOT_ESTABLISHED",
        "diagnostic_subtype": None,
        "structured_candidate_contribution": False,
    },
    "g020": {
        "primary_interpretation": "no legacy dependency (paraphrase case); all arms recover both required groups; structured abstains on the unresolved two-pass mention without negative filtering",
        "failure_classification": None,
        "secondary_failure_classifications": [],
        "paired_outcome": "STRUCTURED_PARITY",
        "dependency_interpretation": "NOT_ESTABLISHED",
        "diagnostic_subtype": None,
        "structured_candidate_contribution": False,
    },
    "n006": {
        "primary_interpretation": "nontrigger control stable across arms; structured injects one neutral PandaRoot repository seed; pre-existing e2 gap unchanged",
        "failure_classification": None,
        "secondary_failure_classifications": [],
        "paired_outcome": "STRUCTURED_PARITY",
        "dependency_interpretation": "NOT_ESTABLISHED",
        "diagnostic_subtype": None,
        "structured_candidate_contribution": True,
    },
    "g041": {
        "primary_interpretation": "negative control behaves identically in all arms; structured correctly abstains on the nonexistent SetMagicRestgasSeed mention; no injection, no false scope narrowing",
        "failure_classification": None,
        "secondary_failure_classifications": [],
        "paired_outcome": "STRUCTURED_PARITY",
        "dependency_interpretation": "NOT_ESTABLISHED",
        "diagnostic_subtype": None,
        "structured_candidate_contribution": False,
    },
    "n014": {
        "primary_interpretation": "LEGACY equals ABLATION on the direct literal case, so the model_factory_theory shortcut was not materially responsible for useful retrieval; structured injects the S-tier model_framework match but the model_framework definition group is missed in all arms (pre-existing recall gap unrelated to the rule)",
        "failure_classification": None,
        "secondary_failure_classifications": [],
        "paired_outcome": "STRUCTURED_PARITY",
        "dependency_interpretation": "NOT_MATERIALLY_USED",
        "diagnostic_subtype": None,
        "structured_candidate_contribution": True,
    },
    "g060": {
        "primary_interpretation": "no legacy dependency (paraphrase case); all arms recover all three groups; structured abstains on the unresolved beam-divergence mention",
        "failure_classification": None,
        "secondary_failure_classifications": [],
        "paired_outcome": "STRUCTURED_PARITY",
        "dependency_interpretation": "NOT_ESTABLISHED",
        "diagnostic_subtype": None,
        "structured_candidate_contribution": False,
    },
    "g052": {
        "primary_interpretation": "LEGACY equals ABLATION on the direct literal case (the question also literally triggers restgas_profile_workflow; both suppressed in ABLATION with no effect), so the effective_acceptance_pipeline shortcut was not materially responsible; structured abstains on both descriptive mentions without narrowing the distinction",
        "failure_classification": None,
        "secondary_failure_classifications": [],
        "paired_outcome": "STRUCTURED_PARITY",
        "dependency_interpretation": "NOT_MATERIALLY_USED",
        "diagnostic_subtype": None,
        "structured_candidate_contribution": False,
    },
    "g055": {
        "primary_interpretation": "distinction control stable across arms; structured abstains on both descriptive mentions; no over-expansion and no false ambiguity collapse",
        "failure_classification": None,
        "secondary_failure_classifications": [],
        "paired_outcome": "STRUCTURED_PARITY",
        "dependency_interpretation": "NOT_ESTABLISHED",
        "diagnostic_subtype": None,
        "structured_candidate_contribution": False,
    },
    "n003": {
        "primary_interpretation": "nontrigger control stable across arms; structured injects one neutral PandaRoot repository seed; pre-existing e2 gap unchanged",
        "failure_classification": None,
        "secondary_failure_classifications": [],
        "paired_outcome": "STRUCTURED_PARITY",
        "dependency_interpretation": "NOT_ESTABLISHED",
        "diagnostic_subtype": None,
        "structured_candidate_contribution": True,
    },
    "g021": {
        "primary_interpretation": "legacy dependency confirmed: required macro/target/prod_sim_hvmaps.C and pgenerators/Target/PndTargetGenerator.cxx evidence enters only through the LEGACY exact channel (rule symbol payload); with the rule suppressed neither file enters any channel; STRUCTURED seeds configuration.restgas_profile, traverses to workflow.restgas_profile_reconstruction, injects two curated objects that rank very high (fused ranks 1 and 3), but prod_sim_hvmaps.C and PndTargetGenerator.cxx appear nowhere in governed D1 object/relation/workflow structure (repository seed or runtime), so no governed provenance exists that the frozen path could bridge",
        "failure_classification": "EVIDENCE_LINK_COVERAGE_GAP",
        "secondary_failure_classifications": ["LEGACY_DEPENDENCY_WITHOUT_STRUCTURED_RECOVERY"],
        "paired_outcome": "STRUCTURED_REGRESSION",
        "dependency_interpretation": "LEGACY_DEPENDENCY_CONFIRMED",
        "diagnostic_subtype": "MISSING_GOVERNED_EVIDENCE_LINK",
        "structured_candidate_contribution": True,
    },
    "n004": {
        "primary_interpretation": "LEGACY equals ABLATION on the direct literal case, so the root_macro_usage shortcut was not materially responsible; structured injects one neutral PandaRoot repository seed; outcomes identical",
        "failure_classification": None,
        "secondary_failure_classifications": [],
        "paired_outcome": "STRUCTURED_PARITY",
        "dependency_interpretation": "NOT_MATERIALLY_USED",
        "diagnostic_subtype": None,
        "structured_candidate_contribution": True,
    },
    "g007": {
        "primary_interpretation": "negative control behaves identically in all arms; structured injects one neutral PandaRoot repository seed; no unsupported-evidence leakage and no false confidence introduced",
        "failure_classification": None,
        "secondary_failure_classifications": [],
        "paired_outcome": "STRUCTURED_PARITY",
        "dependency_interpretation": "NOT_ESTABLISHED",
        "diagnostic_subtype": None,
        "structured_candidate_contribution": True,
    },
}

# Authored per-rule migration decisions under the frozen vocabulary and guards.
RULE_DECISIONS: dict[str, dict[str, Any]] = {
    "lmd_fit_data_chain": {
        "decision": "INSUFFICIENT_EVIDENCE",
        "decision_rationale": "PARTIALLY_IDENTIFIABLE per the frozen preregistration: no direct-trigger case exists, so the required LEGACY-ABLATION dependency contrast is not measurable; the frozen guard restricts the migration decision to INSUFFICIENT_EVIDENCE. Paraphrase cases g029 (1.0) and n021 (0.5) and control g025 are stable across arms; structured abstains correctly on the AMBIGUOUS PndLmdCombinedDataReader mention.",
    },
    "event_poca_handoff": {
        "decision": "STRUCTURED_REGRESSION",
        "decision_rationale": "Direct case g036 establishes a real legacy dependency (LEGACY 1.0 -> ABLATION 0.0 final-evidence recall) and STRUCTURED fails to recover it (0.0): the structured path resolves and ranks the correct governed objects very highly but the answer-bearing macro file is reachable only through the legacy exact-channel symbol payload because no accepted D1 evidence linkage exists. Material underperformance of the structured treatment on valid directly applicable evidence; no safety or control regression.",
    },
    "pid_two_pass_files": {
        "decision": "INSUFFICIENT_EVIDENCE",
        "decision_rationale": "PARTIALLY_IDENTIFIABLE per the frozen preregistration: no direct-trigger case, dependency contrast not measurable; frozen guard applies. Paraphrase g020 (1.0) and controls n006/g041 are stable across arms; structured abstains correctly on the unresolved two-pass mention.",
    },
    "model_factory_theory": {
        "decision": "NO_MEANINGFUL_LEGACY_DEPENDENCY",
        "decision_rationale": "Direct case n014 shows LEGACY == ABLATION (0.5): removing the shortcut does not degrade useful retrieval, so the shortcut was not materially responsible. STRUCTURED neither regresses nor improves (0.5); the model_framework definition group is missed in all arms for reasons unrelated to the rule. Direct dependency is identifiable and ablation shows no material legacy contribution, matching the frozen label semantics.",
    },
    "effective_acceptance_pipeline": {
        "decision": "NO_MEANINGFUL_LEGACY_DEPENDENCY",
        "decision_rationale": "Direct case g052 shows LEGACY == ABLATION == STRUCTURED (1.0): paper-channel retrieval reproduces the useful behavior without the shortcut (the question also literally triggers restgas_profile_workflow; suppressing both changes nothing). The distinction control g055 stays stable and structured abstains without narrowing the acceptance/efficiency distinction.",
    },
    "restgas_profile_workflow": {
        "decision": "STRUCTURED_REGRESSION",
        "decision_rationale": "Direct case g021 establishes a real legacy dependency (LEGACY 1.0 -> ABLATION 0.0) and STRUCTURED fails to recover it (0.0): the structured path seeds configuration.restgas_profile and traverses to workflow.restgas_profile_reconstruction with very high fused ranks, but the answer-bearing configuration-usage and macro files lack accepted D1 evidence linkage and never enter any candidate channel. Material underperformance on valid directly applicable evidence; no safety or control regression.",
    },
    "root_macro_usage": {
        "decision": "NO_MEANINGFUL_LEGACY_DEPENDENCY",
        "decision_rationale": "Direct case n004 shows LEGACY == ABLATION == STRUCTURED (1.0): ordinary documentation retrieval reproduces the useful behavior without the shortcut. The negative control g007 stays stable; the structured PandaRoot repository seed injection is metric-neutral and safe.",
    },
}


def load_records(run_dir: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in (run_dir / "records.jsonl").read_text(encoding="utf-8").splitlines()
        if line
    ]


# ---------------------------------------------------------------------------
# D3-A2-R1 audit constants (post-outcome static/provenance repair; no rerun).
#
# Facts provenance:
#   - repository expected state: configs/seed_objects.yaml, seed_relations.yaml,
#     seed_workflows.yaml at the frozen A1 commit 814a618 (static read);
#   - runtime materialized state: read-only deterministic metadata queries of
#     the deployed knowledge state (permitted as non-scientific reproduction of
#     the already-observed A2 state) plus the active normalized ingestion
#     9925ec31a612 (report 2026-08-16);
#   - edge IDs are deterministic stable_id(subject, predicate, object) values.
# ---------------------------------------------------------------------------
FROZEN_TAXONOMY = [
    "STRUCTURED_CANDIDATE_RECALL_FAILURE",
    "RELATION_COVERAGE_GAP",
    "WORKFLOW_COVERAGE_GAP",
    "EVIDENCE_LINK_COVERAGE_GAP",
    "ENTITY_OR_TERMINOLOGY_RESOLUTION_FAILURE",
    "AMBIGUITY_OR_ABSTENTION",
    "REPOSITORY_OR_VERSION_SCOPE_FAILURE",
    "FUSION_OR_RANKING_FAILURE",
    "FINAL_SELECTOR_FAILURE",
    "LEGACY_DEPENDENCY_WITHOUT_STRUCTURED_RECOVERY",
    "CONTROL_LEAKAGE_OR_OVERMATCH",
    "PROHIBITED_SHORTCUT_ENCODING",
    "INFRASTRUCTURE_OR_ARTIFACT_FAILURE",
]

SEED_OBJECT_IDS = [
    "paper.karavdina_2015.chapter_4",
    "workflow.pandaroot.lmd_reconstruction",
    "data_product.pandaroot.lumi_trks_qa",
    "subsystem.luminosityfit.panda_data_io",
    "paper.pflueger_2017.chapter_4",
    "subsystem.luminosityfit.model_and_fit",
    "concept.li_2026.restgas_effective_acceptance",
    "workflow.restgas_aware_luminosity_acceptance",
    "workflow.restgas_profile_reconstruction",
    "concept.restgas_longitudinal_efficiency",
    "data_product.reconstructed_restgas_profile",
    "repository.restgas_determination.oct19",
    "repository.pandaroot.oct19",
    "document.pandaroot_sphinx_2023_08_25_dev",
    "workflow.pandaroot.generic",
    "configuration.restgas_profile",
    "file_pattern.restgas_profile_input",
    "data_product.restgas.event_poca",
    "data_product.restgas.boost_root",
    "data_product.restgas.pid_root",
    "data_product.restgas.pid_final_root",
    "workflow.restgas.second_pass_pid",
    "workflow.restgas.first_pass_poca",
    "concept.luminosityfit.luminosity_fit_model",
]

RUNTIME_CURATED_OBJECT_IDS = [
    "concept.li_2026.restgas_effective_acceptance",
    "concept.restgas_longitudinal_efficiency",
    "configuration.restgas_profile",
    "data_product.pandaroot.lumi_trks_qa",
    "data_product.reconstructed_restgas_profile",
    "data_product.restgas.boost_root",
    "data_product.restgas.event_poca",
    "data_product.restgas.pid_final_root",
    "data_product.restgas.pid_root",
    "document.pandaroot_sphinx_2023_08_25_dev",
    "file_pattern.restgas_profile_input",
    "paper.karavdina_2015.chapter_4",
    "paper.pflueger_2017.chapter_4",
    "repository.pandaroot.oct19",
    "repository.restgas_determination.oct19",
    "subsystem.luminosityfit.model_and_fit",
    "subsystem.luminosityfit.panda_data_io",
    "workflow.pandaroot.generic",
    "workflow.pandaroot.lmd_reconstruction",
    "workflow.restgas.second_pass_pid",
    "workflow.restgas_aware_luminosity_acceptance",
    "workflow.restgas_profile_reconstruction",
]

SEED_RELATION_TUPLES = [
    ("paper.karavdina_2015.chapter_4", "THEORETICAL_BASIS_FOR", "workflow.pandaroot.lmd_reconstruction"),
    ("workflow.pandaroot.lmd_reconstruction", "PRODUCES", "data_product.pandaroot.lumi_trks_qa"),
    ("data_product.pandaroot.lumi_trks_qa", "PRODUCES_INPUT_FOR", "subsystem.luminosityfit.panda_data_io"),
    ("paper.pflueger_2017.chapter_4", "FORMALIZES", "concept.luminosityfit.luminosity_fit_model"),
    ("subsystem.luminosityfit.model_and_fit", "IMPLEMENTS", "concept.luminosityfit.luminosity_fit_model"),
    ("concept.li_2026.restgas_effective_acceptance", "IMPLEMENTED_AS_PIPELINE", "workflow.restgas_aware_luminosity_acceptance"),
    ("workflow.restgas_profile_reconstruction", "PRODUCES_PROFILE_FOR", "workflow.restgas_aware_luminosity_acceptance"),
    ("concept.restgas_longitudinal_efficiency", "CORRECTS", "data_product.reconstructed_restgas_profile"),
    ("repository.restgas_determination.oct19", "FORKED_FROM", "repository.pandaroot.oct19"),
    ("document.pandaroot_sphinx_2023_08_25_dev", "OPERATIONALLY_DOCUMENTS", "workflow.pandaroot.generic"),
    ("configuration.restgas_profile", "PARAMETERIZES", "workflow.restgas_profile_reconstruction"),
    ("file_pattern.restgas_profile_input", "PRODUCES_INPUT_FOR", "workflow.restgas_profile_reconstruction"),
    ("workflow.restgas.first_pass_poca", "CONSUMES", "data_product.restgas.pid_root"),
    ("workflow.restgas.first_pass_poca", "PRODUCES", "data_product.restgas.boost_root"),
    ("data_product.restgas.event_poca", "PRODUCES_INPUT_FOR", "workflow.restgas.second_pass_pid"),
    ("workflow.restgas.second_pass_pid", "PRODUCES", "data_product.restgas.pid_final_root"),
]

RUNTIME_RELATION_TUPLES = [
    ("concept.li_2026.restgas_effective_acceptance", "IMPLEMENTED_AS_PIPELINE", "workflow.restgas_aware_luminosity_acceptance"),
    ("concept.restgas_longitudinal_efficiency", "CORRECTS", "data_product.reconstructed_restgas_profile"),
    ("configuration.restgas_profile", "PARAMETERIZES", "workflow.restgas_profile_reconstruction"),
    ("data_product.pandaroot.lumi_trks_qa", "PRODUCES_INPUT_FOR", "subsystem.luminosityfit.panda_data_io"),
    ("data_product.restgas.boost_root", "PRODUCES", "data_product.restgas.event_poca"),
    ("data_product.restgas.event_poca", "PRODUCES_INPUT_FOR", "workflow.restgas.second_pass_pid"),
    ("data_product.restgas.pid_root", "PRODUCES_INPUT_FOR", "data_product.restgas.event_poca"),
    ("document.pandaroot_sphinx_2023_08_25_dev", "OPERATIONALLY_DOCUMENTS", "workflow.pandaroot.generic"),
    ("file_pattern.restgas_profile_input", "PRODUCES_INPUT_FOR", "workflow.restgas_profile_reconstruction"),
    ("paper.karavdina_2015.chapter_4", "THEORETICAL_BASIS_FOR", "workflow.pandaroot.lmd_reconstruction"),
    ("paper.pflueger_2017.chapter_4", "FORMALIZES", "subsystem.luminosityfit.model_and_fit"),
    ("repository.restgas_determination.oct19", "FORKED_FROM", "repository.pandaroot.oct19"),
    ("workflow.pandaroot.lmd_reconstruction", "PRODUCES", "data_product.pandaroot.lumi_trks_qa"),
    ("workflow.restgas.second_pass_pid", "PRODUCES", "data_product.restgas.pid_final_root"),
    ("workflow.restgas_profile_reconstruction", "PRODUCES", "data_product.restgas.boost_root"),
    ("workflow.restgas_profile_reconstruction", "PRODUCES_PROFILE_FOR", "workflow.restgas_aware_luminosity_acceptance"),
]

# edge.* IDs verified: runtime-only IDs match the values observed in the
# deployed relation_edges rows during the A2 read-only state queries.
SEED_ONLY_RELATION_EDGE_IDS = {
    ("paper.pflueger_2017.chapter_4", "FORMALIZES", "concept.luminosityfit.luminosity_fit_model"): "edge.161980db8e6627f0ea2e220a",
    ("subsystem.luminosityfit.model_and_fit", "IMPLEMENTS", "concept.luminosityfit.luminosity_fit_model"): "edge.4b871167865184a7c023ab36",
    ("workflow.restgas.first_pass_poca", "CONSUMES", "data_product.restgas.pid_root"): "edge.5a8a1deba5f20c052cdcb044",
    ("workflow.restgas.first_pass_poca", "PRODUCES", "data_product.restgas.boost_root"): "edge.2e09628416a01ce2461d752a",
}

RUNTIME_ONLY_RELATION_EDGE_IDS = {
    ("data_product.restgas.boost_root", "PRODUCES", "data_product.restgas.event_poca"): "edge.8e3356854bd9135cffddf99c",
    ("data_product.restgas.pid_root", "PRODUCES_INPUT_FOR", "data_product.restgas.event_poca"): "edge.f7d601361f017a6a93b5e10b",
    ("workflow.restgas_profile_reconstruction", "PRODUCES", "data_product.restgas.boost_root"): "edge.878ae270451b806be2f6bf79",
    ("paper.pflueger_2017.chapter_4", "FORMALIZES", "subsystem.luminosityfit.model_and_fit"): "edge.2f95e61f216467cb0f7c2dbc",
}


def _relation_accounting(tuples: list[tuple[str, str, str]]) -> list[dict[str, str]]:
    return [
        {
            "subject_id": subject,
            "predicate": predicate,
            "object_id": object_id,
            "expected_edge_id": SEED_ONLY_RELATION_EDGE_IDS.get(
                (subject, predicate, object_id)
            )
            or RUNTIME_ONLY_RELATION_EDGE_IDS.get((subject, predicate, object_id)),
        }
        for subject, predicate, object_id in tuples
    ]


def build_repair_sections() -> dict[str, Any]:
    seed_set = set(SEED_RELATION_TUPLES)
    runtime_set = set(RUNTIME_RELATION_TUPLES)
    return {
        "repair_history": [
            {
                "repair_id": "D3-A2-R1",
                "task": "Outcome Attribution & Runtime Knowledge-State Provenance Repair",
                "scope": "post-outcome interpretation/provenance repair only",
                "scientific_reruns": 0,
                "new_retrieval_or_model_calls": 0,
                "metrics_changed": False,
                "per_rule_decisions_changed": False,
                "repairs": [
                    "restored strict use of the frozen D3-A0-R1 failure taxonomy (descriptive outcome labels removed from failure_classification/failure_taxonomy_counts and separated into paired_outcome/dependency_interpretation)",
                    "refined g036/g021 evidence-link mechanism attribution with audited diagnostic subtypes",
                    "recorded and audited the runtime D1 materialization state versus the repository seed state with a per-item materiality assessment",
                ],
                "original_a2_result_commit": "c6be168",
                "original_a2_taxonomy_counts_superseded": {
                    "EVIDENCE_LINK_COVERAGE_GAP": 2,
                    "STRUCTURED_PARITY": 14,
                    "note": "STRUCTURED_PARITY is a descriptive outcome, not a frozen taxonomy value; it was incorrectly counted as a failure class in the original A2 artifact",
                },
            }
        ],
        "taxonomy_repair": {
            "frozen_failure_taxonomy_authority": "evaluation/d3_a0_shortcut_migration_preregistration.json (D3-A0-R1)",
            "frozen_failure_taxonomy": FROZEN_TAXONOMY,
            "nonfrozen_labels_removed_from_failure_layer": [
                "STRUCTURED_PARITY",
                "LEGACY_SHORTCUT_DEPENDENCY_CONFIRMED",
                "LEGACY_SHORTCUT_NOT_MATERIALLY_USED",
            ],
            "case_layer_separation": {
                "failure_classification": "frozen taxonomy value or null",
                "secondary_failure_classifications": "additional frozen taxonomy values where applicable",
                "paired_outcome": "descriptive structured-vs-ablation outcome (STRUCTURED_PARITY / STRUCTURED_REGRESSION)",
                "dependency_interpretation": "LEGACY_DEPENDENCY_CONFIRMED / NOT_MATERIALLY_USED / NOT_ESTABLISHED",
                "diagnostic_subtype": "interpretation-only refinement of EVIDENCE_LINK_COVERAGE_GAP; not a taxonomy value",
            },
            "frozen_arm_case_outcome_mapping": {
                "anchor": "preregistered metric definitions (regression_rate, useful_retrieval_reproduction_rate, control applicability)",
                "REGRESSION": ["g036", "g021"],
                "FULL_REPRODUCTION": [
                    "g020", "g029", "g052", "g055", "g060",
                    "n003", "n004", "n006", "n014", "n021", "n022",
                ],
                "NOT_APPLICABLE": ["g007", "g025", "g041"],
                "NO_REPRODUCTION": [],
                "PARTIAL_REPRODUCTION": [],
                "IMPROVEMENT": [],
                "NOT_RUN": [],
                "INFRASTRUCTURE_FAILURE": [],
            },
        },
        "runtime_knowledge_state": {
            "audited_against": "frozen A1 commit 814a618 configs (repository expected) versus the deployed materialization used by the 48 A2 executions",
            "repository_expected": {
                "source": "configs/seed_objects.yaml, configs/seed_relations.yaml, configs/seed_workflows.yaml at 814a618",
                "object_count": 24,
                "object_ids": SEED_OBJECT_IDS,
                "accepted_relation_count": 16,
                "accepted_relations": _relation_accounting(SEED_RELATION_TUPLES),
                "workflow_step_count": 1,
                "workflow_step_ids": ["workflow.restgas.first_pass_poca (workflow_id workflow.restgas_profile_reconstruction; entrypoint workflow.restgas.first_pass_poca; inputs data_product.restgas.pid_root; outputs data_product.restgas.boost_root)"],
            },
            "a2_runtime_materialized": {
                "source": "read-only deterministic metadata queries reproducing the state observed during A2; active normalized ingestion 9925ec31a612 (2026-08-16)",
                "object_count": 22,
                "object_ids": RUNTIME_CURATED_OBJECT_IDS,
                "accepted_relation_count": 16,
                "accepted_relations": _relation_accounting(RUNTIME_RELATION_TUPLES),
                "relation_payload_evidence_provenance": "none: all 16 materialized curated-touching relation payloads carry evidence_paths = absent and evidence_object_ids = [] (no relation-level evidence provenance is stored in the deployed state)",
                "workflow_step_count": 0,
                "workflow_step_ids": [],
                "workflow_steps_table_total_rows": 374,
            },
            "missing_items": {
                "missing_runtime_object_ids": [
                    "workflow.restgas.first_pass_poca",
                    "concept.luminosityfit.luminosity_fit_model",
                ],
                "unexpected_runtime_object_ids": [],
                "missing_runtime_relations": _relation_accounting(
                    sorted(set(SEED_RELATION_TUPLES) - runtime_set)
                ),
                "unexpected_runtime_relations": _relation_accounting(
                    sorted(runtime_set - seed_set)
                ),
                "missing_runtime_workflow_step_ids": ["workflow.restgas.first_pass_poca"],
                "unexpected_runtime_workflow_step_ids": [],
            },
            "drift_root_cause": {
                "cause": "repository/runtime drift: the last completed ingestion (normalized 9925ec31a612, 2026-08-16) predates the D1-A2 seed additions (commit 24e4e4b, 2026-08-29) and the D1-A2R1 concept correction (2fc947f); no re-ingestion was authorized or performed afterward (D1-A3R1 recorded FUTURE_REINGESTED_STRUCTURED_KNOWLEDGE_STATE_CHANGED and D3 prohibits reindex/ingestion)",
                "loader_semantics_verified": "the ingestion pipeline and DB upsert paths (seed_workflow_steps with metadata.curated_seed=true, upsert_workflows, upsert_relations) correctly handle the seed additions; the deployed DB simply predates them",
                "relation_count_coincidence": "both states contain 16 accepted curated-touching relations, but the identities differ: 12 common, 4 seed-only (two first_pass_poca edges plus the two D1-A2 model-concept edges), 4 runtime-only (D1-A1-era stand-in edges superseded by D1-A2)",
            },
            "materiality_assessment": {
                "decision_rule": "material only if a missing/drifted item was part of the preregistered structured capability AND its absence could plausibly change g021/g036 or another migration decision under the frozen A1 candidate-generation semantics",
                "per_item": [
                    {
                        "item": "workflow.restgas.first_pass_poca (object)",
                        "required_by_any_structured_path": False,
                        "directly_relevant_to": ["g036"],
                        "would_create_new_retrievable_answer_bearing_candidate": False,
                        "reason": "A materialized curated workflow object (source curated_panda_domain, object_type workflow) can never satisfy the g036 required selector (source_id restgas_determination, path macro/target/ana_dpm.C, object_type function/source_file); the frozen A1 path materializes governed objects only, never corpus-file candidates from provenance",
                    },
                    {
                        "item": "concept.luminosityfit.luminosity_fit_model (object)",
                        "required_by_any_structured_path": False,
                        "directly_relevant_to": ["n014", "g060"],
                        "would_create_new_retrievable_answer_bearing_candidate": False,
                        "reason": "n014/g060 outcomes rest on arm equality (LEGACY == ABLATION == STRUCTURED); the concept was never a D2 match target in the run and its candidate object cannot match the n014 selectors (model_framework definition documentation, PndLmdModelFactory role)",
                    },
                    {
                        "item": "workflow.restgas.first_pass_poca (curated workflow step)",
                        "required_by_any_structured_path": False,
                        "directly_relevant_to": ["g036", "g021"],
                        "would_create_new_retrievable_answer_bearing_candidate": False,
                        "reason": "if materialized it would inject additional curated participants (first_pass_poca, restgas_profile_reconstruction, pid_root, boost_root) into g036/g021; all are governed objects that cannot satisfy the required corpus-file selectors, so group outcomes are unchanged (only engineering diagnostic counts would differ)",
                    },
                    {
                        "item": "4 seed-only relations (incl. the two ana_dpm.C-provenance-bearing first_pass_poca edges)",
                        "required_by_any_structured_path": False,
                        "directly_relevant_to": ["g036"],
                        "would_create_new_retrievable_answer_bearing_candidate": False,
                        "reason": "the frozen hop budget is max_relation_hops=1, and event_poca's only seed edge is PRODUCES_INPUT_FOR second_pass_pid, so the ana_dpm.C-provenance edges would not have been traversed from the D2-resolved seed even under the intended seed state; under A1 semantics relation payloads are never converted into candidates anyway",
                    },
                    {
                        "item": "4 runtime-only D1-A1-era stand-in relations",
                        "required_by_any_structured_path": False,
                        "directly_relevant_to": ["g036"],
                        "would_create_new_retrievable_answer_bearing_candidate": False,
                        "reason": "they made boost_root/pid_root reachable and injectable in g036; the injected curated objects ranked highly but matched no required selector, so outcomes are unchanged",
                    },
                ],
                "conclusion": "no missing or drifted item could have changed any of the 48 frozen scientific outcomes or any per-rule migration decision under the frozen A1 candidate-generation semantics; the drift is recorded as a provenance limitation, not a validity confound",
            },
        },
        "mechanism_attribution_revision": {
            "g036": {
                "primary_failure_classification": "EVIDENCE_LINK_COVERAGE_GAP",
                "secondary_failure_classifications": ["LEGACY_DEPENDENCY_WITHOUT_STRUCTURED_RECOVERY"],
                "diagnostic_subtype": "EXISTING_PROVENANCE_NOT_MATERIALIZED",
                "audited_facts": [
                    "g036 requires evidence at macro/target/ana_dpm.C (source restgas_determination, object_type function/source_file)",
                    "the repository governed seed D1 already carries macro/target/ana_dpm.C as relation-level evidence provenance on workflow.restgas.first_pass_poca CONSUMES data_product.restgas.pid_root (edge.5a8a1deba5f20c052cdcb044) and workflow.restgas.first_pass_poca PRODUCES data_product.restgas.boost_root (edge.2e09628416a01ce2461d752a), both accepted",
                    "the frozen A1 structured path reads relation payloads into its edge receipt but never consumes evidence provenance fields: d3_structured.py contains no reference to evidence_paths/evidence_object_ids/evidence_source_ids; relation_path provenance records only edge_id/predicate/subject_id/object_id/traversal_direction; only subject/object endpoint objects are materialized as candidates",
                    "the deployed runtime state additionally contains neither of those provenance-bearing edges, and none of its 16 materialized relation payloads carries any evidence provenance",
                    "the D2 resolution (event_poca -> data_product.restgas.event_poca, Tier S) and D1 traversal worked; structured candidates ranked at fused ranks 1-2; ranking is not the binding constraint",
                ],
                "revised_attribution": "the missing capability is not a new D1 domain-object relation: the governed evidence provenance already exists at the repository seed level. The frozen structured retrieval path does not materialize relation-level evidence provenance into retrievable source evidence, and the deployed runtime state has not materialized the provenance-bearing edges at all.",
            },
            "g021": {
                "primary_failure_classification": "EVIDENCE_LINK_COVERAGE_GAP",
                "secondary_failure_classifications": ["LEGACY_DEPENDENCY_WITHOUT_STRUCTURED_RECOVERY"],
                "diagnostic_subtype": "MISSING_GOVERNED_EVIDENCE_LINK",
                "audited_facts": [
                    "g021 requires evidence at macro/target/prod_sim_hvmaps.C (e1) and pgenerators/Target/PndTargetGenerator.cxx (e2), source restgas_determination",
                    "neither path appears anywhere in governed D1 structure: not in seed objects, not in any seed relation/workflow evidence provenance, not in the deployed runtime (whose relation payloads carry no evidence provenance at all)",
                    "the only governed-adjacent provenance near g021's topology points to README.md and macro/target/README.md (configuration.restgas_profile PARAMETERIZES workflow.restgas_profile_reconstruction)",
                    "prod_sim_hvmaps.C exists only in the legacy restgas_profile_workflow rule payload — exactly the shortcut whose removal defines this comparison",
                    "D2 resolution (restgas_profile -> configuration.restgas_profile, Tier S) and traversal to workflow.restgas_profile_reconstruction worked; injected candidates ranked at fused ranks 1 and 3",
                ],
                "revised_attribution": "the required answer-bearing evidence is not represented by any inspectable governed evidence linkage in the accepted D1 structure; this is a genuinely missing governed evidence link, not an A1 materialization failure of existing provenance.",
            },
        },
        "experiment_validity_after_repair": {
            "formal_d3_experiment_verdict": "PASS",
            "provenance_limitation": "the frozen A1 implementation was evaluated against the deployed 2026-08-16 D1 materialization rather than the current D1-A2 repository seed state (22/16/0 versus 24/16/1 curated objects/relations/workflow steps, with 4 relation-identity differences in both directions); the drift was audited item-by-item and is outcome-neutral under the frozen A1 candidate-generation semantics",
            "scientific_outcomes_changed": False,
            "per_rule_decisions_changed": False,
            "per_rule_decision_counts": {
                "STRUCTURED_REGRESSION": 2,
                "NO_MEANINGFUL_LEGACY_DEPENDENCY": 3,
                "INSUFFICIENT_EVIDENCE": 2,
                "MIGRATION_SUPPORTED": 0,
                "PARTIALLY_REPRODUCED": 0,
            },
        },
    }


def arm_metric(records: list[dict[str, Any]], arm: str, case_id: str, field: str) -> Any:
    record = next(r for r in records if r["arm"] == arm and r["case_id"] == case_id)
    return (record.get("metrics") or {}).get(field)


def aggregate(records: list[dict[str, Any]], arm: str, field: str) -> dict[str, Any]:
    values = []
    for record in records:
        if record["arm"] != arm:
            continue
        metric = (record.get("metrics") or {}).get(field)
        applicability = ((record.get("metrics") or {}).get("metric_applicability") or {}).get(field)
        if metric is not None and applicability:
            values.append((record["case_id"], metric))
    mean = sum(value for _, value in values) / len(values) if values else None
    return {"mean": mean, "applicable_case_count": len(values)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--run-dir", type=Path, default=None)
    args = parser.parse_args()
    run_dir = args.run_dir or (args.project_root / "data" / "evaluation" / "runs" / RUN_ID)
    records = load_records(run_dir)
    assert len(records) == 48, f"expected 48 records, found {len(records)}"
    assert not [r for r in records if r.get("error")], "runner recorded errors"

    manifest = json.loads((run_dir / "run_manifest.json").read_text(encoding="utf-8"))
    preregistration = json.loads(
        (args.project_root / "evaluation" / "d3_a0_shortcut_migration_preregistration.json").read_text(encoding="utf-8")
    )
    manifest_cases = preregistration["comparison_cases"]
    case_ids = [c["case_id"] for c in manifest_cases]
    assert {r["case_id"] for r in records} == set(case_ids)
    assert {r["arm"] for r in records} == set(ARM_ORDER)
    identifiability = {
        item["rule_id"]: item["identifiability_status"]
        for item in preregistration["selected_rule_identifiability"]
    }

    # --- aggregate metric tables -------------------------------------------------
    metric_fields = [
        "gold_recall_at_5",
        "gold_recall_at_10",
        "gold_recall_at_20",
        "mrr",
        "combined_candidate_recall",
        "final_evidence_recall",
        "critical_final_evidence_recall",
    ]
    arm_summaries: dict[str, Any] = {}
    for arm in ARM_ORDER:
        arm_summaries[arm] = {
            "executions": 16,
            "metrics": {field: aggregate(records, arm, field) for field in metric_fields},
        }

    paired_metrics: dict[str, Any] = {"applicable_case_count": 13, "denominator_note": "means over the 13 answered cases; the 3 insufficient-evidence controls are retained for safety/control analysis only"}
    for field in metric_fields:
        paired_metrics[field] = {}
        for case_id in case_ids:
            l = arm_metric(records, "LEGACY", case_id, field)
            a = arm_metric(records, "ABLATION", case_id, field)
            s = arm_metric(records, "STRUCTURED", case_id, field)
            if None in (l, a, s):
                continue
            paired_metrics[field][case_id] = {
                "LEGACY": l,
                "ABLATION": a,
                "STRUCTURED": s,
                "legacy_dependency": round(l - a, 6),
                "structured_recovery": round(s - a, 6),
                "structured_parity": round(s - l, 6),
            }
        deltas_l_a = [cell["legacy_dependency"] for cell in paired_metrics[field].values()]
        deltas_s_a = [cell["structured_recovery"] for cell in paired_metrics[field].values()]
        deltas_s_l = [cell["structured_parity"] for cell in paired_metrics[field].values()]
        paired_metrics[field]["_summary"] = {
            "mean_legacy_minus_ablation": round(sum(deltas_l_a) / len(deltas_l_a), 6),
            "mean_structured_minus_ablation": round(sum(deltas_s_a) / len(deltas_s_a), 6),
            "mean_structured_minus_legacy": round(sum(deltas_s_l) / len(deltas_s_l), 6),
            "direction": "higher is better for every metric",
        }

    # --- preregistered primary metrics -------------------------------------------
    def case_cells(field: str) -> dict[str, Any]:
        return {
            cid: cell
            for cid, cell in paired_metrics[field].items()
            if cid != "_summary"
        }

    fer_cells = case_cells("final_evidence_recall")
    legacy_dependent = [cid for cid, cell in fer_cells.items() if cell["legacy_dependency"] > 0]
    legacy_positive = [cid for cid, cell in fer_cells.items() if cell["LEGACY"] > 0]
    # The preregistered reproduction/recovery predicate is STRUCTURED >= LEGACY
    # (structured_parity), not STRUCTURED >= ABLATION.
    recovered = [cid for cid in legacy_dependent if fer_cells[cid]["structured_parity"] >= 0]
    reproduced = [cid for cid in legacy_positive if fer_cells[cid]["structured_parity"] >= 0]
    regressed = [cid for cid, cell in fer_cells.items() if cell["structured_parity"] < 0]
    primary_frozen_metrics = {
        "useful_retrieval_reproduction_rate": {
            "numerator": len(reproduced),
            "denominator": len(legacy_positive),
            "value": round(len(reproduced) / len(legacy_positive), 4),
            "cases": {"legacy_positive": legacy_positive, "reproduced": reproduced},
            "definition": "among cases whose LEGACY arm retrieves at least one required evidence group in final evidence, fraction where STRUCTURED reaches an equal or greater required-group count",
        },
        "selected_rule_dependency_rate": {
            "numerator": len(legacy_dependent),
            "denominator": len(fer_cells),
            "value": round(len(legacy_dependent) / len(fer_cells), 4),
            "cases": legacy_dependent,
            "definition": "fraction of applicable comparison cases where LEGACY final-evidence recall exceeds ABLATION",
        },
        "structured_recovery_rate": {
            "numerator": len(recovered),
            "denominator": len(legacy_dependent),
            "value": round(len(recovered) / len(legacy_dependent), 4) if legacy_dependent else None,
            "cases": {"legacy_dependent": legacy_dependent, "recovered": recovered},
            "definition": "among cases with LEGACY > ABLATION, fraction where STRUCTURED reaches or exceeds LEGACY",
        },
        "regression_rate": {
            "numerator": len(regressed),
            "denominator": len(fer_cells),
            "value": round(len(regressed) / len(fer_cells), 4),
            "cases": regressed,
            "definition": "fraction of applicable comparison cases where STRUCTURED final-evidence recall is below LEGACY",
        },
    }

    # --- case results -------------------------------------------------------------
    case_results: list[dict[str, Any]] = []
    for case in manifest_cases:
        case_id = case["case_id"]
        arms_out: dict[str, Any] = {}
        for arm in ARM_ORDER:
            record = next(r for r in records if r["arm"] == arm and r["case_id"] == case_id)
            metrics = record.get("metrics") or {}
            counters = ((record.get("d3_experiment") or {}).get("diagnostic_counters") or {})
            legacy_counters = counters if arm != "LEGACY" else counters
            arms_out[arm] = {
                "retrieval_receipt_ref": {"run_id": RUN_ID, "arm": arm, "case_id": case_id},
                "matched_expansion_rules": (record.get("plan_summary", {}).get("d3_experiment") or {}).get("matched_active_rule_ids"),
                "selected_shortcut_triggered": (
                    (record.get("plan_summary", {}).get("d3_experiment") or {}).get("diagnostic_counters", {}).get("selected_legacy_shortcut_hit_count", 0) > 0
                ),
                "structured_diagnostic_counters": counters if arm == "STRUCTURED" else None,
                "metric_matches": {
                    "final_evidence_recall": metrics.get("final_evidence_recall"),
                    "critical_final_evidence_recall": metrics.get("critical_final_evidence_recall"),
                    "gold_recall_at_5": metrics.get("gold_recall_at_5"),
                    "gold_recall_at_10": metrics.get("gold_recall_at_10"),
                    "gold_recall_at_20": metrics.get("gold_recall_at_20"),
                    "mrr": metrics.get("mrr"),
                    "combined_candidate_recall": metrics.get("combined_candidate_recall"),
                    "final_evidence_group_provenance": (metrics.get("evidence_match_provenance") or {}).get("final_evidence_recall"),
                },
            }
        analysis = CASE_ANALYSIS[case_id]
        legacy_cell = fer_cells.get(case_id, {})
        frozen_arm_case_outcome = (
            "REGRESSION" if case_id in {"g036", "g021"}
            else "NOT_APPLICABLE" if case_id in {"g007", "g025", "g041"}
            else "FULL_REPRODUCTION"
        )
        case_results.append(
            {
                "case_id": case_id,
                "dataset": case["dataset"],
                "bound_rule_id": case["bound_rule_id"],
                "comparison_role": case["comparison_role"],
                "identifiability_status": identifiability[case["bound_rule_id"]],
                "arms": arms_out,
                "paired_interpretation": {
                    "legacy_dependency_confirmed": legacy_cell.get("legacy_dependency", 0) > 0,
                    "structured_recovery_occurred": legacy_cell.get("structured_recovery", 0) > 0,
                    "structured_regression_occurred": legacy_cell.get("structured_parity", 0) < 0,
                    "primary_interpretation": analysis["primary_interpretation"],
                },
                "failure_classification": analysis["failure_classification"],
                "secondary_failure_classifications": analysis["secondary_failure_classifications"],
                "paired_outcome": analysis["paired_outcome"],
                "dependency_interpretation": analysis["dependency_interpretation"],
                "diagnostic_subtype": analysis["diagnostic_subtype"],
                "frozen_arm_case_outcome": frozen_arm_case_outcome,
            }
        )

    # --- per-rule results -----------------------------------------------------------
    rule_to_cases: dict[str, list[str]] = {}
    for case in manifest_cases:
        rule_to_cases.setdefault(case["bound_rule_id"], []).append(case["case_id"])
    per_rule_results = []
    for rule_id, decision in RULE_DECISIONS.items():
        case_ids_for_rule = rule_to_cases[rule_id]
        direct = [c for c in case_ids_for_rule if next(x for x in manifest_cases if x["case_id"] == c)["comparison_role"] == "DIRECT_LITERAL"]
        controls = [c for c in case_ids_for_rule if "CONTROL" in next(x for x in manifest_cases if x["case_id"] == c)["comparison_role"]]
        dependency_evidence = [
            {
                "case_id": cid,
                "legacy_minus_ablation_final_evidence_recall": fer_cells.get(cid, {}).get("legacy_dependency"),
                "structured_minus_ablation_final_evidence_recall": fer_cells.get(cid, {}).get("structured_recovery"),
            }
            for cid in case_ids_for_rule
            if cid in fer_cells
        ]
        per_rule_results.append(
            {
                "rule_id": rule_id,
                "identifiability_status": identifiability[rule_id],
                "case_ids": case_ids_for_rule,
                "direct_case_ids": direct,
                "control_case_ids": controls,
                "legacy_dependency_evidence": dependency_evidence,
                "structured_recovery_evidence": dependency_evidence,
                "structured_parity_evidence": dependency_evidence,
                "mechanism_findings": [
                    CASE_ANALYSIS[cid]["primary_interpretation"] for cid in case_ids_for_rule
                ],
                "safety_findings": "no control regression, no leakage, no ambiguity collapse, all five prohibited-use counters zero in every STRUCTURED execution bound to this rule",
                "decision": decision["decision"],
                "decision_rationale": decision["decision_rationale"],
            }
        )

    # --- counters and accounting ------------------------------------------------------
    safety_counters = {
        "migration_specific_direct_answer_location_injection_count": 0,
        "prohibited_fallback_use_count": 0,
        "evaluation_metadata_runtime_use_count": 0,
        "selected_legacy_payload_reuse_count": 0,
        "same_as_activation_count": 0,
    }
    for record in records:
        if record["arm"] != "STRUCTURED":
            continue
        counters = (record.get("d3_experiment") or {}).get("diagnostic_counters") or {}
        for key in safety_counters:
            assert counters.get(key) == 0, f"safety counter {key} nonzero in {record['case_id']}"

    d3_counter_totals: Counter[str] = Counter()
    for record in records:
        if record["arm"] != "STRUCTURED":
            continue
        counters = (record.get("d3_experiment") or {}).get("diagnostic_counters") or {}
        for key, value in counters.items():
            if isinstance(value, (int, float)):
                d3_counter_totals[key] += value
        statuses = counters.get("structured_resolution_status_counts") or {}
        for status, count in statuses.items():
            d3_counter_totals[f"resolution_status::{status}"] += count

    call_totals: Counter[str] = Counter()
    for record in records:
        for key, value in (record.get("call_accounting") or {}).items():
            if isinstance(value, (int, float)):
                call_totals[key] += value

    taxonomy_counts = Counter(
        CASE_ANALYSIS[cid]["failure_classification"]
        for cid in case_ids
        if CASE_ANALYSIS[cid]["failure_classification"] is not None
    )
    paired_outcome_counts = Counter(CASE_ANALYSIS[cid]["paired_outcome"] for cid in case_ids)

    # --- assemble artifact --------------------------------------------------------------
    decisions_by_value = Counter(dec["decision"] for dec in RULE_DECISIONS.values())
    verdict = "PASS"
    artifact = {
        "schema_version": "1.0.0",
        "checkpoint": "D3-A2",
        "status": "COMPLETE / FROZEN_THREE_ARM_COMPARISON_COMPLETE",
        "verdict": verdict,
        "verdict_scope": "valid single frozen three-arm comparison; PASS does not imply every rule supports migration",
        "implementation_identity": {
            "frozen_implementation_commit": FROZEN_IMPLEMENTATION_SHA,
            "commit_subject": "D3-A1 implement structured shortcut replacement prototype",
            "git_head_during_run": manifest["git_head"],
            "pre_run_identity_diff_lines": manifest["implementation_identity_diff_lines"],
        },
        "preregistration_identity": {
            "structured_artifact": "evaluation/d3_a0_shortcut_migration_preregistration.json",
            "sha256": PREREGISTRATION_SHA,
            "schema_version": preregistration["schema_version"],
            "repair_source_head": preregistration["repair_source_head"],
        },
        "outcome_exposure": {
            "before_first_formal_case": "STARTED",
            "after_valid_complete_comparison": "COMPLETE",
            "started_at_utc": manifest["started_at_utc"],
            "finished_at_utc": manifest["finished_at_utc"],
        },
        "selected_rule_ids": preregistration["selected_batch_revision"]["repaired_selected_rule_ids"],
        "comparison_manifest_identity": {
            "revision_id": preregistration["comparison_manifest_revision"]["revision_id"],
            "case_count": 16,
            "dataset_counts": preregistration["comparison_selection_policy"]["dataset_counts"],
            "case_ids_in_execution_order": manifest["case_order"],
            "gold_dataset_sha256": manifest["gold_dataset_sha256"],
            "novel_dev_dataset_sha256": manifest["novel_dev_dataset_sha256"],
        },
        "execution_order": {
            "arm_order": list(ARM_ORDER),
            "case_order_within_arm": manifest["case_order"],
            "runner": "evaluation/scripts/d3_a2_runner.py",
            "run_id": RUN_ID,
            "raw_records": "data/evaluation/runs/d3_a2_frozen_20260831/records.jsonl",
        },
        "run_counts": {
            "total_executions": 48,
            "LEGACY": 16,
            "ABLATION": 16,
            "STRUCTURED": 16,
            "complete_paired_case_cells": 16,
            "infrastructure_failures": 0,
            "retries": 0,
            "scientific_reruns": 0,
        },
        "call_counts": {
            "analyzer_generation_calls": 48,
            "reranker_generation_calls": 48,
            "total_generation_calls": call_totals.get("generation_calls"),
            "embedding_calls": call_totals.get("embedding_calls"),
            "model_calls_total": call_totals.get("model_calls"),
            "token_usage": call_totals.get("token_usage"),
            "qa_calls": 0,
            "verifier_calls": 0,
            "judge_calls": 0,
            "new_model_class_or_prompt_introduced": False,
        },
        "storage_writes": {
            "postgresql_writes": 0,
            "qdrant_writes": 0,
            "reindex": False,
            "index_migration": False,
        },
        "protected_dataset_access": {
            "novel_validation": "UNSEEN",
            "novel_validation_cases_run": 0,
            "novel_holdout": "SEALED_UNSEEN",
            "novel_holdout_cases_run": 0,
        },
        "arm_summaries": arm_summaries,
        "paired_metrics": paired_metrics,
        "primary_frozen_metrics": primary_frozen_metrics,
        "case_results": case_results,
        "per_rule_results": per_rule_results,
        "failure_taxonomy_counts": dict(sorted(taxonomy_counts.items())),
        "d3_aggregate_counters": dict(sorted(d3_counter_totals.items())),
        "safety_counters": {
            "per_execution_verification": "all five counters verified zero in all 16 STRUCTURED executions",
            **safety_counters,
        },
        "overall_interpretation": {
            "frozen_question": "Can the frozen generic D1/D2 structured path reproduce useful behavior of a small representative legacy-shortcut batch without relying on the legacy answer-location payloads or introducing unsafe retrieval regressions?",
            "answer": "The experiment is valid and fully attributable. Three of the five directly identifiable rules show no meaningful legacy dependency (model_factory_theory, effective_acceptance_pipeline, root_macro_usage): their shortcuts were not materially responsible for useful retrieval, and removal plus structured treatment changes nothing. Two rules show a real, material legacy dependency (event_poca_handoff on g036, restgas_profile_workflow on g021): the useful behavior of these shortcuts is exact-channel injection of answer-location file paths/symbols, and the frozen generic structured path cannot reproduce it because the accepted D1 graph has no evidence linkage from the correctly resolved governed objects to the answer-bearing corpus files, even though structured candidates are recalled and ranked very highly (fused ranks 1-3). No unsafe retrieval regression, no control leakage, no prohibited shortcut encoding was observed anywhere.",
            "migration_support_denominator": {
                "directly_identifiable_rules": 5,
                "migration_supported": decisions_by_value["MIGRATION_SUPPORTED"],
                "note": "the two generalization-only rules are reported separately and carry INSUFFICIENT_EVIDENCE by the frozen guard",
            },
            "run_variance_note": "arms are independent frozen-path executions; analyzer/reranker LLM nondeterminism at temperature 0 produced minor metric-neutral selection variance in one case (n022 e3, both objects selector-matched) and small concept-list differences; ABLATION-vs-STRUCTURED rule state was identical by construction",
        },
        "production_changes": {
            "query_expansions_yaml_modified": False,
            "structured_d3_activated_in_production": False,
            "production_d2_role_changed": False,
            "production_routing_changed": False,
            "runtime_files_changed_during_a2": False,
        },
        "post_run_identity_check": {
            "command": "git diff 814a6183f8054e95f65452fc2a5ac4300a6082f5 -- src/panda_agent/retrieval.py src/panda_agent/d3_structured.py",
            "result": "no runtime semantic change",
        },
        "next_stage": {
            "recommended_task": "structured coverage-gap repair design: a separately authorized bounded D1 evidence-linkage coverage stage connecting governed objects to their retrievable answer-location corpus evidence for the two STRUCTURED_REGRESSION rules (event_poca_handoff, restgas_profile_workflow), followed by a focused re-comparison of only those rules",
            "executed_here": False,
            "evidence_basis": "the single dominant failure class is EVIDENCE_LINK_COVERAGE_GAP (2 cases); D2 resolution and D1 traversal worked and structured candidates ranked at fused ranks 1-3, so ranking is not the binding constraint",
        },
    }

    repair_sections = build_repair_sections()
    artifact.update(repair_sections)
    # --- internal consistency checks -------------------------------------------------
    assert artifact["run_counts"]["total_executions"] == 48
    assert len(artifact["case_results"]) == 16
    assert len(artifact["per_rule_results"]) == 7
    frozen_decision_vocabulary = {
        "MIGRATION_SUPPORTED", "PARTIALLY_REPRODUCED", "STRUCTURED_REGRESSION",
        "NO_MEANINGFUL_LEGACY_DEPENDENCY", "INSUFFICIENT_EVIDENCE",
    }
    assert {dec["decision"] for dec in RULE_DECISIONS.values()} <= frozen_decision_vocabulary
    for rule in per_rule_results:
        assert rule["decision"] in {
            "MIGRATION_SUPPORTED", "PARTIALLY_REPRODUCED", "STRUCTURED_REGRESSION",
            "NO_MEANINGFUL_LEGACY_DEPENDENCY", "INSUFFICIENT_EVIDENCE",
        }
        if rule["identifiability_status"] == "PARTIALLY_IDENTIFIABLE":
            assert rule["decision"] == "INSUFFICIENT_EVIDENCE", rule["rule_id"]
    # R1: the failure layer uses only frozen taxonomy values; descriptive
    # outcome labels live exclusively in the paired-outcome layer.
    assert set(taxonomy_counts) <= set(FROZEN_TAXONOMY)
    assert "STRUCTURED_PARITY" not in taxonomy_counts
    assert "STRUCTURED_IMPROVEMENT" not in taxonomy_counts
    assert not any(
        str(label).startswith("LEGACY_SHORTCUT_") for label in taxonomy_counts
    )
    assert sum(taxonomy_counts.values()) == 2
    assert paired_outcome_counts["STRUCTURED_PARITY"] == 14
    assert paired_outcome_counts["STRUCTURED_REGRESSION"] == 2
    by_case = {case["case_id"]: case for case in case_results}
    for case_id in ("g036", "g021"):
        case = by_case[case_id]
        assert case["failure_classification"] == "EVIDENCE_LINK_COVERAGE_GAP"
        assert case["secondary_failure_classifications"] == [
            "LEGACY_DEPENDENCY_WITHOUT_STRUCTURED_RECOVERY"
        ]
        assert case["paired_outcome"] == "STRUCTURED_REGRESSION"
        assert case["dependency_interpretation"] == "LEGACY_DEPENDENCY_CONFIRMED"
        assert case["diagnostic_subtype"] in {
            "EXISTING_PROVENANCE_NOT_MATERIALIZED",
            "MISSING_GOVERNED_EVIDENCE_LINK",
        }
        assert case["diagnostic_subtype"] is not None
    for case_id, case in by_case.items():
        if case_id not in {"g036", "g021"}:
            assert case["failure_classification"] is None, case_id
            assert case["paired_outcome"] == "STRUCTURED_PARITY", case_id
            assert case["diagnostic_subtype"] is None, case_id
    # R1: runtime knowledge-state accounting is complete and exact.
    state = artifact["runtime_knowledge_state"]
    assert state["repository_expected"]["object_count"] == len(SEED_OBJECT_IDS) == 24
    assert state["a2_runtime_materialized"]["object_count"] == len(RUNTIME_CURATED_OBJECT_IDS) == 22
    missing = state["missing_items"]
    assert missing["missing_runtime_object_ids"] == [
        "workflow.restgas.first_pass_poca",
        "concept.luminosityfit.luminosity_fit_model",
    ]
    assert missing["unexpected_runtime_object_ids"] == []
    assert len(missing["missing_runtime_relations"]) == 4
    assert len(missing["unexpected_runtime_relations"]) == 4
    assert missing["missing_runtime_workflow_step_ids"] == ["workflow.restgas.first_pass_poca"]
    assert missing["unexpected_runtime_workflow_step_ids"] == []
    assert set(SEED_OBJECT_IDS) & set(RUNTIME_CURATED_OBJECT_IDS) == set(RUNTIME_CURATED_OBJECT_IDS)
    seed_set = set(SEED_RELATION_TUPLES)
    runtime_set = set(RUNTIME_RELATION_TUPLES)
    assert len(seed_set & runtime_set) == 12
    assert len(seed_set - runtime_set) == 4
    assert len(runtime_set - seed_set) == 4
    assert artifact["experiment_validity_after_repair"]["formal_d3_experiment_verdict"] == "PASS"

    # --- D3-A2-R1 repair sections (attribution + runtime knowledge-state provenance) ---
    artifact["failure_taxonomy_counts"] = dict(sorted(taxonomy_counts.items()))
    artifact["paired_outcome_counts"] = dict(sorted(paired_outcome_counts.items()))
    artifact["status"] = "COMPLETE / FROZEN_THREE_ARM_COMPARISON_COMPLETE (R1 attribution and runtime-state repaired)"
    artifact["next_stage"] = {
        "recommended_task": "structured evidence-link bridging design: a separately authorized bounded stage with two audited mechanisms — (A) materialize existing governed relation/workflow evidence provenance into retrieval-addressable candidates where the provenance already exists in D1 (g036/ana_dpm.C), and (B) add genuinely missing governed evidence linkage only where no inspectable provenance exists (g021/prod_sim_hvmaps.C, PndTargetGenerator.cxx) — then a focused re-comparison of only the two STRUCTURED_REGRESSION rules",
        "executed_here": False,
        "evidence_basis": "R1 subtype audit: g036 = EXISTING_PROVENANCE_NOT_MATERIALIZED (seed relation provenance exists, A1 does not bridge it, deployed runtime additionally lacks the provenance-bearing edges); g021 = MISSING_GOVERNED_EVIDENCE_LINK (no governed provenance anywhere); ranking and D2 resolution are not the binding constraints",
        "prohibited_replacement_shapes": [
            "trigger phrase -> hardcoded file",
            "selected rule ID -> evidence_path",
            "evaluation case -> answer file",
        ],
        "required_replacement_shape": "query -> D2 object -> accepted governed relation/workflow -> governed evidence provenance -> retrievable source candidate",
    }

    output_path = args.project_root / "evaluation" / "d3_a2_three_arm_results.json"
    output_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {output_path}")
    print("verdict:", verdict)
    print("per-rule decisions:", json.dumps(decisions_by_value, sort_keys=True))
    print("taxonomy:", json.dumps(dict(sorted(taxonomy_counts.items())), sort_keys=True))


if __name__ == "__main__":
    main()
