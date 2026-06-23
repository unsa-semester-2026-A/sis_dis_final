"""Shared domain primitives."""

from finance.shared.domain.money import Money
from finance.shared.domain.types import EntityId, new_id

__all__ = ["EntityId", "Money", "new_id"]
