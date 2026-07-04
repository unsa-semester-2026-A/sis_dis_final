"""Outbound port for node persistence."""

from __future__ import annotations

from typing import Protocol

from finance.ledger.domain.node import Node
from finance.shared.domain.types import EntityId


class NodeRepository(Protocol):
    """Secondary port: persistence operations for Node entities.

    Implementations must guarantee that save() is idempotent
    (saving the same node twice produces no side effects).
    """

    def save(self, node: Node) -> None:
        """Persist a node. Upsert semantics."""
        ...

    def find_by_id(self, node_id: EntityId) -> Node | None:
        """Retrieve a node by its unique identifier."""
        ...

    def find_by_user(self, user_id: EntityId) -> list[Node]:
        """Retrieve all nodes owned by a user."""
        ...


__all__ = ["NodeRepository"]
