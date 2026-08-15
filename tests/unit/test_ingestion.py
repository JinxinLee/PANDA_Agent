from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from panda_agent.ingestion import (
    expand_embedding_chunks,
    materialize_reference_entities,
    parse_cmake,
    parse_cpp,
    parse_generic,
    parse_python,
    parse_shell,
    parse_web,
    resolve_relation_candidates,
    validate_relation_integrity,
)
from panda_agent.models import AuthorityLevel, KnowledgeObject, SourceLocator


def _legacy_chunk_texts(text: str, max_chars: int) -> list[str]:
    """The pre-B4 chunk text algorithm, kept only as a behavior oracle."""
    import re

    paragraphs = re.split(r"\n\s*\n", text)
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        pieces = [paragraph[index:index + max_chars] for index in range(0, len(paragraph), max_chars)] or [""]
        for piece in pieces:
            candidate = (current + "\n\n" + piece).strip() if current else piece
            if current and len(candidate) > max_chars:
                chunks.append(current)
                current = piece
            else:
                current = candidate
    if current:
        chunks.append(current)
    return chunks


def _parent(text: str, locator: SourceLocator) -> KnowledgeObject:
    return KnowledgeObject(
        object_id="object.parent",
        object_type="function",
        source_id="repo",
        source_version_id="repo@sha",
        title="parent",
        text=text,
        authority_level=AuthorityLevel.PRIMARY,
        locator=locator,
        canonical_locator="source.cc:parent:1",
    )


class IngestionTests(unittest.TestCase):
    def test_cpp_symbol_and_root_branch_locator(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "macro.C"
            path.write_text('int run(){ auto x = GetObject("event_poca"); return 0; }', encoding="utf-8")
            objects, relations = parse_cpp(path, "macro.C", "repo", "repo@sha")
            self.assertTrue(any(item.title == "run" for item in objects))
            branch = next(item for item in relations if item.raw_target == "event_poca")
            self.assertEqual(branch.resolution_scope, "root_branch")
            objects.extend(materialize_reference_entities(objects, relations))
            edges, candidates = resolve_relation_candidates(objects, relations)
            validate_relation_integrity(objects, edges)
            resolved_branch = next(item for item in candidates if item.raw_target == "event_poca")
            self.assertEqual(resolved_branch.resolution_status, "resolved")
            self.assertTrue(any(item.predicate == "READS" for item in edges))

    def test_python_function_has_exact_lines(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "run.py"
            path.write_text("def execute():\n    return 'x.root'\n", encoding="utf-8")
            objects, _, workflows = parse_python(path, "run.py", "repo", "repo@sha")
            function = next(item for item in objects if item.title == "execute")
            self.assertEqual(function.locator.start_line, 1)
            self.assertEqual(function.locator.end_line, 2)
            self.assertEqual(workflows[0].inputs, ["x.root"])

    def test_cmake_targets_and_dependencies(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "CMakeLists.txt"
            path.write_text("add_library(Core a.cxx)\ntarget_link_libraries(Core ROOT)\n", encoding="utf-8")
            objects, relations, _ = parse_cmake(path, "CMakeLists.txt", "repo", "repo@sha")
            self.assertIn("Core", [item.title for item in objects])
            self.assertTrue(any(item.predicate == "DEPENDS_ON" for item in relations))

    def test_shell_parser_records_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "run.sh"
            path.write_text("root -l input.root\n", encoding="utf-8")
            objects, _, workflows = parse_shell(path, "run.sh", "repo", "repo@sha")
            self.assertEqual(objects[0].object_type, "shell_script")
            self.assertIn("input.root", workflows[0].inputs)

    def test_file_locators_cover_only_stored_truncated_prefixes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cpp_text = "// x\n" * 5000
            cpp_path = root / "large.cc"
            cpp_path.write_text(cpp_text, encoding="utf-8", newline="")
            cpp_objects, _ = parse_cpp(cpp_path, "large.cc", "repo", "repo@sha")
            cpp_file = cpp_objects[0]
            self.assertEqual(cpp_file.text, cpp_text[:20000])
            self.assertEqual(cpp_file.locator.end_line, 4000)

            python_text = "x = 0\n" * 4000
            python_path = root / "large.py"
            python_path.write_text(python_text, encoding="utf-8", newline="")
            python_objects, _, _ = parse_python(python_path, "large.py", "repo", "repo@sha")
            python_file = python_objects[0]
            self.assertEqual(python_file.text, python_text[:20000])
            self.assertEqual(
                python_file.locator.end_line,
                python_file.text.count("\n", 0, len(python_file.text) - 1) + 1,
            )

            generic_text = "line\n" * 7000
            generic_path = root / "large.txt"
            generic_path.write_text(generic_text, encoding="utf-8", newline="")
            generic_objects, _, _ = parse_generic(generic_path, "large.txt", "repo", "repo@sha")
            generic_file = generic_objects[0]
            self.assertEqual(generic_file.text, generic_text[:30000])
            self.assertEqual(generic_file.locator.end_line, 6000)

    def test_derived_chunks_keep_legacy_text_and_use_ordered_offsets(self) -> None:
        text = "alpha\n\nrepeat\n\nrepeat\n\nomega"
        parent = _parent(text, SourceLocator(path="source.cc", symbol="parent", start_line=10, end_line=16))
        expanded = expand_embedding_chunks([parent], max_chars=8)
        chunks = expanded[1:]
        self.assertEqual([item.text for item in chunks], _legacy_chunk_texts(text, 8))
        self.assertEqual([item.text for item in chunks], ["alpha", "repeat", "repeat", "omega"])
        self.assertEqual(
            [(item.locator.start_line, item.locator.end_line) for item in chunks],
            [(10, 10), (12, 12), (14, 14), (16, 16)],
        )
        self.assertEqual([item.canonical_locator for item in chunks], [
            "source.cc:parent:1:chunk:1",
            "source.cc:parent:1:chunk:2",
            "source.cc:parent:1:chunk:3",
            "source.cc:parent:1:chunk:4",
        ])

    def test_derived_chunk_line_boundaries_handle_blank_crlf_and_midline_splits(self) -> None:
        blank_text = "first\n\n\nsecond\n\n1234567890"
        blank_parent = _parent(blank_text, SourceLocator(path="source.cc", start_line=30, end_line=35))
        blank_chunks = expand_embedding_chunks([blank_parent], max_chars=7)[1:]
        self.assertEqual([item.text for item in blank_chunks], _legacy_chunk_texts(blank_text, 7))
        self.assertEqual(
            [(item.text, item.locator.start_line, item.locator.end_line) for item in blank_chunks],
            [("first", 30, 30), ("second", 33, 33), ("1234567", 35, 35), ("890", 35, 35)],
        )

        crlf_text = "first\r\n\r\nrepeat\r\n\r\nrepeat"
        crlf_parent = _parent(crlf_text, SourceLocator(path="source.cc", start_line=7, end_line=11))
        crlf_chunks = expand_embedding_chunks([crlf_parent], max_chars=6)[1:]
        self.assertEqual([item.text for item in crlf_chunks], _legacy_chunk_texts(crlf_text, 6))
        self.assertEqual(
            [(item.locator.start_line, item.locator.end_line) for item in crlf_chunks],
            [(7, 7), (9, 9), (11, 11)],
        )

        trimmed_text = " \n\nalpha\n\nbeta"
        trimmed_parent = _parent(trimmed_text, SourceLocator(path="source.cc", start_line=40, end_line=44))
        trimmed_chunks = expand_embedding_chunks([trimmed_parent], max_chars=20)[1:]
        self.assertEqual([item.text for item in trimmed_chunks], _legacy_chunk_texts(trimmed_text, 20))
        self.assertEqual(trimmed_chunks[0].text, "alpha\n\nbeta")
        self.assertEqual((trimmed_chunks[0].locator.start_line, trimmed_chunks[0].locator.end_line), (42, 44))

    def test_derived_pdf_chunk_inherits_conservative_page_locator(self) -> None:
        parent = _parent(
            "paragraph one\n\nparagraph two\n\nparagraph three",
            SourceLocator(path="paper.pdf", pdf_page=12, section_path=["Chapter 2"]),
        )
        parent = parent.model_copy(update={"object_type": "thesis_section"})
        chunks = expand_embedding_chunks([parent], max_chars=16)[1:]
        self.assertTrue(chunks)
        for item in chunks:
            self.assertIsNone(item.locator.start_line)
            self.assertIsNone(item.locator.end_line)
            self.assertEqual(item.locator.pdf_page, 12)
            self.assertEqual(item.locator.section_path, ["Chapter 2"])

    def test_readme_heading_paths_are_hierarchical_without_text_changes(self) -> None:
        text = "# Root\nroot text\n## Child\nchild text\n### Grandchild\ngrand text\n## Sibling\nsibling text\n"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "README.md"
            path.write_text(text, encoding="utf-8", newline="")
            objects, _, _ = parse_generic(path, "README.md", "repo", "repo@sha")
        sections = {item.title: item for item in objects if item.parent_object_id}
        self.assertEqual(sections["Root"].text, "# Root\nroot text")
        self.assertEqual(sections["Root"].locator.section_path, ["Root"])
        self.assertEqual(sections["Child"].locator.section_path, ["Root", "Child"])
        self.assertEqual(sections["Grandchild"].locator.section_path, ["Root", "Child", "Grandchild"])
        self.assertEqual(sections["Sibling"].locator.section_path, ["Root", "Sibling"])
        self.assertEqual(sections["Sibling"].canonical_locator, "README.md#Sibling:7")

    def test_sphinx_sections_use_hierarchical_anchor_locators(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project_root = Path(directory)
            html_path = project_root / "data" / "sources" / "web" / "snapshot" / "page.html"
            html_path.parent.mkdir(parents=True)
            html_path.write_text(
                "<html><head><title>Page title</title></head><body>"
                "<section id='root'><h1>Root</h1><p>root text</p>"
                "<section id='child'><h2>Child</h2><p>child text</p></section>"
                "</section><section><h1>Synthetic</h1><p>plain text</p></section></body></html>",
                encoding="utf-8",
            )
            web = {
                "doc_id": "sphinx",
                "snapshot_hash": "snapshot",
                "captured_at": "2026-08-15T00:00:00+00:00",
                "records": [{
                    "content_type": "text/html",
                    "path": "snapshot/page.html",
                    "url": "https://docs.example.test/page.html",
                }],
            }
            objects = parse_web(web, project_root)
        page = next(item for item in objects if item.object_type == "sphinx_page")
        child = next(item for item in objects if item.object_type == "sphinx_section" and item.title == "Child")
        synthetic = next(item for item in objects if item.object_type == "sphinx_section" and item.title == "Synthetic")
        self.assertEqual(page.locator.url, "https://docs.example.test/page.html")
        self.assertEqual(page.locator.section_path, [])
        self.assertEqual(child.text, "Child\nchild text")
        self.assertEqual(child.canonical_locator, "https://docs.example.test/page.html#child")
        self.assertEqual(child.locator.url, "https://docs.example.test/page.html#child")
        self.assertEqual(child.locator.section_path, ["Root", "Child"])
        self.assertEqual(synthetic.canonical_locator, "https://docs.example.test/page.html#section-2")
        self.assertEqual(synthetic.locator.url, "https://docs.example.test/page.html")


if __name__ == "__main__": unittest.main()
