"""Unit tests for ApproveTransferUseCase.

Coverage targets:
  - approve_consent: success, not found, already processed (approved/rejected)
  - reject_consent:  success, not found, already processed
  - execute_transfer: success, forced failure (fail- prefix), duplicate key,
                      consent not found, consent not approved (pending/rejected)
  - get_transfer:    success, not found
"""

from __future__ import annotations

import pytest

from tapp_mock.adapters.secondary.mock_store import InMemoryMockStore
from tapp_mock.core.domain.exceptions import (
    ConsentAlreadyProcessedError,
    ConsentNotApprovedError,
    ConsentNotFoundError,
    DuplicateTransferError,
    TappGatewayError,
    TransferNotFoundError,
)
from tapp_mock.core.domain.models import ConsentStatus, TransferStatus
from tapp_mock.core.ports.inbound import (
    ApproveConsentCommand,
    ExecuteTransferCommand,
    GetTransferCommand,
    RejectConsentCommand,
    RequestConsentCommand,
)
from tapp_mock.core.use_cases.approve_transfer import ApproveTransferUseCase
from tapp_mock.core.use_cases.request_consent import RequestConsentUseCase

# ---------------------------------------------------------------------------
# Fixed seed values
# ---------------------------------------------------------------------------
_SOURCE_ID = "f47ac10b-58cc-4372-a567-0e02b2c3d479"
_TARGET_ID = "c9d8e7f6-0000-0000-0000-000000000002"
_USER_ID = "a1b2c3d4-0000-0000-0000-000000000001"
_UNKNOWN_ID = "00000000-0000-0000-0000-000000000000"

_CONSENT_CMD = RequestConsentCommand(
    user_id=_USER_ID,
    source_account_id=_SOURCE_ID,
    target_account_id=_TARGET_ID,
    amount=250.00,
    currency="PEN",
    description="Pago de alquiler",
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
def approve_use_case(store: InMemoryMockStore) -> ApproveTransferUseCase:
    """Return ApproveTransferUseCase wired to the test store."""
    return ApproveTransferUseCase(store)


@pytest.fixture()
def consent_use_case(store: InMemoryMockStore) -> RequestConsentUseCase:
    """Return RequestConsentUseCase sharing the same store."""
    return RequestConsentUseCase(store)


@pytest.fixture()
def pending_consent_id(
    consent_use_case: RequestConsentUseCase,
) -> str:
    """Create a PENDING consent and return its consent_id."""
    result = consent_use_case.request_consent(_CONSENT_CMD)
    return result.consent_id


@pytest.fixture()
def approved_consent_id(
    pending_consent_id: str,
    approve_use_case: ApproveTransferUseCase,
) -> str:
    """Approve the pending consent and return its consent_id."""
    approve_use_case.approve_consent(
        ApproveConsentCommand(consent_id=pending_consent_id)
    )
    return pending_consent_id


# ===========================================================================
# approve_consent
# ===========================================================================


class TestApproveConsent:
    """Tests for ApproveTransferUseCase.approve_consent."""

    def test_approve_pending_consent_succeeds(
        self,
        pending_consent_id: str,
        approve_use_case: ApproveTransferUseCase,
    ) -> None:
        """Approving a PENDING consent transitions it to APPROVED."""
        result = approve_use_case.approve_consent(
            ApproveConsentCommand(consent_id=pending_consent_id)
        )

        assert result.consent_id == pending_consent_id
        assert result.status == ConsentStatus.APPROVED
        assert result.approved_at is not None

    def test_approve_persists_status_in_store(
        self,
        store: InMemoryMockStore,
        pending_consent_id: str,
        approve_use_case: ApproveTransferUseCase,
    ) -> None:
        """After approval the store must reflect APPROVED status."""
        approve_use_case.approve_consent(
            ApproveConsentCommand(consent_id=pending_consent_id)
        )
        persisted = store.find_consent_by_id(pending_consent_id)

        assert persisted is not None
        assert persisted.status == ConsentStatus.APPROVED
        assert persisted.approved_at is not None
        assert persisted.rejected_at is None

    def test_approve_unknown_consent_raises_not_found(
        self, approve_use_case: ApproveTransferUseCase
    ) -> None:
        """Approving an unknown consent_id raises ConsentNotFoundError."""
        with pytest.raises(ConsentNotFoundError) as exc_info:
            approve_use_case.approve_consent(
                ApproveConsentCommand(consent_id=_UNKNOWN_ID)
            )
        assert exc_info.value.code == "TAPP-010"

    def test_approve_already_approved_consent_raises_conflict(
        self,
        approved_consent_id: str,
        approve_use_case: ApproveTransferUseCase,
    ) -> None:
        """Approving an already-APPROVED consent raises ConsentAlreadyProcessedError."""
        with pytest.raises(ConsentAlreadyProcessedError) as exc_info:
            approve_use_case.approve_consent(
                ApproveConsentCommand(consent_id=approved_consent_id)
            )
        assert exc_info.value.code == "TAPP-011"
        assert "APPROVED" in exc_info.value.detail

    def test_approve_rejected_consent_raises_conflict(
        self,
        pending_consent_id: str,
        approve_use_case: ApproveTransferUseCase,
    ) -> None:
        """Approving an already-REJECTED consent raises ConsentAlreadyProcessedError."""
        approve_use_case.reject_consent(
            RejectConsentCommand(consent_id=pending_consent_id)
        )
        with pytest.raises(ConsentAlreadyProcessedError) as exc_info:
            approve_use_case.approve_consent(
                ApproveConsentCommand(consent_id=pending_consent_id)
            )
        assert exc_info.value.code == "TAPP-011"
        assert "REJECTED" in exc_info.value.detail


# ===========================================================================
# reject_consent
# ===========================================================================


class TestRejectConsent:
    """Tests for ApproveTransferUseCase.reject_consent."""

    def test_reject_pending_consent_succeeds(
        self,
        pending_consent_id: str,
        approve_use_case: ApproveTransferUseCase,
    ) -> None:
        """Rejecting a PENDING consent transitions it to REJECTED."""
        result = approve_use_case.reject_consent(
            RejectConsentCommand(consent_id=pending_consent_id)
        )

        assert result.consent_id == pending_consent_id
        assert result.status == ConsentStatus.REJECTED
        assert result.rejected_at is not None

    def test_reject_persists_status_in_store(
        self,
        store: InMemoryMockStore,
        pending_consent_id: str,
        approve_use_case: ApproveTransferUseCase,
    ) -> None:
        """After rejection the store must reflect REJECTED status."""
        approve_use_case.reject_consent(
            RejectConsentCommand(consent_id=pending_consent_id)
        )
        persisted = store.find_consent_by_id(pending_consent_id)

        assert persisted is not None
        assert persisted.status == ConsentStatus.REJECTED
        assert persisted.rejected_at is not None
        assert persisted.approved_at is None

    def test_reject_unknown_consent_raises_not_found(
        self, approve_use_case: ApproveTransferUseCase
    ) -> None:
        """Rejecting an unknown consent_id raises ConsentNotFoundError."""
        with pytest.raises(ConsentNotFoundError) as exc_info:
            approve_use_case.reject_consent(
                RejectConsentCommand(consent_id=_UNKNOWN_ID)
            )
        assert exc_info.value.code == "TAPP-010"

    def test_reject_already_rejected_consent_raises_conflict(
        self,
        pending_consent_id: str,
        approve_use_case: ApproveTransferUseCase,
    ) -> None:
        """Rejecting an already-REJECTED consent raises ConsentAlreadyProcessedError."""
        approve_use_case.reject_consent(
            RejectConsentCommand(consent_id=pending_consent_id)
        )
        with pytest.raises(ConsentAlreadyProcessedError) as exc_info:
            approve_use_case.reject_consent(
                RejectConsentCommand(consent_id=pending_consent_id)
            )
        assert exc_info.value.code == "TAPP-011"

    def test_reject_approved_consent_raises_conflict(
        self,
        approved_consent_id: str,
        approve_use_case: ApproveTransferUseCase,
    ) -> None:
        """Rejecting an already-APPROVED consent raises ConsentAlreadyProcessedError."""
        with pytest.raises(ConsentAlreadyProcessedError) as exc_info:
            approve_use_case.reject_consent(
                RejectConsentCommand(consent_id=approved_consent_id)
            )
        assert exc_info.value.code == "TAPP-011"


# ===========================================================================
# execute_transfer
# ===========================================================================


class TestExecuteTransfer:
    """Tests for ApproveTransferUseCase.execute_transfer."""

    def _transfer_cmd(
        self, consent_id: str, idempotency_key: str = "txn-test-001"
    ) -> ExecuteTransferCommand:
        return ExecuteTransferCommand(
            consent_id=consent_id,
            source_account_id=_SOURCE_ID,
            target_account_id=_TARGET_ID,
            amount=250.00,
            currency="PEN",
            idempotency_key=idempotency_key,
        )

    def test_success_returns_completed_transfer(
        self,
        approved_consent_id: str,
        approve_use_case: ApproveTransferUseCase,
    ) -> None:
        """A valid command against an APPROVED consent returns COMPLETED."""
        result = approve_use_case.execute_transfer(
            self._transfer_cmd(approved_consent_id)
        )

        assert result.transfer_id
        assert result.consent_id == approved_consent_id
        assert result.source_account_id == _SOURCE_ID
        assert result.target_account_id == _TARGET_ID
        assert result.amount == 250.00
        assert result.currency == "PEN"
        assert result.status == TransferStatus.COMPLETED
        assert result.completed_at is not None
        assert result.tapp_reference.startswith("TAPP-MOCK-")

    def test_transfer_is_persisted_in_store(
        self,
        store: InMemoryMockStore,
        approved_consent_id: str,
        approve_use_case: ApproveTransferUseCase,
    ) -> None:
        """After execution the transfer must be retrievable from the store."""
        result = approve_use_case.execute_transfer(
            self._transfer_cmd(approved_consent_id)
        )
        persisted = store.find_transfer_by_id(result.transfer_id)

        assert persisted is not None
        assert persisted.transfer_id == result.transfer_id
        assert persisted.status == TransferStatus.COMPLETED

    def test_tapp_reference_contains_date_and_short_uuid(
        self,
        approved_consent_id: str,
        approve_use_case: ApproveTransferUseCase,
    ) -> None:
        """The TAPP reference must follow the format TAPP-MOCK-YYYYMMDD-<id>."""
        import re

        result = approve_use_case.execute_transfer(
            self._transfer_cmd(approved_consent_id)
        )
        # e.g. "TAPP-MOCK-20260707-f47ac10b"
        assert re.match(r"TAPP-MOCK-\d{8}-[0-9a-f]+", result.tapp_reference)

    # ------------------------------------------------------------------
    # Forced-failure simulation
    # ------------------------------------------------------------------

    def test_fail_prefix_raises_tapp_gateway_error(
        self,
        approved_consent_id: str,
        approve_use_case: ApproveTransferUseCase,
    ) -> None:
        """An idempotency_key starting with 'fail-' raises TappGatewayError."""
        cmd = self._transfer_cmd(approved_consent_id, idempotency_key="fail-test-001")
        with pytest.raises(TappGatewayError) as exc_info:
            approve_use_case.execute_transfer(cmd)

        assert exc_info.value.code == "TAPP-030"
        assert "fail-" in exc_info.value.detail

    def test_fail_prefix_does_not_persist_any_transfer(
        self,
        store: InMemoryMockStore,
        approved_consent_id: str,
        approve_use_case: ApproveTransferUseCase,
    ) -> None:
        """A forced failure must leave the store completely unchanged."""
        cmd = self._transfer_cmd(approved_consent_id, idempotency_key="fail-atomic")
        with pytest.raises(TappGatewayError):
            approve_use_case.execute_transfer(cmd)

        # No transfer should have been written.
        transfers_in_store = [
            t for t in store._transfers.values()  # noqa: SLF001
            if t.idempotency_key == "fail-atomic"
        ]
        assert len(transfers_in_store) == 0

    def test_fail_prefix_does_not_consume_idempotency_key(
        self,
        store: InMemoryMockStore,
        approved_consent_id: str,
        approve_use_case: ApproveTransferUseCase,
    ) -> None:
        """After a forced failure the same idempotency_key must still be available
        so that a retry (with a non-fail- key) can succeed."""
        with pytest.raises(TappGatewayError):
            approve_use_case.execute_transfer(
                self._transfer_cmd(approved_consent_id, idempotency_key="fail-retry")
            )
        # Verify idempotency index was NOT polluted.
        assert "fail-retry" not in store._idempotency_index  # noqa: SLF001

    # ------------------------------------------------------------------
    # Idempotency
    # ------------------------------------------------------------------

    def test_duplicate_idempotency_key_raises_duplicate_error(
        self,
        approved_consent_id: str,
        approve_use_case: ApproveTransferUseCase,
    ) -> None:
        """Re-submitting the same idempotency_key raises DuplicateTransferError."""
        cmd = self._transfer_cmd(approved_consent_id, idempotency_key="dup-key-001")
        first = approve_use_case.execute_transfer(cmd)

        with pytest.raises(DuplicateTransferError) as exc_info:
            approve_use_case.execute_transfer(cmd)

        assert exc_info.value.code == "TAPP-021"
        assert exc_info.value.existing_transfer_id == first.transfer_id

    def test_different_idempotency_keys_produce_independent_transfers(
        self,
        consent_use_case: RequestConsentUseCase,
        approve_use_case: ApproveTransferUseCase,
    ) -> None:
        """Two transfers with distinct idempotency_keys are both accepted."""
        # Need two separate APPROVED consents (one consent → one transfer).
        c1_id = consent_use_case.request_consent(_CONSENT_CMD).consent_id
        approve_use_case.approve_consent(ApproveConsentCommand(consent_id=c1_id))

        c2_id = consent_use_case.request_consent(_CONSENT_CMD).consent_id
        approve_use_case.approve_consent(ApproveConsentCommand(consent_id=c2_id))

        r1 = approve_use_case.execute_transfer(
            self._transfer_cmd(c1_id, idempotency_key="key-alpha")
        )
        r2 = approve_use_case.execute_transfer(
            self._transfer_cmd(c2_id, idempotency_key="key-beta")
        )

        assert r1.transfer_id != r2.transfer_id

    # ------------------------------------------------------------------
    # Consent gate
    # ------------------------------------------------------------------

    def test_execute_with_unknown_consent_raises_not_found(
        self, approve_use_case: ApproveTransferUseCase
    ) -> None:
        """A transfer referencing an unknown consent_id raises ConsentNotFoundError."""
        cmd = self._transfer_cmd(_UNKNOWN_ID, idempotency_key="no-consent-key")
        with pytest.raises(ConsentNotFoundError) as exc_info:
            approve_use_case.execute_transfer(cmd)
        assert exc_info.value.code == "TAPP-010"

    def test_execute_with_pending_consent_raises_not_approved(
        self,
        pending_consent_id: str,
        approve_use_case: ApproveTransferUseCase,
    ) -> None:
        """A transfer against a PENDING consent raises ConsentNotApprovedError."""
        cmd = self._transfer_cmd(pending_consent_id, idempotency_key="pending-key")
        with pytest.raises(ConsentNotApprovedError) as exc_info:
            approve_use_case.execute_transfer(cmd)
        assert exc_info.value.code == "TAPP-012"
        assert "PENDING" in exc_info.value.detail

    def test_execute_with_rejected_consent_raises_not_approved(
        self,
        pending_consent_id: str,
        approve_use_case: ApproveTransferUseCase,
    ) -> None:
        """A transfer against a REJECTED consent raises ConsentNotApprovedError."""
        approve_use_case.reject_consent(
            RejectConsentCommand(consent_id=pending_consent_id)
        )
        cmd = self._transfer_cmd(pending_consent_id, idempotency_key="rejected-key")
        with pytest.raises(ConsentNotApprovedError) as exc_info:
            approve_use_case.execute_transfer(cmd)
        assert exc_info.value.code == "TAPP-012"
        assert "REJECTED" in exc_info.value.detail


# ===========================================================================
# get_transfer
# ===========================================================================


class TestGetTransfer:
    """Tests for ApproveTransferUseCase.get_transfer."""

    def test_get_existing_transfer_returns_full_record(
        self,
        approved_consent_id: str,
        approve_use_case: ApproveTransferUseCase,
    ) -> None:
        """get_transfer returns all fields for an existing transfer."""
        created = approve_use_case.execute_transfer(
            ExecuteTransferCommand(
                consent_id=approved_consent_id,
                source_account_id=_SOURCE_ID,
                target_account_id=_TARGET_ID,
                amount=250.00,
                currency="PEN",
                idempotency_key="get-transfer-test",
            )
        )
        result = approve_use_case.get_transfer(
            GetTransferCommand(transfer_id=created.transfer_id)
        )

        assert result.transfer_id == created.transfer_id
        assert result.consent_id == approved_consent_id
        assert result.source_account_id == _SOURCE_ID
        assert result.target_account_id == _TARGET_ID
        assert result.amount == 250.00
        assert result.currency == "PEN"
        assert result.idempotency_key == "get-transfer-test"
        assert result.tapp_reference.startswith("TAPP-MOCK-")
        assert result.status == TransferStatus.COMPLETED
        assert result.created_at is not None
        assert result.completed_at is not None

    def test_get_unknown_transfer_raises_not_found(
        self, approve_use_case: ApproveTransferUseCase
    ) -> None:
        """get_transfer with an unknown transfer_id raises TransferNotFoundError."""
        with pytest.raises(TransferNotFoundError) as exc_info:
            approve_use_case.get_transfer(
                GetTransferCommand(transfer_id=_UNKNOWN_ID)
            )
        assert exc_info.value.code == "TAPP-020"