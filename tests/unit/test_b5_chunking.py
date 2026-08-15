from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from panda_agent.chunking import ChunkingPolicy
from panda_agent.ingestion import (
    expand_embedding_chunks,
    parse_cmake,
    parse_cpp,
    parse_generic,
    parse_python,
)
from panda_agent.models import AuthorityLevel, KnowledgeObject, SourceLocator


class ChunkingPolicyTests(unittest.TestCase):
    def test_below_limit_structural_object_remains_intact(self) -> None:
        policy = ChunkingPolicy()
        text = "void configure_tracker() { configure_geometry(); }"
        item = KnowledgeObject(
            object_id="object.b5-structural",
            object_type="function",
            source_id="repo",
            source_version_id="repo@sha",
            title="configure_tracker",
            text=text,
            authority_level=AuthorityLevel.PRIMARY,
            locator=SourceLocator(path="tracking.cc", symbol="configure_tracker", start_line=4, end_line=4),
            canonical_locator="tracking.cc:configure_tracker:4",
            token_count=policy.token_count(text),
        )

        self.assertTrue(policy.embedding_input_is_valid(item.title, item.text, item.token_count))
        self.assertEqual(expand_embedding_chunks([item], policy=policy), [item])

    def test_oversized_object_creates_valid_source_ordered_children(self) -> None:
        policy = ChunkingPolicy(max_embedding_input_chars=100)
        text = "\n\n".join(
            f"block {number} alpha beta gamma delta epsilon zeta eta theta iota"
            for number in range(8)
        )
        parent = KnowledgeObject(
            object_id="object.b5-large", object_type="guide", source_id="repo", source_version_id="repo@sha",
            title="guide", text=text, authority_level=AuthorityLevel.PRIMARY,
            locator=SourceLocator(path="guide.md", start_line=1, end_line=20), canonical_locator="guide.md",
        )
        result = expand_embedding_chunks([parent], policy=policy)
        children = result[1:]
        self.assertFalse(result[0].embedding_eligible)
        self.assertGreater(len(children), 1)
        self.assertTrue(all(policy.embedding_input_is_valid(item.title, item.text, item.token_count) for item in children))
        self.assertEqual("".join(item.text.replace("\n", "") for item in children), text.replace("\n", ""))
        self.assertTrue(all(item.parent_object_id == parent.object_id for item in children))

    def test_pathological_line_uses_deterministic_fallback(self) -> None:
        policy = ChunkingPolicy(max_embedding_input_chars=80)
        text = "word " * 80
        parent = KnowledgeObject(
            object_id="object.b5-line", object_type="script", source_id="repo", source_version_id="repo@sha",
            title="script", text=text, authority_level=AuthorityLevel.PRIMARY,
            locator=SourceLocator(path="run.sh", start_line=1, end_line=1), canonical_locator="run.sh",
        )
        first = expand_embedding_chunks([parent], policy=policy)
        second = expand_embedding_chunks([parent], policy=policy)
        self.assertEqual(first, second)
        self.assertTrue(all(item.embedding_eligible for item in first[1:]))
        self.assertTrue(all(item.locator.start_line == 1 and item.locator.end_line == 1 for item in first[1:]))

    def test_python_module_gap_covers_imports_and_constants(self) -> None:
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "module.py"
            path.write_text("import os\nVALUE = 3\n\ndef work():\n    return VALUE\n", encoding="utf-8")
            objects, _, _ = parse_python(path, "module.py", "repo", "repo@sha")
        gaps = [item for item in objects if item.metadata.get("region_kind") == "python_module_gap"]
        self.assertEqual(len(gaps), 1)
        self.assertIn("VALUE = 3", gaps[0].text)

    def test_cmake_gap_covers_configuration_outside_targets(self) -> None:
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "CMakeLists.txt"
            path.write_text("set(FLAG ON)\nadd_library(core a.cc)\noption(ENABLE_X \"x\" ON)\n", encoding="utf-8")
            objects, _, _ = parse_cmake(path, "CMakeLists.txt", "repo", "repo@sha")
        gaps = [item for item in objects if item.metadata.get("region_kind") == "cmake_configuration_gap"]
        self.assertEqual(len(gaps), 2)
        self.assertIn("set(FLAG ON)", gaps[0].text)

    def test_cpp_gap_covers_include_and_global_declaration(self) -> None:
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "source.cc"
            path.write_text("#include <vector>\nint global = 1;\nvoid work() {}\n", encoding="utf-8")
            objects, _ = parse_cpp(path, "source.cc", "repo", "repo@sha")
        gaps = [item for item in objects if item.metadata.get("region_kind") == "cpp_top_level_gap"]
        self.assertEqual(len(gaps), 1)
        self.assertIn("int global", gaps[0].text)

    def test_input_limit_includes_title_and_newline(self) -> None:
        policy = ChunkingPolicy(max_embedding_input_chars=20)
        self.assertFalse(policy.embedding_input_is_valid("long-title", "short body", 10))

    def test_token_lower_boundary_is_not_eligible(self) -> None:
        policy = ChunkingPolicy()
        self.assertFalse(policy.embedding_input_is_valid("t", "one two", 2))

    def test_token_upper_boundary_is_not_eligible(self) -> None:
        policy = ChunkingPolicy(max_tokens=3)
        self.assertFalse(policy.embedding_input_is_valid("t", "one two three four", 4))

    def test_oversized_source_file_remains_nonsearchable_parent(self) -> None:
        policy = ChunkingPolicy(max_embedding_input_chars=80)
        source = KnowledgeObject(
            object_id="object.b5-file", object_type="source_file", source_id="repo", source_version_id="repo@sha",
            title="file.cc", text="word " * 100, authority_level=AuthorityLevel.PRIMARY,
            locator=SourceLocator(path="file.cc", start_line=1, end_line=1), canonical_locator="file.cc",
        )
        result = expand_embedding_chunks([source], policy=policy)
        self.assertEqual(len(result), 1)
        self.assertFalse(result[0].embedding_eligible)

    def test_derived_chunk_locator_is_contained_by_parent(self) -> None:
        policy = ChunkingPolicy(max_embedding_input_chars=80)
        parent = KnowledgeObject(
            object_id="object.b5-locator", object_type="guide", source_id="repo", source_version_id="repo@sha",
            title="guide", text=("one two three four five six seven eight nine ten\n" * 12),
            authority_level=AuthorityLevel.PRIMARY,
            locator=SourceLocator(path="guide.md", start_line=10, end_line=21), canonical_locator="guide.md",
        )
        for child in expand_embedding_chunks([parent], policy=policy)[1:]:
            self.assertGreaterEqual(child.locator.start_line or 0, 10)
            self.assertLessEqual(child.locator.end_line or 0, 21)

    def test_generic_text_paragraph_regions_cover_configuration(self) -> None:
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "settings.yaml"
            path.write_text("option_a: true\n\ntimeout_ms: 5000\nretries: 3\n", encoding="utf-8")
            objects, _, _ = parse_generic(path, "settings.yaml", "repo", "repo@sha", full_source=True)
        regions = [item for item in objects if item.metadata.get("region_kind") == "generic_text_block"]
        self.assertEqual(len(regions), 2)
        self.assertTrue(all(item.parent_object_id == objects[0].object_id for item in regions))
        self.assertIn("timeout_ms: 5000", regions[1].text)

    def test_full_source_locator_does_not_count_trailing_newline(self) -> None:
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "module.py"
            path.write_text("import os\nVALUE = 3\n", encoding="utf-8")
            objects, _, _ = parse_python(path, "module.py", "repo", "repo@sha", full_source=True)
        self.assertEqual(objects[0].locator.end_line, 2)

    def test_no_sliding_overlap_between_hard_fallback_chunks(self) -> None:
        policy = ChunkingPolicy(max_embedding_input_chars=120)
        text = " ".join("word" for _ in range(80))
        parent = KnowledgeObject(
            object_id="object.b5-overlap", object_type="script", source_id="repo", source_version_id="repo@sha",
            title="script", text=text, authority_level=AuthorityLevel.PRIMARY,
            locator=SourceLocator(path="run.sh", start_line=1, end_line=1), canonical_locator="run.sh",
        )
        children = expand_embedding_chunks([parent], policy=policy)[1:]
        ordered = "".join(item.text for item in children)
        self.assertEqual(ordered, text)

    def test_readme_section_hierarchy_survives_chunking(self) -> None:
        policy = ChunkingPolicy(max_embedding_input_chars=120)
        section = KnowledgeObject(
            object_id="object.b5-readme", object_type="readme_section", source_id="repo", source_version_id="repo@sha",
            title="Setup", text=("alpha beta gamma delta epsilon zeta eta theta\n" * 12),
            authority_level=AuthorityLevel.OPERATIONAL,
            locator=SourceLocator(path="README.md", start_line=3, end_line=14, section_path=["Guide", "Setup"]),
            canonical_locator="README.md#Setup:3",
        )
        result = expand_embedding_chunks([section], policy=policy)
        self.assertFalse(result[0].embedding_eligible)
        self.assertTrue(all(child.locator.section_path == ["Guide", "Setup"] for child in result[1:]))
        self.assertTrue(all(child.parent_object_id == section.object_id for child in result[1:]))

    def test_pdf_page_provenance_remains_honest_in_chunks(self) -> None:
        policy = ChunkingPolicy(max_embedding_input_chars=100)
        page = KnowledgeObject(
            object_id="object.b5-pdf", object_type="thesis_section", source_id="doc", source_version_id="doc@sha",
            title="thesis PDF page 4", text=("one two three four five six seven eight nine ten\n" * 12),
            authority_level=AuthorityLevel.PRIMARY,
            locator=SourceLocator(path="thesis.pdf", pdf_page=4, section_path=["Introduction"]),
            canonical_locator="pdf:doc:page:4",
        )
        for child in expand_embedding_chunks([page], policy=policy)[1:]:
            self.assertEqual(child.locator.pdf_page, 4)
            self.assertIsNone(child.locator.start_line)
