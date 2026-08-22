from __future__ import annotations

import unittest
from types import SimpleNamespace

from panda_agent.c4_sparse_evaluation import (
    INTENT_CYCLE,
    classify_case,
    deterministic_screening_order,
    evaluate_c4_hard_gates,
    explicit_identifier_retention,
    load_c2_plan_records,
    normalize_plan_record,
    provenance_contamination_audit,
    rank_metrics,
    read_only_sparse_preflight,
    run_c4_sparse_evaluation,
    select_screening_cases,
)
from panda_agent.lexical_query import LexicalQuery, LexicalQueryComponent


def _record(case_id: str, intent: str = "usage", *, lexical: bool = True, **changes):
    question = f"Which API ownership covers PndThing_{case_id}?"
    plan = {
        "intent": intent,
        "target_repositories": ["pandaroot"],
        "resolved_versions": {"pandaroot": "locked"},
        "source_budgets": {"code": 1.0},
        "analysis_diagnostics": {
            "analyzer_accepted_semantic_delta": {
                "concepts": [
                    {"value": "owner API", "support_spans": ["API ownership"]}
                ]
            }
        },
    }
    record = {
        "case_id": case_id,
        "question": question,
        "split": "dev",
        "review_status": "approved",
        "effective_product_language": "en",
        "expected_status": "answered",
        "authoritative_evidence": True,
        "required_evidence_groups": [
            {"group_id": f"{case_id}.e1", "critical": True, "any_of": [{"object_id": "hit"}]}
        ],
        "intent": intent,
        "prompt_version": "3.7.0",
        "faithful": True,
        "c2_compatible": True,
        "retrieval_plan": plan,
    }
    if not lexical:
        record["lexical_query"] = {
            "text": question,
            "raw_question": question,
            "components": [],
            "excluded_component_classes": [],
        }
    record.update(changes)
    return record


class _Encoder:
    def __init__(self):
        self.calls = []

    def query_embed(self, text):
        self.calls.append(text)
        return [{"indices": [1], "values": [1.0]}]


class _Qdrant:
    def __init__(self):
        self.calls = []
        self.rankings = [["miss", "hit"], ["hit", "miss"]] * 16

    def collection_exists(self, name):
        return True

    def get_collection(self, name):
        return SimpleNamespace(config=SimpleNamespace(params=SimpleNamespace(sparse_vectors={})))

    def query_points(self, **kwargs):
        self.calls.append(kwargs)
        ranking = self.rankings[len(self.calls) - 1]
        return SimpleNamespace(points=[SimpleNamespace(payload={"object_id": item}) for item in ranking])


class _FailEncoder(_Encoder):
    def query_embed(self, text):
        self.calls.append(text)
        raise RuntimeError("encode unavailable")


class _FailQdrant(_Qdrant):
    def query_points(self, **kwargs):
        self.calls.append(kwargs)
        raise RuntimeError("read unavailable")


class _ContractQdrant:
    def __init__(self, *, vector_name="sparse", modifier="idf"):
        self.vector_name = vector_name
        self.modifier = modifier
        self.read_calls = []

    def collection_exists(self, name):
        self.read_calls.append(("exists", name))
        return True

    def get_collection(self, name):
        self.read_calls.append(("get", name))
        config = SimpleNamespace(
            params=SimpleNamespace(
                sparse_vectors={self.vector_name: SimpleNamespace(modifier=self.modifier)}
            )
        )
        return SimpleNamespace(
            config=config,
            index_identity={"schema_version": 4, "fingerprint": "fp"},
        )

    def query_points(self, **kwargs):
        return SimpleNamespace(points=[])


class C4SparseEvaluationTests(unittest.TestCase):
    def test_load_normalizes_without_analyzer_and_builds_lexical_query(self):
        supplied = _record("g100")
        supplied["lexical_query"] = {
            "text": "CORRUPTED SUPPLIED QUERY",
            "raw_question": supplied["question"],
            "components": [],
            "excluded_component_classes": [],
        }
        records = load_c2_plan_records([supplied])
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["prompt_version"], "3.7.0")
        self.assertNotEqual(records[0]["lexical_query"].text, records[0]["raw_question"])
        self.assertNotEqual(records[0]["lexical_query"].text, "CORRUPTED SUPPLIED QUERY")

    def test_selection_uses_fixed_intent_cycle_and_id_round_robin(self):
        records = [
            _record("g030", "api"),
            _record("g004", "installation"),
            _record("g017", "usage"),
            _record("g005", "installation"),
            _record("g031", "api"),
        ]
        self.assertEqual(
            deterministic_screening_order(records),
            ["g004", "g017", "g030", "g005", "g031"],
        )
        self.assertEqual(INTENT_CYCLE[0], "installation")

    def test_faithful_plan_and_explicit_exclusions_are_fail_closed(self):
        bad_prompt = _record("g100", prompt_version="3.6.0")
        bad_plan = _record("g101", faithful=False)
        excluded = _record("g011")
        selected = select_screening_cases([bad_prompt, bad_plan, excluded])
        self.assertEqual(selected, [])
        missing_proof = _record("g102")
        missing_proof.pop("faithful")
        missing_proof.pop("c2_compatible")
        missing_proof.pop("prompt_version")
        self.assertEqual(select_screening_cases([missing_proof]), [])

    def test_rank_metrics_and_six_classifications(self):
        groups = [{"group_id": "e1", "critical": True, "any_of": [{"object_id": "a"}]}]
        metrics = rank_metrics(groups, ["x", "a"], {})
        self.assertEqual(metrics["first_relevant_rank"], 2)
        self.assertEqual(metrics["recall_at_5"], 1.0)
        self.assertEqual(metrics["mrr"], 0.5)
        self.assertEqual(classify_case(None, None), "no_hit_both")
        self.assertEqual(classify_case(None, 2), "recovered_hit")
        self.assertEqual(classify_case(2, 1), "improved")
        self.assertEqual(classify_case(1, 2), "regressed")
        self.assertEqual(classify_case(1, 1), "unchanged")
        self.assertEqual(classify_case(1, None), "lost_hit")

    def test_raw_and_lexical_sparse_use_identical_non_text_parameters(self):
        records = [_record(f"g{index:03d}", intent="usage") for index in range(100, 106)]
        encoder = _Encoder()
        qdrant = _Qdrant()
        filters = []

        def filter_builder(plan, sources):
            value = {"plan": plan["intent"], "sources": tuple(sources)}
            filters.append(value)
            return value

        result = run_c4_sparse_evaluation(
            records,
            qdrant=qdrant,
            encoder=encoder,
            context_sources=["curated_panda_domain"],
            object_lookup={"hit": {"object_id": "hit"}},
            preflight={"available": True, "contract_ok": True, "evidence_complete": True, "status": "PASS"},
            filter_builder=filter_builder,
        )
        self.assertEqual(result["verdict"], "PASS")
        self.assertEqual(result["call_accounting"]["sparse_encoder_calls"], 12)
        self.assertEqual(result["call_accounting"]["sparse_reads"], 12)
        for name in ("analyzer_calls", "vertex_calls", "dense_embedding_calls", "dense_reads", "downstream_calls", "write_calls", "retries"):
            self.assertEqual(result["call_accounting"][name], 0)
        self.assertEqual(len(encoder.calls), 12)
        self.assertEqual(len(qdrant.calls), 12)
        for pair in zip(qdrant.calls[::2], qdrant.calls[1::2]):
            self.assertEqual(pair[0]["collection_name"], pair[1]["collection_name"])
            self.assertEqual(pair[0]["using"], pair[1]["using"])
            self.assertEqual(pair[0]["limit"], pair[1]["limit"])
            self.assertIs(pair[0]["query_filter"], pair[1]["query_filter"])

    def test_exact_twelve_case_budget_is_twenty_four_encodes_and_reads(self):
        records = [_record(f"g{index:03d}", intent="usage") for index in range(200, 212)]
        result = run_c4_sparse_evaluation(
            records,
            qdrant=_Qdrant(),
            encoder=_Encoder(),
            object_lookup={"hit": {"object_id": "hit"}},
            preflight={"available": True, "contract_ok": True, "evidence_complete": True},
            filter_builder=lambda plan, sources: {"intent": plan["intent"]},
            max_cases=12,
        )
        self.assertEqual(result["selection"]["selected_count"], 12)
        self.assertEqual(result["call_accounting"]["sparse_encoder_calls"], 24)
        self.assertEqual(result["call_accounting"]["sparse_reads"], 24)
        self.assertEqual(result["call_accounting"]["retries"], 0)
        with self.assertRaisesRegex(ValueError, "exactly 20"):
            run_c4_sparse_evaluation(records, top_k=19)

    def test_preflight_requires_sparse_contract_and_zero_reads_when_qdrant_unavailable(self):
        receipt = {"receipt_id": "bm25-receipt"}
        passed = read_only_sparse_preflight(
            _ContractQdrant(),
            collection_name="panda_knowledge_v1",
            vector_name="sparse",
            expected_encoder_receipt=receipt,
            encoder_receipt=receipt,
            expected_schema_version=4,
            expected_fingerprint="fp",
        )
        self.assertTrue(passed["available"])
        self.assertTrue(passed["contract_ok"])
        self.assertEqual(passed["write_calls"], 0)
        self.assertEqual(passed["read_calls"], 2)
        unavailable = read_only_sparse_preflight(
            None,
            collection_name="panda_knowledge_v1",
            vector_name="sparse",
            expected_encoder_receipt=receipt,
        )
        self.assertFalse(unavailable["available"])
        self.assertEqual(unavailable["read_calls"], 0)
        wrong_modifier = read_only_sparse_preflight(
            _ContractQdrant(modifier="none"),
            collection_name="panda_knowledge_v1",
            vector_name="sparse",
            expected_encoder_receipt=receipt,
            encoder_receipt=receipt,
            expected_schema_version=4,
            expected_fingerprint="fp",
        )
        self.assertFalse(wrong_modifier["available"])

        wrong_name = read_only_sparse_preflight(
            _ContractQdrant(vector_name="other"),
            collection_name="panda_knowledge_v1",
            vector_name="sparse",
            expected_encoder_receipt=receipt,
            encoder_receipt=receipt,
            expected_schema_version=4,
            expected_fingerprint="fp",
        )
        self.assertFalse(wrong_name["available"])
        self.assertIn("sparse_vector_name_missing", wrong_name["errors"])

        wrong_identity = read_only_sparse_preflight(
            _ContractQdrant(),
            collection_name="panda_knowledge_v1",
            vector_name="sparse",
            expected_encoder_receipt=receipt,
            encoder_receipt={"receipt_id": "different"},
            expected_schema_version=4,
            expected_fingerprint="fp",
        )
        self.assertFalse(wrong_identity["available"])
        self.assertIn("encoder_receipt_identity_mismatch", wrong_identity["errors"])

        missing_identity = _ContractQdrant()
        missing_receipt = read_only_sparse_preflight(
            missing_identity,
            collection_name="panda_knowledge_v1",
            vector_name="sparse",
            expected_schema_version=4,
            expected_fingerprint="fp",
        )
        self.assertFalse(missing_receipt["available"])
        self.assertEqual(missing_identity.read_calls, [])

    def test_attempt_counters_include_calls_that_raise_without_retry(self):
        records = [_record(f"g{index:03d}") for index in range(220, 226)]
        kwargs = {
            "preflight": {"available": True, "contract_ok": True, "evidence_complete": True},
            "filter_builder": lambda plan, sources: {"intent": plan["intent"]},
        }
        encode_failure = run_c4_sparse_evaluation(records, qdrant=_Qdrant(), encoder=_FailEncoder(), **kwargs)
        self.assertEqual(encode_failure["call_accounting"]["sparse_encoder_calls"], 1)
        self.assertEqual(encode_failure["call_accounting"]["sparse_reads"], 0)
        self.assertEqual(encode_failure["call_accounting"]["retries"], 0)
        read_failure = run_c4_sparse_evaluation(records, qdrant=_FailQdrant(), encoder=_Encoder(), **kwargs)
        self.assertEqual(read_failure["call_accounting"]["sparse_encoder_calls"], 2)
        self.assertEqual(read_failure["call_accounting"]["sparse_reads"], 1)
        self.assertEqual(read_failure["call_accounting"]["retries"], 0)

    def test_critical_new_misses_are_reported_per_case_and_group(self):
        groups = [
            {"group_id": "critical_a", "critical": True, "any_of": [{"object_id": "a"}]},
            {"group_id": "critical_b", "critical": True, "any_of": [{"object_id": "b"}]},
        ]

        class _CriticalQdrant(_Qdrant):
            def query_points(self, **kwargs):
                self.calls.append(kwargs)
                ranking = ["a", "b"] if len(self.calls) % 2 else ["a"]
                return SimpleNamespace(points=[SimpleNamespace(payload={"object_id": item}) for item in ranking])

        records = [_record(f"g{index:03d}") for index in range(230, 236)]
        for record in records:
            record["required_evidence_groups"] = groups
        result = run_c4_sparse_evaluation(
            records,
            qdrant=_CriticalQdrant(),
            encoder=_Encoder(),
            object_lookup={"a": {"object_id": "a"}, "b": {"object_id": "b"}},
            preflight={"available": True, "contract_ok": True, "evidence_complete": True},
            filter_builder=lambda plan, sources: {"intent": plan["intent"]},
        )
        self.assertEqual(len(result["critical_new_miss_by_case"]), 6)
        self.assertEqual(len(result["critical_new_miss_group_ids"]), 6)
        self.assertEqual(result["critical_new_miss_group_ids"][0]["group_id"], "critical_b")

    def test_identifier_retention_and_contamination_audit(self):
        lexical = LexicalQuery(
            text="PndThing_g100 API",
            raw_question="Where is PndThing_g100?",
            components=[
                LexicalQueryComponent(
                    kind="analyzer_concept",
                    value="API",
                    provenance="analyzer_accepted",
                    appended=True,
                )
            ],
            excluded_component_classes=["gold_evidence"],
        )
        retention = explicit_identifier_retention(lexical.raw_question, lexical)
        self.assertTrue(retention["all_retained"])
        exact = LexicalQuery(
            text="PndThing_g100 deadbeef v1.2.3",
            raw_question="PndThing_g100 deadbeef v1.2.3",
            components=[],
            excluded_component_classes=[],
        )
        exact_retention = explicit_identifier_retention(exact.raw_question, exact)
        self.assertEqual(exact_retention["missing_count"], 0)
        changed_case = LexicalQuery(
            text="pndthing_g100 deadbeef v1.2.3",
            raw_question=exact.raw_question,
            components=[],
            excluded_component_classes=[],
        )
        self.assertIn("PndThing_g100", explicit_identifier_retention(exact.raw_question, changed_case)["missing_tokens"])
        self.assertFalse(provenance_contamination_audit(lexical)["contamination"])
        contaminated = LexicalQuery(
            text=lexical.text,
            raw_question=lexical.raw_question,
            components=[
                LexicalQueryComponent(
                    kind="gold_evidence",
                    value="object.secret",
                    provenance="gold_evidence",
                    appended=True,
                )
            ],
            excluded_component_classes=[],
        )
        self.assertTrue(provenance_contamination_audit(contaminated)["contamination"])

    def test_fewer_than_six_and_infrastructure_unavailable_are_inconclusive(self):
        few = run_c4_sparse_evaluation([_record("g100")], qdrant=_Qdrant(), encoder=_Encoder())
        self.assertEqual(few["verdict"], "INCONCLUSIVE")
        self.assertIn("fewer_than_6_qualified_cases", few["gates"]["inconclusive_reasons"])
        records = [_record(f"g{index:03d}") for index in range(100, 106)]
        unavailable = run_c4_sparse_evaluation(
            records,
            qdrant=None,
            encoder=_Encoder(),
            preflight={"available": False, "status": "INCONCLUSIVE"},
        )
        self.assertEqual(unavailable["verdict"], "INCONCLUSIVE")
        self.assertIn("infrastructure_unavailable", unavailable["gates"]["inconclusive_reasons"])

    def test_gate_marks_quality_regression_inconclusive(self):
        result = {
            "selection": {"selected_count": 6},
            "preflight": {"available": True},
            "metrics": {
                "raw": {"recall_at_10": 1.0, "recall_at_20": 1.0, "critical_coverage": 1.0},
                "lexical": {"recall_at_10": 0.5, "recall_at_20": 0.5, "critical_coverage": 0.5},
            },
            "classification_counts": {"lost_hit": 0, "negative": 0, "positive": 0, "informative": 6},
            "critical_new_misses": 1,
            "identifier_retention": {"missing_count": 0},
            "provenance_contamination": {"contamination": False},
            "call_accounting": {"sparse_encoder_calls": 12, "sparse_reads": 12},
            "plan_filter_identity_proven": True,
        }
        gates = evaluate_c4_hard_gates(result)
        self.assertEqual(gates["verdict"], "INCONCLUSIVE")
        self.assertIn("recall_at_10_regressed", gates["inconclusive_reasons"])

    def test_gate_reserves_fail_for_contract_defect(self):
        result = {
            "selection": {"selected_count": 6},
            "preflight": {"available": True},
            "metrics": {
                "raw": {"recall_at_10": 0.5, "recall_at_20": 0.5, "critical_coverage": 1.0},
                "lexical": {"recall_at_10": 0.5, "recall_at_20": 0.5, "critical_coverage": 1.0},
            },
            "classification_counts": {"lost_hit": 0, "negative": 0, "positive": 1, "informative": 6},
            "critical_new_misses": 0,
            "identifier_retention": {"missing_count": 0},
            "provenance_contamination": {"contamination": True},
            "call_accounting": {"sparse_encoder_calls": 12, "sparse_reads": 12},
            "plan_filter_identity_proven": True,
        }
        self.assertEqual(evaluate_c4_hard_gates(result)["verdict"], "FAIL")

        isolated = dict(result)
        isolated["provenance_contamination"] = {"contamination": False}
        isolated["cases"] = [
            {
                "same_non_text_parameters": False,
                "filter_reused": True,
                "raw_query_parameters": {"limit": 20},
                "lexical_query_parameters": {"limit": 19},
            }
        ]
        self.assertEqual(evaluate_c4_hard_gates(isolated)["verdict"], "FAIL")


if __name__ == "__main__":
    unittest.main()
