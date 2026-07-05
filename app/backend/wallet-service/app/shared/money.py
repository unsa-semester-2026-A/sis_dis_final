"""Money value object for currency-aware arithmetic."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Self

from app.shared.errors import CurrencyMismatchError

# Map of supported ISO 4217 currency codes to their allowed decimal places
SUPPORTED_CURRENCIES: dict[str, int] = {
    "PEN": 2,  # Sol peruano
    "USD": 2,  # Dólar estadounidense
    "CLP": 0,  # Peso chileno
    "EUR": 2,  # Euro
    "JPY": 0,  # Yen japonés
    "BHD": 3,  # Dinar bahreiní
}


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
        """Validate invariants on construction.

        Raises:
            ValueError: If the currency is unsupported or the amount exceeds
                the allowed decimal places for the currency.
        """
        if self.currency not in SUPPORTED_CURRENCIES:
            msg = f"Unsupported or invalid ISO 4217 currency code '{self.currency}'"
            raise ValueError(msg)

        allowed_decimals = SUPPORTED_CURRENCIES[self.currency]
        exponent = self.amount.as_tuple().exponent
        scale = -exponent if isinstance(exponent, int) and exponent < 0 else 0

        if scale > allowed_decimals:
            msg = (
                f"Amount {self.amount} has {scale} decimal places, "
                f"but currency {self.currency} only allows up to {allowed_decimals}."
            )
            raise ValueError(msg)

    @classmethod
    def zero(cls, currency: str) -> Self:
        """Create a zero-value Money in the given currency.

        Args:
            currency: The ISO 4217 currency code.

        Returns:
            Money: A Money instance with zero amount.
        """
        return cls(amount=Decimal("0"), currency=currency)

    def __add__(self, other: object) -> Money:
        """Add two Money values of the same currency.

        Args:
            other: The other Money value to add.

        Returns:
            Money: The sum of the two Money values.
        """
        if not isinstance(other, Money):
            return NotImplemented
        self._assert_same_currency(other)
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def __sub__(self, other: object) -> Money:
        """Subtract two Money values of the same currency.

        Args:
            other: The other Money value to subtract.

        Returns:
            Money: The difference of the two Money values.
        """
        if not isinstance(other, Money):
            return NotImplemented
        self._assert_same_currency(other)
        return Money(amount=self.amount - other.amount, currency=self.currency)

    def __neg__(self) -> Money:
        """Negate the monetary amount.

        Returns:
            Money: A Money instance with negated amount.
        """
        return Money(amount=-self.amount, currency=self.currency)

    def _assert_same_currency(self, other: Money) -> None:
        """Raise if currencies differ.

        Args:
            other: The other Money value to compare currency with.

        Raises:
            CurrencyMismatchError: If the currencies differ.
        """
        if self.currency != other.currency:
            msg = f"Cannot operate on {self.currency} and {other.currency}"
            raise CurrencyMismatchError(msg)


__all__ = ["Money"]
