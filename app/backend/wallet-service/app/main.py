# pyright: reportUnusedFunction=false
"""Entry point and application factory for the wallet-service FastAPI application.

Wires dependencies (adapters and core use cases) and registers API routers.
"""

from app.ledger.adapters.file_store import FileNodeRepository, FileVectorRepository
from app.ledger.adapters.rest import create_ledger_router
from app.ledger.core.create_node import CreateNodeUseCase
from app.ledger.core.emit_vector import EmitVectorUseCase
from app.ledger.core.evaluate_balance import EvaluateBalanceUseCase
from fastapi import FastAPI


def create_app(data_dir: str = "data") -> FastAPI:
    """Build and configure the FastAPI application.

    Args:
        data_dir: Directory path for repository storage.

    Returns:
        FastAPI: A fully wired FastAPI application instance.
    """
    # --- Adapters (outbound / secondary) ---
    node_repo = FileNodeRepository(data_dir)
    vector_repo = FileVectorRepository(data_dir)

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
    app_instance = FastAPI(
        title="Spondylus — Wallet Service",
        version="0.1.0",
        description="Wallet and ledger microservice backend",
    )

    app_instance.include_router(ledger_router, prefix="/ledger")

    @app_instance.get("/")
    def read_root() -> dict[str, str]:
        """Read the root endpoint.

        Returns:
            dict: A greeting message.
        """
        return {"message": "Hello World from FastAPI, uv, and Uvicorn!"}

    return app_instance


# Instantiation for the production uvicorn server (uvicorn app.main:app)
app = create_app()
