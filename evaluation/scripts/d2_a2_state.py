"""Deterministic D1-compatible evaluation state for the D2-A2 terminology runner.

Materializes the current D1 contract exactly through the PRODUCTION loaders
(``seed_knowledge_objects``, ``materialize_seed_relations``,
``seed_workflow_steps``, ``seed_knowledge_aliases``) plus a small set of
DECLARED real-corpus source-native rows, and wraps the result in a read-only
in-memory connection adapter that answers EXACTLY the SQL shapes
``EntityResolver.resolve_shadow`` issues (mirroring the FakeConnection pattern
of ``tests/unit/test_d2_shadow_resolution.py``).

Pure Python: no database, no network, no model, no Qdrant.  Deterministic:
every query answer is ordered and every declared row is a fixed constant.

Declared real-corpus source-native rows (ids/versions/locators verified against
``data/normalized/9925ec31a6122e05388806990f79aae036f3b0989c4584d24f2092bc4edb3d94/knowledge_objects.jsonl``):

1. object.11268c4b6743544a8c5494e6 | pandaroot | class PndLmdTrackQ (LmdQA header)
2. object.b786907743079aff236b65b8 | restgas_determination | class PndLmdTrackQ (same path, different locked source)
3. object.c60a8a86eb1b0578b83a8fa2 | luminosityfit | class PndLmdCombinedDataReader
4. object.ceb44bd02a5e3a790cf2dfad | luminosityfit | source_file model/PndLmdModelFactory.cxx
5. object.91b3e79331a311bb259f6a04 | pandaroot | source_file detectors/lmd/LmdQA/PndLmdTrackQ.cxx
6. object.04b079cb4f083d29d694e47a | luminosityfit | source_file data/PndLmdCombinedDataReader.cxx
7. object.5cae2ceab6e67bb4c9065331 | restgas_determination | source_file macro/target/ana_dpm.C

Provenance/evidence support objects (NOT resolver-facing, never served through
the adapter's ``knowledge_objects`` answers): the governed seed relations and
the two accepted aliases resolve their machine-traceable provenance through
declared source-native corpus rows, mirroring the fixture style of
``tests/unit/test_d1_integrity.py``.  The four restgas/luminosityfit/pandaroot
file-level paths that appear both in the declared rows above and in the D1
fixtures are covered once, by the real-corpus declared rows; the remaining
evidence support rows reuse the D1 integrity fixture identifiers (synthetic
file-level ids; real corpus ids for the thesis sections and the sphinx page).
The evaluation state's resolver-facing object table therefore holds exactly
(D2-A1R2 state correction: the symbol-bearing PndLmdModelFactory function record was initially missing from the declared rows). (D2-A1R2 state correction: the symbol-bearing PndLmdModelFactory function record was initially missing from the declared rows).
"""

from __future__ import annotations

import re
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

from panda_agent.config import load_seed_relations
from panda_agent.entity_resolution import EntityResolver
from panda_agent.ingestion import (
    materialize_seed_relations,
    seed_knowledge_aliases,
    seed_knowledge_objects,
    seed_workflow_steps,
)
from panda_agent.models import (
    KnowledgeAlias,
    KnowledgeObject,
    RelationEdge,
    SourceLocator,
    WorkflowStep,
)

RESTGAS_VERSION = "restgas_determination@11f1edc49dcbaeb61d707491a6d3bbec390fcd42"
PANDAROOT_VERSION = "pandaroot@18c09e91100db27867ded30e708b4dae95bd8357"
LUMINOSITYFIT_VERSION = "luminosityfit@ddd83dcd1a74093bf48ef259a2849a67f9413f32"
KARAVDINA_VERSION = (
    "karavdina_2015@422421852c5a046c24e894a77b9380988ec8172914e9b30b055a100145c07a2b"
)
PFLUEGER_VERSION = (
    "pflueger_2017@1b6ec987fc1430be085f2a7ba631d634f6580115ff0a90dff090dfcba5e990f3"
)
SPHINX_VERSION = (
    "pandaroot_sphinx_2023_08_25_dev@"
    "5bff86c0f3a1102c80f3466a8ca0a63db48c0c7d8f142a78a0849219d7844f87"
)

EXPECTED_SEED_OBJECT_COUNT = 24
EXPECTED_DECLARED_OBJECT_COUNT = 8
EXPECTED_OBJECT_COUNT = EXPECTED_SEED_OBJECT_COUNT + EXPECTED_DECLARED_OBJECT_COUNT
EXPECTED_ACCEPTED_RELATION_COUNT = 16
EXPECTED_ACCEPTED_ALIAS_COUNT = 2
EXPECTED_WORKFLOW_STEP_COUNT = 1

REQUIRED_CANONICAL_IDS = (
    "concept.luminosityfit.luminosity_fit_model",
    "workflow.restgas.first_pass_poca",
    "data_product.restgas.pid_final_root",
    "configuration.restgas_profile",
)

POCA_WORKFLOW_ID = "workflow.restgas.first_pass_poca"
POCA_EXPECTED_FEATURES = (
    "CONSUMES data_product.restgas.pid_root",
    "PRODUCES data_product.restgas.boost_root",
)

ALLOWED_IDENTITY_ROLES = frozenset({"canonical", "source_native"})

SPHINX_RUNNING_PAGE_PATH = (
    "pandaroot_sphinx_2023_08_25_dev/raw/~pandacc/documentation/"
    "2023-08-25-dev/sphinx/Running/Running.html"
)


def _declared_row(
    object_id: str,
    *,
    object_type: str,
    source_id: str,
    source_version_id: str,
    title: str,
    path: str | None = None,
    symbol: str | None = None,
    canonical_locator: str,
) -> KnowledgeObject:
    """One DECLARED real-corpus source-native evaluation-state row.

    Ids, versions, locators, types, titles, authority, and canonical locators
    are the verified corpus values; the free text carries the title (the
    resolver never consumes source-native row text).  Parent rows are not part
    of the declared 32-object state, so ``parent_object_id`` stays unset.
    """

    return KnowledgeObject(
        object_id=object_id,
        object_type=object_type,
        source_id=source_id,
        source_version_id=source_version_id,
        title=title,
        text=title,
        authority_level="primary",
        locator=SourceLocator(path=path, symbol=symbol),
        parent_object_id=None,
        metadata={"identity_role": "source_native"},
        canonical_locator=canonical_locator,
    )


def declared_source_native_rows() -> list[KnowledgeObject]:
    """The seven DECLARED real-corpus source-native evaluation-state rows."""

    return [
        _declared_row(
            "object.11268c4b6743544a8c5494e6",
            object_type="class",
            source_id="pandaroot",
            source_version_id=PANDAROOT_VERSION,
            title="PndLmdTrackQ",
            path="detectors/lmd/LmdQA/PndLmdTrackQ.h",
            symbol="PndLmdTrackQ",
            canonical_locator="detectors/lmd/LmdQA/PndLmdTrackQ.h:PndLmdTrackQ:26",
        ),
        _declared_row(
            "object.b786907743079aff236b65b8",
            object_type="class",
            source_id="restgas_determination",
            source_version_id=RESTGAS_VERSION,
            title="PndLmdTrackQ",
            path="detectors/lmd/LmdQA/PndLmdTrackQ.h",
            symbol="PndLmdTrackQ",
            canonical_locator="detectors/lmd/LmdQA/PndLmdTrackQ.h:PndLmdTrackQ:29",
        ),
        _declared_row(
            "object.c60a8a86eb1b0578b83a8fa2",
            object_type="class",
            source_id="luminosityfit",
            source_version_id=LUMINOSITYFIT_VERSION,
            title="PndLmdCombinedDataReader",
            path="data/PndLmdCombinedDataReader.h",
            symbol="PndLmdCombinedDataReader",
            canonical_locator="data/PndLmdCombinedDataReader.h:PndLmdCombinedDataReader:10",
        ),
        _declared_row(
            "object.ceb44bd02a5e3a790cf2dfad",
            object_type="source_file",
            source_id="luminosityfit",
            source_version_id=LUMINOSITYFIT_VERSION,
            title="model/PndLmdModelFactory.cxx",
            path="model/PndLmdModelFactory.cxx",
            canonical_locator="model/PndLmdModelFactory.cxx",
        ),
        _declared_row(
            "object.c08459387c6fd0c77a717960",
            object_type="function",
            source_id="luminosityfit",
            source_version_id=LUMINOSITYFIT_VERSION,
            title="PndLmdModelFactory",
            path="model/PndLmdModelFactory.cxx",
            symbol="PndLmdModelFactory",
            canonical_locator="model/PndLmdModelFactory.cxx:PndLmdModelFactory",
        ),
        _declared_row(
            "object.91b3e79331a311bb259f6a04",
            object_type="source_file",
            source_id="pandaroot",
            source_version_id=PANDAROOT_VERSION,
            title="detectors/lmd/LmdQA/PndLmdTrackQ.cxx",
            path="detectors/lmd/LmdQA/PndLmdTrackQ.cxx",
            canonical_locator="detectors/lmd/LmdQA/PndLmdTrackQ.cxx",
        ),
        _declared_row(
            "object.04b079cb4f083d29d694e47a",
            object_type="source_file",
            source_id="luminosityfit",
            source_version_id=LUMINOSITYFIT_VERSION,
            title="data/PndLmdCombinedDataReader.cxx",
            path="data/PndLmdCombinedDataReader.cxx",
            canonical_locator="data/PndLmdCombinedDataReader.cxx",
        ),
        _declared_row(
            "object.5cae2ceab6e67bb4c9065331",
            object_type="source_file",
            source_id="restgas_determination",
            source_version_id=RESTGAS_VERSION,
            title="macro/target/ana_dpm.C",
            path="macro/target/ana_dpm.C",
            canonical_locator="macro/target/ana_dpm.C",
        ),
    ]


def _support_row(
    object_id: str,
    *,
    object_type: str,
    source_id: str,
    source_version_id: str,
    title: str,
    locator: SourceLocator,
) -> KnowledgeObject:
    """One provenance/evidence support row (never resolver-facing)."""

    return KnowledgeObject(
        object_id=object_id,
        object_type=object_type,
        source_id=source_id,
        source_version_id=source_version_id,
        title=title,
        text=title,
        authority_level="primary",
        locator=locator,
        canonical_locator=locator.path or object_id,
        metadata={},
    )


def provenance_support_rows() -> list[KnowledgeObject]:
    """Real-corpus rows required by governed provenance/evidence resolution.

    These rows exist only so the PRODUCTION loaders can resolve the declared
    evidence paths / provenance paths of the 16 accepted seed relations and the
    two accepted aliases.  They are excluded from the resolver-facing object
    table on purpose (the frozen D2-A2 state exposes exactly 31 objects); the
    resolver never queries them.
    """

    return [
        # Karavdina 2015 thesis sections at the reviewed LMD pages 94/100/104
        # (real corpus ids; locator style mirrors tests/unit/test_d1_integrity.py).
        _support_row(
            "object.b1739b9b6e502cda6a154406",
            object_type="thesis_section",
            source_id="karavdina_2015",
            source_version_id=KARAVDINA_VERSION,
            title="Karavdina thesis section (page 94)",
            locator=SourceLocator(pdf_page=94, section_path=["Chapter 7"]),
        ),
        _support_row(
            "object.30cf42f607e2c228dfe125fd",
            object_type="thesis_section",
            source_id="karavdina_2015",
            source_version_id=KARAVDINA_VERSION,
            title="Karavdina thesis section (page 100)",
            locator=SourceLocator(pdf_page=100, section_path=["Chapter 7"]),
        ),
        _support_row(
            "object.7cd1257841fc461a4e1e5390",
            object_type="thesis_section",
            source_id="karavdina_2015",
            source_version_id=KARAVDINA_VERSION,
            title="Karavdina thesis section (page 104)",
            locator=SourceLocator(pdf_page=104, section_path=["Chapter 7"]),
        ),
        # Pflueger 2017 thesis sections at the reviewed model pages 51/57/65.
        _support_row(
            "object.faaced8bd5058b2a19ba9528",
            object_type="thesis_section",
            source_id="pflueger_2017",
            source_version_id=PFLUEGER_VERSION,
            title="Pflueger thesis section (page 51)",
            locator=SourceLocator(pdf_page=51, section_path=["Chapter 4"]),
        ),
        _support_row(
            "object.86b7c9f862f3e5c328823444",
            object_type="thesis_section",
            source_id="pflueger_2017",
            source_version_id=PFLUEGER_VERSION,
            title="Pflueger thesis section (page 57)",
            locator=SourceLocator(pdf_page=57, section_path=["Chapter 4"]),
        ),
        _support_row(
            "object.6f688277a08ed2f236ae74df",
            object_type="thesis_section",
            source_id="pflueger_2017",
            source_version_id=PFLUEGER_VERSION,
            title="Pflueger thesis section (page 65)",
            locator=SourceLocator(pdf_page=65, section_path=["Chapter 4"]),
        ),
        # Sphinx Running/Running.html page object (real corpus id and path).
        _support_row(
            "object.79b75480980719256f8b7937",
            object_type="sphinx_page",
            source_id="pandaroot_sphinx_2023_08_25_dev",
            source_version_id=SPHINX_VERSION,
            title="Running/Running.html",
            locator=SourceLocator(path=SPHINX_RUNNING_PAGE_PATH),
        ),
        # RestgasDetermination file-level rows required by declared evidence
        # paths of the seed relations and by the alias provenance paths
        # (fixture identifiers mirror tests/unit/test_d1_integrity.py).
        _support_row(
            "object.effcorr2",
            object_type="source_file",
            source_id="restgas_determination",
            source_version_id=RESTGAS_VERSION,
            title="macro/target/correction/efficiency_correction_2.C",
            locator=SourceLocator(
                path="macro/target/correction/efficiency_correction_2.C"
            ),
        ),
        _support_row(
            "object.effcorrsteps",
            object_type="source_file",
            source_id="restgas_determination",
            source_version_id=RESTGAS_VERSION,
            title="macro/target/correction/efficiency_correction_steps.C",
            locator=SourceLocator(
                path="macro/target/correction/efficiency_correction_steps.C"
            ),
        ),
        _support_row(
            "object.readme",
            object_type="readme_section",
            source_id="restgas_determination",
            source_version_id=RESTGAS_VERSION,
            title="README.md",
            locator=SourceLocator(path="README.md"),
        ),
        _support_row(
            "object.targetreadme",
            object_type="readme_section",
            source_id="restgas_determination",
            source_version_id=RESTGAS_VERSION,
            title="macro/target/README.md",
            locator=SourceLocator(path="macro/target/README.md"),
        ),
        _support_row(
            "object.pidcomplete",
            object_type="source_file",
            source_id="restgas_determination",
            source_version_id=RESTGAS_VERSION,
            title="macro/target/pid_complete.C",
            locator=SourceLocator(path="macro/target/pid_complete.C"),
        ),
        _support_row(
            "object.prodaod",
            object_type="source_file",
            source_id="restgas_determination",
            source_version_id=RESTGAS_VERSION,
            title="macro/target/prod_aod_complete.C",
            locator=SourceLocator(path="macro/target/prod_aod_complete.C"),
        ),
    ]


# Column orders mirror _OBJECT_COLUMNS / _D2_OBJECT_COLUMNS in
# src/panda_agent/entity_resolution.py exactly (the D2 canonical query puts
# metadata before canonical_locator).
_OBJECT_COLUMNS = (
    "object_id",
    "source_id",
    "source_version_id",
    "object_type",
    "title",
    "text",
    "authority_level",
    "locator",
    "canonical_locator",
)
_D2_OBJECT_COLUMNS = (
    "object_id",
    "source_id",
    "source_version_id",
    "object_type",
    "title",
    "text",
    "authority_level",
    "locator",
    "metadata",
    "canonical_locator",
)

_WRITE_SQL_PATTERN = re.compile(
    r"\b(insert|update|delete|upsert|create|drop|alter)\b"
)


def _assert_read_only(sql: str) -> None:
    if _WRITE_SQL_PATTERN.search(sql.casefold()):
        raise RuntimeError(
            "evaluation-state adapter is read-only; write statement rejected"
        )


def _row_tuple(row: KnowledgeObject, columns: tuple[str, ...]) -> tuple:
    values = {
        "object_id": row.object_id,
        "source_id": row.source_id,
        "source_version_id": row.source_version_id,
        "object_type": row.object_type,
        "title": row.title,
        "text": row.text,
        "authority_level": str(row.authority_level),
        "locator": row.locator.model_dump(),
        "metadata": dict(row.metadata),
        "canonical_locator": row.canonical_locator,
    }
    return tuple(values[column] for column in columns)


def _exact_hit(row: KnowledgeObject, values: list[Any]) -> bool:
    """Mirror of the resolver's exact-match WHERE clause (symbol/title/path/
    basename), with SQL NULL semantics (a NULL locator field never matches)."""

    symbol = row.locator.symbol
    path = row.locator.path
    basename = path.rsplit("/", 1)[-1] if path else None
    return (
        row.title in values
        or (symbol is not None and symbol in values)
        or (path is not None and path in values)
        or (basename is not None and basename in values)
    )


class EvaluationStateConnection:
    """Read-only in-memory stand-in answering the D2 resolver SQL shapes.

    Dispatch mirrors the FakeConnection of
    ``tests/unit/test_d2_shadow_resolution.py``: the dispatch order matters
    because the canonical relation-feature SQL contains the substring
    ``object_id=any``.  Every answer is deterministically ordered and every
    statement is asserted read-only.
    """

    def __init__(
        self,
        objects: list[KnowledgeObject],
        aliases: list[KnowledgeAlias],
        relations: list[RelationEdge],
    ) -> None:
        self._objects = sorted(objects, key=lambda item: item.object_id)
        self._objects_by_id = {item.object_id: item for item in self._objects}
        self._aliases = sorted(
            (
                alias
                for alias in aliases
                if str(alias.review_status) == "accepted"
            ),
            key=lambda item: (item.normalized_alias, item.target_object_id),
        )
        self._accepted_relations = sorted(
            (
                edge
                for edge in relations
                if str(edge.review_status) == "accepted"
            ),
            key=lambda item: (item.subject_id, item.predicate, item.object_id),
        )
        self.statements: list[tuple[str, tuple]] = []

    def execute(self, sql: str, params: tuple | None = None):
        _assert_read_only(sql)
        self.statements.append((sql, params or ()))
        lowered = sql.casefold()
        if "knowledge_aliases" in lowered:
            return _Rows(
                [
                    (
                        alias.alias_text,
                        alias.normalized_alias,
                        alias.target_object_id,
                        alias.source_version_id,
                        alias.correction_message,
                    )
                    for alias in self._aliases
                ]
            )
        if "same_as" in lowered:
            return _Rows(
                [
                    (edge.subject_id, edge.object_id)
                    for edge in self._accepted_relations
                    if edge.predicate == "SAME_AS"
                ]
            )
        if "identity_role" in lowered:
            return _Rows(
                [
                    _row_tuple(row, _D2_OBJECT_COLUMNS)
                    for row in self._objects
                    if row.metadata.get("identity_role") == "canonical"
                ]
            )
        if "relation_edges" in lowered:
            values = set(list(params)[0]) if params else set()
            return _Rows(
                [
                    (
                        edge.subject_id,
                        edge.predicate,
                        edge.object_id,
                        self._objects_by_id[edge.subject_id].title
                        if edge.subject_id in self._objects_by_id
                        else None,
                        self._objects_by_id[edge.object_id].title
                        if edge.object_id in self._objects_by_id
                        else None,
                    )
                    for edge in self._accepted_relations
                    if edge.subject_id in values or edge.object_id in values
                ]
            )
        values = list(params)[0] if params else []
        if "object_id=any" in lowered:
            wanted = set(values)
            return _Rows(
                [
                    _row_tuple(row, _OBJECT_COLUMNS)
                    for row in self._objects
                    if row.object_id in wanted
                ]
            )
        return _Rows(
            [
                _row_tuple(row, _OBJECT_COLUMNS)
                for row in self._objects
                if _exact_hit(row, values)
            ]
        )


class _Rows:
    def __init__(self, rows: list[tuple]) -> None:
        self._rows = rows

    def fetchall(self) -> list[tuple]:
        return list(self._rows)


class EvaluationStateStorage:
    """Storage stand-in exposing ``connect()`` for ``EntityResolver``."""

    def __init__(self, connection: EvaluationStateConnection) -> None:
        self.connection = connection

    @contextmanager
    def connect(self) -> Iterator[EvaluationStateConnection]:
        yield self.connection


@dataclass(frozen=True)
class D2EvalState:
    """The deterministic D2-A2 evaluation state.

    ``objects`` is the resolver-facing table (24 seeds + 7 declared real-corpus
    rows); ``provenance_support_objects`` records the additional declared rows
    used only by the governed loaders to resolve alias provenance and seed
    relation evidence.
    """

    project_root: Path
    objects: tuple[KnowledgeObject, ...]
    relations: tuple[RelationEdge, ...]
    aliases: tuple[KnowledgeAlias, ...]
    workflow_steps: tuple[WorkflowStep, ...]
    provenance_support_objects: tuple[KnowledgeObject, ...] = field(default_factory=tuple)

    def storage(self) -> EvaluationStateStorage:
        """A fresh deterministic read-only storage for ``EntityResolver``."""

        return EvaluationStateStorage(
            EvaluationStateConnection(
                list(self.objects), list(self.aliases), list(self.relations)
            )
        )

    def object_ids(self) -> frozenset[str]:
        return frozenset(item.object_id for item in self.objects)


PROBE_QUESTION = "Where is *_pid_final.root produced?"


def build_evaluation_state(project_root: Path) -> D2EvalState:
    """Materialize the deterministic D1-compatible D2-A2 evaluation state."""

    root = Path(project_root)
    seeds = seed_knowledge_objects(root)
    declared = declared_source_native_rows()
    support = provenance_support_rows()
    objects = [*seeds, *declared]
    loader_objects = [*objects, *support]
    relations = materialize_seed_relations(
        load_seed_relations(root / "configs" / "seed_relations.yaml"), loader_objects
    )
    aliases = seed_knowledge_aliases(root, loader_objects)
    workflow_steps = seed_workflow_steps(root)
    return D2EvalState(
        project_root=root,
        objects=tuple(objects),
        relations=tuple(relations),
        aliases=tuple(aliases),
        workflow_steps=tuple(workflow_steps),
        provenance_support_objects=tuple(support),
    )


def validate_evaluation_state(state: D2EvalState) -> dict[str, Any]:
    """Validation gate over the built evaluation state.

    Returns counts/booleans for every preregistered D2-A2 state expectation
    plus a read-only ``resolve_shadow`` probe.  ``valid`` is the conjunction of
    all gates.
    """

    objects = list(state.objects)
    object_ids = [item.object_id for item in objects]
    by_id = set(object_ids)
    duplicates = sorted({oid for oid in object_ids if object_ids.count(oid) > 1})

    seed_objects = [
        item for item in objects if item.metadata.get("curated_seed") is True
    ]
    declared_rows = [
        item
        for item in objects
        if item.object_id
        in {row.object_id for row in declared_source_native_rows()}
    ]

    required_counts = {
        object_id: object_ids.count(object_id) for object_id in REQUIRED_CANONICAL_IDS
    }
    required_ok = all(count == 1 for count in required_counts.values())

    seed_roles_ok = all(
        item.metadata.get("identity_role") in ALLOWED_IDENTITY_ROLES
        for item in seed_objects
    )
    observed_roles = sorted(
        {
            item.metadata.get("identity_role")
            for item in objects
            if item.metadata.get("identity_role") is not None
        }
    )
    roles_value_ok = set(observed_roles) <= set(ALLOWED_IDENTITY_ROLES)

    accepted_aliases = [
        alias for alias in state.aliases if str(alias.review_status) == "accepted"
    ]
    corrective_aliases = [
        alias for alias in accepted_aliases if alias.correction_message
    ]
    true_aliases = [
        alias for alias in accepted_aliases if not alias.correction_message
    ]
    missing_alias_targets = sorted(
        {alias.target_object_id for alias in state.aliases if alias.target_object_id not in by_id}
    )

    accepted_relations = [
        edge for edge in state.relations if str(edge.review_status) == "accepted"
    ]
    pending_relations = [
        edge for edge in state.relations if str(edge.review_status) == "pending"
    ]

    storage = state.storage()
    resolver = EntityResolver(storage)
    with storage.connect() as connection:
        canonical_ids = sorted(
            item.object_id
            for item in objects
            if item.metadata.get("identity_role") == "canonical"
        )
        features = resolver._load_canonical_relation_features(
            connection, canonical_ids
        )
    poca_features = tuple(features.get(POCA_WORKFLOW_ID, ()))
    poca_features_ok = all(feature in poca_features for feature in POCA_EXPECTED_FEATURES)

    probe_plan: dict[str, Any] = {
        "intent": "terminology_resolution",
        "target_repositories": [
            "pandaroot",
            "restgas_determination",
            "luminosityfit",
        ],
        "resolved_versions": {},
        "analysis_diagnostics": {
            "analyzer_accepted_semantic_delta": {"symbols": [], "concepts": []}
        },
    }
    try:
        resolver.resolve_shadow(PROBE_QUESTION, probe_plan)
        probe_ok = True
        probe_error: str | None = None
    except Exception as exc:  # pragma: no cover - the probe must never raise
        probe_ok = False
        probe_error = f"{type(exc).__name__}: {exc}"

    report: dict[str, Any] = {
        "state_type": "deterministic_in_memory_d1_compatible",
        "object_count": len(objects),
        "expected_object_count": EXPECTED_OBJECT_COUNT,
        "object_count_ok": len(objects) == EXPECTED_OBJECT_COUNT,
        "seed_object_count": len(seed_objects),
        "declared_source_native_count": len(declared_rows),
        "duplicate_object_ids": duplicates,
        "no_duplicate_object_ids": not duplicates,
        "required_canonical_ids": required_counts,
        "required_canonical_ids_ok": required_ok,
        "identity_role_values": observed_roles,
        "identity_roles_valid": seed_roles_ok and roles_value_ok,
        "accepted_alias_count": len(accepted_aliases),
        "expected_accepted_alias_count": EXPECTED_ACCEPTED_ALIAS_COUNT,
        "corrective_alias_present": len(corrective_aliases) == 1,
        "true_identity_alias_present": len(true_aliases) == 1,
        "alias_targets_missing": missing_alias_targets,
        "no_missing_alias_targets": not missing_alias_targets,
        "accepted_relation_count": len(accepted_relations),
        "expected_accepted_relation_count": EXPECTED_ACCEPTED_RELATION_COUNT,
        "pending_relation_count": len(pending_relations),
        "workflow_step_count": len(state.workflow_steps),
        "expected_workflow_step_count": EXPECTED_WORKFLOW_STEP_COUNT,
        "first_pass_poca_features": list(poca_features),
        "first_pass_poca_features_ok": poca_features_ok,
        "resolver_probe_question": PROBE_QUESTION,
        "resolver_probe_ok": probe_ok,
        "resolver_probe_error": probe_error,
        "read_only_statements": len(storage.connection.statements),
    }
    report["valid"] = bool(
        report["object_count_ok"]
        and report["no_duplicate_object_ids"]
        and required_ok
        and report["identity_roles_valid"]
        and report["accepted_alias_count"] == EXPECTED_ACCEPTED_ALIAS_COUNT
        and report["corrective_alias_present"]
        and report["true_identity_alias_present"]
        and report["no_missing_alias_targets"]
        and report["accepted_relation_count"] == EXPECTED_ACCEPTED_RELATION_COUNT
        and report["pending_relation_count"] == 0
        and report["workflow_step_count"] == EXPECTED_WORKFLOW_STEP_COUNT
        and poca_features_ok
        and probe_ok
    )
    return report
