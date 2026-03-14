from app.ui_hunt import run_ui_smoke_checks


def test_ui_issue_hunt_smoke_checks_pass() -> None:
    result = run_ui_smoke_checks(run_id="test-ui-hunt")
    assert result.success
    names = {check.name for check in result.checks}
    for expected in {
        "route_html_/",
        "route_html_/tried",
        "route_html_/ratings/new",
        "route_html_/settings",
        "static_css",
        "static_js",
        "i18n_labels",
        "auth_login_a",
        "manual_run_a",
        "manual_run_updates_last_run_a",
        "recommended_buys",
        "tried_wines_flow",
        "rating_delete",
        "user_settings_read",
        "user_settings_update",
        "permission_user_b_trigger",
        "permission_user_b_no_run_change",
    }:
        assert expected in names
