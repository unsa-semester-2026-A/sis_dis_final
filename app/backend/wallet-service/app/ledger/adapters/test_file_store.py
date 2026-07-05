# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false
"""Tests for the file-based JSON repository adapters."""

from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from app.ledger.adapters.file_store import FileNodeRepository, FileVectorRepository
from app.ledger.core.node import Node
from app.ledger.core.node_type import NodeType
from app.ledger.core.vector import Vector
from app.shared import new_id


class TestFileNodeRepository:
    def test_save_and_find_by_id(self, tmp_path: Path) -> None:
        repo = FileNodeRepository(data_dir=tmp_path)
        node_id = new_id()
        user_id = new_id()
        node = Node(
            id=node_id,
            user_id=user_id,
            name="Savings Account",
            node_type=NodeType.ASSET,
            currency="USD",
        )

        repo.save(node)

        retrieved = repo.find_by_id(node_id)
        assert retrieved is not None
        assert retrieved.id == node.id
        assert retrieved.user_id == node.user_id
        assert retrieved.name == "Savings Account"
        assert retrieved.node_type == NodeType.ASSET
        assert retrieved.currency == "USD"
        assert retrieved.is_active is True

    def test_find_by_id_missing_returns_none(self, tmp_path: Path) -> None:
        repo = FileNodeRepository(data_dir=tmp_path)
        assert repo.find_by_id(new_id()) is None

    def test_find_by_user(self, tmp_path: Path) -> None:
        repo = FileNodeRepository(data_dir=tmp_path)
        user_a = new_id()
        user_b = new_id()

        node_a1 = Node(
            id=new_id(),
            user_id=user_a,
            name="Bank A1",
            node_type=NodeType.ASSET,
            currency="USD",
        )
        node_a2 = Node(
            id=new_id(),
            user_id=user_a,
            name="Cash A2",
            node_type=NodeType.ASSET,
            currency="PEN",
        )
        node_b1 = Node(
            id=new_id(),
            user_id=user_b,
            name="Bank B1",
            node_type=NodeType.ASSET,
            currency="USD",
        )

        repo.save(node_a1)
        repo.save(node_a2)
        repo.save(node_b1)

        user_a_nodes = repo.find_by_user(user_a)
        assert len(user_a_nodes) == 2
        assert {n.id for n in user_a_nodes} == {node_a1.id, node_a2.id}

        user_b_nodes = repo.find_by_user(user_b)
        assert len(user_b_nodes) == 1
        assert user_b_nodes[0].id == node_b1.id


class TestFileVectorRepository:
    def test_append_and_find_by_node(self, tmp_path: Path) -> None:
        repo = FileVectorRepository(data_dir=tmp_path)
        node_src = new_id()
        node_tgt = new_id()
        other_node = new_id()
        now = datetime.now(tz=timezone.utc)

        v1 = Vector(
            id=new_id(),
            lineage_token="l-01",
            source_node_id=node_src,
            target_node_id=node_tgt,
            amount=Decimal("100.00"),
            effective_at=now,
            system_at=now,
        )
        v2 = Vector(
            id=new_id(),
            lineage_token="l-02",
            source_node_id=other_node,
            target_node_id=node_src,
            amount=Decimal("50.00"),
            effective_at=now,
            system_at=now,
        )

        repo.append(v1)
        repo.append(v2)

        # Retrieve vectors for node_src (should include both as source or target)
        src_vectors = repo.find_by_node(node_src)
        assert len(src_vectors) == 2
        assert {v.id for v in src_vectors} == {v1.id, v2.id}

        # Retrieve vectors for other_node (should include only v2)
        other_vectors = repo.find_by_node(other_node)
        assert len(other_vectors) == 1
        assert other_vectors[0].id == v2.id

    def test_find_by_node_with_date_range(self, tmp_path: Path) -> None:
        repo = FileVectorRepository(data_dir=tmp_path)
        node_src = new_id()
        node_tgt = new_id()

        t1 = datetime(2026, 6, 20, 12, 0, tzinfo=timezone.utc)
        t2 = datetime(2026, 6, 21, 12, 0, tzinfo=timezone.utc)
        t3 = datetime(2026, 6, 22, 12, 0, tzinfo=timezone.utc)

        v1 = Vector(
            id=new_id(),
            lineage_token="l-1",
            source_node_id=node_src,
            target_node_id=node_tgt,
            amount=Decimal("10.00"),
            effective_at=t1,
            system_at=t1,
        )
        v2 = Vector(
            id=new_id(),
            lineage_token="l-2",
            source_node_id=node_src,
            target_node_id=node_tgt,
            amount=Decimal("20.00"),
            effective_at=t2,
            system_at=t2,
        )
        v3 = Vector(
            id=new_id(),
            lineage_token="l-3",
            source_node_id=node_src,
            target_node_id=node_tgt,
            amount=Decimal("30.00"),
            effective_at=t3,
            system_at=t3,
        )

        repo.append(v1)
        repo.append(v2)
        repo.append(v3)

        # Range filtering tests
        results = repo.find_by_node(node_src, start=t2)
        assert len(results) == 2
        assert {v.id for v in results} == {v2.id, v3.id}

        results = repo.find_by_node(node_src, end=t2)
        assert len(results) == 2
        assert {v.id for v in results} == {v1.id, v2.id}

        results = repo.find_by_node(node_src, start=t2, end=t2)
        assert len(results) == 1
        assert results[0].id == v2.id

    def test_find_by_lineage(self, tmp_path: Path) -> None:
        repo = FileVectorRepository(data_dir=tmp_path)
        token = "lin-tok-abc"
        now = datetime.now(tz=timezone.utc)

        v1 = Vector(
            id=new_id(),
            lineage_token=token,
            source_node_id=new_id(),
            target_node_id=new_id(),
            amount=Decimal("100"),
            effective_at=now,
            system_at=now,
        )
        v2 = Vector(
            id=new_id(),
            lineage_token=token,
            source_node_id=new_id(),
            target_node_id=new_id(),
            amount=Decimal("100"),
            effective_at=now,
            system_at=now,
        )
        v3 = Vector(
            id=new_id(),
            lineage_token="different-token",
            source_node_id=new_id(),
            target_node_id=new_id(),
            amount=Decimal("100"),
            effective_at=now,
            system_at=now,
        )

        repo.append(v1)
        repo.append(v2)
        repo.append(v3)

        results = repo.find_by_lineage(token)
        assert len(results) == 2
        assert {v.id for v in results} == {v1.id, v2.id}
