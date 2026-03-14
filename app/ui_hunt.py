from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from fastapi.testclient import TestClient

from app.main import app
from app.time_utils import utc_now_iso


@dataclass(slots=True)
class UISmokeCheck:
    name: str
    success: bool
    details: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(slots=True)
class UISmokeResult:
    run_id: str
    started_at: str
    finished_at: str
    checks: list[UISmokeCheck]

    @property
    def success(self) -> bool:
        return all(check.success for check in self.checks)

    def to_dict(self) -> dict[str, object]:
        return {
            "run_id": self.run_id,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "status": "success" if self.success else "fail",
            "checks": [check.to_dict() for check in self.checks],
        }


def _check(condition: bool, ok: str, fail: str) -> tuple[bool, str]:
    return (True, ok) if condition else (False, fail)


def _json(response: Any) -> dict[str, Any]:
    payload = response.json()
    return payload if isinstance(payload, dict) else {"payload": payload}


def run_ui_smoke_checks(run_id: str) -> UISmokeResult:
    started_at = utc_now_iso()
    checks: list[UISmokeCheck] = []

    def record(name: str, success: bool, details: str) -> None:
        checks.append(UISmokeCheck(name=name, success=success, details=details))

    with TestClient(app) as client:
        # 1) App shell and routes.
        for path in ["/", "/tried", "/ratings/new", "/settings"]:
            response = client.get(path)
            success, details = _check(
                response.status_code == 200 and "text/html" in response.headers.get("content-type", ""),
                f"{path} serves html",
                f"{path} unexpected status/content-type: {response.status_code} {response.headers.get('content-type')}",
            )
            record(f"route_html_{path}", success, details)

        # 2) Static assets.
        css_response = client.get("/static/styles.css")
        success, details = _check(
            css_response.status_code == 200 and "color-bg-default" in css_response.text,
            "styles.css served with design tokens",
            "styles.css missing or token definitions absent",
        )
        record("static_css", success, details)

        js_response = client.get("/static/app.js")
        success, details = _check(
            js_response.status_code == 200 and "const I18N" in js_response.text,
            "app.js served with i18n map",
            "app.js missing or i18n map absent",
        )
        record("static_js", success, details)

        success, details = _check(
            all(marker in js_response.text for marker in ["Home", "Tried Wines", "Главная", "Пробованные вина"]),
            "en/ru labels present in frontend bundle",
            "missing expected EN/RU route labels in frontend bundle",
        )
        record("i18n_labels", success, details)

        # 3) Auth checks.
        bad_login = client.post("/auth/login", json={"user_id": "A", "password": "bad-password"})
        success, details = _check(
            bad_login.status_code == 401,
            "invalid login rejected",
            f"invalid login unexpected status={bad_login.status_code}",
        )
        record("auth_invalid_login", success, details)

        login_a = client.post("/auth/login", json={"user_id": "A", "password": "changeme-a"})
        token_a = _json(login_a).get("access_token", "")
        success, details = _check(
            login_a.status_code == 200 and bool(token_a),
            "login A succeeded",
            f"login A failed status={login_a.status_code}",
        )
        record("auth_login_a", success, details)
        headers_a = {"Authorization": f"Bearer {token_a}"} if token_a else {}

        # 4) Unauthorized recommendation access.
        rec_unauth = client.get("/recommendations?kind=recommended_buys")
        success, details = _check(
            rec_unauth.status_code == 401,
            "protected endpoint requires auth",
            f"protected endpoint expected 401, got {rec_unauth.status_code}",
        )
        record("auth_protected_recommendations", success, details)

        # 5) Manual run and recommendation retrieval.
        status_before_a = client.get("/status/last-run")
        before_payload_a = _json(status_before_a) if status_before_a.status_code == 200 else {}
        previous_run_id_a = before_payload_a.get("run_id")

        run_response = client.post("/runs/trigger", headers=headers_a, json={"mode": "manual"})
        run_json = _json(run_response)
        run_id_a = run_json.get("run_id")
        success, details = _check(
            run_response.status_code == 200 and run_json.get("status") == "success",
            f"manual run succeeded run_id={run_json.get('run_id')}",
            f"manual run failed status={run_response.status_code} payload={run_json}",
        )
        record("manual_run_a", success, details)

        status_after_a = client.get("/status/last-run")
        after_payload_a = _json(status_after_a) if status_after_a.status_code == 200 else {}
        success, details = _check(
            status_after_a.status_code == 200
            and bool(run_id_a)
            and after_payload_a.get("run_id") == run_id_a
            and after_payload_a.get("run_id") != previous_run_id_a,
            f"last-run updated to {run_id_a} after user A trigger",
            (
                "last-run not updated by user A trigger "
                f"before={previous_run_id_a} after={after_payload_a.get('run_id')} triggered={run_id_a}"
            ),
        )
        record("manual_run_updates_last_run_a", success, details)

        recs = client.get("/recommendations?kind=recommended_buys", headers=headers_a)
        recs_json = _json(recs)
        items = recs_json.get("items", []) if isinstance(recs_json.get("items", []), list) else []
        success, details = _check(
            recs.status_code == 200 and len(items) > 0,
            f"recommended buys loaded items={len(items)}",
            f"recommended buys failed status={recs.status_code} payload={recs_json}",
        )
        record("recommended_buys", success, details)

        favorites = client.get("/favorites/cheapest", headers=headers_a)
        success, details = _check(
            favorites.status_code == 200,
            "favorites endpoint reachable",
            f"favorites failed status={favorites.status_code}",
        )
        record("cheapest_favorites", success, details)

        # 6) Rating + tried flow.
        wine_id = items[0]["wine_id"] if items else 1
        rating = client.post(
            "/ratings",
            headers=headers_a,
            json={"wine_id": wine_id, "rating_1_5": 4, "comment": "ui smoke"},
        )
        rating_payload = _json(rating)
        rating_id = rating_payload.get("rating_id")
        success, details = _check(
            rating.status_code == 200 and rating_payload.get("ok") is True,
            f"rating submission ok for wine_id={wine_id}",
            f"rating submission failed status={rating.status_code} payload={rating_payload}",
        )
        record("rating_submit", success, details)

        tried = client.get("/wines/tried?query=", headers=headers_a)
        tried_json = tried.json() if tried.status_code == 200 else []
        has_rated = any(row.get("wine_id") == wine_id for row in tried_json) if isinstance(tried_json, list) else False
        success, details = _check(
            tried.status_code == 200 and has_rated,
            "tried wines includes rated item",
            f"tried wines missing rated item or bad response status={tried.status_code}",
        )
        record("tried_wines_flow", success, details)

        if rating_id is not None:
            deleted = client.delete(f"/ratings/{rating_id}", headers=headers_a)
            delete_payload = _json(deleted)
            success, details = _check(
                deleted.status_code == 200 and delete_payload.get("ok") is True,
                f"rating deleted rating_id={rating_id}",
                f"rating delete failed status={deleted.status_code} payload={delete_payload}",
            )
            record("rating_delete", success, details)

        # 7) User settings config page API.
        user_settings = client.get("/users/me/settings", headers=headers_a)
        settings_payload = _json(user_settings)
        success, details = _check(
            user_settings.status_code == 200 and settings_payload.get("user_id") == "A",
            "settings endpoint returns user config",
            f"user settings failed status={user_settings.status_code} payload={settings_payload}",
        )
        record("user_settings_read", success, details)

        saved_settings = client.patch("/users/me/settings", headers=headers_a, json={"locale": "ru"})
        updated_payload = _json(saved_settings)
        success, details = _check(
            saved_settings.status_code == 200 and updated_payload.get("locale") == "ru",
            "settings update persisted locale",
            f"user settings update failed status={saved_settings.status_code} payload={updated_payload}",
        )
        record("user_settings_update", success, details)

        # 8) Permissions check for User B.
        status_before_b = client.get("/status/last-run")
        before_payload_b = _json(status_before_b) if status_before_b.status_code == 200 else {}
        run_before_b = before_payload_b.get("run_id")

        login_b = client.post("/auth/login", json={"user_id": "B", "password": "changeme-b"})
        token_b = _json(login_b).get("access_token", "")
        headers_b = {"Authorization": f"Bearer {token_b}"} if token_b else {}
        trigger_b = client.post("/runs/trigger", headers=headers_b, json={"mode": "manual"})
        success, details = _check(
            trigger_b.status_code == 403,
            "manual run denied for user B",
            f"user B trigger expected 403, got {trigger_b.status_code}",
        )
        record("permission_user_b_trigger", success, details)

        status_after_b = client.get("/status/last-run")
        after_payload_b = _json(status_after_b) if status_after_b.status_code == 200 else {}
        success, details = _check(
            status_after_b.status_code == 200 and after_payload_b.get("run_id") == run_before_b,
            f"user B trigger did not change last-run ({run_before_b})",
            (
                "user B trigger unexpectedly changed last-run "
                f"before={run_before_b} after={after_payload_b.get('run_id')}"
            ),
        )
        record("permission_user_b_no_run_change", success, details)

    return UISmokeResult(
        run_id=run_id,
        started_at=started_at,
        finished_at=utc_now_iso(),
        checks=checks,
    )
