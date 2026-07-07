"""Consents router — /tapp/v1/consents.

Exposes four endpoints:
  POST   /tapp/v1/consents                         → request a new consent
  GET    /tapp/v1/consents/{consent_id}            → query consent status
  POST   /tapp/v1/consents/{consent_id}/approve    → approve a pending consent
  POST   /tapp/v1/consents/{consent_id}/reject     → reject a pending consent

Approve and reject are wired to the IApproveTransferPort (same use case that
handles transfer execution), because the state machine for consents and the
gate check for transfers belong to the same bounded context.
"""

from __future__ import annotations

from datetime import datetime

import pydantic
from fastapi import APIRouter, Depends, status

from tapp_mock.api.dependencies import (
    get_approve_transfer_use_case,
    get_request_consent_use_case,
)
from tapp_mock.core.domain.models import ConsentStatus
from tapp_mock.core.ports.inbound import (
    ApproveConsentCommand,
    GetConsentCommand,
    IApproveTransferPort,
    IRequestConsentPort,
    RejectConsentCommand,
    RequestConsentCommand,
)

router = APIRouter(prefix="/tapp/v1/consents", tags=["consents"])


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class RequestConsentRequest(pydantic.BaseModel):
    """Request body for POST /tapp/v1/consents."""

    model_config = pydantic.ConfigDict(strict=True)

    user_id: str = pydantic.Field(
        ..., description="UUID of the user who must approve this consent."
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
    description: str = pydantic.Field(
        default="",
        description="Optional human-readable purpose of the transfer.",
    )


class RequestConsentResponse(pydantic.BaseModel):
    """Response body for POST /tapp/v1/consents (HTTP 201)."""

    consent_id: str
    user_id: str
    source_account_id: str
    target_account_id: str
    amount: float
    currency: str
    status: ConsentStatus
    expires_at: datetime
    created_at: datetime


class ConsentStatusResponse(pydantic.BaseModel):
    """Response body for GET /tapp/v1/consents/{consent_id}."""

    consent_id: str
    user_id: str
    source_account_id: str
    target_account_id: str
    amount: float
    currency: str
    status: ConsentStatus
    expires_at: datetime
    created_at: datetime
    approved_at: datetime | None = None
    rejected_at: datetime | None = None


class ApproveConsentResponse(pydantic.BaseModel):
    """Response body for POST /tapp/v1/consents/{consent_id}/approve."""

    consent_id: str
    status: ConsentStatus
    approved_at: datetime


class RejectConsentResponse(pydantic.BaseModel):
    """Response body for POST /tapp/v1/consents/{consent_id}/reject."""

    consent_id: str
    status: ConsentStatus
    rejected_at: datetime


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "",
    response_model=RequestConsentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Request a TAPP consent for a transfer",
    description=(
        "Registers a new consent in PENDING status. Both source and target "
        "accounts must exist and be in LINKED status. The consent expires "
        "after 5 minutes if not approved."
    ),
)
def request_consent(
    body: RequestConsentRequest,
    use_case: IRequestConsentPort = Depends(get_request_consent_use_case),
) -> RequestConsentResponse:
    """Create a new consent request.

    Args:
        body: Validated request body.
        use_case: Injected IRequestConsentPort implementation.

    Returns:
        RequestConsentResponse with the new consent in PENDING status.
    """
    command = RequestConsentCommand(
        user_id=body.user_id,
        source_account_id=body.source_account_id,
        target_account_id=body.target_account_id,
        amount=body.amount,
        currency=body.currency,
        description=body.description,
    )
    result = use_case.request_consent(command)
    return RequestConsentResponse(
        consent_id=result.consent_id,
        user_id=result.user_id,
        source_account_id=result.source_account_id,
        target_account_id=result.target_account_id,
        amount=result.amount,
        currency=result.currency,
        status=result.status,
        expires_at=result.expires_at,
        created_at=result.created_at,
    )


@router.get(
    "/{consent_id}",
    response_model=ConsentStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Query consent status",
    description="Returns the current state of a consent record.",
)
def get_consent(
    consent_id: str,
    use_case: IRequestConsentPort = Depends(get_request_consent_use_case),
) -> ConsentStatusResponse:
    """Get consent status.

    Args:
        consent_id: Path parameter — UUID of the consent.
        use_case: Injected IRequestConsentPort implementation.

    Returns:
        ConsentStatusResponse with all lifecycle timestamps.
    """
    command = GetConsentCommand(consent_id=consent_id)
    result = use_case.get_consent(command)
    return ConsentStatusResponse(
        consent_id=result.consent_id,
        user_id=result.user_id,
        source_account_id=result.source_account_id,
        target_account_id=result.target_account_id,
        amount=result.amount,
        currency=result.currency,
        status=result.status,
        expires_at=result.expires_at,
        created_at=result.created_at,
        approved_at=result.approved_at,
        rejected_at=result.rejected_at,
    )


@router.post(
    "/{consent_id}/approve",
    response_model=ApproveConsentResponse,
    status_code=status.HTTP_200_OK,
    summary="Approve a pending consent",
    description=(
        "Transitions a PENDING consent to APPROVED status. "
        "Returns 409 if the consent is already in a terminal state. "
        "Returns 404 if the consent_id is not found."
    ),
)
def approve_consent(
    consent_id: str,
    use_case: IApproveTransferPort = Depends(get_approve_transfer_use_case),
) -> ApproveConsentResponse:
    """Approve a consent.

    Args:
        consent_id: Path parameter — UUID of the consent to approve.
        use_case: Injected IApproveTransferPort implementation.

    Returns:
        ApproveConsentResponse with APPROVED status and approved_at timestamp.
    """
    command = ApproveConsentCommand(consent_id=consent_id)
    result = use_case.approve_consent(command)
    return ApproveConsentResponse(
        consent_id=result.consent_id,
        status=result.status,
        approved_at=result.approved_at,
    )


@router.post(
    "/{consent_id}/reject",
    response_model=RejectConsentResponse,
    status_code=status.HTTP_200_OK,
    summary="Reject a pending consent",
    description=(
        "Transitions a PENDING consent to REJECTED status. "
        "Returns 409 if the consent is already in a terminal state. "
        "Returns 404 if the consent_id is not found."
    ),
)
def reject_consent(
    consent_id: str,
    use_case: IApproveTransferPort = Depends(get_approve_transfer_use_case),
) -> RejectConsentResponse:
    """Reject a consent.

    Args:
        consent_id: Path parameter — UUID of the consent to reject.
        use_case: Injected IApproveTransferPort implementation.

    Returns:
        RejectConsentResponse with REJECTED status and rejected_at timestamp.
    """
    command = RejectConsentCommand(consent_id=consent_id)
    result = use_case.reject_consent(command)
    return RejectConsentResponse(
        consent_id=result.consent_id,
        status=result.status,
        rejected_at=result.rejected_at,
    )