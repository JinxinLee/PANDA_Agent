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


def _object(
    object_id: str,
    *,
    object_type: str = "data_product",
    source_id: str = "curated_panda_domain",
    path: str | None = None,
    identity_role: str | None = None,
) -> KnowledgeObject:
    return KnowledgeObject(
        object_id=object_id,
        object_type=object_type,
        source_id=source_id,
        source_version_id=f"{source_id}@test",
        title=object_id,
        text=object_id,
        authority_level="derived",
        locator=SourceLocator(path=path),
        canonical_locator=object_id,
        metadata={"identity_role": identity_role} if identity_role else {},
    )


def _relation(
    subject_id: str,
    predicate: str,
    object_id: str,
    *,
    review_status: str = "accepted",
    evidence_object_ids: list[str] | None = None,
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
    )


# Fixture corpus objects covering every evidence path declared in the shipped
# seed_relations.yaml, so the real config materializes with full provenance.
_EVIDENCE_FIXTURES = [
    _object(
        "object.trackq",
        object_type="source_file",
        source_id="pandaroot",
        path="detectors/lmd/LmdQA/PndLmdTrackQ.cxx",
    ),
    _object(
        "object.reader",
        object_type="source_file",
        source_id="luminosityfit",
        path="data/PndLmdCombinedDataReader.cxx",
    ),
    _object(
        "object.effcorr2",
        object_type="macro",
        source_id="restgas_determination",
        path="macro/target/correction/efficiency_correction_2.C",
    ),
    _object(
        "object.effcorrsteps",
        object_type="macro",
        source_id="restgas_determination",
        path="macro/target/correction/efficiency_correction_steps.C",
    ),
    _object(
        "object.readme",
        object_type="readme_section",
        source_id="restgas_determination",
        path="README.md",
    ),
    _object(
        "object.targetreadme",
        object_type="readme_section",
        source_id="restgas_determination",
        path="macro/target/README.md",
    ),
    _object(
        "object.anadpm",
        object_type="macro",
        source_id="restgas_determination",
        path="macro/target/ana_dpm.C",
    ),
    _object(
        "object.pidcomplete",
        object_type="macro",
        source_id="restgas_determination",
        path="macro/target/pid_complete.C",
    ),
    _object(
        "object.prodaod",
        object_type="macro",
        source_id="restgas_determination",
        path="macro/target/prod_aod_complete.C",
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
        self.assertEqual(len(canonical), 20)
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

    def test_review_status_is_taken_from_the_seed_config(self) -> None:
        accepted = [edge for edge in self.edges if edge.review_status is ReviewStatus.ACCEPTED]
        pending = [edge for edge in self.edges if edge.review_status is ReviewStatus.PENDING]
        self.assertEqual(len(accepted), 14)
        self.assertEqual(len(pending), 1)
        self.assertEqual(
            (pending[0].subject_id, pending[0].predicate, pending[0].object_id),
            ("data_product.restgas.pid_root", "PRODUCES_INPUT_FOR", "data_product.restgas.event_poca"),
        )

    def test_accepted_relations_carry_machine_traceable_provenance(self) -> None:
        accepted = [edge for edge in self.edges if edge.review_status is ReviewStatus.ACCEPTED]
        for edge in accepted:
            self.assertTrue(
                edge.source_version_ids,
                f"missing version scope: {edge.edge_id}",
            )
            self.assertTrue(
                edge.evidence_object_ids,
                f"missing evidence objects: {edge.edge_id}",
            )
            self.assertTrue(
                all(object_id is not None for object_id in edge.evidence_object_ids)
            )
        self.assertFalse(
            any(
                edge.review_status is ReviewStatus.ACCEPTED
                and set(edge.metadata) == {"evidence_note"}
                for edge in self.edges
            ),
            "prose-only accepted relations must no longer exist",
        )

    def test_pending_relation_keeps_deferred_requirement_and_stays_non_authoritative(
        self,
    ) -> None:
        pending = next(
            edge for edge in self.edges if edge.review_status is ReviewStatus.PENDING
        )
        self.assertIn("deferred_requirement", pending.metadata)
        self.assertIn("D1-A2", pending.metadata["deferred_requirement"])
        # The retrieval graph channel only traverses review_status='accepted'
        # rows, so a pending edge stored here is structurally non-authoritative.
        self.assertNotEqual(pending.review_status, ReviewStatus.ACCEPTED)

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

    def test_pflueger_ambiguity_normalized_to_existing_predicate(self) -> None:
        edge = next(
            edge
            for edge in self.edges
            if edge.subject_id == "paper.pflueger_2017.chapter_4"
        )
        self.assertEqual(edge.predicate, "THEORETICAL_BASIS_FOR")
        self.assertEqual(edge.review_status, ReviewStatus.ACCEPTED)
        self.assertNotEqual(edge.predicate, "FORMALIZES")


class SameAsContractTests(unittest.TestCase):
    def _materialize(self, relations: list[SeedRelationConfig], objects: list[KnowledgeObject]):
        config = type(
            "SeedRelationsFixture",
            (),
            {"relations": relations},
        )()
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

    def test_semantic_similarity_alone_creates_no_identity_edge(self) -> None:
        objects = [
            _object("object.detector resolution"),
            _object("object.detector  resolution"),
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
