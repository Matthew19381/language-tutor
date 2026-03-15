import logging
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models.achievement import Achievement

logger = logging.getLogger(__name__)

# Achievement definitions: type -> (title, description, icon)
ACHIEVEMENT_DEFS = {
    "first_lesson": ("First Step", "Completed your very first lesson", "🎯"),
    "lessons_5": ("Getting Started", "Completed 5 lessons", "📚"),
    "lessons_10": ("Dedicated Learner", "Completed 10 lessons", "🏅"),
    "lessons_25": ("Consistent Scholar", "Completed 25 lessons", "🎖️"),
    "lessons_50": ("Half Century", "Completed 50 lessons", "🏆"),
    "streak_3": ("On a Roll", "3-day learning streak", "🔥"),
    "streak_7": ("Week Warrior", "7-day learning streak", "⚡"),
    "streak_14": ("Two Week Champion", "14-day learning streak", "💪"),
    "streak_30": ("Monthly Master", "30-day learning streak", "👑"),
    "first_test": ("Test Taker", "Completed your first test", "📝"),
    "first_test_perfect": ("Perfect Score", "Scored 100% on a test", "⭐"),
    "tests_10": ("Quiz Master", "Completed 10 tests", "🎓"),
    "xp_100": ("XP Collector", "Earned 100 XP", "✨"),
    "xp_500": ("XP Hunter", "Earned 500 XP", "💫"),
    "xp_1000": ("XP Legend", "Earned 1000 XP", "🌟"),
    "level_5": ("Level 5 Reached", "Reached level 5", "🚀"),
    "level_10": ("Level 10 Reached", "Reached level 10", "🎊"),
    "level_25": ("Level 25 Reached", "Halfway to mastery", "🏹"),
}


def calculate_level_from_xp(xp: int) -> dict:
    """Calculate level (1-50) from XP using a quadratic curve."""
    # Level n requires (n-1)^2 * 20 total XP
    # Level 1: 0, Level 2: 20, Level 5: 320, Level 10: 1620, Level 25: 11520, Level 50: 48020
    level = 1
    for n in range(1, 51):
        required = (n - 1) ** 2 * 20
        if xp >= required:
            level = n
        else:
            break

    current_xp_req = (level - 1) ** 2 * 20
    next_xp_req = level ** 2 * 20 if level < 50 else current_xp_req + 1000

    if level < 50:
        progress = ((xp - current_xp_req) / (next_xp_req - current_xp_req)) * 100
    else:
        progress = 100.0

    return {
        "level": level,
        "level_name": _get_level_name(level),
        "xp": xp,
        "current_level_xp": current_xp_req,
        "next_level_xp": next_xp_req,
        "progress_percent": min(100.0, max(0.0, progress)),
        "max_level": 50,
    }


def _get_level_name(level: int) -> str:
    if level <= 5:
        return "Beginner"
    elif level <= 10:
        return "Elementary"
    elif level <= 15:
        return "Pre-Intermediate"
    elif level <= 20:
        return "Intermediate"
    elif level <= 25:
        return "Upper-Intermediate"
    elif level <= 30:
        return "Advanced"
    elif level <= 35:
        return "Proficient"
    elif level <= 40:
        return "Expert"
    elif level <= 45:
        return "Master"
    else:
        return "Grand Master"


def check_and_award_achievements(user, db: Session) -> list:
    """Check which achievements the user has earned and award new ones. Returns list of newly awarded achievements."""
    from backend.models.lesson import Lesson
    from backend.models.test_result import TestResult

    # Fetch data needed for checks
    completed_lessons = db.query(Lesson).filter(
        Lesson.user_id == user.id,
        Lesson.is_completed == True
    ).count()

    test_results = db.query(TestResult).filter(
        TestResult.user_id == user.id
    ).all()

    total_tests = len(test_results)
    perfect_tests = sum(1 for t in test_results if t.score >= 100)
    xp = user.total_xp
    streak = user.streak_days or 0
    level_info = calculate_level_from_xp(xp)
    current_level = level_info["level"]

    # Already unlocked
    existing = {a.achievement_type for a in db.query(Achievement).filter(
        Achievement.user_id == user.id
    ).all()}

    candidates = []

    def maybe_award(ach_type: str):
        if ach_type not in existing and ach_type in ACHIEVEMENT_DEFS:
            candidates.append(ach_type)

    # Lesson-based
    if completed_lessons >= 1: maybe_award("first_lesson")
    if completed_lessons >= 5: maybe_award("lessons_5")
    if completed_lessons >= 10: maybe_award("lessons_10")
    if completed_lessons >= 25: maybe_award("lessons_25")
    if completed_lessons >= 50: maybe_award("lessons_50")

    # Streak-based
    if streak >= 3: maybe_award("streak_3")
    if streak >= 7: maybe_award("streak_7")
    if streak >= 14: maybe_award("streak_14")
    if streak >= 30: maybe_award("streak_30")

    # Test-based
    if total_tests >= 1: maybe_award("first_test")
    if perfect_tests >= 1: maybe_award("first_test_perfect")
    if total_tests >= 10: maybe_award("tests_10")

    # XP-based
    if xp >= 100: maybe_award("xp_100")
    if xp >= 500: maybe_award("xp_500")
    if xp >= 1000: maybe_award("xp_1000")

    # Level-based
    if current_level >= 5: maybe_award("level_5")
    if current_level >= 10: maybe_award("level_10")
    if current_level >= 25: maybe_award("level_25")

    # Award new achievements
    newly_awarded = []
    for ach_type in candidates:
        ach = Achievement(
            user_id=user.id,
            achievement_type=ach_type,
            unlocked_at=datetime.utcnow(),
            notified=False
        )
        db.add(ach)
        title, description, icon = ACHIEVEMENT_DEFS[ach_type]
        newly_awarded.append({
            "type": ach_type,
            "title": title,
            "description": description,
            "icon": icon,
        })

    if newly_awarded:
        db.commit()

    return newly_awarded


def get_all_achievements_for_user(user_id: int, db: Session) -> dict:
    """Return all achievements (earned + locked) for display."""
    earned_records = db.query(Achievement).filter(
        Achievement.user_id == user_id
    ).all()
    earned_types = {a.achievement_type: a for a in earned_records}

    all_achievements = []
    for ach_type, (title, description, icon) in ACHIEVEMENT_DEFS.items():
        record = earned_types.get(ach_type)
        all_achievements.append({
            "type": ach_type,
            "title": title,
            "description": description,
            "icon": icon,
            "earned": record is not None,
            "unlocked_at": record.unlocked_at.isoformat() if record else None,
        })

    return {
        "total": len(ACHIEVEMENT_DEFS),
        "earned": len(earned_types),
        "achievements": all_achievements,
    }


def get_unnotified_achievements(user_id: int, db: Session) -> list:
    """Return achievements that haven't been shown as toast yet, then mark them notified."""
    unnotified = db.query(Achievement).filter(
        Achievement.user_id == user_id,
        Achievement.notified == False
    ).all()

    result = []
    for a in unnotified:
        if a.achievement_type in ACHIEVEMENT_DEFS:
            title, description, icon = ACHIEVEMENT_DEFS[a.achievement_type]
            result.append({
                "type": a.achievement_type,
                "title": title,
                "description": description,
                "icon": icon,
                "unlocked_at": a.unlocked_at.isoformat(),
            })
        a.notified = True

    if result:
        db.commit()

    return result
