from fastapi.testclient import TestClient

from app.main import app


def _auth_headers(client: TestClient, user_id: str = "A", password: str = "changeme-a") -> dict[str, str]:
    login = client.post("/auth/login", json={"user_id": user_id, "password": password})
    assert login.status_code == 200
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_login_invalid_credentials_returns_401() -> None:
    with TestClient(app) as client:
        bad = client.post("/auth/login", json={"user_id": "A", "password": "wrong"})
        assert bad.status_code == 401


def test_protected_endpoints_require_auth() -> None:
    with TestClient(app) as client:
        assert client.get("/users/me").status_code == 401
        assert client.get("/recommendations?kind=recommended_buys").status_code == 401
        assert client.get("/favorites/cheapest").status_code == 401
        assert client.get("/wines/tried").status_code == 401
        assert client.post("/ratings", json={"wine_id": 1, "rating_1_5": 4}).status_code == 401
        assert client.post("/runs/trigger", json={"mode": "manual"}).status_code == 401


def test_health_and_recommendations_flow() -> None:
    with TestClient(app) as client:
        headers = _auth_headers(client)

        trigger = client.post("/runs/trigger", headers=headers, json={"mode": "manual"})
        assert trigger.status_code == 200

        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["status"] == "ok"

        recs = client.get("/recommendations?kind=recommended_buys", headers=headers)
        assert recs.status_code == 200
        items = recs.json()["items"]
        assert isinstance(items, list)
        assert len(items) >= 1


def test_recommendations_without_successful_run_returns_404() -> None:
    with TestClient(app) as client:
        headers = _auth_headers(client)
        recs = client.get("/recommendations?kind=recommended_buys", headers=headers)
        assert recs.status_code == 404
        cheapest = client.get("/favorites/cheapest", headers=headers)
        assert cheapest.status_code == 404


def test_rating_submission_and_tried_search() -> None:
    with TestClient(app) as client:
        headers = _auth_headers(client)
        trigger = client.post("/runs/trigger", headers=headers, json={"mode": "manual"})
        assert trigger.status_code == 200

        recs = client.get("/recommendations?kind=recommended_buys", headers=headers).json()["items"]
        wine_id = recs[0]["wine_id"]

        rating = client.post(
            "/ratings",
            headers=headers,
            json={"wine_id": wine_id, "rating_1_5": 5, "comment": "Great value"},
        )
        assert rating.status_code == 200
        assert rating.json()["ok"] is True

        tried = client.get("/wines/tried?query=", headers=headers)
        assert tried.status_code == 200
        body = tried.json()
        assert any(item["wine_id"] == wine_id for item in body)


def test_user_b_cannot_trigger_manual_run() -> None:
    with TestClient(app) as client:
        headers_b = _auth_headers(client, user_id="B", password="changeme-b")
        denied = client.post("/runs/trigger", headers=headers_b, json={"mode": "manual"})
        assert denied.status_code == 403


def test_rating_unknown_wine_returns_404() -> None:
    with TestClient(app) as client:
        headers = _auth_headers(client)
        missing = client.post(
            "/ratings",
            headers=headers,
            json={"wine_id": 999999, "rating_1_5": 5, "comment": "missing"},
        )
        assert missing.status_code == 404


def test_status_last_run_returns_null_when_empty() -> None:
    with TestClient(app) as client:
        status = client.get("/status/last-run")
        assert status.status_code == 200
        assert status.json() == {"run": None}


def test_favorites_get_populated_after_rating_and_rerun() -> None:
    with TestClient(app) as client:
        headers = _auth_headers(client)

        first_run = client.post("/runs/trigger", headers=headers, json={"mode": "manual"})
        assert first_run.status_code == 200
        recs = client.get("/recommendations?kind=recommended_buys", headers=headers).json()["items"]
        wine_id = recs[0]["wine_id"]

        rating = client.post(
            "/ratings",
            headers=headers,
            json={"wine_id": wine_id, "rating_1_5": 5, "comment": "favorite candidate"},
        )
        assert rating.status_code == 200

        second_run = client.post("/runs/trigger", headers=headers, json={"mode": "manual"})
        assert second_run.status_code == 200

        favorites = client.get("/favorites/cheapest", headers=headers)
        assert favorites.status_code == 200
        items = favorites.json()["items"]
        assert any(item["wine_id"] == wine_id for item in items)


def test_frontend_routes_serve_html() -> None:
    with TestClient(app) as client:
        for path in ["/", "/tried", "/ratings/new", "/settings"]:
            response = client.get(path)
            assert response.status_code == 200
            assert "text/html" in response.headers["content-type"]
