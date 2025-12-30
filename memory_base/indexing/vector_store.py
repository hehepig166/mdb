from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


@dataclass(frozen=True)
class VectorRecord:
    """
    A single vector record in a store.
    - id: stable record id (typically an event/pattern/principle id)
    - vector: embedding vector
    - metadata: filterable fields (label/source_type/artifacts/timestamp/etc.)
    """

    id: str
    vector: Sequence[float]
    metadata: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class VectorSearchResult:
    id: str
    score: float
    metadata: Mapping[str, Any] | None = None


class VectorStore(ABC):
    """
    Abstract vector index. Can be backed by FAISS, SQLite extensions, Pinecone, etc.
    """

    @abstractmethod
    def upsert(self, records: Iterable[VectorRecord]) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, ids: Iterable[str]) -> None:
        raise NotImplementedError

    @abstractmethod
    def search(
        self,
        *,
        query_vector: Sequence[float],
        top_k: int,
        filter: Mapping[str, Any] | None = None,
    ) -> list[VectorSearchResult]:
        raise NotImplementedError


