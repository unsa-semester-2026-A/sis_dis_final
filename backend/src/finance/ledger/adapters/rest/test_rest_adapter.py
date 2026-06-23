# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false
"""Black-box REST adapter tests for ledger endpoints."""

from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from finance.ledger.adapters.rest import create_ledger_router
from finance.ledger.core.create_node import CreateNodeUseCase
from finance.ledger.core.emit_vector import EmitVectorUseCase
from finance.ledger.core.evaluate_balance import EvaluateBalanceUseCase

# Reuse the in-memory repos from the co-located use case tests
from finance.ledger.core.test_use_cases import (
    InMemoryNodeRepository,
    InMemoryVectorRepository,
)
from finance.shared.domain import new_id


@pytest.fixture
def client() -> TestClient:
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


class TestCreateNodeEndpoint:
    def test_create_asset_node(self, client: TestClient) -> None:
        user_id = str(new_id())
        resp = client.post(
            "/ledger/nodes",
            json={
                "user_id": user_id,
                "name": "Main Bank",
                "node_type": "ASSET",
                "currency": "PEN",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Main Bank"
        assert data["node_type"] == "ASSET"
        assert data["currency"] == "PEN"
        assert data["is_active"] is True
        assert "id" in data

    def test_create_node_invalid_currency(self, client: TestClient) -> None:
        resp = client.post(
            "/ledger/nodes",
            json={
                "user_id": str(new_id()),
                "name": "Bad",
                "node_type": "ASSET",
                "currency": "TOOLONG",
            },
        )
        assert resp.status_code == 422 or resp.status_code == 400


class TestEmitVectorEndpoint:
    def _create_node(self, client: TestClient, name: str, node_type: str) -> str:
        resp = client.post(
            "/ledger/nodes",
            json={
                "user_id": str(new_id()),
                "name": name,
                "node_type": node_type,
                "currency": "PEN",
            },
        )
        return resp.json()["id"]

    def test_emit_vector(self, client: TestClient) -> None:
        source_id = self._create_node(client, "Bank", "ASSET")
        target_id = self._create_node(client, "Food", "SINK")

        resp = client.post(
            "/ledger/vectors",
            json={
                "source_node_id": source_id,
                "target_node_id": target_id,
                "amount": "100.00",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["amount"] == "100.00"
        assert data["source_node_id"] == source_id
        assert data["target_node_id"] == target_id
        assert "lineage_token" in data


class TestEvaluateBalanceEndpoint:
    def test_balance_after_operations(self, client: TestClient) -> None:
        user_id = str(new_id())
        # Create nodes
        bank_resp = client.post(
            "/ledger/nodes",
            json={
                "user_id": user_id,
                "name": "Bank",
                "node_type": "ASSET",
                "currency": "PEN",
            },
        )
        salary_resp = client.post(
            "/ledger/nodes",
            json={
                "user_id": user_id,
                "name": "Salary",
                "node_type": "SOURCE",
                "currency": "PEN",
            },
        )
        food_resp = client.post(
            "/ledger/nodes",
            json={
                "user_id": user_id,
                "name": "Food",
                "node_type": "SINK",
                "currency": "PEN",
            },
        )
        bank_id = bank_resp.json()["id"]
        salary_id = salary_resp.json()["id"]
        food_id = food_resp.json()["id"]

        # Salary -> Bank: 1000
        client.post(
            "/ledger/vectors",
            json={
                "source_node_id": salary_id,
                "target_node_id": bank_id,
                "amount": "1000.00",
            },
        )
        # Bank -> Food: 250
        client.post(
            "/ledger/vectors",
            json={
                "source_node_id": bank_id,
                "target_node_id": food_id,
                "amount": "250.00",
            },
        )

        resp = client.get(f"/ledger/nodes/{bank_id}/balance")
        assert resp.status_code == 200
        data = resp.json()
        assert Decimal(data["amount"]) == Decimal("750.00")
        assert data["currency"] == "PEN"
