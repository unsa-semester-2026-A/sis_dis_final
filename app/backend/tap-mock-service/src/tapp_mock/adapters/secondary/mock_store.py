"""In-memory implementation of IMockStorePort.

This secondary adapter satisfies the outbound port contract defined in
tapp_mock.core.ports.outbound. It holds all state in plain Python dicts
(keyed by UUID string) and pre-seeds three bank accounts that match the
fixed UUIDs documented in the technical specification.

Thread safety: This implementation is NOT thread-safe. For the purposes of
the Spondylus MVP — a single-threaded uvicorn worker running in Docker
Compose — this is intentional and acceptable. If multi-worker deployments
are needed, replace this adapter with a Redis-backed or SQLite-backed store
that implements the same IMockStorePort contract.

Forced-failure simulation:
    Any transfer whose idempotency_key starts with the prefix defined in
    FORCED_FAILURE_PREFIX ("fail-") will raise TappGatewayError instead of
    being processed. This allows wallet-service integration tests to exercise
    retry logic and the Two-Phase Commit rollback path without any external
    infrastructure.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from tapp_mock.core.domain.exceptions import TappGatewayError
from tapp_mock.core.domain.models import (
    FORCED_FAILURE_PREFIX,
    SEEDED_IBANS,
    AccountMock,
    AccountStatus,
    ConsentMock,
    TransferMock,
)
from tapp_mock.core.ports.outbound import IMockStorePort

# ---------------------------------------------------------------------------
# Seed timestamp — all pre-loaded accounts share this fixed linked_at value
# so that responses are fully deterministic across restarts.
# ---------------------------------------------------------------------------
_SEED_TIMESTAMP: datetime = datetime(2026, 7, 7, 0, 0, 0, tzinfo=timezone.utc)


def _build_seed_accounts() -> dict[str, AccountMock]:
    """Build the initial account registry from the SEEDED_IBANS manifest.

    Returns:
        A dict mapping account_id -> AccountMock for every pre-seeded entry.
    """
    accounts: dict[str, AccountMock] = {}
    for iban, meta in SEEDED_IBANS.items():
        account = AccountMock(
            account_id=meta["account_id"],
            user_id=meta["user_id"],
            iban=iban,
            bank_code=meta["bank_code"],
            alias=meta["alias"],
            status=AccountStatus.LINKED,
            linked_at=_SEED_TIMESTAMP,
            unlinked_at=None,
        )
        accounts[meta["account_id"]] = account
    return accounts


class InMemoryMockStore:
    """Concrete in-memory store implementing IMockStorePort.

    State is held in three dicts:
      - _accounts: account_id  -> AccountMock
      - _consents: consent_id  -> ConsentMock
      - _transfers: transfer_id -> TransferMock

    Two secondary indices are maintained for efficient lookup:
      - _iban_index: iban -> account_id
      - _idempotency_index: idempotency_key -> transfer_id

    The store is pre-populated at construction time with the three seed
    accounts defined in tapp_mock.core.domain.models.SEEDED_IBANS.
    """

    def __init__(self) -> None:
        """Initialise the store and load seed data."""
        self._accounts: dict[str, AccountMock] = _build_seed_accounts()

        # Build IBAN -> account_id secondary index from seeded accounts.
        self._iban_index: dict[str, str] = {
            account.iban: account.account_id
            for account in self._accounts.values()
        }

        self._consents: dict[str, ConsentMock] = {}
        self._transfers: dict[str, TransferMock] = {}

        # Secondary index: idempotency_key -> transfer_id
        self._idempotency_index: dict[str, str] = {}

    # ------------------------------------------------------------------
    # Account operations
    # ------------------------------------------------------------------

    def find_account_by_iban(self, iban: str) -> AccountMock | None:
        """Look up a linked account by its IBAN.

        Args:
            iban: The full IBAN string to search for.

        Returns:
            The matching AccountMock if found in the IBAN index, else None.
        """
        account_id = self._iban_index.get(iban)
        if account_id is None:
            return None
        return self._accounts.get(account_id)

    def find_account_by_id(self, account_id: str) -> AccountMock | None:
        """Look up a linked account by its internal UUID.

        Args:
            account_id: The UUID string of the account linkage record.

        Returns:
            The matching AccountMock if found, else None.
        """
        return self._accounts.get(account_id)

    def save_account(self, account: AccountMock) -> AccountMock:
        """Persist or replace an account record and keep the IBAN index fresh.

        Args:
            account: The AccountMock instance to persist.

        Returns:
            The persisted AccountMock.
        """
        self._accounts[account.account_id] = account
        # Always keep the IBAN index consistent (even on re-link scenarios).
        self._iban_index[account.iban] = account.account_id
        return account

    # ------------------------------------------------------------------
    # Consent operations
    # ------------------------------------------------------------------

    def find_consent_by_id(self, consent_id: str) -> ConsentMock | None:
        """Look up a consent request by its UUID.

        Args:
            consent_id: The UUID string of the consent.

        Returns:
            The matching ConsentMock if found, else None.
        """
        return self._consents.get(consent_id)

    def save_consent(self, consent: ConsentMock) -> ConsentMock:
        """Persist or replace a consent record.

        Args:
            consent: The ConsentMock instance to persist.

        Returns:
            The persisted ConsentMock.
        """
        self._consents[consent.consent_id] = consent
        return consent

    # ------------------------------------------------------------------
    # Transfer operations
    # ------------------------------------------------------------------

    def find_transfer_by_id(self, transfer_id: str) -> TransferMock | None:
        """Look up a transfer by its UUID.

        Args:
            transfer_id: The UUID string of the transfer.

        Returns:
            The matching TransferMock if found, else None.
        """
        return self._transfers.get(transfer_id)

    def find_transfer_by_idempotency_key(
        self, idempotency_key: str
    ) -> TransferMock | None:
        """Look up a transfer by its client-supplied idempotency key.

        Checks the forced-failure simulation prefix BEFORE querying the index.
        If the key starts with FORCED_FAILURE_PREFIX, a TappGatewayError is
        raised immediately — this is the intended mechanism for testing retry
        and 2PC rollback logic in wallet-service.

        Args:
            idempotency_key: The unique key provided by the caller.

        Returns:
            The matching TransferMock if a non-failing key is found, else None.

        Raises:
            TappGatewayError: If the idempotency_key starts with "fail-".
        """
        if idempotency_key.startswith(FORCED_FAILURE_PREFIX):
            raise TappGatewayError(
                detail=(
                    f"Simulated BCRP gateway timeout triggered by "
                    f"idempotency_key prefix '{FORCED_FAILURE_PREFIX}'. "
                    "Retry after 30 seconds."
                )
            )
        transfer_id = self._idempotency_index.get(idempotency_key)
        if transfer_id is None:
            return None
        return self._transfers.get(transfer_id)

    def save_transfer(self, transfer: TransferMock) -> TransferMock:
        """Persist a new transfer record and update the idempotency index.

        Args:
            transfer: The TransferMock instance to persist.

        Returns:
            The persisted TransferMock.
        """
        self._transfers[transfer.transfer_id] = transfer
        self._idempotency_index[transfer.idempotency_key] = transfer.transfer_id
        return transfer

    # ------------------------------------------------------------------
    # Test helper — not part of IMockStorePort, used only in unit tests
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """Reset the store to its initial seeded state.

        This method is intentionally NOT part of the IMockStorePort protocol.
        It exists solely to allow unit and integration tests to start each
        test case from a clean, deterministic state without re-instantiating
        the store.

        Example::

            store.reset()
            assert store.find_account_by_id("f47ac10b-...") is not None
        """
        self.__init__()  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Type-checking assertion — verified at import time in strict Pyright mode
# ---------------------------------------------------------------------------
_: IMockStorePort = InMemoryMockStore()