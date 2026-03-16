"""Tests for /api/tests/* endpoints."""
import json
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock


MOCK_TEST_DATA = {
    "success": True,
    "lesson_id": 1,
    "lesson_title": "Test Lesson",
    "already_taken": False,
    "questions": [
        {
            "id": 1,
            "type": "multiple_choice",
            "question": "How do you say 'dog' in German?",
            "options": ["Katze", "Hund", "Vogel", "Fisch"],
            "correct_answer": "Hund",
        }
    ],
    "cefr_level": "A1",
    "language": "German",
}

MOCK_SUBMIT_RESULT = {
    "success": True,
    "test_result_id": 1,
    "score": 100.0,
    "errors": [],
    "performance_summary": "Excellent!",
    "xp_earned": 50,
    "new_achievements": [],
}


def _create_test_result(db, user_id, score=80.0, test_type="daily"):
    from backend.models.test_result import TestResult
    result = TestResult(
        user_id=user_id,
        test_type=test_type,
        score=score,
        answers=json.dumps({}),
        errors=json.dumps([]),
        cefr_level="A1",
        language="German",
        created_at=datetime.utcnow(),
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


# ---------------------------------------------------------------------------
# GET /api/tests/history/{user_id}
# ---------------------------------------------------------------------------

def test_test_history_empty(client, sample_user):
    uid = sample_user["user_id"]
    # get_test_history returns a list directly (the router wraps it in {"history": ..., "stats": ...})
    with patch("backend.routers.tests.get_test_history",
               new=MagicMock(return_value=[])):
        r = client.get(f"/api/tests/history/{uid}")
    assert r.status_code == 200
    data = r.json()
    assert data["history"] == []
    assert data["stats"]["total_tests"] == 0


def test_test_history_with_results(client, sample_user, db):
    uid = sample_user["user_id"]
    _create_test_result(db, uid, score=75.0, test_type="daily")
    _create_test_result(db, uid, score=90.0, test_type="weekly")

    mock_list = [
        {"id": 1, "test_type": "daily", "score": 75.0,
         "cefr_level": "A1", "created_at": datetime.utcnow().isoformat(),
         "errors_count": 0},
        {"id": 2, "test_type": "weekly", "score": 90.0,
         "cefr_level": "A1", "created_at": datetime.utcnow().isoformat(),
         "errors_count": 0},
    ]
    with patch("backend.routers.tests.get_test_history",
               new=MagicMock(return_value=mock_list)):
        r = client.get(f"/api/tests/history/{uid}")
    data = r.json()
    assert data["stats"]["total_tests"] == 2
    assert data["stats"]["best_score"] == 90.0


# ---------------------------------------------------------------------------
# GET /api/tests/result/{result_id}
# ---------------------------------------------------------------------------

def test_get_test_result_found(client, sample_user, db):
    uid = sample_user["user_id"]
    result = _create_test_result(db, uid, score=85.0)

    r = client.get(f"/api/tests/result/{result.id}")
    assert r.status_code == 200
    data = r.json()
    assert data["score"] == 85.0
    assert data["test_type"] == "daily"
    assert data["user_id"] == uid


def test_get_test_result_not_found(client):
    r = client.get("/api/tests/result/99999")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/tests/daily/{user_id}  (AI mocked via test_generator)
# ---------------------------------------------------------------------------

def test_get_daily_test(client, sample_user, db):
    uid = sample_user["user_id"]
    # Create today's lesson so the router can find it
    from backend.models.lesson import Lesson
    lesson = Lesson(
        user_id=uid, day_number=1, title="Today's Lesson", topic="Greetings",
        content=json.dumps({"vocabulary": []}), cefr_level="A1", language="German",
        is_completed=False, created_at=datetime.now(),
    )
    db.add(lesson)
    db.commit()

    with patch("backend.routers.tests.get_or_create_daily_test",
               new=AsyncMock(return_value=MOCK_TEST_DATA)):
        r = client.get(f"/api/tests/daily/{uid}")
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert len(data["questions"]) == 1


# ---------------------------------------------------------------------------
# POST /api/tests/submit
# ---------------------------------------------------------------------------

def test_submit_test(client, sample_user):
    uid = sample_user["user_id"]
    with patch("backend.routers.tests.submit_test",
               new=AsyncMock(return_value=MOCK_SUBMIT_RESULT)):
        r = client.post("/api/tests/submit", json={
            "user_id": uid,
            "test_type": "daily",
            "questions": [],
            "answers": {},
        })
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert data["score"] == 100.0
    assert data["xp_earned"] == 50
