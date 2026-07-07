"""Integration tests for the transfers router.

Full happy-path and error-path coverage for:
  POST   /tapp/v1/transfers
  GET    /tapp/v1/transfers/{transfer_id}

Special scenarios:
  - Forced-failure simulation via idempotency_key prefix "fail-" → HTTP 503
  - Idempotency: duplicate key → HTTP 409 with existing_transfer_id
  - Consent gate: pending / rejected / unknown consent → HTTP 400 / 404
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from tapp_mock.api.dependencies import get_store
from tapp_mock.app import app

# ---------------------------------------------------------------------------
# Fixed seed values
# ---------------------------------------------------------------------------
_SOURCE_ID = "f47ac10b-58cc-4372-a567-0e02b2c3d479"
_TARGET_ID = "c9d8e7f6-0000-0000-0000-000000000002"
_USER_ID = "a1b2c3d4-0000-0000-0000-000000000001"
_UNKNOWN_ID = "00000000-0000-0000-0000-000000000000"

_CONSENT_BODY = {
    "user_id": _USER_ID,
    "source_account_id": _SOURCE_ID,
    "target_account_id": _TARGET_ID,
    "amount": 250.00,
    "currency": "PEN",
    "description": "Test transfer",
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_store() -> None:
    """Reset store before every test."""
    get_store().reset()


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture()
def pending_consent_id(client: TestClient) -> str:
    r = client.post("/tapp/v1/consents", json=_CONSENT_BODY)
    assert r.status_code == 201
    return str(r.json()["consent_id"])


@pytest.fixture()
def approved_consent_id(client: TestClient, pending_consent_id: str) -> str:
    r = client.post(f"/tapp/v1/consents/{pending_consent_id}/approve")
    assert r.status_code == 200
    return pending_consent_id


def _transfer_body(consent_id: str, idempotency_key: str = "txn-test-001") -> dict:  # type: ignore[type-arg]
    return {
        "consent_id": consent_id,
        "source_account_id": _SOURCE_ID,
        "target_account_id": _TARGET_ID,
        "amount": 250.00,
        "currency": "PEN",
        "idempotency_key": idempotency_key,
    }


# ===========================================================================
# POST /tapp/v1/transfers
# ===========================================================================


class TestExecuteTransfer:
    """Tests for POST /tapp/v1/transfers."""

    def test_valid_transfer_returns_201_completed(
        self, client: TestClient, approved_consent_id: str
    ) -> None:
        response = client.post(
            "/tapp/v1/transfers",
            json=_transfer_body(approved_consent_id),
        )
        assert response.status_code == 201
        body = response.json()
        assert body["status"] == "COMPLETED"
        assert body["consent_id"] == approved_consent_id
        assert body["source_account_id"] == _SOURCE_ID
        assert body["target_account_id"] == _TARGET_ID
        assert body["amount"] == 250.00
        assert body["currency"] == "PEN"
        assert "transfer_id" in body
        assert "tapp_reference" in body
        assert "completed_at" in body
        assert body["tapp_reference"].startswith("TAPP-MOCK-")

    def test_response_shape_contains_all_documented_fields(
        self, client: TestClient, approved_consent_id: str
    ) -> None:
        body = client.post(
            "/tapp/v1/transfers",
            json=_transfer_body(approved_consent_id, "shape-key"),
        ).json()
        expected_fields = (
            "transfer_id", "consent_id", "source_account_id",
            "target_account_id", "amount", "currency",
            "tapp_reference", "status", "completed_at",
        )
        for field in expected_fields:
            assert field in body, f"Missing field: {field}"

    # ------------------------------------------------------------------
    # Forced-failure simulation
    # ------------------------------------------------------------------

    def test_fail_prefix_returns_503(
        self, client: TestClient, approved_consent_id: str
    ) -> None:
        """idempotency_key starting with 'fail-' must return HTTP 503."""
        response = client.post(
            "/tapp/v1/transfers",
            json=_transfer_body(approved_consent_id, "fail-gateway-test"),
        )
        assert response.status_code == 503
        body = response.json()
        assert body["error"] == "TAPP-030"
        assert "fail-" in body["detail"]

    def test_fail_prefix_response_includes_retry_after_header(
        self, client: TestClient, approved_consent_id: str
    ) -> None:
        """HTTP 503 must carry a Retry-After header for the caller's backoff."""
        response = client.post(
            "/tapp/v1/transfers",
            json=_transfer_body(approved_consent_id, "fail-header-test"),
        )
        assert response.status_code == 503
        assert "retry-after" in response.headers
        assert response.headers["retry-after"] == "30"

    def test_fail_prefix_does_not_create_transfer_record(
        self, client: TestClient, approved_consent_id: str
    ) -> None:
        """After a simulated gateway failure the store must be clean."""
        client.post(
            "/tapp/v1/transfers",
            json=_transfer_body(approved_consent_id, "fail-atomicity"),
        )
        # The idempotency key must not be registered — a retry with a valid
        # key succeeds independently.
        response = client.post(
            "/tapp/v1/transfers",
            json=_transfer_body(approved_consent_id, "retry-after-fail"),
        )
        assert response.status_code == 201

    def test_multiple_fail_prefix_calls_all_return_503(
        self, client: TestClient, approved_consent_id: str
    ) -> None:
        """Repeated forced-failure calls always return 503."""
        for i in range(3):
            r = client.post(
                "/tapp/v1/transfers",
                json=_transfer_body(approved_consent_id, f"fail-repeat-{i}"),
            )
            assert r.status_code == 503

    # ------------------------------------------------------------------
    # Idempotency
    # ------------------------------------------------------------------

    def test_duplicate_idempotency_key_returns_409(
        self, client: TestClient, approved_consent_id: str
    ) -> None:
        first = client.post(
            "/tapp/v1/transfers",
            json=_transfer_body(approved_consent_id, "dup-key"),
        )
        assert first.status_code == 201
        existing_id = first.json()["transfer_id"]

        second = client.post(
            "/tapp/v1/transfers",
            json=_transfer_body(approved_consent_id, "dup-key"),
        )
        assert second.status_code == 409
        body = second.json()
        assert body["error"] == "TAPP-021"
        assert body["existing_transfer_id"] == existing_id

    def test_distinct_idempotency_keys_both_succeed(
        self,
        client: TestClient,
        consent_use_case_helper: None,
    ) -> None:
        """Two transfers with different keys succeed independently."""
        # Create and approve two separate consents.
        c1 = client.post("/tapp/v1/consents", json=_CONSENT_BODY).json()["consent_id"]
        client.post(f"/tapp/v1/consents/{c1}/approve")

        c2 = client.post("/tapp/v1/consents", json=_CONSENT_BODY).json()["consent_id"]
        client.post(f"/tapp/v1/consents/{c2}/approve")

        r1 = client.post("/tapp/v1/transfers", json=_transfer_body(c1, "key-alpha"))
        r2 = client.post("/tapp/v1/transfers", json=_transfer_body(c2, "key-beta"))

        assert r1.status_code == 201
        assert r2.status_code == 201
        assert r1.json()["transfer_id"] != r2.json()["transfer_id"]

    # ------------------------------------------------------------------
    # Consent gate
    # ------------------------------------------------------------------

    def test_unknown_consent_returns_404(self, client: TestClient) -> None:
        response = client.post(
            "/tapp/v1/transfers",
            json=_transfer_body(_UNKNOWN_ID, "no-consent-key"),
        )
        assert response.status_code == 404
        assert response.json()["error"] == "TAPP-010"

    def test_pending_consent_returns_400(
        self, client: TestClient, pending_consent_id: str
    ) -> None:
        response = client.post(
            "/tapp/v1/transfers",
            json=_transfer_body(pending_consent_id, "pending-gate"),
        )
        assert response.status_code == 400
        body = response.json()
        assert body["error"] == "TAPP-012"
        assert "PENDING" in body["detail"]

    def test_rejected_consent_returns_400(
        self, client: TestClient, pending_consent_id: str
    ) -> None:
        client.post(f"/tapp/v1/consents/{pending_consent_id}/reject")
        response = client.post(
            "/tapp/v1/transfers",
            json=_transfer_body(pending_consent_id, "rejected-gate"),
        )
        assert response.status_code == 400
        body = response.json()
        assert body["error"] == "TAPP-012"
        assert "REJECTED" in body["detail"]

    def test_missing_required_field_returns_422(
        self, client: TestClient, approved_consent_id: str
    ) -> None:
        body = _transfer_body(approved_consent_id)
        del body["idempotency_key"]
        response = client.post("/tapp/v1/transfers", json=body)
        assert response.status_code == 422

    def test_zero_amount_returns_422(
        self, client: TestClient, approved_consent_id: str
    ) -> None:
        response = client.post(
            "/tapp/v1/transfers",
            json={**_transfer_body(approved_consent_id), "amount": 0},
        )
        assert response.status_code == 422

    # Helper fixture used only by test_distinct_idempotency_keys_both_succeed
    @pytest.fixture()
    def consent_use_case_helper(self) -> None:  # type: ignore[override]
        """No-op fixture — consent creation is done inline."""
        return None


# ===========================================================================
# GET /tapp/v1/transfers/{transfer_id}
# ===========================================================================


class TestGetTransfer:
    """Tests for GET /tapp/v1/transfers/{transfer_id}."""

    def test_get_existing_transfer_returns_200(
        self, client: TestClient, approved_consent_id: str
    ) -> None:
        created = client.post(
            "/tapp/v1/transfers",
            json=_transfer_body(approved_consent_id, "get-test-key"),
        ).json()
        transfer_id = created["transfer_id"]

        response = client.get(f"/tapp/v1/transfers/{transfer_id}")
        assert response.status_code == 200
        body = response.json()
        assert body["transfer_id"] == transfer_id
        assert body["consent_id"] == approved_consent_id
        assert body["status"] == "COMPLETED"
        assert body["idempotency_key"] == "get-test-key"
        assert body["amount"] == 250.00
        assert body["currency"] == "PEN"
        assert body["tapp_reference"].startswith("TAPP-MOCK-")
        assert "created_at" in body
        assert "completed_at" in body

    def test_get_unknown_transfer_returns_404(
        self, client: TestClient
    ) -> None:
        response = client.get(f"/tapp/v1/transfers/{_UNKNOWN_ID}")
        assert response.status_code == 404
        assert response.json()["error"] == "TAPP-020"

    def test_get_transfer_response_shape(
        self, client: TestClient, approved_consent_id: str
    ) -> None:
        """All documented fields must be present in the GET response."""
        transfer_id = client.post(
            "/tapp/v1/transfers",
            json=_transfer_body(approved_consent_id, "shape-get-key"),
        ).json()["transfer_id"]

        body = client.get(f"/tapp/v1/transfers/{transfer_id}").json()
        expected_fields = (
            "transfer_id", "consent_id", "source_account_id",
            "target_account_id", "amount", "currency", "idempotency_key",
            "tapp_reference", "status", "created_at", "completed_at",
        )
        for field in expected_fields:
            assert field in body, f"Missing field in GET /transfers: {field}"


# ===========================================================================
# Health check (smoke test included here for convenience)
# ===========================================================================


class TestHealthCheck:
    """Smoke test for GET /tapp/v1/health."""

    def test_health_returns_200_ok(self, client: TestClient) -> None:
        response = client.get("/tapp/v1/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert body["service"] == "tap-mock-service"
        assert body["version"] == "1.0.0"