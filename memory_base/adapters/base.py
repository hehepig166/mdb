from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Literal, Mapping


Label = Literal["success", "failure", "unknown"]


@dataclass(frozen=True)
class NormalizedExperienceInput:
    """
    Normalized Experience Input (NEI).

    In this project we treat NEI as a *source-agnostic experience event candidate*:
    it should be as close as possible to the L1Event core fields:
    - situation / goal / attempt / result / reflection

    while still preserving traceability to raw sources via `source_ref`.
    """

    source_type: str
    source_ref: Mapping[str, Any]

    # L1-like core slots (may be partially filled depending on source)
    situation: str | None = None
    goal: str | None = None
    attempt: str | None = None
    result: str | None = None
    reflection: str | None = None
    label: Label = "unknown"

    # Raw/auxiliary source information (optional)
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


