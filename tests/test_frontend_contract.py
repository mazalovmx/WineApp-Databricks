from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def _static_text(client: TestClient, path: str) -> str:
    response = client.get(path)
    assert response.status_code == 200
    return response.text


def test_index_shell_includes_frontend_bundle() -> None:
    with TestClient(app) as client:
        html = _static_text(client, "/")
        assert 'id="app"' in html
        assert '/static/styles.css' in html
        assert '/static/app.js' in html


def test_frontend_declares_all_known_routes() -> None:
    with TestClient(app) as client:
        js = _static_text(client, "/static/app.js")
        assert "const KNOWN_ROUTES" in js
        for route in ['"/"', '"/tried"', '"/ratings/new"', '"/settings"']:
            assert route in js


def test_frontend_contains_user_labels_and_i18n_keys() -> None:
    with TestClient(app) as client:
        js = _static_text(client, "/static/app.js")
        for marker in [
            "userALabel",
            "userBLabel",
            "A — Alexander",
            "B — Elena",
            "A — Александр",
            "B — Елена",
            "saveSettings",
            "settingsSaved",
            "ratingDeleted",
            "deleteConfirm",
        ]:
            assert marker in js


def test_frontend_contains_required_button_actions() -> None:
    with TestClient(app) as client:
        js = _static_text(client, "/static/app.js")
        for action in [
            'data-action="refresh-health"',
            'data-action="trigger-run"',
            'data-action="search-tried"',
            'data-action="clear-tried"',
            'data-action="select-wine"',
            'data-action="delete-rating"',
            'data-action="save-user-settings"',
            'data-action="login"',
            'data-action="logout"',
        ]:
            assert action in js


def test_frontend_restricts_manual_run_button_to_user_a() -> None:
    with TestClient(app) as client:
        js = _static_text(client, "/static/app.js")
        assert 'state.me && state.me.id === "A" ? "" : "disabled"' in js
        assert "unauthorizedRun" in js
