"""FastAPI dependency injection configuration.

This module is the composition root of the tap-mock-service. It instantiates
the single shared InMemoryMockStore and exposes one getter function per use
case. FastAPI's Depends() mechanism calls these getters on every request,
but because the store is a module-level singleton the same instance is reused
across all requests within a single process lifetime.

Design decisions:
  - The store is instantiated at module import time (not inside a lifespan
    handler) to keep the wiring simple and to allow test code to import and
    call store.reset() before each test case without patching FastAPI's
    dependency overrides.
  - Each getter returns the concrete use case typed as the inbound Protocol.
    This preserves the hexagonal boundary: routers depend only on the port
    interfaces, never on the concrete use case classes.
  - If in a future iteration the store needs to be replaced (e.g. with a
    Redis-backed adapter), only this file changes.
"""

from __future__ import annotations

from tapp_mock.adapters.secondary.mock_store import InMemoryMockStore
from tapp_mock.core.ports.inbound import (
    IApproveTransferPort,
    ILinkAccountPort,
    IRequestConsentPort,
)
from tapp_mock.core.use_cases.approve_transfer import ApproveTransferUseCase
from tapp_mock.core.use_cases.link_account import LinkAccountUseCase
from tapp_mock.core.use_cases.request_consent import RequestConsentUseCase

# ---------------------------------------------------------------------------
# Composition root — single shared store instance for the whole process.
# ---------------------------------------------------------------------------
_store = InMemoryMockStore()

# ---------------------------------------------------------------------------
# Use-case factories — called by FastAPI's Depends() on every request.
# Returning the same instance is intentional: use cases are stateless wrappers
# around the shared store.
# ---------------------------------------------------------------------------
_link_account_use_case: ILinkAccountPort = LinkAccountUseCase(_store)
_request_consent_use_case: IRequestConsentPort = RequestConsentUseCase(_store)
_approve_transfer_use_case: IApproveTransferPort = ApproveTransferUseCase(_store)


def get_store() -> InMemoryMockStore:
    """Return the shared InMemoryMockStore instance.

    Exposed for test code that needs to call store.reset() between cases.
    Not injected into any router — routers only depend on use case ports.

    Returns:
        The module-level InMemoryMockStore singleton.
    """
    return _store


def get_link_account_use_case() -> ILinkAccountPort:
    """Return the ILinkAccountPort implementation.

    Returns:
        The shared LinkAccountUseCase instance typed as ILinkAccountPort.
    """
    return _link_account_use_case


def get_request_consent_use_case() -> IRequestConsentPort:
    """Return the IRequestConsentPort implementation.

    Returns:
        The shared RequestConsentUseCase instance typed as IRequestConsentPort.
    """
    return _request_consent_use_case


def get_approve_transfer_use_case() -> IApproveTransferPort:
    """Return the IApproveTransferPort implementation.

    Returns:
        The shared ApproveTransferUseCase typed as IApproveTransferPort.
    """
    return _approve_transfer_use_case