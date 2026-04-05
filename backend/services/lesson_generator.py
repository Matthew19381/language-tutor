import logging
from backend.services.gemini_service import generate_json, generate_text, with_model

logger = logging.getLogger(__name__)


@with_model("placement")
async def generate_placement_test(language: str, native_language: str) -> dict:
    prompt = f"""You are a strict certified {language} language examiner. Create a 30-question DIAGNOSTIC placement test for a native {native_language} speaker learning {language}.

GOAL: Correctly distinguish between A1, A2, B1, B2, C1, C2 speakers. Most native {native_language} speakers with NO prior {language} knowledge should score at A1 level, NOT B1.

CRITICAL RULES:
1. Questions must test KNOWLEDGE that requires actual study — not guessable by logic or similarity to {native_language}
2. Do NOT use cognates or internationally recognizable words in correct answers
3. Grammar questions must require knowledge of specific {language} grammatical rules
4. A1 questions should be failed by someone with zero knowledge
5. B1 questions should require at least 6+ months of study to answer
6. fill_blank questions MUST have EXACTLY ONE blank (___) in the sentence. Never two or more gaps.
7. translation questions: do NOT include both the {native_language} phrase AND its {language} translation in the same question — the answer must NOT be visible in the question text
8. Do NOT give away the answer in the question text. The question must not contain the correct answer or any translation that makes the correct option obvious.

QUESTION DISTRIBUTION (30 questions — do NOT deviate):
- Q1-5: A1 — basic verb conjugation in present tense, gender of common nouns, basic word order SVO
- Q6-10: A2 — accusative/dative case endings for articles, separable verbs, common irregular verbs in past tense (Perfekt)
- Q11-17: B1 — Konjunktiv II (würde/wäre), subordinate clause word order (WEIL/DASS/OB), two-way prepositions (Wechselpräpositionen Dativ vs Akkusativ), Genitiv case
- Q18-23: B2 — Passiv constructions (werden+Partizip II), indirect speech (Konjunktiv I), relative clauses with correct case, nominalized verbs
- Q24-27: C1 — extended adjective phrases, stylistic register differences, advanced modal particle usage (DOCH/JA/HALT/SCHON with nuanced meanings)
- Q28-30: C2 — subtle grammatical errors in formal text, pragmatic implicature, advanced stylistic choices

QUESTION TYPES (must vary — use all types):
- fill_blank: A {language} sentence with a blank. Options are {language} word FORMS (e.g. "dem/den/des/der")
- correct_sentence: Show 4 {language} sentences, only one is grammatically correct
- word_order: Scrambled {language} words — pick the correctly ordered sentence
- translation: A {native_language} phrase — pick the correct {language} translation from options
- comprehension: A 3-4 sentence {language} text (no translation given), then a question in {native_language}

MANDATORY LANGUAGE RULE:
- {language} content (sentences, options for grammar questions) MUST stay in {language}
- ONLY question framing ("Uzupełnij zdanie:", "Które zdanie jest poprawne?") is in {native_language}
- Answer options for comprehension questions may be in {native_language}

GOOD EXAMPLE (fill_blank for A2 Akkusativ):
{{"question": "Uzupełnij zdanie (biernik): Ich sehe ___ Mann auf der Straße.", "options": ["A. der", "B. den", "C. dem", "D. ein"], "correct": "B", "points": 1, "cefr_hint": "A2"}}

GOOD EXAMPLE (word_order for B1):
{{"question": "Ułóż słowa w poprawnej kolejności (zdanie podrzędne): weil / ich / müde / bin / heute", "options": ["A. weil ich heute müde bin", "B. weil bin ich heute müde", "C. weil ich bin heute müde", "D. weil heute ich müde bin"], "correct": "A", "points": 2, "cefr_hint": "B1"}}

GOOD EXAMPLE (correct_sentence for B2 Passiv):
{{"question": "Które zdanie jest gramatycznie poprawne (strona bierna)?", "options": ["A. Das Buch wurde von ihm gelesen.", "B. Das Buch ist von ihm gelesen worden.", "C. Das Buch wird von ihm gelesen gewesen.", "D. Das Buch hat von ihm gelesen werden."], "correct": "A", "points": 3, "cefr_hint": "B2"}}

Return ONLY valid JSON:
{{
    "questions": [
        {{
            "id": 1,
            "type": "fill_blank",
            "question": "Question framing in {native_language} with {language} sentence",
            "options": ["A. option", "B. option", "C. option", "D. option"],
            "correct": "B",
            "points": 1,
            "cefr_hint": "A1"
        }}
    ]
}}"""

    try:
        result = await generate_json(prompt)
        if isinstance(result, list):
            result = {"questions": result}
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


@with_model("placement")
async def analyze_placement_results(questions: list, answers: dict, language: str, native_language: str = "Polish") -> dict:
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

    prompt = f"""Analyze placement test results for a {native_language} speaker learning {language}.

Test summary:
- Total questions: {total}
- Correct answers: {correct_count}
- Score: {score:.1f}%
- Question breakdown (with CEFR hints): {questions_summary}

CEFR LEVEL DETERMINATION RULES — BE STRICT AND CONSERVATIVE:
- Assign A1 if student gets fewer than 50% of A2 questions correct
- Assign A2 if student masters A1 but fails more than 50% of B1 questions
- Assign B1 if student masters A1+A2 but fails more than 40% of B2 questions
- Assign B2 if student masters up to B1 with less than 30% of C1 wrong
- Assign C1 only if student clearly demonstrates advanced competence
- Assign C2 only for near-perfect scores on advanced questions

IMPORTANT: A student who gets 30-50% overall is almost always A2, NOT B1. Do not over-estimate.
Most native {native_language} speakers with minimal {language} exposure score A1-A2.

Write ALL text fields (strong_areas, weak_areas, recommendations) in {native_language}.

Return JSON:
{{
    "cefr_level": "A2",
    "score": {score:.1f},
    "strong_areas": ["obszary mocne w {native_language}"],
    "weak_areas": ["obszary słabe w {native_language}"],
    "recommendations": "Rekomendacje w {native_language}..."
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


@with_model("lesson")
async def generate_study_plan(user_data: dict, language: str, native_language: str) -> dict:
    cefr_level = user_data.get("cefr_level", "A1")
    name = user_data.get("name", "Student")

    prompt = f"""Create a comprehensive 30-day language study plan for {name}, a {native_language} speaker learning {language} at CEFR level {cefr_level}.

Write all text fields (grammar_topic, vocabulary_theme, conversation_topic, cultural_note, goal, key_grammar, overall_goal) in {native_language}.


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


@with_model("lesson")
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
    "title": "Dzień {day_number}: {grammar_topic}",
    "topic": "{vocab_theme}",
    "explanation": "Detailed grammar explanation in {native_language} with {language} examples...",
    "vocabulary": [
        {{
            "word": "{language} word",
            "translation": "{native_language} translation",
            "example": "Example sentence in {language}",
            "example_translation": "Translation of example in {native_language}"
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
        "instruction": "Write 2-3 sentences in {language} using today's vocabulary and grammar. AI will evaluate your answer. Keep it simple and focused on today's topic.",
        "example": "Example answer in {language}"
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
        "instruction": "Przeczytaj poniższy tekst, zakryj go i spróbuj odtworzyć go z pamięci. Zacznij od przeczytania całości, potem chowaj słowo po słowie.",
        "text": "EXACTLY 1-2 SHORT sentences in {language} (max 20 words total) using today's grammar. Keep it extremely short and memorable.",
        "translation": "Polish translation of the text above"
    }}
}}

Include at least 10 vocabulary words, a 6-line dialogue, and 5 exercises.
{f'Also add 2-3 interleaved review questions from recent topics: {recent_topics[:3]}. Format: [{{"topic": "...", "question": "...", "answer": "..."}}]' if recent_topics else 'Leave interleaved_review as empty array.'}
If there are errors to address, add them to the error_review array with format:
{{"error": "original mistake", "correction": "correct form", "explanation": "why it's wrong (write explanation in {native_language})", "practice": "practice exercise in {language}"}}"""

    try:
        return await generate_json(prompt)
    except Exception as e:
        logger.error(f"Error generating daily lesson: {e}")
        return {
            "title": f"Dzień {day_number}: {grammar_topic}",
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


@with_model("lesson")
async def generate_daily_test(
    lesson_content: dict,
    cefr_level: str,
    language: str,
    native_language: str
) -> dict:
    vocab = lesson_content.get("vocabulary", [])
    topic = lesson_content.get("topic", "general")
    title = lesson_content.get("title", "Today's Lesson")
    grammar = lesson_content.get("explanation", "")[:600]
    dialogue = lesson_content.get("dialogue", {})
    dialogue_lines = dialogue.get("lines", [])[:4] if isinstance(dialogue, dict) else []
    dialogue_sample = "  ".join(f"{l.get('speaker','')}: {l.get('text','')}" for l in dialogue_lines)

    vocab_words = [f"{v.get('word','')} = {v.get('translation','')}" for v in vocab[:12]]

    prompt = f"""You are a strict {language} language examiner. Create a CHALLENGING 15-question test based on today's lesson.

Lesson: {title}
Topic: {topic}
CEFR Level: {cefr_level}
Native language (student): {native_language}

LESSON VOCABULARY (ALL must be tested):
{chr(10).join(vocab_words)}

GRAMMAR TOPIC:
{grammar}

DIALOGUE EXCERPT:
{dialogue_sample}

REQUIREMENTS — create EXACTLY:
- 4 vocabulary questions: fill-in-the-blank sentences requiring the exact word from the lesson (NO multiple choice)
- 3 grammar questions: multiple choice, test the specific grammar rule from the lesson (include plausible wrong answers)
- 3 translation questions: {native_language}→{language}, student must write the full sentence (no options)
- 2 dialogue questions: multiple choice based on the dialogue context
- 2 application questions: student writes a sentence using a grammar rule or vocabulary word from the lesson (no options)
- 1 bonus error-correction question: give a sentence with 1 error, student writes the corrected version

DIFFICULTY: High. Wrong options must be plausible. Fill-blank and translation questions have no options (student types).
CRITICAL: The answer must NEVER appear literally in the question text.
CRITICAL: For fill_blank type, use ___ (three underscores) exactly ONCE per question. Never two blanks.
CRITICAL: For multiple_choice type, the question stem must be a complete sentence or clear question — NOT a sentence with blanks. Put the blank only if absolutely needed, and then ONLY ONE blank. The options must be single words or short forms (e.g. "A. hat" not "A. hat...geschehen").
CRITICAL: For fill_blank type, add a "hint" field with a short {native_language} hint for the missing word (e.g. the translation or grammar hint like "czas przeszły 'sein'").

Return ONLY valid JSON:
{{
    "questions": [
        {{
            "id": 1,
            "type": "fill_blank",
            "question": "Sentence with ___ to fill in.",
            "hint": "Short {native_language} hint for the missing word",
            "correct": "exact word",
            "points": 7
        }},
        {{
            "id": 2,
            "type": "multiple_choice",
            "question": "Question?",
            "options": ["A. option1", "B. option2", "C. option3", "D. option4"],
            "correct": "A",
            "points": 6
        }}
    ]
}}

Points should total 100. Types: fill_blank, multiple_choice, translation, application, error_correction."""

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

        # Resolve letter (A/B/C/D) to full option text for MC questions
        opts = q.get("options", [])
        opts_map = {}
        for opt in opts:
            letter = opt.split(".")[0].strip()
            opts_map[letter.upper()] = opt
        user_ans_display = opts_map.get(str(user_ans).upper(), user_ans)
        correct_ans_display = opts_map.get(str(q["correct"]).upper(), q["correct"])

        results.append({
            "question_id": q["id"],
            "type": q.get("type", "unknown"),
            "question": q.get("question", ""),
            "user_answer": user_ans_display,
            "correct_answer": correct_ans_display,
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

For each error, classify the type using one of these specific categories:
- "grammar" — general grammar mistake
- "verb_conjugation" — wrong verb form or tense
- "word_order" — incorrect sentence structure
- "articles" — wrong or missing article (der/die/das, a/an/the)
- "prepositions" — wrong preposition used
- "vocabulary" — wrong word choice or unknown word
- "spelling" — spelling or punctuation error
- "comprehension" — misunderstood the question meaning
- "pronunciation" — phonetic confusion (e.g. similar-sounding words)
- "case" — wrong grammatical case (Nominativ/Akkusativ/Dativ/Genitiv)

IMPORTANT: Write "explanation" and "practice" fields in {native_language}. Keep "question", "user_answer", "correct_answer" in the original language.

Return JSON:
{{
    "score": {score:.1f},
    "errors": [
        {{
            "type": "verb_conjugation",
            "question": "original question text",
            "user_answer": "what the student answered",
            "correct_answer": "the correct answer",
            "explanation": "clear explanation in {native_language} of why it was wrong and what rule applies",
            "practice": "a short practice sentence in {language} the student should try to translate"
        }}
    ],
    "performance_summary": "Overall encouraging feedback message in {native_language}"
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
                "type": r["type"] if r["type"] != "unknown" else "grammar",
                "question": r["question"],
                "user_answer": r["user_answer"],
                "correct_answer": r["correct_answer"],
                "explanation": f"Poprawna odpowiedź to: {r['correct_answer']}",
                "practice": f"Przypomnij sobie tę regułę i spróbuj ponownie."
            })

        return {
            "score": score,
            "errors": errors,
            "performance_summary": f"Zdobyłeś {score:.1f}%. Przejrzyj błędy i poćwicz te zagadnienia."
        }


@with_model("lesson")
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


async def generate_errors_test(
    errors: list,
    cefr_level: str,
    language: str,
    native_language: str
) -> dict:
    """Generate a test targeting the user's specific error patterns."""
    # Build error context: up to 15 most recent errors
    error_lines = []
    for e in errors[:15]:
        q = e.get("question", "")
        ua = e.get("user_answer", "")
        ca = e.get("correct_answer", "")
        t = e.get("type", "")
        if ca:
            error_lines.append(f"- [{t}] {q} | Uczeń napisał: '{ua}' | Poprawnie: '{ca}'")

    errors_str = "\n".join(error_lines) if error_lines else "Brak szczegółów błędów."

    prompt = f"""Create a 10-question remediation test in {language} targeting these specific errors:

{errors_str}

CEFR Level: {cefr_level}
Native language: {native_language}

Make each question directly target one of the error patterns above. Focus on:
- Correct forms of words the student got wrong
- Similar constructions to what was answered incorrectly
- Fill-in-the-blank with the correct forms

Rules:
- Each fill_blank question has EXACTLY ONE ___ blank
- Do NOT include the answer in the question text
- Options A/B/C/D for multiple choice questions

Return JSON with MIXED question types — fill_blank has NO options, multiple_choice HAS options:
{{
    "questions": [
        {{
            "id": 1,
            "type": "fill_blank",
            "question": "Sentence with ___ to fill.",
            "correct": "exact word",
            "points": 10
        }},
        {{
            "id": 2,
            "type": "multiple_choice",
            "question": "Choose the correct form:",
            "options": ["A. option1", "B. option2", "C. option3", "D. option4"],
            "correct": "B",
            "points": 10
        }}
    ]
}}

Use at least 5 fill_blank and at most 5 multiple_choice questions. Points total 100."""

    try:
        return await generate_json(prompt)
    except Exception as e:
        logger.error(f"Error generating errors test: {e}")
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


@with_model("conversation")
async def analyze_conversation(
    conversation_history: list,
    cefr_level: str,
    language: str,
    native_language: str
) -> dict:
    prompt = f"""Analyze this {language} conversation practice session for a {native_language} speaker at CEFR {cefr_level}.

Conversation:
{conversation_history}

Produce a DETAILED analysis with SPECIFIC error categories. Use these category types:
- "grammar" — grammatical rule violations (wrong case, wrong tense, wrong conjugation)
- "vocabulary" — wrong word choice, false friends, missing vocabulary
- "word_order" — incorrect sentence structure / word placement
- "articles" — wrong article (der/die/das/ein/eine), gender errors
- "verb_conjugation" — wrong verb form, wrong auxiliary verb
- "prepositions" — wrong preposition usage
- "pronunciation_spelling" — spelling errors that suggest pronunciation issues
- "fluency" — overly simple/broken sentences for the level
- "register" — too formal/informal for the context

Severity rules:
- "critical" — errors that impede comprehension or break fundamental grammar rules (wrong verb form, wrong case, missing key word)
- "minor" — stylistic issues, slight awkwardness, or non-essential improvement suggestions

Return JSON:
{{
    "summary": "2-3 sentence overall assessment in {native_language}",
    "errors": [
        {{
            "type": "grammar|vocabulary|word_order|articles|verb_conjugation|prepositions|pronunciation_spelling|fluency|register",
            "severity": "critical|minor",
            "question": "the problematic phrase the student wrote",
            "correct_answer": "the corrected form",
            "explanation": "brief explanation in {native_language} why it's wrong and what rule applies"
        }}
    ],
    "category_advice": {{
        "grammar": "Specific advice on what grammar topics to study",
        "vocabulary": "Specific vocabulary areas to improve",
        "word_order": "Word order rules to practice"
    }},
    "recommendations": ["Specific actionable recommendation 1", "Specific recommendation 2", "Specific recommendation 3"],
    "score": 75,
    "strengths": ["What the student did well 1", "What the student did well 2"]
}}

Note: category_advice should only include categories where errors were found."""

    try:
        return await generate_json(prompt)
    except Exception as e:
        logger.error(f"Error analyzing conversation: {e}")
        return {
            "summary": "Conversation analysis complete. Good effort in practicing!",
            "errors": [],
            "category_advice": {},
            "recommendations": [
                "Continue practicing daily conversations",
                "Focus on grammar accuracy",
                "Expand vocabulary in this topic area"
            ],
            "score": 70,
            "strengths": ["Attempted communication", "Used target language"]
        }


async def analyze_pasted_conversation(
    pasted_text: str,
    cefr_level: str,
    language: str,
    native_language: str
) -> dict:
    prompt = f"""A {native_language} speaker learning {language} at CEFR {cefr_level} pasted this conversation/text for analysis.
Analyze their {language} usage for errors and provide detailed feedback.

Text to analyze:
{pasted_text}

Instructions:
- Only analyze the LEARNER's lines (not the AI/tutor responses)
- If it's unclear who wrote what, analyze all {language} text
- Be specific about error types

Use these error category types:
- "grammar", "vocabulary", "word_order", "articles", "verb_conjugation", "prepositions", "pronunciation_spelling", "fluency", "register"

Return JSON:
{{
    "summary": "2-3 sentence overall assessment in {native_language}",
    "errors": [
        {{
            "type": "grammar|vocabulary|word_order|articles|verb_conjugation|prepositions|pronunciation_spelling|fluency|register",
            "question": "the problematic phrase",
            "correct_answer": "the corrected form",
            "explanation": "brief explanation in {native_language}"
        }}
    ],
    "category_advice": {{
        "grammar": "what grammar to study"
    }},
    "recommendations": ["recommendation 1", "recommendation 2"],
    "score": 70,
    "strengths": ["strength 1"]
}}"""

    try:
        return await generate_json(prompt)
    except Exception as e:
        logger.error(f"Error analyzing pasted conversation: {e}")
        return {
            "summary": "Analiza zakończona.",
            "errors": [],
            "category_advice": {},
            "recommendations": ["Ćwicz codziennie konwersacje"],
            "score": 0,
            "strengths": []
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

CRITICAL: You MUST write the "title" and "content" fields ENTIRELY in {native_language}. Do NOT use English in these fields. The "source" field can be in English.

Tips should cover different aspects: grammar, vocabulary, culture, and memory techniques.
Each tip must cite a real scientific source (researcher name, year, study/theory name).

Return JSON:
{{
    "tips": [
        {{
            "title": "Tytuł wskazówki po {native_language}",
            "content": "Szczegółowa treść wskazówki w języku {native_language} z przykładami w języku {language}",
            "type": "grammar|vocabulary|culture|memory_tip",
            "source": "Krashen (1982) - Input Hypothesis"
        }}
    ]
}}

Make tips practical, specific, and actionable. Include {language} examples where relevant.
Use real citations: e.g. Ebbinghaus (1885), Krashen (1982), Nation (2001), Baddeley (1986), Swain (1985)."""

    try:
        return await generate_json(prompt)
    except Exception as e:
        logger.error(f"Error generating daily tips: {e}")
        return {
            "tips": [
                {
                    "title": "Ćwicz codziennie",
                    "content": f"Systematyczność to klucz do nauki {language}. Nawet 15 minut dziennie jest lepsze niż 2 godziny raz w tygodniu.",
                    "type": "memory_tip",
                    "source": "Ebbinghaus (1885) - Spacing Effect"
                },
                {
                    "title": "Ucz się w kontekście",
                    "content": f"Nie zapamiętuj pojedynczych słów — ucz się słów {language} w zdaniach, by lepiej je zapamiętać.",
                    "type": "vocabulary",
                    "source": "Nation (2001) - Learning Vocabulary in Another Language"
                },
                {
                    "title": "Słuchaj native speakerów",
                    "content": f"Oglądaj filmy lub słuchaj muzyki po {language}, by przyzwyczaić ucho do języka.",
                    "type": "culture",
                    "source": "Krashen (1982) - Input Hypothesis"
                },
                {
                    "title": "Podstawy gramatyczne",
                    "content": f"Opanuj podstawową budowę zdań w {language} zanim przejdziesz do bardziej złożonych form.",
                    "type": "grammar",
                    "source": "Baddeley (1986) - Working Memory Model"
                }
            ]
        }
