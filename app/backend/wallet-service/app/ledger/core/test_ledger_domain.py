"""Tests for ledger domain entities."""

from datetime import datetime, timezone
from decimal import Decimal

import pytest
from app.ledger.core.node import Node
from app.ledger.core.node_type import NodeType
from app.ledger.core.vector import Vector
from app.shared import InvalidAmountError, new_id


class TestNode:
    def test_creation(self) -> None:
        node = Node(
            id=new_id(),
            user_id=new_id(),
            name="Main Bank",
            node_type=NodeType.ASSET,
            currency="PEN",
        )
        assert node.name == "Main Bank"
        assert node.node_type == NodeType.ASSET
        assert node.is_active is True

    def test_empty_name_raises(self) -> None:
        with pytest.raises(ValueError, match="not be empty"):
            Node(
                id=new_id(),
                user_id=new_id(),
                name="  ",
                node_type=NodeType.ASSET,
                currency="PEN",
            )

    def test_empty_string_name_raises(self) -> None:
        with pytest.raises(ValueError, match="not be empty"):
            Node(
                id=new_id(),
                user_id=new_id(),
                name="",
                node_type=NodeType.ASSET,
                currency="PEN",
            )

    def test_invalid_currency_raises(self) -> None:
        with pytest.raises(ValueError, match="ISO 4217"):
            Node(
                id=new_id(),
                user_id=new_id(),
                name="Bank",
                node_type=NodeType.ASSET,
                currency="ABCD",
            )

    def test_unsupported_3_char_currency_raises(self) -> None:
        with pytest.raises(ValueError, match="ISO 4217"):
            Node(
                id=new_id(),
                user_id=new_id(),
                name="Bank",
                node_type=NodeType.ASSET,
                currency="XYZ",
            )

    def test_deactivate(self) -> None:
        node = Node(
            id=new_id(),
            user_id=new_id(),
            name="Bank",
            node_type=NodeType.ASSET,
            currency="PEN",
        )
        deactivated = node.deactivate()
        assert deactivated.is_active is False
        assert node.is_active is True  # original unchanged

    def test_frozen(self) -> None:
        node = Node(
            id=new_id(),
            user_id=new_id(),
            name="Bank",
            node_type=NodeType.ASSET,
            currency="PEN",
        )
        with pytest.raises(AttributeError):
            node.name = "Changed"  # type: ignore[misc]

    def test_all_node_types(self) -> None:
        for nt in NodeType:
            node = Node(
                id=new_id(),
                user_id=new_id(),
                name=f"Node {nt.value}",
                node_type=nt,
                currency="USD",
            )
            assert node.node_type == nt


class TestVector:
    def _make_vector(self, **overrides: object) -> Vector:
        now = datetime.now(tz=timezone.utc)
        defaults: dict[str, object] = {
            "id": new_id(),
            "lineage_token": "lt-001",
            "source_node_id": new_id(),
            "target_node_id": new_id(),
            "amount": Decimal("100"),
            "effective_at": now,
            "system_at": now,
        }
        defaults.update(overrides)
        return Vector(**defaults)  # type: ignore[arg-type]

    def test_creation(self) -> None:
        v = self._make_vector()
        assert v.amount == Decimal("100")
        assert v.exchange_rate == Decimal("1.0")
        assert v.transaction_id is None
        assert v.tags == {}

    def test_zero_amount_raises(self) -> None:
        with pytest.raises(InvalidAmountError):
            self._make_vector(amount=Decimal("0"))

    def test_negative_amount_raises(self) -> None:
        with pytest.raises(InvalidAmountError):
            self._make_vector(amount=Decimal("-5"))

    def test_same_source_target_raises(self) -> None:
        same_id = new_id()
        with pytest.raises(ValueError, match="must differ"):
            self._make_vector(source_node_id=same_id, target_node_id=same_id)

    def test_negative_exchange_rate_raises(self) -> None:
        with pytest.raises(ValueError, match="positive"):
            self._make_vector(exchange_rate=Decimal("-1"))

    def test_zero_exchange_rate_raises(self) -> None:
        with pytest.raises(ValueError, match="positive"):
            self._make_vector(exchange_rate=Decimal("0"))

    def test_target_amount_property(self) -> None:
        v = self._make_vector(amount=Decimal("100"), exchange_rate=Decimal("3.75"))
        assert v.target_amount == Decimal("375.00")

    def test_frozen(self) -> None:
        v = self._make_vector()
        with pytest.raises(AttributeError):
            v.amount = Decimal("999")  # type: ignore[misc]

    def test_with_tags(self) -> None:
        v = self._make_vector(tags={"trip": "arequipa"})
        assert v.tags == {"trip": "arequipa"}

    def test_with_transaction_id(self) -> None:
        tid = new_id()
        v = self._make_vector(transaction_id=tid)
        assert v.transaction_id == tid
