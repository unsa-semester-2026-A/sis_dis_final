"""Inbound port definitions for the TAPP mock service.

This module defines:
  1. Command dataclasses — the input DTOs that cross the boundary from the
     primary adapter (FastAPI routers) into the core use cases.
  2. Result dataclasses — the output DTOs that the core returns to the
     primary adapter after executing a command.
  3. Protocol classes — the structural interfaces that each use case must
     satisfy. FastAPI dependency injection resolves these at runtime.

Design rules enforced here:
  - Commands and results are frozen dataclasses: immutable value objects with
    no behaviour, no framework dependency, and full Pyright strict coverage.
  - Protocols use typing.Protocol (structural subtyping) so that use case
    classes are never forced to inherit from an abstract base — they only need
    to implement the required method signature.
  - No FastAPI, Pydantic, or HTTP concepts appear in this module. The
    translation between HTTP schemas and these DTOs is the sole
    responsibility of the primary adapter layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, runtime_checkable

from tapp_mock.core.domain.models import (
    AccountStatus,
    ConsentStatus,
    TransferStatus,
)


# ===========================================================================
# Account — Link
# ===========================================================================


@dataclass(frozen=True)
class LinkAccountCommand:
    """Input DTO for the link-account operation.

    Attributes:
        user_id: UUID of the Spondylus user requesting the linkage.
        iban: Full IBAN string of the bank account to link.
        bank_code: Short bank identifier (e.g. "BCP", "BBVA", "INTERBANK").
        alias: Human-readable label for the account. Defaults to empty string
            when the caller omits it.
    """

    user_id: str
    iban: str
    bank_code: str
    alias: str = ""


@dataclass(frozen=True)
class LinkAccountResult:
    """Output DTO returned after a successful account linkage.

    Attributes:
        account_id: UUID assigned to this linkage record.
        user_id: UUID of the owner.
        iban: Full IBAN string of the linked account.
        bank_code: Short bank identifier.
        alias: Human-readable label.
        status: Always AccountStatus.LINKED on success.
        linked_at: UTC timestamp of when the linkage was recorded.
    """

    account_id: str
    user_id: str
    iban: str
    bank_code: str
    alias: str
    status: AccountStatus
    linked_at: datetime


# ===========================================================================
# Account — Get Status
# ===========================================================================


@dataclass(frozen=True)
class GetAccountStatusCommand:
    """Input DTO for the get-account-status operation.

    Attributes:
        account_id: UUID of the account linkage record to look up.
    """

    account_id: str


@dataclass(frozen=True)
class GetAccountStatusResult:
    """Output DTO returned after a successful account status query.

    Attributes:
        account_id: UUID of the account linkage record.
        status: Current linkage status.
        bank_code: Short bank identifier.
        iban_masked: Partially masked IBAN for display (first 6 + last 4 chars).
        linked_at: UTC timestamp of the original linkage.
        unlinked_at: UTC timestamp of unlinking, or None if still linked.
    """

    account_id: str
    status: AccountStatus
    bank_code: str
    iban_masked: str
    linked_at: datetime
    unlinked_at: datetime | None


# ===========================================================================
# Account — Unlink
# ===========================================================================


@dataclass(frozen=True)
class UnlinkAccountCommand:
    """Input DTO for the unlink-account operation.

    Attributes:
        account_id: UUID of the account linkage record to unlink.
    """

    account_id: str


@dataclass(frozen=True)
class UnlinkAccountResult:
    """Output DTO returned after a successful account unlinking.

    Attributes:
        account_id: UUID of the now-unlinked account.
        status: Always AccountStatus.UNLINKED on success.
        unlinked_at: UTC timestamp of when the unlinking was recorded.
    """

    account_id: str
    status: AccountStatus
    unlinked_at: datetime


# ===========================================================================
# Consent — Request
# ===========================================================================


@dataclass(frozen=True)
class RequestConsentCommand:
    """Input DTO for the request-consent operation.

    Attributes:
        user_id: UUID of the user who must approve the consent.
        source_account_id: UUID of the originating linked account.
        target_account_id: UUID of the destination linked account.
        amount: Transfer amount expressed in the given currency.
        currency: ISO 4217 currency code (e.g. "PEN").
        description: Optional human-readable purpose of the transfer.
    """

    user_id: str
    source_account_id: str
    target_account_id: str
    amount: float
    currency: str
    description: str = ""


@dataclass(frozen=True)
class RequestConsentResult:
    """Output DTO returned after a consent request is successfully registered.

    Attributes:
        consent_id: UUID assigned to this consent record.
        user_id: UUID of the user who must approve.
        source_account_id: UUID of the originating account.
        target_account_id: UUID of the destination account.
        amount: Transfer amount.
        currency: ISO 4217 currency code.
        status: Always ConsentStatus.PENDING on creation.
        expires_at: UTC timestamp after which this consent cannot be approved.
        created_at: UTC timestamp of consent creation.
    """

    consent_id: str
    user_id: str
    source_account_id: str
    target_account_id: str
    amount: float
    currency: str
    status: ConsentStatus
    expires_at: datetime
    created_at: datetime


# ===========================================================================
# Consent — Get
# ===========================================================================


@dataclass(frozen=True)
class GetConsentCommand:
    """Input DTO for the get-consent operation.

    Attributes:
        consent_id: UUID of the consent record to retrieve.
    """

    consent_id: str


@dataclass(frozen=True)
class GetConsentResult:
    """Output DTO for a consent status query.

    Attributes:
        consent_id: UUID of the consent.
        user_id: UUID of the approving user.
        source_account_id: UUID of the originating account.
        target_account_id: UUID of the destination account.
        amount: Transfer amount.
        currency: ISO 4217 currency code.
        status: Current consent lifecycle status.
        expires_at: UTC expiry timestamp.
        created_at: UTC creation timestamp.
        approved_at: UTC approval timestamp, or None.
        rejected_at: UTC rejection timestamp, or None.
    """

    consent_id: str
    user_id: str
    source_account_id: str
    target_account_id: str
    amount: float
    currency: str
    status: ConsentStatus
    expires_at: datetime
    created_at: datetime
    approved_at: datetime | None
    rejected_at: datetime | None


# ===========================================================================
# Consent — Approve / Reject
# ===========================================================================


@dataclass(frozen=True)
class ApproveConsentCommand:
    """Input DTO for the approve-consent operation.

    Attributes:
        consent_id: UUID of the consent to approve.
    """

    consent_id: str


@dataclass(frozen=True)
class ApproveConsentResult:
    """Output DTO returned after a consent is successfully approved.

    Attributes:
        consent_id: UUID of the approved consent.
        status: Always ConsentStatus.APPROVED on success.
        approved_at: UTC timestamp of the approval.
    """

    consent_id: str
    status: ConsentStatus
    approved_at: datetime


@dataclass(frozen=True)
class RejectConsentCommand:
    """Input DTO for the reject-consent operation.

    Attributes:
        consent_id: UUID of the consent to reject.
    """

    consent_id: str


@dataclass(frozen=True)
class RejectConsentResult:
    """Output DTO returned after a consent is successfully rejected.

    Attributes:
        consent_id: UUID of the rejected consent.
        status: Always ConsentStatus.REJECTED on success.
        rejected_at: UTC timestamp of the rejection.
    """

    consent_id: str
    status: ConsentStatus
    rejected_at: datetime


# ===========================================================================
# Transfer — Execute
# ===========================================================================


@dataclass(frozen=True)
class ExecuteTransferCommand:
    """Input DTO for the execute-transfer operation.

    Attributes:
        consent_id: UUID of the APPROVED consent authorising this transfer.
        source_account_id: UUID of the originating linked account.
        target_account_id: UUID of the destination linked account.
        amount: Transfer amount expressed in the given currency.
        currency: ISO 4217 currency code.
        idempotency_key: Client-supplied unique key for duplicate detection.
            Keys that begin with "fail-" trigger the forced-failure simulation
            mode and will cause a TappGatewayError to be raised.
    """

    consent_id: str
    source_account_id: str
    target_account_id: str
    amount: float
    currency: str
    idempotency_key: str


@dataclass(frozen=True)
class ExecuteTransferResult:
    """Output DTO returned after a transfer is successfully submitted.

    Attributes:
        transfer_id: UUID assigned to this transfer record.
        consent_id: UUID of the authorising consent.
        source_account_id: UUID of the originating account.
        target_account_id: UUID of the destination account.
        amount: Transfer amount.
        currency: ISO 4217 currency code.
        tapp_reference: Human-readable BCRP-style reference for auditing.
        status: Terminal status of the transfer (COMPLETED in the happy path).
        completed_at: UTC timestamp when the transfer reached terminal status.
    """

    transfer_id: str
    consent_id: str
    source_account_id: str
    target_account_id: str
    amount: float
    currency: str
    tapp_reference: str
    status: TransferStatus
    completed_at: datetime


# ===========================================================================
# Transfer — Get Status
# ===========================================================================


@dataclass(frozen=True)
class GetTransferCommand:
    """Input DTO for the get-transfer-status operation.

    Attributes:
        transfer_id: UUID of the transfer record to retrieve.
    """

    transfer_id: str


@dataclass(frozen=True)
class GetTransferResult:
    """Output DTO for a transfer status query.

    Attributes:
        transfer_id: UUID of the transfer.
        consent_id: UUID of the authorising consent.
        source_account_id: UUID of the originating account.
        target_account_id: UUID of the destination account.
        amount: Transfer amount.
        currency: ISO 4217 currency code.
        idempotency_key: The client-supplied deduplication key.
        tapp_reference: Human-readable BCRP-style reference.
        status: Current transfer lifecycle status.
        created_at: UTC timestamp of submission.
        completed_at: UTC timestamp of terminal state, or None if still
            PROCESSING.
    """

    transfer_id: str
    consent_id: str
    source_account_id: str
    target_account_id: str
    amount: float
    currency: str
    idempotency_key: str
    tapp_reference: str
    status: TransferStatus
    created_at: datetime
    completed_at: datetime | None


# ===========================================================================
# Inbound Port protocols
# ===========================================================================


@runtime_checkable
class ILinkAccountPort(Protocol):
    """Inbound port satisfied by LinkAccountUseCase."""

    def link_account(self, command: LinkAccountCommand) -> LinkAccountResult:
        """Execute the link-account operation.

        Args:
            command: Validated input carrying user_id, iban, bank_code, alias.

        Returns:
            A LinkAccountResult describing the newly linked account.

        Raises:
            AccountNotFoundError: If the IBAN is not in the mock registry.
            AccountAlreadyLinkedError: If the account is already LINKED.
        """
        ...

    def get_account_status(
        self, command: GetAccountStatusCommand
    ) -> GetAccountStatusResult:
        """Execute the get-account-status operation.

        Args:
            command: Input carrying the account_id to look up.

        Returns:
            A GetAccountStatusResult with current status and metadata.

        Raises:
            AccountNotFoundError: If no account matches the given account_id.
        """
        ...

    def unlink_account(
        self, command: UnlinkAccountCommand
    ) -> UnlinkAccountResult:
        """Execute the unlink-account operation.

        Args:
            command: Input carrying the account_id to unlink.

        Returns:
            An UnlinkAccountResult confirming the new UNLINKED status.

        Raises:
            AccountNotFoundError: If no account matches the given account_id.
        """
        ...


@runtime_checkable
class IRequestConsentPort(Protocol):
    """Inbound port satisfied by RequestConsentUseCase."""

    def request_consent(
        self, command: RequestConsentCommand
    ) -> RequestConsentResult:
        """Execute the request-consent operation.

        Args:
            command: Validated input describing the desired transfer.

        Returns:
            A RequestConsentResult with the new consent in PENDING status.

        Raises:
            AccountNotFoundError: If source or target account_id is unknown.
            AccountNotLinkedError: If source or target account is not LINKED.
        """
        ...

    def get_consent(self, command: GetConsentCommand) -> GetConsentResult:
        """Execute the get-consent operation.

        Args:
            command: Input carrying the consent_id to look up.

        Returns:
            A GetConsentResult with current consent state and timestamps.

        Raises:
            ConsentNotFoundError: If no consent matches the given consent_id.
        """
        ...


@runtime_checkable
class IApproveTransferPort(Protocol):
    """Inbound port satisfied by ApproveTransferUseCase."""

    def approve_consent(
        self, command: ApproveConsentCommand
    ) -> ApproveConsentResult:
        """Approve a pending consent.

        Args:
            command: Input carrying the consent_id to approve.

        Returns:
            An ApproveConsentResult confirming APPROVED status.

        Raises:
            ConsentNotFoundError: If no consent matches the consent_id.
            ConsentAlreadyProcessedError: If consent is not in PENDING status.
        """
        ...

    def reject_consent(
        self, command: RejectConsentCommand
    ) -> RejectConsentResult:
        """Reject a pending consent.

        Args:
            command: Input carrying the consent_id to reject.

        Returns:
            A RejectConsentResult confirming REJECTED status.

        Raises:
            ConsentNotFoundError: If no consent matches the consent_id.
            ConsentAlreadyProcessedError: If consent is not in PENDING status.
        """
        ...

    def execute_transfer(
        self, command: ExecuteTransferCommand
    ) -> ExecuteTransferResult:
        """Execute a TAPP-routed interbank transfer.

        This is the most critical operation in the mock. It enforces:
          1. Idempotency — duplicate idempotency_key returns DuplicateTransferError.
          2. Forced-failure simulation — idempotency_key starting with "fail-"
             raises TappGatewayError (HTTP 503) for 2PC rollback testing.
          3. Consent gate — the referenced consent must be in APPROVED status.

        Args:
            command: Validated input describing the transfer to execute.

        Returns:
            An ExecuteTransferResult with the completed transfer record.

        Raises:
            TappGatewayError: If idempotency_key starts with "fail-".
            DuplicateTransferError: If idempotency_key already exists.
            ConsentNotFoundError: If the consent_id is unknown.
            ConsentNotApprovedError: If the consent is not in APPROVED status.
        """
        ...

    def get_transfer(self, command: GetTransferCommand) -> GetTransferResult:
        """Retrieve the current status of a transfer.

        Args:
            command: Input carrying the transfer_id to look up.

        Returns:
            A GetTransferResult with the full transfer record.

        Raises:
            TransferNotFoundError: If no transfer matches the transfer_id.
        """
        ...