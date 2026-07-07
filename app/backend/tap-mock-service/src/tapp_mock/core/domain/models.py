"""Domain models for the TAPP mock service.

These are the core immutable value objects and entities that represent the
state managed by the in-memory store. They deliberately have no dependency
on any framework (FastAPI, Pydantic) — pure Python dataclasses only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class AccountStatus(str, Enum):
    """Lifecycle states of a bank account linked via TAPP."""

    LINKED = "LINKED"
    UNLINKED = "UNLINKED"


class ConsentStatus(str, Enum):
    """Lifecycle states of a TAPP consent request."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class TransferStatus(str, Enum):
    """Lifecycle states of a TAPP-routed transfer."""

    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# ---------------------------------------------------------------------------
# Domain models
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AccountMock:
    """Represents a bank account linked to Spondylus via TAPP.

    Attributes:
        account_id: Stable UUID that identifies this linkage record.
        user_id: UUID of the Spondylus user who owns this account.
        iban: Full IBAN string of the bank account.
        bank_code: Short bank identifier (e.g. "BCP", "BBVA", "INTERBANK").
        alias: Human-readable label chosen by the user.
        status: Current linkage status.
        linked_at: UTC timestamp of when the account was first linked.
        unlinked_at: UTC timestamp of when the account was unlinked, if ever.
    """

    account_id: str
    user_id: str
    iban: str
    bank_code: str
    alias: str
    status: AccountStatus
    linked_at: datetime
    unlinked_at: datetime | None = None

    def unlink(self) -> "AccountMock":
        """Return a new AccountMock with status set to UNLINKED.

        Returns:
            A new immutable AccountMock instance with UNLINKED status and
            the current UTC time recorded as unlinked_at.
        """
        return AccountMock(
            account_id=self.account_id,
            user_id=self.user_id,
            iban=self.iban,
            bank_code=self.bank_code,
            alias=self.alias,
            status=AccountStatus.UNLINKED,
            linked_at=self.linked_at,
            unlinked_at=datetime.now(tz=timezone.utc),
        )


@dataclass(frozen=True)
class ConsentMock:
    """Represents a TAPP consent request for a pending transfer.

    A consent must reach APPROVED status before a transfer can be executed
    against it. Each consent is tied to a specific amount and pair of accounts,
    and expires after a short window (simulated as a fixed timestamp in the
    mock).

    Attributes:
        consent_id: Stable UUID that identifies this consent.
        user_id: UUID of the Spondylus user who must approve this consent.
        source_account_id: UUID of the originating linked account.
        target_account_id: UUID of the destination linked account.
        amount: Transfer amount in the specified currency.
        currency: ISO 4217 currency code (e.g. "PEN").
        description: Optional human-readable purpose of the transfer.
        status: Current consent lifecycle status.
        created_at: UTC timestamp when the consent was created.
        expires_at: UTC timestamp after which the consent cannot be approved.
        approved_at: UTC timestamp when the consent was approved, if ever.
        rejected_at: UTC timestamp when the consent was rejected, if ever.
    """

    consent_id: str
    user_id: str
    source_account_id: str
    target_account_id: str
    amount: float
    currency: str
    description: str
    status: ConsentStatus
    created_at: datetime
    expires_at: datetime
    approved_at: datetime | None = None
    rejected_at: datetime | None = None

    def approve(self) -> "ConsentMock":
        """Return a new ConsentMock with status APPROVED.

        Returns:
            A new immutable ConsentMock with APPROVED status and the current
            UTC time recorded as approved_at.
        """
        return ConsentMock(
            consent_id=self.consent_id,
            user_id=self.user_id,
            source_account_id=self.source_account_id,
            target_account_id=self.target_account_id,
            amount=self.amount,
            currency=self.currency,
            description=self.description,
            status=ConsentStatus.APPROVED,
            created_at=self.created_at,
            expires_at=self.expires_at,
            approved_at=datetime.now(tz=timezone.utc),
            rejected_at=None,
        )

    def reject(self) -> "ConsentMock":
        """Return a new ConsentMock with status REJECTED.

        Returns:
            A new immutable ConsentMock with REJECTED status and the current
            UTC time recorded as rejected_at.
        """
        return ConsentMock(
            consent_id=self.consent_id,
            user_id=self.user_id,
            source_account_id=self.source_account_id,
            target_account_id=self.target_account_id,
            amount=self.amount,
            currency=self.currency,
            description=self.description,
            status=ConsentStatus.REJECTED,
            created_at=self.created_at,
            expires_at=self.expires_at,
            approved_at=None,
            rejected_at=datetime.now(tz=timezone.utc),
        )


@dataclass(frozen=True)
class TransferMock:
    """Represents a TAPP-routed interbank transfer.

    A transfer is only created after the associated consent is APPROVED. The
    idempotency_key is used to detect and reject duplicate submission attempts,
    implementing at-most-once semantics for the mock.

    Attributes:
        transfer_id: Stable UUID that identifies this transfer.
        consent_id: UUID of the APPROVED consent that authorised this transfer.
        source_account_id: UUID of the originating linked account.
        target_account_id: UUID of the destination linked account.
        amount: Transfer amount in the specified currency.
        currency: ISO 4217 currency code.
        idempotency_key: Client-supplied key for duplicate detection.
        tapp_reference: Human-readable BCRP-style reference number for auditing.
        status: Current transfer lifecycle status.
        created_at: UTC timestamp when the transfer was first submitted.
        completed_at: UTC timestamp when the transfer reached a terminal state.
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
    completed_at: datetime | None = None


# ---------------------------------------------------------------------------
# Seed-data helpers — fixed UUIDs used by InMemoryMockStore
# ---------------------------------------------------------------------------

#: Registry of all IBAN strings that the mock considers valid.
#: Any IBAN not present here will result in an AccountNotFoundError.
SEEDED_IBANS: dict[str, dict[str, str]] = {
    "PE12345678901234567890": {
        "account_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
        "user_id": "a1b2c3d4-0000-0000-0000-000000000001",
        "bank_code": "BCP",
        "alias": "Mi Cuenta BCP",
    },
    "PE09876543210987654321": {
        "account_id": "c9d8e7f6-0000-0000-0000-000000000002",
        "user_id": "a1b2c3d4-0000-0000-0000-000000000001",
        "bank_code": "BBVA",
        "alias": "Mi Cuenta BBVA",
    },
    "PE11111111111111111111": {
        "account_id": "d1e2f3a4-0000-0000-0000-000000000003",
        "user_id": "b2c3d4e5-0000-0000-0000-000000000002",
        "bank_code": "INTERBANK",
        "alias": "Mi Cuenta Interbank",
    },
}

#: Prefix that triggers the forced-failure simulation mode.
#: Any transfer whose idempotency_key starts with this string will receive
#: a simulated TAPP gateway error (HTTP 503) instead of being processed.
FORCED_FAILURE_PREFIX: str = "fail-"