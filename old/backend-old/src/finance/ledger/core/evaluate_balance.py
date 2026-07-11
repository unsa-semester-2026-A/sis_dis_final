"""Use case: evaluate a node's balance from the vector ledger."""

from __future__ import annotations

from decimal import Decimal

from finance.ledger.ports.inbound.evaluate_balance import BalanceQuery
from finance.ledger.ports.outbound.node_repository import NodeRepository
from finance.ledger.ports.outbound.vector_repository import VectorRepository
from finance.shared.domain.money import Money


class EvaluateBalanceUseCase:
    """Computes a node's balance by processing all valid vectors.

    Implements the formula:
        Balance(v) = Σ(inflows.amount × inflows.exchange_rate) − Σ(outflows.amount)

    This is pure mathematical accounting — it ignores categorization
    and always matches the physical bank balance.
    """

    def __init__(
        self,
        node_repo: NodeRepository,
        vector_repo: VectorRepository,
    ) -> None:
        """Initialize with repository ports.

        Args:
            node_repo: Outbound port for node lookups.
            vector_repo: Outbound port for vector queries.
        """
        self._node_repo = node_repo
        self._vector_repo = vector_repo

    def execute(self, query: BalanceQuery) -> Money:
        """Calculate the balance for a given node.

        Args:
            query: Node ID and optional date range.

        Returns:
            The computed Money balance in the node's currency.

        Raises:
            ValueError: If the node does not exist.
        """
        node = self._node_repo.find_by_id(query.node_id)
        if node is None:
            msg = f"Node {query.node_id} not found"
            raise ValueError(msg)

        vectors = self._vector_repo.find_by_node(
            query.node_id,
            start=query.start_date,
            end=query.end_date,
        )

        balance = Decimal("0")
        for v in vectors:
            if v.target_node_id == query.node_id:
                # Inflow: amount × exchange_rate
                balance += v.amount * v.exchange_rate
            if v.source_node_id == query.node_id:
                # Outflow: raw amount
                balance -= v.amount

        return Money(amount=balance, currency=node.currency)


__all__ = ["EvaluateBalanceUseCase"]
