from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from .types import ChatMessage, LLMResponse


class ChatSession(ABC):
    """
    Stateful chat session.
    - Maintains internal history.
    - `send()` appends user message and returns assistant response.
    """

    @abstractmethod
    def send(self, message: str) -> LLMResponse:
        raise NotImplementedError

    @property
    @abstractmethod
    def history(self) -> Sequence[ChatMessage]:
        raise NotImplementedError


@dataclass
class _DefaultChatSession(ChatSession):
    _llm: "LLM"
    _model: str
    _temperature: float | None = None
    _max_output_tokens: int | None = None
    _metadata: Mapping[str, Any] | None = None
    _history: list[ChatMessage] = field(default_factory=list)

    def send(self, message: str) -> LLMResponse:
        self._history.append(ChatMessage(role="user", content=message))
        resp = self._llm._chat(
            messages=self._history,
            model=self._model,
            temperature=self._temperature,
            max_output_tokens=self._max_output_tokens,
            metadata=self._metadata,
        )
        self._history.append(ChatMessage(role="assistant", content=resp.text))
        return resp

    @property
    def history(self) -> Sequence[ChatMessage]:
        return tuple(self._history)


class LLM(ABC):
    """
    Provider-agnostic LLM interface (simple surface area).

    You requested only two public operations:
    - respond(): single message -> response
    - start_chat(): persistent chat session with internal history

    Providers implement the internal `_chat()` primitive.
    """

    @abstractmethod
    def _chat(
        self,
        *,
        messages: Sequence[ChatMessage],
        model: str,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> LLMResponse:
        raise NotImplementedError

    def respond(
        self,
        message: str,
        *,
        model: str,
        system: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> LLMResponse:
        msgs: list[ChatMessage] = []
        if system:
            msgs.append(ChatMessage(role="system", content=system))
        msgs.append(ChatMessage(role="user", content=message))
        return self._chat(
            messages=msgs,
            model=model,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            metadata=metadata,
        )

    def start_chat(
        self,
        *,
        model: str,
        system: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ChatSession:
        history: list[ChatMessage] = []
        if system:
            history.append(ChatMessage(role="system", content=system))
        return _DefaultChatSession(
            _llm=self,
            _model=model,
            _temperature=temperature,
            _max_output_tokens=max_output_tokens,
            _metadata=metadata,
            _history=history,
        )


@dataclass
class LLMClient:
    """
    Convenience wrapper with an explicit __init__-style configuration.

    Motivation:
    - `LLM` is an abstract interface; providers often use dataclasses.
    - Call sites usually want a configured client with default model/system/etc.,
      so they don't have to pass `model=...` every time.
    """

    llm: LLM
    model: str
    system: str | None = None
    temperature: float | None = None
    max_output_tokens: int | None = None
    metadata: Mapping[str, Any] | None = None

    def respond(self, message: str, **overrides: Any) -> LLMResponse:
        return self.llm.respond(
            message,
            model=str(overrides.get("model", self.model)),
            system=overrides.get("system", self.system),
            temperature=overrides.get("temperature", self.temperature),
            max_output_tokens=overrides.get("max_output_tokens", self.max_output_tokens),
            metadata=overrides.get("metadata", self.metadata),
        )

    def start_chat(self, **overrides: Any) -> ChatSession:
        return self.llm.start_chat(
            model=str(overrides.get("model", self.model)),
            system=overrides.get("system", self.system),
            temperature=overrides.get("temperature", self.temperature),
            max_output_tokens=overrides.get("max_output_tokens", self.max_output_tokens),
            metadata=overrides.get("metadata", self.metadata),
        )


