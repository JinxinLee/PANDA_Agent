"""Fake-only prospective contract, semantic scoring and execution-boundary checks."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys

import pytest

PATH = Path(__file__).resolve().parents[2] / "evaluation/run_e1_c1_real_style_confirmation.py"
SPEC = importlib.util.spec_from_file_location("e1_c1_runner", PATH)
r = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = r
SPEC.loader.exec_module(r)


@pytest.fixture
def manifest():
    m = r.read(r.MANIFEST)
    m["cases"] = r.resolve_cases(m)
    return m


class Fake:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def stats_snapshot(self):
        return len(self.calls)

    def stats_delta(self, before):
        n = len(self.calls) - before
        return dict(model_calls=n, generation_calls=n, embedding_calls=0, token_usage=0)

    def generate_json(self, prompt, schema, **kwargs):
        self.calls.append((json.loads(prompt), schema, kwargs))
        if isinstance(self.response, Exception):
            raise self.response
        return deepcopy(self.response)


def perfect(m):
    raw, judged = [], []
    for c in m["cases"]:
        ps = [{"answer_point_id": f"point.{i+1}", "text": p["text"], "support_spans": p["support_spans"]}
              for i, p in enumerate(c["reference_points"])]
        j = {"matched_pairs": [{"reference_point_id": ref["reference_point_id"], "prediction_point_id": p["answer_point_id"]}
                               for ref, p in zip(c["reference_points"], ps)],
             "missing_reference_ids": [], "extra_prediction_ids": [], "hidden_prerequisite_prediction_ids": []}
        raw.append({"case_id": c["case_id"], "valid": True, "stage": "complete", "failure_category": None,
                    "prediction": {"points": ps}, "usage": {}})
        judged.append({"case_id": c["case_id"], "stage": "complete", "scoreable": True, "judgment": j, "usage": {}})
    return raw, judged


def test_exact_selector_source_and_contract(manifest):
    r.validate_manifest(manifest)
    source = json.loads(r.git("show", f"{r.SOURCE_COMMIT}:{r.SOURCE_PATH}"))
    assert manifest["cases"] == [c for c in source["cases"] if c["pair_id"] in r.PAIR_IDS]
    assert len(manifest["cases"]) == 12
    assert sum(len(c["reference_points"]) for c in manifest["cases"]) == 28


@pytest.mark.parametrize("change", ["span", "text", "source", "selector", "gate", "sentinel", "order"])
def test_manifest_rejects_corruption(manifest, change):
    if change == "span":
        manifest["cases"][0]["reference_points"][0]["support_spans"] = ["absent substring"]
    elif change == "text":
        manifest["cases"][0]["reference_points"][0]["text"] = "different obligation"
    elif change == "source":
        manifest["source_manifest_commit"] = "HEAD"
    elif change == "selector":
        manifest["selected_pair_ids"][0] = "e1a2.pair06"
    elif change == "gate":
        manifest["gates"]["stable_pairs"] = 5
    elif change == "sentinel":
        manifest["sentinel"]["required_predictions_per_variant"] = 2
    else:
        manifest["cases"].reverse()
    with pytest.raises(ValueError):
        r.validate_manifest(manifest)


def test_question_only_capture_and_taxonomy_blind_judge(manifest):
    c = manifest["cases"][0]
    fake = Fake({"points": [{"text": p["text"], "support_spans": p["support_spans"]} for p in c["reference_points"]],
                 "ambiguity": {"status": "clear", "reason": ""}})
    raw = r.decompose_one(c, fake)
    assert raw["valid"] and raw["raw_proposal"] == fake.response
    assert fake.calls[0][0] == {"task": "decompose_user_question", "untrusted_question": c["question"]}
    ps = raw["prediction"]["points"]
    response = {"matched_pairs": [{"reference_point_id": ref["reference_point_id"], "prediction_point_id": p["answer_point_id"]}
                                  for ref, p in zip(c["reference_points"], ps)],
                "missing_reference_ids": [], "extra_prediction_ids": [], "hidden_prerequisite_prediction_ids": []}
    judge = Fake(response)
    assert r.judge_one(c, raw, judge)["scoreable"]
    payload = judge.calls[0][0]
    assert set(payload) == {"question", "reference_points", "predicted_points"}
    assert all(set(p) == {"reference_point_id", "text"} for p in payload["reference_points"])
    assert all(set(p) == {"answer_point_id", "text"} for p in payload["predicted_points"])


@pytest.mark.parametrize("change", ["repeated_match", "unknown", "missing_set", "extra_set", "hidden_set", "duplicate_list"])
def test_judge_contract_rejects_invalid_ids(manifest, change):
    raw, judged = perfect(manifest)
    j = judged[0]["judgment"]
    if change == "repeated_match":
        j["matched_pairs"].append(j["matched_pairs"][0])
    elif change == "unknown":
        j["matched_pairs"][0]["prediction_point_id"] = "unknown"
    elif change == "missing_set":
        j["missing_reference_ids"] = [manifest["cases"][0]["reference_points"][0]["reference_point_id"]]
    elif change == "extra_set":
        j["extra_prediction_ids"] = ["point.1"]
    elif change == "hidden_set":
        j["hidden_prerequisite_prediction_ids"] = ["point.1"]
    else:
        j["missing_reference_ids"] = ["unknown", "unknown"]
    with pytest.raises(ValueError):
        r.validate_judgment(j, manifest["cases"][0]["reference_points"], raw[0]["prediction"]["points"])


def test_semantic_pass_independent_of_taxonomy(manifest):
    raw, judged = perfect(manifest)
    before = r.aggregate(manifest, raw, judged)
    for row in raw:
        for p in row["prediction"]["points"]:
            p["facet_type"] = "mechanism"
    after = r.aggregate(manifest, raw, judged)
    assert before["verdict"] == after["verdict"] == "PASS"
    assert before["metrics"] == after["metrics"]
    assert before["gates"] == after["gates"]
    assert before["metrics"]["reference_points"] == 28
    assert before["metrics"]["stable_pairs"] == 6


def test_merge_cannot_cover_two_slots_and_pair_gate_fails(manifest):
    raw, judged = perfect(manifest)
    for idx in [0, 2, 4]:
        raw[idx]["prediction"]["points"].pop()
        match = judged[idx]["judgment"]["matched_pairs"].pop()
        judged[idx]["judgment"]["missing_reference_ids"] = [match["reference_point_id"]]
        r.validate_judgment(judged[idx]["judgment"], manifest["cases"][idx]["reference_points"], raw[idx]["prediction"]["points"])
    result = r.aggregate(manifest, raw, judged)
    assert result["metrics"]["stable_pairs"] == 3
    assert result["metrics"]["matched_points"] == 25
    assert result["verdict"] == "FAIL"


def test_hidden_prerequisite_is_hard_gate(manifest):
    raw, judged = perfect(manifest)
    raw[0]["prediction"]["points"].append({"answer_point_id": "point.4", "text": "Inferred prerequisite"})
    judged[0]["judgment"].update(extra_prediction_ids=["point.4"], hidden_prerequisite_prediction_ids=["point.4"])
    result = r.aggregate(manifest, raw, judged)
    assert result["verdict"] == "FAIL"
    assert not result["gates"]["hidden_prerequisite_predictions"]["passed"]


@pytest.mark.parametrize("change", ["partial_raw", "partial_judge", "judge_failure", "provider_failure", "embedding"])
def test_infrastructure_never_partial_pass(manifest, change):
    raw, judged = perfect(manifest)
    if change == "partial_raw":
        raw.pop()
        judged.pop()
    elif change == "partial_judge":
        judged.pop()
    elif change == "judge_failure":
        judged[0]["scoreable"] = False
    elif change == "provider_failure":
        raw[0].update(valid=False, prediction=None, failure_category="PROVIDER_INFRASTRUCTURE")
        judged.pop(0)
    else:
        raw[0]["usage"] = {"embedding_calls": 1}
    result = r.aggregate(manifest, raw, judged)
    assert result["verdict"] == "INCONCLUSIVE"
    assert result["metrics"] is None and not result["gates"]


def test_invalid_product_counts_missing_not_infrastructure(manifest):
    raw, judged = perfect(manifest)
    raw[0].update(valid=False, prediction=None, failure_category="SCHEMA_VALIDATION")
    judged.pop(0)
    result = r.aggregate(manifest, raw, judged)
    assert result["metrics"]["matched_points"] == 25
    assert result["metrics"]["under_decomposed_cases"] == 1
    assert result["metrics"]["stable_pairs"] == 5


def test_failures_record_types_without_provider_messages(manifest):
    product = r.decompose_one(manifest["cases"][0], Fake({"points": [], "ambiguity": {"status": "clear", "reason": ""}}))
    assert product["failure_category"] == "POINT_COUNT"
    infra = r.decompose_one(manifest["cases"][0], Fake(RuntimeError("secret credential")))
    assert infra["failure_category"] == "PROVIDER_INFRASTRUCTURE"
    assert "secret credential" not in json.dumps(infra)


def test_resume_skips_completed_and_rejects_uncertain_request(manifest, tmp_path):
    m = deepcopy(manifest)
    m["cases"] = m["cases"][:1]
    path = tmp_path / "raw.json"
    fake = Fake({"points": [{"text": "Locate builder", "support_spans": [m["cases"][0]["question"]]}],
                 "ambiguity": {"status": "clear", "reason": ""}})
    first = r.run_phase(m, fake, path, "frozen")
    second = r.run_phase(m, fake, path, "frozen")
    assert len(fake.calls) == 1 and first == second
    first["records"][0]["stage"] = "request_started"
    r.save(path, first)
    with pytest.raises(ValueError, match="ambiguous interrupted"):
        r.run_phase(m, fake, path, "frozen")
    assert len(fake.calls) == 1


def test_pair09_sentinel_both_variants(manifest):
    raw, judged = perfect(manifest)
    result = r.aggregate(manifest, raw, judged)
    assert result["pair09_sentinel"]["passed"]
    assert result["pair09_sentinel"]["base"]["predicted_count"] == 3
    assert result["pair09_sentinel"]["paraphrase"]["matched_references"] == 3
    idx = next(i for i,c in enumerate(manifest["cases"]) if c["case_id"] == "e1a2.p09")
    raw[idx]["prediction"]["points"].pop()
    match = judged[idx]["judgment"]["matched_pairs"].pop()
    judged[idx]["judgment"]["missing_reference_ids"] = [match["reference_point_id"]]
    result = r.aggregate(manifest, raw, judged)
    assert result["verdict"] == "FAIL"
    assert result["pair09_sentinel"]["base"]["passed"]
    assert not result["pair09_sentinel"]["paraphrase"]["passed"]
    assert not result["pair09_sentinel"]["passed"]


@pytest.mark.parametrize("change", ["missing_raw_commit", "modified_raw", "partial_raw"])
def test_judge_requires_full_frozen_raw_before_client(manifest, monkeypatch, tmp_path, change):
    raw, _ = perfect(manifest)
    if change == "partial_raw":
        raw.pop()
    package = {"preregistration_commit": "prereg", "raw_commit": None, "records": raw}
    raw_path = tmp_path / "raw.json"
    r.save(raw_path, package)
    monkeypatch.setattr(r, "RAW", raw_path)
    monkeypatch.setattr(r, "verify_freeze", lambda *args: None)
    monkeypatch.setattr(r, "VertexAIClient", lambda *args: pytest.fail("must not construct provider"))
    def git(*args):
        if args[0] == "rev-parse":
            return args[1]
        if args[0] == "show":
            if args[1] == f"{r.SOURCE_COMMIT}:{r.SOURCE_PATH}":
                return json.dumps({"cases": manifest["cases"]})
            return json.dumps({} if change == "modified_raw" else package)
        return ""
    monkeypatch.setattr(r, "git", git)
    argv = ["runner", "judge", "--prereg-commit", "prereg"]
    if change != "missing_raw_commit":
        argv += ["--raw-commit", "rawfreeze"]
    monkeypatch.setattr(sys, "argv", argv)
    with pytest.raises(ValueError, match="raw-freeze commit required|raw outputs changed|all raw records required"):
        r.main()
