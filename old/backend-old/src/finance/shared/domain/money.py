"""Money value object for currency-aware arithmetic."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Self

from finance.shared.errors import CurrencyMismatchError


@dataclass(frozen=True, slots=True)
class Money:
    """Immutable, currency-aware monetary value.

    Uses Decimal for precision. Currency is ISO 4217 (3-char code).
    Arithmetic operations enforce currency homogeneity.

    Attributes:
        amount: The monetary amount as a Decimal.
        currency: ISO 4217 currency code (e.g., 'PEN', 'USD').
    """

    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        """Validate invariants on construction."""
        if len(self.currency) != 3:  # noqa: PLR2004
            msg = f"Currency must be ISO 4217 (3 chars), got '{self.currency}'"
            raise ValueError(msg)

    @classmethod
    def zero(cls, currency: str) -> Self:
        """Create a zero-value Money in the given currency."""
        return cls(amount=Decimal("0"), currency=currency)

    def __add__(self, other: object) -> Money:
        """Add two Money values of the same currency."""
        if not isinstance(other, Money):
            return NotImplemented
        self._assert_same_currency(other)
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def __sub__(self, other: object) -> Money:
        """Subtract two Money values of the same currency."""
        if not isinstance(other, Money):
            return NotImplemented
        self._assert_same_currency(other)
        return Money(amount=self.amount - other.amount, currency=self.currency)

    def __neg__(self) -> Money:
        """Negate the monetary amount."""
        return Money(amount=-self.amount, currency=self.currency)

    def _assert_same_currency(self, other: Money) -> None:
        """Raise if currencies differ."""
        if self.currency != other.currency:
            msg = f"Cannot operate on {self.currency} and {other.currency}"
            raise CurrencyMismatchError(msg)


__all__ = ["Money"]
