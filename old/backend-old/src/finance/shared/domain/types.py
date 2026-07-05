"""Shared primitive domain types."""

from __future__ import annotations

import uuid
from typing import NewType

EntityId = NewType("EntityId", uuid.UUID)
"""Strongly-typed unique identifier for domain entities."""


def new_id() -> EntityId:
    """Generate a new unique entity identifier."""
    return EntityId(uuid.uuid4())


__all__ = ["EntityId", "new_id"]
