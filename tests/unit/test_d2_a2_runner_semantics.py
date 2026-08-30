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


if __name__ == "__main__":
    unittest.main()
