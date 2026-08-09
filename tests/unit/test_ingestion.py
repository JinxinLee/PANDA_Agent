from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from panda_agent.ingestion import (
    materialize_reference_entities,
    parse_cmake,
    parse_cpp,
    parse_python,
    parse_shell,
    resolve_relation_candidates,
    validate_relation_integrity,
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


if __name__ == "__main__": unittest.main()
