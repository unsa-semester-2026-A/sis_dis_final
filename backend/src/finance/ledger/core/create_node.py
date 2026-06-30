"""Use case: create a new ledger node."""

from __future__ import annotations

from finance.ledger.domain.node import Node
from finance.ledger.ports.inbound.create_node import CreateNodeCommand
from finance.ledger.ports.outbound.node_repository import NodeRepository
from finance.shared.domain.types import new_id


class CreateNodeUseCase:
    """Creates a new financial node and persists it.

    This use case is framework-agnostic. It receives a command,
    constructs the domain entity, and delegates persistence
    to the injected NodeRepository port.
    """

    def __init__(self, node_repo: NodeRepository) -> None:
        """Initialize with a node repository.

        Args:
            node_repo: Outbound port for node persistence.
        """
        self._node_repo = node_repo

    def execute(self, command: CreateNodeCommand) -> Node:
        """Create and persist a new Node.

        Args:
            command: Creation parameters.

        Returns:
            The newly created Node.
        """
        node = Node(
            id=new_id(),
            user_id=command.user_id,
            name=command.name,
            node_type=command.node_type,
            currency=command.currency,
        )
        self._node_repo.save(node)
        return node


__all__ = ["CreateNodeUseCase"]
