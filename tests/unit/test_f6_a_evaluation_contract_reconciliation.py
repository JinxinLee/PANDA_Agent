"""Focused zero-model-call tests for the F6-A evaluation-contract reconciliation.

T1-T10 cover the successor Gold m6-benchmark-v2.11, calibration v8, the
critical-evidence role/any_of equivalence contract, the g011 negative control,
the g039 correction, and the future gate-category classification.
"""
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from dotenv import load_dotenv

from panda_agent.evaluation import (
    GoldEvidenceSelector,
    calibration_compatibility,
    load_gold_dataset,
)
from panda_agent.evaluation_runner import load_object_lookup, validate_gold_dataset

ROOT = Path(__file__).resolve().parents[2]
V210 = ROOT / "evaluation" / "benchmarks" / "v2_10" / "gold_questions.yaml"
V211 = ROOT / "evaluation" / "benchmarks" / "v2_11" / "gold_questions.yaml"
CHANGED_IDS = ["g013", "g016", "g020", "g039", "g044", "g110"]
P1_NEW = "Locate the longitudinal-profile efficiency-correction implementation macro."


class SuccessorGoldTests(unittest.TestCase):
    def test_t1_successor_gold_valid(self) -> None:
        ds = load_gold_dataset(V211)
        self.assertEqual(ds.benchmark_version, "m6-benchmark-v2.11")
        self.assertEqual(len(ds.questions), 120)
        validation = validate_gold_dataset(ROOT, V211, require_approved=True)
        self.assertTrue(validation["official_ready"])
        self.assertTrue(validation["structurally_valid"])
        self.assertEqual(validation["unmatched_evidence_groups"], [])
        self.assertEqual(validation["unknown_allowed_source_versions"], [])
        split_counts: dict[str, int] = {}
        status_counts: dict[str, int] = {}
        for q in ds.questions:
            split_counts[q.split] = split_counts.get(q.split, 0) + 1
            status_counts[q.expected_status.value] = status_counts.get(q.expected_status.value, 0) + 1
        self.assertEqual(split_counts, {"dev": 80, "challenge": 24, "regression": 16})
        self.assertEqual(
            status_counts,
            {"answered": 102, "insufficient_evidence": 10, "version_conflict": 8},
        )
        self.assertEqual(
            validation["review_counts"],
            {"approved": 120},
        )
        changed = sorted(
            q.id
            for q in load_gold_dataset(V210).questions
            if q.model_dump(mode="json", exclude_none=True)
            != next(
                x.model_dump(mode="json", exclude_none=True)
                for x in ds.questions
                if x.id == q.id
            )
        )
        self.assertEqual(changed, CHANGED_IDS)

    def test_t2_v210_immutable(self) -> None:
        self.assertEqual(
            hashlib.sha256(V210.read_bytes()).hexdigest(),
            "bdce5cbdc0a6f1645d7350b87bc2f289265c3d67311dab4b12e488b9dc499513",
        )

    def test_t3_critical_role_any_of(self) -> None:
        ds = load_gold_dataset(V211)
        q = next(x for x in ds.questions if x.id == "g020")
        grp = next(g for g in q.required_evidence_groups if g.group_id == "g020.e1")
        lookup = load_object_lookup(ROOT)
        # Original pinned selector still satisfies the group (existence is
        # guaranteed by the v2.10-era unmatched-groups validation).
        original = next(
            s
            for s in grp.any_of
            if s.path == "macro/target/README.md" and s.title_contains == "POCA Workflow"
        )
        original_target = next(o for o in lookup.values() if original.matches(o))
        self.assertTrue(original.matches(original_target))
        # Audited equivalent selector also satisfies the same group.
        equivalent = next(
            s
            for s in grp.any_of
            if s.path == "README.md" and s.section_contains == "POCA"
        )
        equivalent_target = next(
            o
            for o in lookup.values()
            if (o.get("locator") or {}).get("path") == "README.md"
            and o.get("object_type") == "readme_section"
            and "POCA" in " ".join((o.get("locator") or {}).get("section_path") or [])
        )
        self.assertTrue(equivalent.matches(equivalent_target))

    def test_t4_wrong_source_does_not_satisfy(self) -> None:
        wrong = GoldEvidenceSelector.model_validate({"source_id": "li_2026", "pdf_page": 99})
        lookup = load_object_lookup(ROOT)
        target = lookup["object.557d3c23dd41029ce0e7e202"]  # li_2026 page 72
        self.assertFalse(wrong.matches(target))
        pflueger = GoldEvidenceSelector.model_validate({"source_id": "pflueger_2017", "pdf_page": 57})
        self.assertFalse(pflueger.matches(target))


class G039CorrectionTests(unittest.TestCase):
    def test_t6_corrected_point_is_literal(self) -> None:
        ds = load_gold_dataset(V211)
        q = next(x for x in ds.questions if x.id == "g039")
        p1 = next(p for p in q.required_answer_points if p.point_id == "p1")
        self.assertEqual(p1.text, P1_NEW)
        self.assertNotIn("distinguish", p1.text.lower())
        self.assertIn("Locate", p1.text)
        identifier = next(i for i in q.required_identifiers if i.text == "efficiency_correction_2.C")
        self.assertTrue(identifier.critical)

    def test_t7_forbidden_evidence_preserved(self) -> None:
        ds = load_gold_dataset(V211)
        q = next(x for x in ds.questions if x.id == "g039")
        forbidden_paths = [f.path for f in q.forbidden_evidence]
        self.assertIn("data/PndLmdAcceptance.cxx", forbidden_paths)


class CalibrationSuccessorTests(unittest.TestCase):
    def test_t8_calibration_v8_reconciled(self) -> None:
        ds = load_gold_dataset(V211)
        cal_path = ROOT / "evaluation" / "baselines" / "manifests" / "phase_b_t3_product_language_scope_v8.json"
        cal = json.loads(cal_path.read_text(encoding="utf-8"))
        self.assertEqual(cal["calibration_id"], "phase_b_t3_product_language_scope_v8")
        self.assertEqual(cal["source_gold"]["version"], "m6-benchmark-v2.11")
        self.assertEqual(
            cal["source_gold"]["sha256"],
            hashlib.sha256(V211.read_bytes()).hexdigest(),
        )
        compat = calibration_compatibility(cal, ds, dataset_path=V211)
        self.assertTrue(compat["compatible"], compat)
        v7 = json.loads(
            (ROOT / "evaluation" / "baselines" / "manifests" / "phase_b_t3_product_language_scope_v7.json")
            .read_text(encoding="utf-8")
        )
        self.assertEqual(cal["formal_english_ids"], v7["formal_english_ids"])
        self.assertEqual(cal["non_english_ids"], v7["non_english_ids"])
        self.assertEqual(cal["counts"], v7["counts"])


class GateCategoryTests(unittest.TestCase):
    def test_t9_future_gate_categories(self) -> None:
        recon = json.loads(
            (ROOT / "evaluation" / "f6_a_evaluation_contract_reconciliation.json")
            .read_text(encoding="utf-8")
        )
        hard = recon["hard_safety_future_contract"]["gates"]
        strict = recon["strict_release_quality_future_contract"]["gates"]
        self.assertNotIn("critical_answer_point_miss_count", hard)
        self.assertIn("critical_answer_point_miss_count", strict)
        self.assertEqual(strict["critical_answer_point_miss_count"], 0)
        for gate in ("citation_integrity", "wrong_version_evidence_count", "forbidden_evidence_count", "contradiction_count", "major_unsupported_claim_count", "unhandled_exception_count"):
            self.assertIn(gate, hard)
            self.assertNotIn(gate, strict)
        self.assertIn("critical_final_evidence_recall", strict)

    def test_t10_thresholds_unchanged(self) -> None:
        recon = json.loads(
            (ROOT / "evaluation" / "f6_a_evaluation_contract_reconciliation.json")
            .read_text(encoding="utf-8")
        )
        self.assertEqual(recon["threshold_changes"], "NONE")
        # Successor Gold keeps the same distributions and thresholds carrier.
        ds = load_gold_dataset(V211)
        self.assertEqual(ds.benchmark_version, "m6-benchmark-v2.11")
        d211 = json.loads(
            (ROOT / "evaluation" / "benchmarks" / "v2_11" / "benchmark_manifest.json")
            .read_text(encoding="utf-8")
        )
        self.assertEqual(
            d211["status_counts"],
            {"answered": 102, "insufficient_evidence": 10, "version_conflict": 8},
        )


class G011NegativeControlTests(unittest.TestCase):
    def test_t5_g011_still_fails_reconciled_contract(self) -> None:
        lookup = load_object_lookup(ROOT)
        ds11 = load_gold_dataset(V211)
        q11 = next(x for x in ds11.questions if x.id == "g011")
        run_path = (
            ROOT
            / "data"
            / "evaluation"
            / "runs"
            / "f6a-rc5-gold-formal-full-20260919"
            / "results.jsonl"
        )
        record = None
        for line in run_path.read_text(encoding="utf-8").splitlines():
            candidate = json.loads(line)
            if candidate["id"] == "g011":
                record = candidate
        from panda_agent.evaluation import deterministic_case_metrics

        metrics = deterministic_case_metrics(q11, record["result"], record["diagnostics"], lookup)
        self.assertEqual(metrics["critical_final_evidence_recall"], 0.0)


if __name__ == "__main__":
    unittest.main()
