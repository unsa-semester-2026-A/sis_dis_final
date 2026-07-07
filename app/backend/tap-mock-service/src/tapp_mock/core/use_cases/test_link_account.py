"""Unit tests for LinkAccountUseCase.

Strategy: inject the real InMemoryMockStore (reset between tests) instead of
a mock object. This gives us true behaviour verification without brittle
call-count assertions, while remaining fully in-memory and deterministic.

Coverage targets:
  - link_account: success (re-link after unlink), IBAN not found, already linked
  - get_account_status: success, not found
  - unlink_account: success, not found, idempotent second unlink
"""

from __future__ import annotations

import pytest

from tapp_mock.adapters.secondary.mock_store import InMemoryMockStore
from tapp_mock.core.domain.exceptions import (
    AccountAlreadyLinkedError,
    AccountNotFoundError,
)
from tapp_mock.core.domain.models import AccountStatus
from tapp_mock.core.ports.inbound import (
    GetAccountStatusCommand,
    LinkAccountCommand,
    UnlinkAccountCommand,
)
from tapp_mock.core.use_cases.link_account import LinkAccountUseCase

# ---------------------------------------------------------------------------
# Fixed seed values taken from SEEDED_IBANS (models.py)
# ---------------------------------------------------------------------------
_LINKED_IBAN = "PE12345678901234567890"
_LINKED_ACCOUNT_ID = "f47ac10b-58cc-4372-a567-0e02b2c3d479"
_LINKED_USER_ID = "a1b2c3d4-0000-0000-0000-000000000001"
_LINKED_BANK_CODE = "BCP"

_UNKNOWN_IBAN = "PE99999999999999999999"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def store() -> InMemoryMockStore:
    """Return a freshly reset InMemoryMockStore for each test."""
    s = InMemoryMockStore()
    s.reset()
    return s


@pytest.fixture()
def use_case(store: InMemoryMockStore) -> LinkAccountUseCase:
    """Return a LinkAccountUseCase wired to the test store."""
    return LinkAccountUseCase(store)


# ===========================================================================
# link_account
# ===========================================================================


class TestLinkAccount:
    """Tests for LinkAccountUseCase.link_account."""

    def test_link_unknown_iban_raises_account_not_found(
        self, use_case: LinkAccountUseCase
    ) -> None:
        """An IBAN not in the seed registry must raise AccountNotFoundError."""
        command = LinkAccountCommand(
            user_id=_LINKED_USER_ID,
            iban=_UNKNOWN_IBAN,
            bank_code="FAKE",
            alias="Cuenta fantasma",
        )
        with pytest.raises(AccountNotFoundError) as exc_info:
            use_case.link_account(command)

        assert exc_info.value.code == "TAPP-001"
        assert _UNKNOWN_IBAN in exc_info.value.detail

    def test_link_already_linked_account_raises_conflict(
        self, use_case: LinkAccountUseCase
    ) -> None:
        """Attempting to link an account that is already LINKED raises
        AccountAlreadyLinkedError."""
        command = LinkAccountCommand(
            user_id=_LINKED_USER_ID,
            iban=_LINKED_IBAN,
            bank_code=_LINKED_BANK_CODE,
            alias="Mi BCP",
        )
        with pytest.raises(AccountAlreadyLinkedError) as exc_info:
            use_case.link_account(command)

        assert exc_info.value.code == "TAPP-002"
        assert _LINKED_IBAN in exc_info.value.detail

    def test_link_previously_unlinked_account_succeeds(
        self,
        store: InMemoryMockStore,
        use_case: LinkAccountUseCase,
    ) -> None:
        """An UNLINKED account can be re-linked and returns LINKED status."""
        # First unlink the seeded account.
        unlink_cmd = UnlinkAccountCommand(account_id=_LINKED_ACCOUNT_ID)
        use_case.unlink_account(unlink_cmd)

        # Now re-link it.
        link_cmd = LinkAccountCommand(
            user_id=_LINKED_USER_ID,
            iban=_LINKED_IBAN,
            bank_code=_LINKED_BANK_CODE,
            alias="BCP Relinkado",
        )
        result = use_case.link_account(link_cmd)

        assert result.account_id == _LINKED_ACCOUNT_ID
        assert result.status == AccountStatus.LINKED
        assert result.iban == _LINKED_IBAN
        assert result.bank_code == _LINKED_BANK_CODE
        assert result.alias == "BCP Relinkado"
        assert result.linked_at is not None

        # Verify persistence: store must reflect the new status.
        persisted = store.find_account_by_id(_LINKED_ACCOUNT_ID)
        assert persisted is not None
        assert persisted.status == AccountStatus.LINKED
        assert persisted.unlinked_at is None

    def test_link_result_contains_all_expected_fields(
        self,
        store: InMemoryMockStore,
        use_case: LinkAccountUseCase,
    ) -> None:
        """The result DTO must include every field defined in LinkAccountResult."""
        # Unlink first so link_account can proceed.
        use_case.unlink_account(UnlinkAccountCommand(account_id=_LINKED_ACCOUNT_ID))

        result = use_case.link_account(
            LinkAccountCommand(
                user_id=_LINKED_USER_ID,
                iban=_LINKED_IBAN,
                bank_code=_LINKED_BANK_CODE,
            )
        )

        assert result.account_id
        assert result.user_id == _LINKED_USER_ID
        assert result.iban == _LINKED_IBAN
        assert result.bank_code == _LINKED_BANK_CODE
        assert result.status == AccountStatus.LINKED
        assert result.linked_at is not None


# ===========================================================================
# get_account_status
# ===========================================================================


class TestGetAccountStatus:
    """Tests for LinkAccountUseCase.get_account_status."""

    def test_get_status_of_seeded_linked_account(
        self, use_case: LinkAccountUseCase
    ) -> None:
        """A seeded account returns LINKED status with a masked IBAN."""
        command = GetAccountStatusCommand(account_id=_LINKED_ACCOUNT_ID)
        result = use_case.get_account_status(command)

        assert result.account_id == _LINKED_ACCOUNT_ID
        assert result.status == AccountStatus.LINKED
        assert result.bank_code == _LINKED_BANK_CODE
        # Masked IBAN must start with the first 6 chars and end with last 4.
        assert result.iban_masked.startswith("PE1234")
        assert result.iban_masked.endswith("7890")
        assert "..." in result.iban_masked
        assert result.linked_at is not None
        assert result.unlinked_at is None

    def test_get_status_of_unknown_account_raises_not_found(
        self, use_case: LinkAccountUseCase
    ) -> None:
        """An unknown account_id raises AccountNotFoundError."""
        command = GetAccountStatusCommand(account_id="00000000-0000-0000-0000-000000000000")
        with pytest.raises(AccountNotFoundError) as exc_info:
            use_case.get_account_status(command)

        assert exc_info.value.code == "TAPP-001"

    def test_get_status_after_unlink_shows_unlinked(
        self, use_case: LinkAccountUseCase
    ) -> None:
        """After unlinking, get_account_status returns UNLINKED with unlinked_at."""
        use_case.unlink_account(UnlinkAccountCommand(account_id=_LINKED_ACCOUNT_ID))

        result = use_case.get_account_status(
            GetAccountStatusCommand(account_id=_LINKED_ACCOUNT_ID)
        )

        assert result.status == AccountStatus.UNLINKED
        assert result.unlinked_at is not None


# ===========================================================================
# unlink_account
# ===========================================================================


class TestUnlinkAccount:
    """Tests for LinkAccountUseCase.unlink_account."""

    def test_unlink_linked_account_succeeds(
        self,
        store: InMemoryMockStore,
        use_case: LinkAccountUseCase,
    ) -> None:
        """Unlinking a LINKED account returns UNLINKED status."""
        command = UnlinkAccountCommand(account_id=_LINKED_ACCOUNT_ID)
        result = use_case.unlink_account(command)

        assert result.account_id == _LINKED_ACCOUNT_ID
        assert result.status == AccountStatus.UNLINKED
        assert result.unlinked_at is not None

        # Verify persistence.
        persisted = store.find_account_by_id(_LINKED_ACCOUNT_ID)
        assert persisted is not None
        assert persisted.status == AccountStatus.UNLINKED
        assert persisted.unlinked_at is not None

    def test_unlink_unknown_account_raises_not_found(
        self, use_case: LinkAccountUseCase
    ) -> None:
        """An unknown account_id raises AccountNotFoundError."""
        command = UnlinkAccountCommand(account_id="00000000-0000-0000-0000-000000000000")
        with pytest.raises(AccountNotFoundError) as exc_info:
            use_case.unlink_account(command)

        assert exc_info.value.code == "TAPP-001"

    def test_unlink_already_unlinked_account_is_idempotent(
        self, use_case: LinkAccountUseCase
    ) -> None:
        """Unlinking an already-UNLINKED account succeeds and refreshes
        unlinked_at."""
        cmd = UnlinkAccountCommand(account_id=_LINKED_ACCOUNT_ID)

        first = use_case.unlink_account(cmd)
        second = use_case.unlink_account(cmd)

        assert second.status == AccountStatus.UNLINKED
        # Second unlink_at must be >= first (time never goes backward).
        assert second.unlinked_at >= first.unlinked_at

    def test_all_three_seeded_accounts_can_be_unlinked(
        self, use_case: LinkAccountUseCase
    ) -> None:
        """Every pre-seeded account is independently unlinkable."""
        ids = [
            "f47ac10b-58cc-4372-a567-0e02b2c3d479",
            "c9d8e7f6-0000-0000-0000-000000000002",
            "d1e2f3a4-0000-0000-0000-000000000003",
        ]
        for account_id in ids:
            result = use_case.unlink_account(
                UnlinkAccountCommand(account_id=account_id)
            )
            assert result.status == AccountStatus.UNLINKED