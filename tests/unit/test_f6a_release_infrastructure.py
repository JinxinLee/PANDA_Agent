"""Focused F6-A release-score, composer-audit, and ablation-overlay tests.

Evaluation-infrastructure only: deterministic helpers with mocked vertices and
services; no scientific model calls.
"""

import hashlib
import json
import unittest
from pathlib import Path
from unittest.mock import patch

import panda_agent.evaluation_runner as runner
from panda_agent import candidate
from panda_agent.f6a_ablation import install as install_ablation
from panda_agent.f6a_composer_audit import (
    build_composer_audit_pairs,
    judge_composer_factuality,
    judge_composer_readability,
    aggregate_composer_audit,
)


class ReleaseScoreTests(unittest.TestCase):
    def test_answered_case_scores_answer_point_coverage(self):
        records = [
            {"id": "g001", "expected_status": "answered", "metrics": {"answer_point_coverage": 0.8}}
        ]
        self.assertEqual(runner.f6a_release_score(records)["release_score"], 0.8)
        self.assertEqual(runner.f6a_release_score(records)["denominator"], 1)

    def test_refusal_case_scores_expected_status_correctness(self):
        records = [
            {"id": "g002", "expected_status": "refusal", "metrics": {"expected_status_correct": True}},
            {"id": "g003", "expected_status": "refusal", "metrics": {"expected_status_correct": False}},
        ]
        self.assertEqual(runner.f6a_release_score(records)["release_score"], 0.5)

    def test_missing_metric_is_incomplete_not_zero(self):
        records = [
            {"id": "g001", "expected_status": "answered", "metrics": {"answer_point_coverage": 1.0}},
            {"id": "g002", "expected_status": "answered", "metrics": {}},
        ]
        result = runner.f6a_release_score(records)
        self.assertEqual(result["release_score"], 1.0)
        self.assertEqual(result["incomplete_case_ids"], ["g002"])
        self.assertEqual(result["denominator"], 1)

    def test_exception_case_is_incomplete(self):
        records = [{"id": "g001", "expected_status": "answered", "metrics": {"answer_point_coverage": None}, "exception": "boom"}]
        result = runner.f6a_release_score(records)
        self.assertEqual(result["incomplete_case_ids"], ["g001"])
        self.assertIsNone(result["release_score"])

    def test_denominator_reports_completeness(self):
        records = [
            {"id": f"g{index:03d}", "expected_status": "answered", "metrics": {"answer_point_coverage": 1.0}}
            for index in range(1, 5)
        ]
        result = runner.f6a_release_score(records)
        self.assertEqual(result["complete_case_count"], 4)
        self.assertEqual(result["denominator"], 4)


class _AuditVertex:
    def __init__(self, verdicts):
        self.verdicts = list(verdicts)
        self.calls = []

    def generate_json(self, prompt, schema, **kwargs):
        self.calls.append(json.loads(prompt))
        return self.verdicts.pop(0)


class ComposerAuditTests(unittest.TestCase):
    def _record(self, *, accepted=True, attempted=True, claims=2, status="answered"):
        return {
            "id": "g0042",
            "result": {
                "status": status,
                "answer": "Composed answer text.",
                "claims": [
                    {"claim_id": f"c{index}", "claim_text": f"Claim {index}.", "evidence_ids": [f"e{index}"]}
                    for index in range(1, claims + 1)
                ],
            },
            "diagnostics": {"composer": {"attempted": attempted, "accepted": accepted}},
        }

    def test_eligibility_requires_answered_accepted_multi_claim(self):
        pairs = build_composer_audit_pairs([self._record()])
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0]["case_id"], "g0042")
        self.assertEqual(len(pairs[0]["verified_claims"]), 2)

    def test_fallback_and_single_claim_and_refusal_excluded(self):
        records = [
            self._record(accepted=False),
            self._record(claims=1),
            self._record(status="insufficient_evidence"),
            self._record(attempted=False, accepted=False),
        ]
        self.assertEqual(build_composer_audit_pairs(records), [])
        # Fallback case is still reported as a diagnostic exclusion count by the
        # caller via composer diagnostics; the pair builder excludes it.

    def test_deterministic_counterpart_matches_render_verified_answer(self):
        pair = build_composer_audit_pairs([self._record()])[0]
        expected = "Claim 1. [e1]\nClaim 2. [e2]"
        self.assertEqual(pair["deterministic_answer"], expected)

    def test_factuality_judge_payload_carries_claims_and_answer_only(self):
        vertex = _AuditVertex([{"introduces_new_facts": False, "reason": ""}])
        pair = build_composer_audit_pairs([self._record()])[0]
        verdict = judge_composer_factuality(pair, vertex)
        self.assertFalse(verdict["introduces_new_facts"])
        payload = vertex.calls[0]
        self.assertEqual(set(payload), {"task", "verified_claims", "composed_answer"})
        for claim in payload["verified_claims"]:
            self.assertEqual(set(claim), {"claim_id", "claim_text"})

    def test_readability_counterbalance_maps_labels_deterministically(self):
        pair = build_composer_audit_pairs([self._record()])[0]
        even = {**pair, "case_id": "g0042"}  # even -> composed labeled A
        vertex = _AuditVertex([{"preferred": "A", "reason": ""}])
        self.assertEqual(judge_composer_readability(even, vertex)["preferred"], "composed")
        odd = {**pair, "case_id": "g0041"}  # odd -> composed labeled B
        vertex = _AuditVertex([{"preferred": "A", "reason": ""}])
        self.assertEqual(judge_composer_readability(odd, vertex)["preferred"], "deterministic")

    def test_aggregate_reports_counts_and_rate(self):
        pairs = [{} for _ in range(4)]
        factuality = [{"introduces_new_facts": False}] * 4
        readability = [{"preferred": "composed"}, {"preferred": "composed"}, {"preferred": "deterministic"}, {"preferred": "tie"}]
        aggregate = aggregate_composer_audit(pairs, factuality, readability)
        self.assertEqual(aggregate["eligible_cases"], 4)
        self.assertEqual(aggregate["composer_new_fact_rate"], 0.0)
        self.assertEqual(aggregate["composed_preferred"], 2)
        self.assertEqual(aggregate["deterministic_preferred"], 1)
        self.assertEqual(aggregate["tie"], 1)

    def test_aggregate_new_fact_rate_detects_hallucination(self):
        pairs = [{} for _ in range(2)]
        factuality = [{"introduces_new_facts": False}, {"introduces_new_facts": True}]
        aggregate = aggregate_composer_audit(pairs, factuality, [])
        self.assertEqual(aggregate["composer_new_fact_rate"], 0.5)


class AblationOverlayTests(unittest.TestCase):
    def test_install_disables_expansions_and_restores(self):
        import panda_agent.retrieval as retrieval
        from panda_agent.config import load_query_expansions

        original = retrieval.load_query_expansions
        with install_ablation() as manifest:
            self.assertEqual(manifest["ablation_id"], "disable_query_expansion_injection")
            self.assertIsNot(retrieval.load_query_expansions, original)
            disabled = retrieval.load_query_expansions(Path("configs/query_expansions.yaml"))
            self.assertEqual(disabled.rules, [])
            self.assertNotEqual(disabled.rules, load_query_expansions(Path("configs/query_expansions.yaml")).rules)
        self.assertIs(retrieval.load_query_expansions, original)


class DockerReleaseIdentityTests(unittest.TestCase):
    def test_empty_image_set_fails_option_a_contract(self):
        result = candidate._docker_release_identity({"status": "ok", "images": []})
        self.assertFalse(result["satisfied"])
        self.assertTrue(result["release_critical"])

    def test_missing_required_service_fails(self):
        result = candidate._docker_release_identity(
            {"status": "ok", "images": [{"Service": "postgres", "Image": "postgres:17-alpine"}]}
        )
        self.assertFalse(result["satisfied"])
        self.assertIn("qdrant", result["reason"])

    def test_complete_service_set_satisfies(self):
        result = candidate._docker_release_identity(
            {
                "status": "ok",
                "images": [
                    {"Service": "postgres", "Image": "postgres:17-alpine"},
                    {"Service": "qdrant", "Image": "qdrant/qdrant:v1.15.5"},
                ],
            }
        )
        self.assertTrue(result["satisfied"])

    def test_unavailable_docker_fails(self):
        result = candidate._docker_release_identity({"status": "unavailable", "error": "x"})
        self.assertFalse(result["satisfied"])


class BenchmarkAuthorityFlagTests(unittest.TestCase):
    @staticmethod
    def _manifest(*, official=True, structural=True, version="m6-benchmark-v2.6", dataset_sha256=None):
        manifest = {
            "benchmark_version": version,
            "question_count": 120,
            "status": "approved_exposed_development_benchmark_v2_6",
            "dataset": "gold_questions.yaml",
            "dataset_sha256": dataset_sha256,
            "project_official_validation": {
                "official_ready": official,
                "structurally_valid": structural,
            },
        }
        return manifest

    @staticmethod
    def _identity_with_dataset(dataset_bytes: bytes, **overrides) -> dict:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            benchmark_dir = root / "evaluation" / "benchmarks" / "v2_6"
            benchmark_dir.mkdir(parents=True)
            (benchmark_dir / "gold_questions.yaml").write_bytes(dataset_bytes)
            manifest = BenchmarkAuthorityFlagTests._manifest(
                dataset_sha256=hashlib.sha256(dataset_bytes).hexdigest(), **overrides
            )
            manifest_path = benchmark_dir / "benchmark_manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            return candidate._benchmark_identity(root)

    def test_valid_authority_accepted_and_manifest_hash_recorded(self):
        import tempfile

        identity = self._identity_with_dataset(b"questions: []\n")
        self.assertTrue(identity["benchmark_official_ready"])
        self.assertTrue(identity["benchmark_structurally_valid"])
        self.assertEqual(identity["benchmark_version"], "m6-benchmark-v2.6")
        self.assertEqual(identity["benchmark_question_count"], 120)
        with tempfile.TemporaryDirectory() as tmp:
            # recompute the manifest hash for the same fixture shape
            manifest = self._manifest(dataset_sha256=hashlib.sha256(b"questions: []\n").hexdigest())
            expected = hashlib.sha256(
                json.dumps(manifest).encode("utf-8")
            ).hexdigest()
            self.assertEqual(identity["benchmark_manifest_sha256"], expected)

    def test_official_ready_false_rejected(self):
        # GOLD-9: an unqualified directory is simply not resolved; a root with
        # no qualified benchmark raises FileNotFoundError instead of freezing.
        with self.assertRaises((RuntimeError, FileNotFoundError)):
            self._identity_with_dataset(b"questions: []\n", official=False)

    def test_structurally_valid_false_rejected(self):
        with self.assertRaises((RuntimeError, FileNotFoundError)):
            self._identity_with_dataset(b"questions: []\n", structural=False)

    def test_resolves_newest_qualified_benchmark_directory(self):
        # GOLD-9: directory discovery picks the highest qualified version, so a
        # stale v2.6 directory is not selected while a valid v2.9 exists.
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            def _make(version_dir, dataset_bytes, version):
                benchmark_dir = root / "evaluation" / "benchmarks" / version_dir
                benchmark_dir.mkdir(parents=True)
                (benchmark_dir / "gold_questions.yaml").write_bytes(dataset_bytes)
                (benchmark_dir / "benchmark_manifest.json").write_text(
                    json.dumps(
                        {
                            "benchmark_version": version,
                            "question_count": 120,
                            "status": f"approved_exposed_development_benchmark_{version_dir}",
                            "dataset": "gold_questions.yaml",
                            "dataset_sha256": hashlib.sha256(dataset_bytes).hexdigest(),
                            "project_official_validation": {
                                "official_ready": True,
                                "structurally_valid": True,
                            },
                        }
                    ),
                    encoding="utf-8",
                )

            _make("v2_6", b"v26 questions\n", "m6-benchmark-v2.6")
            _make("v2_9", b"v29 questions\n", "m6-benchmark-v2.9")
            self.assertEqual(
                candidate._benchmark_identity(root)["benchmark_version"],
                "m6-benchmark-v2.9",
            )

    def test_manifest_hash_sensitivity(self):
        # Sensitivity is asserted against the active authoritative benchmark
        # directory (newest signed exposed Gold), not a hard-coded version.
        from panda_agent.evaluation import newest_signed_exposed_gold_dir

        active_dir = newest_signed_exposed_gold_dir(Path.cwd())
        manifest_path = active_dir / "benchmark_manifest.json"
        original = manifest_path.read_bytes()
        before = candidate._benchmark_identity(Path.cwd())["benchmark_manifest_sha256"]
        try:
            manifest_path.write_bytes(original + b"\n")
            after = candidate._benchmark_identity(Path.cwd())["benchmark_manifest_sha256"]
            self.assertNotEqual(before, after)
        finally:
            manifest_path.write_bytes(original)
        self.assertEqual(candidate._benchmark_identity(Path.cwd())["benchmark_manifest_sha256"], before)

    def test_missing_manual_adjudications_is_optional_not_fatal(self):
        # GOLD-9 §5.4: Gold v2.9 carries no manual_adjudications.yaml; the
        # freezer records the absence (hash None) instead of requiring a
        # legacy adjudication artifact copied forward.
        from types import SimpleNamespace
        from unittest import mock

        from panda_agent.candidate import _current_manifest

        settings = SimpleNamespace(
            generation_model="g",
            verification_model=None,
            effective_verification_model="g",
            evaluation_judge_model="j",
            embedding_model="e",
            embedding_dimensions=3072,
            location="global",
        )
        with mock.patch("panda_agent.candidate.VertexSettings") as vertex_settings, mock.patch(
            "panda_agent.candidate.IndexIdentity"
        ) as index_identity, mock.patch(
            "panda_agent.candidate._docker_images",
            return_value={"status": "ok", "images": []},
        ):
            vertex_settings.from_env.return_value = settings
            # Match the real stored index identity so the freezer's authority
            # checks pass and only the adjudications disposition is exercised.
            index_identity.from_settings.return_value.fingerprint.return_value = (
                "8172f9a640e62977be6e911bfb4848ce3aecd0994f1f3ba51a0985bffec62cb9"
            )
            manifest = _current_manifest(Path.cwd(), "authority-binding-probe")
        self.assertIsNone(manifest["manual_adjudications_hash"])
        self.assertIn("gold_questions.yaml", manifest["protected_file_hashes"])
        self.assertNotIn("manual_adjudications.yaml", manifest["protected_file_hashes"])

    def test_old_checkout_falls_back_to_historical_chain(self):
        # GOLD-9: an old checkout without any signed exposed benchmark still
        # resolves through the historical fallback chain (v2.2 raw file).
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            legacy = root / "evaluation" / "benchmarks" / "v2_2"
            legacy.mkdir(parents=True)
            (legacy / "gold_questions.yaml").write_text("questions: []\n", encoding="utf-8")
            from panda_agent.evaluation_runner import default_gold_dataset_path

            self.assertEqual(
                default_gold_dataset_path(root),
                legacy / "gold_questions.yaml",
            )


class ManifestIdentitySourceTests(unittest.TestCase):
    def test_manifest_records_implementation_git_commit(self):
        source = (Path(__file__).resolve().parents[2] / "src" / "panda_agent" / "candidate.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("implementation_git_commit", source)
        self.assertIn("repository_identity", source)

    def test_freeze_requires_clean_implementation_tree(self):
        source = (Path(__file__).resolve().parents[2] / "src" / "panda_agent" / "candidate.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("git", source)
        self.assertIn("must be clean", source)


class ProductScopeSelectorTests(unittest.TestCase):
    """F6-A Stage A0: the reviewed product-language calibration must be
    mechanically reconcilable with the current Gold, the loader must prefer the
    versioned successor, and the freezer must record the calibration identity
    plus the exact selector output hash."""

    PROJECT_ROOT = Path(__file__).resolve().parents[2]

    def test_successor_calibration_is_loaded_and_compatible(self):
        from panda_agent.evaluation import (
            calibration_compatibility,
            load_gold_dataset,
            load_product_language_calibration,
        )
        from panda_agent.evaluation_runner import default_gold_dataset_path

        calibration = load_product_language_calibration(self.PROJECT_ROOT)
        self.assertIsNotNone(calibration)
        self.assertEqual(
            calibration["calibration_id"], "phase_b_t3_product_language_scope_v8"
        )
        dataset = load_gold_dataset(default_gold_dataset_path(self.PROJECT_ROOT))
        self.assertEqual(dataset.benchmark_version, "m6-benchmark-v2.11")
        compatibility = calibration_compatibility(
            calibration, dataset, dataset_path=default_gold_dataset_path(self.PROJECT_ROOT)
        )
        self.assertTrue(compatibility["compatible"], compatibility["reason"])

    def test_reconciliation_mechanically_reproduces_declared_ids(self):
        from panda_agent.evaluation import (
            derive_product_language_ids,
            load_gold_dataset,
            load_product_language_calibration,
        )
        from panda_agent.evaluation_runner import default_gold_dataset_path

        calibration = load_product_language_calibration(self.PROJECT_ROOT)
        dataset = load_gold_dataset(default_gold_dataset_path(self.PROJECT_ROOT))
        derived_en, derived_non = derive_product_language_ids(dataset, calibration)
        self.assertEqual(sorted(derived_en), sorted(calibration["formal_english_ids"]))
        self.assertEqual(sorted(derived_non), sorted(calibration["non_english_ids"]))

    def test_reconciliation_records_provenance_and_no_fresh_review_claim(self):
        calibration_path = (
            self.PROJECT_ROOT / "evaluation" / "baselines" / "manifests"
            / "phase_b_t3_product_language_scope_v3.json"
        )
        calibration = json.loads(calibration_path.read_text(encoding="utf-8"))
        self.assertEqual(
            calibration["predecessor_calibration"]["calibration_id"],
            "phase_b_t3_product_language_scope_v2",
        )
        self.assertEqual(calibration["source_gold"]["sha256"], "6f12d54b4db3fdd87fb30670e730ffd8c025a55a968c90a4ea63ab7cecdb878f")
        self.assertTrue(calibration["reconciliation"]["no_fresh_human_review_claimed"])
        self.assertEqual(calibration["reconciliation"]["mechanical_verification"]["formal_english_count"], 59)

    def test_freezer_records_calibration_and_selector_identity(self):
        identity = candidate._product_scope_identity(self.PROJECT_ROOT)
        self.assertEqual(
            identity["product_language_calibration_id"],
            "phase_b_t3_product_language_scope_v8",
        )
        self.assertEqual(identity["formal_product_scope_selector_count"], 59)
        self.assertEqual(
            identity["formal_product_scope_selector_sha256"],
            "e27ef67a866274b4a8441b789ca78fc3ccb7e022eed537c7442e15230777a0e5",
        )
        self.assertEqual(
            identity["product_language_calibration_sha256"],
            "6079baaa08f9bee4cd9d63f6acf7fb2cb999743e7c596edd105378b07c1293e8",
        )

    def test_selector_hash_is_deterministic(self):
        first = candidate._product_scope_identity(self.PROJECT_ROOT)
        second = candidate._product_scope_identity(self.PROJECT_ROOT)
        self.assertEqual(
            first["formal_product_scope_selector_sha256"],
            second["formal_product_scope_selector_sha256"],
        )

    def test_runner_computes_product_gate_from_selector_completeness(self):
        source = (
            self.PROJECT_ROOT / "src" / "panda_agent" / "evaluation_runner.py"
        ).read_text(encoding="utf-8")
        self.assertIn("product_selector_complete", source)
        self.assertNotIn("and full_dev_execution:", source)


if __name__ == "__main__":
    unittest.main()
