from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from dotenv import load_dotenv
from panda_agent.retrieval import Retriever

def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    load_dotenv(); parser=argparse.ArgumentParser(); parser.add_argument("question",nargs="+"); parser.add_argument("--project-root",type=Path,default=Path(__file__).resolve().parents[3]); args=parser.parse_args()
    print(json.dumps(Retriever(args.project_root.resolve()).retrieve(" ".join(args.question)),ensure_ascii=False,indent=2))
if __name__=="__main__": main()
