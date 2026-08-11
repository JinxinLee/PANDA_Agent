"""Serve the PANDA QA API only on a loopback interface."""

from __future__ import annotations

import argparse
import ipaddress
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

from panda_agent.api import create_app


def _loopback_host(host: str) -> bool:
    if host.casefold() == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the local PANDA QA API on loopback only")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[3])
    return parser.parse_args()


def _configure_panda_agent_logging() -> None:
    level_name = os.getenv("PANDA_LOG_LEVEL", "INFO").upper()
    level = logging.getLevelName(level_name)
    if not isinstance(level, int):
        raise ValueError("PANDA_LOG_LEVEL must be a valid logging level")
    logger = logging.getLogger("panda_agent")
    logger.setLevel(level)
    logger.propagate = False
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.handlers[:] = [handler]


def main() -> None:
    load_dotenv()
    args = parse_args()
    if not _loopback_host(args.host):
        raise SystemExit("panda-qa-api accepts loopback hosts only")
    _configure_panda_agent_logging()
    import uvicorn

    uvicorn.run(create_app(args.project_root), host=args.host, port=args.port, workers=1)


if __name__ == "__main__":
    main()
