"""F6-A Stage A6 composer release audit runner (evaluation-only).

Consumes the frozen Gold + novel_validation run records, builds eligible
composer pairs, and runs the preregistered factuality/readability judgments
through the offline evaluation judge. No product model calls; no holdout.

Usage:
  PYTHONPATH=src python evaluation/scripts/f6a_composer_audit.py \
      --run-ids f6a-rc1-gold-full-20260913 f6a-rc1-novel-validation-full-20260913 \
      --output evaluation/f6a_composer_audit.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from dotenv import load_dotenv

from panda_agent.f6a_composer_audit import (
    aggregate_composer_audit,
    build_composer_audit_pairs,
    judge_composer_factuality,
    judge_composer_readability,
)
from panda_agent.evaluation_runner import load_run_records
from panda_agent.llm.vertex import VertexAIClient, VertexSettings


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--run-ids", nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    records: list[dict[str, Any]] = []
    for run_id in args.run_ids:
        run_dir = args.project_root / "data" / "evaluation" / "runs" / run_id
        records.extend(load_run_records(run_dir))

    pairs = build_composer_audit_pairs(records)
    fallback_count = 0
    attempt_count = 0
    for record in records:
        diagnostics = (record.get("diagnostics") or {}).get("composer") or {}
        if diagnostics.get("attempted"):
            attempt_count += 1
        if diagnostics.get("attempted") and not diagnostics.get("accepted"):
            fallback_count += 1

    vertex = VertexAIClient(VertexSettings.from_env())
    factuality_verdicts = []
    readability_verdicts = []
    for pair in pairs:
        factuality_verdicts.append(judge_composer_factuality(pair, vertex))
        readability_verdicts.append(judge_composer_readability(pair, vertex))

    aggregate = aggregate_composer_audit(pairs, factuality_verdicts, readability_verdicts)
    accept_rate = (attempt_count - fallback_count) / attempt_count if attempt_count else None
    output = {
        "schema_version": "f6a-composer-audit-v1",
        "run_ids": args.run_ids,
        "composer_attempt_count": attempt_count,
        "composer_accept_count": attempt_count - fallback_count,
        "composer_fallback_count": fallback_count,
        "composer_accept_rate": accept_rate,
        "composer_fallback_rate": (fallback_count / attempt_count) if attempt_count else None,
        **aggregate,
        "case_verdicts": [
            {
                "case_id": pair["case_id"],
                "factuality": factuality,
                "readability": readability,
            }
            for pair, factuality, readability in zip(
                pairs, factuality_verdicts, readability_verdicts
            )
        ],
    }
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in output.items() if k != "case_verdicts"}, indent=2))


if __name__ == "__main__":
    main()
