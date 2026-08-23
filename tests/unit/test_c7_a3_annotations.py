from __future__ import annotations

from types import SimpleNamespace
import unittest

from evaluation.scripts.build_c7_a3_annotations import (
    MATCHER_IDENTITY,
    _normalized_payloads,
    build_annotations,
    project_case_annotations,
    validate_exact_cohort,
)
from evaluation.scripts.capture_c7_a2_post_reranker import EXPECTED_COHORT_IDS
from panda_agent.evaluation import GoldEvidenceGroup, GoldEvidenceSelector


def payload(object_id: str, *, source_id: str = "repository", path: str = "src/item.py") -> dict:
    return {
        "object_id": object_id,
        "source_id": source_id,
        "source_version_id": "v1",
        "object_type": "source_file",
        "locator": {"path": path},
    }


def case(case_id: str, groups: list[GoldEvidenceGroup]) -> SimpleNamespace:
    return SimpleNamespace(id=case_id, required_evidence_groups=groups, forbidden_evidence=[GoldEvidenceSelector(source_id="forbidden")])


class C7A3AnnotationTests(unittest.TestCase):
    def test_generic_authoritative_matching_supports_selector_all_of_and_group_any_of(self) -> None:
        all_of = GoldEvidenceSelector(source_id="repository", path="src/good.py")
        other = GoldEvidenceSelector(source_id="alternate", path="docs/other.md")
        group = GoldEvidenceGroup(group_id="evidence", critical=True, any_of=[all_of, other])
        annotation = project_case_annotations(
            case("synthetic", [group]),
            {
                "wrong-path": payload("wrong-path", path="src/wrong.py"),
                "all-of-match": payload("all-of-match", path="src/good.py"),
                "any-of-match": payload("any-of-match", source_id="alternate", path="docs/other.md"),
            },
        )
        self.assertEqual(annotation["relevant_groups_by_object"], {"all-of-match": ["evidence"], "any-of-match": ["evidence"]})
        self.assertEqual(annotation["critical_groups_by_object"], annotation["relevant_groups_by_object"])
        self.assertEqual(annotation["matcher_identity"], MATCHER_IDENTITY)

    def test_case_scoped_groups_and_object_style_mapping_remain_separate(self) -> None:
        group = GoldEvidenceGroup(group_id="shared", critical=False, any_of=[GoldEvidenceSelector(source_id="repository")])
        annotations = build_annotations(
            [case("synthetic-a", [group]), case("synthetic-b", [group])],
            {"synthetic-a": {"object-a": payload("object-a")}, "synthetic-b": {"object-b": payload("object-b")}},
            expected_case_ids=("synthetic-a", "synthetic-b"),
        )
        self.assertEqual(set(annotations), {"synthetic-a", "synthetic-b"})
        self.assertEqual(annotations["synthetic-a"]["relevant_groups_by_object"], {"object-a": ["shared"]})
        self.assertEqual(annotations["synthetic-b"]["relevant_groups_by_object"], {"object-b": ["shared"]})
        self.assertEqual(annotations["synthetic-a"]["critical_groups"], [])

    def test_payload_identity_accepts_equal_id_falls_back_when_absent_and_rejects_conflict(self) -> None:
        normalized = _normalized_payloads(
            {
                "equal": payload("equal"),
                "fallback": {"source_id": "repository", "locator": {"path": "src/fallback.py"}},
            }
        )
        self.assertEqual(normalized["equal"]["object_id"], "equal")
        self.assertEqual(normalized["fallback"]["object_id"], "fallback")
        with self.assertRaisesRegex(ValueError, "object_id conflicts with mapping key"):
            _normalized_payloads({"key": payload("other")})

    def test_unsupported_conditions_fail_closed_and_critical_passthrough_is_preserved(self) -> None:
        critical = GoldEvidenceGroup(group_id="critical", critical=True, any_of=[GoldEvidenceSelector(source_id="repository")])
        annotation = project_case_annotations(case("synthetic", [critical, object()]), {"object": payload("object")})
        self.assertEqual(annotation["critical_groups"], ["critical"])
        self.assertEqual(annotation["critical_groups_by_object"], {"object": ["critical"]})
        self.assertEqual(annotation["unsupported_conditions"][0]["reason"], "unsupported_evidence_group_type")
        self.assertNotIn("<object object", annotation["relevant_groups_by_object"])

    def test_matcher_error_discards_earlier_group_mapping(self) -> None:
        group = GoldEvidenceGroup(group_id="transactional", critical=True, any_of=[GoldEvidenceSelector(source_id="repository")])
        annotation = project_case_annotations(
            case("synthetic", [group]),
            {
                "a-match": payload("a-match"),
                "z-unsupported": {**payload("z-unsupported"), "locator": "not-a-mapping"},
            },
        )
        self.assertEqual(annotation["relevant_groups_by_object"], {})
        self.assertEqual(annotation["critical_groups_by_object"], {})
        self.assertEqual(annotation["unsupported_conditions"], [{"condition": "transactional", "reason": "matcher_unsupported:AttributeError"}])

    def test_forbidden_evidence_does_not_fabricate_negative_completeness(self) -> None:
        group = GoldEvidenceGroup(group_id="evidence", any_of=[GoldEvidenceSelector(source_id="repository")])
        annotation = project_case_annotations(case("synthetic", [group]), {"object": payload("object")})
        self.assertFalse(annotation["negative_completeness"])
        self.assertNotIn("known_irrelevant_object_ids", annotation)

    def test_exact_cohort_validator_requires_frozen_order(self) -> None:
        self.assertEqual(validate_exact_cohort(EXPECTED_COHORT_IDS), EXPECTED_COHORT_IDS)
        with self.assertRaisesRegex(ValueError, "exact preregistered cohort order"):
            validate_exact_cohort(tuple(reversed(EXPECTED_COHORT_IDS)))


if __name__ == "__main__":
    unittest.main()
