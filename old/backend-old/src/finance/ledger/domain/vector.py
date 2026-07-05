"""Ledger Vector entity — directed edges of the financial graph."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from finance.shared.domain.types import EntityId
from finance.shared.errors import InvalidAmountError


@dataclass(frozen=True, slots=True)
class Vector:
    """An immutable, append-only financial mutation edge.

    Represents a directed transfer of value from source to target node.
    Vectors are never deleted or modified — corrections use the same
    lineage_token to enable netting.

    Attributes:
        id: Unique vector identifier.
        lineage_token: Groups related vectors for report netting.
        source_node_id: Node from which funds originate.
        target_node_id: Node to which funds arrive.
        amount: Absolute value extracted from source (must be > 0).
        exchange_rate: Multiplier for cross-currency conversions.
        tags: Orthogonal metadata for classification.
        effective_at: Logical time for budgets and balances.
        system_at: Physical creation timestamp for audit trail.
        transaction_id: Optional FK to a banking Transaction (None for corrections).
    """

    id: EntityId
    lineage_token: str
    source_node_id: EntityId
    target_node_id: EntityId
    amount: Decimal
    effective_at: datetime
    system_at: datetime
    exchange_rate: Decimal = Decimal("1.0")
    tags: dict[str, str] = field(default_factory=dict)
    transaction_id: EntityId | None = None

    def __post_init__(self) -> None:
        """Enforce vector invariants."""
        if self.amount <= 0:
            msg = f"Vector amount must be positive, got {self.amount}"
            raise InvalidAmountError(msg)
        if self.source_node_id == self.target_node_id:
            msg = "Source and target nodes must differ"
            raise ValueError(msg)
        if self.exchange_rate <= 0:
            msg = f"Exchange rate must be positive, got {self.exchange_rate}"
            raise ValueError(msg)

    @property
    def target_amount(self) -> Decimal:
        """Compute the amount received by the target node."""
        return self.amount * self.exchange_rate


__all__ = ["Vector"]
