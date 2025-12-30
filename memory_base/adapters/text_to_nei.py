from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from memory_base.llm.base import LLMClient
from memory_base.utils.extract import extract_nei_from_tagged_or_json

from .base import Adapter, NormalizedExperienceInput


_SYSTEM_PROMPT = """Goal: extract actionable experience from the event described in the input text, and normalize it into an NEI record for a multi-level experience memory system.

Given the input text, extract a normalized experience event (NEI).

Return ONLY the tagged block below (no markdown, no extra commentary).
If unknown, leave the tag content empty.

<nei>
<situation></situation>
<goal></goal>
<attempt></attempt>
<result></result>
<reflection></reflection>
<label>success|failure|unknown</label>
</nei>

Rules:
- <situation> must be detailed enough to reproduce the state:
  include relevant context, constraints, inputs, environment/tooling (versions if applicable),
  and concrete symptoms (e.g., error messages, failing tests, proof state).
- Prefer writing <situation> as a detailed and complete snapshot, not a vague summary.
- Field boundaries are strict (do not mix fields):
  - <situation>: ONLY the initial context/state/constraints/symptoms from the given text.
    DO NOT include goal/attempt/result/reflection in <situation>.
  - <goal>: ONLY the intended objective described in the text.
  - <attempt>: ONLY the actions/steps that were tried in the text.
  - <result>: ONLY the observed outcome in the text (outcome/metrics/errors).
  - <reflection>: ONLY the lessons / next-time adjustments stated in the text.
- Do NOT output placeholders like "..." or "…". If unknown, leave the tag content empty.
- If unsure, leave the tag content empty and set label to "unknown".
- Prefer concise, information-dense strings.
"""


@dataclass
class TextToNEIAdapter(Adapter):
    """
    LLM-backed adapter: free-text -> NEI.

    This is useful for:
    - "生活任务尝试描述" -> NEI
    - (later) commit summaries / chat logs after you pre-render them into text
    """

    llm: LLMClient
    source_type: str = "text"
    system_prompt: str = _SYSTEM_PROMPT

    def ingest(self, raw: Any) -> NormalizedExperienceInput:
        if isinstance(raw, dict):
            text = raw.get("text") or raw.get("payload") or raw.get("attempt") or ""
            source_ref = raw.get("source_ref") or {"kind": "text", "note": "dict-input"}
        else:
            text = str(raw)
            source_ref = {"kind": "text", "note": "string-input"}

        resp = self.llm.respond(text, system=self.system_prompt)
        obj = extract_nei_from_tagged_or_json(resp.text)

        label = obj.get("label", "unknown")
        if label not in ("success", "failure", "unknown"):
            label = "unknown"

        return NormalizedExperienceInput(
            source_type=self.source_type,
            source_ref=source_ref,
            situation=obj.get("situation"),
            goal=obj.get("goal"),
            attempt=obj.get("attempt"),
            result=obj.get("result"),
            reflection=obj.get("reflection"),
            label=label,  # type: ignore[arg-type]
            payload={"raw_text": text},
            observations=None,
            hints=None,
        )


