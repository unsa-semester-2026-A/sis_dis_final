# pyright: reportUnknownMemberType=false
"""File-based JSON storage implementation of Ledger bounded context repositories."""

import json
import uuid
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from finance.ledger.domain.node import Node
from finance.ledger.domain.node_type import NodeType
from finance.ledger.domain.vector import Vector
from finance.ledger.ports.outbound.node_repository import NodeRepository
from finance.ledger.ports.outbound.vector_repository import VectorRepository
from finance.shared.domain.types import EntityId


class FileNodeRepository(NodeRepository):
    """File-based implementation of the NodeRepository port using JSON files."""

    def __init__(self, data_dir: Path | str = "data") -> None:
        """Initialize repository and verify directory existence.

        Args:
            data_dir: Path to base data directory.
        """
        self._data_dir = Path(data_dir) / "nodes"
        self._data_dir.mkdir(parents=True, exist_ok=True)

    def save(self, node: Node) -> None:
        """Persist a node to a JSON file. Upsert semantics.

        Args:
            node: The node entity to save.
        """
        filepath = self._data_dir / f"{node.id}.json"
        data = {
            "id": str(node.id),
            "user_id": str(node.user_id),
            "name": node.name,
            "node_type": node.node_type.value,
            "currency": node.currency,
            "is_active": node.is_active,
        }
        # Write to temporary file first and rename to ensure atomicity
        temp_filepath = filepath.with_suffix(".tmp")
        with open(temp_filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        temp_filepath.rename(filepath)

    def find_by_id(self, node_id: EntityId) -> Node | None:
        """Retrieve a node from its JSON file.

        Args:
            node_id: Unique identifier of the node.

        Returns:
            The Node entity if found, otherwise None.
        """
        filepath = self._data_dir / f"{node_id}.json"
        if not filepath.exists():
            return None
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return Node(
                id=EntityId(uuid.UUID(data["id"])),
                user_id=EntityId(uuid.UUID(data["user_id"])),
                name=str(data["name"]),
                node_type=NodeType(data["node_type"]),
                currency=str(data["currency"]),
                is_active=bool(data["is_active"]),
            )
        except Exception:
            return None

    def find_by_user(self, user_id: EntityId) -> list[Node]:
        """Retrieve all nodes owned by a user.

        Args:
            user_id: Unique identifier of the owner.

        Returns:
            A list of Node entities owned by the user.
        """
        nodes: list[Node] = []
        for filepath in self._data_dir.glob("*.json"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                node_user_id = EntityId(uuid.UUID(data["user_id"]))
                if node_user_id == user_id:
                    nodes.append(
                        Node(
                            id=EntityId(uuid.UUID(data["id"])),
                            user_id=node_user_id,
                            name=str(data["name"]),
                            node_type=NodeType(data["node_type"]),
                            currency=str(data["currency"]),
                            is_active=bool(data["is_active"]),
                        )
                    )
            except Exception:
                continue
        return nodes


class FileVectorRepository(VectorRepository):
    """File-based implementation of the VectorRepository port using JSON files."""

    def __init__(self, data_dir: Path | str = "data") -> None:
        """Initialize repository and verify directory existence.

        Args:
            data_dir: Path to base data directory.
        """
        self._data_dir = Path(data_dir) / "vectors"
        self._data_dir.mkdir(parents=True, exist_ok=True)

    def append(self, vector: Vector) -> None:
        """Append a vector to the ledger by writing to a JSON file.

        Args:
            vector: The vector entity to append.
        """
        filepath = self._data_dir / f"{vector.id}.json"
        data = {
            "id": str(vector.id),
            "lineage_token": vector.lineage_token,
            "source_node_id": str(vector.source_node_id),
            "target_node_id": str(vector.target_node_id),
            "amount": str(vector.amount),
            "exchange_rate": str(vector.exchange_rate),
            "tags": vector.tags,
            "effective_at": vector.effective_at.isoformat(),
            "system_at": vector.system_at.isoformat(),
            "transaction_id": (
                str(vector.transaction_id) if vector.transaction_id else None
            ),
        }
        # Write atomically
        temp_filepath = filepath.with_suffix(".tmp")
        with open(temp_filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        temp_filepath.rename(filepath)

    def find_by_node(
        self,
        node_id: EntityId,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[Vector]:
        """Find all vectors involving a node as source or target.

        Args:
            node_id: Unique identifier of the node.
            start: Optional lower bound (inclusive) filter for effective_at.
            end: Optional upper bound (inclusive) filter for effective_at.

        Returns:
            A sorted list of Vector entities involving the node.
        """
        vectors: list[Vector] = []
        for filepath in self._data_dir.glob("*.json"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                source_node_id = EntityId(uuid.UUID(data["source_node_id"]))
                target_node_id = EntityId(uuid.UUID(data["target_node_id"]))
                if source_node_id != node_id and target_node_id != node_id:
                    continue

                effective_at = datetime.fromisoformat(data["effective_at"])
                if start and effective_at < start:
                    continue
                if end and effective_at > end:
                    continue

                vectors.append(
                    Vector(
                        id=EntityId(uuid.UUID(data["id"])),
                        lineage_token=str(data["lineage_token"]),
                        source_node_id=source_node_id,
                        target_node_id=target_node_id,
                        amount=Decimal(data["amount"]),
                        exchange_rate=Decimal(data["exchange_rate"]),
                        tags=dict(data["tags"]),
                        effective_at=effective_at,
                        system_at=datetime.fromisoformat(data["system_at"]),
                        transaction_id=(
                            EntityId(uuid.UUID(data["transaction_id"]))
                            if data["transaction_id"]
                            else None
                        ),
                    )
                )
            except Exception:
                continue
        # Sort by effective_at for ledger chronology
        vectors.sort(key=lambda v: v.effective_at)
        return vectors

    def find_by_lineage(self, lineage_token: str) -> list[Vector]:
        """Find all vectors sharing a lineage token.

        Args:
            lineage_token: The grouping token.

        Returns:
            A list of Vector entities sharing the lineage token.
        """
        vectors: list[Vector] = []
        for filepath in self._data_dir.glob("*.json"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if data["lineage_token"] != lineage_token:
                    continue

                vectors.append(
                    Vector(
                        id=EntityId(uuid.UUID(data["id"])),
                        lineage_token=str(data["lineage_token"]),
                        source_node_id=EntityId(uuid.UUID(data["source_node_id"])),
                        target_node_id=EntityId(uuid.UUID(data["target_node_id"])),
                        amount=Decimal(data["amount"]),
                        exchange_rate=Decimal(data["exchange_rate"]),
                        tags=dict(data["tags"]),
                        effective_at=datetime.fromisoformat(data["effective_at"]),
                        system_at=datetime.fromisoformat(data["system_at"]),
                        transaction_id=(
                            EntityId(uuid.UUID(data["transaction_id"]))
                            if data["transaction_id"]
                            else None
                        ),
                    )
                )
            except Exception:
                continue
        vectors.sort(key=lambda v: v.system_at)
        return vectors


__all__ = ["FileNodeRepository", "FileVectorRepository"]
