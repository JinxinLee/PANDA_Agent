"""Pre-run E1-A2 scorer/runner checks using synthetic predictions only."""

import copy
import importlib.util
import inspect
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("e1_a2", ROOT / "evaluation/run_e1_a2_dynamic_question_decomposition_validation.py")
runner = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = runner
SPEC.loader.exec_module(runner)


@pytest.fixture
def manifest():
    return json.loads(runner.MANIFEST.read_text(encoding="utf-8"))


def test_manifest_invariants_and_distribution(manifest):
    runner.validate_manifest(manifest)
    assert len(manifest["cases"]) == 24
    assert len({c["pair_id"] for c in manifest["cases"]}) == 12
    assert manifest["cohort"]["total_reference_points"] == 44


@pytest.mark.parametrize("mutation", ["count", "pair", "variant", "span", "slot", "facet", "duplicate_id", "protected_group", "protected_path", "protected_split"])
def test_bad_manifests_rejected(manifest, mutation):
    case = manifest["cases"][1]
    if mutation == "count":
        manifest["cases"].pop()
    elif mutation == "pair":
        case["pair_id"] = "different"
    elif mutation == "variant":
        case["variant"] = "base"
    elif mutation == "span":
        case["reference_points"][0]["support_spans"] = ["not present"]
    elif mutation == "slot":
        case["reference_points"][0]["reference_slot_id"] = "different"
    elif mutation == "facet":
        case["reference_points"][0]["facet_type"] = "locator"
    elif mutation == "duplicate_id":
        case["reference_points"][0]["reference_point_id"] = manifest["cases"][0]["reference_points"][0]["reference_point_id"]
    elif mutation == "protected_group":
        case["source_group"] = "novel_validation"
    elif mutation == "protected_path":
        case["source_path"] = "evaluation/novel/v1/novel_holdout.yaml"
    else:
        case["source_split"] = "acceptance"
    with pytest.raises(ValueError):
        runner.validate_manifest(manifest)


def synthetic_case():
    return dict(case_id="b", pair_id="pair", variant="base", language="en", source_group="benchmark_dev",
                question="Where is X and why is it needed?", reference_points=[
                    dict(reference_point_id="ref1", reference_slot_id="slot.1", facet_type="locator", text="Locate X", support_spans=["Where is X"]),
                    dict(reference_point_id="ref2", reference_slot_id="slot.2", facet_type="cause_reason", text="Why X is needed", support_spans=["why is it needed"]),
                ])


def predictions():
    return [dict(answer_point_id="point.1", facet_type="locator", text="Locate X", support_spans=["Where is X"]),
            dict(answer_point_id="point.2", facet_type="cause_reason", text="Why X is needed", support_spans=["why is it needed"])]


def judgment():
    return dict(matched_pairs=[dict(reference_point_id="ref1", prediction_point_id="point.1", facet_type_match=True),
                               dict(reference_point_id="ref2", prediction_point_id="point.2", facet_type_match=True)],
                missing_reference_ids=[], extra_prediction_ids=[], hidden_prerequisite_prediction_ids=[])


def test_one_to_one_judgment_accepted():
    assert runner.validate_judgment(judgment(), synthetic_case()["reference_points"], predictions()) == judgment()


@pytest.mark.parametrize("mutation", ["duplicate", "unknown", "missing", "extra", "hidden", "type_flag"])
def test_invalid_judgments_rejected(mutation):
    j = judgment()
    if mutation == "duplicate":
        j["matched_pairs"].append(j["matched_pairs"][0])
    elif mutation == "unknown":
        j["matched_pairs"][0]["prediction_point_id"] = "unknown"
    elif mutation == "missing":
        j["missing_reference_ids"] = ["ref1"]
    elif mutation == "extra":
        j["extra_prediction_ids"] = ["point.1"]
    elif mutation == "hidden":
        j["hidden_prerequisite_prediction_ids"] = ["point.1"]
    else:
        j["matched_pairs"][0]["facet_type_match"] = False
    with pytest.raises(ValueError):
        runner.validate_judgment(j, synthetic_case()["reference_points"], predictions())


class FakeClient:
    def __init__(self, response):
        self.response = response
        self.requests = []

    def generate_json(self, prompt, schema, **kwargs):
        self.requests.append(json.loads(prompt))
        if isinstance(self.response, Exception):
            raise self.response
        return copy.deepcopy(self.response)

    def stats_snapshot(self):
        n = len(self.requests)
        return dict(model_calls=n, generation_calls=n, embedding_calls=0, token_usage=0)

    def stats_delta(self, before):
        return {k: v - before[k] for k, v in self.stats_snapshot().items()}


def test_invalid_decomposition_all_missing_no_judge():
    g = FakeClient({"points": [], "ambiguity": {"status": "clear", "reason": ""}})
    j = FakeClient(judgment())
    row = runner.score_case(synthetic_case(), g, j)
    assert row["scoreable"]
    assert row["decomposition"]["failure_category"] == "POINT_COUNT"
    assert row["semantic_evaluation"]["missing_reference_ids"] == ["ref1", "ref2"]
    assert not j.requests
    m = runner.metrics([row])
    assert m["micro_reference_recall"] == 0
    assert m["under_decomposed_cases"] == 1
    assert m["over_decomposed_cases"] == 0
    assert m["exact_count_cases"] == 0
    assert m["stable_pairs"] == 0


def test_valid_execution_payloads_and_incremental_persistence():
    raw = {"points": [{k: v for k, v in p.items() if k != "answer_point_id"} for p in predictions()], "ambiguity": {"status": "clear", "reason": ""}}
    g, j = FakeClient(raw), FakeClient(judgment())
    stages = []
    row = runner.score_case(synthetic_case(), g, j, lambda r: stages.append(r["stage"]))
    assert row["scoreable"]
    assert stages == ["decomposition_pending", "decomposition_complete", "judge_pending", "complete"]
    assert g.requests == [{"task": "decompose_user_question", "untrusted_question": synthetic_case()["question"]}]
    assert set(j.requests[0]) == {"question", "reference_points", "predicted_points"}
    assert row["logical_calls"] == {"decomposition": 1, "judge": 1}


def perfect_records(manifest):
    rows = []
    for case in manifest["cases"]:
        pts = [dict(answer_point_id=f"p{i}", facet_type=p["facet_type"], text=p["text"], support_spans=p["support_spans"]) for i, p in enumerate(case["reference_points"])]
        sem = runner.empty_semantics(case)
        sem.update(performed=True, missing_reference_ids=[], matched_pairs=[dict(reference_point_id=p["reference_point_id"], prediction_point_id=q["answer_point_id"], facet_type_match=True) for p, q in zip(case["reference_points"], pts)])
        rows.append({**case, "stage": "complete", "scoreable": True,
                     "decomposition": {"valid": True, "prediction": {"points": pts, "ambiguity": {"status": "clear", "reason": ""}}},
                     "semantic_evaluation": sem, "logical_calls": {"decomposition": 1, "judge": 1},
                     "usage": {"decomposition": {}, "judge": {}}})
    return rows


def test_metrics_and_pass_fail_inconclusive(manifest):
    rows = perfect_records(manifest)
    result = runner.aggregate(manifest, rows, "test")
    assert result["verdict"] == "PASS"
    m = result["primary_metrics"]
    assert m["matched_points"] == 44
    assert m["micro_reference_recall"] == m["micro_prediction_precision"] == m["matched_facet_accuracy"] == 1
    assert m["stable_pairs"] == 12
    assert m["exact_count_cases"] == 24
    row = rows[0]
    row["decomposition"]["prediction"]["points"].append(dict(answer_point_id="hidden.1", facet_type="implementation", text="Unstated component", support_spans=[row["question"]]))
    row["semantic_evaluation"]["extra_prediction_ids"] = ["hidden.1"]
    row["semantic_evaluation"]["hidden_prerequisite_prediction_ids"] = ["hidden.1"]
    result = runner.aggregate(manifest, rows, "test")
    assert result["verdict"] == "FAIL"
    assert not result["gates"]["G9"]["passed"]
    assert result["primary_metrics"]["micro_prediction_precision"] == 44 / 45
    assert result["primary_metrics"]["stable_pairs"] == 11
    assert result["primary_metrics"]["over_decomposed_cases"] == 1
    assert runner.aggregate(manifest, rows[:-1], "test")["verdict"] == "INCONCLUSIVE"
    rows[-1]["scoreable"] = False
    assert runner.aggregate(manifest, rows, "test")["verdict"] == "INCONCLUSIVE"


def test_judge_invalid_output_is_evaluation_infrastructure():
    raw = {"points": [{k: v for k, v in p.items() if k != "answer_point_id"} for p in predictions()], "ambiguity": {"status": "clear", "reason": ""}}
    row = runner.score_case(synthetic_case(), FakeClient(raw), FakeClient({}))
    assert not row["scoreable"]
    assert row["semantic_evaluation"]["failure_category"] == "EVALUATION_INFRASTRUCTURE"


def test_adapter_wrapped_json_failure_is_product_failure():
    try:
        try:
            json.loads("bad json")
        except ValueError as cause:
            raise runner.VertexCallError("wrapped") from cause
    except runner.VertexCallError as exc:
        assert runner.classify_failure(exc) == "SCHEMA_VALIDATION"
    assert runner.classify_failure(runner.VertexCallError("outage")) == "PROVIDER_INFRASTRUCTURE"


def test_runner_has_no_qa_or_retrieval_imports():
    source = inspect.getsource(runner)
    assert "from panda_agent.qa" not in source
    assert "from panda_agent.retrieval" not in source
    assert "QAAgent(" not in source
    assert "Retriever(" not in source
