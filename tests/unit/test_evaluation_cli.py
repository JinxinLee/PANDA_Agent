import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from panda_agent.cli.evaluate import main


class _CliStdout(io.StringIO):
    def reconfigure(self, **kwargs: object) -> None:
        return None


class EvaluationCliTests(unittest.TestCase):
    def test_rescore_dry_run_dispatches_without_artifact_writer(self) -> None:
        expected = {"dry_run": True, "rescore_model_calls": 0, "records": []}
        with (
        patch("panda_agent.cli.evaluate.dry_rescore_run", return_value=expected) as dry,
        patch.object(
            sys,
            "argv",
            [
                "panda-qa-eval",
                "--project-root",
                ".",
                "rescore",
                "--run-id",
                "source-run",
                "--dataset",
                "evaluation/benchmarks/v2_5/gold_questions.yaml",
                "--include-case",
                "g039",
                "--dry-run",
            ],
        ),
        patch.object(sys, "stdout", new_callable=_CliStdout) as stdout,
        ):
            main()
        self.assertEqual(json.loads(stdout.getvalue()), expected)
        self.assertEqual(dry.call_args.kwargs["case_ids"], ["g039"])
        self.assertEqual(
            dry.call_args.args[2],
            Path("evaluation/benchmarks/v2_5/gold_questions.yaml").resolve(),
        )
