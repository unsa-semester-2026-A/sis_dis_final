"""FastAPI application factory for tap-mock-service.

This module builds and exports the FastAPI ``app`` instance. It is the only
place in the codebase that:
  1. Registers all routers under their canonical prefixes.
  2. Registers global exception handlers that translate domain exceptions into
     RFC 7807-style HTTP error responses.
  3. Exposes the health-check endpoint at GET /tapp/v1/health.

Import structure:
  app.py → routers → dependencies.py → use cases → domain

Nothing in the domain or use case layers may import from this module.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from tapp_mock.api.routers import accounts, consents, transfers
from tapp_mock.core.domain.exceptions import (
    AccountAlreadyLinkedError,
    AccountNotFoundError,
    AccountNotLinkedError,
    ConsentAlreadyProcessedError,
    ConsentNotApprovedError,
    ConsentNotFoundError,
    DuplicateTransferError,
    TappGatewayError,
    TappMockError,
    TransferNotFoundError,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Application metadata
# ---------------------------------------------------------------------------
_DESCRIPTION = """
## tap-mock-service

Deterministic simulation of the BCRP TAPP infrastructure for the
**Spondylus** distributed personal finance system.

### Capabilities
- **Account linking** — simulate TAPP account registration and revocation.
- **Consent management** — create, approve, and reject transfer consents.
- **Transfer execution** — execute TAPP-routed interbank transfers with full
  idempotency support and forced-failure simulation for 2PC testing.

### Forced-failure mode
Send any transfer request with an `idempotency_key` that begins with `fail-`
to receive a simulated HTTP 503 BCRP gateway timeout. Use this to exercise
the wallet-service retry and Two-Phase Commit rollback logic.
"""

app = FastAPI(
    title="tap-mock-service",
    description=_DESCRIPTION,
    version="1.0.0",
    docs_url="/tapp/docs",
    redoc_url="/tapp/redoc",
    openapi_url="/tapp/openapi.json",
)


# ===========================================================================
# Global exception handlers
#
# Each handler maps one (or more) domain exception class(es) to the
# appropriate HTTP status code and a consistent RFC 7807-inspired error body:
#
#   {
#       "error":  "<machine-readable code>",   e.g. "TAPP-001"
#       "detail": "<human-readable message>",
#       ...extra fields specific to the exception type...
#   }
#
# Ordering matters: more specific subclasses must be registered BEFORE their
# base class. FastAPI matches the first handler whose exception type is an
# instance-of match.
# ===========================================================================


def _error_body(exc: TappMockError, **extra: Any) -> dict[str, Any]:
    """Build a consistent error response body from a domain exception.

    Args:
        exc: The caught domain exception.
        **extra: Additional key-value pairs to include in the body (e.g.
            existing_transfer_id for DuplicateTransferError).

    Returns:
        A dict suitable for JSONResponse content.
    """
    body: dict[str, Any] = {"error": exc.code, "detail": exc.detail}
    body.update(extra)
    return body


# ---------------------------------------------------------------------------
# 404 — Not Found
# ---------------------------------------------------------------------------


@app.exception_handler(AccountNotFoundError)
async def account_not_found_handler(
    _request: Request, exc: AccountNotFoundError
) -> JSONResponse:
    """Translate AccountNotFoundError to HTTP 404."""
    logger.debug("AccountNotFoundError: %s", exc.detail)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=_error_body(exc),
    )


@app.exception_handler(ConsentNotFoundError)
async def consent_not_found_handler(
    _request: Request, exc: ConsentNotFoundError
) -> JSONResponse:
    """Translate ConsentNotFoundError to HTTP 404."""
    logger.debug("ConsentNotFoundError: %s", exc.detail)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=_error_body(exc),
    )


@app.exception_handler(TransferNotFoundError)
async def transfer_not_found_handler(
    _request: Request, exc: TransferNotFoundError
) -> JSONResponse:
    """Translate TransferNotFoundError to HTTP 404."""
    logger.debug("TransferNotFoundError: %s", exc.detail)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=_error_body(exc),
    )


# ---------------------------------------------------------------------------
# 400 — Bad Request
# ---------------------------------------------------------------------------


@app.exception_handler(AccountNotLinkedError)
async def account_not_linked_handler(
    _request: Request, exc: AccountNotLinkedError
) -> JSONResponse:
    """Translate AccountNotLinkedError to HTTP 400."""
    logger.debug("AccountNotLinkedError: %s", exc.detail)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=_error_body(exc),
    )


@app.exception_handler(ConsentNotApprovedError)
async def consent_not_approved_handler(
    _request: Request, exc: ConsentNotApprovedError
) -> JSONResponse:
    """Translate ConsentNotApprovedError to HTTP 400."""
    logger.debug("ConsentNotApprovedError: %s", exc.detail)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=_error_body(exc),
    )


# ---------------------------------------------------------------------------
# 409 — Conflict
# ---------------------------------------------------------------------------


@app.exception_handler(AccountAlreadyLinkedError)
async def account_already_linked_handler(
    _request: Request, exc: AccountAlreadyLinkedError
) -> JSONResponse:
    """Translate AccountAlreadyLinkedError to HTTP 409."""
    logger.debug("AccountAlreadyLinkedError: %s", exc.detail)
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=_error_body(exc),
    )


@app.exception_handler(ConsentAlreadyProcessedError)
async def consent_already_processed_handler(
    _request: Request, exc: ConsentAlreadyProcessedError
) -> JSONResponse:
    """Translate ConsentAlreadyProcessedError to HTTP 409."""
    logger.debug("ConsentAlreadyProcessedError: %s", exc.detail)
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=_error_body(exc),
    )


@app.exception_handler(DuplicateTransferError)
async def duplicate_transfer_handler(
    _request: Request, exc: DuplicateTransferError
) -> JSONResponse:
    """Translate DuplicateTransferError to HTTP 409.

    Includes the existing_transfer_id in the response body so that the
    caller can retrieve the already-completed transfer without a separate
    lookup.
    """
    logger.debug(
        "DuplicateTransferError: %s (existing: %s)",
        exc.detail,
        exc.existing_transfer_id,
    )
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=_error_body(exc, existing_transfer_id=exc.existing_transfer_id),
    )


# ---------------------------------------------------------------------------
# 503 — Service Unavailable (forced-failure simulation)
# ---------------------------------------------------------------------------


@app.exception_handler(TappGatewayError)
async def tapp_gateway_error_handler(
    _request: Request, exc: TappGatewayError
) -> JSONResponse:
    """Translate TappGatewayError to HTTP 503.

    This is triggered by the forced-failure simulation mode (idempotency_key
    prefix "fail-"). wallet-service should treat this as a retryable error.
    """
    logger.warning("TappGatewayError (simulated): %s", exc.detail)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=_error_body(exc),
        headers={"Retry-After": "30"},
    )


# ---------------------------------------------------------------------------
# 500 — Catch-all for any unhandled TappMockError subclass
# (safety net; should not be reached in normal operation)
# ---------------------------------------------------------------------------


@app.exception_handler(TappMockError)
async def tapp_mock_base_handler(
    _request: Request, exc: TappMockError
) -> JSONResponse:
    """Catch-all for any TappMockError not handled by a more specific handler."""
    logger.error("Unhandled TappMockError [%s]: %s", exc.code, exc.detail)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_error_body(exc),
    )


# ===========================================================================
# Routers
# ===========================================================================

app.include_router(accounts.router)
app.include_router(consents.router)
app.include_router(transfers.router)


# ===========================================================================
# Health check
# ===========================================================================


@app.get(
    "/tapp/v1/health",
    tags=["health"],
    summary="Health check",
    description="Returns service liveness status. Used by Docker and ACA.",
    status_code=status.HTTP_200_OK,
)
async def health() -> dict[str, str]:
    """Return a simple liveness response.

    Returns:
        A dict with status, service name, and version string.
    """
    return {
        "status": "ok",
        "service": "tap-mock-service",
        "version": "1.0.0",
    }