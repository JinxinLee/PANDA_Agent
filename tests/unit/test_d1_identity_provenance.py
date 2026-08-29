"""D1-A1 focused T0: identity roles, SAME_AS contract, curated relation provenance."""

from __future__ import annotations

import unittest
from pathlib import Path

from panda_agent.config import (
    load_relation_ontology,
    load_seed_relations,
    SeedObjectConfig,
    SeedRelationConfig,
)
from panda_agent.ingestion import (
    materialize_seed_relations,
    seed_knowledge_objects,
    validate_identity_relations,
)
from panda_agent.models import KnowledgeObject, ReviewStatus, SourceLocator

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = REPO_ROOT / "configs"

RESTGAS_VERSION = "restgas_determination@11f1edc49dcbaeb61d707491a6d3bbec390fcd42"
PANDAROOT_VERSION = "pandaroot@18c09e91100db27867ded30e708b4dae95bd8357"
LUMINOSITYFIT_VERSION = "luminosityfit@ddd83dcd1a74093bf48ef259a2849a67f9413f32"
KARAVDINA_VERSION = "karavdina_2015@422421852c5a046c24e894a77b9380988ec8172914e9b30b055a100145c07a2b"
PFLUEGER_VERSION = "pflueger_2017@1b6ec987fc1430be085f2a7ba631d634f6580115ff0a90dff090dfcba5e990f3"
SPHINX_VERSION = "pandaroot_sphinx_2023_08_25_dev@5bff86c0f3a1102c80f3466a8ca0a63db48c0c7d8f142a78a0849219d7844f87"

KARAVDINA_EVIDENCE = [
    "object.b1739b9b6e502cda6a154406",
    "object.30cf42f607e2c228dfe125fd",
    "object.7cd1257841fc461a4e1e5390",
]
PFLUEGER_EVIDENCE = [
    "object.faaced8bd5058b2a19ba9528",
    "object.86b7c9f862f3e5c328823444",
    "object.6f688277a08ed2f236ae74df",
]
SPHINX_EVIDENCE = ["object.79b75480980719256f8b7937"]

MODEL_CONCEPT_ID = "concept.luminosityfit.luminosity_fit_model"
MODEL_CONCEPT_SUPERSEDED_ID = "concept.luminosityfit.differential_luminosity_model"


def _object(
    object_id: str,
    *,
    object_type: str = "data_product",
    source_id: str = "curated_panda_domain",
    source_version: str | None = None,
    path: str | None = None,
    locator: SourceLocator | None = None,
    identity_role: str | None = None,
    chunk_parent: bool = False,
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
        canonical_locator=object_id,
        chunk_parent_id=object_id if chunk_parent else None,
        metadata={"identity_role": identity_role} if identity_role else {},
    )


def _relation(
    subject_id: str,
    predicate: str,
    object_id: str,
    *,
    review_status: str = "accepted",
    evidence_object_ids: list[str] | None = None,
    evidence_paths: list[str] | None = None,
    evidence_source_ids: list[str] | None = None,
    source_version_ids: list[str] | None = None,
) -> SeedRelationConfig:
    return SeedRelationConfig(
        subject_id=subject_id,
        predicate=predicate,
        object_id=object_id,
        confidence=1.0,
        creation_method="curated",
        review_status=review_status,
        evidence_note="fixture note",
        evidence_object_ids=evidence_object_ids or [],
        evidence_paths=evidence_paths or [],
        evidence_source_ids=evidence_source_ids or [],
        source_version_ids=source_version_ids or [],
    )


def _section_fixture(object_id: str, source_id: str, version: str, page: int) -> KnowledgeObject:
    return _object(
        object_id,
        object_type="thesis_section",
        source_id=source_id,
        source_version=version,
        locator=SourceLocator(pdf_page=page, section_path=[f"section {page}"]),
    )


# Fixture corpus objects covering every declared evidence reference of the
# shipped seed_relations.yaml, with the real locked corpus source versions.
_EVIDENCE_FIXTURES = [
    _object(
        "object.trackq",
        object_type="source_file",
        source_id="pandaroot",
        source_version=PANDAROOT_VERSION,
        path="detectors/lmd/LmdQA/PndLmdTrackQ.cxx",
    ),
    _object(
        "object.reader",
        object_type="source_file",
        source_id="luminosityfit",
        source_version=LUMINOSITYFIT_VERSION,
        path="data/PndLmdCombinedDataReader.cxx",
    ),
    _object(
        "object.factory",
        object_type="source_file",
        source_id="luminosityfit",
        source_version=LUMINOSITYFIT_VERSION,
        path="model/PndLmdModelFactory.cxx",
    ),
    _object(
        "object.effcorr2",
        object_type="source_file",
        source_id="restgas_determination",
        source_version=RESTGAS_VERSION,
        path="macro/target/correction/efficiency_correction_2.C",
    ),
    _object(
        "object.effcorrsteps",
        object_type="source_file",
        source_id="restgas_determination",
        source_version=RESTGAS_VERSION,
        path="macro/target/correction/efficiency_correction_steps.C",
    ),
    _object(
        "object.readme",
        object_type="readme_section",
        source_id="restgas_determination",
        source_version=RESTGAS_VERSION,
        path="README.md",
    ),
    _object(
        "object.targetreadme",
        object_type="readme_section",
        source_id="restgas_determination",
        source_version=RESTGAS_VERSION,
        path="macro/target/README.md",
    ),
    _object(
        "object.anadpm",
        object_type="source_file",
        source_id="restgas_determination",
        source_version=RESTGAS_VERSION,
        path="macro/target/ana_dpm.C",
    ),
    _object(
        "object.pidcomplete",
        object_type="source_file",
        source_id="restgas_determination",
        source_version=RESTGAS_VERSION,
        path="macro/target/pid_complete.C",
    ),
    _object(
        "object.prodaod",
        object_type="source_file",
        source_id="restgas_determination",
        source_version=RESTGAS_VERSION,
        path="macro/target/prod_aod_complete.C",
    ),
    _section_fixture(KARAVDINA_EVIDENCE[0], "karavdina_2015", KARAVDINA_VERSION, 94),
    _section_fixture(KARAVDINA_EVIDENCE[1], "karavdina_2015", KARAVDINA_VERSION, 100),
    _section_fixture(KARAVDINA_EVIDENCE[2], "karavdina_2015", KARAVDINA_VERSION, 104),
    _section_fixture(PFLUEGER_EVIDENCE[0], "pflueger_2017", PFLUEGER_VERSION, 51),
    _section_fixture(PFLUEGER_EVIDENCE[1], "pflueger_2017", PFLUEGER_VERSION, 57),
    _section_fixture(PFLUEGER_EVIDENCE[2], "pflueger_2017", PFLUEGER_VERSION, 65),
    _object(
        SPHINX_EVIDENCE[0],
        object_type="sphinx_page",
        source_id="pandaroot_sphinx_2023_08_25_dev",
        source_version=SPHINX_VERSION,
        locator=SourceLocator(url="https://example.invalid/sphinx/Running/Running.html"),
    ),
]


class OntologyContractTests(unittest.TestCase):
    def test_ontology_has_exactly_one_new_identity_predicate(self) -> None:
        ontology = load_relation_ontology(CONFIG_DIR / "relation_ontology.yaml")
        names = [item.name for item in ontology.predicates]
        self.assertEqual(len(names), 24)
        self.assertEqual(names.count("SAME_AS"), 1)

    def test_same_as_description_excludes_non_identity_semantics(self) -> None:
        ontology = load_relation_ontology(CONFIG_DIR / "relation_ontology.yaml")
        description = next(
            item.description for item in ontology.predicates if item.name == "SAME_AS"
        )
        self.assertIn("co-referential representations of the same entity", description)

    def test_repaired_predicate_descriptions_match_frozen_boundaries(self) -> None:
        ontology = load_relation_ontology(CONFIG_DIR / "relation_ontology.yaml")
        descriptions = {item.name: item.description for item in ontology.predicates}
        self.assertIn("structural containment is not production", descriptions["PRODUCES"])
        self.assertIn("file pattern", descriptions["PRODUCES_INPUT_FOR"])
        self.assertIn("configuration-like object", descriptions["PARAMETERIZES"])
        self.assertIn("how a process runs", descriptions["CONFIGURES"])
        self.assertIn("correction concept, factor, or object", descriptions["CORRECTS"])


class IdentityRoleTests(unittest.TestCase):
    def test_seed_objects_carry_explicit_identity_roles(self) -> None:
        objects = seed_knowledge_objects(REPO_ROOT)
        roles = {item.metadata.get("identity_role") for item in objects}
        self.assertEqual(roles, {"canonical", "source_native"})
        canonical = [
            item for item in objects if item.metadata.get("identity_role") == "canonical"
        ]
        source_native = [
            item for item in objects if item.metadata.get("identity_role") == "source_native"
        ]
        self.assertEqual(len(canonical), 22)
        self.assertEqual(len(source_native), 2)
        self.assertTrue(
            all(item.object_type == "repository_version" for item in source_native)
        )

    def test_identity_role_is_never_inferred(self) -> None:
        from panda_agent.ingestion import _identity_role

        unmarked = _object("object.plain", path=None)
        self.assertIsNone(_identity_role(unmarked))
        marked = _object("object.canon", identity_role="canonical")
        self.assertEqual(_identity_role(marked), "canonical")

    def test_seed_identity_role_config_validates_values(self) -> None:
        with self.assertRaises(ValueError):
            SeedObjectConfig(
                object_id="object.bad",
                object_type="workflow",
                title="bad",
                text="bad",
                identity_role="similarity_guess",
            )


class SeedRelationMaterializationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.objects = [
            *seed_knowledge_objects(REPO_ROOT),
            *_EVIDENCE_FIXTURES,
        ]
        self.edges = materialize_seed_relations(
            load_seed_relations(CONFIG_DIR / "seed_relations.yaml"), self.objects
        )

    def _accepted(self) -> list:
        return [edge for edge in self.edges if edge.review_status is ReviewStatus.ACCEPTED]

    def test_review_status_is_taken_from_the_seed_config(self) -> None:
        accepted = self._accepted()
        pending = [edge for edge in self.edges if edge.review_status is ReviewStatus.PENDING]
        self.assertEqual(len(accepted), 16)
        self.assertEqual(len(pending), 0)

    def test_accepted_relations_carry_machine_traceable_provenance(self) -> None:
        accepted = self._accepted()
        for edge in accepted:
            self.assertTrue(edge.source_version_ids, f"missing version scope: {edge.edge_id}")
            self.assertTrue(edge.evidence_object_ids, f"missing evidence objects: {edge.edge_id}")
        self.assertFalse(
            any(
                set(edge.metadata) == {"evidence_note"}
                for edge in accepted
            ),
            "prose-only accepted relations must no longer exist",
        )

    def test_accepted_versions_are_grounded_in_evidence_versions(self) -> None:
        by_pair = {
            (edge.subject_id, edge.predicate, edge.object_id): edge for edge in self._accepted()
        }
        expectations = {
            ("workflow.pandaroot.lmd_reconstruction", "PRODUCES", "data_product.pandaroot.lumi_trks_qa"): [PANDAROOT_VERSION],
            ("data_product.pandaroot.lumi_trks_qa", "PRODUCES_INPUT_FOR", "subsystem.luminosityfit.panda_data_io"): [LUMINOSITYFIT_VERSION],
            ("paper.karavdina_2015.chapter_4", "THEORETICAL_BASIS_FOR", "workflow.pandaroot.lmd_reconstruction"): [KARAVDINA_VERSION],
            ("paper.pflueger_2017.chapter_4", "FORMALIZES", MODEL_CONCEPT_ID): [PFLUEGER_VERSION],
            ("subsystem.luminosityfit.model_and_fit", "IMPLEMENTS", MODEL_CONCEPT_ID): [LUMINOSITYFIT_VERSION],
            ("document.pandaroot_sphinx_2023_08_25_dev", "OPERATIONALLY_DOCUMENTS", "workflow.pandaroot.generic"): [SPHINX_VERSION],
            ("workflow.restgas.first_pass_poca", "CONSUMES", "data_product.restgas.pid_root"): [RESTGAS_VERSION],
            ("workflow.restgas.first_pass_poca", "PRODUCES", "data_product.restgas.boost_root"): [RESTGAS_VERSION],
        }
        for key, expected in expectations.items():
            self.assertEqual(by_pair[key].source_version_ids, expected, str(key))
        forked = by_pair[
            ("repository.restgas_determination.oct19", "FORKED_FROM", "repository.pandaroot.oct19")
        ]
        self.assertEqual(
            forked.source_version_ids, [RESTGAS_VERSION, PANDAROOT_VERSION]
        )
        self.assertFalse(
            any(
                edge.source_version_ids == ["curated_panda_domain@1.0"]
                for edge in self._accepted()
            ),
            "endpoint curated versions must never replace evidence grounding",
        )

    def test_boost_root_containment_is_structural_not_produces(self) -> None:
        self.assertFalse(
            any(
                edge.subject_id == "data_product.restgas.boost_root"
                and edge.object_id == "data_product.restgas.event_poca"
                for edge in self.edges
            ),
            "boost_root -> event_poca must not remain a PRODUCES edge",
        )
        event_poca = next(
            item
            for item in self.objects
            if item.object_id == "data_product.restgas.event_poca"
        )
        self.assertEqual(
            event_poca.parent_object_id, "data_product.restgas.boost_root"
        )

    def test_pflueger_model_concept_pattern_is_represented(self) -> None:
        """D1-A2 pattern: theory/document FORMALIZES the domain concept, and
        the implementing subsystem IMPLEMENTS it; the D1-A1 direct
        paper-to-subsystem stand-in edge is no longer authoritative. The
        concept semantics were corrected in D1-A2R1: the model describes the
        elastic antiproton-proton scattering angular distribution, not
        photon-pair kinematics."""
        seed_ids = {item.object_id for item in self.objects}
        self.assertIn(MODEL_CONCEPT_ID, seed_ids)
        self.assertNotIn(
            MODEL_CONCEPT_SUPERSEDED_ID,
            seed_ids,
            "the erroneous pre-repair curated identity must not survive as a "
            "second canonical concept",
        )
        concept = next(
            item
            for item in self.objects
            if item.object_id == MODEL_CONCEPT_ID
        )
        self.assertEqual(concept.metadata.get("identity_role"), "canonical")
        self.assertEqual(concept.title, "Luminosity fit model")
        self.assertNotIn("photon", concept.text.lower())
        self.assertIn("elastic", concept.text.lower())
        self.assertIn("luminosity", concept.text.lower())
        self.assertIn("angular distribution", concept.text.lower())
        self.assertIn("acceptance", concept.text.lower())
        self.assertIn("resolution", concept.text.lower())
        by_pair = {
            (edge.subject_id, edge.predicate, edge.object_id): edge
            for edge in self.edges
        }
        formalizes = by_pair[
            (
                "paper.pflueger_2017.chapter_4",
                "FORMALIZES",
                MODEL_CONCEPT_ID,
            )
        ]
        implements = by_pair[
            (
                "subsystem.luminosityfit.model_and_fit",
                "IMPLEMENTS",
                MODEL_CONCEPT_ID,
            )
        ]
        self.assertEqual(formalizes.review_status, ReviewStatus.ACCEPTED)
        self.assertEqual(implements.review_status, ReviewStatus.ACCEPTED)
        self.assertEqual(
            sorted(formalizes.evidence_object_ids), sorted(PFLUEGER_EVIDENCE)
        )
        self.assertEqual(
            implements.evidence_object_ids, ["object.factory"]
        )
        self.assertNotIn(
            (
                "paper.pflueger_2017.chapter_4",
                "THEORETICAL_BASIS_FOR",
                "subsystem.luminosityfit.model_and_fit",
            ),
            by_pair,
            "the superseded direct paper-to-subsystem edge must not remain",
        )
        self.assertNotIn(
            MODEL_CONCEPT_SUPERSEDED_ID,
            {edge.object_id for edge in self.edges}
            | {edge.subject_id for edge in self.edges},
            "the superseded concept ID must not remain on any seed relation",
        )

    def test_first_pass_poca_data_flow_pattern_is_represented(self) -> None:
        """D1-A2 pattern: the materialized first-pass POCA process carries the
        process-centric data flow, replacing the pending product-to-product
        shortcut; containment stays structural via parent_object_id."""
        by_pair = {
            (edge.subject_id, edge.predicate, edge.object_id): edge
            for edge in self.edges
        }
        consumes = by_pair[
            ("workflow.restgas.first_pass_poca", "CONSUMES", "data_product.restgas.pid_root")
        ]
        produces = by_pair[
            ("workflow.restgas.first_pass_poca", "PRODUCES", "data_product.restgas.boost_root")
        ]
        self.assertEqual(consumes.review_status, ReviewStatus.ACCEPTED)
        self.assertEqual(produces.review_status, ReviewStatus.ACCEPTED)
        self.assertNotIn(
            (
                "data_product.restgas.pid_root",
                "PRODUCES_INPUT_FOR",
                "data_product.restgas.event_poca",
            ),
            by_pair,
            "the obsolete pending product-to-product edge must be gone",
        )
        self.assertNotIn(
            (
                "workflow.restgas_profile_reconstruction",
                "PRODUCES",
                "data_product.restgas.boost_root",
            ),
            by_pair,
            "the superseded workflow-level stand-in edge must be gone",
        )
        event_poca = next(
            item
            for item in self.objects
            if item.object_id == "data_product.restgas.event_poca"
        )
        self.assertEqual(
            event_poca.parent_object_id, "data_product.restgas.boost_root"
        )

    def test_seed_workflow_step_records_stage_decomposition(self) -> None:
        from panda_agent.ingestion import seed_workflow_steps

        steps = seed_workflow_steps(REPO_ROOT)
        self.assertEqual(len(steps), 1)
        step = steps[0]
        self.assertEqual(step.workflow_id, "workflow.restgas_profile_reconstruction")
        self.assertEqual(step.step_id, "workflow.restgas.first_pass_poca")
        self.assertEqual(step.entrypoint_object_id, "workflow.restgas.first_pass_poca")
        self.assertEqual(step.inputs, ["data_product.restgas.pid_root"])
        self.assertEqual(step.outputs, ["data_product.restgas.boost_root"])


class EvidenceResolutionTests(unittest.TestCase):
    def _materialize(self, relations: list[SeedRelationConfig], objects: list[KnowledgeObject]):
        config = type("SeedRelationsFixture", (), {"relations": relations})()
        return materialize_seed_relations(config, objects)

    def test_accepted_relation_fails_on_one_unresolved_declared_path(self) -> None:
        objects = [
            _object(
                "object.readme",
                object_type="readme_section",
                source_id="restgas_determination",
                source_version=RESTGAS_VERSION,
                path="README.md",
            ),
            _object("object.seed", source_id="restgas_determination", source_version=RESTGAS_VERSION),
        ]
        with self.assertRaises(ValueError) as context:
            self._materialize(
                [
                    _relation(
                        "object.readme",
                        "PARAMETERIZES",
                        "object.seed",
                        evidence_paths=["README.md", "docs/missing.md"],
                        evidence_source_ids=["restgas_determination"],
                    )
                ],
                objects,
            )
        self.assertIn("docs/missing.md", str(context.exception))

    def test_pending_relation_records_individual_unresolved_paths(self) -> None:
        objects = [
            _object(
                "object.readme",
                object_type="readme_section",
                source_id="restgas_determination",
                source_version=RESTGAS_VERSION,
                path="README.md",
            ),
            _object("object.seed", source_id="restgas_determination", source_version=RESTGAS_VERSION),
        ]
        edges = self._materialize(
            [
                _relation(
                    "object.readme",
                    "PARAMETERIZES",
                    "object.seed",
                    review_status="pending",
                    evidence_paths=["README.md", "docs/missing.md"],
                    evidence_source_ids=["restgas_determination"],
                )
            ],
            objects,
        )
        self.assertEqual(edges[0].metadata["unresolved_evidence_paths"], ["docs/missing.md"])

    def test_whole_file_object_is_preferred_over_functions_and_chunks(self) -> None:
        objects = [
            _object(
                "object.file",
                object_type="source_file",
                source_id="restgas_determination",
                source_version=RESTGAS_VERSION,
                path="macro/target/ana_dpm.C",
            ),
            _object(
                "object.func",
                object_type="function",
                source_id="restgas_determination",
                source_version=RESTGAS_VERSION,
                path="macro/target/ana_dpm.C",
            ),
            _object(
                "object.funcchunk",
                object_type="function_chunk",
                source_id="restgas_determination",
                source_version=RESTGAS_VERSION,
                path="macro/target/ana_dpm.C",
                chunk_parent=True,
            ),
            _object("object.seed", source_id="restgas_determination", source_version=RESTGAS_VERSION),
        ]
        edges = self._materialize(
            [
                _relation(
                    "object.seed",
                    "PRODUCES",
                    "object.file",
                    evidence_paths=["macro/target/ana_dpm.C"],
                    evidence_source_ids=["restgas_determination"],
                )
            ],
            objects,
        )
        self.assertEqual(edges[0].evidence_object_ids, ["object.file"])

    def test_accepted_evidence_requires_an_inspectable_locator(self) -> None:
        objects = [
            _object("object.opaque1"),
            _object("object.opaque2"),
        ]
        with self.assertRaises(ValueError) as context:
            self._materialize(
                [
                    _relation(
                        "object.opaque1",
                        "PRODUCES",
                        "object.opaque2",
                        evidence_object_ids=["object.opaque2"],
                    )
                ],
                objects,
            )
        self.assertIn("not inspectable", str(context.exception))

    def test_declared_version_outside_corpus_universe_fails(self) -> None:
        objects = [
            _object(
                "object.readme",
                object_type="readme_section",
                source_id="restgas_determination",
                source_version=RESTGAS_VERSION,
                path="README.md",
            ),
            _object("object.seed", source_id="restgas_determination", source_version=RESTGAS_VERSION),
        ]
        with self.assertRaises(ValueError) as context:
            self._materialize(
                [
                    _relation(
                        "object.readme",
                        "PARAMETERIZES",
                        "object.seed",
                        evidence_paths=["README.md"],
                        source_version_ids=["restgas_determination@nonexistent"],
                    )
                ],
                objects,
            )
        self.assertIn("version universe", str(context.exception))

    def test_declared_scope_must_cover_evidence_versions(self) -> None:
        objects = [
            _object(
                "object.readme",
                object_type="readme_section",
                source_id="restgas_determination",
                source_version=RESTGAS_VERSION,
                path="README.md",
            ),
            _object(
                "object.pandaroot",
                object_type="source_file",
                source_id="pandaroot",
                source_version=PANDAROOT_VERSION,
                path="pgenerators/Target/PndTargetGenerator.cxx",
            ),
            _object("object.seed", source_id="restgas_determination", source_version=RESTGAS_VERSION),
        ]
        with self.assertRaises(ValueError) as context:
            self._materialize(
                [
                    _relation(
                        "object.readme",
                        "PARAMETERIZES",
                        "object.seed",
                        evidence_paths=["README.md"],
                        source_version_ids=[PANDAROOT_VERSION],
                    )
                ],
                objects,
            )
        self.assertIn("do not cover", str(context.exception))

    def test_multi_version_evidence_derives_unique_sorted_set(self) -> None:
        objects = [
            _object(
                "object.trackq",
                object_type="source_file",
                source_id="pandaroot",
                source_version=PANDAROOT_VERSION,
                path="detectors/lmd/LmdQA/PndLmdTrackQ.cxx",
            ),
            _object(
                "object.reader",
                object_type="source_file",
                source_id="luminosityfit",
                source_version=LUMINOSITYFIT_VERSION,
                path="data/PndLmdCombinedDataReader.cxx",
            ),
            _object("object.seed"),
        ]
        edges = self._materialize(
            [
                _relation(
                    "object.seed",
                    "PRODUCES_INPUT_FOR",
                    "object.trackq",
                    evidence_object_ids=["object.trackq", "object.reader"],
                )
            ],
            objects,
        )
        self.assertEqual(
            edges[0].source_version_ids,
            sorted([PANDAROOT_VERSION, LUMINOSITYFIT_VERSION]),
        )


class SameAsContractTests(unittest.TestCase):
    def _materialize(self, relations: list[SeedRelationConfig], objects: list[KnowledgeObject]):
        config = type("SeedRelationsFixture", (), {"relations": relations})()
        return materialize_seed_relations(config, objects)

    def test_case_a_orients_noncanonical_to_canonical(self) -> None:
        objects = [
            _object("object.canonical", identity_role="canonical"),
            _object("object.plain"),
        ]
        edges = self._materialize(
            [
                _relation(
                    "object.canonical",
                    "SAME_AS",
                    "object.plain",
                    evidence_object_ids=["object.plain"],
                )
            ],
            objects,
        )
        self.assertEqual(edges[0].subject_id, "object.plain")
        self.assertEqual(edges[0].object_id, "object.canonical")

    def test_case_b_uses_lexicographic_order_without_canonical(self) -> None:
        objects = [_object("object.zzz"), _object("object.aaa")]
        edges = self._materialize(
            [
                _relation(
                    "object.zzz",
                    "SAME_AS",
                    "object.aaa",
                    evidence_object_ids=["object.aaa"],
                )
            ],
            objects,
        )
        self.assertEqual(edges[0].subject_id, "object.aaa")
        self.assertEqual(edges[0].object_id, "object.zzz")

    def test_case_c_rejects_accepted_dual_canonical_edge(self) -> None:
        objects = [
            _object("object.canon1", identity_role="canonical"),
            _object("object.canon2", identity_role="canonical"),
        ]
        with self.assertRaises(ValueError):
            self._materialize(
                [
                    _relation(
                        "object.canon1",
                        "SAME_AS",
                        "object.canon2",
                        evidence_object_ids=["object.canon1"],
                    )
                ],
                objects,
            )

    def test_case_c_pending_dual_canonical_stays_declared_and_non_authoritative(
        self,
    ) -> None:
        objects = [
            _object("object.canon1", identity_role="canonical"),
            _object("object.canon2", identity_role="canonical"),
        ]
        edges = self._materialize(
            [
                _relation(
                    "object.canon1",
                    "SAME_AS",
                    "object.canon2",
                    review_status="pending",
                    evidence_object_ids=["object.canon1"],
                )
            ],
            objects,
        )
        self.assertEqual(edges[0].review_status, ReviewStatus.PENDING)
        self.assertEqual(
            (edges[0].subject_id, edges[0].object_id), ("object.canon1", "object.canon2")
        )

    def test_accepted_edge_requires_existing_endpoints(self) -> None:
        objects = [_object("object.canonical", identity_role="canonical")]
        with self.assertRaises(ValueError):
            self._materialize(
                [_relation("object.canonical", "SAME_AS", "object.missing")], objects
            )

    def test_validate_identity_relations_rejects_duplicate_pairs(self) -> None:
        objects = [_object("object.aaa"), _object("object.zzz")]
        edges = self._materialize(
            [
                _relation(
                    "object.aaa",
                    "SAME_AS",
                    "object.zzz",
                    evidence_object_ids=["object.aaa"],
                ),
                _relation(
                    "object.zzz",
                    "SAME_AS",
                    "object.aaa",
                    evidence_object_ids=["object.aaa"],
                ),
            ],
            objects,
        )
        with self.assertRaises(ValueError):
            validate_identity_relations(objects, edges)

    def test_same_as_endpoint_evidence_is_corpus_level_identity_evidence(self) -> None:
        """Identity assertions are record-level claims: reviewed endpoints are
        the auditable referents, so the inspectable-locator gate for
        source-grounded semantic relations does not apply to SAME_AS."""
        objects = [
            _object("object.canonical", identity_role="canonical"),
            _object("object.plain"),
        ]
        edges = self._materialize(
            [
                _relation(
                    "object.plain",
                    "SAME_AS",
                    "object.canonical",
                    evidence_object_ids=["object.canonical"],
                )
            ],
            objects,
        )
        self.assertEqual(edges[0].review_status, ReviewStatus.ACCEPTED)
        self.assertEqual(edges[0].evidence_object_ids, ["object.canonical"])

    def test_semantic_similarity_alone_creates_no_identity_edge(self) -> None:
        objects = [
            _object(
                "object.detector resolution",
                path="docs/detector_resolution.md",
            ),
            _object(
                "object.detector  resolution",
                path="docs/detector_resolution.md",
            ),
        ]
        edges = self._materialize(
            [
                _relation(
                    "object.detector resolution",
                    "THEORETICAL_BASIS_FOR",
                    "object.detector  resolution",
                    evidence_object_ids=["object.detector resolution"],
                )
            ],
            objects,
        )
        self.assertFalse(any(edge.predicate == "SAME_AS" for edge in edges))
        validate_identity_relations(objects, edges)


if __name__ == "__main__":
    unittest.main()
