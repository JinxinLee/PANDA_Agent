"""One-command launcher for the local PANDA QA Web UI."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import threading
import time
from typing import Any, Callable
from urllib.request import urlopen
import webbrowser

from dotenv import load_dotenv

from panda_agent.api import create_app
from panda_agent.cli.api import _configure_panda_agent_logging
from panda_agent.runtime import verify_runtime


def _start_dependencies(
    project_root: Path,
    *,
    runner: Callable[..., Any] = subprocess.run,
) -> None:
    try:
        runner(
            ["docker", "compose", "up", "-d", "--wait", "postgres", "qdrant"],
            cwd=project_root,
            check=True,
        )
    except FileNotFoundError as exc:
        raise SystemExit("Docker is required to start the PANDA QA UI") from exc
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"PostgreSQL/Qdrant startup failed with exit code {exc.returncode}") from exc


def _open_when_live(
    ui_url: str,
    *,
    opener: Callable[..., Any] = webbrowser.open,
    probe: Callable[..., Any] = urlopen,
    timeout_seconds: float = 30.0,
) -> bool:
    health_url = ui_url.removesuffix("/ui") + "/health/live"
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            with probe(health_url, timeout=1) as response:
                if response.status == 200:
                    opener(ui_url, new=2)
                    return True
        except OSError:
            time.sleep(0.1)
    return False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Start PostgreSQL, Qdrant, and the local PANDA QA Web UI"
    )
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[3],
    )
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()
    project_root = args.project_root.resolve()
    if not 1 <= args.port <= 65535:
        raise SystemExit("--port must be between 1 and 65535")

    _start_dependencies(project_root)
    runtime = verify_runtime(project_root=project_root)
    if not runtime["valid"]:
        status = runtime.get("runtime_status", "invalid")
        raise SystemExit(
            f"PANDA runtime is not ready ({status}); restore and register the Knowledge Bundle first"
        )

    ui_url = f"http://127.0.0.1:{args.port}/ui"
    if not args.no_browser:
        threading.Thread(
            target=_open_when_live,
            args=(ui_url,),
            name="panda-qa-ui-browser",
            daemon=True,
        ).start()

    _configure_panda_agent_logging()
    print(f"PANDA QA UI: {ui_url}")
    print("Press Ctrl+C to stop the UI server; PostgreSQL and Qdrant remain running.")
    import uvicorn

    uvicorn.run(create_app(project_root), host="127.0.0.1", port=args.port, workers=1)


if __name__ == "__main__":
    main()
