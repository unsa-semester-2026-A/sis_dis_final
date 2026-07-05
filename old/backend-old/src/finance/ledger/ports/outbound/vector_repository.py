"""Outbound port for vector persistence."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from finance.ledger.domain.vector import Vector
from finance.shared.domain.types import EntityId


class VectorRepository(Protocol):
    """Secondary port: append-only persistence for Vector entities.

    The append() method name (not save/update) reinforces the
    immutable, append-only nature of the financial ledger.
    """

    def append(self, vector: Vector) -> None:
        """Append a vector to the ledger. Vectors are never modified."""
        ...

    def find_by_node(
        self,
        node_id: EntityId,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[Vector]:
        """Find all vectors involving a node as source or target."""
        ...

    def find_by_lineage(self, lineage_token: str) -> list[Vector]:
        """Find all vectors sharing a lineage token (for netting)."""
        ...


__all__ = ["VectorRepository"]
