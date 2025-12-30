from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from ..base import LLM
from ..types import ChatMessage, LLMResponse


@dataclass
class MockLLM(LLM):
    """
    Deterministic local provider for tests/dev.
    - respond(): echoes the message
    - start_chat(): maintains history, echoes each user message
    """

    def _chat(
        self,
        *,
        messages: Sequence[ChatMessage],
        model: str,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> LLMResponse:
        last = next((m.content for m in reversed(messages) if m.role == "user"), "")
        return LLMResponse(text=f"[mock:{model}] {last}")


