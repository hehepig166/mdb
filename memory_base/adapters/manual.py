from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .base import Adapter, Label, NormalizedExperienceInput


@dataclass
class ManualAdapter(Adapter):
    """
    Minimal adapter for manual inputs.

    Accepted raw formats:
    - dict (preferred): can directly provide NEI fields
    - str: treated as `attempt`
    """

    source_type: str = "manual"

    def ingest(self, raw: Any) -> NormalizedExperienceInput:
        if isinstance(raw, dict):
            source_ref = raw.get("source_ref") or {"manual": True}
            label = raw.get("label", "unknown")
            if label not in ("success", "failure", "unknown"):
                label = "unknown"

            return NormalizedExperienceInput(
                source_type=str(raw.get("source_type", self.source_type)),
                source_ref=source_ref,
                situation=raw.get("situation"),
                goal=raw.get("goal"),
                attempt=raw.get("attempt"),
                result=raw.get("result"),
                reflection=raw.get("reflection"),
                label=label,  # type: ignore[arg-type]
                payload=raw.get("payload"),
                observations=raw.get("observations"),
                hints=raw.get("hints"),
            )

        # Fallback: treat as plain-text attempt
        return NormalizedExperienceInput(
            source_type=self.source_type,
            source_ref={"manual": True},
            attempt=str(raw),
            payload={"text": str(raw)},
        )


