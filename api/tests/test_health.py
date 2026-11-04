from finsense_api import create_app


def test_health_runs_before_database_exists():
    app = create_app()
    response = app.test_client().get("/api/health")
    assert response.status_code == 200
    body = response.get_json()
    assert body["status"] == "ok"
    assert body["database"] in {"ok", "unavailable"}
