"""Inbound port for emitting financial vectors."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Protocol

from finance.ledger.domain.vector import Vector
from finance.shared.domain.types import EntityId


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
        """Create and append a new Vector to the ledger."""
        ...


__all__ = ["EmitVectorCommand", "EmitVectorPort"]
