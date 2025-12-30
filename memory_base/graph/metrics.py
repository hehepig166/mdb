from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Mapping, Protocol

from .types import NodeRef


class NodeAccessor(Protocol):
    """
    Allows metrics to access node data without binding to a concrete storage model.
    Implementations can fetch text fields, artifacts, timestamps, etc.
    """

    def get_node(self, node: NodeRef) -> Mapping[str, Any]:
        ...


class SimilarityMetric(ABC):
    """
    Compute similarity between nodes.

    This is the key abstraction you requested:
    all "edge generation" can be expressed as choosing a SimilarityMetric
    + choosing an EdgeBuilder strategy (threshold / top-k / clustering).
    """

    name: str

    @abstractmethod
    def similarity(self, *, u: NodeRef, v: NodeRef, accessor: NodeAccessor) -> float:
        raise NotImplementedError


@dataclass(frozen=True)
class MetricSpec:
    """
    A serializable description of a metric used to generate edges.
    Useful for auditability and for re-generating edges later.
    """

    name: str
    params: Mapping[str, Any] | None = None


