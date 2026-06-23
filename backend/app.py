"""
Bootstrap: wires ports/adapters and exposes the FastAPI REST adapter.
The core domain has zero knowledge of FastAPI or HTTP.
"""
from fastapi import FastAPI
from src.auth.adapters.rest import router as auth_router
from src.accounts.adapters.rest import router as accounts_router
from src.transactions.adapters.rest import router as transactions_router

def create_app() -> FastAPI:
    app = FastAPI(title="Spondylus", version="0.1.0")
    app.include_router(auth_router, prefix="/auth")
    app.include_router(accounts_router, prefix="/accounts")
    app.include_router(transactions_router, prefix="/transactions")
    return app

app = create_app()
