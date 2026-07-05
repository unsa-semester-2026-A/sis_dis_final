"""FastAPI application factory.

Wires domain use cases to infrastructure adapters and mounts
REST routers. The domain layer has zero awareness of this module.
"""

from __future__ import annotations

from fastapi import FastAPI

from finance.ledger.adapters.rest import create_ledger_router
from finance.ledger.core.create_node import CreateNodeUseCase
from finance.ledger.core.emit_vector import EmitVectorUseCase
from finance.ledger.core.evaluate_balance import EvaluateBalanceUseCase


def create_app() -> FastAPI:
    """Build and configure the FastAPI application.

    Returns:
        A fully wired FastAPI instance.
    """
    # --- Adapters (outbound / secondary) ---
    from finance.ledger.adapters.file_store import (
        FileNodeRepository,
        FileVectorRepository,
    )

    node_repo = FileNodeRepository("data")
    vector_repo = FileVectorRepository("data")

    # --- Use Cases (core) ---
    create_node_uc = CreateNodeUseCase(node_repo=node_repo)
    emit_vector_uc = EmitVectorUseCase(node_repo=node_repo, vector_repo=vector_repo)
    evaluate_balance_uc = EvaluateBalanceUseCase(
        node_repo=node_repo, vector_repo=vector_repo
    )

    # --- Primary Adapters (REST routers) ---
    ledger_router = create_ledger_router(
        create_node=create_node_uc,
        emit_vector=emit_vector_uc,
        evaluate_balance=evaluate_balance_uc,
    )

    # --- Application ---
    app = FastAPI(
        title="Spondylus — Distributed Finance",
        version="0.1.0",
        description="Distributed personal finance system backend",
    )
    app.include_router(ledger_router, prefix="/ledger")

    return app


__all__ = ["create_app"]
