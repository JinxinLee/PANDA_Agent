from __future__ import annotations
import argparse, json
from pathlib import Path
from dotenv import load_dotenv
from panda_agent.indexing import (
    apply_b5_selective_index, apply_index, index_plan, migrate_b3_sparse_identity,
    resume_index, sync_b4_locator_metadata, verify_index, plan_b5_reindex_impact,
)

def main() -> None:
    load_dotenv()
    parser=argparse.ArgumentParser(); parser.add_argument("command",choices=("plan","apply","resume","verify","migrate-b3-sparse-identity","sync-b4-locators","b5-impact-plan","b5-apply")); parser.add_argument("--limit",type=int); parser.add_argument("--offset",type=int,default=0); parser.add_argument("--run-id",type=int); parser.add_argument("--run",action="store_true",help="apply an otherwise dry-run metadata migration"); parser.add_argument("--project-root",type=Path,default=Path(__file__).resolve().parents[3]); args=parser.parse_args()
    if args.command == "plan": result=index_plan(args.project_root.resolve())
    elif args.command == "verify": result=verify_index(args.project_root.resolve())
    elif args.command == "resume":
        if args.run_id is None: parser.error("resume requires --run-id")
        result=resume_index(args.project_root.resolve(),args.run_id)
    elif args.command == "migrate-b3-sparse-identity": result=migrate_b3_sparse_identity(args.project_root.resolve(),run=args.run)
    elif args.command == "sync-b4-locators": result=sync_b4_locator_metadata(args.project_root.resolve(),run=args.run)
    elif args.command == "b5-impact-plan": result=plan_b5_reindex_impact(args.project_root.resolve())
    elif args.command == "b5-apply": result=apply_b5_selective_index(args.project_root.resolve(),run=args.run)
    else: result=apply_index(args.project_root.resolve(),limit=args.limit,offset=args.offset)
    print(json.dumps(result,indent=2))
if __name__=="__main__": main()
