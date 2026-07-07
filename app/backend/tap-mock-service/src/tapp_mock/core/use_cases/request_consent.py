"""RequestConsentUseCase — consent creation and status query.

This use case satisfies the IRequestConsentPort inbound protocol. It is
responsible for:
  - Validating that both the source and target accounts exist and are LINKED.
  - Creating a new ConsentMock in PENDING status with a deterministic expiry
    window (5 minutes from creation time, matching the specification).
  - Querying the current state of any existing consent.

No framework imports. No HTTP concepts. Pure domain logic only.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from tapp_mock.core.domain.exceptions import (
    AccountNotFoundError,
    AccountNotLinkedError,
    ConsentNotFoundError,
)
from tapp_mock.core.domain.models import AccountStatus, ConsentMock, ConsentStatus
from tapp_mock.core.ports.inbound import (
    GetConsentCommand,
    GetConsentResult,
    RequestConsentCommand,
    RequestConsentResult,
)
from tapp_mock.core.ports.outbound import IMockStorePort

# Consent validity window: how long a PENDING consent can be approved.
_CONSENT_TTL_MINUTES: int = 5


class RequestConsentUseCase:
    """Handles consent creation and status queries for the TAPP mock.

    Satisfies IRequestConsentPort via structural subtyping (no inheritance).

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
    # IRequestConsentPort implementation
    # ------------------------------------------------------------------

    def request_consent(
        self, command: RequestConsentCommand
    ) -> RequestConsentResult:
        """Register a new consent request for an upcoming transfer.

        Validation sequence:
          1. Resolve source account by account_id → AccountNotFoundError if
             missing.
          2. Assert source account is LINKED → AccountNotLinkedError if not.
          3. Resolve target account by account_id → AccountNotFoundError if
             missing.
          4. Assert target account is LINKED → AccountNotLinkedError if not.
          5. Generate a UUID for the new consent.
          6. Set expires_at = now + _CONSENT_TTL_MINUTES.
          7. Persist ConsentMock in PENDING status.
          8. Return RequestConsentResult.

        Args:
            command: Validated command describing the desired transfer.

        Returns:
            A RequestConsentResult with the consent in PENDING status.

        Raises:
            AccountNotFoundError: If source or target account_id is unknown.
            AccountNotLinkedError: If source or target account is not LINKED.
        """
        # --- Validate source account ---
        source = self._store.find_account_by_id(command.source_account_id)
        if source is None:
            raise AccountNotFoundError(
                detail=(
                    f"Source account {command.source_account_id} was not "
                    "found in the TAPP mock registry."
                )
            )
        if source.status != AccountStatus.LINKED:
            raise AccountNotLinkedError(
                detail=(
                    f"Source account {command.source_account_id} is in "
                    f"status {source.status.value} and cannot be used for "
                    "a consent request. Only LINKED accounts are permitted."
                )
            )

        # --- Validate target account ---
        target = self._store.find_account_by_id(command.target_account_id)
        if target is None:
            raise AccountNotFoundError(
                detail=(
                    f"Target account {command.target_account_id} was not "
                    "found in the TAPP mock registry."
                )
            )
        if target.status != AccountStatus.LINKED:
            raise AccountNotLinkedError(
                detail=(
                    f"Target account {command.target_account_id} is in "
                    f"status {target.status.value} and cannot be used for "
                    "a consent request. Only LINKED accounts are permitted."
                )
            )

        # --- Build and persist the consent ---
        now: datetime = datetime.now(tz=timezone.utc)
        consent: ConsentMock = ConsentMock(
            consent_id=str(uuid.uuid4()),
            user_id=command.user_id,
            source_account_id=command.source_account_id,
            target_account_id=command.target_account_id,
            amount=command.amount,
            currency=command.currency,
            description=command.description,
            status=ConsentStatus.PENDING,
            created_at=now,
            expires_at=now + timedelta(minutes=_CONSENT_TTL_MINUTES),
            approved_at=None,
            rejected_at=None,
        )
        saved: ConsentMock = self._store.save_consent(consent)

        return RequestConsentResult(
            consent_id=saved.consent_id,
            user_id=saved.user_id,
            source_account_id=saved.source_account_id,
            target_account_id=saved.target_account_id,
            amount=saved.amount,
            currency=saved.currency,
            status=saved.status,
            expires_at=saved.expires_at,
            created_at=saved.created_at,
        )

    def get_consent(self, command: GetConsentCommand) -> GetConsentResult:
        """Retrieve the current state of a consent record.

        Args:
            command: Input carrying the consent_id to look up.

        Returns:
            A GetConsentResult with the full consent record and all timestamps.

        Raises:
            ConsentNotFoundError: If no consent matches the given consent_id.
        """
        consent = self._store.find_consent_by_id(command.consent_id)

        if consent is None:
            raise ConsentNotFoundError(
                detail=(
                    f"Consent {command.consent_id} was not found in the "
                    "TAPP mock registry."
                )
            )

        return GetConsentResult(
            consent_id=consent.consent_id,
            user_id=consent.user_id,
            source_account_id=consent.source_account_id,
            target_account_id=consent.target_account_id,
            amount=consent.amount,
            currency=consent.currency,
            status=consent.status,
            expires_at=consent.expires_at,
            created_at=consent.created_at,
            approved_at=consent.approved_at,
            rejected_at=consent.rejected_at,
        )