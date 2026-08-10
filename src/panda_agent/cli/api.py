"""Serve the PANDA QA API only on a loopback interface."""

from __future__ import annotations

import argparse
import ipaddress
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


def main() -> None:
    load_dotenv()
    args = parse_args()
    if not _loopback_host(args.host):
        raise SystemExit("panda-qa-api accepts loopback hosts only")
    import uvicorn

    uvicorn.run(create_app(args.project_root), host=args.host, port=args.port, workers=1)


if __name__ == "__main__":
    main()
