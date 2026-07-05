"""Shared kernel — cross-cutting domain primitives and errors."""

from app.shared.errors import (
    CurrencyMismatchError,
    DomainError,
    InactiveNodeError,
    InvalidAmountError,
)
from app.shared.money import Money
from app.shared.types import EntityId, new_id

__all__ = [
    "CurrencyMismatchError",
    "DomainError",
    "InactiveNodeError",
    "InvalidAmountError",
    "Money",
    "EntityId",
    "new_id",
]
