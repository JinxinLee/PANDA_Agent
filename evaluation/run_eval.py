"""Run the declared real retrieval or QA evaluation set."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import uuid
from pathlib import Path

import yaml
from dotenv import load_dotenv

from panda_agent.qa import QAAgent
from panda_agent.retrieval import Retriever
from panda_agent.evaluation import EvaluationRunStore


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    load_dotenv()
    parser=argparse.ArgumentParser()
    parser.add_argument("mode",choices=("retrieval","qa")); parser.add_argument("--limit",type=int); parser.add_argument("--start",type=int,default=0)
    parser.add_argument("--run-id"); parser.add_argument("--resume",action="store_true")
    parser.add_argument("--project-root",type=Path,default=Path(__file__).resolve().parents[1]); args=parser.parse_args()
    source=args.project_root/"evaluation"/("retrieval_questions.yaml" if args.mode=="retrieval" else "qa_questions.yaml")
    source_bytes=source.read_bytes()
    cases=yaml.safe_load(source_bytes)["questions"][args.start:args.start+args.limit if args.limit else None]
    run_id=args.run_id or f"{args.mode}-{uuid.uuid4()}"
    store=EvaluationRunStore(
        args.project_root/"data"/"evaluation"/"runs", run_id,
        {"mode":args.mode,"dataset_hash":hashlib.sha256(source_bytes).hexdigest(),"start":args.start,"limit":args.limit},
        resume=args.resume,
    )
    engine=Retriever(args.project_root) if args.mode=="retrieval" else QAAgent(args.project_root)
    for case in cases:
        if case["id"] in store.completed_ids:
            continue
        value=engine.retrieve(case["query"]) if args.mode=="retrieval" else engine.run(case["query"]).model_dump(mode="json")
        store.record({"id":case["id"],"expected_intent":case["intent"],"result":value})
        print(json.dumps({"id":case["id"],"status":value.get("status","retrieved")},ensure_ascii=False),flush=True)
    records=[json.loads(line) for line in store.results_path.read_text(encoding="utf-8").splitlines() if line]
    intent_correct=sum(
        item["result"].get("plan",{}).get("intent")==item["expected_intent"]
        for item in records if args.mode=="retrieval"
    )
    metrics={
        "cases_completed":len(records),
        "intent_accuracy":intent_correct/len(records) if records and args.mode=="retrieval" else None,
        "answered_rate":sum(item["result"].get("status")=="answered" for item in records)/len(records) if records and args.mode=="qa" else None,
        "nonempty_evidence_rate":sum(bool(item["result"].get("evidence")) for item in records)/len(records) if records else 0.0,
    }
    (store.run_dir/"metrics.json").write_text(json.dumps(metrics,indent=2)+"\n",encoding="utf-8")
    print(store.run_dir)


if __name__=="__main__": main()
