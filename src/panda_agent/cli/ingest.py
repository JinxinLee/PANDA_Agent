from __future__ import annotations

import argparse
from pathlib import Path

from panda_agent.ingestion import ingest


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse the locked PANDA corpus")
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[3])
    args = parser.parse_args()
    print(ingest(args.project_root.resolve()).model_dump_json(indent=2))


if __name__ == "__main__": main()
