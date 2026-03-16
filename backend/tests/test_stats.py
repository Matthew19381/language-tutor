"""Tests for /api/stats/* and /api/tips/* endpoints."""
from unittest.mock import AsyncMock, patch


# ---------------------------------------------------------------------------
# GET /api/stats/{user_id}
# ---------------------------------------------------------------------------

def test_get_stats_user_not_found(client):
    r = client.get("/api/stats/99999")
    assert r.status_code == 404


def test_get_stats_basic_structure(client, sample_user):
    uid = sample_user["user_id"]
    r = client.get(f"/api/stats/{uid}")
    assert r.status_code == 200
    data = r.json()

    # Top-level keys
    for key in ("user", "level_info", "lessons", "tests", "flashcards",
                "error_categories", "achievements", "new_achievements"):
        assert key in data, f"Missing key: {key}"

    # User sub-object
    assert data["user"]["id"] == uid
    assert data["user"]["name"] == "Test User"
    assert data["user"]["total_xp"] == 0

    # Level info
    li = data["level_info"]
    assert li["level"] == 1
    assert li["xp"] == 0
    assert li["max_level"] == 50

    # Empty lessons / tests
    assert data["lessons"]["total"] == 0
    assert data["tests"]["total_taken"] == 0
    assert data["flashcards"]["total"] == 0


def test_get_stats_achievements_shape(client, sample_user):
    uid = sample_user["user_id"]
    r = client.get(f"/api/stats/{uid}")
    ach = r.json()["achievements"]
    assert "total" in ach
    assert "earned" in ach
    assert isinstance(ach["achievements"], list)
    assert ach["earned"] == 0


# ---------------------------------------------------------------------------
# POST /api/stats/{user_id}/xp
# ---------------------------------------------------------------------------

def test_add_xp_success(client, sample_user):
    uid = sample_user["user_id"]
    r = client.post(f"/api/stats/{uid}/xp", json={"amount": 50, "reason": "test"})
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert data["xp_added"] == 50
    assert data["total_xp"] == 50
    assert data["reason"] == "test"
    assert data["level_info"]["xp"] == 50


def test_add_xp_level_up(client, sample_user):
    uid = sample_user["user_id"]
    # Level 2 requires 20 XP
    client.post(f"/api/stats/{uid}/xp", json={"amount": 20})
    r = client.post(f"/api/stats/{uid}/xp", json={"amount": 0})
    # Verify via stats
    stats = client.get(f"/api/stats/{uid}").json()
    assert stats["level_info"]["level"] >= 2


def test_add_xp_user_not_found(client):
    r = client.post("/api/stats/99999/xp", json={"amount": 10})
    assert r.status_code == 404


def test_add_xp_accumulates(client, sample_user):
    uid = sample_user["user_id"]
    client.post(f"/api/stats/{uid}/xp", json={"amount": 25})
    client.post(f"/api/stats/{uid}/xp", json={"amount": 25})
    r = client.post(f"/api/stats/{uid}/xp", json={"amount": 25})
    assert r.json()["total_xp"] == 75


# ---------------------------------------------------------------------------
# GET /api/stats/{user_id}/leaderboard
# ---------------------------------------------------------------------------

def test_leaderboard_single_user(client, sample_user):
    uid = sample_user["user_id"]
    r = client.get(f"/api/stats/{uid}/leaderboard")
    assert r.status_code == 200
    data = r.json()
    assert data["user_id"] == uid
    assert data["position"] == 1
    assert data["total_users"] == 1
    assert len(data["top_users"]) == 1


def test_leaderboard_ranking(client):
    """User with more XP should rank higher."""
    u1 = client.post("/api/placement/create-user", json={"name": "Alice"}).json()
    u2 = client.post("/api/placement/create-user", json={"name": "Bob"}).json()

    # Give Alice more XP
    client.post(f"/api/stats/{u1['user_id']}/xp", json={"amount": 100})
    client.post(f"/api/stats/{u2['user_id']}/xp", json={"amount": 10})

    r1 = client.get(f"/api/stats/{u1['user_id']}/leaderboard").json()
    r2 = client.get(f"/api/stats/{u2['user_id']}/leaderboard").json()

    assert r1["position"] < r2["position"]  # Alice ranks higher


def test_leaderboard_not_found(client):
    r = client.get("/api/stats/99999/leaderboard")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/tips/{user_id}  (AI call mocked)
# ---------------------------------------------------------------------------

def test_get_tips(client, sample_user):
    uid = sample_user["user_id"]
    mock_tips = {"tips": ["Practice every day", "Use flashcards"]}
    with patch("backend.routers.stats.generate_daily_tips",
               new=AsyncMock(return_value=mock_tips)):
        r = client.get(f"/api/tips/{uid}")
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert len(data["tips"]) == 2


def test_get_tips_not_found(client):
    r = client.get("/api/tips/99999")
    assert r.status_code == 404
