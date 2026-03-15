import logging
from backend.services.gemini_service import generate_json, generate_text

logger = logging.getLogger(__name__)


async def generate_placement_test(language: str, native_language: str) -> dict:
    prompt = f"""Generate a placement test for {language} language learners whose native language is {native_language}.
Create exactly 20 multiple choice questions covering CEFR levels A1 through C2 (escalating difficulty).
Include 5 vocabulary questions, 5 grammar questions, 5 reading comprehension questions, and 5 sentence building questions.

Return a JSON object with this exact structure:
{{
    "questions": [
        {{
            "id": 1,
            "type": "vocabulary",
            "question": "What does the {language} word 'Haus' mean?",
            "options": ["A. House", "B. Car", "C. Tree", "D. Dog"],
            "correct": "A",
            "points": 1,
            "cefr_hint": "A1"
        }}
    ]
}}

Make sure:
- Questions progress from A1 (easy) to C2 (very hard)
- All questions are in English for clarity, with target language words where needed
- Options are labeled A, B, C, D
- correct field contains only the letter (A, B, C, or D)
- Include cefr_hint for each question indicating its difficulty level"""

    try:
        result = await generate_json(prompt)
        return result
    except Exception as e:
        logger.error(f"Error generating placement test: {e}")
        # Return a basic fallback test
        return {
            "questions": [
                {
                    "id": 1,
                    "type": "vocabulary",
                    "question": f"What does the {language} word for 'hello' translate to?",
                    "options": ["A. Goodbye", "B. Hello", "C. Thank you", "D. Please"],
                    "correct": "B",
                    "points": 1,
                    "cefr_hint": "A1"
                }
            ]
        }


async def analyze_placement_results(questions: list, answers: dict, language: str) -> dict:
    questions_summary = []
    for q in questions:
        user_ans = answers.get(str(q["id"]), answers.get(q["id"], ""))
        questions_summary.append({
            "id": q["id"],
            "type": q.get("type", "unknown"),
            "correct": q["correct"],
            "user_answer": user_ans,
            "cefr_hint": q.get("cefr_hint", "A1"),
            "is_correct": str(user_ans).upper() == str(q["correct"]).upper()
        })

    correct_count = sum(1 for q in questions_summary if q["is_correct"])
    total = len(questions)
    score = (correct_count / total * 100) if total > 0 else 0

    prompt = f"""Analyze placement test results for a {language} learner.

Test summary:
- Total questions: {total}
- Correct answers: {correct_count}
- Score: {score:.1f}%
- Question breakdown: {questions_summary}

Based on these results, determine:
1. The appropriate CEFR level (A1, A2, B1, B2, C1, C2)
2. Strong areas (types of questions they answered well)
3. Weak areas (types of questions they struggled with)
4. Personalized recommendations

Return JSON:
{{
    "cefr_level": "B1",
    "score": 65.0,
    "strong_areas": ["vocabulary", "reading"],
    "weak_areas": ["grammar", "sentence_building"],
    "recommendations": "Focus on grammar structures and practice building complex sentences..."
}}"""

    try:
        return await generate_json(prompt)
    except Exception as e:
        logger.error(f"Error analyzing placement results: {e}")
        # Calculate basic level from score
        if score < 20:
            level = "A1"
        elif score < 35:
            level = "A2"
        elif score < 50:
            level = "B1"
        elif score < 65:
            level = "B2"
        elif score < 80:
            level = "C1"
        else:
            level = "C2"

        return {
            "cefr_level": level,
            "score": score,
            "strong_areas": ["general knowledge"],
            "weak_areas": ["needs assessment"],
            "recommendations": f"Based on your score of {score:.1f}%, you are at the {level} level. Continue practicing regularly."
        }


async def generate_study_plan(user_data: dict, language: str, native_language: str) -> dict:
    cefr_level = user_data.get("cefr_level", "A1")
    name = user_data.get("name", "Student")

    prompt = f"""Create a comprehensive 30-day language study plan for {name}, a {native_language} speaker learning {language} at CEFR level {cefr_level}.

The plan should:
- Build progressively from their current level ({cefr_level})
- Cover grammar, vocabulary, conversation, and culture
- Be realistic and engaging

Return JSON with this exact structure:
{{
    "language": "{language}",
    "cefr_level": "{cefr_level}",
    "daily_topics": [
        {{
            "day": 1,
            "grammar_topic": "Present tense conjugation",
            "vocabulary_theme": "Greetings and introductions",
            "conversation_topic": "Meeting someone new",
            "cultural_note": "Formal vs informal greetings in {language}-speaking countries"
        }}
    ],
    "weekly_goals": [
        {{
            "week": 1,
            "goal": "Master basic greetings and introduce yourself",
            "key_grammar": "Basic sentence structure",
            "vocabulary_count": 50
        }}
    ],
    "overall_goal": "Reach {cefr_level} proficiency and begin transitioning to the next level"
}}

Generate all 30 days and 4 weekly goals."""

    try:
        return await generate_json(prompt)
    except Exception as e:
        logger.error(f"Error generating study plan: {e}")
        # Return a basic fallback plan
        days = []
        grammar_topics = [
            "Basic sentence structure", "Present tense", "Articles and nouns",
            "Adjectives", "Numbers and counting", "Past tense", "Future tense",
            "Modal verbs", "Prepositions", "Questions and negation"
        ]
        vocab_themes = [
            "Greetings", "Family", "Colors and shapes", "Food and drinks",
            "Days and months", "Weather", "Travel", "Work and professions",
            "Health", "Hobbies"
        ]
        for day in range(1, 31):
            days.append({
                "day": day,
                "grammar_topic": grammar_topics[(day - 1) % len(grammar_topics)],
                "vocabulary_theme": vocab_themes[(day - 1) % len(vocab_themes)],
                "conversation_topic": f"Everyday conversation {day}",
                "cultural_note": f"Cultural aspect of {language}-speaking countries"
            })

        return {
            "language": language,
            "cefr_level": cefr_level,
            "daily_topics": days,
            "weekly_goals": [
                {"week": 1, "goal": "Basic communication", "key_grammar": "Present tense", "vocabulary_count": 50},
                {"week": 2, "goal": "Expand vocabulary", "key_grammar": "Past tense", "vocabulary_count": 100},
                {"week": 3, "goal": "Complex sentences", "key_grammar": "Modal verbs", "vocabulary_count": 150},
                {"week": 4, "goal": "Fluent conversations", "key_grammar": "Advanced structures", "vocabulary_count": 200}
            ],
            "overall_goal": f"Build foundation in {language}"
        }


async def generate_daily_lesson(
    day_number: int,
    study_plan_data: dict,
    user_errors: list,
    cefr_level: str,
    language: str,
    native_language: str,
    recent_topics: list = None
) -> dict:
    # Get today's topic from study plan
    daily_topics = study_plan_data.get("daily_topics", [])
    today_topic = {}
    for topic in daily_topics:
        if topic.get("day") == day_number:
            today_topic = topic
            break

    if not today_topic and daily_topics:
        today_topic = daily_topics[(day_number - 1) % len(daily_topics)]

    grammar_topic = today_topic.get("grammar_topic", "Basic grammar")
    vocab_theme = today_topic.get("vocabulary_theme", "Everyday vocabulary")
    conversation_topic = today_topic.get("conversation_topic", "Daily conversation")

    error_section = ""
    if user_errors:
        error_section = f"\nRecent errors to address: {user_errors[:3]}"

    interleaving_section = ""
    if recent_topics:
        interleaving_section = f"\nRecent topics from the last 7 days (for interleaved review): {recent_topics[:5]}"

    prompt = f"""Create a comprehensive language lesson for Day {day_number}.

Student profile:
- Learning: {language}
- Native language: {native_language}
- CEFR level: {cefr_level}
- Grammar topic: {grammar_topic}
- Vocabulary theme: {vocab_theme}
- Conversation topic: {conversation_topic}
{error_section}
{interleaving_section}

Generate a complete lesson with rich content. Return JSON:
{{
    "title": "Day {day_number}: {grammar_topic}",
    "topic": "{vocab_theme}",
    "explanation": "Detailed grammar explanation in English with {language} examples...",
    "vocabulary": [
        {{
            "word": "{language} word",
            "translation": "{native_language} translation",
            "example": "Example sentence in {language}"
        }}
    ],
    "dialogue": {{
        "context": "Scenario description",
        "lines": [
            {{
                "speaker": "A",
                "text": "{language} sentence",
                "translation": "{native_language} translation"
            }},
            {{
                "speaker": "B",
                "text": "{language} response",
                "translation": "{native_language} translation"
            }}
        ]
    }},
    "exercises": [
        {{
            "type": "fill_blank",
            "instruction": "Fill in the blank",
            "content": "Sentence with ___",
            "answer": "correct answer"
        }},
        {{
            "type": "multiple_choice",
            "instruction": "Choose the correct form",
            "content": "Question text",
            "options": ["A. option1", "B. option2", "C. option3", "D. option4"],
            "answer": "A"
        }},
        {{
            "type": "translation",
            "instruction": "Translate to {language}",
            "content": "Sentence in {native_language}",
            "answer": "Translation in {language}"
        }}
    ],
    "production_task": {{
        "instruction": "Write 3 sentences using today's vocabulary...",
        "example": "Example sentence"
    }},
    "error_review": [],
    "comprehensible_input": {{
        "text": "A 100-150 word passage in {language} at {cefr_level} level using 95% known words and 3-5 new words in context",
        "new_words": ["new_word_1", "new_word_2"],
        "comprehension_questions": [
            {{"question": "Question about the text in {native_language}", "answer": "Answer"}}
        ]
    }},
    "interleaved_review": [],
    "output_forcing": {{
        "instruction": "Read the following text, then hide it and reproduce it from memory",
        "text": "A short {language} paragraph (3-5 sentences) using today's grammar and vocabulary"
    }}
}}

Include at least 10 vocabulary words, a 6-line dialogue, and 5 exercises.
{f'Also add 2-3 interleaved review questions from recent topics: {recent_topics[:3]}. Format: [{{"topic": "...", "question": "...", "answer": "..."}}]' if recent_topics else 'Leave interleaved_review as empty array.'}
If there are errors to address, add them to the error_review array with format:
{{"error": "original mistake", "correction": "correct form", "explanation": "why it's wrong", "practice": "practice exercise"}}"""

    try:
        return await generate_json(prompt)
    except Exception as e:
        logger.error(f"Error generating daily lesson: {e}")
        return {
            "title": f"Day {day_number}: {grammar_topic}",
            "topic": vocab_theme,
            "explanation": f"Today we will study {grammar_topic} in {language}. This is an important foundation for your {cefr_level} level studies.",
            "vocabulary": [
                {"word": "Hallo", "translation": "Cześć", "example": "Hallo, wie geht es dir?"},
                {"word": "Danke", "translation": "Dziękuję", "example": "Danke schön!"},
                {"word": "Bitte", "translation": "Proszę", "example": "Bitte sehr."}
            ],
            "dialogue": {
                "context": "Two people meeting for the first time",
                "lines": [
                    {"speaker": "A", "text": "Hallo! Wie heißt du?", "translation": "Cześć! Jak masz na imię?"},
                    {"speaker": "B", "text": "Ich heiße Anna. Und du?", "translation": "Mam na imię Anna. A ty?"},
                    {"speaker": "A", "text": "Ich bin Max. Freut mich!", "translation": "Jestem Max. Miło mi!"}
                ]
            },
            "exercises": [
                {"type": "fill_blank", "instruction": "Fill in the blank", "content": "___ heiße Maria.", "answer": "Ich"},
                {"type": "multiple_choice", "instruction": "Choose the correct greeting",
                 "content": "How do you say 'Good morning' in German?",
                 "options": ["A. Gute Nacht", "B. Guten Morgen", "C. Auf Wiedersehen", "D. Danke"],
                 "answer": "B"},
                {"type": "translation", "instruction": "Translate to German",
                 "content": "My name is Anna.", "answer": "Ich heiße Anna."}
            ],
            "production_task": {
                "instruction": "Write 3 sentences introducing yourself in German",
                "example": "Ich heiße Max. Ich komme aus Polen. Ich lerne Deutsch."
            },
            "error_review": [],
            "comprehensible_input": {
                "text": "Hallo! Ich heiße Max. Ich komme aus Polen. Ich lerne Deutsch. Das ist schön. Ich mag Deutsch sehr.",
                "new_words": ["schön", "mag"],
                "comprehension_questions": [
                    {"question": "Skąd pochodzi Max?", "answer": "Z Polski"}
                ]
            },
            "interleaved_review": [],
            "output_forcing": {
                "instruction": "Read the text, then hide it and try to reproduce it from memory.",
                "text": "Hallo, ich heiße Max. Ich komme aus Polen und lerne Deutsch. Ich bin Student."
            }
        }


async def generate_daily_test(
    lesson_content: dict,
    cefr_level: str,
    language: str,
    native_language: str
) -> dict:
    vocab = lesson_content.get("vocabulary", [])[:5]
    topic = lesson_content.get("topic", "general")
    title = lesson_content.get("title", "Today's Lesson")

    prompt = f"""Create a 10-question test based on this {language} lesson.

Lesson: {title}
Topic: {topic}
CEFR Level: {cefr_level}
Vocabulary covered: {vocab}
Native language: {native_language}

Generate 10 questions testing:
- 3 vocabulary questions from the lesson
- 3 grammar questions based on lesson content
- 2 translation questions (from {native_language} to {language})
- 2 comprehension/application questions

Return JSON:
{{
    "questions": [
        {{
            "id": 1,
            "type": "vocabulary",
            "question": "Question text",
            "options": ["A. option", "B. option", "C. option", "D. option"],
            "correct": "A",
            "points": 10
        }}
    ]
}}

All questions should be answerable from the lesson content. Points should total 100."""

    try:
        return await generate_json(prompt)
    except Exception as e:
        logger.error(f"Error generating daily test: {e}")
        return {
            "questions": [
                {
                    "id": 1,
                    "type": "vocabulary",
                    "question": f"What is the {language} word for 'Hello'?",
                    "options": ["A. Auf Wiedersehen", "B. Danke", "C. Hallo", "D. Bitte"],
                    "correct": "C",
                    "points": 10
                }
            ]
        }


async def analyze_test_errors(
    questions: list,
    answers: dict,
    language: str,
    native_language: str
) -> dict:
    results = []
    total_points = 0
    earned_points = 0

    for q in questions:
        user_ans = answers.get(str(q["id"]), answers.get(q["id"], ""))
        is_correct = str(user_ans).upper().strip() == str(q["correct"]).upper().strip()
        points = q.get("points", 10)
        total_points += points
        if is_correct:
            earned_points += points

        results.append({
            "question_id": q["id"],
            "type": q.get("type", "unknown"),
            "question": q.get("question", ""),
            "user_answer": user_ans,
            "correct_answer": q["correct"],
            "is_correct": is_correct,
            "points": points
        })

    score = (earned_points / total_points * 100) if total_points > 0 else 0
    wrong_answers = [r for r in results if not r["is_correct"]]

    prompt = f"""Analyze these {language} test errors and provide detailed feedback.

Test results:
- Score: {score:.1f}%
- Wrong answers: {wrong_answers}
- Native language of student: {native_language}

For each error, provide:
- Error type (grammar, vocabulary, syntax, comprehension)
- Clear explanation of why the answer was wrong
- The grammar rule or vocabulary note
- A brief practice suggestion

Return JSON:
{{
    "score": {score:.1f},
    "errors": [
        {{
            "type": "grammar",
            "question": "original question",
            "user_answer": "what they wrote",
            "correct_answer": "correct answer",
            "explanation": "why it's wrong in simple terms",
            "rule": "the grammar/vocabulary rule to remember"
        }}
    ],
    "performance_summary": "Overall feedback message for the student"
}}"""

    try:
        result = await generate_json(prompt)
        result["score"] = score
        return result
    except Exception as e:
        logger.error(f"Error analyzing test errors: {e}")
        errors = []
        for r in wrong_answers:
            errors.append({
                "type": r["type"],
                "question": r["question"],
                "user_answer": r["user_answer"],
                "correct_answer": r["correct_answer"],
                "explanation": f"The correct answer is {r['correct_answer']}",
                "rule": "Review this topic in the lesson"
            })

        return {
            "score": score,
            "errors": errors,
            "performance_summary": f"You scored {score:.1f}%. Review the errors and practice more."
        }


async def generate_weekly_test(
    study_plan_data: dict,
    week_number: int,
    cefr_level: str,
    language: str,
    native_language: str
) -> dict:
    weekly_goals = study_plan_data.get("weekly_goals", [])
    week_goal = {}
    for goal in weekly_goals:
        if goal.get("week") == week_number:
            week_goal = goal
            break

    if not week_goal and weekly_goals:
        week_goal = weekly_goals[(week_number - 1) % len(weekly_goals)]

    daily_topics = study_plan_data.get("daily_topics", [])
    week_topics = [t for t in daily_topics if (week_number - 1) * 7 < t.get("day", 0) <= week_number * 7]

    prompt = f"""Create a comprehensive 25-question weekly review test for Week {week_number} of {language} learning.

Student level: CEFR {cefr_level}
Native language: {native_language}
Week goal: {week_goal.get("goal", "General review")}
Topics covered this week: {week_topics}
Key grammar: {week_goal.get("key_grammar", "Various")}

Create 25 varied questions covering all topics from the week.
Include: 8 vocabulary, 7 grammar, 5 translation, 5 reading comprehension questions.

Return JSON:
{{
    "questions": [
        {{
            "id": 1,
            "type": "vocabulary|grammar|translation|comprehension",
            "question": "Question text",
            "options": ["A. option", "B. option", "C. option", "D. option"],
            "correct": "A",
            "points": 4
        }}
    ]
}}

Points should total 100."""

    try:
        return await generate_json(prompt)
    except Exception as e:
        logger.error(f"Error generating weekly test: {e}")
        return await generate_daily_test({}, cefr_level, language, native_language)


async def generate_conversation_scenario(
    topic: str,
    cefr_level: str,
    user_errors: list,
    language: str,
    native_language: str
) -> dict:
    error_context = ""
    if user_errors:
        error_context = f"Help the student practice areas where they made errors: {user_errors[:3]}"

    prompt = f"""Create a conversation practice scenario for a {language} learner.

Student profile:
- CEFR level: {cefr_level}
- Native language: {native_language}
- Topic to practice: {topic}
{error_context}

Design an engaging, realistic conversation scenario appropriate for level {cefr_level}.

Return JSON:
{{
    "scenario": "Brief description of the situation",
    "ai_role": "Your role in this conversation (e.g., 'a shopkeeper in Berlin')",
    "user_role": "The student's role (e.g., 'a tourist buying souvenirs')",
    "suggested_phrases": [
        "Useful phrase 1 in {language}",
        "Useful phrase 2 in {language}",
        "Useful phrase 3 in {language}",
        "Useful phrase 4 in {language}",
        "Useful phrase 5 in {language}"
    ],
    "system_prompt": "You are playing the role of [AI role] in a {language} conversation practice. The student is at CEFR {cefr_level} level. Always respond in {language}. If the student makes an error, gently incorporate the correct form naturally in your response. Keep sentences appropriate for {cefr_level} level. Be encouraging and patient. If asked for help, provide it in {native_language}.",
    "opening_line": "The first line you'll say to start the conversation in {language}"
}}"""

    try:
        return await generate_json(prompt)
    except Exception as e:
        logger.error(f"Error generating conversation scenario: {e}")
        return {
            "scenario": f"You are at a {language}-speaking café ordering food and drinks.",
            "ai_role": "A friendly café waiter/waitress",
            "user_role": "A customer visiting for the first time",
            "suggested_phrases": [
                "Ich möchte... (I would like...)",
                "Was empfehlen Sie? (What do you recommend?)",
                "Die Rechnung, bitte. (The bill, please.)",
                "Danke schön! (Thank you very much!)",
                "Entschuldigung... (Excuse me...)"
            ],
            "system_prompt": f"You are a friendly café waiter in a German café. The student is at CEFR {cefr_level} level. Respond only in German. Be patient and encouraging.",
            "opening_line": "Guten Tag! Was darf ich Ihnen bringen?"
        }


async def analyze_conversation(
    conversation_history: list,
    cefr_level: str,
    language: str,
    native_language: str
) -> dict:
    prompt = f"""Analyze this {language} conversation practice session.

CEFR level: {cefr_level}
Native language: {native_language}

Conversation:
{conversation_history}

Evaluate:
1. Grammar accuracy
2. Vocabulary range and appropriateness
3. Fluency and naturalness
4. Achievement of communication goals
5. Areas for improvement

Return JSON:
{{
    "summary": "Overall assessment of the conversation",
    "errors": [
        {{
            "type": "grammar|vocabulary|syntax|fluency",
            "original": "what the student wrote",
            "correction": "correct form",
            "explanation": "why it should be changed"
        }}
    ],
    "vocabulary_used": [
        {{
            "word": "word used",
            "correct_usage": true,
            "note": "any relevant note"
        }}
    ],
    "recommendations": [
        "Specific improvement recommendation 1",
        "Specific improvement recommendation 2",
        "Specific improvement recommendation 3"
    ],
    "score": 75,
    "strengths": ["What the student did well"]
}}"""

    try:
        return await generate_json(prompt)
    except Exception as e:
        logger.error(f"Error analyzing conversation: {e}")
        return {
            "summary": "Conversation analysis complete. Good effort in practicing!",
            "errors": [],
            "vocabulary_used": [],
            "recommendations": [
                "Continue practicing daily conversations",
                "Focus on grammar accuracy",
                "Expand vocabulary in this topic area"
            ],
            "score": 70,
            "strengths": ["Attempted communication", "Used target language"]
        }


async def answer_language_question(
    question: str,
    cefr_level: str,
    language: str,
    native_language: str
) -> str:
    prompt = f"""You are an expert {language} language tutor. A student (CEFR level {cefr_level}, native {native_language} speaker) asks:

"{question}"

Provide a clear, helpful explanation appropriate for their level.
Use examples in {language} with {native_language} translations.
Keep the explanation concise but thorough."""

    try:
        return await generate_text(prompt)
    except Exception as e:
        logger.error(f"Error answering language question: {e}")
        return f"I apologize, but I couldn't generate an answer right now. Please try again later."


async def generate_daily_tips(
    cefr_level: str,
    language: str,
    native_language: str
) -> dict:
    prompt = f"""Generate 4 helpful daily language learning tips for a {native_language} speaker learning {language} at CEFR level {cefr_level}.

Tips should cover different aspects: grammar, vocabulary, culture, and memory techniques.

Return JSON:
{{
    "tips": [
        {{
            "title": "Tip title",
            "content": "Detailed tip content with examples",
            "type": "grammar|vocabulary|culture|memory_tip"
        }}
    ]
}}

Make tips practical, specific, and actionable. Include {language} examples where relevant."""

    try:
        return await generate_json(prompt)
    except Exception as e:
        logger.error(f"Error generating daily tips: {e}")
        return {
            "tips": [
                {
                    "title": "Practice Every Day",
                    "content": f"Consistency is key in learning {language}. Even 15 minutes daily is better than 2 hours once a week.",
                    "type": "memory_tip"
                },
                {
                    "title": "Learn in Context",
                    "content": f"Don't just memorize word lists. Learn {language} words in sentences to remember them better.",
                    "type": "vocabulary"
                },
                {
                    "title": "Listen to Native Speakers",
                    "content": f"Watch {language} movies or listen to {language} music to improve your ear for the language.",
                    "type": "culture"
                },
                {
                    "title": "Grammar Building Blocks",
                    "content": f"Master the basic sentence structure of {language} before moving to complex forms.",
                    "type": "grammar"
                }
            ]
        }
