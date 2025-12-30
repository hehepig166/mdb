from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from ..base import LLM
from ..types import ChatMessage, LLMResponse


def _normalize_ollama_messages(messages: Sequence[ChatMessage]) -> list[dict[str, str]]:
    """
    Ollama chat API expects roles in {"system","user","assistant"}.
    We drop/convert unknown roles conservatively.
    """

    out: list[dict[str, str]] = []
    for m in messages:
        role = m.role
        if role not in ("system", "user", "assistant"):
            role = "user"
        out.append({"role": role, "content": m.content})
    return out


def _post_json(url: str, payload: Mapping[str, Any], timeout_s: float) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:  # nosec - localhost
        body = resp.read().decode("utf-8")
    return json.loads(body)


@dataclass
class OllamaLLM(LLM):
    """
    Ollama local provider.

    Default endpoint: http://localhost:11434
    Uses: POST /api/chat (non-streaming).
    """

    base_url: str = "http://localhost:11434"
    timeout_s: float = 60.0

    def _chat(
        self,
        *,
        messages: Sequence[ChatMessage],
        model: str,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> LLMResponse:
        url = self.base_url.rstrip("/") + "/api/chat"

        options: dict[str, Any] = {}
        if temperature is not None:
            options["temperature"] = float(temperature)
        if max_output_tokens is not None:
            # Ollama uses num_predict as max tokens to generate.
            options["num_predict"] = int(max_output_tokens)

        payload: dict[str, Any] = {
            "model": model,
            "messages": _normalize_ollama_messages(messages),
            "stream": False,
        }
        if options:
            payload["options"] = options
        if metadata:
            # Keep metadata for audit/debug; Ollama ignores unknown fields.
            payload["metadata"] = dict(metadata)

        try:
            raw = _post_json(url, payload, timeout_s=self.timeout_s)
        except urllib.error.URLError as e:
            raise RuntimeError(
                f"Failed to reach Ollama at {self.base_url!r}. "
                "Is `ollama serve` running?"
            ) from e

        # Expected:
        # {"message": {"role":"assistant","content":"..."}, ...}
        msg = raw.get("message") if isinstance(raw, dict) else None
        text = ""
        if isinstance(msg, dict):
            text = str(msg.get("content", ""))
        return LLMResponse(text=text, raw=raw)


def ollama_has_model(*, base_url: str, model: str, timeout_s: float = 3.0) -> bool:
    """
    Best-effort check via GET /api/tags.
    Returns False if unreachable or model not found.
    """

    url = base_url.rstrip("/") + "/api/tags"
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:  # nosec - localhost
            body = resp.read().decode("utf-8")
        data = json.loads(body)
        models = data.get("models", [])
        for m in models:
            name = m.get("name")
            if name == model:
                return True
        return False
    except Exception:
        return False


