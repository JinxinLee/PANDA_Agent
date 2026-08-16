"""Shared B5 embedding-input and deterministic chunking contract."""

from __future__ import annotations

import re
from dataclasses import dataclass


TOKEN_PATTERN = re.compile(r"\w+|[^\w\s]", flags=re.UNICODE)


@dataclass(frozen=True)
class ChunkingPolicy:
    """The sole validity contract for normalized embedding units."""

    min_tokens: int = 10
    max_tokens: int = 1800
    max_embedding_input_chars: int = 4000
    version: str = "b5-v2"

    def token_count(self, text: str) -> int:
        return len(TOKEN_PATTERN.findall(text))

    def embedding_input(self, title: str, text: str) -> str:
        return f"{title}\n{text}"

    def within_upper_bounds(
        self, title: str, text: str, token_count: int | None = None
    ) -> bool:
        """Intermediate splitting bound: no minimum-token requirement.

        Sub-minimum atoms may stay alive during structure-first splitting so
        they can merge with adjacent atoms in source order. Only the final
        embedding candidate is checked with :meth:`embedding_input_is_valid`.
        """
        tokens = self.token_count(text) if token_count is None else token_count
        return (
            tokens <= self.max_tokens
            and len(self.embedding_input(title, text)) <= self.max_embedding_input_chars
        )

    def embedding_input_is_valid(
        self, title: str, text: str, token_count: int | None = None
    ) -> bool:
        tokens = self.token_count(text) if token_count is None else token_count
        return (
            self.min_tokens <= tokens <= self.max_tokens
            and len(self.embedding_input(title, text)) <= self.max_embedding_input_chars
        )

    def max_text_chars(self, title: str) -> int:
        return max(1, self.max_embedding_input_chars - len(title) - 1)


DEFAULT_CHUNKING_POLICY = ChunkingPolicy()
