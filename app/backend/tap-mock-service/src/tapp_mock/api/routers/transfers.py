"""Transfers router — /tapp/v1/transfers.

Exposes two endpoints:
  POST   /tapp/v1/transfers                      → execute a transfer
  GET    /tapp/v1/transfers/{transfer_id}        → query transfer status

The POST endpoint is the most critical in the entire mock. It enforces:
  - Forced-failure simulation (idempotency_key prefix "fail-" → HTTP 503).
  - Idempotency (duplicate key → HTTP 409 with existing transfer_id).
  - Consent gate (consent must be APPROVED → HTTP 400 if not).
All of this logic lives in ApproveTransferUseCase; the router only translates
HTTP ↔ domain DTOs.
"""

from __future__ import annotations

from datetime import datetime

import pydantic
from fastapi import APIRouter, Depends, status

from tapp_mock.api.dependencies import get_approve_transfer_use_case
from tapp_mock.core.domain.models import TransferStatus
from tapp_mock.core.ports.inbound import (
    ExecuteTransferCommand,
    GetTransferCommand,
    IApproveTransferPort,
)

router = APIRouter(prefix="/tapp/v1/transfers", tags=["transfers"])


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class ExecuteTransferRequest(pydantic.BaseModel):
    """Request body for POST /tapp/v1/transfers."""

    model_config = pydantic.ConfigDict(strict=True)

    consent_id: str = pydantic.Field(
        ...,
        description="UUID of the APPROVED consent authorising this transfer.",
    )
    source_account_id: str = pydantic.Field(
        ..., description="UUID of the originating linked account."
    )
    target_account_id: str = pydantic.Field(
        ..., description="UUID of the destination linked account."
    )
    amount: float = pydantic.Field(
        ..., gt=0, description="Transfer amount — must be greater than zero."
    )
    currency: str = pydantic.Field(
        ...,
        min_length=3,
        max_length=3,
        description="ISO 4217 currency code, e.g. PEN.",
    )
    idempotency_key: str = pydantic.Field(
        ...,
        description=(
            "Client-supplied unique key for duplicate detection. "
            'Keys beginning with "fail-" trigger the forced-failure '
            "simulation mode (HTTP 503)."
        ),
    )


class ExecuteTransferResponse(pydantic.BaseModel):
    """Response body for POST /tapp/v1/transfers (HTTP 201)."""

    transfer_id: str
    consent_id: str
    source_account_id: str
    target_account_id: str
    amount: float
    currency: str
    tapp_reference: str
    status: TransferStatus
    completed_at: datetime


class TransferStatusResponse(pydantic.BaseModel):
    """Response body for GET /tapp/v1/transfers/{transfer_id}."""

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
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "",
    response_model=ExecuteTransferResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Execute a TAPP-routed interbank transfer",
    description=(
        "Executes a transfer using an APPROVED consent. "
        "Idempotency is enforced via idempotency_key. "
        'Keys starting with "fail-" return HTTP 503 to simulate BCRP '
        "gateway failures for 2PC rollback testing. "
        "Duplicate keys return HTTP 409 with the existing transfer_id."
    ),
)
def execute_transfer(
    body: ExecuteTransferRequest,
    use_case: IApproveTransferPort = Depends(get_approve_transfer_use_case),
) -> ExecuteTransferResponse:
    """Execute a transfer.

    Args:
        body: Validated request body.
        use_case: Injected IApproveTransferPort implementation.

    Returns:
        ExecuteTransferResponse with the completed transfer record.
    """
    command = ExecuteTransferCommand(
        consent_id=body.consent_id,
        source_account_id=body.source_account_id,
        target_account_id=body.target_account_id,
        amount=body.amount,
        currency=body.currency,
        idempotency_key=body.idempotency_key,
    )
    result = use_case.execute_transfer(command)
    return ExecuteTransferResponse(
        transfer_id=result.transfer_id,
        consent_id=result.consent_id,
        source_account_id=result.source_account_id,
        target_account_id=result.target_account_id,
        amount=result.amount,
        currency=result.currency,
        tapp_reference=result.tapp_reference,
        status=result.status,
        completed_at=result.completed_at,
    )


@router.get(
    "/{transfer_id}",
    response_model=TransferStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Query transfer status",
    description="Returns the full record for a given transfer_id.",
)
def get_transfer(
    transfer_id: str,
    use_case: IApproveTransferPort = Depends(get_approve_transfer_use_case),
) -> TransferStatusResponse:
    """Get transfer status.

    Args:
        transfer_id: Path parameter — UUID of the transfer.
        use_case: Injected IApproveTransferPort implementation.

    Returns:
        TransferStatusResponse with all transfer metadata.
    """
    command = GetTransferCommand(transfer_id=transfer_id)
    result = use_case.get_transfer(command)
    return TransferStatusResponse(
        transfer_id=result.transfer_id,
        consent_id=result.consent_id,
        source_account_id=result.source_account_id,
        target_account_id=result.target_account_id,
        amount=result.amount,
        currency=result.currency,
        idempotency_key=result.idempotency_key,
        tapp_reference=result.tapp_reference,
        status=result.status,
        created_at=result.created_at,
        completed_at=result.completed_at,
    )