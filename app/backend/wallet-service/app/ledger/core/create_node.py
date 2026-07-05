"""Use case: create a new ledger node."""

from __future__ import annotations

from app.ledger.core.node import Node
from app.ledger.ports.inbound import CreateNodeCommand, CreateNodePort
from app.ledger.ports.outbound import NodeRepository
from app.shared import new_id


class CreateNodeUseCase(CreateNodePort):
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
