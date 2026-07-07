"""Integration tests for the accounts router.

Uses FastAPI's TestClient (backed by httpx) against the real application
instance. The store is reset before each test via the get_store() dependency
so that every test starts from the three pre-seeded accounts.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from tapp_mock.api.dependencies import get_store
from tapp_mock.app import app

# ---------------------------------------------------------------------------
# Fixed seed values
# ---------------------------------------------------------------------------
_LINKED_IBAN = "PE12345678901234567890"
_LINKED_ACCOUNT_ID = "f47ac10b-58cc-4372-a567-0e02b2c3d479"
_BBVA_ACCOUNT_ID = "c9d8e7f6-0000-0000-0000-000000000002"
_UNKNOWN_IBAN = "PE99999999999999999999"
_UNKNOWN_ID = "00000000-0000-0000-0000-000000000000"
_USER_ID = "a1b2c3d4-0000-0000-0000-000000000001"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_store() -> None:
    """Reset the shared store before every test in this module."""
    get_store().reset()


@pytest.fixture()
def client() -> TestClient:
    """Return a synchronous TestClient for the FastAPI app."""
    return TestClient(app, raise_server_exceptions=False)


# ===========================================================================
# POST /tapp/v1/accounts/link
# ===========================================================================


class TestLinkAccount:
    """Tests for POST /tapp/v1/accounts/link."""

    def test_link_unknown_iban_returns_404(self, client: TestClient) -> None:
        response = client.post(
            "/tapp/v1/accounts/link",
            json={
                "user_id": _USER_ID,
                "iban": _UNKNOWN_IBAN,
                "bank_code": "FAKE",
                "alias": "Ghost",
            },
        )
        assert response.status_code == 404
        body = response.json()
        assert body["error"] == "TAPP-001"
        assert _UNKNOWN_IBAN in body["detail"]

    def test_link_already_linked_returns_409(self, client: TestClient) -> None:
        response = client.post(
            "/tapp/v1/accounts/link",
            json={
                "user_id": _USER_ID,
                "iban": _LINKED_IBAN,
                "bank_code": "BCP",
            },
        )
        assert response.status_code == 409
        body = response.json()
        assert body["error"] == "TAPP-002"

    def test_link_after_unlink_returns_200(self, client: TestClient) -> None:
        # Unlink first.
        client.delete(f"/tapp/v1/accounts/{_LINKED_ACCOUNT_ID}/unlink")

        response = client.post(
            "/tapp/v1/accounts/link",
            json={
                "user_id": _USER_ID,
                "iban": _LINKED_IBAN,
                "bank_code": "BCP",
                "alias": "BCP Re-linked",
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["account_id"] == _LINKED_ACCOUNT_ID
        assert body["status"] == "LINKED"
        assert body["iban"] == _LINKED_IBAN
        assert body["alias"] == "BCP Re-linked"
        assert "linked_at" in body

    def test_link_missing_required_field_returns_422(
        self, client: TestClient
    ) -> None:
        response = client.post(
            "/tapp/v1/accounts/link",
            json={"user_id": _USER_ID},  # iban and bank_code missing
        )
        assert response.status_code == 422

    def test_link_response_shape(self, client: TestClient) -> None:
        """Response must include all documented fields."""
        client.delete(f"/tapp/v1/accounts/{_LINKED_ACCOUNT_ID}/unlink")

        body = client.post(
            "/tapp/v1/accounts/link",
            json={"user_id": _USER_ID, "iban": _LINKED_IBAN, "bank_code": "BCP"},
        ).json()

        for field in ("account_id", "user_id", "iban", "bank_code", "alias", "status", "linked_at"):
            assert field in body, f"Missing field: {field}"


# ===========================================================================
# GET /tapp/v1/accounts/{account_id}/status
# ===========================================================================


class TestGetAccountStatus:
    """Tests for GET /tapp/v1/accounts/{account_id}/status."""

    def test_get_status_of_seeded_account_returns_200(
        self, client: TestClient
    ) -> None:
        response = client.get(f"/tapp/v1/accounts/{_LINKED_ACCOUNT_ID}/status")
        assert response.status_code == 200
        body = response.json()
        assert body["account_id"] == _LINKED_ACCOUNT_ID
        assert body["status"] == "LINKED"
        assert body["bank_code"] == "BCP"
        assert "iban_masked" in body
        # Mask check: must not expose the full IBAN.
        assert body["iban_masked"] != _LINKED_IBAN
        assert "..." in body["iban_masked"]

    def test_get_status_of_unknown_account_returns_404(
        self, client: TestClient
    ) -> None:
        response = client.get(f"/tapp/v1/accounts/{_UNKNOWN_ID}/status")
        assert response.status_code == 404
        assert response.json()["error"] == "TAPP-001"

    def test_get_status_after_unlink_shows_unlinked(
        self, client: TestClient
    ) -> None:
        client.delete(f"/tapp/v1/accounts/{_LINKED_ACCOUNT_ID}/unlink")
        response = client.get(f"/tapp/v1/accounts/{_LINKED_ACCOUNT_ID}/status")
        body = response.json()
        assert body["status"] == "UNLINKED"
        assert body["unlinked_at"] is not None

    def test_all_three_seeded_accounts_return_200(
        self, client: TestClient
    ) -> None:
        ids = [
            "f47ac10b-58cc-4372-a567-0e02b2c3d479",
            "c9d8e7f6-0000-0000-0000-000000000002",
            "d1e2f3a4-0000-0000-0000-000000000003",
        ]
        for account_id in ids:
            r = client.get(f"/tapp/v1/accounts/{account_id}/status")
            assert r.status_code == 200, f"Expected 200 for {account_id}"


# ===========================================================================
# DELETE /tapp/v1/accounts/{account_id}/unlink
# ===========================================================================


class TestUnlinkAccount:
    """Tests for DELETE /tapp/v1/accounts/{account_id}/unlink."""

    def test_unlink_linked_account_returns_200(
        self, client: TestClient
    ) -> None:
        response = client.delete(f"/tapp/v1/accounts/{_LINKED_ACCOUNT_ID}/unlink")
        assert response.status_code == 200
        body = response.json()
        assert body["account_id"] == _LINKED_ACCOUNT_ID
        assert body["status"] == "UNLINKED"
        assert "unlinked_at" in body

    def test_unlink_unknown_account_returns_404(
        self, client: TestClient
    ) -> None:
        response = client.delete(f"/tapp/v1/accounts/{_UNKNOWN_ID}/unlink")
        assert response.status_code == 404
        assert response.json()["error"] == "TAPP-001"

    def test_unlink_is_idempotent(self, client: TestClient) -> None:
        client.delete(f"/tapp/v1/accounts/{_LINKED_ACCOUNT_ID}/unlink")
        response = client.delete(f"/tapp/v1/accounts/{_LINKED_ACCOUNT_ID}/unlink")
        assert response.status_code == 200
        assert response.json()["status"] == "UNLINKED"