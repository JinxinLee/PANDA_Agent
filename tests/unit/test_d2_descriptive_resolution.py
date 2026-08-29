"""Unit tests for D2-A1 deterministic descriptive (Tier D) resolution.

Fixtures are source-grounded: positive-case entity title/text come from
configs/seed_objects.yaml (loaded via yaml). Competitor entities use
title/object_id/object_type features only, as specified by the D2-A1 task.
Pure unittest; no DB, network, or model.
"""

from __future__ import annotations

import unittest
from pathlib import Path

import yaml

from panda_agent.descriptive_resolution import (
    DescriptiveDecision,
    GovernedEntity,
    build_descriptive_index,
    evaluate_descriptive_mentions,
    _tokenize,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SEED_OBJECTS_PATH = REPO_ROOT / "configs" / "seed_objects.yaml"

FIT_MODEL_ID = "concept.luminosityfit.luminosity_fit_model"
RESTGAS_ACCEPTANCE_ID = "workflow.restgas_aware_luminosity_acceptance"
FIRST_PASS_POCA_ID = "workflow.restgas.first_pass_poca"
PID_ROOT_ID = "data_product.restgas.pid_root"

LUMINOSITY_QUESTION = "the model used to extract luminosity from the LMD angular distribution"
POCA_QUESTION = "the step that reads the first PID output and writes the boost ROOT file"


def _load_seed_objects() -> dict[str, dict]:
    with open(SEED_OBJECTS_PATH, encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return {obj["object_id"]: obj for obj in data["objects"]}


def _seed_entity(object_id: str) -> GovernedEntity:
    """GovernedEntity built from the real seed_objects.yaml entry."""
    raw = _load_seed_objects()[object_id]
    return GovernedEntity(
        object_id=raw["object_id"],
        object_type=raw["object_type"],
        source_id="configs/seed_objects.yaml",
        source_version_id="test-fixture",
        title=raw["title"],
        text=raw.get("text", "") or "",
        identity_role=raw.get("identity_role", "canonical"),
    )


def _title_only_entity(
    object_id: str,
    object_type: str,
    title: str,
    identity_role: str = "canonical",
) -> GovernedEntity:
    """Competitor fixture: title/object_id/object_type features, no text."""
    return GovernedEntity(
        object_id=object_id,
        object_type=object_type,
        source_id="test-fixture",
        source_version_id="test-fixture",
        title=title,
        text="",
        identity_role=identity_role,
    )


def _decision_for(
    decisions: list[DescriptiveDecision],
    object_id: str,
) -> DescriptiveDecision:
    matches = [d for d in decisions if d.candidate_object_id == object_id]
    assert matches, f"no decision for {object_id} in {[d.candidate_object_id for d in decisions]}"
    return matches[0]


class TestLuminosityFitModelPositive(unittest.TestCase):
    def test_fit_model_eligible_and_dominant_related_workflow_rejected(self) -> None:
        fit_model = _seed_entity(FIT_MODEL_ID)
        related_workflow = _title_only_entity(
            RESTGAS_ACCEPTANCE_ID, "workflow", "Restgas-aware luminosity acceptance workflow"
        )
        index = build_descriptive_index([fit_model, related_workflow])

        decisions = evaluate_descriptive_mentions(
            LUMINOSITY_QUESTION, ["the model used to extract luminosity"], index
        )

        fit_decision = _decision_for(decisions, FIT_MODEL_ID)
        self.assertTrue(fit_decision.eligible)
        self.assertTrue(fit_decision.dominance)
        self.assertIsNone(fit_decision.rejection_reason)
        self.assertGreaterEqual(fit_decision.feature_count, 2)
        self.assertEqual(
            set(fit_decision.matched_features),
            {"model", "luminosity", "angular", "distribution"},
        )
        self.assertEqual(
            {entry["object_id"] for entry in fit_decision.competing}, {RESTGAS_ACCEPTANCE_ID}
        )

        # Related-but-not-identical workflow: insufficient features (weak signal).
        workflow_decision = _decision_for(decisions, RESTGAS_ACCEPTANCE_ID)
        self.assertFalse(workflow_decision.eligible)
        self.assertFalse(workflow_decision.dominance)
        self.assertEqual(workflow_decision.rejection_reason, "single_feature")
        self.assertEqual(workflow_decision.matched_features, ("luminosity",))
        self.assertEqual(workflow_decision.feature_count, 1)

        # Deterministic ordering: dominant candidate first.
        self.assertEqual(decisions[0].candidate_object_id, FIT_MODEL_ID)


class TestFirstPassPocaPositive(unittest.TestCase):
    def test_poca_workflow_dominates_pid_root_data_product(self) -> None:
        poca = _seed_entity(FIRST_PASS_POCA_ID)
        pid_root = _title_only_entity(PID_ROOT_ID, "data_product", "*_pid.root")
        relation_features = {
            FIRST_PASS_POCA_ID: (
                "CONSUMES data_product.restgas.pid_root",
                "PRODUCES data_product.restgas.boost_root",
                "*_pid.root",
                "*_boost.root",
            )
        }
        index = build_descriptive_index([poca, pid_root], relation_features)

        decisions = evaluate_descriptive_mentions(POCA_QUESTION, ["the first-pass step"], index)

        poca_decision = _decision_for(decisions, FIRST_PASS_POCA_ID)
        self.assertTrue(poca_decision.eligible)
        self.assertTrue(poca_decision.dominance)
        self.assertIsNone(poca_decision.rejection_reason)
        self.assertEqual(
            set(poca_decision.matched_features),
            {"first", "pid", "output", "writes", "boost", "root"},
        )
        self.assertEqual(len(poca_decision.competing), 1)
        self.assertEqual(poca_decision.competing[0]["object_id"], PID_ROOT_ID)
        self.assertEqual(poca_decision.competing[0]["matched_features"], ("pid", "root"))

        # Competitor matches only pid/root and is dominated.
        pid_decision = _decision_for(decisions, PID_ROOT_ID)
        self.assertEqual(pid_decision.matched_features, ("pid", "root"))
        self.assertEqual(pid_decision.feature_count, 2)
        self.assertTrue(pid_decision.eligible)
        self.assertFalse(pid_decision.dominance)
        self.assertEqual(pid_decision.rejection_reason, "tied_with_competitor")


class TestSingleFeatureRejection(unittest.TestCase):
    def test_one_matched_feature_is_never_eligible(self) -> None:
        index = build_descriptive_index([_seed_entity(FIT_MODEL_ID)])

        decisions = evaluate_descriptive_mentions("the model", ["the model"], index)

        self.assertTrue(decisions, "expected a decision row for the single match")
        fit_decision = _decision_for(decisions, FIT_MODEL_ID)
        self.assertEqual(fit_decision.matched_features, ("model",))
        self.assertEqual(fit_decision.feature_count, 1)
        self.assertFalse(fit_decision.eligible)
        self.assertFalse(fit_decision.dominance)
        self.assertEqual(fit_decision.rejection_reason, "single_feature")
        self.assertFalse(any(d.eligible for d in decisions))


class TestTieIsAmbiguous(unittest.TestCase):
    def test_equal_feature_counts_leave_neither_dominant(self) -> None:
        alpha = _title_only_entity(
            "concept.demo.alpha_reconstruction", "physics_concept", "Sparse reconstruction efficiency"
        )
        beta = _title_only_entity(
            "concept.demo.beta_reconstruction", "physics_concept", "Dense reconstruction efficiency"
        )
        index = build_descriptive_index([alpha, beta])

        decisions = evaluate_descriptive_mentions(
            "the reconstruction efficiency comparison", ["reconstruction efficiency"], index
        )

        self.assertEqual(len(decisions), 2)
        alpha_decision = _decision_for(decisions, alpha.object_id)
        beta_decision = _decision_for(decisions, beta.object_id)
        for decision in (alpha_decision, beta_decision):
            self.assertTrue(decision.eligible)
            self.assertFalse(decision.dominance)
            self.assertEqual(decision.rejection_reason, "tied_with_competitor")
            self.assertEqual(decision.feature_count, 2)
            self.assertEqual(
                set(decision.matched_features), {"reconstruction", "efficiency"}
            )
        self.assertEqual(
            {entry["object_id"] for entry in alpha_decision.competing}, {beta.object_id}
        )
        self.assertEqual(
            {entry["object_id"] for entry in beta_decision.competing}, {alpha.object_id}
        )


class TestNonCanonicalExclusion(unittest.TestCase):
    def test_source_native_entity_never_eligible_despite_overlap(self) -> None:
        factory = GovernedEntity(
            object_id="macro.panda.pnd_lmd_model_factory",
            object_type="macro",
            source_id="test-fixture",
            source_version_id="test-fixture",
            title="PndLmdModelFactory",
            text="Factory that creates the luminosity fit model for the angular distribution.",
            identity_role="source_native",
        )
        index = build_descriptive_index([factory])

        decisions = evaluate_descriptive_mentions(
            LUMINOSITY_QUESTION, ["the model factory"], index
        )

        factory_decision = _decision_for(decisions, factory.object_id)
        self.assertFalse(factory_decision.eligible)
        self.assertFalse(factory_decision.dominance)
        self.assertEqual(factory_decision.rejection_reason, "non_canonical")
        self.assertGreaterEqual(factory_decision.feature_count, 2)


class TestDeterminism(unittest.TestCase):
    def test_same_inputs_produce_identical_decisions_and_order(self) -> None:
        poca = _seed_entity(FIRST_PASS_POCA_ID)
        pid_root = _title_only_entity(PID_ROOT_ID, "data_product", "*_pid.root")
        relation_features = {
            FIRST_PASS_POCA_ID: ("CONSUMES data_product.restgas.pid_root", "*_pid.root")
        }
        index = build_descriptive_index([poca, pid_root], relation_features)

        first = evaluate_descriptive_mentions(POCA_QUESTION, ["the first-pass step"], index)
        second = evaluate_descriptive_mentions(POCA_QUESTION, ["the first-pass step"], index)

        self.assertEqual(first, second)
        counts = [d.feature_count for d in first]
        self.assertEqual(counts, sorted(counts, reverse=True))
        for count in {d.feature_count for d in first}:
            ids = [d.candidate_object_id for d in first if d.feature_count == count]
            self.assertEqual(ids, sorted(ids))


class TestTokenization(unittest.TestCase):
    def test_camel_case_and_snake_case_splitting(self) -> None:
        self.assertEqual(_tokenize("PndLmdModelFactory"), ("pnd", "lmd", "model", "factory"))
        self.assertEqual(_tokenize("luminosity_fit_model"), ("luminosity", "fit", "model"))
        self.assertEqual(_tokenize("*_pid_final.root"), ("pid", "final", "root"))
        self.assertEqual(_tokenize("RestgasDetermination"), ("restgas", "determination"))
        self.assertEqual(_tokenize("CONSUMES data_product.restgas.pid_root"),
                         ("consumes", "data", "product", "restgas", "pid", "root"))

    def test_short_tokens_and_stopwords_dropped(self) -> None:
        self.assertEqual(_tokenize("a C is at by or"), ())
        self.assertEqual(_tokenize("the model used to extract"), ("model", "extract"))
        self.assertEqual(_tokenize("Restgas-aware luminosity"), ("restgas", "aware", "luminosity"))


if __name__ == "__main__":
    unittest.main()
