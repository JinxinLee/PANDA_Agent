"""Vertex AI adapter for structured generation and retrieval embeddings."""

from __future__ import annotations

import json
import os
import threading
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, replace
from typing import Any, Sequence

from google import genai
from google.genai import types


class VertexConfigurationError(ValueError):
    """Raised when mandatory Vertex configuration is missing."""


class VertexCallError(RuntimeError):
    """Raised with stage and model context when a Vertex request fails."""


@dataclass(frozen=True)
class VertexSettings:
    project: str
    location: str = "global"
    generation_model: str = "gemini-3.7-flash"
    evaluation_judge_model: str = "gemini-3.7-flash"
    embedding_model: str = "gemini-embedding-2"
    embedding_dimensions: int = 3072
    timeout_ms: int = 120_000

    @classmethod
    def from_env(cls) -> "VertexSettings":
        project = os.getenv("QA_GCP_PROJECT_ID") or os.getenv("GCP_PROJECT_ID")
        if not project:
            raise VertexConfigurationError(
                "QA_GCP_PROJECT_ID or GCP_PROJECT_ID is required for Vertex AI"
            )
        return cls(
            project=project,
            location=(
                os.getenv("QA_VERTEX_LOCATION")
                or os.getenv("GCP_LOCATION")
                or "global"
            ),
            generation_model=os.getenv(
                "QA_GENERATION_MODEL_ID", "gemini-3.7-flash"
            ),
            evaluation_judge_model=os.getenv(
                "QA_EVALUATION_JUDGE_MODEL_ID", "gemini-3.7-flash"
            ),
            embedding_model=os.getenv(
                "QA_EMBEDDING_MODEL_ID", "gemini-embedding-2"
            ),
            embedding_dimensions=int(os.getenv("QA_EMBEDDING_DIMENSIONS", "3072")),
            timeout_ms=int(os.getenv("QA_VERTEX_TIMEOUT_MS", "120000")),
        )

    def for_generation_model(self, model: str) -> "VertexSettings":
        """Return equivalent settings for a separate structured-generation role."""
        return replace(self, generation_model=model)


@dataclass(frozen=True)
class VertexHealthResult:
    status: str
    location: str
    generation_model: str
    embedding_model: str
    generation_response: dict[str, Any]
    query_embedding_dimensions: int
    document_embedding_dimensions: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class VertexAIClient:
    def __init__(self, settings: VertexSettings, client: Any | None = None) -> None:
        self.settings = settings
        self._stats: Counter[str] = Counter()
        self._stats_lock = threading.Lock()
        self.client = client or genai.Client(
            vertexai=True,
            project=settings.project,
            location=settings.location,
            http_options=types.HttpOptions(timeout=settings.timeout_ms),
        )

    def _record_request(self, stage: str) -> None:
        with self._stats_lock:
            self._stats["model_calls"] += 1
            self._stats[f"{stage}_calls"] += 1

    def _record_usage(self, response: Any) -> None:
        usage = getattr(response, "usage_metadata", None)
        total = getattr(usage, "total_token_count", None) if usage else None
        if total is not None:
            with self._stats_lock:
                self._stats["token_usage"] += int(total)

    @staticmethod
    def _is_transient_error(message: str) -> bool:
        lowered = message.casefold()
        return any(
            token in lowered
            for token in (
                "429",
                "500",
                "502",
                "503",
                "504",
                "resource_exhausted",
                "temporarily unavailable",
                "timeout",
                "deadline",
                "unavailable",
            )
        )

    def stats_snapshot(self) -> dict[str, int]:
        """Return cumulative request counters without exposing prompts or credentials."""
        with self._stats_lock:
            return {
                key: self._stats.get(key, 0)
                for key in ("model_calls", "token_usage", "generation_calls", "embedding_calls")
            } | dict(self._stats)

    def stats_delta(self, previous: dict[str, int]) -> dict[str, int]:
        """Return one request's counter delta from a prior cumulative snapshot."""
        current = self.stats_snapshot()
        return {
            key: current.get(key, 0) - previous.get(key, 0)
            for key in current.keys() | previous.keys()
        }

    def generate_json(
        self,
        prompt: str,
        response_schema: dict[str, Any],
        *,
        system_instruction: str | None = None,
        temperature: float = 0.0,
    ) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                self._record_request("generation")
                response = self.client.models.generate_content(
                    model=self.settings.generation_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=temperature,
                        response_mime_type="application/json",
                        response_json_schema=response_schema,
                    ),
                )
                self._record_usage(response)
                text = getattr(response, "text", None)
                if not text:
                    raise ValueError("Vertex returned an empty structured response")
                value = json.loads(text)
                if not isinstance(value, dict):
                    raise ValueError("structured response must be a JSON object")
                return value
            except Exception as exc:
                last_error = exc
                message = str(exc).casefold()
                transient = self._is_transient_error(message)
                if transient and attempt < 2:
                    time.sleep(2**attempt)
                    continue
                break
        raise VertexCallError(
            "structured generation failed "
            f"for {self.settings.generation_model} in {self.settings.location}: {last_error}"
        ) from last_error

    def embed_query(self, text: str) -> list[float]:
        vectors = self._embed([text], task_type="RETRIEVAL_QUERY")
        return vectors[0]

    def embed_documents(
        self, texts: Sequence[str], *, title: str | None = None
    ) -> list[list[float]]:
        if not texts:
            return []
        return self._embed(texts, task_type="RETRIEVAL_DOCUMENT", title=title)

    def _embed(
        self,
        texts: Sequence[str],
        *,
        task_type: str,
        title: str | None = None,
    ) -> list[list[float]]:
        if len(texts) > 1:
            workers=min(int(os.getenv("QA_EMBEDDING_CONCURRENCY","16")),len(texts))
            with ThreadPoolExecutor(max_workers=workers) as executor:
                return list(executor.map(lambda text:self._embed([text],task_type=task_type,title=title)[0],texts))
        last_error: Exception | None = None
        for attempt in range(5):
          try:
            self._record_request("embedding")
            response = self.client.models.embed_content(
                model=self.settings.embedding_model,
                contents=[
                    types.Content(parts=[types.Part.from_text(text=text)])
                    for text in texts
                ],
                config=types.EmbedContentConfig(
                    task_type=task_type,
                    title=title,
                    auto_truncate=False,
                ),
            )
            self._record_usage(response)
            embeddings = getattr(response, "embeddings", None) or []
            vectors = [list(item.values or []) for item in embeddings]
            if len(vectors) != len(texts) or any(not vector for vector in vectors):
                raise ValueError(
                    f"expected {len(texts)} non-empty embeddings, got {len(vectors)}"
                )
            return vectors
          except Exception as exc:
            last_error=exc; message=str(exc).lower()
            transient=self._is_transient_error(message)
            if transient and attempt<4:
                time.sleep(2**attempt); continue
            break
        raise VertexCallError(
            f"{task_type} embedding failed for {self.settings.embedding_model} "
            f"in {self.settings.location}: {last_error}"
        ) from last_error

    def health_check(self) -> VertexHealthResult:
        response = self.generate_json(
            "Return a JSON object whose status field is exactly 'ok'.",
            {
                "type": "object",
                "properties": {"status": {"type": "string"}},
                "required": ["status"],
                "additionalProperties": False,
            },
            system_instruction="You are a deterministic API health checker.",
        )
        query_vector = self.embed_query("PANDA luminosity reconstruction")
        document_vector = self.embed_documents(
            ["PandaRoot produces reconstructed data used by LuminosityFit."],
            title="PANDA QA health document",
        )[0]
        return VertexHealthResult(
            status="ok" if response.get("status") == "ok" else "unexpected_response",
            location=self.settings.location,
            generation_model=self.settings.generation_model,
            embedding_model=self.settings.embedding_model,
            generation_response=response,
            query_embedding_dimensions=len(query_vector),
            document_embedding_dimensions=len(document_vector),
        )

    def generation_health_check(self) -> dict[str, Any]:
        """Run only the structured-generation probe for a model role."""
        response = self.generate_json(
            "Return a JSON object whose status field is exactly 'ok'.",
            {
                "type": "object",
                "properties": {"status": {"type": "string"}},
                "required": ["status"],
                "additionalProperties": False,
            },
            system_instruction="You are a deterministic API health checker.",
        )
        return {
            "status": "ok" if response.get("status") == "ok" else "unexpected_response",
            "location": self.settings.location,
            "generation_model": self.settings.generation_model,
        }
