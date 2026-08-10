"""CLI for runtime registration and readiness verification."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from dotenv import load_dotenv

from panda_agent.runtime import register_runtime, verify_runtime


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="PANDA local runtime readiness")
    parser.add_argument("command", choices=("register-runtime", "verify"))
    parser.add_argument("--bundle", type=Path)
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[3])
    args = parser.parse_args()
    if args.command == "register-runtime":
        if args.bundle is None:
            parser.error("register-runtime requires --bundle")
        output = register_runtime(args.bundle, project_root=args.project_root)
    else:
        output = verify_runtime(project_root=args.project_root)
    print(json.dumps(output, indent=2, sort_keys=True, default=str))
    if not output["valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
