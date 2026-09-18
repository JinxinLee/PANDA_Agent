"""Focused F6 release-identity tests for the candidate freezer.

These cover the pre-outcome infrastructure correction only: the signed
m6-benchmark-v2.6 binding, the complete prompt fingerprint, the three distinct
model-role identities, and the recorded runtime mode. Freezing a full candidate
additionally requires live Docker/Postgres/Qdrant and is exercised at freeze
time, not here.
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import panda_agent.evaluation_runner as runner
from panda_agent import candidate
from panda_agent.evaluation_runner import prompt_fingerprint
from panda_agent.qa import DEFAULT_ANSWER_POINT_MODE

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROMPT_GLOBALS = {
    "answer": "ANSWER_SYSTEM_PROMPT",
    "answer_composer": "ANSWER_COMPOSER_SYSTEM_PROMPT",
    "answer_composer_review": "ANSWER_COMPOSER_REVIEW_SYSTEM_PROMPT",
    "answer_point_coverage_review": "ANSWER_POINT_COVERAGE_REVIEW_SYSTEM_PROMPT",
    "answer_point_coverage_revision": "ANSWER_POINT_COVERAGE_REVISION_SYSTEM_PROMPT",
    "evaluation_judge": "EVALUATION_JUDGE_SYSTEM_PROMPT",
    "evidence_review": "EVIDENCE_REVIEW_SYSTEM_PROMPT",
    "query_analyzer": "QUERY_ANALYZER_SYSTEM_PROMPT",
    "rerank": "RERANK_SYSTEM_PROMPT",
    "revision": "REVISION_SYSTEM_PROMPT",
}


class PromptFingerprintTests(unittest.TestCase):
    def test_fingerprint_is_stable(self):
        self.assertEqual(prompt_fingerprint(), prompt_fingerprint())

    def test_fingerprint_covers_every_active_prompt(self):
        baseline = prompt_fingerprint()
        self.assertTrue(baseline)
        for key, global_name in PROMPT_GLOBALS.items():
            with self.subTest(prompt=key):
                original = getattr(runner, global_name)
                try:
                    setattr(runner, global_name, original + "\n altered")
                    self.assertNotEqual(prompt_fingerprint(), baseline)
                finally:
                    setattr(runner, global_name, original)


class BenchmarkIdentityTests(unittest.TestCase):
    def test_benchmark_identity_binds_newest_signed_exposed_gold(self):
        # GOLD-9: the freezer binds the same newest qualified benchmark the
        # evaluator resolves (currently m6-benchmark-v2.10), never an older
        # hard-coded authority.
        identity = candidate._benchmark_identity(PROJECT_ROOT)
        manifest = json.loads(
            (PROJECT_ROOT / "evaluation" / "benchmarks" / "v2_10" / "benchmark_manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(identity["benchmark_version"], "m6-benchmark-v2.10")
        self.assertEqual(identity["benchmark_question_count"], 120)
        self.assertEqual(identity["benchmark_dataset_sha256"], manifest["dataset_sha256"])
        self.assertIn("approved", identity["benchmark_status"])

    def test_benchmark_identity_rejects_dataset_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            benchmark_dir = root / "evaluation" / "benchmarks" / "v2_6"
            benchmark_dir.mkdir(parents=True)
            (benchmark_dir / "gold_questions.yaml").write_text("questions: []\n", encoding="utf-8")
            (benchmark_dir / "benchmark_manifest.json").write_text(
                json.dumps(
                    {
                        "benchmark_version": "m6-benchmark-v2.6",
                        "question_count": 120,
                        "status": "approved_exposed_development_benchmark_v2_6",
                        "dataset": "gold_questions.yaml",
                        "dataset_sha256": "0" * 64,
                    }
                ),
                encoding="utf-8",
            )
            # GOLD-9: a hash-mismatched directory is not qualified, so the
            # resolver skips it and the root has no frozen-able authority.
            with self.assertRaises((RuntimeError, FileNotFoundError)):
                candidate._benchmark_identity(root)


class CandidateManifestIdentityTests(unittest.TestCase):
    """The freezer must record the F4 model-role trio, the runtime mode, and
    the v2.6 benchmark binding. The full manifest requires live infrastructure,
    so the assembly contract is verified at the source level."""

    def test_manifest_source_records_required_identity_fields(self):
        source = (PROJECT_ROOT / "src" / "panda_agent" / "candidate.py").read_text(encoding="utf-8")
        for fragment in (
            'newest_signed_exposed_gold_dir',
            "runtime_verification_model_id",
            "effective_verification_model_id",
            "evaluation_judge_model_id",
            "primary_answer_point_mode",
            "benchmark_version",
            "benchmark_question_count",
            "manual_adjudications.yaml",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, source)
        self.assertNotIn('benchmarks" / "v2" / "gold_questions.yaml"', source)

    def test_recorded_mode_matches_product_default(self):
        self.assertEqual(DEFAULT_ANSWER_POINT_MODE, "production_answer_obligations_v1")


if __name__ == "__main__":
    unittest.main()
