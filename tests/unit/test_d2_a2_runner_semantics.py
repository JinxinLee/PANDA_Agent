"""D2-A2R1 focused T0: evaluation-semantics self-checks for the D2-A2 runner.

Tests the pure comparison/classification semantics of
``evaluation/scripts/d2_a2_runner.py`` with synthetic resolutions — no live
DB, no model, no network.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

_EVAL_SCRIPTS_DIR = (
    Path(__file__).resolve().parents[2] / "evaluation" / "scripts"
)
_MODULE_PATH = _EVAL_SCRIPTS_DIR / "d2_a2_runner.py"
# The runner imports its sibling state module by top-level name; make the
# script directory importable before loading it.
if str(_EVAL_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_EVAL_SCRIPTS_DIR))
_spec = importlib.util.spec_from_file_location("d2_a2_runner", _MODULE_PATH)
d2_a2_runner = importlib.util.module_from_spec(_spec)
sys.modules["d2_a2_runner"] = d2_a2_runner
_spec.loader.exec_module(d2_a2_runner)

from panda_agent.entity_resolution import (  # noqa: E402
    D2Evidence,
    D2Resolution,
    RESOLVED_UNIQUE,
    AMBIGUOUS,
    UNRESOLVED,
    REJECTED_VERSION,
)


def _resolution(
    mention_text: str,
    status: str,
    *,
    matched_object_id: str | None = None,
    canonical_object_id: str | None = None,
    tier: str | None = None,
    kind: str | None = None,
    descriptive: bool = False,
    detail: str = "",
) -> D2Resolution:
    evidence = []
    if tier is not None:
        evidence.append(
            D2Evidence(
                tier=tier,
                kind=kind or "test",
                matched_value=mention_text,
                object_id=matched_object_id or "",
                detail=detail,
            )
        )
    return D2Resolution(
        mention_text=mention_text,
        mention_kind="descriptive" if descriptive else "explicit_identifier",
        support_span=mention_text,
        status=status,
        matched_object_id=matched_object_id,
        canonical_object_id=canonical_object_id,
        evidence=evidence,
        diagnostics={
            "canonicalization": False,
            "descriptive_inference": descriptive,
            "corrective": False,
            "correction_message": None,
            "identity_authority": status == RESOLVED_UNIQUE,
            "ambiguity_reason": None,
            "abstention_reason": None,
            "rejection_reasons": [],
        },
    )


def _bucket(
    expected_status,
    resolutions,
    *,
    expected_object_ids=(),
    expected_canonical_object_ids=(),
    require_all=False,
    invalid=False,
    isolation_tokens=None,
    allowed_context_object_ids=(),
):
    classified = d2_a2_runner._classify_case_decision(
        expected_status=expected_status,
        resolutions=resolutions,
        required_target_ids=set(expected_object_ids),
        expected_canonical_object_ids=set(expected_canonical_object_ids),
        allowed_context_object_ids=set(allowed_context_object_ids),
        require_all_targets=require_all,
        invalid=invalid,
        isolation_tokens=isolation_tokens or {},
    )
    return classified["decision"]


class SingleTargetTests(unittest.TestCase):
    def test_correct_expected_target_passes(self) -> None:
        bucket = _bucket(
            RESOLVED_UNIQUE,
            [_resolution("m", RESOLVED_UNIQUE, matched_object_id="object.a", tier="S", kind="exact_symbol")],
            expected_object_ids=["object.a"],
        )
        self.assertEqual(bucket, "correct_resolve")

    def test_wrong_identity_is_wrong_resolve(self) -> None:
        bucket = _bucket(
            RESOLVED_UNIQUE,
            [_resolution("m", RESOLVED_UNIQUE, matched_object_id="object.b")],
            expected_object_ids=["object.a"],
        )
        self.assertEqual(bucket, "wrong_resolve")


class MultiTargetTests(unittest.TestCase):
    def test_all_targets_resolved_passes(self) -> None:
        resolutions = [
            _resolution("mA", RESOLVED_UNIQUE, matched_object_id="concept.a"),
            _resolution("mB", RESOLVED_UNIQUE, matched_object_id="workflow.b"),
        ]
        bucket = _bucket(
            RESOLVED_UNIQUE,
            resolutions,
            expected_object_ids=["concept.a", "workflow.b"],
            require_all=True,
        )
        self.assertEqual(bucket, "correct_resolve")

    def test_only_one_of_two_targets_fails(self) -> None:
        resolutions = [
            _resolution("mA", RESOLVED_UNIQUE, matched_object_id="concept.a")
        ]
        # One correct target resolved, the other missing, and no incorrect
        # identity asserted: per the frozen D2-A2R1 semantics this is
        # wrong_abstain (expected resolution not fully produced; no confident
        # incorrect identity).
        bucket = _bucket(
            RESOLVED_UNIQUE,
            resolutions,
            expected_object_ids=["concept.a", "workflow.b"],
            require_all=True,
        )
        self.assertEqual(bucket, "wrong_abstain")


class InvalidCaseTests(unittest.TestCase):
    def test_invalid_case_excluded_from_quantitative_buckets(self) -> None:
        bucket = _bucket(
            RESOLVED_UNIQUE,
            [_resolution("m", RESOLVED_UNIQUE, matched_object_id="object.a")],
            invalid=True,
        )
        # D2-A2R2 §37: invalid cases use CASE_INVALID, not not_applicable,
        # and are excluded from the authoritative valid-case accounting.
        self.assertEqual(bucket, "CASE_INVALID")


class NegativeCaseTests(unittest.TestCase):
    def test_correct_abstention_has_no_fpr(self) -> None:
        bucket = _bucket(
            UNRESOLVED, [_resolution("m", UNRESOLVED)]
        )
        self.assertEqual(bucket, "correct_abstain")

    def test_confident_wrong_resolution_is_fpr(self) -> None:
        bucket = _bucket(
            UNRESOLVED,
            [_resolution("m", RESOLVED_UNIQUE, matched_object_id="object.a")],
        )
        self.assertEqual(bucket, "wrong_resolve")

    def test_rejection_with_fallback_confident_resolve_is_fpr(self) -> None:
        bucket = _bucket(
            REJECTED_VERSION,
            [
                _resolution("identifier", REJECTED_VERSION),
                _resolution("whole question", RESOLVED_UNIQUE, matched_object_id="workflow.x"),
            ],
        )
        self.assertEqual(bucket, "wrong_resolve")

    def test_expected_ambiguous_correct(self) -> None:
        bucket = _bucket(AMBIGUOUS, [_resolution("m", AMBIGUOUS)])
        self.assertEqual(bucket, "correct_ambiguous")


class MetricConsistencyTests(unittest.TestCase):
    def test_metric_consistency_assertions(self) -> None:
        records = [
            {"case_invalid": False, "not_applicable": False, "primary_failure_type": None},
            {"case_invalid": False, "not_applicable": False, "primary_failure_type": None},
        ]
        metrics = {
            "case_counts": {"valid": 2, "not_applicable": 0},
            "decision_accounting": {
                "correct_resolve": 1,
                "wrong_ambiguous": 1,
            },
            "resolution_accuracy": {"numerator": 1, "denominator": 2, "value": 0.5},
        }
        problems = d2_a2_runner._validate_metric_consistency(records, metrics)
        self.assertEqual(problems, [])

    def test_metric_consistency_detects_mismatch(self) -> None:
        records = [
            {"case_invalid": False, "not_applicable": False, "primary_failure_type": None},
            {"case_invalid": False, "not_applicable": False, "primary_failure_type": None},
        ]
        metrics = {
            "case_counts": {"valid": 2, "not_applicable": 0},
            "decision_accounting": {
                "correct_resolve": 0,
                "wrong_ambiguous": 1,
            },
            "resolution_accuracy": {"numerator": 1, "denominator": 2, "value": 0.5},
        }
        problems = d2_a2_runner._validate_metric_consistency(records, metrics)
        self.assertTrue(problems)


class ContextScopingTests(unittest.TestCase):
    def test_allowed_context_is_not_wrong_resolve(self) -> None:
        # Primary target ambiguous + allowed context confidently resolved:
        # wrong_ambiguous, never wrong_resolve.
        bucket = _bucket(
            RESOLVED_UNIQUE,
            [
                _resolution("m", AMBIGUOUS),
                _resolution("ctx", RESOLVED_UNIQUE, matched_object_id="object.ctx"),
            ],
            expected_object_ids=["object.primary"],
            allowed_context_object_ids=["object.ctx"],
        )
        self.assertEqual(bucket, "wrong_ambiguous")

    def test_unrelated_confident_identity_is_wrong_resolve(self) -> None:
        bucket = _bucket(
            RESOLVED_UNIQUE,
            [
                _resolution("m", AMBIGUOUS),
                _resolution("unrelated", RESOLVED_UNIQUE, matched_object_id="object.x"),
            ],
            expected_object_ids=["object.primary"],
            allowed_context_object_ids=["object.ctx"],
        )
        self.assertEqual(bucket, "wrong_resolve")

    def test_primary_success_with_allowed_context_is_correct(self) -> None:
        resolutions = [
            _resolution("primary", RESOLVED_UNIQUE, matched_object_id="object.primary"),
            _resolution("ctx", RESOLVED_UNIQUE, matched_object_id="object.ctx"),
        ]
        bucket = _bucket(
            RESOLVED_UNIQUE,
            resolutions,
            expected_object_ids=["object.primary"],
            allowed_context_object_ids=["object.ctx"],
        )
        self.assertEqual(bucket, "correct_resolve")


class CanonicalizationDenominatorTests(unittest.TestCase):
    def test_direct_governed_id_excluded_from_explicit_canonicalization(self) -> None:
        # C01: direct governed ID — no explicit canonicalization operation.
        records = [
            {
                "case_id": "C01",
                "case_invalid": False,
                "not_applicable": False,
                "correct": True,
                "expected_resolution_kind": "true_identity",
                "expects_explicit_canonicalization": False,
                "primary_failure_type": None,
                "evidence_valid": True,
            },
        ]
        metrics = {
            "case_counts": {"valid": 1, "not_applicable": 0},
            "decision_accounting": {"correct_resolve": 1},
            "explicit_canonicalization_accuracy": d2_a2_runner._metric(0, 0),
        }
        problems = d2_a2_runner._validate_metric_consistency(records, metrics)
        self.assertEqual(problems, [])

    def test_accepted_alias_enters_explicit_canonicalization(self) -> None:
        records = [
            {
                "case_id": "C07",
                "case_invalid": False,
                "not_applicable": False,
                "correct": True,
                "expected_resolution_kind": "true_identity",
                "expects_explicit_canonicalization": True,
                "explicit_canonicalization_valid": True,
                "primary_failure_type": None,
                "evidence_valid": True,
            },
        ]
        metrics = {
            "case_counts": {"valid": 1, "not_applicable": 0},
            "decision_accounting": {"correct_resolve": 1},
            "explicit_canonicalization_accuracy": d2_a2_runner._metric(1, 1),
        }
        problems = d2_a2_runner._validate_metric_consistency(records, metrics)
        self.assertEqual(problems, [])

    def test_explicit_canonicalization_failure_fails_metric(self) -> None:
        records = [
            {
                "case_id": "C07-bad",
                "case_invalid": False,
                "not_applicable": False,
                "correct": False,
                "expected_resolution_kind": "true_identity",
                "expects_explicit_canonicalization": True,
                "explicit_canonicalization_valid": False,
                "primary_failure_type": "FALSE_CANONICALIZATION",
                "evidence_valid": True,
            },
        ]
        metrics = {
            "case_counts": {"valid": 1, "not_applicable": 0},
            "decision_accounting": {"wrong_resolve": 1},
            "failure_taxonomy_counts": {"FALSE_CANONICALIZATION": 1},
            "explicit_canonicalization_accuracy": d2_a2_runner._metric(0, 1),
        }
        problems = d2_a2_runner._validate_metric_consistency(records, metrics)
        self.assertEqual(problems, [])


class CanonicalSemanticsTests(unittest.TestCase):
    def test_direct_canonical_match_satisfies(self) -> None:
        resolution = _resolution(
            "m", RESOLVED_UNIQUE, matched_object_id="concept.a", canonical_object_id=None
        )
        self.assertTrue(
            d2_a2_runner._canonical_match(resolution, {"concept.a"})
        )

    def test_explicit_canonicalization_satisfies(self) -> None:
        resolution = _resolution(
            "m",
            RESOLVED_UNIQUE,
            matched_object_id="data_product.x",
            canonical_object_id="data_product.x",
            tier="G",
            kind="true_alias",
        )
        self.assertTrue(
            d2_a2_runner._canonical_match(resolution, {"data_product.x"})
        )

    def test_wrong_canonical_target_fails(self) -> None:
        resolution = _resolution(
            "m", RESOLVED_UNIQUE, matched_object_id="concept.a", canonical_object_id="concept.b"
        )
        self.assertFalse(
            d2_a2_runner._canonical_match(resolution, {"concept.a"})
        )


class IsolationTests(unittest.TestCase):
    def test_isolation_leak_detected(self) -> None:
        resolution = _resolution(
            "luminosity fit model",
            AMBIGUOUS,
            tier="D",
            kind="descriptive_inferential",
            descriptive=True,
            detail="matched=['luminosity', 'fit', 'model', 'poca', 'workflow']",
        )
        valid, details = d2_a2_runner._evaluate_isolation(
            resolutions=[resolution],
            isolation_tokens={"luminosity fit model": ["poca", "workflow"]},
        )
        self.assertFalse(valid)
        self.assertTrue(any("poca" in detail for detail in details))

    def test_isolation_clean(self) -> None:
        resolution = _resolution(
            "luminosity fit model",
            RESOLVED_UNIQUE,
            tier="D",
            kind="descriptive_inferential",
            descriptive=True,
            detail="matched=['luminosity', 'fit', 'model']",
        )
        valid, details = d2_a2_runner._evaluate_isolation(
            resolutions=[resolution],
            isolation_tokens={"luminosity fit model": ["poca", "workflow"]},
        )
        self.assertTrue(valid)


def _fixture_results() -> dict:
    """Synthetic results artifact shaped like the D2-A2 runner output,
    including deliberately bulky per-case receipt payloads that the compact
    report projection must exclude."""

    return {
        "run_provenance": {
            "head": "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
            "baseline_commit": "67eff2b",
            "case_artifact_path": "evaluation/d2_a2_terminology_cases.yaml",
            "state_type": "deterministic_in_memory_d1_compatible",
            "state_valid": True,
            "timestamp_utc": "2026-01-01T00:00:00+00:00",
            "case_count": 2,
        },
        "state_validation": {
            "state_type": "deterministic_in_memory_d1_compatible",
            "object_count": 32,
            "valid": True,
        },
        "metrics": {
            "case_counts": {
                "total": 2,
                "valid": 2,
                "invalid": 0,
                "invalid_case_ids": [],
                "not_applicable": 0,
                "correct": 1,
            },
            "failure_taxonomy_counts": {"COMPETITION_AMBIGUITY": 1},
            "decision_accounting": {
                "correct_resolve": 1,
                "wrong_resolve": 0,
                "correct_abstain": 0,
                "wrong_abstain": 0,
                "correct_ambiguous": 0,
                "wrong_ambiguous": 1,
                "not_applicable": 0,
            },
            "case_validity": {"numerator": 2, "denominator": 2, "value": 1.0},
            "resolution_accuracy": {"numerator": 1, "denominator": 1, "value": 1.0},
            "descriptive_resolution_summary": {
                "descriptive_positive_cases": 0,
                "descriptive_correctly_resolved": 0,
                "descriptive_ambiguous": 0,
                "descriptive_unresolved": 0,
                "descriptive_wrong_confident": 0,
            },
            "corrective_handling_correct": 0,
            "corrective_handling_incorrect": 0,
        },
        "category_summaries": {
            "ambiguous_terminology": {
                "cases": 1,
                "applicable": 1,
                "correct": 0,
                "incorrect": 1,
                "not_applicable": 0,
                "case_invalid": 0,
                "false_positive_resolutions": 0,
                "decisions": {"wrong_ambiguous": 1},
                "failure_types": {"COMPETITION_AMBIGUITY": 1},
            },
            "exact_canonical_terminology": {
                "cases": 1,
                "applicable": 1,
                "correct": 1,
                "incorrect": 0,
                "not_applicable": 0,
                "case_invalid": 0,
                "false_positive_resolutions": 0,
                "decisions": {"correct_resolve": 1},
                "failure_types": {},
            },
        },
        "per_case_results": [
            {
                "case_id": "C01",
                "actual": {
                    "receipt": {
                        "resolutions": [
                            {
                                "mention_text": "luminosity fit",
                                "candidates": [{"object_id": "object.a"}],
                            }
                        ]
                    },
                    "statuses": ["RESOLVED_UNIQUE"],
                },
            },
            {
                "case_id": "C02",
                "actual": {"receipt": {"resolutions": []}, "statuses": ["AMBIGUOUS"]},
            },
        ],
        "not_applicable_records": [],
        "metric_consistency_problems": [],
        "receipt_consistency_vs_ae7b281": {"resolver_behavior_unchanged": True},
    }


def _collect_all_keys(value: object) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, item in value.items():
            keys.add(str(key))
            keys |= _collect_all_keys(item)
    elif isinstance(value, list):
        for item in value:
            keys |= _collect_all_keys(item)
    return keys


class ReportMetricsProjectionTests(unittest.TestCase):
    """Compact report-metrics projection (ND-0A WS-C) semantics."""

    def setUp(self) -> None:
        self.results = _fixture_results()
        self.projection = d2_a2_runner.build_report_metrics_projection(self.results)

    def test_projection_excludes_per_case_results(self) -> None:
        self.assertNotIn("per_case_results", self.projection)
        self.assertNotIn("not_applicable_records", self.projection)
        self.assertNotIn("state_validation", self.projection)
        self.assertNotIn("metric_consistency_problems", self.projection)
        self.assertNotIn("receipt_consistency_vs_ae7b281", self.projection)

    def test_projection_excludes_raw_receipts(self) -> None:
        keys = _collect_all_keys(self.projection)
        receipt_shaped_keys = {
            "receipt",
            "resolutions",
            "candidates",
            "evidence",
            "mention_text",
            "mention_kind",
            "actual",
            "plan",
            "diagnostics",
            "failure_detail",
        }
        self.assertEqual(keys & receipt_shaped_keys, set())
        for key in keys:
            self.assertNotIn("receipt", key)
        # No receipt payload leaked into any string value either.
        dumped = json.dumps(self.projection)
        self.assertNotIn("mention_text", dumped)
        self.assertNotIn("object.a", dumped)

    def test_projection_top_level_keys(self) -> None:
        self.assertEqual(
            set(self.projection),
            {
                "case_counts",
                "decision_accounting",
                "failure_taxonomy_counts",
                "metrics",
                "descriptive_resolution_summary",
                "category_summaries",
                "run_provenance",
            },
        )
        # Hoisted aggregates appear exactly once (not duplicated under
        # ``metrics``); every remaining metric is compact aggregate data.
        self.assertNotIn("case_counts", self.projection["metrics"])
        self.assertNotIn("decision_accounting", self.projection["metrics"])
        self.assertNotIn("failure_taxonomy_counts", self.projection["metrics"])
        self.assertNotIn(
            "descriptive_resolution_summary", self.projection["metrics"]
        )
        self.assertIn("resolution_accuracy", self.projection["metrics"])

    def test_projection_keeps_only_tiny_provenance(self) -> None:
        self.assertEqual(
            set(self.projection["run_provenance"]),
            {"head", "baseline_commit", "timestamp_utc", "case_count"},
        )

    def test_projection_compacts_category_summaries(self) -> None:
        self.assertEqual(
            self.projection["category_summaries"]["exact_canonical_terminology"],
            {"cases": 1, "correct": 1, "decisions": {"correct_resolve": 1}},
        )


class ReportMetricsRoundTripTests(unittest.TestCase):
    """render/validate round trip over the compact projection."""

    def test_render_validate_round_trip_clean(self) -> None:
        results = _fixture_results()
        report_text = d2_a2_runner.render_metrics_block(results)
        self.assertIn("BEGIN_D2_A2_METRICS", report_text)
        self.assertIn("END_D2_A2_METRICS", report_text)
        self.assertEqual(d2_a2_runner.validate_report_metrics(report_text, results), [])

    def test_rendered_block_is_compact(self) -> None:
        report_text = d2_a2_runner.render_metrics_block(_fixture_results())
        self.assertNotIn("per_case_results", report_text)
        self.assertNotIn("resolutions", report_text)
        self.assertNotIn("candidates", report_text)

    def test_tampered_compact_metric_fails_validation(self) -> None:
        results = _fixture_results()
        report_text = d2_a2_runner.render_metrics_block(results)
        tampered = json.loads(json.dumps(results))
        tampered["metrics"]["resolution_accuracy"]["value"] = 0.99
        problems = d2_a2_runner.validate_report_metrics(report_text, tampered)
        self.assertTrue(problems)
        self.assertTrue(any("resolution_accuracy" in problem for problem in problems))

    def test_tampered_decision_accounting_fails_validation(self) -> None:
        results = _fixture_results()
        report_text = d2_a2_runner.render_metrics_block(results)
        tampered = json.loads(json.dumps(results))
        tampered["metrics"]["decision_accounting"]["correct_resolve"] = 2
        problems = d2_a2_runner.validate_report_metrics(report_text, tampered)
        self.assertTrue(any("decision_accounting" in problem for problem in problems))

    def test_missing_block_fails_validation(self) -> None:
        problems = d2_a2_runner.validate_report_metrics("no block here", _fixture_results())
        self.assertEqual(problems, ["report is missing the BEGIN/END_D2_A2_METRICS block"])


class CommittedReportMetricsTests(unittest.TestCase):
    """The ACTUAL committed report must validate against the ACTUAL
    committed results artifact (paths resolved from this test file upward)."""

    def test_committed_report_matches_committed_results(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        results = json.loads(
            (repo_root / "evaluation" / "d2_a2_results.json").read_text(encoding="utf-8")
        )
        report_text = (
            repo_root / "docs" / "PHASE_D2_A2_TERMINOLOGY_EVALUATION.md"
        ).read_text(encoding="utf-8")
        self.assertEqual(
            d2_a2_runner.validate_report_metrics(report_text, results), []
        )


if __name__ == "__main__":
    unittest.main()
