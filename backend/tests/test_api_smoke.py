def test_health_smoke(client):
    # Simple smoke: ensure app responds to 404 on unknown route
    r = client.get("/__not_exists__")
    assert r.status_code == 404
