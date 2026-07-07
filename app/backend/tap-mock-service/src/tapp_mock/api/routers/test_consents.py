"""Integration tests for the consents router.

Full happy-path and error-path coverage for:
  POST   /tapp/v1/consents
  GET    /tapp/v1/consents/{consent_id}
  POST   /tapp/v1/consents/{consent_id}/approve
  POST   /tapp/v1/consents/{consent_id}/reject
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from tapp_mock.api.dependencies import get_store
from tapp_mock.app import app

# ---------------------------------------------------------------------------
# Fixed seed values
# ---------------------------------------------------------------------------
_SOURCE_ID = "f47ac10b-58cc-4372-a567-0e02b2c3d479"   # BCP
_TARGET_ID = "c9d8e7f6-0000-0000-0000-000000000002"   # BBVA
_INTERBANK_ID = "d1e2f3a4-0000-0000-0000-000000000003"
_USER_ID = "a1b2c3d4-0000-0000-0000-000000000001"
_UNKNOWN_ID = "00000000-0000-0000-0000-000000000000"

_VALID_CONSENT_BODY = {
    "user_id": _USER_ID,
    "source_account_id": _SOURCE_ID,
    "target_account_id": _TARGET_ID,
    "amount": 250.00,
    "currency": "PEN",
    "description": "Pago alquiler",
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
    """Create a PENDING consent and return its consent_id."""
    response = client.post("/tapp/v1/consents", json=_VALID_CONSENT_BODY)
    assert response.status_code == 201
    return str(response.json()["consent_id"])


@pytest.fixture()
def approved_consent_id(client: TestClient, pending_consent_id: str) -> str:
    """Approve the pending consent and return its consent_id."""
    response = client.post(f"/tapp/v1/consents/{pending_consent_id}/approve")
    assert response.status_code == 200
    return pending_consent_id


# ===========================================================================
# POST /tapp/v1/consents
# ===========================================================================


class TestRequestConsent:
    """Tests for POST /tapp/v1/consents."""

    def test_valid_request_returns_201_pending(self, client: TestClient) -> None:
        response = client.post("/tapp/v1/consents", json=_VALID_CONSENT_BODY)
        assert response.status_code == 201
        body = response.json()
        assert body["status"] == "PENDING"
        assert body["user_id"] == _USER_ID
        assert body["source_account_id"] == _SOURCE_ID
        assert body["target_account_id"] == _TARGET_ID
        assert body["amount"] == 250.00
        assert body["currency"] == "PEN"
        assert "consent_id" in body
        assert "expires_at" in body
        assert "created_at" in body

    def test_unknown_source_account_returns_404(self, client: TestClient) -> None:
        body = {**_VALID_CONSENT_BODY, "source_account_id": _UNKNOWN_ID}
        response = client.post("/tapp/v1/consents", json=body)
        assert response.status_code == 404
        assert response.json()["error"] == "TAPP-001"

    def test_unknown_target_account_returns_404(self, client: TestClient) -> None:
        body = {**_VALID_CONSENT_BODY, "target_account_id": _UNKNOWN_ID}
        response = client.post("/tapp/v1/consents", json=body)
        assert response.status_code == 404
        assert response.json()["error"] == "TAPP-001"

    def test_unlinked_source_returns_400(self, client: TestClient) -> None:
        client.delete(f"/tapp/v1/accounts/{_SOURCE_ID}/unlink")
        response = client.post("/tapp/v1/consents", json=_VALID_CONSENT_BODY)
        assert response.status_code == 400
        assert response.json()["error"] == "TAPP-003"

    def test_unlinked_target_returns_400(self, client: TestClient) -> None:
        client.delete(f"/tapp/v1/accounts/{_TARGET_ID}/unlink")
        response = client.post("/tapp/v1/consents", json=_VALID_CONSENT_BODY)
        assert response.status_code == 400
        assert response.json()["error"] == "TAPP-003"

    def test_missing_required_field_returns_422(self, client: TestClient) -> None:
        body = {k: v for k, v in _VALID_CONSENT_BODY.items() if k != "amount"}
        response = client.post("/tapp/v1/consents", json=body)
        assert response.status_code == 422

    def test_zero_amount_returns_422(self, client: TestClient) -> None:
        response = client.post(
            "/tapp/v1/consents", json={**_VALID_CONSENT_BODY, "amount": 0}
        )
        assert response.status_code == 422

    def test_negative_amount_returns_422(self, client: TestClient) -> None:
        response = client.post(
            "/tapp/v1/consents", json={**_VALID_CONSENT_BODY, "amount": -1}
        )
        assert response.status_code == 422

    def test_currency_must_be_three_chars(self, client: TestClient) -> None:
        response = client.post(
            "/tapp/v1/consents", json={**_VALID_CONSENT_BODY, "currency": "PE"}
        )
        assert response.status_code == 422

    def test_two_consent_requests_produce_distinct_ids(
        self, client: TestClient
    ) -> None:
        r1 = client.post("/tapp/v1/consents", json=_VALID_CONSENT_BODY)
        r2 = client.post("/tapp/v1/consents", json=_VALID_CONSENT_BODY)
        assert r1.json()["consent_id"] != r2.json()["consent_id"]


# ===========================================================================
# GET /tapp/v1/consents/{consent_id}
# ===========================================================================


class TestGetConsent:
    """Tests for GET /tapp/v1/consents/{consent_id}."""

    def test_get_pending_consent_returns_200(
        self, client: TestClient, pending_consent_id: str
    ) -> None:
        response = client.get(f"/tapp/v1/consents/{pending_consent_id}")
        assert response.status_code == 200
        body = response.json()
        assert body["consent_id"] == pending_consent_id
        assert body["status"] == "PENDING"
        assert body["approved_at"] is None
        assert body["rejected_at"] is None

    def test_get_approved_consent_shows_approved_at(
        self, client: TestClient, approved_consent_id: str
    ) -> None:
        response = client.get(f"/tapp/v1/consents/{approved_consent_id}")
        body = response.json()
        assert body["status"] == "APPROVED"
        assert body["approved_at"] is not None
        assert body["rejected_at"] is None

    def test_get_unknown_consent_returns_404(self, client: TestClient) -> None:
        response = client.get(f"/tapp/v1/consents/{_UNKNOWN_ID}")
        assert response.status_code == 404
        assert response.json()["error"] == "TAPP-010"


# ===========================================================================
# POST /tapp/v1/consents/{consent_id}/approve
# ===========================================================================


class TestApproveConsent:
    """Tests for POST /tapp/v1/consents/{consent_id}/approve."""

    def test_approve_pending_returns_200_approved(
        self, client: TestClient, pending_consent_id: str
    ) -> None:
        response = client.post(
            f"/tapp/v1/consents/{pending_consent_id}/approve"
        )
        assert response.status_code == 200
        body = response.json()
        assert body["consent_id"] == pending_consent_id
        assert body["status"] == "APPROVED"
        assert "approved_at" in body

    def test_approve_unknown_consent_returns_404(
        self, client: TestClient
    ) -> None:
        response = client.post(f"/tapp/v1/consents/{_UNKNOWN_ID}/approve")
        assert response.status_code == 404
        assert response.json()["error"] == "TAPP-010"

    def test_approve_already_approved_returns_409(
        self, client: TestClient, approved_consent_id: str
    ) -> None:
        response = client.post(
            f"/tapp/v1/consents/{approved_consent_id}/approve"
        )
        assert response.status_code == 409
        assert response.json()["error"] == "TAPP-011"

    def test_approve_rejected_consent_returns_409(
        self, client: TestClient, pending_consent_id: str
    ) -> None:
        client.post(f"/tapp/v1/consents/{pending_consent_id}/reject")
        response = client.post(
            f"/tapp/v1/consents/{pending_consent_id}/approve"
        )
        assert response.status_code == 409
        assert response.json()["error"] == "TAPP-011"


# ===========================================================================
# POST /tapp/v1/consents/{consent_id}/reject
# ===========================================================================


class TestRejectConsent:
    """Tests for POST /tapp/v1/consents/{consent_id}/reject."""

    def test_reject_pending_returns_200_rejected(
        self, client: TestClient, pending_consent_id: str
    ) -> None:
        response = client.post(
            f"/tapp/v1/consents/{pending_consent_id}/reject"
        )
        assert response.status_code == 200
        body = response.json()
        assert body["consent_id"] == pending_consent_id
        assert body["status"] == "REJECTED"
        assert "rejected_at" in body

    def test_reject_unknown_consent_returns_404(
        self, client: TestClient
    ) -> None:
        response = client.post(f"/tapp/v1/consents/{_UNKNOWN_ID}/reject")
        assert response.status_code == 404
        assert response.json()["error"] == "TAPP-010"

    def test_reject_already_rejected_returns_409(
        self, client: TestClient, pending_consent_id: str
    ) -> None:
        client.post(f"/tapp/v1/consents/{pending_consent_id}/reject")
        response = client.post(
            f"/tapp/v1/consents/{pending_consent_id}/reject"
        )
        assert response.status_code == 409
        assert response.json()["error"] == "TAPP-011"

    def test_reject_approved_consent_returns_409(
        self, client: TestClient, approved_consent_id: str
    ) -> None:
        response = client.post(
            f"/tapp/v1/consents/{approved_consent_id}/reject"
        )
        assert response.status_code == 409
        assert response.json()["error"] == "TAPP-011"