from __future__ import annotations
import argparse,sys
from pathlib import Path
from dotenv import load_dotenv
from panda_agent.service import QAService

def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    load_dotenv(); parser=argparse.ArgumentParser(prog="panda-qa"); sub=parser.add_subparsers(dest="command",required=True); ask=sub.add_parser("ask"); ask.add_argument("question",nargs="+"); ask.add_argument("--project-root",type=Path,default=Path(__file__).resolve().parents[3]); args=parser.parse_args(); print(QAService(args.project_root.resolve(), origin="cli").run(" ".join(args.question)).model_dump_json(indent=2))
if __name__=="__main__": main()
