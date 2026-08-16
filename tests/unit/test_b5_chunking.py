from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from panda_agent.chunking import DEFAULT_CHUNKING_POLICY, ChunkingPolicy
from panda_agent.ingestion import (
    _structure_first_spans,
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

    def test_oversized_source_file_without_children_stays_searchable(self) -> None:
        policy = ChunkingPolicy(max_embedding_input_chars=80)
        source = KnowledgeObject(
            object_id="object.b5-file", object_type="source_file", source_id="repo", source_version_id="repo@sha",
            title="file.cc", text="word " * 100, authority_level=AuthorityLevel.PRIMARY,
            locator=SourceLocator(path="file.cc", start_line=1, end_line=1), canonical_locator="file.cc",
        )
        result = expand_embedding_chunks([source], policy=policy)
        self.assertFalse(result[0].embedding_eligible)
        self.assertTrue(all(item.embedding_eligible for item in result[1:]))
        self.assertTrue(all(item.parent_object_id == source.object_id for item in result[1:]))

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

    def test_two_submin_paragraphs_merge_into_one_valid_chunk(self) -> None:
        policy = ChunkingPolicy()
        text = "alpha beta gamma delta epsilon\n\nzeta eta theta iota kappa"
        spans, residuals = _structure_first_spans("guide [9999/9999]", text, policy)
        self.assertEqual(spans, [(0, len(text))])
        self.assertEqual(residuals, [])
        self.assertTrue(policy.embedding_input_is_valid("guide [9999/9999]", text))

    def test_multiple_short_lines_merge_into_one_valid_chunk(self) -> None:
        policy = ChunkingPolicy()
        text = "one two\nthree four\nfive six\nseven eight\nnine ten"
        spans, residuals = _structure_first_spans("guide [9999/9999]", text, policy)
        self.assertEqual(spans, [(0, len(text))])
        self.assertEqual(residuals, [])

    def test_trailing_submin_residual_merges_into_previous_chunk(self) -> None:
        policy = ChunkingPolicy(max_embedding_input_chars=200)
        body = "word " * 30
        tail = "tail one two three four"
        text = f"{body}\n\n{tail}"
        spans, residuals = _structure_first_spans("guide [9999/9999]", text, policy)
        self.assertEqual(residuals, [])
        self.assertEqual(len(spans), 1)
        self.assertIn("tail", text[spans[0][0]:spans[0][1]])

    def test_unmergeable_submin_residual_is_reported_not_emitted(self) -> None:
        policy = ChunkingPolicy(max_embedding_input_chars=60, max_tokens=30)
        text = "w1 w2 w3 w4 w5 w6 w7 w8 w9 w10 w11 w12 w13 w14 w15"
        spans, residuals = _structure_first_spans("guide [9999/9999]", text, policy)
        self.assertGreater(len(residuals), 0)
        self.assertGreater(len(spans), 0)
        covered = "".join(text[start:end] for start, end in spans)
        residual_text = "".join(text[start:end] for start, end in residuals)
        self.assertEqual(covered + residual_text, text)
        self.assertTrue(all(
            policy.embedding_input_is_valid("guide [9999/9999]", text[start:end])
            for start, end in spans
        ))

    def test_emitted_children_locators_are_ordered_and_contained(self) -> None:
        policy = ChunkingPolicy(max_embedding_input_chars=200)
        text = "\n\n".join(f"paragraph {index} " + "content " * 15 for index in range(12))
        parent = KnowledgeObject(
            object_id="object.b5-ordered", object_type="guide", source_id="repo", source_version_id="repo@sha",
            title="guide", text=text, authority_level=AuthorityLevel.PRIMARY,
            locator=SourceLocator(path="guide.md", start_line=5, end_line=30), canonical_locator="guide.md",
        )
        children = expand_embedding_chunks([parent], policy=policy)[1:]
        starts = [child.locator.start_line for child in children]
        self.assertEqual(starts, sorted(starts))
        for child in children:
            self.assertGreaterEqual(child.locator.start_line or 0, 5)
            self.assertLessEqual(child.locator.end_line or 0, 30)

    def test_submin_merge_is_deterministic_across_runs(self) -> None:
        policy = ChunkingPolicy()
        text = ("alpha beta gamma\n\nzeta eta theta\n\n"
                + "\n\n".join(f"para {index} " + "word " * 12 for index in range(6)))
        first = _structure_first_spans("guide [9999/9999]", text, policy)
        second = _structure_first_spans("guide [9999/9999]", text, policy)
        self.assertEqual(first, second)

    def test_python_parent_with_children_is_container_not_rechunked(self) -> None:
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "big_module.py"
            body = "# module documentation line\n" * 400
            body += "GLOBAL_VALUE = 42\n\ndef work():\n    return GLOBAL_VALUE\n"
            path.write_text(body, encoding="utf-8")
            objects, _, _ = parse_python(path, "big_module.py", "repo", "repo@sha", full_source=True)
        expanded = expand_embedding_chunks(objects)
        parent = expanded[0]
        self.assertFalse(parent.embedding_eligible)
        module_chunks = [
            item for item in expanded
            if item.object_type == "python_script_chunk" and item.metadata.get("derived_from") == parent.object_id
        ]
        self.assertEqual(module_chunks, [])
        gap_children = [
            item for item in expanded
            if item.parent_object_id == parent.object_id and item.metadata.get("region_kind") == "python_module_gap"
        ]
        self.assertGreater(len(gap_children), 0)

    def test_readme_root_with_sections_is_container_with_preamble_gap(self) -> None:
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "README.md"
            text = "preamble line with meaning\n" * 400
            text += "# Section One\nsection body words\n\n## Sub\nsub body words\n"
            path.write_text(text, encoding="utf-8")
            objects, _, _ = parse_generic(path, "README.md", "repo", "repo@sha", full_source=True)
        expanded = expand_embedding_chunks(objects)
        root = expanded[0]
        self.assertTrue(root.metadata.get("readme_root"))
        self.assertFalse(root.embedding_eligible)
        root_chunks = [
            item for item in expanded
            if item.parent_object_id == root.object_id and item.metadata.get("derived_from") == root.object_id
        ]
        self.assertEqual(root_chunks, [])
        preamble = [item for item in expanded if item.metadata.get("region_kind") == "readme_preamble_gap"]
        self.assertEqual(len(preamble), 1)
        self.assertIn("preamble line with meaning", preamble[0].text)

    def test_generic_long_file_keeps_eligible_children(self) -> None:
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "long.txt"
            text = "\n\n".join(f"documentation paragraph {index} " + "word " * 60 for index in range(30))
            path.write_text(text, encoding="utf-8")
            objects, _, _ = parse_generic(path, "long.txt", "repo", "repo@sha", full_source=True)
        expanded = expand_embedding_chunks(objects)
        eligible_children = [
            item for item in expanded
            if item.parent_object_id == expanded[0].object_id and item.embedding_eligible
        ]
        self.assertGreater(len(eligible_children), 0)
        self.assertTrue(all(
            DEFAULT_CHUNKING_POLICY.embedding_input_is_valid(item.title, item.text, item.token_count)
            for item in eligible_children
        ))

    def test_python_tail_beyond_20000_chars_is_searchable(self) -> None:
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "tail_module.py"
            filler = "# filler documentation line\n" * 750  # > 20000 chars
            text = filler + "TAIL_MARKER_CONSTANT = 12345\n"
            path.write_text(text, encoding="utf-8")
            objects, _, _ = parse_python(path, "tail_module.py", "repo", "repo@sha", full_source=True)
        parent = objects[0]
        self.assertGreater(len(parent.text), 20000)
        expanded = expand_embedding_chunks(objects)
        searchable = [
            item for item in expanded
            if item.embedding_eligible and "TAIL_MARKER_CONSTANT" in item.text
        ]
        self.assertGreater(len(searchable), 0)
        self.assertGreater(searchable[0].locator.start_line or 0, 700)

    def test_generic_tail_beyond_30000_chars_is_searchable(self) -> None:
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "long_data.txt"
            filler = "filler line with words for length\n" * 900  # > 30000 chars
            text = filler + "TAIL_MARKER_SECTION = end-of-file configuration\n"
            path.write_text(text, encoding="utf-8")
            objects, _, _ = parse_generic(path, "long_data.txt", "repo", "repo@sha", full_source=True)
        parent = objects[0]
        self.assertGreater(len(parent.text), 30000)
        expanded = expand_embedding_chunks(objects)
        searchable = [
            item for item in expanded
            if item.embedding_eligible and "TAIL_MARKER_SECTION" in item.text
        ]
        self.assertGreater(len(searchable), 0)
        self.assertGreaterEqual(searchable[0].locator.end_line or 0, 900)

    def test_b5_gaps_do_not_change_relation_resolution(self) -> None:
        from panda_agent.ingestion import RelationResolver
        from panda_agent.models import RelationCandidate, ResolutionStatus
        file_obj = KnowledgeObject(
            object_id="object.rel-file", object_type="source_file", source_id="repo", source_version_id="repo@sha",
            title="src/module.cc", text="x", authority_level=AuthorityLevel.PRIMARY,
            locator=SourceLocator(path="src/module.cc", start_line=1, end_line=1), canonical_locator="src/module.cc",
        )
        function = KnowledgeObject(
            object_id="object.rel-func", object_type="function", source_id="repo", source_version_id="repo@sha",
            title="helper", text="void helper() {}", parent_object_id=file_obj.object_id,
            authority_level=AuthorityLevel.PRIMARY,
            locator=SourceLocator(path="src/module.cc", symbol="helper", start_line=2, end_line=2),
            canonical_locator="src/module.cc:helper:2",
        )
        gap = KnowledgeObject(
            object_id="object.rel-gap", object_type="source_file_chunk", source_id="repo", source_version_id="repo@sha",
            title="src/module.cc [top-level region 1]", text="int global = 1;",
            parent_object_id=file_obj.object_id, authority_level=AuthorityLevel.PRIMARY,
            locator=SourceLocator(path="src/module.cc", start_line=1, end_line=1),
            canonical_locator="src/module.cc:top-level-gap:1:1",
            metadata={"b5_source_gap": True, "region_kind": "cpp_top_level_gap"},
        )
        candidate = RelationCandidate(
            candidate_id="candidate.rel-call", subject_id=function.object_id, predicate="CALLS",
            raw_target="helper", source_version_ids=["repo@sha"], resolution_scope="symbol",
            confidence=0.8,
        )
        without_gap = RelationResolver([file_obj, function]).resolve(candidate)
        with_gap = RelationResolver([file_obj, function, gap]).resolve(candidate)
        self.assertEqual(without_gap, with_gap)
        self.assertEqual(with_gap[0].object_id if with_gap[0] else None, function.object_id)

    def test_b5_gaps_do_not_change_curated_alias_provenance(self) -> None:
        import yaml
        from panda_agent.ingestion import seed_knowledge_aliases
        with TemporaryDirectory() as temporary:
            fake_root = Path(temporary)
            (fake_root / "configs").mkdir()
            (fake_root / "configs" / "aliases.yaml").write_text(
                "schema_version: \"1.0\"\n"
                "aliases:\n"
                "  - alias_text: restgas_profile.txt\n"
                "    target_object_id: configuration.restgas_profile\n"
                "    alias_kind: generic_user_term\n"
                "    source_id: restgas_determination\n"
                "    source_version_id: restgas_determination@11f1edc49dcbaeb61d707491a6d3bbec390fcd42\n"
                "    review_status: accepted\n"
                "    provenance_paths:\n"
                "      - README.md\n"
                "    correction_message: fixture\n",
                encoding="utf-8",
            )
            target = KnowledgeObject(
                object_id="configuration.restgas_profile", object_type="configuration_key",
                source_id="restgas_determination", source_version_id="repo@sha", title="restgas_profile",
                text="restgas profile configuration", authority_level=AuthorityLevel.PRIMARY,
                locator=SourceLocator(path="README.md", start_line=1, end_line=1),
                canonical_locator="configuration.restgas_profile",
            )
            parent = KnowledgeObject(
                object_id="object.alias-parent", object_type="source_file",
                source_id="restgas_determination", source_version_id="repo@sha", title="README.md",
                text="profile docs", authority_level=AuthorityLevel.PRIMARY,
                locator=SourceLocator(path="README.md", start_line=1, end_line=1),
                canonical_locator="README.md",
            )
            gap = KnowledgeObject(
                object_id="object.alias-gap", object_type="source_file_chunk",
                source_id="restgas_determination", source_version_id="repo@sha",
                title="README.md [top-level region 1]", text="int global = 1;",
                parent_object_id=parent.object_id, authority_level=AuthorityLevel.PRIMARY,
                locator=SourceLocator(path="README.md", start_line=1, end_line=1),
                canonical_locator="README.md:top-level-gap:1:1",
                metadata={"b5_source_gap": True, "region_kind": "cpp_top_level_gap"},
            )
            without_gap = seed_knowledge_aliases(fake_root, [target, parent])
            with_gap = seed_knowledge_aliases(fake_root, [target, parent, gap])
        self.assertEqual(
            without_gap[0].provenance_object_ids,
            with_gap[0].provenance_object_ids,
        )
        self.assertNotIn(gap.object_id, with_gap[0].provenance_object_ids)
