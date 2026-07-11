"""Inbound port for evaluating node balances."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from finance.shared.domain.money import Money
from finance.shared.domain.types import EntityId


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
        """Calculate Balance(v) = sum(inflows * rate) - sum(outflows)."""
        ...


__all__ = ["BalanceQuery", "EvaluateBalancePort"]
