"""D1-A3 focused T0: structural integrity, persistence compatibility, and the
tiny read-only structured-knowledge smokes for the representative D1 batch."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from panda_agent.config import load_seed_objects, load_seed_relations
from panda_agent.ingestion import (
    materialize_seed_relations,
    seed_knowledge_objects,
    seed_workflow_steps,
    validate_ingestion_contract,
    validate_parent_integrity,
    validate_workflow_integrity,
    write_jsonl,
)
from panda_agent.models import (
    KnowledgeObject,
    RelationEdge,
    ReviewStatus,
    SourceLocator,
    WorkflowStep,
)
from panda_agent.storage import load_jsonl, load_structured_objects

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = REPO_ROOT / "configs"

RESTGAS_VERSION = "restgas_determination@11f1edc49dcbaeb61d707491a6d3bbec390fcd42"
PANDAROOT_VERSION = "pandaroot@18c09e91100db27867ded30e708b4dae95bd8357"
LUMINOSITYFIT_VERSION = "luminosityfit@ddd83dcd1a74093bf48ef259a2849a67f9413f32"
KARAVDINA_VERSION = "karavdina_2015@422421852c5a046c24e894a77b9380988ec8172914e9b30b055a100145c07a2b"
PFLUEGER_VERSION = "pflueger_2017@1b6ec987fc1430be085f2a7ba631d634f6580115ff0a90dff090dfcba5e990f3"
SPHINX_VERSION = "pandaroot_sphinx_2023_08_25_dev@5bff86c0f3a1102c80f3466a8ca0a63db48c0c7d8f142a78a0849219d7844f87"

MODEL_CONCEPT_ID = "concept.luminosityfit.luminosity_fit_model"


def _object(
    object_id: str,
    *,
    object_type: str = "data_product",
    source_id: str = "curated_panda_domain",
    source_version: str | None = None,
    path: str | None = None,
    locator: SourceLocator | None = None,
    identity_role: str | None = None,
    parent_object_id: str | None = None,
) -> KnowledgeObject:
    return KnowledgeObject(
        object_id=object_id,
        object_type=object_type,
        source_id=source_id,
        source_version_id=source_version or f"{source_id}@test",
        title=object_id,
        text=object_id,
        authority_level="derived",
        locator=locator or SourceLocator(path=path),
        parent_object_id=parent_object_id,
        canonical_locator=object_id,
        metadata={"identity_role": identity_role} if identity_role else {},
    )


def _curated_step(**overrides) -> WorkflowStep:
    step = WorkflowStep(
        workflow_id="workflow.restgas_profile_reconstruction",
        step_id="workflow.restgas.first_pass_poca",
        name="First-pass POCA analysis",
        entrypoint_object_id="workflow.restgas.first_pass_poca",
        inputs=["data_product.restgas.pid_root"],
        outputs=["data_product.restgas.boost_root"],
        metadata={"curated_seed": True},
    )
    return step.model_copy(update=overrides)


def _accepted(subject_id: str, predicate: str, object_id: str) -> RelationEdge:
    return RelationEdge(
        edge_id=f"edge.{subject_id}.{predicate}.{object_id}",
        subject_id=subject_id,
        predicate=predicate,
        object_id=object_id,
        source_version_ids=["v1"],
        confidence=1.0,
        creation_method="curated",
        review_status="accepted",
        evidence_object_ids=[subject_id],
        metadata={},
    )


def _representative_objects() -> list[KnowledgeObject]:
    """Real seed objects plus the corpus-evidence fixtures for path resolution."""
    return [
        *seed_knowledge_objects(REPO_ROOT),
        _object("object.trackq", object_type="source_file", source_id="pandaroot",
                source_version=PANDAROOT_VERSION, path="detectors/lmd/LmdQA/PndLmdTrackQ.cxx"),
        _object("object.reader", object_type="source_file", source_id="luminosityfit",
                source_version=LUMINOSITYFIT_VERSION, path="data/PndLmdCombinedDataReader.cxx"),
        _object("object.factory", object_type="source_file", source_id="luminosityfit",
                source_version=LUMINOSITYFIT_VERSION, path="model/PndLmdModelFactory.cxx"),
        _object("object.effcorr2", object_type="source_file", source_id="restgas_determination",
                source_version=RESTGAS_VERSION, path="macro/target/correction/efficiency_correction_2.C"),
        _object("object.effcorrsteps", object_type="source_file", source_id="restgas_determination",
                source_version=RESTGAS_VERSION, path="macro/target/correction/efficiency_correction_steps.C"),
        _object("object.readme", object_type="readme_section", source_id="restgas_determination",
                source_version=RESTGAS_VERSION, path="README.md"),
        _object("object.targetreadme", object_type="readme_section", source_id="restgas_determination",
                source_version=RESTGAS_VERSION, path="macro/target/README.md"),
        _object("object.anadpm", object_type="source_file", source_id="restgas_determination",
                source_version=RESTGAS_VERSION, path="macro/target/ana_dpm.C"),
        _object("object.pidcomplete", object_type="source_file", source_id="restgas_determination",
                source_version=RESTGAS_VERSION, path="macro/target/pid_complete.C"),
        _object("object.prodaod", object_type="source_file", source_id="restgas_determination",
                source_version=RESTGAS_VERSION, path="macro/target/prod_aod_complete.C"),
        _object("object.b1739b9b6e502cda6a154406", object_type="thesis_section",
                source_id="karavdina_2015", source_version=KARAVDINA_VERSION,
                locator=SourceLocator(pdf_page=94, section_path=["Chapter 7"])),
        _object("object.30cf42f607e2c228dfe125fd", object_type="thesis_section",
                source_id="karavdina_2015", source_version=KARAVDINA_VERSION,
                locator=SourceLocator(pdf_page=100, section_path=["Chapter 7"])),
        _object("object.7cd1257841fc461a4e1e5390", object_type="thesis_section",
                source_id="karavdina_2015", source_version=KARAVDINA_VERSION,
                locator=SourceLocator(pdf_page=104, section_path=["Chapter 7"])),
        _object("object.faaced8bd5058b2a19ba9528", object_type="thesis_section",
                source_id="pflueger_2017", source_version=PFLUEGER_VERSION,
                locator=SourceLocator(pdf_page=51, section_path=["Chapter 4"])),
        _object("object.86b7c9f862f3e5c328823444", object_type="thesis_section",
                source_id="pflueger_2017", source_version=PFLUEGER_VERSION,
                locator=SourceLocator(pdf_page=57, section_path=["Chapter 4"])),
        _object("object.6f688277a08ed2f236ae74df", object_type="thesis_section",
                source_id="pflueger_2017", source_version=PFLUEGER_VERSION,
                locator=SourceLocator(pdf_page=65, section_path=["Chapter 4"])),
        _object("object.79b75480980719256f8b7937", object_type="sphinx_page",
                source_id="pandaroot_sphinx_2023_08_25_dev", source_version=SPHINX_VERSION,
                locator=SourceLocator(url="https://example.invalid/sphinx/Running/Running.html")),
    ]


def _materialized():
    objects = _representative_objects()
    edges = materialize_seed_relations(
        load_seed_relations(CONFIG_DIR / "seed_relations.yaml"), objects
    )
    steps = seed_workflow_steps(REPO_ROOT)
    return objects, edges, steps


class ParentIntegrityTests(unittest.TestCase):
    def test_valid_representative_containment_passes(self) -> None:
        objects = [
            _object("data_product.restgas.boost_root"),
            _object(
                "data_product.restgas.event_poca",
                parent_object_id="data_product.restgas.boost_root",
            ),
        ]
        validate_parent_integrity(objects)

    def test_missing_parent_fails(self) -> None:
        with self.assertRaises(ValueError):
            validate_parent_integrity(
                [_object("object.child", parent_object_id="object.missing")]
            )

    def test_self_parent_fails(self) -> None:
        with self.assertRaises(ValueError):
            validate_parent_integrity(
                [_object("object.self", parent_object_id="object.self")]
            )

    def test_parent_cycle_fails(self) -> None:
        with self.assertRaises(ValueError):
            validate_parent_integrity(
                [
                    _object("object.a", parent_object_id="object.b"),
                    _object("object.b", parent_object_id="object.a"),
                ]
            )


class WorkflowIntegrityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.objects = _representative_objects()
        self.relations = materialize_seed_relations(
            load_seed_relations(CONFIG_DIR / "seed_relations.yaml"), self.objects
        )

    def test_valid_representative_step_passes(self) -> None:
        validate_workflow_integrity(
            self.objects, seed_workflow_steps(REPO_ROOT), self.relations
        )

    def test_missing_workflow_object_fails(self) -> None:
        step = _curated_step(workflow_id="workflow.missing")
        with self.assertRaises(ValueError):
            validate_workflow_integrity(self.objects, [step], self.relations)

    def test_missing_entrypoint_fails(self) -> None:
        step = _curated_step(entrypoint_object_id="object.missing")
        with self.assertRaises(ValueError):
            validate_workflow_integrity(self.objects, [step], self.relations)

    def test_missing_input_fails(self) -> None:
        step = _curated_step(inputs=["object.missing"])
        with self.assertRaises(ValueError):
            validate_workflow_integrity(self.objects, [step], self.relations)

    def test_missing_output_fails(self) -> None:
        step = _curated_step(outputs=["object.missing"])
        with self.assertRaises(ValueError):
            validate_workflow_integrity(self.objects, [step], self.relations)

    def test_missing_predecessor_step_fails(self) -> None:
        step = _curated_step(predecessor_step_ids=["step.missing"])
        with self.assertRaises(ValueError):
            validate_workflow_integrity(self.objects, [step], self.relations)

    def test_self_predecessor_fails(self) -> None:
        step = _curated_step(predecessor_step_ids=["workflow.restgas.first_pass_poca"])
        with self.assertRaises(ValueError):
            validate_workflow_integrity(self.objects, [step], self.relations)

    def test_contradictory_reciprocal_declarations_fail(self) -> None:
        first = _curated_step(successor_step_ids=["step.second"])
        second = WorkflowStep(
            workflow_id="workflow.restgas_profile_reconstruction",
            step_id="step.second",
            name="second",
            metadata={"curated_seed": True},
            successor_step_ids=["workflow.restgas.first_pass_poca"],
        )
        with self.assertRaises(ValueError):
            validate_workflow_integrity(self.objects, [first, second], self.relations)

    def test_input_without_accepted_consumes_fails(self) -> None:
        step = _curated_step(inputs=["object.unsupported"])
        objects = [*self.objects, _object("object.unsupported")]
        with self.assertRaises(ValueError):
            validate_workflow_integrity(objects, [step], self.relations)

    def test_output_without_accepted_produces_fails(self) -> None:
        step = _curated_step(outputs=["object.unsupported"])
        objects = [*self.objects, _object("object.unsupported")]
        with self.assertRaises(ValueError):
            validate_workflow_integrity(objects, [step], self.relations)

    def test_script_steps_are_not_held_to_the_curated_contract(self) -> None:
        script_step = WorkflowStep(
            workflow_id="script.restgas_determination",
            step_id="object.scriptfile",
            name="script",
            entrypoint_object_id="object.scriptfile",
            inputs=["raw_filename.root"],
        )
        objects = [
            *self.objects,
            _object("object.scriptfile", object_type="python_script"),
        ]
        validate_workflow_integrity(objects, [script_step], self.relations)


class GlobalGovernanceRegressionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.objects, self.edges, self.steps = _materialized()

    def test_expected_seed_governance_counts(self) -> None:
        accepted = [e for e in self.edges if e.review_status is ReviewStatus.ACCEPTED]
        pending = [e for e in self.edges if e.review_status is ReviewStatus.PENDING]
        self.assertEqual(len(seed_knowledge_objects(REPO_ROOT)), 24)
        self.assertEqual(len(accepted), 16)
        self.assertEqual(len(pending), 0)
        self.assertEqual(len(self.steps), 1)

    def test_ingestion_contract_passes_end_to_end(self) -> None:
        validate_ingestion_contract(
            REPO_ROOT, self.objects, (), self.edges, self.steps
        )

    def test_no_duplicate_object_or_edge_ids(self) -> None:
        object_ids = [item.object_id for item in self.objects]
        self.assertEqual(len(object_ids), len(set(object_ids)))
        edge_ids = [edge.edge_id for edge in self.edges]
        self.assertEqual(len(edge_ids), len(set(edge_ids)))

    def test_provenance_regression_holds_globally(self) -> None:
        object_map = {item.object_id: item for item in self.objects}
        accepted = [e for e in self.edges if e.review_status is ReviewStatus.ACCEPTED]
        for edge in accepted:
            self.assertTrue(edge.source_version_ids, edge.edge_id)
            self.assertTrue(edge.evidence_object_ids, edge.edge_id)
            self.assertTrue(
                all(object_id in object_map for object_id in edge.evidence_object_ids),
                edge.edge_id,
            )
            evidence_versions = {
                object_map[object_id].source_version_id
                for object_id in edge.evidence_object_ids
            }
            self.assertTrue(
                evidence_versions.issubset(set(edge.source_version_ids)), edge.edge_id
            )
            self.assertFalse(
                set(edge.metadata) == {"evidence_note"}, edge.edge_id
            )

    def test_canonical_identity_regression(self) -> None:
        seed_objects = seed_knowledge_objects(REPO_ROOT)
        ids = [item.object_id for item in seed_objects]
        self.assertNotIn("concept.luminosityfit.differential_luminosity_model", ids)
        self.assertEqual(ids.count(MODEL_CONCEPT_ID), 1)
        roles = {
            item.metadata.get("identity_role")
            for item in seed_objects
            if item.metadata.get("identity_role") is not None
        }
        self.assertEqual(roles, {"canonical", "source_native"})


class NormalizedArtifactRoundTripTests(unittest.TestCase):
    def test_materialized_records_survive_jsonl_round_trip(self) -> None:
        objects, edges, steps = _materialized()
        with tempfile_directory() as directory:
            object_path = Path(directory) / "knowledge_objects.jsonl"
            relation_path = Path(directory) / "relation_edges.jsonl"
            step_path = Path(directory) / "workflow_steps.jsonl"
            write_jsonl(object_path, (item.model_dump(mode="json") for item in objects))
            write_jsonl(relation_path, (item.model_dump(mode="json") for item in edges))
            write_jsonl(step_path, (item.model_dump(mode="json") for item in steps))
            reloaded_objects = [
                KnowledgeObject.model_validate(item) for item in load_jsonl(object_path)
            ]
            reloaded_edges = [
                RelationEdge.model_validate(item) for item in load_jsonl(relation_path)
            ]
            reloaded_steps = [
                WorkflowStep.model_validate(item) for item in load_jsonl(step_path)
            ]
        by_id = {item.object_id: item for item in reloaded_objects}
        self.assertEqual(len(by_id), len(objects))
        concept = by_id[MODEL_CONCEPT_ID]
        self.assertEqual(concept.metadata.get("identity_role"), "canonical")
        event_poca = by_id["data_product.restgas.event_poca"]
        # Normalized artifacts carry the model field; the metadata parent
        # representation is created at the SQL boundary (A1R1 contract).
        self.assertEqual(
            event_poca.parent_object_id, "data_product.restgas.boost_root"
        )
        self.assertEqual(len(reloaded_edges), len(edges))
        for edge in reloaded_edges:
            self.assertTrue(edge.source_version_ids)
            self.assertTrue(edge.evidence_object_ids)
            self.assertIn(edge.review_status, (ReviewStatus.ACCEPTED, ReviewStatus.PENDING))
        self.assertEqual(len(reloaded_steps), len(steps))
        self.assertEqual(
            reloaded_steps[0].entrypoint_object_id, "workflow.restgas.first_pass_poca"
        )
        self.assertEqual(reloaded_steps[0].inputs, ["data_product.restgas.pid_root"])
        self.assertEqual(reloaded_steps[0].outputs, ["data_product.restgas.boost_root"])


def tempfile_directory():
    import tempfile

    return tempfile.TemporaryDirectory()


class StoragePayloadCompatibilityTests(unittest.TestCase):
    def test_relation_payload_preserves_provenance_fields(self) -> None:
        objects, edges, _ = _materialized()
        edge = edges[0]
        payload = edge.model_dump(mode="json")
        for field in (
            "source_version_ids",
            "evidence_object_ids",
            "review_status",
            "creation_method",
            "metadata",
        ):
            self.assertIn(field, payload)
        self.assertEqual(payload["subject_id"], edge.subject_id)

    def test_workflow_payload_preserves_structure(self) -> None:
        _, _, steps = _materialized()
        payload = steps[0].model_dump(mode="json")
        for field in (
            "workflow_id",
            "step_id",
            "entrypoint_object_id",
            "inputs",
            "outputs",
            "predecessor_step_ids",
            "successor_step_ids",
        ):
            self.assertIn(field, payload)

    def test_load_structured_objects_restores_governed_parent(self) -> None:
        from panda_agent.storage import object_persisted_metadata

        objects, _, _ = _materialized()
        rows = []
        for item in objects:
            record = item.model_dump(mode="json")
            # Simulate the exact persisted row: the SQL table has no parent
            # column, and upsert_objects merges the model parent into the
            # JSONB metadata via object_persisted_metadata.
            metadata = object_persisted_metadata(
                record["metadata"], record["parent_object_id"]
            )
            rows.append(
                (
                    record["object_id"],
                    record["object_type"],
                    record["source_id"],
                    record["source_version_id"],
                    record["title"],
                    record["text"],
                    record["authority_level"],
                    record["locator"],
                    metadata,
                    record["canonical_locator"],
                    record["token_count"],
                    record["embedding_eligible"],
                )
            )

        class _FakeCursor:
            def __init__(self, rows):
                self._rows = rows

            def fetchall(self):
                return self._rows

        class _FakeConnection:
            def __init__(self, rows):
                self._rows = rows

            def execute(self, query, *args):
                return _FakeCursor(self._rows)

        restored = load_structured_objects(_FakeConnection(rows))
        by_id = {record["object_id"]: record for record in restored}
        event_poca = by_id["data_product.restgas.event_poca"]
        self.assertEqual(
            event_poca["parent_object_id"], "data_product.restgas.boost_root"
        )
        self.assertEqual(
            event_poca["metadata"]["identity_role"], "canonical"
        )
        standalone = by_id["workflow.restgas_profile_reconstruction"]
        self.assertIsNone(standalone["parent_object_id"])


class IndexCompatibilityTests(unittest.TestCase):
    def test_curated_object_types_are_schema_allowed(self) -> None:
        import yaml

        schema = yaml.safe_load((CONFIG_DIR / "knowledge_schema.yaml").open(encoding="utf-8"))
        allowed = {t for group in schema["object_types"].values() for t in group}
        for object_type in ("physics_concept", "workflow", "workflow_step", "root_tree"):
            self.assertIn(object_type, allowed)

    def test_embedding_input_construction_is_valid_for_curated_records(self) -> None:
        from panda_agent.indexing import embedding_eligible, embedding_input

        objects, _, _ = _materialized()
        concept = next(
            item for item in objects if item.object_id == MODEL_CONCEPT_ID
        ).model_dump(mode="json")
        text = embedding_input(concept)
        self.assertIn(concept["title"], text)
        self.assertTrue(embedding_eligible(concept))


class RepresentativeSmokeTests(unittest.TestCase):
    """Tiny read-only structured-knowledge smoke over the representative D1
    graph (normalized in-memory records; no ranking, no QA, no model)."""

    def setUp(self) -> None:
        self.objects, self.edges, self.steps = _materialized()

    def test_smoke_a_luminosityfit_concept_neighborhood(self) -> None:
        by_pair = {
            (edge.subject_id, edge.predicate, edge.object_id): edge
            for edge in self.edges
            if edge.review_status is ReviewStatus.ACCEPTED
        }
        formalizes = by_pair[
            ("paper.pflueger_2017.chapter_4", "FORMALIZES", MODEL_CONCEPT_ID)
        ]
        implements = by_pair[
            ("subsystem.luminosityfit.model_and_fit", "IMPLEMENTS", MODEL_CONCEPT_ID)
        ]
        self.assertTrue(formalizes.source_version_ids)
        self.assertTrue(formalizes.evidence_object_ids)
        self.assertTrue(implements.evidence_object_ids)

    def test_smoke_b_poca_workflow_neighborhood(self) -> None:
        by_pair = {
            (edge.subject_id, edge.predicate, edge.object_id): edge
            for edge in self.edges
            if edge.review_status is ReviewStatus.ACCEPTED
        }
        self.assertIn(
            ("workflow.restgas.first_pass_poca", "CONSUMES", "data_product.restgas.pid_root"),
            by_pair,
        )
        self.assertIn(
            ("workflow.restgas.first_pass_poca", "PRODUCES", "data_product.restgas.boost_root"),
            by_pair,
        )
        objects = {item.object_id: item for item in self.objects}
        self.assertEqual(
            objects["data_product.restgas.event_poca"].parent_object_id,
            "data_product.restgas.boost_root",
        )
        self.assertEqual(len(self.steps), 1)
        self.assertEqual(
            self.steps[0].workflow_id, "workflow.restgas_profile_reconstruction"
        )


if __name__ == "__main__":
    unittest.main()
