"""Tests for shared domain primitives."""

import uuid
from decimal import Decimal

import pytest
from app.shared import CurrencyMismatchError, Money, new_id


class TestEntityId:
    def test_new_id_returns_uuid(self) -> None:
        eid = new_id()
        assert isinstance(eid, uuid.UUID)

    def test_new_id_unique(self) -> None:
        assert new_id() != new_id()


class TestMoney:
    def test_creation(self) -> None:
        m = Money(amount=Decimal("100.50"), currency="PEN")
        assert m.amount == Decimal("100.50")
        assert m.currency == "PEN"

    def test_zero_factory(self) -> None:
        m = Money.zero("USD")
        assert m.amount == Decimal("0")
        assert m.currency == "USD"

    def test_add_same_currency(self) -> None:
        a = Money(Decimal("10"), "PEN")
        b = Money(Decimal("20"), "PEN")
        result = a + b
        assert result.amount == Decimal("30")

    def test_sub_same_currency(self) -> None:
        a = Money(Decimal("30"), "PEN")
        b = Money(Decimal("10"), "PEN")
        result = a - b
        assert result.amount == Decimal("20")

    def test_neg(self) -> None:
        m = Money(Decimal("50"), "PEN")
        assert (-m).amount == Decimal("-50")

    def test_add_different_currency_raises(self) -> None:
        a = Money(Decimal("10"), "PEN")
        b = Money(Decimal("10"), "USD")
        with pytest.raises(CurrencyMismatchError):
            _ = a + b

    def test_sub_different_currency_raises(self) -> None:
        a = Money(Decimal("10"), "PEN")
        b = Money(Decimal("10"), "USD")
        with pytest.raises(CurrencyMismatchError):
            _ = a - b

    def test_invalid_currency_length(self) -> None:
        with pytest.raises(ValueError, match="ISO 4217"):
            Money(Decimal("10"), "PESO")

    def test_unsupported_currency_code(self) -> None:
        with pytest.raises(ValueError, match="Unsupported or invalid ISO 4217"):
            Money(Decimal("10"), "ARS")

    def test_currency_exponent_validation(self) -> None:
        # PEN allows 2 decimal places, 3 is invalid
        with pytest.raises(ValueError, match="decimal places"):
            Money(Decimal("10.001"), "PEN")

        # CLP allows 0 decimal places, 1 is invalid
        with pytest.raises(ValueError, match="decimal places"):
            Money(Decimal("10.5"), "CLP")

        # BHD allows 3 decimal places, 4 is invalid
        with pytest.raises(ValueError, match="decimal places"):
            Money(Decimal("10.0001"), "BHD")

        # Valid exponents should not raise
        assert Money(Decimal("10.00"), "PEN").amount == Decimal("10.00")
        assert Money(Decimal("10"), "CLP").amount == Decimal("10")
        assert Money(Decimal("10.123"), "BHD").amount == Decimal("10.123")

    def test_frozen(self) -> None:
        m = Money(Decimal("10"), "PEN")
        with pytest.raises(AttributeError):
            m.amount = Decimal("20")  # type: ignore[misc]

    def test_add_non_money_returns_not_implemented(self) -> None:
        m = Money(Decimal("10"), "PEN")
        assert m.__add__(42) is NotImplemented
