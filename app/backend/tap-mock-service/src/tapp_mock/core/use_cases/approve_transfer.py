"""ApproveTransferUseCase — consent approval/rejection and transfer execution.

This is the most critical use case in the mock. It satisfies the
IApproveTransferPort inbound protocol and enforces the full transaction safety
contract of the TAPP simulation:

  1. Consent gate: A transfer can only be executed when its associated consent
     is in APPROVED status. Any other status raises ConsentNotApprovedError.

  2. Forced-failure simulation: Any transfer whose idempotency_key begins with
     the string "fail-" causes InMemoryMockStore.find_transfer_by_idempotency_key
     to raise TappGatewayError before any write occurs. This allows
     wallet-service to exercise its Two-Phase Commit (2PC) rollback logic and
     retry strategies without requiring real external infrastructure.

  3. Idempotency: A duplicate submission (same idempotency_key, different
     transfer_id) raises DuplicateTransferError carrying the existing
     transfer_id, enabling the caller to safely retry and retrieve the
     already-completed record.

  4. State machine enforcement: consent.approve() and consent.reject() each
     return new frozen ConsentMock instances — the use case never mutates
     in-place. It simply overwrites the stored record with the new instance.

No framework imports. No HTTP concepts. Pure domain logic and port interfaces.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from tapp_mock.core.domain.exceptions import (
    ConsentAlreadyProcessedError,
    ConsentNotApprovedError,
    ConsentNotFoundError,
    DuplicateTransferError,
    TransferNotFoundError,
)
from tapp_mock.core.domain.models import (
    ConsentStatus,
    TransferMock,
    TransferStatus,
)
from tapp_mock.core.ports.inbound import (
    ApproveConsentCommand,
    ApproveConsentResult,
    ExecuteTransferCommand,
    ExecuteTransferResult,
    GetTransferCommand,
    GetTransferResult,
    RejectConsentCommand,
    RejectConsentResult,
)
from tapp_mock.core.ports.outbound import IMockStorePort

# ---------------------------------------------------------------------------
# TAPP reference number format
# Produces a human-readable audit trail identifier in the style the spec
# documents: "TAPP-MOCK-YYYYMMDD-<short-uuid>".
# ---------------------------------------------------------------------------
_TAPP_REF_PREFIX: str = "TAPP-MOCK"


def _build_tapp_reference(transfer_id: str, now: datetime) -> str:
    """Build a deterministic BCRP-style reference for a transfer.

    Uses the first 8 characters of the transfer UUID to keep references short
    and readable in logs.

    Args:
        transfer_id: The UUID assigned to the new transfer.
        now: The UTC datetime at the moment of transfer creation.

    Returns:
        A string like "TAPP-MOCK-20260707-f47ac10b".
    """
    date_part: str = now.strftime("%Y%m%d")
    short_id: str = transfer_id.split("-")[0]
    return f"{_TAPP_REF_PREFIX}-{date_part}-{short_id}"


class ApproveTransferUseCase:
    """Handles consent approval/rejection and transfer execution.

    Satisfies IApproveTransferPort via structural subtyping (no inheritance).

    Attributes:
        _store: Outbound port providing read/write access to the mock state.
    """

    def __init__(self, store: IMockStorePort) -> None:
        """Inject the outbound store dependency.

        Args:
            store: Any object satisfying IMockStorePort.
        """
        self._store = store

    # ------------------------------------------------------------------
    # IApproveTransferPort implementation
    # ------------------------------------------------------------------

    def approve_consent(
        self, command: ApproveConsentCommand
    ) -> ApproveConsentResult:
        """Approve a consent that is currently in PENDING status.

        State machine:
          PENDING → APPROVED  (valid transition, recorded here)
          APPROVED → *        (ConsentAlreadyProcessedError)
          REJECTED → *        (ConsentAlreadyProcessedError)
          EXPIRED  → *        (ConsentAlreadyProcessedError)

        Args:
            command: Input carrying the consent_id to approve.

        Returns:
            An ApproveConsentResult with APPROVED status and approved_at
            timestamp.

        Raises:
            ConsentNotFoundError: If the consent_id is not in the store.
            ConsentAlreadyProcessedError: If the consent is not in PENDING
                status.
        """
        consent = self._store.find_consent_by_id(command.consent_id)

        if consent is None:
            raise ConsentNotFoundError(
                detail=(
                    f"Consent {command.consent_id} was not found in the "
                    "TAPP mock registry."
                )
            )

        if consent.status != ConsentStatus.PENDING:
            raise ConsentAlreadyProcessedError(
                detail=(
                    f"Consent {command.consent_id} is already in status "
                    f"{consent.status.value} and cannot be approved."
                )
            )

        approved = consent.approve()
        self._store.save_consent(approved)

        # approved_at is guaranteed non-None after .approve() — assert so
        # Pyright strict narrows the type from datetime | None.
        assert approved.approved_at is not None, (
            "ConsentMock.approve() must set approved_at"
        )

        return ApproveConsentResult(
            consent_id=approved.consent_id,
            status=approved.status,
            approved_at=approved.approved_at,
        )

    def reject_consent(
        self, command: RejectConsentCommand
    ) -> RejectConsentResult:
        """Reject a consent that is currently in PENDING status.

        State machine mirrors approve_consent: only PENDING → REJECTED is
        a valid transition.

        Args:
            command: Input carrying the consent_id to reject.

        Returns:
            A RejectConsentResult with REJECTED status and rejected_at
            timestamp.

        Raises:
            ConsentNotFoundError: If the consent_id is not in the store.
            ConsentAlreadyProcessedError: If the consent is not in PENDING
                status.
        """
        consent = self._store.find_consent_by_id(command.consent_id)

        if consent is None:
            raise ConsentNotFoundError(
                detail=(
                    f"Consent {command.consent_id} was not found in the "
                    "TAPP mock registry."
                )
            )

        if consent.status != ConsentStatus.PENDING:
            raise ConsentAlreadyProcessedError(
                detail=(
                    f"Consent {command.consent_id} is already in status "
                    f"{consent.status.value} and cannot be rejected."
                )
            )

        rejected = consent.reject()
        self._store.save_consent(rejected)

        assert rejected.rejected_at is not None, (
            "ConsentMock.reject() must set rejected_at"
        )

        return RejectConsentResult(
            consent_id=rejected.consent_id,
            status=rejected.status,
            rejected_at=rejected.rejected_at,
        )

    def execute_transfer(
        self, command: ExecuteTransferCommand
    ) -> ExecuteTransferResult:
        """Execute a TAPP-routed interbank transfer.

        This method enforces the full transaction safety contract in the
        following order — the ordering is critical and must not be changed:

        Step 1 — Forced-failure check (via store lookup):
            Delegates to store.find_transfer_by_idempotency_key(), which raises
            TappGatewayError before touching any other state if the
            idempotency_key begins with "fail-". This ensures that NO consent
            state changes and NO transfer records are written when simulating
            a gateway failure, correctly modelling the atomicity requirement
            of the 2PC protocol.

        Step 2 — Idempotency check:
            If the store returns an existing TransferMock for the same
            idempotency_key, a DuplicateTransferError is raised. The caller
            can retrieve the existing transfer via GET /tapp/v1/transfers/{id}.

        Step 3 — Consent resolution:
            The consent referenced by command.consent_id must exist.

        Step 4 — Consent gate:
            The resolved consent must be in APPROVED status.

        Step 5 — Transfer creation:
            A new TransferMock is built, persisted, and returned as
            ExecuteTransferResult. The transfer is set to COMPLETED immediately
            (the mock skips the PROCESSING intermediary state for simplicity).

        Args:
            command: Validated command describing the transfer to execute.

        Returns:
            An ExecuteTransferResult with COMPLETED status and all metadata.

        Raises:
            TappGatewayError: If idempotency_key starts with "fail-".
            DuplicateTransferError: If the idempotency_key is already recorded.
            ConsentNotFoundError: If the consent_id is unknown.
            ConsentNotApprovedError: If the consent is not in APPROVED status.
        """
        # ------------------------------------------------------------------
        # Step 1 + 2: Idempotency check (also triggers forced-failure logic
        # inside the store for "fail-" prefixed keys).
        # ------------------------------------------------------------------
        # NOTE: TappGatewayError propagates transparently from the store —
        # we intentionally do NOT catch it here so it surfaces to the router.
        existing_transfer = self._store.find_transfer_by_idempotency_key(
            command.idempotency_key
        )

        if existing_transfer is not None:
            raise DuplicateTransferError(
                detail=(
                    f"A transfer with idempotency_key "
                    f"'{command.idempotency_key}' already exists."
                ),
                existing_transfer_id=existing_transfer.transfer_id,
            )

        # ------------------------------------------------------------------
        # Step 3: Resolve the consent.
        # ------------------------------------------------------------------
        consent = self._store.find_consent_by_id(command.consent_id)

        if consent is None:
            raise ConsentNotFoundError(
                detail=(
                    f"Consent {command.consent_id} was not found in the "
                    "TAPP mock registry."
                )
            )

        # ------------------------------------------------------------------
        # Step 4: Enforce the consent gate.
        # ------------------------------------------------------------------
        if consent.status != ConsentStatus.APPROVED:
            raise ConsentNotApprovedError(
                detail=(
                    f"Transfer cannot be executed. Consent "
                    f"{command.consent_id} is in status "
                    f"{consent.status.value}. Only APPROVED consents may "
                    "authorise a transfer."
                )
            )

        # ------------------------------------------------------------------
        # Step 5: Build and persist the transfer record.
        # ------------------------------------------------------------------
        now: datetime = datetime.now(tz=timezone.utc)
        transfer_id: str = str(uuid.uuid4())

        transfer: TransferMock = TransferMock(
            transfer_id=transfer_id,
            consent_id=command.consent_id,
            source_account_id=command.source_account_id,
            target_account_id=command.target_account_id,
            amount=command.amount,
            currency=command.currency,
            idempotency_key=command.idempotency_key,
            tapp_reference=_build_tapp_reference(transfer_id, now),
            status=TransferStatus.COMPLETED,
            created_at=now,
            completed_at=now,
        )
        saved: TransferMock = self._store.save_transfer(transfer)

        # completed_at is set to `now` above — assert for Pyright strict.
        assert saved.completed_at is not None, (
            "TransferMock must have completed_at set after execution"
        )

        return ExecuteTransferResult(
            transfer_id=saved.transfer_id,
            consent_id=saved.consent_id,
            source_account_id=saved.source_account_id,
            target_account_id=saved.target_account_id,
            amount=saved.amount,
            currency=saved.currency,
            tapp_reference=saved.tapp_reference,
            status=saved.status,
            completed_at=saved.completed_at,
        )

    def get_transfer(self, command: GetTransferCommand) -> GetTransferResult:
        """Retrieve the current status of a transfer record.

        Args:
            command: Input carrying the transfer_id to look up.

        Returns:
            A GetTransferResult with the full transfer record.

        Raises:
            TransferNotFoundError: If no transfer matches the transfer_id.
        """
        transfer = self._store.find_transfer_by_id(command.transfer_id)

        if transfer is None:
            raise TransferNotFoundError(
                detail=(
                    f"Transfer {command.transfer_id} was not found in the "
                    "TAPP mock registry."
                )
            )

        return GetTransferResult(
            transfer_id=transfer.transfer_id,
            consent_id=transfer.consent_id,
            source_account_id=transfer.source_account_id,
            target_account_id=transfer.target_account_id,
            amount=transfer.amount,
            currency=transfer.currency,
            idempotency_key=transfer.idempotency_key,
            tapp_reference=transfer.tapp_reference,
            status=transfer.status,
            created_at=transfer.created_at,
            completed_at=transfer.completed_at,
        )