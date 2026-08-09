"""CLI for M1 source snapshot and offline verification."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from panda_agent.config import load_corpora
from panda_agent.source import build_manifest, migrate_manifest_contract, verify_manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Snapshot or verify the fixed PANDA corpus")
    parser.add_argument("command", choices=("snapshot", "verify", "migrate-contract"))
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[3])
    args = parser.parse_args()
    root = args.project_root.resolve()
    manifest_path = root / "data" / "manifests" / "source_manifest.json"
    config = load_corpora(root / "configs" / "corpora.yaml")
    if args.command == "snapshot":
        result = build_manifest(config, root)
        output = {
            "corpus_locked": result["corpus_locked"],
            "repositories": len(result["repositories"]),
            "papers": len(result["papers"]),
            "web_pages": sum(item["page_count"] for item in result["web_documents"]),
        }
    elif args.command == "migrate-contract":
        output = migrate_manifest_contract(manifest_path, root, config)
    else:
        output = verify_manifest(manifest_path, root, config)
    print(json.dumps(output, ensure_ascii=False, indent=2))
    if not output["corpus_locked"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
