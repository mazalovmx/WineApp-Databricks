from fastapi.testclient import TestClient

from app.main import app


def _auth_headers(client: TestClient, user_id: str = "A", password: str = "changeme-a") -> dict[str, str]:
    login = client.post("/auth/login", json={"user_id": user_id, "password": password})
    assert login.status_code == 200
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


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
