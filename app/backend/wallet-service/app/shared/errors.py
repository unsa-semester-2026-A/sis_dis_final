"""Base domain error hierarchy."""


class DomainError(Exception):
    """Base exception for all domain-level errors."""


class CurrencyMismatchError(DomainError):
    """Raised when operating on Money with different currencies."""


class InactiveNodeError(DomainError):
    """Raised when attempting to use a deactivated ledger node."""


class InvalidAmountError(DomainError):
    """Raised when a monetary amount violates domain invariants."""
