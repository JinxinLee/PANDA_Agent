"""D2-A2R1 focused T0: evaluation-semantics self-checks for the D2-A2 runner.

Tests the pure comparison/classification semantics of
``evaluation/scripts/d2_a2_runner.py`` with synthetic resolutions — no live
DB, no model, no network.
"""

from __future__ import annotations

import importlib.util
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
):
    return d2_a2_runner._classify_case_decision(
        expected_status=expected_status,
        resolutions=resolutions,
        expected_object_ids=set(expected_object_ids),
        expected_canonical_object_ids=set(expected_canonical_object_ids),
        require_all_targets=require_all,
        invalid=invalid,
        isolation_tokens=isolation_tokens or {},
    )


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
        self.assertEqual(bucket, "not_applicable")


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
        problems = d2_a2_runner._validate_metric_consistency(
            {
                "case_counts": {"valid": 10, "not_applicable": 0},
                "decision_accounting": {
                    "correct_resolve": 9,
                    "wrong_ambiguous": 1,
                    "not_applicable": 0,
                },
                "resolution_accuracy": {"numerator": 9, "denominator": 10, "value": 0.9},
            }
        )
        self.assertEqual(problems, [])

    def test_metric_consistency_detects_mismatch(self) -> None:
        problems = d2_a2_runner._validate_metric_consistency(
            {
                "case_counts": {"valid": 10, "not_applicable": 0},
                "decision_accounting": {
                    "correct_resolve": 8,
                    "wrong_ambiguous": 1,
                    "not_applicable": 0,
                },
                "resolution_accuracy": {"numerator": 9, "denominator": 10, "value": 0.9},
            }
        )
        self.assertTrue(problems)


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


if __name__ == "__main__":
    unittest.main()
