"""Outbound port definitions for the TAPP mock service.

This module defines the abstract contracts (typing.Protocol) that the core
use cases depend on when they need to read or write state. By coding against
these protocols — not concrete classes — the core remains fully decoupled from
the infrastructure adapter that implements them.

Following the Dependency Inversion Principle and the Hexagonal Architecture
adopted by the rest of the Spondylus backend, any secondary adapter (e.g.
InMemoryMockStore, a future SQLite store, or a real TAPP HTTP client) need
only satisfy the structural subtyping enforced by these Protocol classes.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from tapp_mock.core.domain.models import (
    AccountMock,
    ConsentMock,
    TransferMock,
)


@runtime_checkable
class IMockStorePort(Protocol):
    """Contract for the state store consumed by all TAPP mock use cases.

    This is the single outbound port of the service. It provides read and
    write access to the three aggregate roots: accounts, consents, and
    transfers.

    All methods are synchronous. If an async store is needed in the future,
    a new protocol (IAsyncMockStorePort) should be introduced rather than
    modifying this one.
    """

    # ------------------------------------------------------------------
    # Account operations
    # ------------------------------------------------------------------

    def find_account_by_iban(self, iban: str) -> AccountMock | None:
        """Look up a linked account by its IBAN.

        Args:
            iban: The full IBAN string to search for.

        Returns:
            The matching AccountMock if found, otherwise None.
        """
        ...

    def find_account_by_id(self, account_id: str) -> AccountMock | None:
        """Look up a linked account by its internal UUID.

        Args:
            account_id: The UUID string of the account linkage record.

        Returns:
            The matching AccountMock if found, otherwise None.
        """
        ...

    def save_account(self, account: AccountMock) -> AccountMock:
        """Persist or replace an account record.

        If an account with the same account_id already exists it is
        overwritten (used for status transitions such as UNLINKED).

        Args:
            account: The AccountMock instance to persist.

        Returns:
            The persisted AccountMock (same object in the in-memory
            implementation).
        """
        ...

    # ------------------------------------------------------------------
    # Consent operations
    # ------------------------------------------------------------------

    def find_consent_by_id(self, consent_id: str) -> ConsentMock | None:
        """Look up a consent request by its UUID.

        Args:
            consent_id: The UUID string of the consent.

        Returns:
            The matching ConsentMock if found, otherwise None.
        """
        ...

    def save_consent(self, consent: ConsentMock) -> ConsentMock:
        """Persist or replace a consent record.

        Args:
            consent: The ConsentMock instance to persist.

        Returns:
            The persisted ConsentMock.
        """
        ...

    # ------------------------------------------------------------------
    # Transfer operations
    # ------------------------------------------------------------------

    def find_transfer_by_id(self, transfer_id: str) -> TransferMock | None:
        """Look up a transfer by its UUID.

        Args:
            transfer_id: The UUID string of the transfer.

        Returns:
            The matching TransferMock if found, otherwise None.
        """
        ...

    def find_transfer_by_idempotency_key(
        self, idempotency_key: str
    ) -> TransferMock | None:
        """Look up a transfer by its client-supplied idempotency key.

        This method is used to detect duplicate submission attempts and
        implement at-most-once semantics.

        Args:
            idempotency_key: The unique key provided by the caller.

        Returns:
            The matching TransferMock if found, otherwise None.
        """
        ...

    def save_transfer(self, transfer: TransferMock) -> TransferMock:
        """Persist a new transfer record.

        Args:
            transfer: The TransferMock instance to persist.

        Returns:
            The persisted TransferMock.
        """
        ...