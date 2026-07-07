"""Unit tests for RequestConsentUseCase.

Coverage targets:
  - request_consent: success, source not found, source not linked,
                     target not found, target not linked
  - get_consent: success, not found
"""

from __future__ import annotations

import pytest

from tapp_mock.adapters.secondary.mock_store import InMemoryMockStore
from tapp_mock.core.domain.exceptions import (
    AccountNotFoundError,
    AccountNotLinkedError,
    ConsentNotFoundError,
)
from tapp_mock.core.domain.models import ConsentStatus
from tapp_mock.core.ports.inbound import (
    GetConsentCommand,
    RequestConsentCommand,
    UnlinkAccountCommand,
)
from tapp_mock.core.use_cases.link_account import LinkAccountUseCase
from tapp_mock.core.use_cases.request_consent import RequestConsentUseCase

# ---------------------------------------------------------------------------
# Fixed seed values
# ---------------------------------------------------------------------------
_SOURCE_ID = "f47ac10b-58cc-4372-a567-0e02b2c3d479"   # BCP — user 1
_TARGET_ID = "c9d8e7f6-0000-0000-0000-000000000002"   # BBVA — user 1
_USER_ID = "a1b2c3d4-0000-0000-0000-000000000001"
_UNKNOWN_ID = "00000000-0000-0000-0000-000000000000"

_VALID_COMMAND = RequestConsentCommand(
    user_id=_USER_ID,
    source_account_id=_SOURCE_ID,
    target_account_id=_TARGET_ID,
    amount=250.00,
    currency="PEN",
    description="Pago de alquiler julio",
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def store() -> InMemoryMockStore:
    """Return a freshly reset InMemoryMockStore."""
    s = InMemoryMockStore()
    s.reset()
    return s


@pytest.fixture()
def use_case(store: InMemoryMockStore) -> RequestConsentUseCase:
    """Return a RequestConsentUseCase wired to the test store."""
    return RequestConsentUseCase(store)


@pytest.fixture()
def link_use_case(store: InMemoryMockStore) -> LinkAccountUseCase:
    """Return a LinkAccountUseCase sharing the same store."""
    return LinkAccountUseCase(store)


# ===========================================================================
# request_consent
# ===========================================================================


class TestRequestConsent:
    """Tests for RequestConsentUseCase.request_consent."""

    def test_success_returns_pending_consent(
        self, use_case: RequestConsentUseCase
    ) -> None:
        """A valid command with two LINKED accounts returns a PENDING consent."""
        result = use_case.request_consent(_VALID_COMMAND)

        assert result.consent_id  # non-empty UUID string
        assert result.user_id == _USER_ID
        assert result.source_account_id == _SOURCE_ID
        assert result.target_account_id == _TARGET_ID
        assert result.amount == 250.00
        assert result.currency == "PEN"
        assert result.status == ConsentStatus.PENDING
        assert result.created_at is not None
        assert result.expires_at > result.created_at

    def test_consent_expires_five_minutes_after_creation(
        self, use_case: RequestConsentUseCase
    ) -> None:
        """expires_at must be exactly 5 minutes after created_at."""
        from datetime import timedelta

        result = use_case.request_consent(_VALID_COMMAND)
        delta = result.expires_at - result.created_at
        # Allow a 1-second tolerance for execution time.
        assert abs(delta - timedelta(minutes=5)).total_seconds() < 1

    def test_consent_is_persisted_in_store(
        self,
        store: InMemoryMockStore,
        use_case: RequestConsentUseCase,
    ) -> None:
        """The new consent must be retrievable from the store after creation."""
        result = use_case.request_consent(_VALID_COMMAND)
        persisted = store.find_consent_by_id(result.consent_id)

        assert persisted is not None
        assert persisted.consent_id == result.consent_id
        assert persisted.status == ConsentStatus.PENDING

    def test_each_call_produces_unique_consent_id(
        self, use_case: RequestConsentUseCase
    ) -> None:
        """Two consent requests must produce distinct consent_ids."""
        first = use_case.request_consent(_VALID_COMMAND)
        second = use_case.request_consent(_VALID_COMMAND)
        assert first.consent_id != second.consent_id

    def test_unknown_source_account_raises_not_found(
        self, use_case: RequestConsentUseCase
    ) -> None:
        """A source account_id not in the store raises AccountNotFoundError."""
        command = RequestConsentCommand(
            user_id=_USER_ID,
            source_account_id=_UNKNOWN_ID,
            target_account_id=_TARGET_ID,
            amount=100.00,
            currency="PEN",
        )
        with pytest.raises(AccountNotFoundError) as exc_info:
            use_case.request_consent(command)

        assert exc_info.value.code == "TAPP-001"
        assert _UNKNOWN_ID in exc_info.value.detail

    def test_unknown_target_account_raises_not_found(
        self, use_case: RequestConsentUseCase
    ) -> None:
        """A target account_id not in the store raises AccountNotFoundError."""
        command = RequestConsentCommand(
            user_id=_USER_ID,
            source_account_id=_SOURCE_ID,
            target_account_id=_UNKNOWN_ID,
            amount=100.00,
            currency="PEN",
        )
        with pytest.raises(AccountNotFoundError) as exc_info:
            use_case.request_consent(command)

        assert exc_info.value.code == "TAPP-001"

    def test_unlinked_source_account_raises_not_linked(
        self,
        store: InMemoryMockStore,
        use_case: RequestConsentUseCase,
        link_use_case: LinkAccountUseCase,
    ) -> None:
        """A source account in UNLINKED status raises AccountNotLinkedError."""
        link_use_case.unlink_account(UnlinkAccountCommand(account_id=_SOURCE_ID))

        command = RequestConsentCommand(
            user_id=_USER_ID,
            source_account_id=_SOURCE_ID,
            target_account_id=_TARGET_ID,
            amount=100.00,
            currency="PEN",
        )
        with pytest.raises(AccountNotLinkedError) as exc_info:
            use_case.request_consent(command)

        assert exc_info.value.code == "TAPP-003"

    def test_unlinked_target_account_raises_not_linked(
        self,
        store: InMemoryMockStore,
        use_case: RequestConsentUseCase,
        link_use_case: LinkAccountUseCase,
    ) -> None:
        """A target account in UNLINKED status raises AccountNotLinkedError."""
        link_use_case.unlink_account(UnlinkAccountCommand(account_id=_TARGET_ID))

        command = RequestConsentCommand(
            user_id=_USER_ID,
            source_account_id=_SOURCE_ID,
            target_account_id=_TARGET_ID,
            amount=100.00,
            currency="PEN",
        )
        with pytest.raises(AccountNotLinkedError) as exc_info:
            use_case.request_consent(command)

        assert exc_info.value.code == "TAPP-003"

    def test_consent_description_defaults_to_empty_string(
        self, use_case: RequestConsentUseCase
    ) -> None:
        """Omitting description must not raise and must persist as empty string."""
        command = RequestConsentCommand(
            user_id=_USER_ID,
            source_account_id=_SOURCE_ID,
            target_account_id=_TARGET_ID,
            amount=50.00,
            currency="PEN",
        )
        result = use_case.request_consent(command)
        assert result.consent_id  # no exception


# ===========================================================================
# get_consent
# ===========================================================================


class TestGetConsent:
    """Tests for RequestConsentUseCase.get_consent."""

    def test_get_existing_consent_returns_full_record(
        self, use_case: RequestConsentUseCase
    ) -> None:
        """get_consent returns all fields for an existing consent."""
        created = use_case.request_consent(_VALID_COMMAND)
        result = use_case.get_consent(GetConsentCommand(consent_id=created.consent_id))

        assert result.consent_id == created.consent_id
        assert result.user_id == _USER_ID
        assert result.source_account_id == _SOURCE_ID
        assert result.target_account_id == _TARGET_ID
        assert result.amount == 250.00
        assert result.currency == "PEN"
        assert result.status == ConsentStatus.PENDING
        assert result.approved_at is None
        assert result.rejected_at is None

    def test_get_unknown_consent_raises_not_found(
        self, use_case: RequestConsentUseCase
    ) -> None:
        """get_consent with an unknown consent_id raises ConsentNotFoundError."""
        with pytest.raises(ConsentNotFoundError) as exc_info:
            use_case.get_consent(GetConsentCommand(consent_id=_UNKNOWN_ID))

        assert exc_info.value.code == "TAPP-010"