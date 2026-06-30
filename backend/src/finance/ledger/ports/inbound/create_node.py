"""Inbound port for creating ledger nodes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from finance.ledger.domain.node import Node
from finance.ledger.domain.node_type import NodeType
from finance.shared.domain.types import EntityId


@dataclass(frozen=True, slots=True)
class CreateNodeCommand:
    """Command to create a new financial node.

    Attributes:
        user_id: Owner of the node.
        name: Display name for the node.
        node_type: Financial classification.
        currency: ISO 4217 currency code (immutable after creation).
    """

    user_id: EntityId
    name: str
    node_type: NodeType
    currency: str


class CreateNodePort(Protocol):
    """Inbound port: create a new ledger node."""

    def execute(self, command: CreateNodeCommand) -> Node:
        """Create and persist a new Node."""
        ...


__all__ = ["CreateNodeCommand", "CreateNodePort"]
