from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Mapping, Sequence


Role = Literal["system", "user", "assistant", "tool"]


@dataclass(frozen=True)
class ChatMessage:
    role: Role
    content: str


@dataclass(frozen=True)
class LLMUsage:
    """
    Optional usage metadata (tokens/cost). Providers may leave fields as None.
    """

    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    cost_usd: float | None = None


@dataclass(frozen=True)
class LLMResponse:
    """
    A generic response container.
    - text: the main assistant text
    - raw: provider-native payload (for debugging/auditing), optional
    - usage: optional token/cost usage
    """

    text: str
    raw: Mapping[str, Any] | None = None
    usage: LLMUsage | None = None


def ensure_messages(messages: Sequence[ChatMessage]) -> list[dict[str, str]]:
    """
    Convert internal message objects into a simple serializable shape.
    Providers can use this helper or ignore it.
    """

    return [{"role": m.role, "content": m.content} for m in messages]


