"""EA1 deterministic structural backing fixtures; no models or database required."""
from copy import deepcopy
import json
from types import SimpleNamespace
from contextlib import nullcontext
from pathlib import Path

import pytest

from panda_agent import qa
from panda_agent.models import Evidence, stable_id
from test_e2_a1_answer_point_coverage import agent, claim, review, QUESTION
from test_post_a5_o1_observability import RecordingVertex, assert_neutral, event
from test_e2_a1_answer_point_coverage import state as verification_state
from test_qa import code_evidence, CatalogConnection
from panda_agent.storage import Storage, _OBJECT_READ_COLUMNS
from panda_agent.retrieval_trace import build_retrieval_trace


SOURCE = "synthetic_sphinx"
VERSION = SOURCE + "@snapshot"
TEXT = "The input is a record. The output is a table."
BACKING_ID = stable_id("section", "ea_exact_backing", prefix="evidence")


def objects():
    locator = {"path": "page.html", "url": "https://example.invalid/page", "snapshot_date": "2000-01-01", "section_path": []}
    page = dict(object_id="page", object_type="sphinx_page", source_id=SOURCE, source_version_id=VERSION,
                text="Heading\n" + TEXT + "\nFooter", locator=locator, metadata={"snapshot_hash": "snapshot"},
                authority_level="operational")
    child = {**deepcopy(page), "object_id": "section", "object_type": "sphinx_section", "text": TEXT,
             "parent_object_id": "page", "metadata": {"snapshot_hash": "snapshot", "parent_object_id": "page"},
             "locator": {**locator, "url": locator["url"] + "#section", "section_path": ["Section"]},
             "ea_text_length": len(TEXT)}
    selected = Evidence(evidence_id="selected-page", object_id="page", source_id=SOURCE,
                        source_version_id=VERSION, text=page["text"], locator=locator,
                        retrieval_channels=["dense"], score=0.8, authority_level="operational").model_dump(mode="json")
    return page, child, selected


class FakeStorage:
    def __init__(self, pages, children):
        self.pages, self.children, self.calls = pages, children, []
        self.error = None

    def connect(self):
        return CatalogConnection([])

    def read_sphinx_backing(self, ids):
        self.calls.append(list(ids))
        if self.error:
            raise self.error
        return deepcopy({"pages": self.pages, "children": self.children})


def setup(tmp_path, vertex=None):
    page, child, selected = objects()
    directory = tmp_path / "data/manifests"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "source_manifest.json").write_text(json.dumps({"web_documents": [{
        "doc_id": SOURCE, "snapshot_hash": "snapshot", "captured_at": "2000-01-01T00:00:00Z",
        "records": [{"path": "page.html", "url": "https://example.invalid/page"}]}]}), encoding="utf-8")
    runner = agent(tmp_path, vertex)
    runner.retriever.bundle["evidence"] = [selected]
    runner.retriever.bundle["plan"]["required_source_types"] = []
    storage = FakeStorage([page], {"page": [child]})
    runner.retriever.storage = storage
    state = {"question": QUESTION, "bundle": runner.retriever.bundle, "_ea_cache": {}}
    return runner, state, storage


def test_unique_exact_backing_and_cache(tmp_path):
    runner, state, storage = setup(tmp_path)
    original = deepcopy(state["bundle"])
    admitted = runner._admitted_evidence(state)
    assert [x["evidence_id"] for x in admitted] == [BACKING_ID]
    assert admitted[0]["object_id"] == "section"
    assert admitted[0]["text"] == TEXT
    assert not qa._is_public_claim_citation_eligible(state["bundle"]["evidence"][0])
    assert runner._admitted_evidence(state) == admitted
    assert storage.calls == [["page"]]
    assert state["bundle"] == original


def decision(state):
    return state["_ea_cache"]["decisions"][0]


def child_evidence(child):
    return Evidence(**{k: child[k] for k in ("object_id", "source_id", "source_version_id", "text", "locator", "authority_level")},
                    evidence_id="existing-child", retrieval_channels=["dense"], score=0.7).model_dump(mode="json")


def test_direct_and_existing_child_order(tmp_path):
    runner, state, storage = setup(tmp_path)
    child = child_evidence(storage.children["page"][0])
    other = code_evidence()
    state["bundle"]["evidence"] += [other, child]
    original = deepcopy(state["bundle"])
    assert runner._admitted_evidence(state) == [other, child]
    assert state["_ea_cache"]["backings"] == []
    assert decision(state)["backing_evidence_id"] == "existing-child"
    assert state["bundle"] == original
    state["_ea_cache"] = {}
    state["bundle"]["evidence"] = [child, other]
    storage.calls.clear()
    assert runner._admitted_evidence(state) == [child, other]
    assert storage.calls == []


@pytest.mark.parametrize("count,reason", [(0, "NO_VALID_BACKING"), (2, "AMBIGUOUS_BACKING"), (17, "BOUND_EXCEEDED")])
def test_no_tiebreak_or_first_n(tmp_path, count, reason):
    runner, state, storage = setup(tmp_path)
    child = storage.children["page"][0]
    storage.children["page"] = [{**deepcopy(child), "object_id": f"child-{i}"} for i in range(count)]
    assert runner._admitted_evidence(state) == []
    assert decision(state)["reason_code"] == reason


@pytest.mark.parametrize("field,value,reason", [
    ("source_id", "other", "VERSION_MISMATCH"),
    ("source_version_id", "other", "VERSION_MISMATCH"),
    ("metadata.snapshot_hash", "other", "VERSION_MISMATCH"),
    ("locator.snapshot_date", "other", "VERSION_MISMATCH"),
    ("parent_object_id", "other", "CONTENT_RELATION_NOT_ESTABLISHED"),
    ("metadata.parent_object_id", "other", "CONTENT_RELATION_NOT_ESTABLISHED"),
    ("object_type", "chunk", "CONTENT_RELATION_NOT_ESTABLISHED"),
    ("locator.path", "other.html", "INVALID_LOCATOR"),
    ("locator.url", "https://example.invalid/other", "INVALID_LOCATOR"),
    ("locator.url", None, "INVALID_LOCATOR"),
    ("locator.section_path", [], "INVALID_LOCATOR"),
    ("text", "the input is a record.", "CONTENT_RELATION_NOT_ESTABLISHED"),
    ("text", "The input  is a record.", "CONTENT_RELATION_NOT_ESTABLISHED"),
    ("text", "", "CONTENT_RELATION_NOT_ESTABLISHED"),
    ("text", "x" * 12001, "BOUND_EXCEEDED"),
    ("ea_text_length", 12001, "BOUND_EXCEEDED"),
])
def test_child_rejection(tmp_path, field, value, reason):
    runner, state, storage = setup(tmp_path)
    target = storage.children["page"][0]
    keys = field.split(".")
    if len(keys) == 2:
        target = target[keys[0]]
    target[keys[-1]] = value
    assert runner._admitted_evidence(state) == []
    assert decision(state)["reason_code"] == "NO_VALID_BACKING"
    assert decision(state)["candidate_rejections"][0]["reason_code"] == reason


@pytest.mark.parametrize("field,value,reason", [
    ("text", "other", "CONTENT_RELATION_NOT_ESTABLISHED"),
    ("source_id", "other", "VERSION_MISMATCH"),
    ("source_version_id", "other", "VERSION_MISMATCH"),
    ("metadata.snapshot_hash", "other", "VERSION_MISMATCH"),
    ("locator.snapshot_date", "other", "VERSION_MISMATCH"),
    ("locator.path", "other", "CONTENT_RELATION_NOT_ESTABLISHED"),
    ("locator.url", "other", "CONTENT_RELATION_NOT_ESTABLISHED"),
    ("object_type", "chunk", "NO_VALID_BACKING"),
])
def test_page_identity(tmp_path, field, value, reason):
    runner, state, storage = setup(tmp_path)
    target = storage.pages[0]
    keys = field.split(".")
    if len(keys) == 2:
        target = target[keys[0]]
    target[keys[-1]] = value
    assert runner._admitted_evidence(state) == []
    assert decision(state)["reason_code"] == reason


@pytest.mark.parametrize("page_text,child_text,ok", [(TEXT + TEXT, TEXT, False), ("aaa", "aa", False),
                                                     ("X" + "a" * 12000 + "Y", "a" * 12000, True)])
def test_occurrence_and_text_limit(tmp_path, page_text, child_text, ok):
    runner, state, storage = setup(tmp_path)
    storage.pages[0]["text"] = state["bundle"]["evidence"][0]["text"] = page_text
    storage.children["page"][0].update(text=child_text, ea_text_length=len(child_text))
    assert bool(runner._admitted_evidence(state)) == ok


def test_candidate_bound_before_lookup(tmp_path):
    runner, state, storage = setup(tmp_path)
    parent = state["bundle"]["evidence"][0]
    state["bundle"]["evidence"] = [{**parent, "evidence_id": f"e{i}", "object_id": f"p{i}"} for i in range(5)]
    assert runner._admitted_evidence(state) == []
    assert storage.calls == []
    assert {d["reason_code"] for d in state["_ea_cache"]["decisions"]} == {"BOUND_EXCEEDED"}


@pytest.mark.parametrize("failure", ["database", "timeout", "missing_manifest", "malformed_manifest"])
def test_failure_cached_and_qa_continues(tmp_path, failure):
    vertex = RecordingVertex(answers=[], reviews=[review({}, missing=["point.1", "point.2"])] * 2)
    runner, state, storage = setup(tmp_path, vertex)
    manifest = tmp_path / "data/manifests/source_manifest.json"
    if failure == "missing_manifest":
        manifest.unlink()
    elif failure == "malformed_manifest":
        manifest.write_text("{", encoding="utf-8")
    else:
        storage.error = TimeoutError("statement timeout") if failure == "timeout" else RuntimeError("DB unavailable")
    assert runner._admitted_evidence(state) == []
    assert runner._admitted_evidence(state) == []
    assert decision(state)["reason_code"] == "LOOKUP_FAILED"
    assert len(storage.calls) == (0 if "manifest" in failure else 1)
    storage.calls.clear()
    out = runner._run_detailed(QUESTION, mode=qa.DEFAULT_ANSWER_POINT_MODE, capture_stage_trace=True)
    assert out["result"]["claims"] == []
    assert len(storage.calls) <= 1
    tasks = [json.loads(c[0])["task"] for c in vertex.exact_calls]
    assert tasks.count("create_atomic_evidence_bound_claims") == 1
    assert tasks.count("revise_unsupported_claims_once") <= 1


def test_full_graph_revision_cache_trace_and_public_backing(tmp_path, monkeypatch):
    reads = []
    original_read = Path.read_text
    def read(path, *args, **kwargs):
        if path == tmp_path / "data/manifests/source_manifest.json":
            reads.append(path)
        return original_read(path, *args, **kwargs)
    monkeypatch.setattr(Path, "read_text", read)
    runs = []
    for capture in (False, True):
        vertex = RecordingVertex(answers=[claim(evidence=BACKING_ID)],
            revisions=[claim("c2", "point.2", "The output is a table.", BACKING_ID)],
            reviews=[review({"c1": ["point.1"]}, missing=["point.2"]),
                     review({"c1": ["point.1"], "c2": ["point.2"]})])
        runner, state, storage = setup(tmp_path, vertex)
        before = deepcopy(state["bundle"])
        out = runner._run_detailed(QUESTION, mode=qa.DEFAULT_ANSWER_POINT_MODE, capture_stage_trace=capture)
        assert state["bundle"] == before
        assert storage.calls == [["page"]]
        assert runner.retriever.calls == 1
        assert out["model_usage"]["embedding_calls"] == 0
        assert out["diagnostics"]["revision_count"] == 1
        assert [e["object_id"] for e in out["result"]["evidence"]] == ["section"]
        assert len(out["result"]["claims"]) == 2
        trace_args = dict(question_id="synthetic", run_id="fixture", question=QUESTION,
                          manifest={}, object_lookup={}, result=out["result"])
        trace = build_retrieval_trace(diagnostics=out["diagnostics"], **trace_args)
        prior = {**before, "selected_evidence": before["evidence"]}
        assert trace == build_retrieval_trace(diagnostics=prior, **trace_args)
        assert [e["object_id"] for e in trace.final_evidence] == ["page"]
        payloads = [json.loads(c[0]) for c in vertex.exact_calls]
        a0 = next(p for p in payloads if p["task"] == "create_atomic_evidence_bound_claims")
        a1 = next(p for p in payloads if p["task"] == "revise_unsupported_claims_once")
        assert a0["untrusted_evidence"] == a1["untrusted_evidence"]
        assert [e["evidence_id"] for e in a0["untrusted_evidence"]] == [BACKING_ID]
        for p in payloads:
            if p["task"] == "review_claim_support_and_relevance":
                assert {e["evidence_id"] for e in p["untrusted_evidence"]} == {"selected-page", BACKING_ID}
        assert len(vertex.exact_calls) == 6
        runs.append((out, vertex.exact_calls, runner.retriever.calls))
    assert len(reads) == 2
    assert_neutral(*runs)
    resolved = event(runs[1][0], "EA_ADMISSION")["payload"]["decisions"][0]
    assert resolved["reason_code"] == "RESOLVED_EXACT_BACKING"
    assert resolved["containment_offsets"] == [8, 8 + len(TEXT)]
    assert resolved["parent_object_id"] == "page" and resolved["backing_object_id"] == "section"


@pytest.mark.parametrize("kind", ["parent", "unknown", "unsupported", "version"])
def test_normal_verification_still_rejects(tmp_path, kind):
    vertex = RecordingVertex(reviews=[review({"c1": ["point.1"]}, missing=["point.2"],
                                             unsupported=["c1"] if kind == "unsupported" else [])])
    runner, state, storage = setup(tmp_path, vertex)
    runner._admitted_evidence(state)
    eid = {"parent": "selected-page", "unknown": "unknown"}.get(kind, BACKING_ID)
    check = verification_state(runner, [claim(evidence=eid)])
    check["_ea_cache"] = state["_ea_cache"]
    if kind == "version":
        wrong = code_evidence()
        wrong["source_version_id"] = "pandaroot@wrong"
        check["bundle"]["evidence"].append(wrong)
        check["draft"]["claims"][0]["evidence_ids"] = [wrong["evidence_id"]]
    result = runner._verify(check)
    assert result["supported_claims"] == []
    if kind != "unsupported":
        assert vertex.calls[0][0]["untrusted_claims"] == []


def test_e3_retained_contract_unchanged(tmp_path):
    runner, state, storage = setup(tmp_path)
    state["answer_point_coverage_mode"] = "runtime_e1_v2"
    assert runner._admitted_evidence(state) == []
    assert storage.calls == []


@pytest.mark.parametrize("change,reason", [("snapshot_hash", "VERSION_MISMATCH"),
    ("captured_at", "VERSION_MISMATCH"), ("doc_id", "VERSION_MISMATCH"),
    ("records", "CONTENT_RELATION_NOT_ESTABLISHED")])
def test_manifest_authority(tmp_path, change, reason):
    runner, state, storage = setup(tmp_path)
    path = tmp_path / "data/manifests/source_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["web_documents"][0][change] = [] if change == "records" else "other"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    assert runner._admitted_evidence(state) == []
    assert decision(state)["reason_code"] == reason


def test_four_pages_and_insertion_order(tmp_path):
    runner, state, storage = setup(tmp_path)
    parent, child = storage.pages[0], storage.children["page"][0]
    selected = state["bundle"]["evidence"][0]
    storage.pages, storage.children = [], {}
    evidence = [code_evidence(evidence_id="before")]
    for i in range(4):
        pid = f"page-{i}"
        storage.pages.append({**deepcopy(parent), "object_id": pid})
        storage.children[pid] = [{**deepcopy(child), "object_id": f"child-{i}", "parent_object_id": pid,
                                  "metadata": {"snapshot_hash": "snapshot", "parent_object_id": pid}}]
        evidence.append({**deepcopy(selected), "object_id": pid, "evidence_id": f"selected-{i}"})
    evidence.append(code_evidence(evidence_id="after"))
    state["bundle"].update(evidence=evidence, rankings={"dense": [e["object_id"] for e in evidence]},
                           fusion_scores={e["object_id"]: 1.0 for e in evidence},
                           ranked_object_ids=[e["object_id"] for e in evidence], reranked_object_ids=[])
    before = deepcopy(state["bundle"])
    admitted = runner._admitted_evidence(state)
    assert [e["object_id"] for e in admitted] == ["o-before", *[f"child-{i}" for i in range(4)], "o-after"]
    assert len(state["_ea_cache"]["backings"]) == 4
    assert state["bundle"] == before
    assert len(storage.calls) == 1


@pytest.mark.parametrize("field,value,reason", [("object_id", None, "CONTENT_RELATION_NOT_ESTABLISHED"),
                                               ("url", None, "INVALID_LOCATOR"),
                                               ("snapshot_date", None, "INVALID_LOCATOR")])
def test_ineligible_input_does_not_lookup(tmp_path, field, value, reason):
    runner, state, storage = setup(tmp_path)
    selected = state["bundle"]["evidence"][0]
    (selected if field == "object_id" else selected["locator"])[field] = value
    assert runner._admitted_evidence(state) == []
    assert decision(state)["reason_code"] == reason
    assert storage.calls == []


def test_storage_bounded_read_contract():
    page, child, _ = objects()
    columns = _OBJECT_READ_COLUMNS.split(",")
    queries = []
    class Connection:
        def transaction(self):
            return nullcontext()
        def execute(self, sql, params=None):
            queries.append((sql, params))
            obj = child if "CROSS JOIN LATERAL" in sql else page
            row = tuple(obj.get(k) for k in columns)
            return SimpleNamespace(fetchall=lambda: [row + ((len(TEXT),) if obj is child else ())])
    storage = object.__new__(Storage)
    storage.connect = lambda: nullcontext(Connection())
    result = storage.read_sphinx_backing(["page"])
    assert len(queries) == 4
    assert queries[0][0] == "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY"
    assert queries[1][0] == "SET LOCAL statement_timeout = '1000ms'"
    assert "WHERE object_id=ANY(%s) ORDER BY object_id LIMIT 4" in queries[2][0]
    assert queries[2][1] == (["page"],)
    sql, params = queries[3]
    for fragment in ("c.source_id=p.source_id", "c.source_version_id=p.source_version_id",
                     "c.object_type='sphinx_section'", "c.metadata->>'parent_object_id'=p.object_id",
                     "ORDER BY c.object_id LIMIT 17", "left(c.text,12000)", "char_length(c.text)"):
        assert fragment in sql
    assert params == (["page"], [SOURCE], [VERSION])
    assert result["children"]["page"][0]["parent_object_id"] == "page"
    for ids in ([], [str(i) for i in range(5)]):
        with pytest.raises(ValueError):
            storage.read_sphinx_backing(ids)
    assert len(queries) == 4
