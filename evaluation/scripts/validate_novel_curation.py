"""T0 static validation for the Novel v1 curation package.

Checks dataset/sidecar consistency, ID and family uniqueness, duplicate
queries, canonical intents, difficulty and novelty enums, overlap metadata,
curation governance flags, deterministic evidence-selector existence, and
coverage-report consistency. Purely static: no retrieval, QA, model, judge,
embedding, or index operations.

Usage (repo root):
    python evaluation/scripts/validate_novel_curation.py
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from panda_agent.evaluation import GoldDataset, INTENTS  # noqa: E402

NOVEL_DIR = REPO_ROOT / "evaluation" / "novel" / "v1"

CANONICAL_INTENTS = INTENTS
DIFFICULTIES = {"simple", "moderate", "hard"}
NOVELTY_TYPES = {
    "entity",
    "relation",
    "composition",
    "reasoning_topology",
    "nontrivial_expression",
    "failure_mode",
    "task_form",
}
WORDING = {"low", "medium", "high"}
ENTITY_OVERLAP = {"none", "partial", "high"}
EVIDENCE_OVERLAP = {"none", "partial", "high"}
NEED_OVERLAP = {"low", "medium", "high"}
SOURCE_TYPES = {"paper", "documentation", "readme", "code", "workflow", "graph"}
EXPRESSION_FORMS = {
    "explicit",
    "descriptive",
    "causal",
    "implementation_oriented",
    "identifier_free",
    "identifier_heavy",
}

errors: list[str] = []
notes: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def load_yaml(path: Path):
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def main() -> int:
    dataset_path = NOVEL_DIR / "novel_dev.yaml"
    sidecar_path = NOVEL_DIR / "curation_metadata.yaml"
    coverage_path = NOVEL_DIR / "coverage_report.json"
    manifest_path = NOVEL_DIR / "manifest.json"
    source_manifest_path = REPO_ROOT / "data" / "manifests" / "source_manifest.json"

    raw_dataset = load_yaml(dataset_path)
    raw_sidecar = load_yaml(sidecar_path)
    coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source_manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))

    # 1. Dataset parses through the existing strict Gold schema.
    try:
        dataset = GoldDataset.model_validate(raw_dataset)
    except Exception as exc:  # noqa: BLE001
        print(f"GoldDataset parse failed: {exc}")
        return 1

    repo_roots = {
        item["repo_id"]: Path(item["path"])
        for item in source_manifest.get("repositories", [])
    }
    paper_pages = {
        item["doc_id"]: item["page_count"] for item in source_manifest.get("papers", [])
    }
    web_root = REPO_ROOT / "data" / "sources" / "web"

    records = raw_sidecar.get("records", [])
    if raw_sidecar.get("schema_version") != "novel-curation-sidecar-v1":
        fail("sidecar schema_version must be novel-curation-sidecar-v1")
    if raw_sidecar.get("benchmark_version") != raw_dataset["benchmark_version"]:
        fail("sidecar benchmark_version does not match dataset benchmark_version")

    questions = dataset.questions
    by_id = {q.id: q for q in questions}

    # 2. One-to-one mapping between dataset questions and sidecar records.
    sidecar_by_id = {}
    for record in records:
        qid = record.get("question_id")
        if not qid:
            fail("sidecar record without question_id")
            continue
        if qid in sidecar_by_id:
            fail(f"duplicate sidecar record for {qid}")
        sidecar_by_id[qid] = record
    missing = sorted(set(by_id) - set(sidecar_by_id))
    orphans = sorted(set(sidecar_by_id) - set(by_id))
    if missing:
        fail(f"questions without sidecar records: {missing}")
    if orphans:
        fail(f"orphan sidecar records without dataset questions: {orphans}")

    # 3. IDs unique (dataset schema enforces), families present and unique.
    family_ids = []
    for qid, record in sorted(sidecar_by_id.items()):
        family = record.get("curation_family_id")
        if not family or not family.startswith("nf"):
            fail(f"{qid}: missing or malformed curation_family_id")
            continue
        family_ids.append(family)
        question = by_id.get(qid)
        if question is None:
            continue
        if question.cluster_id and question.cluster_id != family:
            fail(f"{qid}: Gold cluster_id {question.cluster_id!r} does not mirror family {family!r}")
        # Intent and status mirrors.
        if record.get("intent") != question.intent:
            fail(f"{qid}: sidecar intent {record.get('intent')!r} != dataset intent {question.intent!r}")
        if record.get("expected_status") != question.expected_status.value:
            fail(f"{qid}: sidecar expected_status does not match dataset")
        # Governance: pilot records must stay unapproved drafts.
        if question.review_status != "draft":
            fail(f"{qid}: pilot review_status must stay draft, got {question.review_status!r}")
        if question.reviewer is not None or question.reviewed_at is not None:
            fail(f"{qid}: draft pilot records must not carry reviewer/reviewed_at")
        # Novelty block.
        novelty = record.get("novelty") or {}
        types = novelty.get("types") or []
        if not types:
            fail(f"{qid}: at least one novelty type is required")
        unknown_types = sorted(set(types) - NOVELTY_TYPES)
        if unknown_types:
            fail(f"{qid}: unknown novelty types {unknown_types}")
        closest = novelty.get("closest_exposed_cases")
        assessment = novelty.get("closest_case_assessment")
        if closest is None and assessment != "none_found":
            fail(f"{qid}: closest_exposed_cases missing and no closest_case_assessment")
        if closest is not None:
            for case in closest:
                if not (isinstance(case, str) and case.startswith("g") and case[1:].isdigit()):
                    fail(f"{qid}: malformed closest case {case!r}")
            if not closest and assessment != "none_found":
                fail(f"{qid}: empty closest list requires closest_case_assessment none_found")
        overlap = novelty.get("benchmark_overlap") or {}
        for key, allowed in (
            ("wording", WORDING),
            ("entity", ENTITY_OVERLAP),
            ("evidence", EVIDENCE_OVERLAP),
            ("information_need", NEED_OVERLAP),
        ):
            if overlap.get(key) not in allowed:
                fail(f"{qid}: benchmark_overlap.{key} missing or invalid ({overlap.get(key)!r})")
        if not (novelty.get("rationale") or "").strip():
            fail(f"{qid}: empty novelty rationale")
        # Coverage block.
        cov = record.get("coverage") or {}
        if cov.get("difficulty") not in DIFFICULTIES:
            fail(f"{qid}: coverage.difficulty invalid ({cov.get('difficulty')!r})")
        if cov.get("expression_form") not in EXPRESSION_FORMS:
            fail(f"{qid}: coverage.expression_form invalid ({cov.get('expression_form')!r})")
        stypes = cov.get("source_types") or []
        unknown_stypes = sorted(set(stypes) - SOURCE_TYPES)
        if unknown_stypes:
            fail(f"{qid}: unknown coverage source_types {unknown_stypes}")
        repo_scope = cov.get("repository_scope")
        if repo_scope not in {"single_repository", "cross_repository"}:
            fail(f"{qid}: coverage.repository_scope invalid ({repo_scope!r})")
        # Curation block.
        cur = record.get("curation") or {}
        if cur.get("agent_outcome_seen_before_freeze") is not False:
            fail(f"{qid}: agent_outcome_seen_before_freeze must be false")
        if cur.get("evidence_selected_from_agent_output") is not False:
            fail(f"{qid}: evidence_selected_from_agent_output must be false")
        if not (cur.get("origin") or "").strip():
            fail(f"{qid}: curation.origin missing")
        if not (cur.get("lifecycle") or "").strip():
            fail(f"{qid}: curation.lifecycle missing")

    duplicate_families = sorted(f for f, n in Counter(family_ids).items() if n > 1)
    if duplicate_families:
        notes.append(
            "shared families (allowed only with an explicit same-family curation "
            f"reason): {duplicate_families}"
        )

    # 4. No duplicate question text (exact and casefolded).
    seen_exact = {}
    seen_folded = {}
    for q in questions:
        if q.query in seen_exact:
            fail(f"duplicate query text between {seen_exact[q.query]} and {q.id}")
        seen_exact[q.query] = q.id
        folded = q.query.casefold()
        if folded in seen_folded:
            fail(f"duplicate casefolded query between {seen_folded[folded]} and {q.id}")
        seen_folded[folded] = q.id

    # 5. Split hygiene: no validation/holdout content in the dev pilot file.
    for q in questions:
        if q.split != "novel_dev":
            fail(f"{q.id}: pilot dataset may only contain novel_dev split, got {q.split!r}")

    # 6. Cross-file family isolation: one family must not cross novel splits.
    family_splits: dict[str, set[str]] = {}
    for path in sorted(NOVEL_DIR.glob("novel_*.yaml")):
        payload = load_yaml(path)
        for question in payload.get("questions", []):
            family_splits.setdefault(question.get("cluster_id"), set()).add(question.get("split"))
    for family, splits in family_splits.items():
        if len(splits) > 1:
            fail(f"family {family} crosses novel splits: {sorted(splits)}")

    # 7. Deterministic evidence-selector checks: path existence, page bounds.
    for q in questions:
        for group in q.required_evidence_groups:
            if not group.any_of:
                fail(f"{q.id}/{group.group_id}: empty any_of")
            for selector in group.any_of:
                fields = selector.model_dump(exclude_none=True)
                if not fields:
                    fail(f"{q.id}/{group.group_id}: empty selector")
                source_id = selector.source_id
                if selector.path is not None:
                    if source_id in repo_roots:
                        target = repo_roots[source_id] / selector.path.replace("\\", "/")
                        if not target.exists():
                            fail(f"{q.id}/{group.group_id}: repo path missing: {source_id}/{selector.path}")
                    elif source_id == "pandaroot_sphinx_2023_08_25_dev":
                        target = web_root / selector.path.replace("\\", "/")
                        if not target.exists():
                            fail(f"{q.id}/{group.group_id}: web path missing: {selector.path}")
                    else:
                        fail(f"{q.id}/{group.group_id}: path selector with unsupported source {source_id!r}")
                if selector.pdf_page is not None:
                    limit = paper_pages.get(source_id)
                    if limit is None:
                        fail(f"{q.id}/{group.group_id}: pdf_page on non-paper source {source_id!r}")
                    else:
                        end = selector.pdf_page_end or selector.pdf_page
                        if not (1 <= selector.pdf_page <= end <= limit):
                            fail(
                                f"{q.id}/{group.group_id}: pdf_page range "
                                f"{selector.pdf_page}-{end} outside 1..{limit} for {source_id}"
                            )

    # 8. Coverage-report consistency with the sidecar.
    sidecar_list = [sidecar_by_id[q.id] for q in questions if q.id in sidecar_by_id]

    def count(field):
        return dict(Counter((r.get("coverage") or {}).get(field) for r in sidecar_list))

    checks = {
        "question_count": (coverage.get("question_count"), len(questions)),
        "independent_family_count": (
            coverage.get("independent_family_count"),
            len(set(family_ids)),
        ),
        "counts_by_intent": (
            coverage.get("counts_by_intent"),
            dict(Counter(r.get("intent") for r in sidecar_list)),
        ),
        "counts_by_difficulty": (coverage.get("counts_by_difficulty"), count("difficulty")),
        "counts_by_expected_status": (
            coverage.get("counts_by_expected_status"),
            dict(Counter(q.expected_status.value for q in questions)),
        ),
        "counts_by_expression_form": (coverage.get("counts_by_expression_form"), count("expression_form")),
        "counts_by_repository_scope": (coverage.get("counts_by_repository_scope"), count("repository_scope")),
        "counts_by_evidence_topology": (coverage.get("counts_by_evidence_topology"), count("evidence_topology")),
    }
    novelty_counts = Counter(
        t for r in sidecar_list for t in (r.get("novelty") or {}).get("types", [])
    )
    checks["counts_by_novelty_type"] = (
        coverage.get("counts_by_novelty_type"),
        dict(novelty_counts),
    )
    for label, (reported, computed) in checks.items():
        # Reports may state explicit zero entries (e.g. cross_repository: 0)
        # to document gaps; zero entries do not affect count consistency.
        if isinstance(reported, dict):
            reported = {k: v for k, v in reported.items() if v}
        if reported != computed:
            fail(
                f"coverage_report.{label} mismatch: reported {reported} != computed {computed}"
            )

    multi_hop = sum(1 for r in sidecar_list if (r.get("coverage") or {}).get("evidence_topology") == "multi_hop")
    if coverage.get("multi_hop_count") != multi_hop:
        fail(f"coverage_report.multi_hop_count mismatch ({coverage.get('multi_hop_count')} != {multi_hop})")
    cross_repo = sum(
        1 for r in sidecar_list if (r.get("coverage") or {}).get("repository_scope") == "cross_repository"
    )
    if coverage.get("cross_repository_count") != cross_repo:
        fail(f"coverage_report.cross_repository_count mismatch ({coverage.get('cross_repository_count')} != {cross_repo})")
    descriptive = sum(
        1
        for r in sidecar_list
        if (r.get("coverage") or {}).get("expression_form") in {"descriptive", "identifier_free"}
    )
    if coverage.get("descriptive_or_identifier_free_count") != descriptive:
        fail("coverage_report.descriptive_or_identifier_free_count mismatch")
    multi_evidence = sum(1 for q in questions if len(q.required_evidence_groups) >= 2)
    if coverage.get("multi_evidence_count") != multi_evidence:
        fail(f"coverage_report.multi_evidence_count mismatch ({coverage.get('multi_evidence_count')} != {multi_evidence})")

    # 9. Manifest consistency.
    if manifest.get("question_count") != len(questions):
        fail("manifest question_count mismatch")
    if manifest.get("independent_family_count") != len(set(family_ids)):
        fail("manifest independent_family_count mismatch")
    if manifest.get("benchmark_version") != raw_dataset["benchmark_version"]:
        fail("manifest benchmark_version mismatch")
    if manifest.get("release_eligible") is not False:
        fail("pilot manifest must keep release_eligible false")

    for note in notes:
        print(f"NOTE: {note}")

    if errors:
        print(f"FAIL — {len(errors)} problem(s):")
        for message in errors:
            print(f"  - {message}")
        return 1

    print(
        f"PASS — {len(questions)} novel_dev questions, "
        f"{len(set(family_ids))} independent families, all static checks green."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
