"""Tests for the /api/health endpoint."""


def test_health_check(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"
    assert data["service"] == "LinguaAI API"
    assert "version" in data
