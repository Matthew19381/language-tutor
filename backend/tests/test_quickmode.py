"""Tests for /api/quickmode/{user_id} endpoint."""


def test_quickmode_user_not_found(client):
    r = client.get("/api/quickmode/99999")
    assert r.status_code == 404


def test_quickmode_basic_response(client, sample_user):
    uid = sample_user["user_id"]
    r = client.get(f"/api/quickmode/{uid}")
    assert r.status_code == 200
    data = r.json()

    assert data["user_id"] == uid
    assert data["timer_minutes"] == 15
    assert isinstance(data["activities"], list)
    assert len(data["activities"]) > 0


def test_quickmode_activity_structure(client, sample_user):
    uid = sample_user["user_id"]
    r = client.get(f"/api/quickmode/{uid}")
    activities = r.json()["activities"]

    for act in activities:
        assert "id" in act
        assert "title" in act
        assert "estimated_minutes" in act
        assert "priority" in act
        assert "route" in act


def test_quickmode_total_time_is_15(client, sample_user):
    uid = sample_user["user_id"]
    r = client.get(f"/api/quickmode/{uid}")
    data = r.json()
    assert data["total_estimated_minutes"] == 15
