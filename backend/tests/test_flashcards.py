"""Tests for /api/flashcards/* endpoints (no AI calls needed)."""
from datetime import datetime, timedelta


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def add_card(client, user_id, word="Hund", translation="dog", example=None):
    payload = {"word": word, "translation": translation}
    if example:
        payload["example_sentence"] = example
    return client.post(f"/api/flashcards/{user_id}/add", json=payload)


# ---------------------------------------------------------------------------
# GET /api/flashcards/{user_id}
# ---------------------------------------------------------------------------

def test_get_flashcards_empty(client, sample_user):
    uid = sample_user["user_id"]
    r = client.get(f"/api/flashcards/{uid}")
    assert r.status_code == 200
    data = r.json()
    assert data["flashcards"] == []
    assert data["total"] == 0


def test_get_flashcards_user_not_found(client):
    r = client.get("/api/flashcards/99999")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# POST /api/flashcards/{user_id}/add
# ---------------------------------------------------------------------------

def test_add_flashcard_success(client, sample_user):
    uid = sample_user["user_id"]
    r = add_card(client, uid, "Katze", "cat", "Die Katze schläft.")
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert isinstance(data["id"], int)


def test_add_flashcard_appears_in_list(client, sample_user):
    uid = sample_user["user_id"]
    add_card(client, uid, "Hund", "dog")
    r = client.get(f"/api/flashcards/{uid}")
    cards = r.json()["flashcards"]
    assert len(cards) == 1
    assert cards[0]["word"] == "Hund"
    assert cards[0]["translation"] == "dog"


def test_add_flashcard_duplicate_prevented(client, sample_user):
    uid = sample_user["user_id"]
    add_card(client, uid, "Hund", "dog")
    r2 = add_card(client, uid, "Hund", "dog again")
    assert r2.status_code == 200
    data = r2.json()
    assert data["success"] is False
    assert "already exists" in data["message"]


def test_add_flashcard_user_not_found(client):
    r = client.post("/api/flashcards/99999/add", json={"word": "X", "translation": "Y"})
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/flashcards/{user_id}/due
# ---------------------------------------------------------------------------

def test_due_flashcards_empty(client, sample_user):
    uid = sample_user["user_id"]
    r = client.get(f"/api/flashcards/{uid}/due")
    assert r.status_code == 200
    # Newly created cards have next_review_date = now, so they ARE due
    assert "due_cards" in r.json()
    assert "count" in r.json()


def test_due_flashcards_newly_added_are_due(client, sample_user):
    uid = sample_user["user_id"]
    add_card(client, uid, "Buch", "book")
    r = client.get(f"/api/flashcards/{uid}/due")
    data = r.json()
    assert data["count"] >= 1


def test_due_flashcards_user_not_found(client):
    r = client.get("/api/flashcards/99999/due")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# POST /api/flashcards/{flashcard_id}/review
# ---------------------------------------------------------------------------

def test_review_flashcard_not_found(client):
    r = client.post("/api/flashcards/99999/review", json={"rating": 3})
    assert r.status_code == 404


def test_review_rating_again(client, sample_user):
    uid = sample_user["user_id"]
    add_r = add_card(client, uid, "Tisch", "table")
    card_id = add_r.json()["id"]

    r = client.post(f"/api/flashcards/{card_id}/review", json={"rating": 1})
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert data["new_interval"] == 1          # Again resets to 1
    assert data["new_ease_factor"] <= 2.5


def test_review_rating_good(client, sample_user):
    uid = sample_user["user_id"]
    add_r = add_card(client, uid, "Stuhl", "chair")
    card_id = add_r.json()["id"]

    r = client.post(f"/api/flashcards/{card_id}/review", json={"rating": 3})
    assert r.status_code == 200
    data = r.json()
    assert data["new_interval"] >= 3          # Good from interval=1 → 3


def test_review_rating_easy_increases_ease_factor(client, sample_user):
    uid = sample_user["user_id"]
    add_r = add_card(client, uid, "Fenster", "window")
    card_id = add_r.json()["id"]

    r = client.post(f"/api/flashcards/{card_id}/review", json={"rating": 4})
    assert r.status_code == 200
    data = r.json()
    assert data["new_interval"] >= 4
    assert data["new_ease_factor"] >= 2.5     # Easy raises ease factor


def test_review_returns_next_review_date(client, sample_user):
    uid = sample_user["user_id"]
    add_r = add_card(client, uid, "Auto", "car")
    card_id = add_r.json()["id"]

    r = client.post(f"/api/flashcards/{card_id}/review", json={"rating": 3})
    data = r.json()
    assert "next_review" in data
    # next_review should be in the future
    next_review = datetime.fromisoformat(data["next_review"])
    assert next_review > datetime.utcnow()
