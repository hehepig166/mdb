from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from ..base import LLM
from ..types import ChatMessage, LLMResponse


@dataclass
class AnthropicLLM(LLM):
    """
    Anthropic provider (skeleton).

    This repo intentionally avoids hard-binding dependencies at scaffold time.
    Implementations can use the official SDK or raw HTTP.
    """

    api_key: str | None = None
    base_url: str | None = None

    def _chat(
        self,
        *,
        messages: Sequence[ChatMessage],
        model: str,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> LLMResponse:
        raise NotImplementedError(
            "AnthropicLLM._chat is a scaffold. Implement using your preferred Anthropic client."
        )


