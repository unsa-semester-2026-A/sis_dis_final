"""Entry point for the wallet-service FastAPI application.

This module initializes the FastAPI application, wires dependencies
(adapters and core use cases), and registers API routers.
"""

from app.ledger.adapters.file_store import FileNodeRepository, FileVectorRepository
from app.ledger.adapters.rest import create_ledger_router
from app.ledger.core.create_node import CreateNodeUseCase
from app.ledger.core.emit_vector import EmitVectorUseCase
from app.ledger.core.evaluate_balance import EvaluateBalanceUseCase
from fastapi import FastAPI

# --- Adapters (outbound / secondary) ---
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
    title="Spondylus — Wallet Service",
    version="0.1.0",
    description="Wallet and ledger microservice backend",
)

app.include_router(ledger_router, prefix="/ledger")


@app.get("/")
def read_root() -> dict[str, str]:
    """Read the root endpoint.

    Returns:
        dict: A greeting message.
    """
    return {"message": "Hello World from FastAPI, uv, and Uvicorn!"}
