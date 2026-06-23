"""White-box tests for ledger use cases."""

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from finance.ledger.domain import Node, NodeType, Vector
from finance.ledger.ports.inbound import (
    BalanceQuery,
    CreateNodeCommand,
    EmitVectorCommand,
)
from finance.shared.domain import EntityId, Money, new_id
from finance.shared.errors import InactiveNodeError


# ---------------------------------------------------------------------------
# In-memory repository stubs (test doubles)
# ---------------------------------------------------------------------------


class InMemoryNodeRepository:
    """In-memory NodeRepository for testing."""

    def __init__(self) -> None:
        self._store: dict[EntityId, Node] = {}

    def save(self, node: Node) -> None:
        self._store[node.id] = node

    def find_by_id(self, node_id: EntityId) -> Node | None:
        return self._store.get(node_id)

    def find_by_user(self, user_id: EntityId) -> list[Node]:
        return [n for n in self._store.values() if n.user_id == user_id]


class InMemoryVectorRepository:
    """In-memory VectorRepository for testing."""

    def __init__(self) -> None:
        self._store: list[Vector] = []

    def append(self, vector: Vector) -> None:
        self._store.append(vector)

    def find_by_node(
        self,
        node_id: EntityId,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[Vector]:
        results: list[Vector] = []
        for v in self._store:
            if v.source_node_id != node_id and v.target_node_id != node_id:
                continue
            if start and v.effective_at < start:
                continue
            if end and v.effective_at > end:
                continue
            results.append(v)
        return results

    def find_by_lineage(self, lineage_token: str) -> list[Vector]:
        return [v for v in self._store if v.lineage_token == lineage_token]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def node_repo() -> InMemoryNodeRepository:
    return InMemoryNodeRepository()


@pytest.fixture
def vector_repo() -> InMemoryVectorRepository:
    return InMemoryVectorRepository()


# ---------------------------------------------------------------------------
# CreateNodeUseCase tests
# ---------------------------------------------------------------------------


class TestCreateNodeUseCase:
    def test_creates_and_persists_node(
        self, node_repo: InMemoryNodeRepository
    ) -> None:
        from finance.ledger.core.create_node import CreateNodeUseCase

        uc = CreateNodeUseCase(node_repo=node_repo)
        cmd = CreateNodeCommand(
            user_id=new_id(),
            name="Main Bank",
            node_type=NodeType.ASSET,
            currency="PEN",
        )
        node = uc.execute(cmd)

        assert node.name == "Main Bank"
        assert node.node_type == NodeType.ASSET
        assert node.currency == "PEN"
        assert node.is_active is True
        assert node_repo.find_by_id(node.id) == node

    def test_creates_node_with_all_types(
        self, node_repo: InMemoryNodeRepository
    ) -> None:
        from finance.ledger.core.create_node import CreateNodeUseCase

        uc = CreateNodeUseCase(node_repo=node_repo)
        for nt in NodeType:
            cmd = CreateNodeCommand(
                user_id=new_id(),
                name=f"Node {nt.value}",
                node_type=nt,
                currency="USD",
            )
            node = uc.execute(cmd)
            assert node.node_type == nt


# ---------------------------------------------------------------------------
# EmitVectorUseCase tests
# ---------------------------------------------------------------------------


class TestEmitVectorUseCase:
    def _seed_nodes(
        self, node_repo: InMemoryNodeRepository, user_id: EntityId
    ) -> tuple[Node, Node]:
        source = Node(
            id=new_id(),
            user_id=user_id,
            name="Bank",
            node_type=NodeType.ASSET,
            currency="PEN",
        )
        target = Node(
            id=new_id(),
            user_id=user_id,
            name="Food",
            node_type=NodeType.SINK,
            currency="PEN",
        )
        node_repo.save(source)
        node_repo.save(target)
        return source, target

    def test_emits_and_appends_vector(
        self,
        node_repo: InMemoryNodeRepository,
        vector_repo: InMemoryVectorRepository,
    ) -> None:
        from finance.ledger.core.emit_vector import EmitVectorUseCase

        user_id = new_id()
        source, target = self._seed_nodes(node_repo, user_id)
        uc = EmitVectorUseCase(node_repo=node_repo, vector_repo=vector_repo)

        cmd = EmitVectorCommand(
            source_node_id=source.id,
            target_node_id=target.id,
            amount=Decimal("50"),
        )
        vector = uc.execute(cmd)

        assert vector.amount == Decimal("50")
        assert vector.source_node_id == source.id
        assert vector.target_node_id == target.id
        assert vector.lineage_token  # auto-generated
        assert len(vector_repo.find_by_node(source.id)) == 1

    def test_auto_generates_lineage_token(
        self,
        node_repo: InMemoryNodeRepository,
        vector_repo: InMemoryVectorRepository,
    ) -> None:
        from finance.ledger.core.emit_vector import EmitVectorUseCase

        user_id = new_id()
        source, target = self._seed_nodes(node_repo, user_id)
        uc = EmitVectorUseCase(node_repo=node_repo, vector_repo=vector_repo)

        v1 = uc.execute(EmitVectorCommand(
            source_node_id=source.id,
            target_node_id=target.id,
            amount=Decimal("10"),
        ))
        v2 = uc.execute(EmitVectorCommand(
            source_node_id=source.id,
            target_node_id=target.id,
            amount=Decimal("20"),
        ))
        assert v1.lineage_token != v2.lineage_token

    def test_preserves_explicit_lineage_token(
        self,
        node_repo: InMemoryNodeRepository,
        vector_repo: InMemoryVectorRepository,
    ) -> None:
        from finance.ledger.core.emit_vector import EmitVectorUseCase

        user_id = new_id()
        source, target = self._seed_nodes(node_repo, user_id)
        uc = EmitVectorUseCase(node_repo=node_repo, vector_repo=vector_repo)

        vector = uc.execute(EmitVectorCommand(
            source_node_id=source.id,
            target_node_id=target.id,
            amount=Decimal("10"),
            lineage_token="custom-token-123",
        ))
        assert vector.lineage_token == "custom-token-123"

    def test_rejects_inactive_source_node(
        self,
        node_repo: InMemoryNodeRepository,
        vector_repo: InMemoryVectorRepository,
    ) -> None:
        from finance.ledger.core.emit_vector import EmitVectorUseCase

        user_id = new_id()
        source, target = self._seed_nodes(node_repo, user_id)
        node_repo.save(source.deactivate())
        uc = EmitVectorUseCase(node_repo=node_repo, vector_repo=vector_repo)

        with pytest.raises(InactiveNodeError):
            uc.execute(EmitVectorCommand(
                source_node_id=source.id,
                target_node_id=target.id,
                amount=Decimal("10"),
            ))

    def test_rejects_inactive_target_node(
        self,
        node_repo: InMemoryNodeRepository,
        vector_repo: InMemoryVectorRepository,
    ) -> None:
        from finance.ledger.core.emit_vector import EmitVectorUseCase

        user_id = new_id()
        source, target = self._seed_nodes(node_repo, user_id)
        node_repo.save(target.deactivate())
        uc = EmitVectorUseCase(node_repo=node_repo, vector_repo=vector_repo)

        with pytest.raises(InactiveNodeError):
            uc.execute(EmitVectorCommand(
                source_node_id=source.id,
                target_node_id=target.id,
                amount=Decimal("10"),
            ))


# ---------------------------------------------------------------------------
# EvaluateBalanceUseCase tests
# ---------------------------------------------------------------------------


class TestEvaluateBalanceUseCase:
    def test_balance_single_inflow(
        self,
        node_repo: InMemoryNodeRepository,
        vector_repo: InMemoryVectorRepository,
    ) -> None:
        from finance.ledger.core.evaluate_balance import EvaluateBalanceUseCase

        user_id = new_id()
        bank = Node(
            id=new_id(), user_id=user_id, name="Bank",
            node_type=NodeType.ASSET, currency="PEN",
        )
        salary = Node(
            id=new_id(), user_id=user_id, name="Salary",
            node_type=NodeType.SOURCE, currency="PEN",
        )
        node_repo.save(bank)
        node_repo.save(salary)

        now = datetime.now(tz=timezone.utc)
        vector_repo.append(Vector(
            id=new_id(), lineage_token="lt-1",
            source_node_id=salary.id, target_node_id=bank.id,
            amount=Decimal("1000"), effective_at=now, system_at=now,
        ))

        uc = EvaluateBalanceUseCase(
            node_repo=node_repo, vector_repo=vector_repo
        )
        balance = uc.execute(BalanceQuery(node_id=bank.id))
        assert balance == Money(Decimal("1000"), "PEN")

    def test_balance_inflow_minus_outflow(
        self,
        node_repo: InMemoryNodeRepository,
        vector_repo: InMemoryVectorRepository,
    ) -> None:
        from finance.ledger.core.evaluate_balance import EvaluateBalanceUseCase

        user_id = new_id()
        bank = Node(
            id=new_id(), user_id=user_id, name="Bank",
            node_type=NodeType.ASSET, currency="PEN",
        )
        salary = Node(
            id=new_id(), user_id=user_id, name="Salary",
            node_type=NodeType.SOURCE, currency="PEN",
        )
        food = Node(
            id=new_id(), user_id=user_id, name="Food",
            node_type=NodeType.SINK, currency="PEN",
        )
        for n in (bank, salary, food):
            node_repo.save(n)

        now = datetime.now(tz=timezone.utc)
        vector_repo.append(Vector(
            id=new_id(), lineage_token="lt-1",
            source_node_id=salary.id, target_node_id=bank.id,
            amount=Decimal("1000"), effective_at=now, system_at=now,
        ))
        vector_repo.append(Vector(
            id=new_id(), lineage_token="lt-2",
            source_node_id=bank.id, target_node_id=food.id,
            amount=Decimal("300"), effective_at=now, system_at=now,
        ))

        uc = EvaluateBalanceUseCase(
            node_repo=node_repo, vector_repo=vector_repo
        )
        balance = uc.execute(BalanceQuery(node_id=bank.id))
        assert balance == Money(Decimal("700"), "PEN")

    def test_balance_with_exchange_rate(
        self,
        node_repo: InMemoryNodeRepository,
        vector_repo: InMemoryVectorRepository,
    ) -> None:
        from finance.ledger.core.evaluate_balance import EvaluateBalanceUseCase

        user_id = new_id()
        usd_bank = Node(
            id=new_id(), user_id=user_id, name="USD Bank",
            node_type=NodeType.ASSET, currency="USD",
        )
        pen_bank = Node(
            id=new_id(), user_id=user_id, name="PEN Bank",
            node_type=NodeType.ASSET, currency="PEN",
        )
        for n in (usd_bank, pen_bank):
            node_repo.save(n)

        now = datetime.now(tz=timezone.utc)
        vector_repo.append(Vector(
            id=new_id(), lineage_token="lt-fx",
            source_node_id=pen_bank.id, target_node_id=usd_bank.id,
            amount=Decimal("375"), exchange_rate=Decimal("0.27"),
            effective_at=now, system_at=now,
        ))

        uc = EvaluateBalanceUseCase(
            node_repo=node_repo, vector_repo=vector_repo
        )
        balance = uc.execute(BalanceQuery(node_id=usd_bank.id))
        assert balance == Money(Decimal("101.25"), "USD")

    def test_zero_balance_no_vectors(
        self,
        node_repo: InMemoryNodeRepository,
        vector_repo: InMemoryVectorRepository,
    ) -> None:
        from finance.ledger.core.evaluate_balance import EvaluateBalanceUseCase

        bank = Node(
            id=new_id(), user_id=new_id(), name="Bank",
            node_type=NodeType.ASSET, currency="PEN",
        )
        node_repo.save(bank)

        uc = EvaluateBalanceUseCase(
            node_repo=node_repo, vector_repo=vector_repo
        )
        balance = uc.execute(BalanceQuery(node_id=bank.id))
        assert balance == Money.zero("PEN")
