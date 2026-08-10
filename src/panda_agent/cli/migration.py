"""CLI for offline evidence-preserving migration validation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from panda_agent.migration import (
    MigrationError,
    build_suite,
    collect_live_capture,
    collect_live_qa,
    capture_replay,
    compare_evaluators,
    compare_qa_records,
    compare_replays,
    load_records,
    load_suite,
    replay_capture,
    replay_backend,
    score_qa_records,
    write_report,
    write_comparison_artifact,
)


def _root(value: str | None) -> Path:
    return Path(value).resolve() if value else Path.cwd().resolve()


def _canonical_gold(root: Path, value: Path | None) -> Path:
    return (value or root / "evaluation" / "benchmarks" / "v2_6" / "gold_questions.yaml").resolve()


def _json_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise MigrationError(f"expected a JSON object: {path}")
    return value


def _records_map(path: Path) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in load_records(path)}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(prog="panda-qa-migration")
    parser.add_argument("--project-root")
    commands = parser.add_subparsers(dest="command", required=True)

    build = commands.add_parser("build-suite")
    build.add_argument("--canonical-gold", type=Path)
    build.add_argument("--output", type=Path, required=True)

    validate = commands.add_parser("validate-suite")
    validate.add_argument("--suite", type=Path, required=True)
    validate.add_argument("--canonical-gold", type=Path)

    capture = commands.add_parser("capture")
    capture.add_argument("--suite", type=Path, required=True)
    capture_source = capture.add_mutually_exclusive_group(required=True)
    capture_source.add_argument("--cases", type=Path, help="Previously collected fixed original-run plan/vector/channel JSON object.")
    capture_source.add_argument("--live", action="store_true", help="Capture all suite inputs from the original runtime; may call Vertex only during capture.")
    capture.add_argument("--output", type=Path, required=True)

    replay = commands.add_parser("replay")
    replay.add_argument("--suite", type=Path, required=True)
    replay.add_argument("--capture", type=Path, required=True)
    replay.add_argument("--output", type=Path, required=True)
    replay.add_argument("--database-url")
    replay.add_argument("--qdrant-url")
    replay.add_argument("--collection")

    replay_compare = commands.add_parser("compare-replay")
    replay_compare.add_argument("--left", type=Path, required=True)
    replay_compare.add_argument("--right", type=Path, required=True)
    replay_compare.add_argument("--tolerance", type=float, default=1e-6)
    replay_compare.add_argument("--output", type=Path, required=True)

    evaluator = commands.add_parser("compare-evaluator")
    evaluator.add_argument("--canonical-gold", type=Path)
    evaluator.add_argument("--normalized-objects", type=Path, required=True)
    evaluator.add_argument("--portable-catalog", type=Path, required=True)
    evaluator.add_argument("--records", type=Path)
    evaluator.add_argument("--output", type=Path, required=True)

    qa = commands.add_parser("run-qa")
    qa.add_argument("--role", choices=("baseline", "restored"), required=True)
    qa.add_argument("--canonical-gold", type=Path)
    qa.add_argument("--portable-catalog", type=Path, required=True)
    qa_source = qa.add_mutually_exclusive_group(required=True)
    qa_source.add_argument("--records", type=Path, help="Saved live role records; this command re-scores without model calls.")
    qa_source.add_argument("--live", action="store_true", help="Run all ten suite questions in this role environment; this is the only command path that may call Vertex.")
    qa.add_argument("--suite", type=Path)
    qa.add_argument("--database-url")
    qa.add_argument("--qdrant-url")
    qa.add_argument("--collection")
    qa.add_argument("--output", type=Path, required=True)

    qa_compare = commands.add_parser("compare-qa")
    qa_compare.add_argument("--baseline", type=Path, required=True)
    qa_compare.add_argument("--restored", type=Path, required=True)
    qa_compare.add_argument("--output", type=Path, required=True)

    report = commands.add_parser("report")
    report.add_argument("--suite", type=Path, required=True)
    report.add_argument("--output-dir", type=Path, required=True)
    report.add_argument("--replay", type=Path)
    report.add_argument("--evaluator", type=Path)
    report.add_argument("--qa", type=Path)

    args = parser.parse_args()
    load_dotenv()
    root = _root(args.project_root)
    try:
        if args.command == "build-suite":
            value = build_suite(_canonical_gold(root, args.canonical_gold), args.output.resolve())
        elif args.command == "validate-suite":
            value = load_suite(args.suite.resolve(), _canonical_gold(root, args.canonical_gold))
        elif args.command == "capture":
            suite = load_suite(args.suite.resolve())
            cases = collect_live_capture(root, suite) if args.live else _json_object(args.cases.resolve())
            value = capture_replay(suite, cases, args.output.resolve())
        elif args.command == "replay":
            suite = load_suite(args.suite.resolve())
            if any((args.database_url, args.qdrant_url, args.collection)):
                from panda_agent.storage import Storage, StorageSettings
                settings = StorageSettings(
                    database_url=args.database_url or StorageSettings().database_url,
                    qdrant_url=args.qdrant_url or StorageSettings().qdrant_url,
                    collection_name=args.collection or StorageSettings().collection_name,
                )
                value = replay_backend(suite, args.capture.resolve(), args.output.resolve(), storage=Storage(settings))
            else:
                value = replay_capture(suite, args.capture.resolve(), args.output.resolve())
        elif args.command == "compare-replay":
            value = compare_replays(args.left.resolve(), args.right.resolve(), args.tolerance)
            write_comparison_artifact(args.output.resolve(), value)
        elif args.command == "compare-evaluator":
            records = _records_map(args.records.resolve()) if args.records else None
            value = compare_evaluators(
                _canonical_gold(root, args.canonical_gold), args.normalized_objects.resolve(), args.portable_catalog.resolve(),
                records=records,
            )
            write_comparison_artifact(args.output.resolve(), value)
        elif args.command == "run-qa":
            if args.live:
                if args.suite is None:
                    raise MigrationError("--live requires --suite")
                from panda_agent.storage import Storage, StorageSettings
                defaults = StorageSettings.from_env()
                storage = Storage(StorageSettings(database_url=args.database_url or defaults.database_url, qdrant_url=args.qdrant_url or defaults.qdrant_url, collection_name=args.collection or defaults.collection_name))
                raw_records = collect_live_qa(root, load_suite(args.suite.resolve()), args.role, _canonical_gold(root, args.canonical_gold), storage=storage)
            else:
                raw_records = load_records(args.records.resolve())
            value = {
                "role": args.role,
                "model_calls": (sum(int(item.get("model_calls", 0)) for item in raw_records) if args.live else 0),
                "records": score_qa_records(_canonical_gold(root, args.canonical_gold), args.portable_catalog.resolve(), raw_records),
            }
            if args.output.exists():
                raise MigrationError(f"refusing to overwrite artifact: {args.output}")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        elif args.command == "compare-qa":
            baseline_value = _json_object(args.baseline.resolve())
            restored_value = _json_object(args.restored.resolve())
            if baseline_value.get("role") != "baseline" or restored_value.get("role") != "restored":
                raise MigrationError("compare-qa needs baseline and restored role receipts")
            value = compare_qa_records(baseline_value.get("records", []), restored_value.get("records", []))
            write_comparison_artifact(args.output.resolve(), value)
        else:
            suite = load_suite(args.suite.resolve())
            replay_value = _json_object(args.replay.resolve()) if args.replay else None
            evaluator_value = _json_object(args.evaluator.resolve()) if args.evaluator else None
            qa_value = _json_object(args.qa.resolve()) if args.qa else None
            json_path, markdown_path = write_report(args.output_dir.resolve(), suite=suite, replay=replay_value, evaluator=evaluator_value, qa=qa_value)
            value = {"json": str(json_path), "markdown": str(markdown_path)}
    except (FileNotFoundError, ValueError, MigrationError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    print(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
