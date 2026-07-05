"""Outbound ports for the ledger bounded context."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from app.ledger.core.node import Node
from app.ledger.core.vector import Vector
from app.shared import EntityId


class NodeRepository(Protocol):
    """Secondary port: persistence operations for Node entities.

    Implementations must guarantee that save() is idempotent
    (saving the same node twice produces no side effects).
    """

    def save(self, node: Node) -> None:
        """Persist a node. Upsert semantics.

        Args:
            node: The Node entity to save.
        """
        ...

    def find_by_id(self, node_id: EntityId) -> Node | None:
        """Retrieve a node by its unique identifier.

        Args:
            node_id: Unique identifier of the node.

        Returns:
            Node | None: The Node if found, else None.
        """
        ...

    def find_by_user(self, user_id: EntityId) -> list[Node]:
        """Retrieve all nodes owned by a user.

        Args:
            user_id: Owner of the nodes.

        Returns:
            list[Node]: Nodes belonging to the user.
        """
        ...


class VectorRepository(Protocol):
    """Secondary port: append-only persistence for Vector entities.

    The append() method name (not save/update) reinforces the
    immutable, append-only nature of the financial ledger.
    """

    def append(self, vector: Vector) -> None:
        """Append a vector to the ledger. Vectors are never modified.

        Args:
            vector: The Vector entity to append.
        """
        ...

    def find_by_node(
        self,
        node_id: EntityId,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[Vector]:
        """Find all vectors involving a node as source or target.

        Args:
            node_id: Unique identifier of the node.
            start: Optional start bounds filter.
            end: Optional end bounds filter.

        Returns:
            list[Vector]: List of matching Vectors.
        """
        ...

    def find_by_lineage(self, lineage_token: str) -> list[Vector]:
        """Find all vectors sharing a lineage token (for netting).

        Args:
            lineage_token: Netting lineage token.

        Returns:
            list[Vector]: List of matching Vectors.
        """
        ...


__all__ = ["NodeRepository", "VectorRepository"]
