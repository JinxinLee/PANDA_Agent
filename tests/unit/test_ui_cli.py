from __future__ import annotations

import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from panda_agent.cli import ui


class _Response:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


class UICommandTests(unittest.TestCase):
    def test_console_entry_point_is_declared(self) -> None:
        with (Path(__file__).parents[2] / "pyproject.toml").open("rb") as stream:
            scripts = tomllib.load(stream)["project"]["scripts"]
        self.assertEqual(scripts["panda-qa-ui"], "panda_agent.cli.ui:main")

    def test_dependency_start_and_browser_probe(self) -> None:
        runner = Mock()
        root = Path("project").resolve()
        ui._start_dependencies(root, runner=runner)
        runner.assert_called_once_with(
            ["docker", "compose", "up", "-d", "--wait", "postgres", "qdrant"],
            cwd=root,
            check=True,
        )

        opened: list[tuple[str, int]] = []
        self.assertTrue(
            ui._open_when_live(
                "http://127.0.0.1:8000/ui",
                opener=lambda url, new: opened.append((url, new)),
                probe=lambda *_args, **_kwargs: _Response(),
                timeout_seconds=0.1,
            )
        )
        self.assertEqual(opened, [("http://127.0.0.1:8000/ui", 2)])

    def test_main_starts_dependencies_verifies_runtime_and_runs_ui(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            app = object()
            with (
                patch.object(sys, "argv", ["panda-qa-ui", "--project-root", str(root), "--no-browser"]),
                patch("panda_agent.cli.ui._start_dependencies") as start_dependencies,
                patch("panda_agent.cli.ui.verify_runtime", return_value={"valid": True}),
                patch("panda_agent.cli.ui._configure_panda_agent_logging"),
                patch("panda_agent.cli.ui.create_app", return_value=app),
                patch("uvicorn.run") as run,
            ):
                ui.main()

        start_dependencies.assert_called_once_with(root)
        run.assert_called_once_with(app, host="127.0.0.1", port=8000, workers=1)

    def test_main_fails_before_server_when_runtime_is_not_registered(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            with (
                patch.object(sys, "argv", ["panda-qa-ui", "--project-root", str(root), "--no-browser"]),
                patch("panda_agent.cli.ui._start_dependencies"),
                patch(
                    "panda_agent.cli.ui.verify_runtime",
                    return_value={"valid": False, "runtime_status": "not_registered"},
                ),
                patch("uvicorn.run") as run,
            ):
                with self.assertRaisesRegex(SystemExit, "restore and register"):
                    ui.main()
        run.assert_not_called()

    def test_dependency_failure_is_actionable(self) -> None:
        runner = Mock(side_effect=subprocess.CalledProcessError(2, "docker"))
        with self.assertRaisesRegex(SystemExit, "exit code 2"):
            ui._start_dependencies(Path.cwd(), runner=runner)


if __name__ == "__main__":
    unittest.main()
