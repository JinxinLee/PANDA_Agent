"""CLI for trusted local PANDA knowledge bundles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from dotenv import load_dotenv

from panda_agent.kb_bundle import export_bundle, inspect_bundle, restore_bundle, verify_bundle


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="PANDA local knowledge bundle")
    parser.add_argument("command", choices=("export", "inspect", "restore", "verify"))
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[3])
    args = parser.parse_args()
    if args.command == "export":
        result = export_bundle(args.bundle, project_root=args.project_root)
        output: object = result.model_dump(mode="json")
    elif args.command == "inspect":
        output = inspect_bundle(args.bundle)
    elif args.command == "restore":
        result = restore_bundle(args.bundle, project_root=args.project_root)
        output = result.model_dump(mode="json")
    else:
        output = verify_bundle(args.bundle, project_root=args.project_root)
    print(json.dumps(output, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
