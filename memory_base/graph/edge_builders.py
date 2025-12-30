from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

from .metrics import MetricSpec, NodeAccessor, SimilarityMetric
from .types import Edge, NodeRef


@dataclass(frozen=True)
class BuildEdgesConfig:
    """
    How to convert similarities into edges.
    """

    edge_type: str = "similar"
    directed: bool = False
    min_similarity: float | None = None  # threshold strategy
    top_k: int | None = None  # top-k strategy


def build_similarity_edges(
    *,
    nodes: Sequence[NodeRef],
    metric: SimilarityMetric,
    metric_spec: MetricSpec | None,
    accessor: NodeAccessor,
    config: BuildEdgesConfig,
) -> list[Edge]:
    """
    Build intra-layer (or any-layer) edges based on a SimilarityMetric.

    MVP implementation is O(n^2) and intended for small-scale bootstrapping.
    When you need scale:
    - use vector indexing (FAISS) for embedding metrics
    - or use blocking/candidate generation for non-embedding metrics
    """

    if config.min_similarity is None and config.top_k is None:
        raise ValueError("Either min_similarity or top_k must be set.")

    edges: list[Edge] = []
    meta: Mapping[str, Any] | None = None
    if metric_spec is not None:
        meta = {"metric": metric_spec.name, "metric_params": metric_spec.params}

    # Compute full pairwise similarity (naive).
    sims: list[list[float]] = [[0.0 for _ in nodes] for _ in nodes]
    for i, u in enumerate(nodes):
        for j, v in enumerate(nodes):
            if i == j:
                continue
            sims[i][j] = float(metric.similarity(u=u, v=v, accessor=accessor))

    if config.top_k is not None:
        k = int(config.top_k)
        for i, u in enumerate(nodes):
            ranked = sorted(
                ((j, sims[i][j]) for j in range(len(nodes)) if j != i),
                key=lambda t: t[1],
                reverse=True,
            )[:k]
            for j, score in ranked:
                if config.min_similarity is not None and score < config.min_similarity:
                    continue
                v = nodes[j]
                edges.append(Edge(src=u, dst=v, edge_type=config.edge_type, weight=score, meta=meta))
                if not config.directed:
                    edges.append(Edge(src=v, dst=u, edge_type=config.edge_type, weight=score, meta=meta))
        return edges

    # threshold-only
    assert config.min_similarity is not None
    for i, u in enumerate(nodes):
        for j, v in enumerate(nodes):
            if i == j:
                continue
            score = sims[i][j]
            if score >= config.min_similarity:
                edges.append(Edge(src=u, dst=v, edge_type=config.edge_type, weight=score, meta=meta))
                if not config.directed:
                    edges.append(Edge(src=v, dst=u, edge_type=config.edge_type, weight=score, meta=meta))
    return edges


