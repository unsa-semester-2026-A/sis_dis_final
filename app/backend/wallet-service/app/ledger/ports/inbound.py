"""Inbound ports for the ledger bounded context."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Protocol

from app.ledger.core.node import Node
from app.ledger.core.node_type import NodeType
from app.ledger.core.vector import Vector
from app.shared import EntityId, Money


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
        """Create and persist a new Node.

        Args:
            command: Creation parameters.

        Returns:
            Node: The created Node.
        """
        ...


@dataclass(frozen=True, slots=True)
class EmitVectorCommand:
    """Command to emit a new financial mutation vector.

    Attributes:
        source_node_id: Node from which funds originate.
        target_node_id: Node to which funds arrive.
        amount: Positive value to transfer.
        exchange_rate: Currency conversion multiplier.
        lineage_token: Grouping token for netting. Auto-generated if None.
        transaction_id: Optional banking transaction reference.
        tags: Orthogonal classification metadata.
        effective_at: Logical date. Defaults to current time if None.
    """

    source_node_id: EntityId
    target_node_id: EntityId
    amount: Decimal
    exchange_rate: Decimal = Decimal("1.0")
    lineage_token: str | None = None
    transaction_id: EntityId | None = None
    tags: dict[str, str] = field(default_factory=dict)
    effective_at: datetime | None = None


class EmitVectorPort(Protocol):
    """Inbound port: emit an append-only financial vector."""

    def execute(self, command: EmitVectorCommand) -> Vector:
        """Create and append a new Vector to the ledger.

        Args:
            command: Vector emission parameters.

        Returns:
            Vector: The emitted Vector.
        """
        ...


@dataclass(frozen=True, slots=True)
class BalanceQuery:
    """Query to evaluate a node's balance over a time range.

    Attributes:
        node_id: Target node to evaluate.
        start_date: Lower bound (inclusive). None means no lower bound.
        end_date: Upper bound (inclusive). None means no upper bound.
    """

    node_id: EntityId
    start_date: datetime | None = None
    end_date: datetime | None = None


class EvaluateBalancePort(Protocol):
    """Inbound port: compute a node's balance from the vector ledger."""

    def execute(self, query: BalanceQuery) -> Money:
        """Calculate Balance(v) = sum(inflows * rate) - sum(outflows).

        Args:
            query: Balance query parameters.

        Returns:
            Money: The computed Money balance.
        """
        ...


__all__ = [
    "CreateNodeCommand",
    "CreateNodePort",
    "EmitVectorCommand",
    "EmitVectorPort",
    "BalanceQuery",
    "EvaluateBalancePort",
]
