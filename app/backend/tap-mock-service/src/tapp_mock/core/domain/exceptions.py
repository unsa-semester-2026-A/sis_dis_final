"""Domain exceptions for the TAPP mock service.

All exceptions here inherit from a single base TappMockError so that callers
can catch any domain-level failure with a single except clause when needed,
while still being able to discriminate specific cases.

Each exception carries:
- A machine-readable ``code`` string (e.g. "TAPP-001") for the error body.
- A human-readable ``detail`` string explaining what went wrong.

These exceptions are framework-agnostic: the FastAPI exception handlers in
the primary adapter layer are responsible for translating them to HTTP
responses.
"""

from __future__ import annotations


class TappMockError(Exception):
    """Base class for all TAPP mock domain exceptions.

    Attributes:
        code: Machine-readable error code exposed in the HTTP response body.
        detail: Human-readable description of the error.
    """

    code: str = "TAPP-000"

    def __init__(self, detail: str) -> None:
        """Initialise the exception with a descriptive message.

        Args:
            detail: Human-readable description of the specific failure.
        """
        super().__init__(detail)
        self.detail = detail


# ---------------------------------------------------------------------------
# Account exceptions  (TAPP-001 range)
# ---------------------------------------------------------------------------


class AccountNotFoundError(TappMockError):
    """Raised when an IBAN or account_id is not recognised by the mock store.

    HTTP equivalent: 404 Not Found.

    Attributes:
        code: "TAPP-001"
    """

    code = "TAPP-001"


class AccountAlreadyLinkedError(TappMockError):
    """Raised when trying to link an account that is already in LINKED status.

    HTTP equivalent: 409 Conflict.

    Attributes:
        code: "TAPP-002"
    """

    code = "TAPP-002"


class AccountNotLinkedError(TappMockError):
    """Raised when an operation requires a LINKED account but the account is
    in UNLINKED (or any non-LINKED) status.

    HTTP equivalent: 400 Bad Request.

    Attributes:
        code: "TAPP-003"
    """

    code = "TAPP-003"


# ---------------------------------------------------------------------------
# Consent exceptions  (TAPP-010 range)
# ---------------------------------------------------------------------------


class ConsentNotFoundError(TappMockError):
    """Raised when a consent_id is not found in the mock store.

    HTTP equivalent: 404 Not Found.

    Attributes:
        code: "TAPP-010"
    """

    code = "TAPP-010"


class ConsentAlreadyProcessedError(TappMockError):
    """Raised when trying to approve or reject a consent that is no longer
    in PENDING status (already APPROVED, REJECTED, or EXPIRED).

    HTTP equivalent: 409 Conflict.

    Attributes:
        code: "TAPP-011"
    """

    code = "TAPP-011"


class ConsentNotApprovedError(TappMockError):
    """Raised when a transfer is requested against a consent that is not in
    APPROVED status.

    HTTP equivalent: 400 Bad Request.

    Attributes:
        code: "TAPP-012"
    """

    code = "TAPP-012"


# ---------------------------------------------------------------------------
# Transfer exceptions  (TAPP-020 range)
# ---------------------------------------------------------------------------


class TransferNotFoundError(TappMockError):
    """Raised when a transfer_id is not found in the mock store.

    HTTP equivalent: 404 Not Found.

    Attributes:
        code: "TAPP-020"
    """

    code = "TAPP-020"


class DuplicateTransferError(TappMockError):
    """Raised when a transfer submission uses an idempotency_key that already
    exists in the mock store.

    HTTP equivalent: 409 Conflict.

    Attributes:
        code: "TAPP-021"
        existing_transfer_id: The transfer_id of the previously recorded
            transfer that holds this idempotency_key.
    """

    code = "TAPP-021"

    def __init__(self, detail: str, existing_transfer_id: str) -> None:
        """Initialise the exception with an existing transfer reference.

        Args:
            detail: Human-readable description of the duplicate.
            existing_transfer_id: UUID of the already-recorded transfer.
        """
        super().__init__(detail)
        self.existing_transfer_id = existing_transfer_id


class TappGatewayError(TappMockError):
    """Raised when the forced-failure simulation mode is triggered.

    This simulates a transient BCRP gateway timeout so that wallet-service
    can exercise its retry and 2PC rollback logic without real infrastructure.

    HTTP equivalent: 503 Service Unavailable.

    Attributes:
        code: "TAPP-030"
    """

    code = "TAPP-030"