from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

import jwt
from fastapi.testclient import TestClient

from api.auth import get_current_user_id
from api.database import database
from api.main import app


class FakeDatabase:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, dict]] = []

    def request(self, method: str, table: str, **kwargs):
        self.calls.append((method, table, kwargs))
        if method == "GET" and table == "watchlists":
            return [{"id": 1, "user_id": kwargs["params"]["user_id"].removeprefix("eq.")}]
        return [{"id": 1, "name": "Research"}]


def test_private_route_rejects_missing_token():
    client = TestClient(app)
    response = client.get("/api/v1/watchlists")
    assert response.status_code == 401


def test_valid_token_uses_authenticated_subject_and_ownership_filter():
    secret = "test-secret"
    auth_settings = SimpleNamespace(
        supabase_url="https://example.supabase.co",
        supabase_jwt_secret=secret,
    )
    token = jwt.encode(
        {"sub": "user-a", "role": "authenticated", "aud": "authenticated", "iss": "https://example.supabase.co/auth/v1"},
        secret,
        algorithm="HS256",
    )
    fake_db = FakeDatabase()
    app.dependency_overrides[database] = lambda: fake_db
    try:
        with patch("api.auth.settings", auth_settings):
            response = TestClient(app).get(
                "/api/v1/watchlists",
                headers={"Authorization": f"Bearer {token}"},
            )
        assert response.status_code == 200
        assert fake_db.calls[0][2]["params"]["user_id"] == "eq.user-a"
    finally:
        app.dependency_overrides.clear()


def test_invalid_token_is_rejected():
    client = TestClient(app)
    response = client.get("/api/v1/watchlists", headers={"Authorization": "Bearer invalid"})
    assert response.status_code == 401
