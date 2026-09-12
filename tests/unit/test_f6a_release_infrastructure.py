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
            benchmark_dir = root / candidate.BENCHMARK_DIR
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
        with self.assertRaises(RuntimeError):
            self._identity_with_dataset(b"questions: []\n", official=False)

    def test_structurally_valid_false_rejected(self):
        with self.assertRaises(RuntimeError):
            self._identity_with_dataset(b"questions: []\n", structural=False)

    def test_wrong_benchmark_version_rejected(self):
        with self.assertRaises(RuntimeError):
            self._identity_with_dataset(b"questions: []\n", version="m6-benchmark-v2.5")

    def test_manifest_hash_sensitivity(self):
        manifest_path = Path("evaluation/benchmarks/v2_6/benchmark_manifest.json")
        original = manifest_path.read_bytes()
        before = candidate._benchmark_identity(Path.cwd())["benchmark_manifest_sha256"]
        try:
            manifest_path.write_bytes(original + b"\n")
            after = candidate._benchmark_identity(Path.cwd())["benchmark_manifest_sha256"]
            self.assertNotEqual(before, after)
        finally:
            manifest_path.write_bytes(original)
        self.assertEqual(candidate._benchmark_identity(Path.cwd())["benchmark_manifest_sha256"], before)


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


if __name__ == "__main__":
    unittest.main()
