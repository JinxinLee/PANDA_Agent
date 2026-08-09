"""Deterministic benchmark-v2 migration and audit utilities.

The legacy 120 questions have been exposed during development review.  They can
therefore seed development, challenge, and regression partitions, but never a
new release acceptance set.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml

from panda_agent.evaluation import (
    GoldDataset,
    GoldQuestion,
    apply_signed_rescore_adjudication,
    load_gold_dataset,
    validate_v25_adjudication_document,
)


_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "do", "does", "for",
    "from", "how", "i", "in", "into", "is", "it", "of", "on", "or", "the",
    "to", "what", "where", "which", "with", "如何", "什么", "哪里", "怎么",
}


_FORMAL_RESCORE_REVISIONS = frozenset({"2.1", "2.2", "2.3", "2.4", "2.5", "2.6"})


def _formal_rescore_identity(benchmark_version: str) -> dict[str, str]:
    """Return the formal rescore identity for a supported reviewed benchmark.

    The benchmark revision is the authority for every identity field emitted
    by a formal rescore.  Keep the accepted revisions explicit so a newly
    reviewed dataset cannot be labelled as a previous evaluator by accident.
    """
    match = re.fullmatch(r"m6-benchmark-v(?P<revision>\d+\.\d+)", benchmark_version)
    revision = match.group("revision") if match else None
    if revision not in _FORMAL_RESCORE_REVISIONS:
        raise ValueError(
            "unsupported reviewed benchmark version for formal rescore: "
            f"{benchmark_version!r}"
        )
    # Policy-only revisions fix artifact semantics without changing reviewed
    # Gold. Keep them in the identity so corrected composites cannot collide
    # with earlier artifacts for the same benchmark.
    policy_revision = {
        "2.5": "2.5.1",
        "2.6": "2.6.1",
    }.get(revision, revision)
    revision_tag = policy_revision.replace(".", "_")
    return {
        "artifact_evaluator": f"evaluator-{revision_tag}",
        "schema_version": policy_revision,
        "evaluation_revision": f"evaluator-{policy_revision}",
        "selector_policy": (
            "direct>ancestor>path_descendant_containment>"
            f"explicit_v{revision_tag}_any_of"
        ),
    }


def _rescore_identity_sha256(identity_inputs: dict[str, Any]) -> str:
    """Hash the complete immutable-input identity of a formal rescore."""
    return hashlib.sha256(
        json.dumps(identity_inputs, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assert_v2_draft_target_writable(dataset_path: Path) -> None:
    """Prevent draft regeneration from overwriting a reviewed benchmark.

    ``build-v2`` is a migration helper, not an update mechanism for signed
    annotations.  Once any question has been approved (or the benchmark no
    longer identifies itself as the generated draft), replacement must happen
    through an explicitly reviewed import instead.
    """
    if not dataset_path.exists():
        return
    existing = load_gold_dataset(dataset_path)
    approved = [item.id for item in existing.questions if item.review_status == "approved"]
    if existing.benchmark_version != "m6-benchmark-v2-draft" or approved:
        raise ValueError(
            "refusing to overwrite reviewed benchmark v2 with build-v2; "
            f"benchmark_version={existing.benchmark_version!r}, approved={len(approved)}"
        )


def _query_tokens(text: str) -> set[str]:
    values = re.findall(r"[A-Za-z_][A-Za-z0-9_:.-]*|[\u4e00-\u9fff]{2,}", text.casefold())
    return {value for value in values if value not in _STOPWORDS and len(value) > 1}


def _selector_key(selector: Any) -> str | None:
    if selector.object_id:
        return f"object:{selector.object_id}"
    if selector.path and selector.path.lower() != "readme.md":
        return f"path:{selector.source_id}:{selector.path}:{selector.symbol or ''}"
    if selector.pdf_page:
        return f"paper:{selector.source_id}:{selector.pdf_page}"
    if selector.title_contains and "installation" not in selector.title_contains.casefold():
        return f"title:{selector.source_id}:{selector.title_contains.casefold()}"
    return None


def _features(question: GoldQuestion) -> dict[str, set[str]]:
    evidence = {
        key
        for group in question.required_evidence_groups
        for selector in group.any_of
        if (key := _selector_key(selector))
    }
    identifiers = {item.text.casefold().rstrip("*&") for item in question.required_identifiers}
    return {"tokens": _query_tokens(question.query), "evidence": evidence, "identifiers": identifiers}


def _jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 0.0


def cluster_questions(dataset: GoldDataset) -> tuple[dict[str, str], list[dict[str, Any]]]:
    questions = sorted(dataset.questions, key=lambda item: item.id)
    parent = {item.id: item.id for item in questions}
    feature_map = {item.id: _features(item) for item in questions}

    def find(value: str) -> str:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    def union(left: str, right: str) -> None:
        a, b = find(left), find(right)
        if a != b:
            parent[max(a, b)] = min(a, b)

    similarities: list[dict[str, Any]] = []
    for index, left in enumerate(questions):
        for right in questions[index + 1 :]:
            lf, rf = feature_map[left.id], feature_map[right.id]
            token_score = _jaccard(lf["tokens"], rf["tokens"])
            evidence_score = _jaccard(lf["evidence"], rf["evidence"])
            identifier_overlap = sorted(lf["identifiers"] & rf["identifiers"])
            linked = (
                token_score >= 0.62
                or evidence_score >= 0.80
                or (bool(identifier_overlap) and token_score >= 0.15)
                or (evidence_score >= 0.34 and token_score >= 0.18)
            )
            if linked:
                union(left.id, right.id)
            if left.split != right.split and max(token_score, evidence_score) >= 0.30:
                similarities.append(
                    {
                        "left": left.id,
                        "right": right.id,
                        "left_split": left.split,
                        "right_split": right.split,
                        "query_jaccard": round(token_score, 4),
                        "evidence_jaccard": round(evidence_score, 4),
                        "shared_identifiers": identifier_overlap,
                        "cluster_linked": linked,
                    }
                )
    members: dict[str, list[str]] = defaultdict(list)
    for question in questions:
        members[find(question.id)].append(question.id)
    cluster_ids = {
        case_id: f"cluster-{min(values)}"
        for values in members.values()
        for case_id in values
    }
    return cluster_ids, sorted(
        similarities,
        key=lambda item: max(item["query_jaccard"], item["evidence_jaccard"]),
        reverse=True,
    )


def _cluster_stats(dataset: GoldDataset, cluster_ids: dict[str, str]) -> list[dict[str, Any]]:
    by_cluster: dict[str, list[GoldQuestion]] = defaultdict(list)
    for question in dataset.questions:
        by_cluster[cluster_ids[question.id]].append(question)
    values = []
    for cluster_id, questions in sorted(by_cluster.items()):
        statuses = Counter(item.expected_status.value for item in questions)
        values.append(
            {
                "cluster_id": cluster_id,
                "case_ids": sorted(item.id for item in questions),
                "size": len(questions),
                "answered": statuses.get("answered", 0),
                "insufficient_evidence": statuses.get("insufficient_evidence", 0),
                "version_conflict": statuses.get("version_conflict", 0),
            }
        )
    return values


def _select_clusters(
    clusters: list[dict[str, Any]], target: tuple[int, int, int]
) -> set[str] | None:
    """Select whole clusters for (total, insufficient, version_conflict)."""
    states: dict[tuple[int, int, int], tuple[str, ...]] = {(0, 0, 0): ()}
    for cluster in clusters:
        delta = (
            cluster["size"],
            cluster["insufficient_evidence"],
            cluster["version_conflict"],
        )
        updated = dict(states)
        for state, selected in states.items():
            candidate = tuple(state[index] + delta[index] for index in range(3))
            if all(candidate[index] <= target[index] for index in range(3)):
                updated.setdefault(candidate, (*selected, cluster["cluster_id"]))
        states = updated
    selected = states.get(target)
    return set(selected) if selected is not None else None


def partition_clusters(
    dataset: GoldDataset, cluster_ids: dict[str, str]
) -> tuple[dict[str, str], dict[str, Any]]:
    clusters = _cluster_stats(dataset, cluster_ids)
    dev_selection = None
    dev_target = None
    for target in ((80, 7, 7), (80, 8, 6), (80, 6, 8)):
        dev_selection = _select_clusters(clusters, target)
        if dev_selection is not None:
            dev_target = target
            break
    if dev_selection is None:
        raise ValueError("cannot create an 80-case cluster-disjoint dev partition")
    remaining = [item for item in clusters if item["cluster_id"] not in dev_selection]
    challenge_selection = _select_clusters(
        remaining,
        (
            24,
            sum(item["insufficient_evidence"] for item in remaining),
            sum(item["version_conflict"] for item in remaining),
        ),
    )
    if challenge_selection is None:
        # Status composition is secondary for the exposed challenge set.  Find
        # any whole-cluster subset of exactly 24 cases.
        states: dict[int, tuple[str, ...]] = {0: ()}
        for cluster in remaining:
            updated = dict(states)
            for count, selected in states.items():
                candidate = count + cluster["size"]
                if candidate <= 24:
                    updated.setdefault(candidate, (*selected, cluster["cluster_id"]))
            states = updated
        challenge_selection = set(states.get(24, ()))
    if sum(item["size"] for item in remaining if item["cluster_id"] in challenge_selection) != 24:
        raise ValueError("cannot create a 24-case cluster-disjoint challenge partition")
    assignment: dict[str, str] = {}
    for question in dataset.questions:
        cluster_id = cluster_ids[question.id]
        assignment[question.id] = (
            "dev"
            if cluster_id in dev_selection
            else "challenge"
            if cluster_id in challenge_selection
            else "regression"
        )
    return assignment, {
        "dev_target": dev_target,
        "dev_clusters": sorted(dev_selection),
        "challenge_clusters": sorted(challenge_selection),
    }


def _set_points(question: dict[str, Any], points: list[str]) -> None:
    question["required_answer_points"] = [
        {"point_id": f"p{index}", "text": text, "weight": 1.0, "critical": True}
        for index, text in enumerate(points, 1)
    ]


def _reviewed_annotation_fixes(question: dict[str, Any]) -> None:
    case_id = question["id"]
    groups = question["required_evidence_groups"]
    if case_id == "g001":
        selectors = [selector for group in groups for selector in group["any_of"]]
        question["required_evidence_groups"] = [
            {
                "group_id": "g001.installation",
                "role": "locked_developer_installation",
                "critical": True,
                "any_of": selectors,
            }
        ]
    if case_id in {"g018", "g019", "g113"}:
        question["required_evidence_groups"] = [
            group
            for group in groups
            if not any((item.get("path") or "").casefold() == "readme.md" for item in group["any_of"])
        ]
        question["required_source_types"] = ["code"]
    if case_id == "g027":
        question["query"] = (
            "Where is PndTargetGenerator defined in the locked PandaRoot snapshot "
            "and the RestgasDetermination fork, and why does version scope matter?"
        )
        question["required_evidence_groups"] = [
            {
                "group_id": "g027.pandaroot",
                "role": "upstream_snapshot_definition",
                "critical": True,
                "any_of": [
                    {"source_id": "pandaroot", "path": "pgenerators/Target/PndTargetGenerator.h"},
                    {"source_id": "pandaroot", "path": "pgenerators/Target/PndTargetGenerator.cxx"},
                ],
            },
            {
                "group_id": "g027.restgas_fork",
                "role": "fork_definition",
                "critical": True,
                "any_of": [
                    {"source_id": "restgas_determination", "path": "pgenerators/Target/PndTargetGenerator.h"},
                    {"source_id": "restgas_determination", "path": "pgenerators/Target/PndTargetGenerator.cxx"},
                ],
            },
        ]
        _set_points(
            question,
            [
                "Give the PndTargetGenerator path in the locked PandaRoot snapshot.",
                "Give the corresponding path in the locked RestgasDetermination fork.",
                "Explain that behavior must be resolved against the requested source version.",
            ],
        )
    if case_id == "g013":
        question["query"] = (
            "How do I set up the terminal and run a ROOT simulation macro in "
            "PandaRoot, and how does the master run task participate in the lifecycle?"
        )
        groups[0]["any_of"] = [
            {
                "source_id": "pandaroot_sphinx_2023_08_25_dev",
                "path": (
                    "pandaroot_sphinx_2023_08_25_dev/raw/~pandacc/documentation/"
                    "2023-08-25-dev/sphinx/Running/Macros.html"
                ),
            }
        ]
        groups[1]["any_of"] = [
            {"source_id": "pandaroot", "path": "tools/MasterTasks/PndMasterRunSim.h"},
            {"source_id": "pandaroot", "path": "tools/MasterTasks/PndMasterRunSim.cxx"},
        ]
        _set_points(
            question,
            [
                "Explain how to initialize the PandaRoot environment before running a macro.",
                "Give the documented ROOT macro invocation pattern.",
                "Explain how a master run task is configured and orchestrates the simulation event loop.",
            ],
        )
    if case_id == "g085":
        groups[0]["role"] = "profile_feedback_theory"
        groups[0]["any_of"] = [
            {"source_id": "li_2026", "pdf_page": 141, "pdf_page_end": 152}
        ]
    if case_id == "g087":
        groups[0]["role"] = "pandaroot_data_product_definition"
        groups[0]["critical"] = False
        groups[0]["any_of"].append(
            {"source_id": "pandaroot", "path": "detectors/lmd/LmdQA/PndLmdTrackQ.h"}
        )
        groups[1]["role"] = "adapter_read_boundary"
    if case_id == "g089":
        groups[2]["role"] = "target_generator_interface_or_sampling"
        groups[2]["any_of"].append(
            {"source_id": "pandaroot", "path": "pgenerators/Target/PndTargetGenerator.h"}
        )
    if case_id == "g098":
        question["required_source_types"] = ["code"]
        _set_points(
            question,
            [
                "Explain that PandaRoot produces the LMD QA ROOT data product.",
                "Explain that PndLmdCombinedDataReader is the PandaRoot-to-LuminosityFit adapter.",
                "Explain that PndLmdModelFactory builds the independent fit-model layer and does not perform PandaRoot event production.",
            ],
        )
    if case_id == "g112":
        question["query"] = (
            "createLmdFitData returns no acceptance: which data mode, Lumi_TrksQA "
            "input/tree assumptions, selection filters, and accepted/generated "
            "histogram filling should I inspect?"
        )
        # The executable and reader implementations are the authoritative
        # evidence for these debugging checks.  Documentation is useful
        # retrieval context but must not be a mandatory final citation.
        question["required_evidence_groups"] = groups[1:]
        question["required_source_types"] = ["code"]
        _set_points(
            question,
            [
                "Verify the requested createLmdFitData data mode.",
                "Verify the input Lumi_TrksQA files and expected ROOT tree or branch assumptions.",
                "Verify selection and filtering conditions.",
                "Verify accepted and generated histogram filling in PndLmdDataReader.",
            ],
        )
    for group in question["required_evidence_groups"]:
        if not group.get("role"):
            group["role"] = group["group_id"]
        group.setdefault("critical", True)


def build_v2_draft(project_root: Path) -> dict[str, Any]:
    v2_dir = project_root / "evaluation" / "benchmarks" / "v2"
    dataset_path = v2_dir / "gold_questions.yaml"
    assert_v2_draft_target_writable(dataset_path)
    source_path = project_root / "evaluation" / "gold_questions.yaml"
    source = load_gold_dataset(source_path)
    cluster_ids, similarities = cluster_questions(source)
    assignment, partition_report = partition_clusters(source, cluster_ids)
    questions = []
    for item in source.questions:
        value = item.model_dump(mode="json")
        value["split"] = assignment[item.id]
        value["cluster_id"] = cluster_ids[item.id]
        value["challenge_tags"] = list(
            dict.fromkeys(
                [
                    *value.get("challenge_tags", []),
                    *( ["negative_control"] if value["expected_status"] == "insufficient_evidence" else [] ),
                    *( ["version_conflict"] if value["expected_status"] == "version_conflict" else [] ),
                ]
            )
        )
        value["review_status"] = "draft"
        value["reviewer"] = None
        value["reviewed_at"] = None
        _reviewed_annotation_fixes(value)
        questions.append(value)
    split_counts = dict(Counter(item["split"] for item in questions))
    status_counts = dict(Counter(item["expected_status"] for item in questions))
    output = {
        "schema_version": "2.0",
        "benchmark_version": "m6-benchmark-v2-draft",
        "release_eligible": False,
        "acceptance_exposed": True,
        "expected_split_counts": split_counts,
        "expected_status_counts": status_counts,
        "questions": questions,
    }
    # Validate the generated artifact before writing it.
    GoldDataset.model_validate(output)
    v1_dir = project_root / "evaluation" / "benchmarks" / "v1"
    v1_dir.mkdir(parents=True, exist_ok=True)
    v2_dir.mkdir(parents=True, exist_ok=True)
    archived = v1_dir / "gold_questions.yaml"
    if not archived.exists():
        archived.write_bytes(source_path.read_bytes())
    (v1_dir / "benchmark_manifest.json").write_text(
        json.dumps(
            {
                "dataset_sha256": _sha256(source_path),
                "status": "retired_for_release",
                "reason": "All 120 questions, including the former acceptance split, were exposed during development review.",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    dataset_path.write_text(
        yaml.safe_dump(output, allow_unicode=True, sort_keys=False, width=120),
        encoding="utf-8",
    )
    acceptance_policy = {
        "schema_version": "1.0",
        "status": "not_created",
        "ownership": "independent_domain_reviewer",
        "question_count": 64,
        "intent_distribution": {intent: 8 for intent in sorted({item.intent for item in source.questions})},
        "status_distribution": {"answered": 52, "insufficient_evidence": 6, "version_conflict": 6},
        "rules": [
            "Must be cluster-disjoint from all exposed development, challenge, and regression questions.",
            "Must not be inspected or used for tuning before the release candidate is frozen.",
            "A consumed acceptance set cannot be reused after acceptance-driven implementation changes.",
        ],
    }
    (v2_dir / "acceptance_policy.yaml").write_text(
        yaml.safe_dump(acceptance_policy, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    manual_overrides = {
        "schema_version": "1.0",
        "source_run_id": "m6-qa-dev-candidate-v8",
        "review_decision_sha256": _sha256(
            project_root
            / "data"
            / "evaluation"
            / "runs"
            / "m6-qa-dev-candidate-v8"
            / "failure_review_decisions.yaml"
        ),
        "overrides": {
            "g001": {"final_evidence_recall": 1.0, "unsupported_claim_ids": []},
            "g003": {"unsupported_claim_ids": []},
            "g007": {"final_evidence_recall": None},
            "g013": {
                "answer_point_coverage": 2 / 3,
                "covered_point_ids": ["p1", "p2"],
                "critical_answer_points_missing": ["p3"],
                "unsupported_claim_ids": [],
            },
            "g016": {"unsupported_claim_ids": []},
            "g018": {"gold_recall_at_10": 1.0, "final_evidence_recall": 1.0},
            "g019": {"gold_recall_at_10": 1.0, "final_evidence_recall": 1.0},
            "g021": {"unsupported_claim_ids": []},
            "g027": {
                "answer_point_coverage": 1 / 3,
                "covered_point_ids": ["p1"],
                "critical_answer_points_missing": ["p2", "p3"],
            },
            "g079": {"hallucinated_identifiers": [], "major_identifier_hallucinations": []},
            "g085": {"final_evidence_recall": 1.0},
            "g087": {
                "gold_recall_at_10": 1.0,
                "final_evidence_recall": 1.0,
                "hallucinated_identifiers": [],
                "major_identifier_hallucinations": [],
            },
            "g089": {"gold_recall_at_10": 1.0, "final_evidence_recall": 1.0},
            "g098": {
                "answer_point_coverage": 2 / 3,
                "covered_point_ids": ["p1", "p2"],
                "critical_answer_points_missing": ["p3"],
            },
            "g101": {
                "answer_point_coverage": 1.0,
                "covered_point_ids": ["p1"],
                "critical_answer_points_missing": [],
            },
            "g112": {
                "answer_point_coverage": 0.0,
                "covered_point_ids": [],
                "critical_answer_points_missing": ["p1", "p2", "p3", "p4"],
            },
            "g113": {"gold_recall_at_10": 1.0, "final_evidence_recall": 1.0},
        },
        "policy": "Only human-reviewed metric corrections are applied; original records remain immutable.",
    }
    (v2_dir / "manual_rescore_overrides.yaml").write_text(
        yaml.safe_dump(manual_overrides, allow_unicode=True, sort_keys=False, width=120),
        encoding="utf-8",
    )
    audit = audit_dataset(project_root, dataset_path, similarities=similarities)
    audit["partition"] = partition_report
    (v2_dir / "audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    broad = [item for item in audit["broad_selectors"] if item["matches"] > 10]
    annotation_lines = [
        "# Benchmark v2 annotation review queue",
        "",
        "> This draft is not release-eligible. All 120 questions require human approval after schema and split changes.",
        "",
        f"- Questions: `{len(questions)}`",
        f"- Knowledge clusters: `{len(set(cluster_ids.values()))}`",
        f"- Broad selectors shown below: `{len(broad)}`",
        "- Karavdina selectors require page/section spot checks because that PDF used PyMuPDF fallback.",
        "",
        "## Broad selector queue",
        "",
        "| Case | Group | Role | Matches | Selector |",
        "|---|---|---|---:|---|",
    ]
    for item in broad:
        annotation_lines.append(
            f"| `{item['case_id']}` | `{item['group_id']}` | `{item['role']}` | "
            f"{item['matches']} | `{json.dumps(item['selector'], ensure_ascii=False)}` |"
        )
    annotation_lines.extend(
        [
            "",
            "## Full 120-question approval queue",
            "",
            "> Review the YAML for full selectors and answer-point text. Fill reviewer/status in the YAML; this table is a navigation checklist.",
            "",
            "| Case | Split | Cluster | Intent | Status | Query | Evidence roles | Points | Decision |",
            "|---|---|---|---|---|---|---|---:|---|",
        ]
    )
    for question in questions:
        query = str(question["query"]).replace("|", "\\|").replace("\n", " ")
        roles = ", ".join(
            str(group.get("role") or group["group_id"])
            for group in question["required_evidence_groups"]
        ).replace("|", "\\|")
        annotation_lines.append(
            f"| `{question['id']}` | `{question['split']}` | `{question['cluster_id']}` | "
            f"`{question['intent']}` | `{question['expected_status']}` | {query} | "
            f"{roles} | {len(question['required_answer_points'])} | pending |"
        )
    (v2_dir / "annotation_review.md").write_text(
        "\n".join(annotation_lines) + "\n", encoding="utf-8"
    )
    return {
        "dataset_path": str(dataset_path),
        "dataset_sha256": _sha256(dataset_path),
        "split_counts": split_counts,
        "status_counts": status_counts,
        "cluster_count": len(set(cluster_ids.values())),
        "cross_split_similarity_pairs": len(similarities),
        "official_ready": False,
        "acceptance_status": "not_created",
    }


def rescore_run(
    project_root: Path,
    run_id: str,
    dataset_path: Path,
    overrides_path: Path | None = None,
    *,
    review_decisions_path: Path | None = None,
    replacement_run_id: str | None = None,
    adjudications_path: Path | None = None,
    replacement_specs: list[tuple[str, list[str]] | dict[str, Any]] | None = None,
    include_case_ids: list[str] | None = None,
    exclude_case_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Uniformly rescore an immutable run without any model calls.

    The modern interface consumes the signed review-decision overlay and an
    optional replacement records.  New callers must declare the exact cases
    selected from every replacement run. ``replacement_run_id`` preserves the
    v2.1 status-fix compatibility path for g041/g119. ``include_case_ids`` and
    ``exclude_case_ids`` make a diagnostic subset explicit, so it cannot be
    mistaken for a complete development run.

    ``overrides_path`` remains accepted for archived v2 runs, but it is
    deliberately incompatible with the v2.1 review-decisions interface so an
    old override file cannot silently alter a newer diagnostic baseline.
    """
    from panda_agent.evaluation import (
        aggregate_metrics,
        deterministic_case_metrics,
        evaluate_development_gate,
        evaluate_regression_gate,
        load_run_records,
    )
    from panda_agent.evaluation_runner import (
        enforce_protected_rubric_metrics,
        load_object_lookup,
        result_content_hash,
        sha256_bytes,
    )

    dataset = load_gold_dataset(dataset_path)
    rescore_identity = _formal_rescore_identity(dataset.benchmark_version)
    questions = {item.id: item for item in dataset.questions}
    run_dir = project_root / "data" / "evaluation" / "runs" / run_id
    records = load_run_records(run_dir)
    object_lookup = load_object_lookup(project_root)
    if not records:
        raise ValueError(f"evaluation run has no records: {run_id}")
    source_manifest_path = run_dir / "manifest.json"
    source_manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    source_manifest_hash = _sha256(source_manifest_path)
    source_results_path = run_dir / "results.jsonl"
    source_results_hash = _sha256(source_results_path)
    if review_decisions_path and overrides_path:
        raise ValueError("use either --review-decisions or --overrides, not both")
    review_decisions_path = review_decisions_path.resolve() if review_decisions_path else None
    adjudications_path = (
        adjudications_path.resolve()
        if adjudications_path
        else dataset_path.parent / "manual_adjudications.yaml"
    )
    decisions: dict[str, dict[str, Any]] = {}
    review_decisions_hash: str | None = None
    review_imported_source_hash: str | None = None
    override_doc: dict[str, Any] = {}
    overrides_hash: str | None = None
    if review_decisions_path:
        review_doc = yaml.safe_load(review_decisions_path.read_text(encoding="utf-8")) or {}
        if review_doc.get("run_id") != run_id:
            raise ValueError("review decision overlay has the wrong source_run_id")
        review_decisions_hash = _sha256(review_decisions_path)
        review_imported_source_hash = review_doc.get("imported_source_sha256")
        for item in review_doc.get("decisions", []):
            decision = dict(item.get("human_review") or {})
            classification = decision.get("classification")
            action = decision.get("action")
            if classification not in {"metric_false_positive", "acceptable_exception"}:
                continue
            if action not in {"rescore", "fix", "waiver", "offline_rescore"}:
                continue
            decisions[str(item["case_id"])] = decision
    elif overrides_path:
        override_doc = yaml.safe_load(overrides_path.read_text(encoding="utf-8")) or {}
        if override_doc.get("source_run_id") != run_id:
            raise ValueError("manual rescore overrides have the wrong source_run_id")
        overrides_hash = _sha256(overrides_path)

    source_records_by_id = {str(item["id"]): item for item in records}
    if len(source_records_by_id) != len(records):
        raise ValueError(f"source run contains duplicate case records: {run_id}")
    source_case_ids = set(source_records_by_id)
    if include_case_ids and len(include_case_ids) != len(set(include_case_ids)):
        raise ValueError("include cases must be unique")
    if exclude_case_ids and len(exclude_case_ids) != len(set(exclude_case_ids)):
        raise ValueError("exclude cases must be unique")
    explicit_included = include_case_ids is not None
    included = set(include_case_ids or source_case_ids)
    excluded = set(exclude_case_ids or [])
    unknown_included = sorted(included - source_case_ids)
    unknown_excluded = sorted(excluded - source_case_ids)
    if unknown_included:
        raise ValueError(f"include cases are absent from source run: {unknown_included}")
    if unknown_excluded:
        raise ValueError(f"exclude cases are absent from source run: {unknown_excluded}")
    if explicit_included and included & excluded:
        raise ValueError(f"a case cannot be both included and excluded: {sorted(included & excluded)}")
    selected_case_ids = included - excluded
    if not selected_case_ids:
        raise ValueError("rescore subset is empty")

    # Compatibility contract: v2.1 callers which supplied only
    # ``replacement_run_id`` retain the historical g041/g119 replacement
    # behavior. New callers must provide explicit per-run case selections.
    if replacement_run_id and replacement_specs:
        raise ValueError("use either replacement_run_id or replacement_specs, not both")
    normalized_specs: list[tuple[str, list[str], bool]] = []
    if replacement_run_id:
        normalized_specs.append((replacement_run_id, ["g041", "g119"], True))
    for raw_spec in replacement_specs or []:
        if isinstance(raw_spec, dict):
            spec_run_id = str(raw_spec.get("run_id") or "")
            case_ids = [str(value) for value in raw_spec.get("case_ids", [])]
        else:
            spec_run_id, case_ids = raw_spec
            spec_run_id = str(spec_run_id)
            case_ids = [str(value) for value in case_ids]
        if not spec_run_id or not case_ids:
            raise ValueError("each replacement specification needs a run_id and non-empty explicit case_ids")
        normalized_specs.append((spec_run_id, case_ids, False))

    replacement_records: dict[str, dict[str, Any]] = {}
    replacement_sources: list[dict[str, Any]] = []
    all_replacement_case_ids: set[str] = set()
    strict_identity_keys = (
        "source_manifest_hash",
        "index_identity",
        "generation_model_id",
        "runtime_generation_model_id",
        "evaluation_judge_model_id",
        "embedding_model_id",
        "retrieval_policy_hash",
        "query_expansion_hash",
    )
    prompt_mismatches: list[dict[str, str | None]] = []
    for spec_run_id, requested_case_ids, is_legacy in normalized_specs:
        replacement_dir = project_root / "data" / "evaluation" / "runs" / spec_run_id
        replacement_manifest_path = replacement_dir / "manifest.json"
        replacement_manifest = json.loads(replacement_manifest_path.read_text(encoding="utf-8"))
        replacement_records_all = {
            str(item["id"]): item for item in load_run_records(replacement_dir)
        }
        if len(replacement_records_all) != len(load_run_records(replacement_dir)):
            raise ValueError(f"replacement run contains duplicate case records: {spec_run_id}")
        if len(set(requested_case_ids)) != len(requested_case_ids):
            raise ValueError(f"replacement specification repeats a case: {spec_run_id}")
        if is_legacy:
            allowed_sentinels = {"g031", "g112"}
            unknown = sorted(set(replacement_records_all) - set(requested_case_ids) - allowed_sentinels)
            if unknown:
                raise ValueError(f"replacement run contains unsupported cases: {unknown}")
        missing = sorted(set(requested_case_ids) - set(replacement_records_all))
        if missing:
            raise ValueError(f"replacement run is missing requested cases: {spec_run_id}: {missing}")
        missing_source = sorted(set(requested_case_ids) - source_case_ids)
        if missing_source:
            raise ValueError(f"replacement cases are absent from immutable source run: {missing_source}")
        outside_subset = sorted(set(requested_case_ids) - selected_case_ids)
        if outside_subset:
            raise ValueError(f"replacement cases are not in the selected subset: {outside_subset}")
        duplicate_cases = sorted(all_replacement_case_ids & set(requested_case_ids))
        if duplicate_cases:
            raise ValueError(f"a case may be replaced by only one run: {duplicate_cases}")
        for key in strict_identity_keys:
            if source_manifest.get(key) != replacement_manifest.get(key):
                raise ValueError(f"replacement manifest identity mismatch for {spec_run_id}: {key}")
        source_prompt = source_manifest.get("prompt_hash")
        replacement_prompt = replacement_manifest.get("prompt_hash")
        if source_prompt != replacement_prompt:
            prompt_mismatches.append(
                {
                    "replacement_run_id": spec_run_id,
                    "source_prompt_hash": source_prompt,
                    "replacement_prompt_hash": replacement_prompt,
                }
            )
        selected_replacements = {
            case_id: replacement_records_all[case_id]
            for case_id in sorted(set(requested_case_ids))
        }
        replacement_records.update(selected_replacements)
        all_replacement_case_ids.update(selected_replacements)
        replacement_sources.append(
            {
                "run_id": spec_run_id,
                "case_ids": sorted(selected_replacements),
                "manifest_sha256": _sha256(replacement_manifest_path),
                "all_records_sha256": sha256_bytes(
                    json.dumps(replacement_records_all, ensure_ascii=False, sort_keys=True).encode("utf-8")
                ),
                "selected_records_sha256": sha256_bytes(
                    json.dumps(selected_replacements, ensure_ascii=False, sort_keys=True).encode("utf-8")
                ),
                "prompt_hash": replacement_prompt,
                "prompt_matches_source": source_prompt == replacement_prompt,
                "legacy_compatibility_mode": is_legacy,
            }
        )

    adjudications: dict[str, dict[str, Any]] = {}
    adjudications_hash: str | None = None
    if adjudications_path and adjudications_path.is_file():
        adjudication_doc = yaml.safe_load(adjudications_path.read_text(encoding="utf-8")) or {}
        validate_v25_adjudication_document(dataset.benchmark_version, adjudication_doc)
        adjudications_hash = _sha256(adjudications_path)
        for item in adjudication_doc.get("adjudications", []):
            adjudications[str(item["case_id"])] = item

    overrides = (override_doc.get("overrides", {}) if overrides_path else {})
    rescored: list[dict[str, Any]] = []
    record_source_runs: dict[str, str] = {}
    replacement_run_by_case = {
        case_id: source["run_id"]
        for source in replacement_sources
        for case_id in source["case_ids"]
    }
    for record in records:
        case_id = str(record["id"])
        if case_id not in selected_case_ids:
            continue
        source_record = record
        replacement_used = False
        if case_id in replacement_records:
            source_record = replacement_records[case_id]
            replacement_used = True
        question = questions.get(case_id)
        if question is None:
            continue
        metrics = {
            **(source_record.get("metrics") or {}),
            **deterministic_case_metrics(
                question,
                source_record.get("result") or {},
                source_record.get("diagnostics") or {},
                object_lookup,
            ),
        }
        metrics = enforce_protected_rubric_metrics(
            question, source_record.get("result") or {}, metrics
        )
        applied = dict(overrides.get(case_id, {}))
        adjudication = adjudications.get(case_id)
        metrics.update(applied)
        if adjudication:
            metrics, human_fields = apply_signed_rescore_adjudication(
                dataset.benchmark_version, question, metrics, adjudication
            )
            applied.update({field: metrics[field] for field in human_fields})
        if "unsupported_claim_ids" in applied:
            metrics["major_unsupported_claim_ids"] = list(applied["unsupported_claim_ids"])
            metrics["minor_unsupported_claim_ids"] = []
        computed_fields = [
            "intent_correct",
            "expected_status_correct",
            "gold_recall_at_10",
            "final_evidence_recall",
            "critical_final_evidence_recall",
            "refusal_evidence_recall",
            "required_source_coverage",
            "wrong_version_evidence",
            "forbidden_evidence",
            "citation_integrity",
            "identifier_exists_in_locked_corpus",
            "identifier_supported_by_claim_evidence",
            "hallucinated_identifiers",
            "paper_code_dual_source",
            "metric_applicability",
            "metric_denominators",
        ]
        judge_fields = [
            "answer_point_coverage",
            "covered_point_ids",
            "critical_answer_points_missing",
            "contradictions",
            "unsupported_claim_ids",
            "major_unsupported_claim_ids",
            "minor_unsupported_claim_ids",
            "claim_verdicts",
        ]
        human_fields = sorted(applied)
        field_provenance = {
            field: (
                "human_adjudicated"
                if field in human_fields
                else "computed"
                if field in computed_fields
                else "preserved_judge"
                if field in judge_fields
                else "preserved"
            )
            for field in sorted(metrics)
        }
        rescored.append(
            {
                **source_record,
                "split": question.split,
                "expected_status": question.expected_status.value,
                "required_source_types": question.required_source_types,
                "required_answer_points": [
                    item.model_dump(mode="json") for item in question.required_answer_points
                ],
                "metrics": metrics,
                "rescore_provenance": {
                    "replacement_record": replacement_used,
                    "replacement_run_id": replacement_run_by_case.get(case_id),
                    "review_decision": decisions.get(case_id),
                    "computed_fields": computed_fields,
                    "preserved_judge_fields": [
                        field for field in judge_fields if field not in human_fields
                    ],
                    "human_adjudicated_fields": human_fields,
                    "field_provenance": field_provenance,
                    "human_adjudication_source": str(adjudications_path) if adjudication else None,
                },
            }
        )
        record_source_runs[case_id] = replacement_run_by_case.get(case_id, run_id)
    metrics = aggregate_metrics(rescored)
    metrics["result_content_hash"] = result_content_hash(rescored)
    expected_dev_ids = {item.id for item in dataset.questions if item.split == "dev"}
    expected_regression_ids = {
        item.id for item in dataset.questions if item.split == "regression"
    }
    actual_ids = {item["id"] for item in rescored}
    complete_dev_structural = actual_ids == expected_dev_ids and len(actual_ids) == 80
    complete_regression_structural = (
        actual_ids == expected_regression_ids and len(actual_ids) == 16
    )
    diagnostic_composite_runtime = bool(replacement_sources)
    uniform_candidate_identity = not diagnostic_composite_runtime
    complete_dev_eligible = (
        complete_dev_structural
        and not diagnostic_composite_runtime
        and uniform_candidate_identity
    )
    complete_regression_eligible = (
        complete_regression_structural
        and not diagnostic_composite_runtime
        and uniform_candidate_identity
    )
    all_questions_approved = all(
        item.review_status == "approved" for item in dataset.questions if item.id in actual_ids
    )
    if complete_regression_structural:
        rescore_scope = "regression"
        diagnostic_quality_checks = evaluate_regression_gate(
            metrics,
            rescored,
            complete_full_regression=True,
            all_questions_approved=all_questions_approved,
        )
        if diagnostic_composite_runtime or not uniform_candidate_identity:
            diagnostic_quality_checks["note"] = (
                "16-case regression quality checks passed for the reviewed composite; "
                "mixed runtime provenance prevents a formal frozen-candidate gate claim."
            )
    else:
        rescore_scope = "development" if complete_dev_structural else "subset"
        diagnostic_quality_checks = evaluate_development_gate(
            metrics,
            rescored,
            mode="qa",
            complete_full_dev=complete_dev_structural,
            all_questions_approved=all_questions_approved,
        )
        if diagnostic_composite_runtime or not uniform_candidate_identity:
            diagnostic_quality_checks["note"] = (
                "80-case diagnostic quality checks only; composite runtime identity cannot pass "
                "the frozen development gate."
            )
    development_gate = evaluate_development_gate(
        metrics,
        rescored,
        mode="qa",
        complete_full_dev=complete_dev_eligible,
        all_questions_approved=all_questions_approved,
    )
    if diagnostic_composite_runtime or not uniform_candidate_identity:
        development_gate["note"] = (
            "Diagnostic composite runtime: quality checks are reported separately, "
            "but this result cannot pass the frozen development gate."
        )
    regression_gate = evaluate_regression_gate(
        metrics,
        rescored,
        complete_full_regression=complete_regression_eligible,
        all_questions_approved=all_questions_approved,
    )
    if complete_regression_structural and (
        diagnostic_composite_runtime or not uniform_candidate_identity
    ):
        regression_gate["note"] = (
            "Reviewed composite covers all 16 regression cases and passes diagnostic "
            "quality checks, but mixed runtime provenance prevents a formal gate claim."
        )
    dataset_hash = _sha256(dataset_path)
    selected_ids_sorted = sorted(actual_ids)
    excluded_ids_sorted = sorted(source_case_ids - actual_ids)
    selection_sha256 = sha256_bytes(
        json.dumps(
            {"included_case_ids": selected_ids_sorted, "excluded_case_ids": excluded_ids_sorted},
            ensure_ascii=False,
            sort_keys=True,
        ).encode("utf-8")
    )
    replacement_identity_sources = sorted(
        (
            {
                "run_id": source["run_id"],
                "case_ids": source["case_ids"],
                "manifest_sha256": source["manifest_sha256"],
                "selected_records_sha256": source["selected_records_sha256"],
            }
            for source in replacement_sources
        ),
        key=lambda source: (source["run_id"], tuple(source["case_ids"])),
    )
    rescore_identity_inputs = {
        "formal_rescore_identity": rescore_identity,
        "dataset_sha256": dataset_hash,
        "selection_sha256": selection_sha256,
        "review_decisions_sha256": review_decisions_hash,
        "manual_adjudications_sha256": adjudications_hash,
        "overrides_sha256": overrides_hash,
        "source_manifest_sha256": source_manifest_hash,
        "source_results_sha256": source_results_hash,
        "replacement_sources": replacement_identity_sources,
    }
    rescore_identity_hash = _rescore_identity_sha256(rescore_identity_inputs)
    output_dir = project_root / "data" / "evaluation" / "rescores" / (
        f"{run_id}-{rescore_identity['artifact_evaluator']}-"
        f"{dataset_hash[:12]}-{selection_sha256[:12]}-{rescore_identity_hash[:12]}"
    )
    if output_dir.exists():
        raise FileExistsError(f"refusing to overwrite existing rescore: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=False)
    (output_dir / "records.jsonl").write_text(
        "".join(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n" for item in rescored),
        encoding="utf-8",
    )
    preserved_ids = sorted(actual_ids - set(replacement_records))
    preserved_payload = {
        record["id"]: record.get("result")
        for record in records
        if record["id"] in preserved_ids
    }
    preserved_hash = sha256_bytes(
        json.dumps(preserved_payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    )
    identifier_catalog = {
        item["id"]: item.get("metrics", {}).get("identifier_exists_in_locked_corpus", [])
        for item in rescored
    }
    rescore_manifest = {
        "schema_version": rescore_identity["schema_version"],
        "runtime_source": run_id.replace("-qa-dev", ""),
        "runtime_replacements": sorted(replacement_records),
        "evaluation_revision": rescore_identity["evaluation_revision"],
        "source_run_id": run_id,
        "source_manifest_sha256": source_manifest_hash,
        "source_results_sha256": source_results_hash,
        "source_preserved_result_sha256": preserved_hash,
        "replacement_run_id": replacement_run_id,
        "replacement_sources": replacement_sources,
        "record_source_runs": record_source_runs,
        "prompt_mismatches": prompt_mismatches,
        # Composite records can be useful for diagnosis but never identify a
        # freezeable, uniform runtime candidate. This remains true even when
        # the prompts happen to match, because records have more than one run
        # provenance.
        "diagnostic_composite_runtime": diagnostic_composite_runtime,
        "uniform_candidate_identity": uniform_candidate_identity,
        "dataset_sha256": dataset_hash,
        "review_decisions_sha256": review_decisions_hash,
        "review_decisions_imported_source_sha256": review_imported_source_hash,
        "manual_adjudications_sha256": adjudications_hash,
        "overrides_sha256": overrides_hash,
        "rescore_identity_sha256": rescore_identity_hash,
        "rescore_identity_fingerprint": rescore_identity_hash[:12],
        "rescore_identity_inputs": rescore_identity_inputs,
        "evaluator_policy_sha256": _sha256(project_root / "src" / "panda_agent" / "evaluation.py"),
        "selector_policy": rescore_identity["selector_policy"],
        "identifier_catalog_fingerprint": sha256_bytes(
            json.dumps(identifier_catalog, ensure_ascii=False, sort_keys=True).encode("utf-8")
        ),
        "rescore_model_calls": 0,
        "rescore_token_usage": 0,
        "cases": len(rescored),
        "included_case_ids": selected_ids_sorted,
        "excluded_case_ids": excluded_ids_sorted,
        "selection_sha256": selection_sha256,
        "complete_development_gate_eligible": complete_dev_eligible,
        "complete_regression_gate_eligible": complete_regression_eligible,
        "complete_regression_structural": complete_regression_structural,
        "rescore_scope": rescore_scope,
        "subset_diagnostic_only": not (
            complete_dev_eligible or complete_regression_eligible
        ),
        "immutable_source_records": True,
    }
    (output_dir / "rescore_manifest.json").write_text(
        json.dumps(rescore_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    report = {
        "source_run_id": run_id,
        "dataset": str(dataset_path),
        "dataset_sha256": dataset_hash,
        "review_decisions_sha256": review_decisions_hash,
        "review_decisions_imported_source_sha256": review_imported_source_hash,
        "manual_adjudications_sha256": adjudications_hash,
        "overrides_sha256": overrides_hash,
        "rescore_identity_sha256": rescore_identity_hash,
        "rescore_identity_fingerprint": rescore_identity_hash[:12],
        "replacement_run_id": replacement_run_id,
        "replacement_sources": replacement_sources,
        "prompt_mismatches": prompt_mismatches,
        "diagnostic_composite_runtime": rescore_manifest["diagnostic_composite_runtime"],
        "cases_rescored": len(rescored),
        "complete_v2_dev": complete_dev_eligible,
        "complete_v2_dev_structural": complete_dev_structural,
        "complete_regression": complete_regression_eligible,
        "complete_regression_structural": complete_regression_structural,
        "rescore_scope": rescore_scope,
        "diagnostic_quality_checks": diagnostic_quality_checks,
        "rescore_model_calls": 0,
        "rescore_token_usage": 0,
        "source_results_sha256": source_results_hash,
        "runtime_source": rescore_manifest["runtime_source"],
        "runtime_replacements": rescore_manifest["runtime_replacements"],
        "schema_version": rescore_identity["schema_version"],
        "evaluation_revision": rescore_identity["evaluation_revision"],
        "selector_policy": rescore_identity["selector_policy"],
        "metrics": metrics,
        "development_gate": development_gate,
        "regression_gate": regression_gate,
    }
    (output_dir / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return {**report, "output_dir": str(output_dir)}


def audit_dataset(
    project_root: Path,
    dataset_path: Path,
    *,
    similarities: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    dataset = load_gold_dataset(dataset_path)
    from panda_agent.evaluation_runner import load_object_lookup

    objects = list(load_object_lookup(project_root).values())
    widths: list[dict[str, Any]] = []
    selector_keys: set[str] = set()
    for question in dataset.questions:
        for group in question.required_evidence_groups:
            for selector in group.any_of:
                payload = selector.model_dump(mode="json", exclude_none=True)
                key = json.dumps(payload, sort_keys=True, ensure_ascii=False)
                selector_keys.add(key)
                widths.append(
                    {
                        "case_id": question.id,
                        "group_id": group.group_id,
                        "role": group.role,
                        "selector": payload,
                        "matches": sum(selector.matches(item) for item in objects),
                    }
                )
    if similarities is None:
        _, similarities = cluster_questions(dataset)
    match_counts = sorted(item["matches"] for item in widths)
    return {
        "dataset": str(dataset_path),
        "question_count": len(dataset.questions),
        "release_eligible": dataset.release_eligible,
        "acceptance_exposed": dataset.acceptance_exposed,
        "split_counts": dict(Counter(item.split for item in dataset.questions)),
        "status_by_split": {
            split: dict(
                Counter(item.expected_status.value for item in dataset.questions if item.split == split)
            )
            for split in sorted({item.split for item in dataset.questions})
        },
        "selector_count": len(widths),
        "unique_selector_count": len(selector_keys),
        "selector_match_width": {
            "mean": sum(match_counts) / len(match_counts) if match_counts else 0.0,
            "median": match_counts[len(match_counts) // 2] if match_counts else 0,
            "max": max(match_counts, default=0),
        },
        "broad_selectors": sorted(widths, key=lambda item: item["matches"], reverse=True)[:30],
        "cross_split_similarity_pairs": similarities[:100],
    }
