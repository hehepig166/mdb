from __future__ import annotations

import json
import re
from typing import Any, Mapping


def extract_tag(text: str, tag: str) -> str | None:
    """
    Extract <tag>...</tag> content. Returns None if missing or empty.
    """

    m = re.search(rf"(?s)<{tag}>\s*(.*?)\s*</{tag}>", text)
    if not m:
        return None
    val = m.group(1).strip()
    if not val:
        return None
    # Treat common LLM placeholders as empty.
    if val in {"...", "…", "N/A", "NA", "null", "None"}:
        return None
    return val


def extract_tagged_fields(text: str, *, tags: list[str]) -> dict[str, str | None]:
    """
    Extract multiple tags from text.
    """

    return {t: extract_tag(text, t) for t in tags}


def extract_json_object(text: str) -> Mapping[str, Any]:
    """
    Best-effort JSON object extraction.
    - If extra text exists, slice the first {...} block.
    """

    text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in text")
    obj = json.loads(text[start : end + 1])
    if not isinstance(obj, dict):
        raise TypeError("JSON root must be an object")
    return obj


def extract_nei_from_tagged_or_json(text: str) -> dict[str, Any]:
    """
    Extract NEI fields from either a tagged <nei> block or (fallback) JSON.

    Returns a dict with keys:
    situation, goal, attempt, result, reflection, label
    """

    tags = ["situation", "goal", "attempt", "result", "reflection", "label"]
    out: dict[str, Any] = extract_tagged_fields(text, tags=tags)

    # If tags basically missing, try JSON fallback.
    if not any(out.get(k) for k in ("situation", "goal", "attempt", "result", "reflection")):
        obj = extract_json_object(text)
        for k in tags:
            out[k] = obj.get(k)

    if not out.get("label"):
        out["label"] = "unknown"
    return out


