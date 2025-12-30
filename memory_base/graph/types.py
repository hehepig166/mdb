from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Mapping


Layer = Literal["L1", "L2", "L3"]


@dataclass(frozen=True)
class NodeRef:
    """
    Lightweight reference to a node in the EMB graph.
    """

    id: str
    layer: Layer


@dataclass(frozen=True)
class Edge:
    """
    Generic graph edge.
    - edge_type: e.g. member_of / supports / about / similar / contradict / refine
    - weight: optional edge weight (e.g. similarity score)
    - meta: optional metadata (e.g. which metric generated the edge)
    """

    src: NodeRef
    dst: NodeRef
    edge_type: str
    weight: float | None = None
    meta: Mapping[str, Any] | None = None


