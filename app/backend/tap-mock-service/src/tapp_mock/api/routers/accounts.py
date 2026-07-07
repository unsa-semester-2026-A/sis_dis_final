"""Accounts router — /tapp/v1/accounts.

Exposes three endpoints:
  POST   /tapp/v1/accounts/link                  → link a bank account
  GET    /tapp/v1/accounts/{account_id}/status   → query linkage status
  DELETE /tapp/v1/accounts/{account_id}/unlink   → revoke linkage

The router depends only on ILinkAccountPort (the inbound protocol). It knows
nothing about use case internals, store implementation, or domain models.
Its sole responsibilities are:
  1. Parse and validate the HTTP request via Pydantic schemas.
  2. Translate validated data into a command dataclass.
  3. Call the use case through the port.
  4. Translate the result dataclass into an HTTP response schema.

Exception translation lives in app.py (global exception handlers), NOT here.
"""

from __future__ import annotations

from datetime import datetime

import pydantic
from fastapi import APIRouter, Depends, status

from tapp_mock.api.dependencies import get_link_account_use_case
from tapp_mock.core.domain.models import AccountStatus
from tapp_mock.core.ports.inbound import (
    GetAccountStatusCommand,
    ILinkAccountPort,
    LinkAccountCommand,
    UnlinkAccountCommand,
)

router = APIRouter(prefix="/tapp/v1/accounts", tags=["accounts"])


# ---------------------------------------------------------------------------
# Request / Response schemas (Pydantic v2)
# ---------------------------------------------------------------------------


class LinkAccountRequest(pydantic.BaseModel):
    """Request body for POST /tapp/v1/accounts/link."""

    model_config = pydantic.ConfigDict(strict=True)

    user_id: str = pydantic.Field(
        ..., description="UUID of the Spondylus user requesting the linkage."
    )
    iban: str = pydantic.Field(
        ..., description="Full IBAN string of the bank account to link."
    )
    bank_code: str = pydantic.Field(
        ..., description='Short bank identifier, e.g. "BCP", "BBVA".'
    )
    alias: str = pydantic.Field(
        default="",
        description="Human-readable label for this account.",
    )


class LinkAccountResponse(pydantic.BaseModel):
    """Response body for POST /tapp/v1/accounts/link (HTTP 200)."""

    account_id: str
    user_id: str
    iban: str
    bank_code: str
    alias: str
    status: AccountStatus
    linked_at: datetime


class AccountStatusResponse(pydantic.BaseModel):
    """Response body for GET /tapp/v1/accounts/{account_id}/status."""

    account_id: str
    status: AccountStatus
    bank_code: str
    iban_masked: str
    linked_at: datetime
    unlinked_at: datetime | None = None


class UnlinkAccountResponse(pydantic.BaseModel):
    """Response body for DELETE /tapp/v1/accounts/{account_id}/unlink."""

    account_id: str
    status: AccountStatus
    unlinked_at: datetime


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/link",
    response_model=LinkAccountResponse,
    status_code=status.HTTP_200_OK,
    summary="Link a bank account via TAPP",
    description=(
        "Simulates the TAPP account-linking flow. The IBAN must be present "
        "in the mock registry (three pre-seeded IBANs are available). "
        "Returns 409 if the account is already LINKED, 404 if the IBAN is "
        "unknown."
    ),
)
def link_account(
    body: LinkAccountRequest,
    use_case: ILinkAccountPort = Depends(get_link_account_use_case),
) -> LinkAccountResponse:
    """Link a bank account.

    Args:
        body: Validated request body.
        use_case: Injected ILinkAccountPort implementation.

    Returns:
        LinkAccountResponse with the linked account details.
    """
    command = LinkAccountCommand(
        user_id=body.user_id,
        iban=body.iban,
        bank_code=body.bank_code,
        alias=body.alias,
    )
    result = use_case.link_account(command)
    return LinkAccountResponse(
        account_id=result.account_id,
        user_id=result.user_id,
        iban=result.iban,
        bank_code=result.bank_code,
        alias=result.alias,
        status=result.status,
        linked_at=result.linked_at,
    )


@router.get(
    "/{account_id}/status",
    response_model=AccountStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Query bank account linkage status",
    description=(
        "Returns the current TAPP linkage status for the given account_id. "
        "Returns 404 if the account_id is not found."
    ),
)
def get_account_status(
    account_id: str,
    use_case: ILinkAccountPort = Depends(get_link_account_use_case),
) -> AccountStatusResponse:
    """Get account status.

    Args:
        account_id: Path parameter — UUID of the account linkage record.
        use_case: Injected ILinkAccountPort implementation.

    Returns:
        AccountStatusResponse with current status and masked IBAN.
    """
    command = GetAccountStatusCommand(account_id=account_id)
    result = use_case.get_account_status(command)
    return AccountStatusResponse(
        account_id=result.account_id,
        status=result.status,
        bank_code=result.bank_code,
        iban_masked=result.iban_masked,
        linked_at=result.linked_at,
        unlinked_at=result.unlinked_at,
    )


@router.delete(
    "/{account_id}/unlink",
    response_model=UnlinkAccountResponse,
    status_code=status.HTTP_200_OK,
    summary="Unlink a bank account",
    description=(
        "Revokes the TAPP linkage for the given account. "
        "The operation is idempotent: unlinking an already-UNLINKED account "
        "succeeds and refreshes unlinked_at. Returns 404 if not found."
    ),
)
def unlink_account(
    account_id: str,
    use_case: ILinkAccountPort = Depends(get_link_account_use_case),
) -> UnlinkAccountResponse:
    """Unlink a bank account.

    Args:
        account_id: Path parameter — UUID of the account to unlink.
        use_case: Injected ILinkAccountPort implementation.

    Returns:
        UnlinkAccountResponse confirming UNLINKED status.
    """
    command = UnlinkAccountCommand(account_id=account_id)
    result = use_case.unlink_account(command)
    return UnlinkAccountResponse(
        account_id=result.account_id,
        status=result.status,
        unlinked_at=result.unlinked_at,
    )