# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false
"""Top-down integration tests.

Tests the system from the top primary adapter (REST controllers / FastAPI)
downwards, stubbing out the lower secondary adapters (the persistence layer
repositories) using in-memory doubles.
"""

from decimal import Decimal

import pytest
from app.ledger.adapters.rest import create_ledger_router
from app.ledger.core.create_node import CreateNodeUseCase
from app.ledger.core.emit_vector import EmitVectorUseCase
from app.ledger.core.evaluate_balance import EvaluateBalanceUseCase
from app.ledger.core.test_use_cases import (
    InMemoryNodeRepository,
    InMemoryVectorRepository,
)
from app.shared import new_id
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def top_down_client() -> TestClient:
    """Setup a top-down integration testing client.

    Wires the top-level REST controller and business use cases
    to in-memory test double repositories (stubbing out the filesystem).
    """
    node_repo = InMemoryNodeRepository()
    vector_repo = InMemoryVectorRepository()

    create_node_uc = CreateNodeUseCase(node_repo=node_repo)
    emit_vector_uc = EmitVectorUseCase(node_repo=node_repo, vector_repo=vector_repo)
    evaluate_balance_uc = EvaluateBalanceUseCase(
        node_repo=node_repo, vector_repo=vector_repo
    )

    router = create_ledger_router(
        create_node=create_node_uc,
        emit_vector=emit_vector_uc,
        evaluate_balance=evaluate_balance_uc,
    )

    app = FastAPI()
    app.include_router(router, prefix="/ledger")
    return TestClient(app)


def test_top_down_flow(top_down_client: TestClient) -> None:
    """Verify top-down HTTP endpoint to port use case integration."""
    user_id = str(new_id())

    # 1. Test POST /ledger/nodes -> Wires down to CreateNodeUseCase
    bank_resp = top_down_client.post(
        "/ledger/nodes",
        json={
            "user_id": user_id,
            "name": "Checking Account",
            "node_type": "ASSET",
            "currency": "PEN",
        },
    )
    assert bank_resp.status_code == 201
    bank_id = bank_resp.json()["id"]

    expense_resp = top_down_client.post(
        "/ledger/nodes",
        json={
            "user_id": user_id,
            "name": "Rent Expense",
            "node_type": "SINK",
            "currency": "PEN",
        },
    )
    assert expense_resp.status_code == 201
    expense_id = expense_resp.json()["id"]

    # 2. Test POST /ledger/vectors -> Wires down to EmitVectorUseCase
    vector_resp = top_down_client.post(
        "/ledger/vectors",
        json={
            "source_node_id": bank_id,
            "target_node_id": expense_id,
            "amount": "450.00",
        },
    )
    assert vector_resp.status_code == 201
    assert vector_resp.json()["amount"] == "450.00"

    # 3. Test GET /ledger/nodes/{node_id}/balance ->
    # Wires down to EvaluateBalanceUseCase
    balance_resp = top_down_client.get(f"/ledger/nodes/{bank_id}/balance")
    assert balance_resp.status_code == 200
    from typing import cast

    balance_payload = cast(dict[str, str], balance_resp.json())
    assert Decimal(balance_payload["amount"]) == Decimal("-450.00")
    assert balance_payload["currency"] == "PEN"
