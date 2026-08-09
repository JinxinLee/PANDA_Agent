from __future__ import annotations
import argparse, json
from pathlib import Path
from dotenv import load_dotenv
from panda_agent.indexing import apply_index, index_plan, resume_index, verify_index

def main() -> None:
    load_dotenv()
    parser=argparse.ArgumentParser(); parser.add_argument("command",choices=("plan","apply","resume","verify")); parser.add_argument("--limit",type=int); parser.add_argument("--offset",type=int,default=0); parser.add_argument("--run-id",type=int); parser.add_argument("--project-root",type=Path,default=Path(__file__).resolve().parents[3]); args=parser.parse_args()
    if args.command == "plan": result=index_plan(args.project_root.resolve())
    elif args.command == "verify": result=verify_index(args.project_root.resolve())
    elif args.command == "resume":
        if args.run_id is None: parser.error("resume requires --run-id")
        result=resume_index(args.project_root.resolve(),args.run_id)
    else: result=apply_index(args.project_root.resolve(),limit=args.limit,offset=args.offset)
    print(json.dumps(result,indent=2))
if __name__=="__main__": main()
