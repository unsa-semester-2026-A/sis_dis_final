"""Use case: emit an append-only financial vector."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from finance.ledger.domain.vector import Vector
from finance.ledger.ports.inbound.emit_vector import EmitVectorCommand
from finance.ledger.ports.outbound.node_repository import NodeRepository
from finance.ledger.ports.outbound.vector_repository import VectorRepository
from finance.shared.domain.types import new_id
from finance.shared.errors import InactiveNodeError


class EmitVectorUseCase:
    """Emits a new financial mutation vector to the append-only ledger.

    Validates that both source and target nodes exist and are active.
    Auto-generates lineage_token and effective_at if not provided.
    """

    def __init__(
        self,
        node_repo: NodeRepository,
        vector_repo: VectorRepository,
    ) -> None:
        """Initialize with repository ports.

        Args:
            node_repo: Outbound port for node lookups.
            vector_repo: Outbound port for vector persistence.
        """
        self._node_repo = node_repo
        self._vector_repo = vector_repo

    def execute(self, command: EmitVectorCommand) -> Vector:
        """Validate nodes and append a new Vector.

        Args:
            command: Vector emission parameters.

        Returns:
            The newly created Vector.

        Raises:
            InactiveNodeError: If source or target node is inactive.
            ValueError: If source or target node does not exist.
        """
        source = self._node_repo.find_by_id(command.source_node_id)
        if source is None:
            msg = f"Source node {command.source_node_id} not found"
            raise ValueError(msg)
        if not source.is_active:
            msg = f"Source node '{source.name}' is inactive"
            raise InactiveNodeError(msg)

        target = self._node_repo.find_by_id(command.target_node_id)
        if target is None:
            msg = f"Target node {command.target_node_id} not found"
            raise ValueError(msg)
        if not target.is_active:
            msg = f"Target node '{target.name}' is inactive"
            raise InactiveNodeError(msg)

        now = datetime.now(tz=timezone.utc)
        lineage_token = command.lineage_token or str(uuid.uuid4())
        effective_at = command.effective_at or now

        vector = Vector(
            id=new_id(),
            lineage_token=lineage_token,
            source_node_id=command.source_node_id,
            target_node_id=command.target_node_id,
            amount=command.amount,
            exchange_rate=command.exchange_rate,
            tags=dict(command.tags),
            effective_at=effective_at,
            system_at=now,
            transaction_id=command.transaction_id,
        )
        self._vector_repo.append(vector)
        return vector


__all__ = ["EmitVectorUseCase"]
