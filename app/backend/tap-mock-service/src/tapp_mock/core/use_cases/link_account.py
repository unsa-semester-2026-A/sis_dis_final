"""LinkAccountUseCase — account linking, status query, and unlinking.

This use case satisfies the ILinkAccountPort inbound protocol. It is the sole
consumer of IMockStorePort for account-related operations and contains zero
framework imports: no FastAPI, no Pydantic, no HTTP concepts.

Responsibilities:
  - Validate that the requested IBAN exists in the mock registry.
  - Enforce the LINKED/UNLINKED state machine.
  - Return immutable result DTOs to the primary adapter.
"""

from __future__ import annotations

from tapp_mock.core.domain.exceptions import (
    AccountAlreadyLinkedError,
    AccountNotFoundError,
)
from tapp_mock.core.domain.models import AccountMock, AccountStatus
from tapp_mock.core.ports.inbound import (
    GetAccountStatusCommand,
    GetAccountStatusResult,
    LinkAccountCommand,
    LinkAccountResult,
    UnlinkAccountCommand,
    UnlinkAccountResult,
)
from tapp_mock.core.ports.outbound import IMockStorePort


def _mask_iban(iban: str) -> str:
    """Return a partially masked IBAN for safe display.

    Keeps the first 6 and last 4 characters; replaces the middle with dots.
    For IBANs shorter than 10 characters the full string is returned unchanged.

    Args:
        iban: The full IBAN string.

    Returns:
        A masked representation such as "PE1234...7890".
    """
    if len(iban) < 10:  # noqa: PLR2004 — magic number is the guard threshold
        return iban
    return f"{iban[:6]}...{iban[-4:]}"


class LinkAccountUseCase:
    """Handles all account lifecycle operations for the TAPP mock.

    This class satisfies the ILinkAccountPort structural protocol without
    inheriting from it, relying on Pyright's runtime_checkable validation
    instead.

    Attributes:
        _store: The outbound port used to read and persist account records.
    """

    def __init__(self, store: IMockStorePort) -> None:
        """Inject the outbound store dependency.

        Args:
            store: Any object that satisfies IMockStorePort. In production
                this will be InMemoryMockStore; in tests it can be any
                compatible mock or stub.
        """
        self._store = store

    # ------------------------------------------------------------------
    # ILinkAccountPort implementation
    # ------------------------------------------------------------------

    def link_account(self, command: LinkAccountCommand) -> LinkAccountResult:
        """Link a bank account to Spondylus via the TAPP mock.

        Lookup sequence:
          1. Search the store for the requested IBAN.
          2. If not found → AccountNotFoundError (TAPP-001).
          3. If already LINKED → AccountAlreadyLinkedError (TAPP-002).
          4. If UNLINKED (previously revoked) → re-link by saving a fresh
             AccountMock with LINKED status and updated linked_at timestamp.
          5. If not yet in the store at all (first-time) → persist new record.

        Note: In the seeded mock, all three pre-loaded accounts are already
        LINKED. Calling link_account on any of them will raise
        AccountAlreadyLinkedError unless they have been explicitly unlinked
        first via unlink_account.

        Args:
            command: Validated command carrying user_id, iban, bank_code,
                alias.

        Returns:
            A LinkAccountResult describing the linked account.

        Raises:
            AccountNotFoundError: If the IBAN is not in the mock registry.
            AccountAlreadyLinkedError: If the account is already LINKED.
        """
        existing = self._store.find_account_by_iban(command.iban)

        if existing is None:
            raise AccountNotFoundError(
                detail=(
                    f"IBAN {command.iban} is not registered in the "
                    "TAPP mock registry."
                )
            )

        if existing.status == AccountStatus.LINKED:
            raise AccountAlreadyLinkedError(
                detail=(
                    f"Account {existing.account_id} with IBAN {command.iban} "
                    "is already in LINKED status."
                )
            )

        # Re-link a previously unlinked account by creating a new immutable
        # instance with refreshed timestamps and LINKED status.
        from datetime import datetime, timezone

        refreshed: AccountMock = AccountMock(
            account_id=existing.account_id,
            user_id=command.user_id,
            iban=existing.iban,
            bank_code=command.bank_code or existing.bank_code,
            alias=command.alias or existing.alias,
            status=AccountStatus.LINKED,
            linked_at=datetime.now(tz=timezone.utc),
            unlinked_at=None,
        )
        saved = self._store.save_account(refreshed)

        return LinkAccountResult(
            account_id=saved.account_id,
            user_id=saved.user_id,
            iban=saved.iban,
            bank_code=saved.bank_code,
            alias=saved.alias,
            status=saved.status,
            linked_at=saved.linked_at,
        )

    def get_account_status(
        self, command: GetAccountStatusCommand
    ) -> GetAccountStatusResult:
        """Return the current linkage status of an account.

        Args:
            command: Input carrying the account_id to look up.

        Returns:
            A GetAccountStatusResult with current status and metadata.

        Raises:
            AccountNotFoundError: If no account matches the given account_id.
        """
        account = self._store.find_account_by_id(command.account_id)

        if account is None:
            raise AccountNotFoundError(
                detail=(
                    f"Account {command.account_id} was not found in the "
                    "TAPP mock registry."
                )
            )

        return GetAccountStatusResult(
            account_id=account.account_id,
            status=account.status,
            bank_code=account.bank_code,
            iban_masked=_mask_iban(account.iban),
            linked_at=account.linked_at,
            unlinked_at=account.unlinked_at,
        )

    def unlink_account(
        self, command: UnlinkAccountCommand
    ) -> UnlinkAccountResult:
        """Revoke the TAPP linkage for a bank account.

        The account must exist in the store (whether LINKED or UNLINKED).
        If it is already UNLINKED the call still succeeds (idempotent
        unlinking) but unlinked_at is refreshed to the current UTC time.

        Args:
            command: Input carrying the account_id to unlink.

        Returns:
            An UnlinkAccountResult confirming the new UNLINKED status.

        Raises:
            AccountNotFoundError: If no account matches the given account_id.
        """
        account = self._store.find_account_by_id(command.account_id)

        if account is None:
            raise AccountNotFoundError(
                detail=(
                    f"Account {command.account_id} was not found in the "
                    "TAPP mock registry."
                )
            )

        unlinked = account.unlink()
        saved = self._store.save_account(unlinked)

        # unlinked_at is guaranteed non-None after .unlink() — assert for
        # Pyright strict so it narrows the type from datetime | None.
        assert saved.unlinked_at is not None, (
            "AccountMock.unlink() must set unlinked_at"
        )

        return UnlinkAccountResult(
            account_id=saved.account_id,
            status=saved.status,
            unlinked_at=saved.unlinked_at,
        )