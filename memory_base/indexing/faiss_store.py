from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Sequence

from .vector_store import VectorRecord, VectorSearchResult, VectorStore


@dataclass
class FaissVectorStore(VectorStore):
    """
    FAISS-backed VectorStore (optional dependency).

    Notes:
    - This is a thin wrapper scaffold. You can extend it with:
      - persistence (write/read index + id map)
      - IVF/HNSW indexes
      - better metadata filtering (pre-filter candidate ids, then search)
    """

    dim: int
    metric: str = "ip"  # "ip" (inner product) or "l2"
    _index: Any = field(default=None, init=False, repr=False)
    _ids: list[str] = field(default_factory=list, init=False, repr=False)
    _meta: list[Mapping[str, Any] | None] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        try:
            import faiss  # type: ignore
        except Exception as e:  # pragma: no cover
            raise ImportError(
                "FaissVectorStore requires optional dependency 'faiss-cpu' (or 'faiss-gpu')."
            ) from e

        if self.metric == "ip":
            self._index = faiss.IndexFlatIP(self.dim)
        elif self.metric == "l2":
            self._index = faiss.IndexFlatL2(self.dim)
        else:
            raise ValueError("metric must be 'ip' or 'l2'")

    def upsert(self, records: Iterable[VectorRecord]) -> None:
        """
        MVP behavior:
        - append-only (no true update). For updates, delete+rebuild or keep a tombstone map.
        """
        import numpy as np

        batch = list(records)
        if not batch:
            return

        vecs = np.asarray([r.vector for r in batch], dtype="float32")
        if vecs.ndim != 2 or vecs.shape[1] != self.dim:
            raise ValueError(f"expected vectors shape (n, {self.dim}), got {vecs.shape}")

        self._index.add(vecs)
        self._ids.extend([r.id for r in batch])
        self._meta.extend([r.metadata for r in batch])

    def delete(self, ids: Iterable[str]) -> None:
        """
        MVP behavior:
        - not supported for IndexFlat*. Implement via IDMap2 or maintain a rebuild strategy.
        """
        raise NotImplementedError("FaissVectorStore.delete not supported in this MVP scaffold.")

    def search(
        self,
        *,
        query_vector: Sequence[float],
        top_k: int,
        filter: Mapping[str, Any] | None = None,
    ) -> list[VectorSearchResult]:
        import numpy as np

        if filter:
            # MVP: no metadata filtering inside FAISS for Flat index.
            # Recommended approach:
            # - pre-filter candidate ids using metadata store
            # - run FAISS on that subset (or use a different index strategy)
            raise NotImplementedError("metadata filter not supported in this MVP scaffold.")

        q = np.asarray([query_vector], dtype="float32")
        if q.shape != (1, self.dim):
            raise ValueError(f"expected query_vector dim {self.dim}, got {q.shape}")

        scores, idxs = self._index.search(q, top_k)
        out: list[VectorSearchResult] = []
        for score, idx in zip(scores[0].tolist(), idxs[0].tolist(), strict=False):
            if idx < 0:
                continue
            out.append(VectorSearchResult(id=self._ids[idx], score=float(score), metadata=self._meta[idx]))
        return out


