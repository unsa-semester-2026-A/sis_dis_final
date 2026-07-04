"""Ledger Node entity — vertices of the financial graph."""

from __future__ import annotations

from dataclasses import dataclass, replace

from finance.ledger.domain.node_type import NodeType
from finance.shared.domain.types import EntityId


@dataclass(frozen=True, slots=True)
class Node:
    """A vertex in the financial directed graph.

    Represents a financial actor: bank account, expense category,
    income source, or liability. Currency is immutable after creation.

    Attributes:
        id: Unique node identifier.
        user_id: Owner of this node.
        name: Human-readable display name.
        node_type: Accounting classification (ASSET, LIABILITY, SOURCE, SINK).
        currency: ISO 4217 currency code. Immutable after creation.
        is_active: When False, node rejects new vectors.
    """

    id: EntityId
    user_id: EntityId
    name: str
    node_type: NodeType
    currency: str
    is_active: bool = True

    def __post_init__(self) -> None:
        """Validate node invariants."""
        if not self.name.strip():
            msg = "Node name must not be empty"
            raise ValueError(msg)
        if len(self.currency) != 3:  # noqa: PLR2004
            msg = f"Currency must be ISO 4217 (3 chars), got '{self.currency}'"
            raise ValueError(msg)

    def deactivate(self) -> Node:
        """Return a copy of this node with is_active=False."""
        return replace(self, is_active=False)


__all__ = ["Node"]
