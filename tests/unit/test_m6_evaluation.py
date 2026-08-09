from __future__ import annotations

import json
import tempfile
import unittest
from collections import Counter
from pathlib import Path

from panda_agent.evaluation import (
    EXPECTED_INTENT_COUNTS,
    EXPECTED_LANGUAGE_COUNTS,
    EXPECTED_SPLIT_COUNTS,
    EXPECTED_STATUS_COUNTS,
    EXPECTED_INTENT_SPLIT_COUNTS,
    aggregate_metrics,
    build_identifier_catalog,
    evaluate_development_gate,
    evaluate_regression_gate,
    evaluate_quality_gate,
    load_gold_dataset,
    evidence_group_recall,
    GoldEvidenceGroup,
    GoldEvidenceSelector,
    classify_identifier_mention,
    deterministic_case_metrics,
)
from panda_agent.indexing import normalized_dir
from panda_agent.storage import iter_jsonl
from panda_agent.evaluation import EvaluationRunStore, load_run_records
from panda_agent.evaluation_runner import (
    _claim_relevant_evidence_excerpt,
    _attempt_budget_stop_reason,
    _deterministic_point_ids,
    _protected_rubric_point_ids,
    build_failure_review,
    default_gold_dataset_path,
    import_failure_review_decisions,
    judge_answer,
    result_content_hash,
    run_evaluation,
    validate_gold_dataset,
    validate_failure_review,
)
from panda_agent.benchmark_v2 import (
    _formal_rescore_identity,
    assert_v2_draft_target_writable,
    rescore_run,
)


class M6EvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[2]
        cls.dataset = load_gold_dataset(cls.root / "evaluation" / "gold_questions.yaml")

    @staticmethod
    def _write_rescore_fixture(
        project_root: Path,
        dataset_path: Path,
        run_id: str,
        case_ids: list[str],
        *,
        prompt_hash: str = "prompt-hash",
        identity_overrides: dict[str, str] | None = None,
    ) -> None:
        """Create a tiny offline run tree accepted by ``rescore_run``.

        The fixture deliberately lives under a temporary project root.  It has
        no Vertex, Docker, database, or real evaluation-output dependency; the
        scorer only needs immutable records, identity metadata, an empty object
        lookup, and the evaluator policy file it fingerprints.
        """
        dataset = load_gold_dataset(dataset_path)
        questions = {item.id: item for item in dataset.questions}
        run_dir = project_root / "data" / "evaluation" / "runs" / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        records = [
            {
                "id": case_id,
                "intent": questions[case_id].intent,
                "result": {
                    "status": questions[case_id].expected_status.value,
                    "answer": "",
                    "claims": [],
                    "evidence": [],
                },
                "diagnostics": {},
                "metrics": {},
                "duration_ms": 1,
            }
            for case_id in case_ids
        ]
        (run_dir / "results.jsonl").write_text(
            "".join(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n" for item in records),
            encoding="utf-8",
        )
        manifest = {
            key: "fixture-identity"
            for key in (
                "source_manifest_hash",
                "index_identity",
                "generation_model_id",
                "runtime_generation_model_id",
                "evaluation_judge_model_id",
                "embedding_model_id",
                "retrieval_policy_hash",
                "query_expansion_hash",
            )
        }
        manifest["prompt_hash"] = prompt_hash
        manifest.update(identity_overrides or {})
        (run_dir / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    @classmethod
    def _prepare_rescore_project(
        cls,
        project_root: Path,
        dataset_path: Path,
        source_case_ids: list[str],
    ) -> None:
        normalized = project_root / "data" / "normalized" / "fixture"
        normalized.mkdir(parents=True, exist_ok=True)
        (normalized / "ingestion_report.json").write_text("{}\n", encoding="utf-8")
        (normalized / "knowledge_objects.jsonl").write_text("", encoding="utf-8")
        policy = project_root / "src" / "panda_agent" / "evaluation.py"
        policy.parent.mkdir(parents=True, exist_ok=True)
        policy.write_text("offline fixture policy\n", encoding="utf-8")
        cls._write_rescore_fixture(
            project_root,
            dataset_path,
            "source",
            source_case_ids,
        )

    def test_gold_dataset_has_exact_frozen_distribution(self) -> None:
        self.assertEqual(
            Counter(item.intent for item in self.dataset.questions),
            EXPECTED_INTENT_COUNTS,
        )
        self.assertEqual(
            Counter(item.split for item in self.dataset.questions), EXPECTED_SPLIT_COUNTS
        )
        self.assertEqual(
            Counter((item.intent, item.split) for item in self.dataset.questions),
            EXPECTED_INTENT_SPLIT_COUNTS,
        )
        self.assertEqual(
            Counter(item.language for item in self.dataset.questions),
            EXPECTED_LANGUAGE_COUNTS,
        )
        self.assertEqual(
            Counter(item.expected_status.value for item in self.dataset.questions),
            EXPECTED_STATUS_COUNTS,
        )

    def test_human_reviewed_dataset_is_officially_approved(self) -> None:
        self.dataset.require_approved("dev")
        self.dataset.require_approved("acceptance")

    def test_all_gold_evidence_groups_match_locked_objects(self) -> None:
        objects = list(
            iter_jsonl(normalized_dir(self.root) / "knowledge_objects.jsonl")
        )
        unmatched = [
            (case.id, group.group_id)
            for case in self.dataset.questions
            for group in case.required_evidence_groups
            if not any(
                candidate.matches(item)
                for candidate in group.any_of
                for item in objects
            )
        ]
        self.assertEqual(unmatched, [])

    def test_aggregate_metrics_and_gate_are_deterministic(self) -> None:
        records = []
        for case in self.dataset.questions:
            metrics = {
                "intent_correct": True,
                "gold_recall_at_10": 1.0,
                "final_evidence_recall": 1.0,
                "expected_status_correct": True,
                "citation_integrity": True,
                "required_source_coverage": True,
                "wrong_version_evidence": [],
                "forbidden_evidence": [],
                "missing_identifiers": [],
                "identifier_mentions": [],
                "hallucinated_identifiers": [],
                "answer_point_coverage": 1.0,
                "contradictions": [],
                "unsupported_claim_ids": [],
                "paper_code_dual_source": True,
            }
            records.append(
                {
                    "id": case.id,
                    "intent": case.intent,
                    "expected_status": case.expected_status.value,
                    "required_source_types": case.required_source_types,
                    "duration_ms": 10,
                    "model_calls": 1,
                    "token_usage": 0,
                    "metrics": metrics,
                }
            )
        acceptance = [item for item in records if item["id"] >= "g081"]
        # Use the real split membership rather than relying on numeric ranges.
        acceptance_ids = {
            item.id for item in self.dataset.questions if item.split == "acceptance"
        }
        acceptance = [item for item in records if item["id"] in acceptance_ids]
        metrics = aggregate_metrics(acceptance)
        gate = evaluate_quality_gate(
            metrics,
            acceptance,
            official=True,
            all_questions_approved=True,
        )
        self.assertTrue(gate["passed"])
        draft_gate = evaluate_quality_gate(
            metrics,
            acceptance,
            official=False,
            all_questions_approved=False,
        )
        self.assertFalse(draft_gate["passed"])

    def test_aggregate_metrics_preserves_runtime_and_judge_usage(self) -> None:
        records = [
            {
                "id": "g001",
                "intent": "installation",
                "expected_status": "answered",
                "required_source_types": [],
                "model_calls": 3,
                "token_usage": 120,
                "model_call_breakdown": {
                    "runtime": {"model_calls": 2, "token_usage": 80},
                    "judge": {"model_calls": 1, "token_usage": 40},
                },
                "metrics": {
                    "intent_correct": True,
                    "gold_recall_at_10": 1.0,
                    "final_evidence_recall": 1.0,
                    "critical_final_evidence_recall": 1.0,
                    "expected_status_correct": True,
                    "citation_integrity": True,
                    "required_source_coverage": True,
                    "wrong_version_evidence": [],
                    "forbidden_evidence": [],
                    "missing_identifiers": [],
                    "identifier_mentions": [],
                    "hallucinated_identifiers": [],
                    "answer_point_coverage": 1.0,
                    "contradictions": [],
                    "unsupported_claim_ids": [],
                    "paper_code_dual_source": True,
                },
            }
        ]
        metrics = aggregate_metrics(records)
        self.assertEqual(metrics["model_calls"], 3)
        self.assertEqual(metrics["token_usage"], 120)
        self.assertEqual(metrics["model_usage_by_role"]["runtime"]["model_calls"], 2)
        self.assertEqual(
            metrics["model_usage_by_role"]["evaluation_judge"]["token_usage"], 40
        )

    def test_budget_window_is_per_attempt_and_deadline_is_rebased(self) -> None:
        self.assertEqual(
            _attempt_budget_stop_reason(
                attempt_calls=2,
                attempt_tokens=20,
                max_model_calls=2,
                max_token_usage=100,
                deadline_at=200.0,
                now=100.0,
            ),
            "max_model_calls_exceeded",
        )
        self.assertIsNone(
            _attempt_budget_stop_reason(
                attempt_calls=0,
                attempt_tokens=0,
                max_model_calls=2,
                max_token_usage=100,
                deadline_at=200.0,
                now=100.0,
            )
        )
        self.assertEqual(
            _attempt_budget_stop_reason(
                attempt_calls=0,
                attempt_tokens=0,
                max_model_calls=2,
                max_token_usage=100,
                deadline_at=100.0,
                now=100.0,
            ),
            "deadline_exceeded",
        )

    def test_gold_yaml_contains_complete_human_approval_metadata(self) -> None:
        raw = json.loads(self.dataset.model_dump_json())
        self.assertTrue(all(item["review_status"] == "approved" for item in raw["questions"]))
        self.assertTrue(all(item["reviewer"] for item in raw["questions"]))
        self.assertTrue(all(item["reviewed_at"] for item in raw["questions"]))

    def test_page_selector_matches_retrieved_child_section_via_parent(self) -> None:
        parent = {
            "object_id": "page",
            "source_id": "docs",
            "title": "Docker Images for Panda",
            "locator": {"path": "Docker/Docker.html"},
        }
        child = {
            "object_id": "section",
            "source_id": "docs",
            "title": "On a Workstation",
            "parent_object_id": "page",
            "locator": {
                "path": "Docker/Docker.html",
                "section_path": ["Docker Containers", "Docker Images for Panda"],
            },
        }
        groups = [GoldEvidenceGroup(
            group_id="page-evidence",
            any_of=[GoldEvidenceSelector(
                source_id="docs", title_contains="Docker Images"
            )],
        )]
        self.assertEqual(
            evidence_group_recall(
                groups, ["section"], {"page": parent, "section": child}
            ),
            1.0,
        )

    def test_title_selector_can_match_sphinx_heading_path(self) -> None:
        selector = GoldEvidenceSelector(
            source_id="docs", title_contains="Docker Containers"
        )
        self.assertTrue(
            selector.matches(
                {
                    "source_id": "docs",
                    "title": "Docker Images for Panda [1/3]",
                    "locator": {
                        "section_path": ["Docker Containers", "Docker Images for Panda"]
                    },
                }
            )
        )

    def test_resumed_and_continuous_results_have_same_content_hash(self) -> None:
        records = [
            {"id": "g001", "result": {"status": "answered"}, "duration_ms": 1},
            {"id": "g002", "result": {"status": "answered"}, "duration_ms": 2},
        ]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            continuous = EvaluationRunStore(root, "continuous", {"dataset": "x"})
            for record in records:
                continuous.record(record)
            resumed = EvaluationRunStore(root, "resumed", {"dataset": "x"})
            resumed.record(records[0])
            resumed = EvaluationRunStore(
                root, "resumed", {"dataset": "x"}, resume=True
            )
            resumed.record(records[1])
            self.assertEqual(
                result_content_hash(load_run_records(continuous.run_dir)),
                result_content_hash(load_run_records(resumed.run_dir)),
            )

    def test_resume_tolerates_only_a_partial_final_jsonl_write(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            store = EvaluationRunStore(root, "partial", {"dataset": "x"})
            store.record({"id": "g001", "result": {"status": "answered"}})
            with store.results_path.open("a", encoding="utf-8") as stream:
                stream.write('{"id":"g002"')
            reopened = EvaluationRunStore(
                root, "partial", {"dataset": "x"}, resume=True
            )
            self.assertEqual(reopened.completed_ids, {"g001"})
            reopened.record({"id": "g002", "result": {"status": "answered"}})
            self.assertEqual(
                [item["id"] for item in load_run_records(reopened.run_dir)],
                ["g001", "g002"],
            )

    def test_development_gate_is_mode_aware_and_requires_full_dev(self) -> None:
        dev_cases = [item for item in self.dataset.questions if item.split == "dev"]
        records = []
        for case in dev_cases:
            records.append(
                {
                    "id": case.id,
                    "intent": case.intent,
                    "expected_status": case.expected_status.value,
                    "required_source_types": case.required_source_types,
                    "duration_ms": 1,
                    "metrics": {
                        "intent_correct": True,
                        "gold_recall_at_10": 1.0,
                        "final_evidence_recall": 1.0,
                        "expected_status_correct": True,
                        "citation_integrity": True,
                        "required_source_coverage": True,
                        "wrong_version_evidence": [],
                        "forbidden_evidence": [],
                        "missing_identifiers": [],
                        "identifier_mentions": [],
                        "hallucinated_identifiers": [],
                        "answer_point_coverage": 1.0,
                        "contradictions": [],
                        "unsupported_claim_ids": [],
                        "paper_code_dual_source": True,
                    },
                }
            )
        metrics = aggregate_metrics(records)
        # The legacy dev split contains no version-conflict examples.  An empty
        # sample must not pass that guardrail vacuously.
        self.assertFalse(
            evaluate_development_gate(
                metrics,
                records,
                mode="retrieval",
                complete_full_dev=True,
                all_questions_approved=True,
            )["passed"]
        )
        records[0]["expected_status"] = "version_conflict"
        metrics = aggregate_metrics(records)
        self.assertTrue(
            evaluate_development_gate(
                metrics,
                records,
                mode="retrieval",
                complete_full_dev=True,
                all_questions_approved=True,
            )["passed"]
        )
        self.assertTrue(
            evaluate_development_gate(
                metrics,
                records,
                mode="qa",
                complete_full_dev=True,
                all_questions_approved=True,
            )["passed"]
        )
        self.assertFalse(
            evaluate_development_gate(
                metrics,
                records,
                mode="qa",
                complete_full_dev=False,
                all_questions_approved=True,
            )["passed"]
        )

    def test_failure_review_contains_output_evidence_and_human_fields(self) -> None:
        case = next(item for item in self.dataset.questions if item.split == "dev")
        record = {
            "id": case.id,
            "intent": case.intent,
            "expected_status": case.expected_status.value,
            "required_source_types": case.required_source_types,
            "metrics": {
                "intent_correct": True,
                "expected_status_correct": True,
                "gold_recall_at_10": 1.0,
                "final_evidence_recall": 1.0,
                "required_source_coverage": True,
                "citation_integrity": True,
                "wrong_version_evidence": [],
                "forbidden_evidence": [],
                "missing_identifiers": [],
                "identifier_mentions": ["PndExample"],
                "hallucinated_identifiers": ["PndExample"],
                "answer_point_coverage": 1.0,
                "contradictions": [],
                "unsupported_claim_ids": [],
                "paper_code_dual_source": True,
            },
            "result": {
                "status": case.expected_status.value,
                "answer": "PndExample is used.",
                "claims": [
                    {
                        "claim_id": "c1",
                        "claim_text": "PndExample is used.",
                        "evidence_ids": ["e1"],
                    }
                ],
                "verification_errors": [],
                "evidence": [
                    {
                        "evidence_id": "e1",
                        "source_id": "pandaroot",
                        "source_version_id": "pandaroot@sha",
                        "authority_level": "primary",
                        "locator": {"path": "src/example.cxx", "start_line": 1},
                        "text": "class PndExample {};",
                    }
                ],
            },
        }
        review = build_failure_review(
            self.dataset,
            {"mode": "qa", "split": "dev"},
            [record],
            run_id="review-test",
        )
        self.assertEqual(len(review["entries"]), 1)
        entry = review["entries"][0]
        self.assertEqual(entry["model_output"]["answer"], "PndExample is used.")
        self.assertEqual(entry["supporting_evidence"][0]["evidence_id"], "e1")
        self.assertEqual(entry["human_review"]["action"], "pending")

    def test_failure_review_validation_requires_completed_decisions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            run_dir = root / "data" / "evaluation" / "runs" / "candidate"
            run_dir.mkdir(parents=True)
            review = {
                "allowed_classifications": ["metric_false_positive"],
                "allowed_actions": ["rescore"],
                "entries": [
                    {
                        "case_id": "g001",
                        "human_review": {
                            "status": "pending",
                            "classification": "pending",
                            "action": "pending",
                            "target_layer": "pending",
                            "rationale": "",
                            "reviewer": "",
                            "reviewed_at": None,
                            "waiver_id": None,
                        },
                    }
                ],
            }
            (run_dir / "failure_review.yaml").write_text(
                __import__("yaml").safe_dump(review), encoding="utf-8"
            )
            value = validate_failure_review(root, "candidate")
            self.assertFalse(value["valid"])
            self.assertTrue(value["errors"])

    def test_review_decisions_import_preserves_generated_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            run_dir = root / "data" / "evaluation" / "runs" / "candidate"
            run_dir.mkdir(parents=True)
            pending = {
                "run_id": "candidate",
                "allowed_classifications": ["metric_false_positive"],
                "allowed_actions": ["rescore"],
                "entries": [{"case_id": "g001", "human_review": {"status": "pending"}}],
            }
            reviewed = {
                **pending,
                "entries": [
                    {
                        "case_id": "g001",
                        "human_review": {
                            "status": "reviewed",
                            "classification": "metric_false_positive",
                            "action": "rescore",
                            "target_layer": "evaluation",
                            "rationale": "Verified against cited evidence.",
                            "reviewer": "reviewer",
                            "reviewed_at": "2026-08-02T00:00:00+00:00",
                            "waiver_id": None,
                        },
                    }
                ],
            }
            generated_path = run_dir / "failure_review.yaml"
            reviewed_path = root / "reviewed.yaml"
            generated_path.write_text(__import__("yaml").safe_dump(pending), encoding="utf-8")
            reviewed_path.write_text(__import__("yaml").safe_dump(reviewed), encoding="utf-8")
            original = generated_path.read_bytes()
            value = import_failure_review_decisions(root, "candidate", reviewed_path)
            self.assertTrue(value["valid"])
            self.assertEqual(generated_path.read_bytes(), original)
            self.assertTrue((run_dir / "failure_review_decisions.yaml").is_file())

    def test_regression_review_actions_map_to_canonical_actions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            run_dir = root / "data" / "evaluation" / "runs" / "regression"
            run_dir.mkdir(parents=True)
            case_ids = ["g090", "g109", "g116"]
            pending = {
                "run_id": "regression",
                "allowed_classifications": [
                    "metric_false_positive", "acceptable_exception", "real_failure"
                ],
                "allowed_actions": ["archive", "release_reject"],
                "entries": [
                    {"case_id": case_id, "human_review": {"status": "pending"}}
                    for case_id in case_ids
                ],
            }
            classifications = {
                "g090": ("metric_false_positive", "archive", None),
                "g109": (
                    "acceptable_exception", "archive",
                    "rc3f-g109-relative-path-shorthand",
                ),
                "g116": ("real_failure", "release_reject", None),
            }
            reviewed = {
                **pending,
                "entries": [
                    {
                        "case_id": case_id,
                        "human_review": {
                            "status": "reviewed",
                            "classification": classifications[case_id][0],
                            "action": classifications[case_id][1],
                            "target_layer": "evaluation",
                            "rationale": "Reviewed decision.",
                            "reviewer": "reviewer",
                            "reviewed_at": "2026-08-09T00:00:00+00:00",
                            "waiver_id": classifications[case_id][2],
                        },
                    }
                    for case_id in case_ids
                ],
            }
            generated_path = run_dir / "failure_review.yaml"
            reviewed_path = root / "reviewed.yaml"
            generated_path.write_text(__import__("yaml").safe_dump(pending), encoding="utf-8")
            reviewed_path.write_text(__import__("yaml").safe_dump(reviewed), encoding="utf-8")
            result = import_failure_review_decisions(root, "regression", reviewed_path)
            self.assertTrue(result["valid"])
            overlay = __import__("yaml").safe_load(
                (run_dir / "failure_review_decisions.yaml").read_text(encoding="utf-8")
            )
            decisions = {
                item["case_id"]: item["human_review"] for item in overlay["decisions"]
            }
            self.assertEqual(decisions["g090"]["action"], "rescore")
            self.assertEqual(decisions["g109"]["action"], "waiver")
            self.assertEqual(decisions["g116"]["action"], "fix")
            self.assertEqual(decisions["g090"]["original_action"], "archive")
            self.assertEqual(decisions["g116"]["original_action"], "release_reject")

    def test_selector_supports_line_overlap_and_pdf_page_ranges(self) -> None:
        code_selector = GoldEvidenceSelector(
            source_id="pandaroot", path="x.cxx", start_line=10, end_line=20
        )
        self.assertTrue(code_selector.matches({"source_id":"pandaroot","locator":{"path":"x.cxx","start_line":18,"end_line":30}}))
        self.assertFalse(code_selector.matches({"source_id":"pandaroot","locator":{"path":"x.cxx","start_line":21,"end_line":30}}))
        paper_selector = GoldEvidenceSelector(source_id="li_2026", pdf_page=141, pdf_page_end=152)
        self.assertTrue(paper_selector.matches({"source_id":"li_2026","locator":{"pdf_page":150}}))

    def test_glob_and_pointer_notation_are_not_major_identifiers(self) -> None:
        self.assertEqual(classify_identifier_mention("Lumi_TrksQA*.root")[0], "glob")
        self.assertEqual(classify_identifier_mention("PndLmdTrackQ*")[0], "type_expression")
        self.assertEqual(classify_identifier_mention("PndPidCorrelator")[0], "code_symbol")

    def test_protected_rubric_points_override_overpermissive_judge_coverage(self) -> None:
        dataset = load_gold_dataset(
            self.root / "evaluation" / "benchmarks" / "v2_6" / "gold_questions.yaml"
        )
        questions = {item.id: item for item in dataset.questions}

        class AllCoveredJudge:
            def generate_json(self, prompt, schema, system_instruction=None):
                payload = json.loads(prompt)
                return {
                    "point_scores": [
                        {"point_id": item["point_id"], "covered": True, "reason": "forced"}
                        for item in payload["required_points"]
                    ],
                    "covered_point_ids": [
                        item["point_id"] for item in payload["required_points"]
                    ],
                    "unsupported_claim_ids": [],
                    "claim_verdicts": [
                        {
                            "claim_id": item["claim_id"],
                            "status": "supported",
                            "severity": "minor",
                            "reason": "fixture",
                        }
                        for item in payload["claims"]
                    ],
                    "contradictions": [],
                }

        run_dir = (
            self.root
            / "data"
            / "evaluation"
            / "runs"
            / "m6-v2-36-qa-regression-rc3f"
            / "records"
        )
        g087_result = json.loads((run_dir / "g087.json").read_text(encoding="utf-8"))["result"]
        g087 = questions["g087"]
        self.assertEqual(_protected_rubric_point_ids(g087), {"p1"})
        self.assertNotIn("p1", _deterministic_point_ids(g087, g087_result))
        self.assertIn("p1", judge_answer(g087, g087_result, AllCoveredJudge())["critical_answer_points_missing"])

        g116_result = json.loads((run_dir / "g116.json").read_text(encoding="utf-8"))["result"]
        g116 = questions["g116"]
        self.assertEqual(_protected_rubric_point_ids(g116), {"p1", "p2", "p3"})
        self.assertEqual(
            judge_answer(g116, g116_result, AllCoveredJudge())["critical_answer_points_missing"],
            ["p1", "p2", "p3"],
        )

    def test_correct_refusal_has_not_applicable_final_evidence_metrics(self) -> None:
        case = next(
            item
            for item in self.dataset.questions
            if item.expected_status.value == "insufficient_evidence"
        )
        metrics = deterministic_case_metrics(
            case,
            {"status":"insufficient_evidence","answer":"","claims":[],"evidence":[]},
            {"plan":{"intent":case.intent},"ranked_object_ids":[]},
            {},
        )
        self.assertIsNone(metrics["final_evidence_recall"])
        self.assertIsNone(metrics["required_source_coverage"])

    def test_identifier_catalog_is_locked_and_uses_exact_file_tokens(self) -> None:
        lookup = {
            "locked": {
                "source_version_id": "repo@locked",
                "locator": {"path": "model/PndLmdAcceptance.cxx", "symbol": "PndLmdAcceptance"},
                "text": "class PndLmdAcceptance {}; input.root",
            },
            "unlocked": {
                "source_version_id": "repo@other",
                "locator": {"path": "model/OtherOnly.cxx", "symbol": "OtherOnly"},
                "text": "class OtherOnly {}; other.root",
            },
        }
        catalog = build_identifier_catalog(lookup, ["repo@locked"])
        self.assertIn("PndLmdAcceptance", catalog["symbols"])
        self.assertIn("model/PndLmdAcceptance.cxx", catalog["paths"])
        self.assertIn("input.root", catalog["paths"])
        self.assertNotIn("OtherOnly", catalog["symbols"])
        self.assertNotIn("other.root", catalog["paths"])

    def test_v2_exposed_questions_are_cluster_disjoint_and_not_release_eligible(self) -> None:
        dataset = load_gold_dataset(
            self.root / "evaluation" / "benchmarks" / "v2" / "gold_questions.yaml"
        )
        by_cluster = {}
        for case in dataset.questions:
            by_cluster.setdefault(case.cluster_id, set()).add(case.split)
        self.assertTrue(all(len(splits) == 1 for splits in by_cluster.values()))
        self.assertFalse(dataset.release_eligible)
        self.assertTrue(dataset.acceptance_exposed)
        self.assertEqual(Counter(case.split for case in dataset.questions), {"dev":80,"challenge":24,"regression":16})

    def test_v2_2_preserves_v2_1_question_identity_and_changes_only_three_rubrics(self) -> None:
        v21 = load_gold_dataset(
            self.root / "evaluation" / "benchmarks" / "v2_1" / "gold_questions.yaml"
        )
        v22 = load_gold_dataset(
            self.root / "evaluation" / "benchmarks" / "v2_2" / "gold_questions.yaml"
        )
        self.assertEqual(v22.benchmark_version, "m6-benchmark-v2.2")
        self.assertEqual(len(v22.questions), 120)
        self.assertTrue(all(item.review_status == "approved" for item in v22.questions))
        self.assertEqual(
            Counter(item.split for item in v22.questions),
            Counter(item.split for item in v21.questions),
        )
        self.assertEqual(
            Counter(item.expected_status.value for item in v22.questions),
            Counter(item.expected_status.value for item in v21.questions),
        )
        old = {item.id: item for item in v21.questions}
        new = {item.id: item for item in v22.questions}
        self.assertEqual(set(old), set(new))
        changed_ids: set[str] = set()
        allowed_rubric_fields = {
            "accepted_intents",
            "required_evidence_groups",
            "required_source_types",
        }
        for case_id in sorted(old):
            old_payload = old[case_id].model_dump(mode="json")
            new_payload = new[case_id].model_dump(mode="json")
            for field in ("query", "split", "cluster_id", "expected_status", "allowed_source_versions"):
                self.assertEqual(new_payload[field], old_payload[field], f"{case_id}: {field}")
            diff_fields = {
                field for field in old_payload if old_payload[field] != new_payload[field]
            }
            if diff_fields:
                changed_ids.add(case_id)
                self.assertTrue(
                    diff_fields <= allowed_rubric_fields,
                    f"{case_id} changed non-rubric fields: {sorted(diff_fields)}",
                )
        self.assertEqual(changed_ids, {"g074", "g079", "g086"})

    def test_v2_2_selector_audit_and_narrow_rubric_rules(self) -> None:
        dataset = load_gold_dataset(
            self.root / "evaluation" / "benchmarks" / "v2_2" / "gold_questions.yaml"
        )
        audit = json.loads(
            (
                self.root
                / "evaluation"
                / "benchmarks"
                / "v2_2"
                / "selector_match_count_audit.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(audit["unmatched_selectors"], [])
        questions = {item.id: item for item in dataset.questions}

        g074 = questions["g074"]
        self.assertEqual(g074.accepted_intents, ["data_flow"])
        self.assertEqual(g074.required_source_types, ["code"])
        self.assertEqual([group.group_id for group in g074.required_evidence_groups], ["g074.e2"])
        self.assertEqual(
            g074.required_evidence_groups[0].any_of[0].model_dump(mode="json", exclude_none=True),
            {"source_id": "luminosityfit", "path": "data/PndLmdCombinedDataReader.cxx"},
        )

        g079 = questions["g079"]
        self.assertEqual(g079.required_source_types, ["code"])
        data_product = next(group for group in g079.required_evidence_groups if group.group_id == "g079.data_product")
        selectors = [item.model_dump(mode="json", exclude_none=True) for item in data_product.any_of]
        self.assertEqual(
            selectors,
            [
                {"object_id": "data_product.pandaroot.lumi_trks_qa"},
                {
                    "source_id": "pandaroot",
                    "source_version_id": "pandaroot@18c09e91100db27867ded30e708b4dae95bd8357",
                    "path": "detectors/lmd/LmdQA/PndLmdTrackQ.cxx",
                },
                {
                    "source_id": "luminosityfit",
                    "source_version_id": "luminosityfit@ddd83dcd1a74093bf48ef259a2849a67f9413f32",
                    "path": "data/PndLmdCombinedDataReader.cxx",
                },
            ],
        )

        g086 = questions["g086"]
        self.assertEqual(g086.required_source_types, ["code"])
        self.assertEqual([group.group_id for group in g086.required_evidence_groups], ["g086.e2"])
        self.assertEqual(
            g086.required_evidence_groups[0].any_of[0].model_dump(mode="json", exclude_none=True),
            {"source_id": "luminosityfit", "path": "apps/createLmdFitData.cxx"},
        )

    def test_build_v2_cannot_overwrite_reviewed_dataset(self) -> None:
        dataset_path = (
            self.root / "evaluation" / "benchmarks" / "v2" / "gold_questions.yaml"
        )
        with self.assertRaisesRegex(ValueError, "refusing to overwrite reviewed benchmark v2"):
            assert_v2_draft_target_writable(dataset_path)

    def test_formal_rescore_identity_is_versioned_and_unknown_fails_closed(self) -> None:
        self.assertEqual(
            _formal_rescore_identity("m6-benchmark-v2.6"),
            {
                "artifact_evaluator": "evaluator-2_6_1",
                "schema_version": "2.6.1",
                "evaluation_revision": "evaluator-2.6.1",
                "selector_policy": (
                    "direct>ancestor>path_descendant_containment>explicit_v2_6_1_any_of"
                ),
            },
        )
        self.assertEqual(
            _formal_rescore_identity("m6-benchmark-v2.5"),
            {
                "artifact_evaluator": "evaluator-2_5_1",
                "schema_version": "2.5.1",
                "evaluation_revision": "evaluator-2.5.1",
                "selector_policy": (
                    "direct>ancestor>path_descendant_containment>explicit_v2_5_1_any_of"
                ),
            },
        )
        self.assertEqual(
            _formal_rescore_identity("m6-benchmark-v2.4"),
            {
                "artifact_evaluator": "evaluator-2_4",
                "schema_version": "2.4",
                "evaluation_revision": "evaluator-2.4",
                "selector_policy": (
                    "direct>ancestor>path_descendant_containment>explicit_v2_4_any_of"
                ),
            },
        )
        self.assertEqual(
            _formal_rescore_identity("m6-benchmark-v2.3"),
            {
                "artifact_evaluator": "evaluator-2_3",
                "schema_version": "2.3",
                "evaluation_revision": "evaluator-2.3",
                "selector_policy": (
                    "direct>ancestor>path_descendant_containment>explicit_v2_3_any_of"
                ),
            },
        )
        self.assertEqual(
            _formal_rescore_identity("m6-benchmark-v2.2"),
            {
                "artifact_evaluator": "evaluator-2_2",
                "schema_version": "2.2",
                "evaluation_revision": "evaluator-2.2",
                "selector_policy": (
                    "direct>ancestor>path_descendant_containment>explicit_v2_2_any_of"
                ),
            },
        )
        with self.assertRaisesRegex(ValueError, "unsupported reviewed benchmark version"):
            _formal_rescore_identity("m6-benchmark-v9.9")

        with tempfile.TemporaryDirectory() as temporary:
            project_root = Path(temporary)
            unknown_dataset = project_root / "unknown.yaml"
            unknown_dataset.write_text(
                (
                    self.root
                    / "evaluation"
                    / "benchmarks"
                    / "v2_3"
                    / "gold_questions.yaml"
                )
                .read_text(encoding="utf-8")
                .replace("benchmark_version: m6-benchmark-v2.3", "benchmark_version: m6-benchmark-v9.9", 1),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "unsupported reviewed benchmark version"):
                rescore_run(project_root, "unknown-version", unknown_dataset)
            rescore_dir = project_root / "data" / "evaluation" / "rescores"
            self.assertFalse(rescore_dir.exists())

    def test_rescore_identity_fingerprint_covers_all_immutable_inputs(self) -> None:
        dataset_path = (
            self.root / "evaluation" / "benchmarks" / "v2_3" / "gold_questions.yaml"
        )

        def prepare(project_root: Path) -> None:
            self._prepare_rescore_project(project_root, dataset_path, ["g001"])

        def run(project_root: Path, **kwargs):
            return rescore_run(
                project_root,
                "source",
                dataset_path,
                include_case_ids=["g001"],
                **kwargs,
            )

        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            first_root, second_root = Path(first), Path(second)
            prepare(first_root)
            prepare(second_root)
            first_report = run(first_root)
            second_report = run(second_root)
            self.assertEqual(
                first_report["rescore_identity_sha256"],
                second_report["rescore_identity_sha256"],
            )
            self.assertEqual(
                Path(first_report["output_dir"]).name,
                Path(second_report["output_dir"]).name,
            )

            first_output = Path(first_report["output_dir"])
            manifest = json.loads(
                (first_output / "rescore_manifest.json").read_text(encoding="utf-8")
            )
            persisted_report = json.loads(
                (first_output / "report.json").read_text(encoding="utf-8")
            )
            identity_hash = first_report["rescore_identity_sha256"]
            self.assertEqual(manifest["rescore_identity_sha256"], identity_hash)
            self.assertEqual(persisted_report["rescore_identity_sha256"], identity_hash)
            self.assertEqual(manifest["rescore_identity_fingerprint"], identity_hash[:12])
            self.assertEqual(persisted_report["rescore_identity_fingerprint"], identity_hash[:12])
            with self.assertRaisesRegex(FileExistsError, "refusing to overwrite existing rescore"):
                run(first_root)

        with tempfile.TemporaryDirectory() as temporary:
            project_root = Path(temporary)
            prepare(project_root)

            adjudication_a = project_root / "adjudication-a.yaml"
            adjudication_a.write_text(
                "adjudications:\n  - case_id: g001\n    covered_point_ids: []\n    reviewer: one\n",
                encoding="utf-8",
            )
            adjudication_b = project_root / "adjudication-b.yaml"
            adjudication_b.write_text(
                "adjudications:\n  - case_id: g001\n    covered_point_ids: []\n    reviewer: two\n",
                encoding="utf-8",
            )
            report_adjudication_a = run(project_root, adjudications_path=adjudication_a)
            report_adjudication_b = run(project_root, adjudications_path=adjudication_b)
            self.assertNotEqual(
                report_adjudication_a["rescore_identity_sha256"],
                report_adjudication_b["rescore_identity_sha256"],
            )
            self.assertNotEqual(
                Path(report_adjudication_a["output_dir"]).name,
                Path(report_adjudication_b["output_dir"]).name,
            )

            review_a = project_root / "review-a.yaml"
            review_a.write_text("run_id: source\ndecisions: []\n", encoding="utf-8")
            review_b = project_root / "review-b.yaml"
            review_b.write_text(
                "run_id: source\ndecisions:\n"
                "  - case_id: g001\n"
                "    human_review:\n"
                "      classification: metric_false_positive\n"
                "      action: rescore\n",
                encoding="utf-8",
            )
            report_review_a = run(project_root, review_decisions_path=review_a)
            report_review_b = run(project_root, review_decisions_path=review_b)
            self.assertNotEqual(
                report_review_a["rescore_identity_sha256"],
                report_review_b["rescore_identity_sha256"],
            )
            self.assertNotEqual(
                Path(report_review_a["output_dir"]).name,
                Path(report_review_b["output_dir"]).name,
            )

            self._write_rescore_fixture(project_root, dataset_path, "replacement", ["g001"])
            report_replacement_a = run(
                project_root,
                replacement_specs=[("replacement", ["g001"])],
            )
            replacement_results = project_root / "data" / "evaluation" / "runs" / "replacement" / "results.jsonl"
            replacement_record = json.loads(replacement_results.read_text(encoding="utf-8").splitlines()[0])
            replacement_record["duration_ms"] = 2
            replacement_results.write_text(
                json.dumps(replacement_record, ensure_ascii=False, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            report_replacement_b = run(
                project_root,
                replacement_specs=[("replacement", ["g001"])],
            )
            self.assertNotEqual(
                report_replacement_a["rescore_identity_sha256"],
                report_replacement_b["rescore_identity_sha256"],
            )
            self.assertNotEqual(
                Path(report_replacement_a["output_dir"]).name,
                Path(report_replacement_b["output_dir"]).name,
            )
            replacement_a = report_replacement_a["replacement_sources"][0]["selected_records_sha256"]
            replacement_b = report_replacement_b["replacement_sources"][0]["selected_records_sha256"]
            self.assertNotEqual(replacement_a, replacement_b)

    def test_rescore_replacement_run_id_preserves_v21_compatibility(self) -> None:
        dataset_path = (
            self.root / "evaluation" / "benchmarks" / "v2_1" / "gold_questions.yaml"
        )
        case_ids = ["g031", "g041", "g112", "g119"]
        with tempfile.TemporaryDirectory() as temporary:
            project_root = Path(temporary)
            self._prepare_rescore_project(project_root, dataset_path, case_ids)
            self._write_rescore_fixture(
                project_root,
                dataset_path,
                "replacement",
                case_ids,
            )
            report = rescore_run(
                project_root,
                "source",
                dataset_path,
                replacement_run_id="replacement",
            )
            self.assertEqual(report["runtime_replacements"], ["g041", "g119"])
            manifest = json.loads(
                (Path(report["output_dir"]) / "rescore_manifest.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(manifest["replacement_run_id"], "replacement")
            self.assertTrue(manifest["replacement_sources"][0]["legacy_compatibility_mode"])
            self.assertEqual(
                manifest["replacement_sources"][0]["case_ids"], ["g041", "g119"]
            )

    def test_multiple_replacement_specs_are_explicit_and_do_not_import_unrequested_records(self) -> None:
        dataset_path = (
            self.root / "evaluation" / "benchmarks" / "v2_2" / "gold_questions.yaml"
        )
        source_ids = ["g001", "g002", "g003"]
        with tempfile.TemporaryDirectory() as temporary:
            project_root = Path(temporary)
            self._prepare_rescore_project(project_root, dataset_path, source_ids)
            with self.assertRaisesRegex(ValueError, "non-empty explicit case_ids"):
                rescore_run(
                    project_root,
                    "source",
                    dataset_path,
                    replacement_specs=[("replacement-a", [])],
                )
            self._write_rescore_fixture(project_root, dataset_path, "replacement-a", ["g001"])
            self._write_rescore_fixture(project_root, dataset_path, "replacement-b", ["g002"])
            report = rescore_run(
                project_root,
                "source",
                dataset_path,
                replacement_specs=[
                    ("replacement-a", ["g001"]),
                    ("replacement-b", ["g002"]),
                ],
            )
            self.assertEqual(report["runtime_replacements"], ["g001", "g002"])
            manifest = json.loads(
                (Path(report["output_dir"]) / "rescore_manifest.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(manifest["cases"], 3)
            self.assertEqual(
                manifest["record_source_runs"],
                {"g001": "replacement-a", "g002": "replacement-b", "g003": "source"},
            )
            self.assertNotIn("g031", manifest["record_source_runs"])

    def test_rescore_rejects_duplicate_missing_overlapping_and_identity_mismatch_inputs(self) -> None:
        dataset_path = (
            self.root / "evaluation" / "benchmarks" / "v2_2" / "gold_questions.yaml"
        )
        with tempfile.TemporaryDirectory() as temporary:
            project_root = Path(temporary)
            self._prepare_rescore_project(project_root, dataset_path, ["g001", "g002"])
            self._write_rescore_fixture(project_root, dataset_path, "replacement-a", ["g001"])
            self._write_rescore_fixture(project_root, dataset_path, "replacement-b", ["g001"])
            with self.assertRaisesRegex(ValueError, "only one run"):
                rescore_run(
                    project_root,
                    "source",
                    dataset_path,
                    replacement_specs=[
                        ("replacement-a", ["g001"]),
                        ("replacement-b", ["g001"]),
                    ],
                )

            self._write_rescore_fixture(project_root, dataset_path, "replacement-missing", [])
            with self.assertRaisesRegex(ValueError, "missing requested cases"):
                rescore_run(
                    project_root,
                    "source",
                    dataset_path,
                    replacement_specs=[("replacement-missing", ["g002"])],
                )

            with self.assertRaisesRegex(ValueError, "both included and excluded"):
                rescore_run(
                    project_root,
                    "source",
                    dataset_path,
                    include_case_ids=["g001"],
                    exclude_case_ids=["g001"],
                )
            with self.assertRaisesRegex(ValueError, "include cases must be unique"):
                rescore_run(
                    project_root,
                    "source",
                    dataset_path,
                    include_case_ids=["g001", "g001"],
                )
            with self.assertRaisesRegex(ValueError, "exclude cases must be unique"):
                rescore_run(
                    project_root,
                    "source",
                    dataset_path,
                    exclude_case_ids=["g002", "g002"],
                )

            self._write_rescore_fixture(
                project_root,
                dataset_path,
                "replacement-identity-mismatch",
                ["g001"],
                identity_overrides={"index_identity": "different-identity"},
            )
            with self.assertRaisesRegex(ValueError, "identity mismatch"):
                rescore_run(
                    project_root,
                    "source",
                    dataset_path,
                    replacement_specs=[("replacement-identity-mismatch", ["g001"])],
                )

            self._write_rescore_fixture(project_root, dataset_path, "replacement-extra", ["g001", "g031"])
            report = rescore_run(
                project_root,
                "source",
                dataset_path,
                replacement_specs=[("replacement-extra", ["g001"])],
            )
            manifest = json.loads(
                (Path(report["output_dir"]) / "rescore_manifest.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(manifest["runtime_replacements"], ["g001"])
            self.assertNotIn("g031", manifest["record_source_runs"])

    def test_prompt_mismatch_is_recorded_as_diagnostic_composite_identity(self) -> None:
        dataset_path = (
            self.root / "evaluation" / "benchmarks" / "v2_2" / "gold_questions.yaml"
        )
        with tempfile.TemporaryDirectory() as temporary:
            project_root = Path(temporary)
            self._prepare_rescore_project(project_root, dataset_path, ["g001"])
            self._write_rescore_fixture(
                project_root,
                dataset_path,
                "replacement",
                ["g001"],
                prompt_hash="replacement-prompt-hash",
            )
            report = rescore_run(
                project_root,
                "source",
                dataset_path,
                replacement_specs=[("replacement", ["g001"])],
            )
            manifest = json.loads(
                (Path(report["output_dir"]) / "rescore_manifest.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(
                manifest["prompt_mismatches"],
                [
                    {
                        "replacement_run_id": "replacement",
                        "source_prompt_hash": "prompt-hash",
                        "replacement_prompt_hash": "replacement-prompt-hash",
                    }
                ],
            )
            self.assertTrue(manifest["diagnostic_composite_runtime"])
            self.assertFalse(manifest["uniform_candidate_identity"])
            self.assertEqual(manifest["record_source_runs"], {"g001": "replacement"})
            replacement_source = manifest["replacement_sources"][0]
            self.assertFalse(replacement_source["prompt_matches_source"])
            for field in ("manifest_sha256", "all_records_sha256", "selected_records_sha256"):
                self.assertRegex(replacement_source[field], r"^[0-9a-f]{64}$")

    def test_rescore_subset_is_exact_deterministic_and_never_a_full_dev_gate(self) -> None:
        dataset_path = (
            self.root / "evaluation" / "benchmarks" / "v2_2" / "gold_questions.yaml"
        )
        dataset = load_gold_dataset(dataset_path)
        dev_ids = [item.id for item in dataset.questions if item.split == "dev"]
        excluded = {
            "g023",
            "g025",
            "g039",
            "g057",
            "g060",
            "g063",
            "g073",
            "g088",
            "g089",
            "g095",
            "g110",
            "g114",
        }

        def run_isolated(root: Path) -> tuple[dict, dict]:
            self._prepare_rescore_project(root, dataset_path, dev_ids)
            report = rescore_run(
                root,
                "source",
                dataset_path,
                exclude_case_ids=sorted(excluded),
            )
            manifest = json.loads(
                (Path(report["output_dir"]) / "rescore_manifest.json").read_text(
                    encoding="utf-8"
                )
            )
            return report, manifest

        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            first_report, first_manifest = run_isolated(Path(first))
            second_report, second_manifest = run_isolated(Path(second))

        expected_ids = sorted(set(dev_ids) - excluded)
        self.assertEqual(len(expected_ids), 68)
        self.assertEqual(first_manifest["included_case_ids"], expected_ids)
        self.assertEqual(first_manifest["excluded_case_ids"], sorted(excluded))
        self.assertEqual(first_manifest["included_case_ids"], second_manifest["included_case_ids"])
        self.assertEqual(first_manifest["excluded_case_ids"], second_manifest["excluded_case_ids"])
        self.assertEqual(first_manifest["selection_sha256"], second_manifest["selection_sha256"])
        self.assertEqual(
            first_report["metrics"]["result_content_hash"],
            second_report["metrics"]["result_content_hash"],
        )
        self.assertFalse(first_report["complete_v2_dev"])
        self.assertTrue(first_manifest["subset_diagnostic_only"])
        self.assertEqual(first_manifest["rescore_model_calls"], 0)
        self.assertEqual(first_manifest["rescore_token_usage"], 0)
        self.assertFalse(first_report["development_gate"]["passed"])

    def test_complete_v25_prompt_mismatch_composite_is_diagnostic_only(self) -> None:
        dataset_path = (
            self.root / "evaluation" / "benchmarks" / "v2_5" / "gold_questions.yaml"
        )
        dev_ids = [
            item.id for item in load_gold_dataset(dataset_path).questions if item.split == "dev"
        ]
        self.assertEqual(len(dev_ids), 80)
        with tempfile.TemporaryDirectory() as temporary:
            project_root = Path(temporary)
            self._prepare_rescore_project(project_root, dataset_path, dev_ids)
            self._write_rescore_fixture(
                project_root,
                dataset_path,
                "replacement",
                ["g001"],
                prompt_hash="replacement-prompt-hash",
            )
            report = rescore_run(
                project_root,
                "source",
                dataset_path,
                replacement_specs=[("replacement", ["g001"])],
            )
            manifest = json.loads(
                (Path(report["output_dir"]) / "rescore_manifest.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertIn("evaluator-2_5_1", Path(report["output_dir"]).name)
            self.assertTrue(report["complete_v2_dev_structural"])
            self.assertFalse(report["complete_v2_dev"])
            self.assertTrue(report["diagnostic_composite_runtime"])
            self.assertFalse(manifest["uniform_candidate_identity"])
            self.assertFalse(manifest["complete_development_gate_eligible"])
            self.assertTrue(manifest["subset_diagnostic_only"])
            self.assertFalse(report["development_gate"]["passed"])
            self.assertFalse(report["development_gate"]["checks"]["complete_full_dev"])
            self.assertTrue(report["diagnostic_quality_checks"]["checks"]["complete_full_dev"])
            self.assertIn("Diagnostic composite runtime", report["development_gate"]["note"])

    def test_complete_v26_regression_composite_uses_regression_quality_contract(self) -> None:
        dataset_path = (
            self.root / "evaluation" / "benchmarks" / "v2_6" / "gold_questions.yaml"
        )
        regression_ids = [
            item.id
            for item in load_gold_dataset(dataset_path).questions
            if item.split == "regression"
        ]
        self.assertEqual(len(regression_ids), 16)
        with tempfile.TemporaryDirectory() as temporary:
            project_root = Path(temporary)
            self._prepare_rescore_project(project_root, dataset_path, regression_ids)
            self._write_rescore_fixture(
                project_root,
                dataset_path,
                "replacement",
                ["g087"],
            )
            report = rescore_run(
                project_root,
                "source",
                dataset_path,
                replacement_specs=[("replacement", ["g087"])],
            )
            manifest = json.loads(
                (Path(report["output_dir"]) / "rescore_manifest.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertIn("evaluator-2_6_1", Path(report["output_dir"]).name)
            self.assertEqual(report["rescore_scope"], "regression")
            self.assertTrue(report["complete_regression_structural"])
            self.assertFalse(report["complete_regression"])
            self.assertTrue(
                report["diagnostic_quality_checks"]["checks"]["complete_full_regression"]
            )
            self.assertFalse(report["regression_gate"]["passed"])
            self.assertFalse(report["regression_gate"]["checks"]["complete_full_regression"])
            self.assertEqual(manifest["rescore_scope"], "regression")
            self.assertTrue(manifest["complete_regression_structural"])
            self.assertFalse(manifest["complete_regression_gate_eligible"])
            self.assertTrue(manifest["subset_diagnostic_only"])

    def test_default_dataset_is_reviewed_v2_6_and_hidden_acceptance_is_blocked(self) -> None:
        dataset_path = default_gold_dataset_path(self.root)
        self.assertEqual(
            dataset_path,
            self.root / "evaluation" / "benchmarks" / "v2_6" / "gold_questions.yaml",
        )
        explicit_v25 = load_gold_dataset(
            self.root / "evaluation" / "benchmarks" / "v2_5" / "gold_questions.yaml"
        )
        self.assertEqual(explicit_v25.benchmark_version, "m6-benchmark-v2.5")
        explicit_v24 = load_gold_dataset(
            self.root / "evaluation" / "benchmarks" / "v2_4" / "gold_questions.yaml"
        )
        self.assertEqual(explicit_v24.benchmark_version, "m6-benchmark-v2.4")
        explicit_v23 = load_gold_dataset(
            self.root / "evaluation" / "benchmarks" / "v2_3" / "gold_questions.yaml"
        )
        self.assertEqual(explicit_v23.benchmark_version, "m6-benchmark-v2.3")
        explicit_v22 = load_gold_dataset(
            self.root / "evaluation" / "benchmarks" / "v2_2" / "gold_questions.yaml"
        )
        self.assertEqual(explicit_v22.benchmark_version, "m6-benchmark-v2.2")
        with self.assertRaisesRegex(ValueError, "hidden acceptance is not created"):
            run_evaluation(
                self.root,
                mode="qa",
                split="acceptance",
                run_id="must-not-be-created",
                dataset_path=dataset_path,
            )

    def test_explicit_v2_1_dataset_still_loads_and_validates(self) -> None:
        dataset_path = self.root / "evaluation" / "benchmarks" / "v2_1" / "gold_questions.yaml"
        dataset = load_gold_dataset(dataset_path)
        self.assertEqual(dataset.benchmark_version, "m6-benchmark-v2.1")
        dataset.require_approved()
        validation = validate_gold_dataset(self.root, dataset_path, require_approved=True)
        self.assertTrue(validation["structurally_valid"])
        self.assertTrue(validation["official_ready"])

    def test_regression_gate_requires_complete_sixteen_case_run(self) -> None:
        metrics = {
            "gold_recall_at_10": 1.0,
            "final_evidence_recall": 1.0,
            "citation_integrity": 1.0,
            "required_source_coverage_answered": 1.0,
            "identifier_miss_count": 0,
            "identifier_hallucination_rate": 0.0,
            "wrong_version_evidence_count": 0,
            "forbidden_evidence_count": 0,
            "answer_point_coverage": 1.0,
            "critical_answer_point_miss_count": 0,
            "contradiction_count": 0,
            "major_unsupported_claim_count": 0,
            "unhandled_exception_count": 0,
        }
        passed = evaluate_regression_gate(
            metrics, [], complete_full_regression=True, all_questions_approved=True
        )
        self.assertTrue(passed["passed"])
        incomplete = evaluate_regression_gate(
            metrics, [], complete_full_regression=False, all_questions_approved=True
        )
        self.assertFalse(incomplete["passed"])

    def test_judge_excerpt_keeps_support_near_cited_identifier(self) -> None:
        text = "prefix " * 1000 + "PndLmdDataReader::fillData checks IsSecondary"
        excerpt = _claim_relevant_evidence_excerpt(
            {"evidence_id":"e1","text":text},
            [{"claim_text":"Inspect PndLmdDataReader::fillData and IsSecondary.","evidence_ids":["e1"]}],
        )
        self.assertIn("PndLmdDataReader::fillData", excerpt)
        self.assertIn("IsSecondary", excerpt)


if __name__ == "__main__":
    unittest.main()
