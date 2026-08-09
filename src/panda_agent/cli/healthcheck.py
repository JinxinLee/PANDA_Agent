"""Real Vertex generation and embedding health check."""

from __future__ import annotations

import argparse
import json

from dotenv import load_dotenv

from panda_agent.llm.vertex import VertexAIClient, VertexSettings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run real Gemini generation and embedding health checks on Vertex AI."
    )
    parser.add_argument("--project")
    parser.add_argument("--location")
    parser.add_argument("--generation-model")
    parser.add_argument("--evaluation-judge-model")
    parser.add_argument("--embedding-model")
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()
    env_settings = VertexSettings.from_env()
    settings = VertexSettings(
        project=args.project or env_settings.project,
        location=args.location or env_settings.location,
        generation_model=args.generation_model or env_settings.generation_model,
        evaluation_judge_model=(
            args.evaluation_judge_model or env_settings.evaluation_judge_model
        ),
        embedding_model=args.embedding_model or env_settings.embedding_model,
        embedding_dimensions=env_settings.embedding_dimensions,
        timeout_ms=env_settings.timeout_ms,
    )
    def safe_call(stage: str, callback, *, generation_model: str):
        try:
            value = callback()
            return value.to_dict() if hasattr(value, "to_dict") else value
        except Exception as exc:  # healthcheck must report both roles, even if one is unavailable
            return {
                "status": "error",
                "stage": stage,
                "error_type": type(exc).__name__,
                "generation_model": generation_model,
                # Do not print exception text: SDK errors can contain project,
                # credential, request, or endpoint details.
            }

    runtime_client = VertexAIClient(settings)
    runtime_result = safe_call(
        "runtime_generation_and_embeddings",
        runtime_client.health_check,
        generation_model=settings.generation_model,
    )
    judge_client = VertexAIClient(
        settings.for_generation_model(settings.evaluation_judge_model)
    )
    judge_result = safe_call(
        "evaluation_judge_generation",
        judge_client.generation_health_check,
        generation_model=settings.evaluation_judge_model,
    )
    output = {**runtime_result, "evaluation_judge": judge_result}
    print(json.dumps(output, ensure_ascii=False, indent=2))
    if runtime_result.get("status") != "ok" or judge_result.get("status") != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
