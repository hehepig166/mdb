from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class NormalizedExperienceInput:
    """
    Source-agnostic normalized input (NEI).
    This mirrors the spec document and is intentionally minimal.
    """

    source_type: str
    source_ref: Mapping[str, Any]
    payload: Mapping[str, Any] | None = None
    observations: Mapping[str, Any] | None = None
    hints: Mapping[str, Any] | None = None


class Adapter(ABC):
    """
    Convert a raw source input into a NormalizedExperienceInput.

    Keep adapters "thin":
    - do not embed/cluster here
    - do not call LLM here (unless you explicitly want a source-specific extractor)
    """

    @abstractmethod
    def ingest(self, raw: Any) -> NormalizedExperienceInput:
        raise NotImplementedError


