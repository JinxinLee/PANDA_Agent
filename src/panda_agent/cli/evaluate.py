"""Command-line interface for the M6 benchmark."""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path

from dotenv import load_dotenv

from panda_agent.evaluation_runner import (
    default_gold_dataset_path,
    dry_rescore_run,
    import_failure_review_decisions,
    report_evaluation,
    resume_evaluation,
    run_evaluation,
    validate_failure_review,
    validate_gold_dataset,
    write_failure_review,
)
from panda_agent.benchmark_v2 import audit_dataset, build_v2_draft, rescore_run
from panda_agent.candidate import freeze_candidate, verify_candidate
from panda_agent.baseline import package_generalization_baseline, select_stratified_case_ids
from panda_agent.evaluation_finalization import create_stage_receipt


def _root(value: str | None) -> Path:
    return Path(value).resolve() if value else Path.cwd().resolve()


def _parse_replacement_spec(value: str) -> tuple[str, list[str]]:
    """Parse ``RUN_ID:CASE_ID[,CASE_ID]`` without guessing replacement scope."""
    run_id, separator, raw_case_ids = value.partition(":")
    case_ids = [item.strip() for item in raw_case_ids.split(",") if item.strip()]
    if not separator or not run_id or not case_ids:
        raise argparse.ArgumentTypeError(
            "replacement must be RUN_ID:CASE_ID[,CASE_ID], for example run-a:g041,g119"
        )
    if len(case_ids) != len(set(case_ids)):
        raise argparse.ArgumentTypeError("replacement case IDs must be unique within one spec")
    return run_id, case_ids


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    load_dotenv()
    parser = argparse.ArgumentParser(prog="panda-qa-eval")
    parser.add_argument("--project-root")
    commands = parser.add_subparsers(dest="command", required=True)

    validate = commands.add_parser("validate")
    validate.add_argument("--official", action="store_true")
    validate.add_argument("--dataset", type=Path)

    run = commands.add_parser("run")
    run.add_argument("mode", choices=("retrieval", "qa", "full"))
    run.add_argument(
        "--split",
        choices=(
            "dev",
            "challenge",
            "regression",
            "acceptance",
            "novel_dev",
            "novel_validation",
            "novel_holdout",
            "all",
        ),
        required=True,
    )
    run.add_argument("--run-id")
    run.add_argument("--draft", action="store_true")
    run.add_argument("--limit", type=int)
    run.add_argument("--case-id", action="append", dest="case_ids")
    run.add_argument("--dataset", type=Path)
    run.add_argument("--candidate-id")
    run.add_argument("--max-model-calls", type=int)
    run.add_argument("--max-token-usage", type=int)
    run.add_argument("--deadline-minutes", type=float)

    resume = commands.add_parser("resume")
    resume.add_argument("--run-id", required=True)

    report = commands.add_parser("report")
    report.add_argument("--run-id", required=True)

    receipt = commands.add_parser("receipt")
    receipt.add_argument("--run-id", required=True)

    review = commands.add_parser("review")
    review.add_argument("--run-id", required=True)
    review.add_argument("--check", action="store_true")
    review.add_argument("--overwrite", action="store_true")
    review.add_argument("--import-decisions", type=Path)

    build_v2 = commands.add_parser("build-v2")
    audit = commands.add_parser("audit")
    audit.add_argument("--dataset", type=Path, required=True)

    rescore = commands.add_parser("rescore")
    rescore.add_argument("--run-id", required=True)
    rescore.add_argument("--dataset", type=Path, required=True)
    rescore.add_argument("--overrides", type=Path)
    rescore.add_argument("--review-decisions", type=Path)
    rescore.add_argument("--replacement-run")
    rescore.add_argument(
        "--replacement",
        action="append",
        type=_parse_replacement_spec,
        dest="replacement_specs",
        help="Explicit replacement scope: RUN_ID:CASE_ID[,CASE_ID]; may be repeated.",
    )
    rescore.add_argument(
        "--include-case",
        action="append",
        dest="include_case_ids",
        help="Only rescore this source-run case; may be repeated.",
    )
    rescore.add_argument(
        "--exclude-case",
        action="append",
        dest="exclude_case_ids",
        help="Exclude this source-run case from a diagnostic subset; may be repeated.",
    )
    rescore.add_argument("--adjudications", type=Path)
    rescore.add_argument(
        "--dry-run",
        action="store_true",
        help="Recompute immutable records in memory; writes no rescore artifacts and makes no model calls.",
    )

    freeze = commands.add_parser("freeze")
    freeze.add_argument("--candidate-id", required=True)

    verify_candidate_command = commands.add_parser("verify-candidate")
    verify_candidate_command.add_argument("--candidate-id", required=True)

    package_baseline = commands.add_parser("package-baseline")
    package_baseline.add_argument("--baseline-id", required=True)
    package_baseline.add_argument("--historical-run-id", required=True)
    package_baseline.add_argument("--benchmark-retrieval-run-id", required=True)
    package_baseline.add_argument("--novel-retrieval-run-id")
    package_baseline.add_argument("--small-e2e-run-id", required=True)
    package_baseline.add_argument("--selection-manifest", type=Path)
    package_baseline.add_argument("--overwrite", action="store_true")

    select_baseline = commands.add_parser("select-baseline-cases")
    select_baseline.add_argument("--dataset", type=Path)
    select_baseline.add_argument("--retrieval-size", type=int, default=24)
    select_baseline.add_argument("--qa-size", type=int, default=16)

    args = parser.parse_args()
    project_root = _root(args.project_root)
    if args.command == "select-baseline-cases":
        dataset_path = (
            args.dataset.resolve()
            if args.dataset
            else default_gold_dataset_path(project_root)
        )
        try:
            value = {
                "schema_version": "1.0",
                "dataset": (
                    dataset_path.relative_to(project_root).as_posix()
                    if dataset_path.is_relative_to(project_root)
                    else str(dataset_path)
                ),
                "method": "approved English development cases (dev/challenge/regression only); round-robin intents; within each intent round-robin expected_status and split; stable case-id order",
                "retrieval_case_ids": select_stratified_case_ids(
                    dataset_path, args.retrieval_size
                ),
                "qa_case_ids": select_stratified_case_ids(dataset_path, args.qa_size),
            }
        except (FileNotFoundError, ValueError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            raise SystemExit(2) from exc
        print(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2))
        return
    if args.command == "package-baseline":
        try:
            value = package_generalization_baseline(
                project_root,
                baseline_id=args.baseline_id,
                historical_run_id=args.historical_run_id,
                benchmark_retrieval_run_id=args.benchmark_retrieval_run_id,
                novel_retrieval_run_id=args.novel_retrieval_run_id,
                small_e2e_run_id=args.small_e2e_run_id,
                selection_manifest_path=(
                    args.selection_manifest.resolve() if args.selection_manifest else None
                ),
                overwrite=args.overwrite,
            )
        except (FileExistsError, FileNotFoundError, ValueError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            raise SystemExit(2) from exc
        print(value)
        return
    if args.command == "freeze":
        try:
            value = freeze_candidate(project_root, args.candidate_id)
        except (FileNotFoundError, RuntimeError, ValueError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            raise SystemExit(2) from exc
        print(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2))
        return
    if args.command == "verify-candidate":
        try:
            value = verify_candidate(project_root, args.candidate_id)
        except (FileNotFoundError, RuntimeError, ValueError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            raise SystemExit(2) from exc
        print(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2))
        if not value["valid"]:
            raise SystemExit(2)
        return
    if args.command == "build-v2":
        try:
            value = build_v2_draft(project_root)
        except (FileNotFoundError, ValueError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            raise SystemExit(2) from exc
        print(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2))
        return
    if args.command == "audit":
        print(
            json.dumps(
                audit_dataset(project_root, args.dataset.resolve()),
                ensure_ascii=False,
                sort_keys=True,
                indent=2,
            )
        )
        return
    if args.command == "rescore":
        try:
            if args.dry_run:
                if any(
                    value is not None
                    for value in (
                        args.overrides,
                        args.review_decisions,
                        args.replacement_run,
                        args.replacement_specs,
                        args.exclude_case_ids,
                    )
                ):
                    raise ValueError(
                        "--dry-run supports only --dataset, --include-case, and --adjudications"
                    )
                value = dry_rescore_run(
                    project_root,
                    args.run_id,
                    args.dataset.resolve(),
                    case_ids=args.include_case_ids,
                    adjudications_path=(
                        args.adjudications.resolve() if args.adjudications else None
                    ),
                )
            else:
                value = rescore_run(
                    project_root,
                    args.run_id,
                    args.dataset.resolve(),
                    args.overrides.resolve() if args.overrides else None,
                    review_decisions_path=(
                        args.review_decisions.resolve() if args.review_decisions else None
                    ),
                    replacement_run_id=args.replacement_run,
                    adjudications_path=(
                        args.adjudications.resolve() if args.adjudications else None
                    ),
                    replacement_specs=args.replacement_specs,
                    include_case_ids=args.include_case_ids,
                    exclude_case_ids=args.exclude_case_ids,
                )
        except (FileNotFoundError, ValueError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            raise SystemExit(2) from exc
        print(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2))
        return
    if args.command == "validate":
        dataset_path = (
            args.dataset.resolve()
            if args.dataset
            else default_gold_dataset_path(project_root)
        )
        value = validate_gold_dataset(
            project_root,
            dataset_path,
            require_approved=args.official,
        )
        print(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2))
        if args.official and not value["official_ready"]:
            raise SystemExit(2)
        return
    if args.command == "run":
        run_id = args.run_id or f"{args.mode}-{args.split}-{uuid.uuid4()}"
        try:
            path = run_evaluation(
                project_root,
                mode=args.mode,
                split=args.split,
                run_id=run_id,
                allow_draft=args.draft,
                limit=args.limit,
                case_ids=args.case_ids,
                dataset_path=args.dataset.resolve() if args.dataset else None,
                candidate_id=args.candidate_id,
                max_model_calls=args.max_model_calls,
                max_token_usage=args.max_token_usage,
                deadline_minutes=args.deadline_minutes,
            )
        except (FileNotFoundError, ValueError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            raise SystemExit(2) from exc
        print(path)
        return
    if args.command == "resume":
        try:
            print(resume_evaluation(project_root, args.run_id))
        except (FileNotFoundError, ValueError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            raise SystemExit(2) from exc
        return
    if args.command == "receipt":
        try:
            value = create_stage_receipt(project_root, args.run_id)
        except (FileNotFoundError, ValueError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            raise SystemExit(2) from exc
        print(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2))
        return
    if args.command == "review":
        try:
            if args.import_decisions:
                value = import_failure_review_decisions(
                    project_root, args.run_id, args.import_decisions.resolve()
                )
            elif args.check:
                value = validate_failure_review(project_root, args.run_id)
            else:
                value = write_failure_review(
                    project_root,
                    args.run_id,
                    overwrite=args.overwrite,
                )
        except (FileNotFoundError, ValueError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            raise SystemExit(2) from exc
        print(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2))
        if args.check and not value["valid"]:
            raise SystemExit(2)
        return
    try:
        value = report_evaluation(project_root, args.run_id)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    print(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
