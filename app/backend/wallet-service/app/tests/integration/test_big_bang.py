# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false
"""Big-Bang integration tests.

Tests the entire system integrated as a whole: the full vertical slice from
HTTP request down to file-based JSON disk persistence, using the actual
FastAPI application composition root defined in app/main.py.
"""

from decimal import Decimal
from pathlib import Path
from typing import cast

import pytest
from app.main import create_app
from app.shared import new_id
from fastapi.testclient import TestClient


@pytest.fixture
def big_bang_client(tmp_path: Path) -> TestClient:
    """Setup a Big-Bang integration testing client.

    Instantiates a fresh application instance via the Application Factory
    configured to write to a temporary test directory.
    """
    app = create_app(data_dir=str(tmp_path))
    return TestClient(app)


def test_big_bang_end_to_end_flow(big_bang_client: TestClient, tmp_path: Path) -> None:
    """Verify end-to-end integration of the complete system."""
    user_id = str(new_id())

    # 1. API Call: Create source node (wires through to filesystem)
    resp_src = big_bang_client.post(
        "/ledger/nodes",
        json={
            "user_id": user_id,
            "name": "Bank account",
            "node_type": "ASSET",
            "currency": "USD",
        },
    )
    assert resp_src.status_code == 201
    src_id = resp_src.json()["id"]

    # 2. API Call: Create target node
    resp_tgt = big_bang_client.post(
        "/ledger/nodes",
        json={
            "user_id": user_id,
            "name": "Coffee Shop",
            "node_type": "SINK",
            "currency": "USD",
        },
    )
    assert resp_tgt.status_code == 201
    tgt_id = resp_tgt.json()["id"]

    # Verify physical file existence (Big-Bang verification of bottom layer)
    assert (tmp_path / "nodes" / f"{src_id}.json").exists()
    assert (tmp_path / "nodes" / f"{tgt_id}.json").exists()

    # 3. API Call: Emit transaction vector
    resp_vec = big_bang_client.post(
        "/ledger/vectors",
        json={
            "source_node_id": src_id,
            "target_node_id": tgt_id,
            "amount": "5.50",
        },
    )
    assert resp_vec.status_code == 201
    vec_id = resp_vec.json()["id"]
    assert (tmp_path / "vectors" / f"{vec_id}.json").exists()

    # 4. API Call: Query balance
    resp_bal = big_bang_client.get(f"/ledger/nodes/{src_id}/balance")
    assert resp_bal.status_code == 200
    balance_payload = cast(dict[str, str], resp_bal.json())
    assert Decimal(balance_payload["amount"]) == Decimal("-5.50")
    assert balance_payload["currency"] == "USD"
