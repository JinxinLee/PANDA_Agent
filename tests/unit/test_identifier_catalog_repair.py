"""Deterministic tests for the identifier-catalog scoped-identifier repair.

T1-T8 follow the post-A5 review's required matrix: qualified/scoped identifiers
that appear verbatim in allowed locked-corpus text must not be classified as
hallucinated, fabricated qualified identifiers must remain hallucinated,
disallowed-version symbols must stay nonexistent, and the
exists-versus-supported distinction must be preserved.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from panda_agent.evaluation import (
    build_identifier_catalog,
    deterministic_case_metrics,
    load_gold_dataset,
)
from panda_agent.evaluation_runner import load_object_lookup
from panda_agent.models import QAStatus
from panda_agent.evaluation import GoldQuestion

_LOCKED_TEXT = (
    "namespace ExampleNS {\n"
    "  enum Frame { VALUE_A };\n"
    "}\n"
    "auto v = ExampleNS::VALUE_A;\n"
)


def _lookup() -> dict:
    return {
        "locked_enum": {
            "source_id": "repo",
            "source_version_id": "repo@locked",
            "object_type": "source_file_chunk",
            "locator": {"path": "src/example.cxx", "symbol": None},
            "text": _LOCKED_TEXT,
        },
        "other_locked": {
            "source_id": "repo",
            "source_version_id": "repo@locked",
            "object_type": "source_file_chunk",
            "locator": {"path": "src/other.cxx", "symbol": None},
            "text": "ExampleNS::VALUE_B is referenced elsewhere.\n",
        },
        "disallowed": {
            "source_id": "repo",
            "source_version_id": "repo@other",
            "object_type": "source_file_chunk",
            "locator": {"path": "src/secret.cxx", "symbol": None},
            "text": "namespace OtherNS { enum S { SECRET_VALUE }; }\n",
        },
    }


def _case() -> GoldQuestion:
    return GoldQuestion.model_construct(
        id="t001",
        split="dev",
        language="en",
        intent="api",
        query="How is ExampleNS::VALUE_A used?",
        expected_status=QAStatus.ANSWERED,
        accepted_intents=[],
        allowed_source_versions=["repo@locked"],
        required_evidence_groups=[],
        required_source_types=[],
        required_answer_points=[],
        required_identifiers=[],
        forbidden_evidence=[],
    )


def _metrics(lookup: dict, claim_text: str, cited_object_key: str = "locked_enum") -> dict:
    cited = lookup[cited_object_key]
    result = {
        "status": "answered",
        "answer": claim_text,
        "claims": [
            {
                "claim_id": "c1",
                "claim_text": claim_text,
                "evidence_ids": ["e1"],
            }
        ],
        "evidence": [
            {
                "evidence_id": "e1",
                "object_id": cited_object_key,
                "source_id": cited.get("source_id"),
                "source_version_id": cited.get("source_version_id"),
                "locator": cited.get("locator") or {},
                "text": cited.get("text") or "",
            }
        ],
    }
    diagnostics = {"plan": {"intent": "api"}, "ranked_object_ids": []}
    return deterministic_case_metrics(_case(), result, diagnostics, lookup)


class QualifiedIdentifierCatalogTests(unittest.TestCase):
    """T1/T2/T8: allowed-corpus qualified literals are not hallucinations."""

    def test_t1_qualified_literal_exists(self) -> None:
        lookup = _lookup()
        metrics = _metrics(lookup, "Uses ExampleNS::VALUE_A for the frame.")
        self.assertNotIn("ExampleNS::VALUE_A", metrics["hallucinated_identifiers"])
        self.assertIn("ExampleNS::VALUE_A", metrics["identifier_exists_in_locked_corpus"])

    def test_t2_multiple_scoped_members_recognized(self) -> None:
        lookup = _lookup()
        metrics = _metrics(lookup, "Uses ExampleNS::VALUE_A and ExampleNS::VALUE_B.")
        self.assertNotIn("ExampleNS::VALUE_A", metrics["hallucinated_identifiers"])
        self.assertNotIn("ExampleNS::VALUE_B", metrics["hallucinated_identifiers"])

    def test_t8_cited_qualified_identifier_supported(self) -> None:
        lookup = _lookup()
        metrics = _metrics(lookup, "Uses ExampleNS::VALUE_A for the frame.")
        self.assertNotIn("ExampleNS::VALUE_A", metrics["hallucinated_identifiers"])
        self.assertIn("ExampleNS::VALUE_A", metrics["identifier_supported_by_claim_evidence"])


class FabricatedIdentifierControlTests(unittest.TestCase):
    """T3/T32: fabricated qualified identifiers remain hallucinated."""

    def test_t3_fabricated_member_stays_hallucinated(self) -> None:
        lookup = _lookup()
        metrics = _metrics(lookup, "Uses ExampleNS::DOES_NOT_EXIST.")
        self.assertIn("ExampleNS::DOES_NOT_EXIST", metrics["hallucinated_identifiers"])

    def test_t32_nonexistent_member_control_stays_hallucinated(self) -> None:
        lookup = _lookup()
        metrics = _metrics(lookup, "Uses ExampleNS::TOTALLY_NONEXISTENT_MEMBER.")
        self.assertIn("ExampleNS::TOTALLY_NONEXISTENT_MEMBER", metrics["hallucinated_identifiers"])


class NamespaceSpoofControlTests(unittest.TestCase):
    """T4: a bare corpus symbol must not legitimize a fabricated qualification."""

    def test_t4_namespace_spoof_is_hallucinated(self) -> None:
        lookup = _lookup()
        lookup["bare_symbol"] = {
            "source_id": "repo",
            "source_version_id": "repo@locked",
            "object_type": "function",
            "locator": {"path": "src/bare.cxx", "symbol": "VALUE_A"},
            "text": "void VALUE_A() {}\n",
        }
        metrics = _metrics(lookup, "Uses FakeNS::VALUE_A from the bare helper.")
        self.assertIn("FakeNS::VALUE_A", metrics["hallucinated_identifiers"])


class AllowedVersionBoundaryTests(unittest.TestCase):
    """T5/T33: disallowed-version symbols stay nonexistent."""

    def test_t5_disallowed_version_stays_nonexistent(self) -> None:
        lookup = _lookup()
        metrics = _metrics(lookup, "Uses OtherNS::SECRET_VALUE.")
        self.assertIn("OtherNS::SECRET_VALUE", metrics["hallucinated_identifiers"])
        self.assertNotIn("OtherNS::SECRET_VALUE", metrics["identifier_exists_in_locked_corpus"])


class CatalogRegressionTests(unittest.TestCase):
    """T6: existing locator/declaration/path authority keeps working."""

    def test_t6_existing_catalog_behavior(self) -> None:
        lookup = {
            "obj": {
                "source_id": "repo",
                "source_version_id": "repo@locked",
                "object_type": "source_file",
                "locator": {"path": "model/PndLmdAcceptance.cxx", "symbol": "PndLmdAcceptance"},
                "text": "class PndLmdHelper {}; enum PndLmdMode {}; input.root",
            },
        }
        catalog = build_identifier_catalog(lookup, ["repo@locked"])
        self.assertIn("PndLmdAcceptance", catalog["symbols"])
        self.assertIn("PndLmdHelper", catalog["symbols"])
        self.assertIn("PndLmdMode", catalog["symbols"])
        self.assertIn("model/PndLmdAcceptance.cxx", catalog["paths"])
        self.assertIn("input.root", catalog["paths"])

    def test_t7_exists_but_unsupported_is_not_hallucinated(self) -> None:
        lookup = _lookup()
        metrics = _metrics(
            lookup,
            "Uses ExampleNS::VALUE_B somewhere unrelated.",
            cited_object_key="locked_enum",
        )
        self.assertNotIn("ExampleNS::VALUE_B", metrics["hallucinated_identifiers"])
        self.assertIn("ExampleNS::VALUE_B", metrics["identifier_exists_in_locked_corpus"])
        self.assertIn("ExampleNS::VALUE_B", metrics["unsupported_identifiers"])


class Attempt5IdentifierRegressionTests(unittest.TestCase):
    """Case-specific offline regression on the production corpus (allowed only
    after the generic behavior above was established): the six Attempt-5
    false-positive hallucinations must stay cleared under the repaired catalog.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[2]
        cls.lookup = load_object_lookup(cls.root)
        cls.dataset = load_gold_dataset(
            cls.root / "evaluation" / "benchmarks" / "v2_10" / "gold_questions.yaml"
        )
        run_path = (
            cls.root
            / "data"
            / "evaluation"
            / "runs"
            / "f6a-rc5-gold-formal-full-20260919"
            / "results.jsonl"
        )
        cls.records = {}
        for line in run_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                record = json.loads(line)
                cls.records[record["id"]] = record

    def _metrics(self, case_id: str) -> dict:
        case = next(q for q in self.dataset.questions if q.id == case_id)
        record = self.records[case_id]
        return deterministic_case_metrics(
            case, record["result"], record["diagnostics"], self.lookup
        )

    def test_attempt5_false_positive_hallucinations_cleared(self) -> None:
        expected = {
            "g060": ["LumiFit::THETA_X", "LumiFit::THETA_Y"],
            "g113": ["LumiFit::MC", "LumiFit::MC_ACC", "LumiFit::RECO", "LumiFit::THETA_X"],
        }
        for case_id, identifiers in expected.items():
            metrics = self._metrics(case_id)
            for identifier in identifiers:
                self.assertIn(identifier, metrics["identifier_exists_in_locked_corpus"], case_id)
                self.assertNotIn(identifier, metrics["hallucinated_identifiers"], case_id)


class QualifiedOwnershipBoundaryTests(unittest.TestCase):
    """R1 matrix: qualified existence requires exact ownership evidence; a known
    namespace head combined with an independently known bare tail must not
    fabricate a qualified symbol."""

    def test_r1_t1_known_head_plus_unrelated_known_tail_is_hallucinated(self) -> None:
        lookup = {
            "enum_owner": {
                "source_id": "repo",
                "source_version_id": "repo@locked",
                "object_type": "source_file_chunk",
                "locator": {"path": "src/example.cxx", "symbol": None},
                "text": "ExampleNS::VALUE_B selects the alternate frame.\n",
            },
            "bare_tail": {
                "source_id": "repo",
                "source_version_id": "repo@locked",
                "object_type": "function",
                "locator": {"path": "src/bare.cxx", "symbol": "VALUE_A"},
                "text": "void VALUE_A() {}\n",
            },
        }
        metrics = _metrics(lookup, "Uses ExampleNS::VALUE_A here.", cited_object_key="enum_owner")
        self.assertIn("ExampleNS::VALUE_A", metrics["hallucinated_identifiers"])
        self.assertNotIn("ExampleNS::VALUE_A", metrics["identifier_exists_in_locked_corpus"])

    def test_r1_t3_nested_exact_qualified_literal_recognized(self) -> None:
        lookup = {
            "nested": {
                "source_id": "repo",
                "source_version_id": "repo@locked",
                "object_type": "source_file_chunk",
                "locator": {"path": "src/nested.cxx", "symbol": None},
                "text": "Outer::Inner::VALUE_A is the nested constant.\n",
            },
        }
        metrics = _metrics(lookup, "Uses Outer::Inner::VALUE_A.", cited_object_key="nested")
        self.assertNotIn("Outer::Inner::VALUE_A", metrics["hallucinated_identifiers"])
        self.assertIn("Outer::Inner::VALUE_A", metrics["identifier_exists_in_locked_corpus"])

    def test_r1_t5_wrong_member_is_hallucinated(self) -> None:
        lookup = {
            "enum_owner": {
                "source_id": "repo",
                "source_version_id": "repo@locked",
                "object_type": "source_file_chunk",
                "locator": {"path": "src/example.cxx", "symbol": None},
                "text": "ExampleNS::VALUE_A is the documented constant.\n",
            },
        }
        metrics = _metrics(lookup, "Uses ExampleNS::VALUE_Z.", cited_object_key="enum_owner")
        self.assertIn("ExampleNS::VALUE_Z", metrics["hallucinated_identifiers"])

    def test_r1_t6_wrong_owner_is_hallucinated(self) -> None:
        lookup = {
            "enum_owner": {
                "source_id": "repo",
                "source_version_id": "repo@locked",
                "object_type": "source_file_chunk",
                "locator": {"path": "src/example.cxx", "symbol": None},
                "text": "ExampleNS::VALUE_A is the documented constant.\n",
            },
        }
        metrics = _metrics(lookup, "Uses OtherNS::VALUE_A.", cited_object_key="enum_owner")
        self.assertIn("OtherNS::VALUE_A", metrics["hallucinated_identifiers"])


if __name__ == "__main__":
    unittest.main()
