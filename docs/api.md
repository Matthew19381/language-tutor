# Dokumentacja API LinguaAI

Wszyskie endpointy API są dostępne pod prefiksem `/api/`. Frontend komunikuje się z backendem przez proxy Vite na porcie 5173, które przekierowuje żądania `/api` i `/audio` do backendu na porcie 8000.

## Spis Treści
1. [Placement API](#placement-api)
2. [Lessons API](#lessons-api)
3. [Tests API](#tests-api)
4. [Flashcards API](#flashcards-api)
5. [Conversation API](#conversation-api)
6. [Stats API](#stats-api)
7. [QuickMode API](#quickmode-api)
8. [News API](#news-api)
9. [Pronunciation API](#pronunciation-api)
10. [Settings API](#settings-api)
11. [Audio API](#audio-api)
12. [YouTube API](#youtube-api)
13. [Voice Chat API](#voice-chat-api)

---

## Placement API

**Prefix**: `/api/placement/`

### POST `/api/placement/create`
Tworzenie nowego użytkownika.

**Request Body:**
```json
{
  "username": "jan_kowalski",
  "email": "jan@example.com",
  "native_language": "pl"
}
```

**Response (200):**
```json
{
  "user_id": 1,
  "username": "jan_kowalski",
  "xp": 0,
  "level": 1
}
```

### GET `/api/placement/test`
Pobieranie 20-pytań testu poziomującego CEFR.

**Response (200):**
```json
{
  "questions": [
    {
      "id": 1,
      "question": "Wybierz poprawną formę...",
      "options": ["opcja A", "opcja B", "opcja C", "opcja D"],
      "correct_answer": "opcja A",
      "cefr_level": "A1"
    }
  ],
  "total_questions": 20
}
```

### POST `/api/placement/submit`
Przesyłanie wyników testu poziomującego.

**Request Body:**
```json
{
  "user_id": 1,
  "answers": [0, 2, 1, 3, ...],
  "time_taken_seconds": 900
}
```

**Response (200):**
```json
{
  "cefr_level": "B1",
  "score": 14,
  "total": 20,
  "study_plan_id": 1
}
```

### POST `/api/placement/generate-plan`
Generowanie planu nauki dla użytkownika.

**Request Body:**
```json
{
  "user_id": 1,
  "cefr_level": "B1",
  "interests": ["business", "travel"]
}
```

**Response (200):**
```json
{
  "plan_id": 1,
  "topics": ["Present Tenses", "Business Vocabulary", "Travel Phrases"],
  "duration_weeks": 12,
  "daily_lesson_duration_minutes": 30
}
```

---

## Lessons API

**Prefix**: `/api/lessons/`

### GET `/api/lessons/today`
Pobieranie lekcji na dzisiaj dla użytkownika.

**Query Parameters:**
- `user_id` (required): ID użytkownika

**Response (200):**
```json
{
  "lesson_id": 42,
  "date": "2026-05-08",
  "content": {
    "title": "Present Perfect - Doświadczenia",
    "cefr_level": "B1",
    "vocabulary": [
      {"word": "experience", "translation": "doświadczenie", "example": "I have experience in..."}
    ],
    "grammar": {"topic": "Present Perfect", "explanation": "..."},
    "comprehensible_input": {
      "text": "i+1 text here...",
      "highlighted_words": ["word1", "word2"]
    },
    "interleaved_review": [
      {"question": "Previous topic review...", "answer": "..."}
    ],
    "output_forcing": {
      "prompt": "Describe your last holiday",
      "hint": "Use Present Perfect"
    }
  },
  "completed": false
}
```

### POST `/api/lessons/create`
Tworzenie nowej lekcji na dzisiaj.

**Request Body:**
```json
{
  "user_id": 1,
  "topic": "Present Perfect",
  "recent_topics": ["Past Simple", "Used to"]
}
```

**Response (201):**
```json
{
  "lesson_id": 42,
  "message": "Lesson created successfully"
}
```

### POST `/api/lessons/{lesson_id}/complete`
Oznaczanie lekcji jako ukończonej (+25 XP).

**Path Parameters:**
- `lesson_id` (required): ID lekcji

**Request Body:**
```json
{
  "user_id": 1
}
```

**Response (200):**
```json
{
  "message": "Lesson completed",
  "xp_earned": 25,
  "total_xp": 125,
  "new_achievements": [
    {"id": 3, "name": "Fast Learner", "description": "Complete 10 lessons"}
  ]
}
```

### GET `/api/lessons/{lesson_id}/export-pdf`
Eksport lekcji do formatu PDF.

**Path Parameters:**
- `lesson_id` (required): ID lekcji

**Response:** Plik binarny PDF (Content-Type: application/pdf)

### GET `/api/lessons/history`
Historia lekcji użytkownika.

**Query Parameters:**
- `user_id` (required): ID użytkownika
- `limit` (optional, default=30): Liczba lekcji
- `offset` (optional, default=0): Przesunięcie

**Response (200):**
```json
{
  "lessons": [
    {
      "lesson_id": 42,
      "date": "2026-05-08",
      "title": "Present Perfect",
      "completed": true,
      "xp_earned": 25
    }
  ],
  "total": 15
}
```

### GET `/api/lessons/{lesson_id}/audio`
Generowanie pliku audio dla lekcji.

**Path Parameters:**
- `lesson_id` (required): ID lekcji

**Query Parameters:**
- `section` (optional): Sekcja lekcji (vocabulary, grammar, etc.)
- `voice` (optional, default="en-US-JennyNeural"): Głos

**Response:** Plik binarny audio (Content-Type: audio/mpeg)

---

## Tests API

**Prefix**: `/api/tests/`

### GET `/api/tests/daily`
Pobieranie testu dziennego.

**Query Parameters:**
- `user_id` (required): ID użytkownika
- `lesson_id` (optional): ID lekcji (test powiązany)

**Response (200):**
```json
{
  "test_id": 15,
  "type": "daily",
  "questions": [
    {
      "id": 101,
      "question": "Complete the sentence...",
      "options": ["have been", "has been", "had been"],
      "correct_answer": 0
    }
  ],
  "total_questions": 10
}
```

### POST `/api/tests/daily/submit`
Przesyłanie odpowiedzi testu dziennego.

**Request Body:**
```json
{
  "user_id": 1,
  "test_id": 15,
  "answers": [0, 2, 1, 0, ...],
  "time_taken_seconds": 300
}
```

**Response (200):**
```json
{
  "score": 8,
  "total": 10,
  "xp_earned": 4.0,
  "percentage": 80,
  "new_achievements": []
}
```

### GET `/api/tests/weekly`
Pobieranie testu tygodniowego.

**Query Parameters:**
- `user_id` (required): ID użytkownika

**Response (200):** (struktura podobna do daily)

### POST `/api/tests/weekly/submit`
Przesyłanie odpowiedzi testu tygodniowego.

**Request Body:** (podobnie jak daily/submit)

**Response (200):** (podobnie jak daily/submit)

### GET `/api/tests/history`
Historia testów użytkownika.

**Query Parameters:**
- `user_id` (required): ID użytkownika
- `type` (optional): "daily" lub "weekly"
- `limit` (optional, default=20)

**Response (200):**
```json
{
  "tests": [
    {
      "test_id": 15,
      "type": "daily",
      "score": 8,
      "total": 10,
      "xp_earned": 4.0,
      "date": "2026-05-08"
    }
  ]
}
```

---

## Flashcards API

**Prefix**: `/api/flashcards/`

### GET `/api/flashcards/due`
Pobieranie fiszek do powtórki (spaced repetition).

**Query Parameters:**
- `user_id` (required): ID użytkownika
- `limit` (optional, default=20)

**Response (200):**
```json
{
  "flashcards": [
    {
      "id": 55,
      "front": "experience",
      "back": "doświadczenie",
      "example": "I have experience in teaching.",
      "next_review": "2026-05-08",
      "interval_days": 3
    }
  ],
  "total_due": 5
}
```

### POST `/api/flashcards/review`
Zapisanie wyniku powtórki fiszki.

**Request Body:**
```json
{
  "user_id": 1,
  "flashcard_id": 55,
  "quality": 4
}
```

**Note:** `quality` (0-5): 0=complete blackout, 5=perfect recall. Oblicza nowy interwał.

**Response (200):**
```json
{
  "message": "Review recorded",
  "next_review": "2026-05-11",
  "interval_days": 6,
  "xp_earned": 2
}
```

### GET `/api/flashcards/export-anki`
Eksport fiszek do formatu Anki (.apkg).

**Query Parameters:**
- `user_id` (required): ID użytkownika

**Response:** Plik binarny .apkg (Content-Type: application/apkg)

### POST `/api/flashcards/generate`
Automatyczne generowanie fiszek z lekcji.

**Request Body:**
```json
{
  "user_id": 1,
  "lesson_id": 42
}
```

**Response (201):**
```json
{
  "message": "Flashcards generated",
  "count": 10
}
```

---

## Conversation API

**Prefix**: `/api/conversation/`

### POST `/api/conversation/start`
Rozpoczęcie nowej sesji konwersacji.

**Request Body:**
```json
{
  "user_id": 1,
  "topic": "Travel",
  "cefr_level": "B1"
}
```

**Response (201):**
```json
{
  "session_id": 7,
  "message": "Session started",
  "ai_greeting": "Hello! Let's talk about travel. Where did you go on your last holiday?"
}
```

### POST `/api/conversation/{session_id}/message`
Wysłanie wiadomości w sesji konwersacji.

**Path Parameters:**
- `session_id` (required): ID sesji

**Request Body:**
```json
{
  "user_id": 1,
  "message": "I went to Spain last summer."
}
```

**Response (200):**
```json
{
  "ai_response": "That sounds wonderful! Spain is beautiful. What cities did you visit?",
  "corrections": [
    {"original": "I went", "suggested": "I went (correct)", "type": "grammar"}
  ],
  "vocabulary_suggestions": [
    {"word": "beautiful", "translation": "piękny"}
  ]
}
```

### GET `/api/conversation/{session_id}/analyze`
Analiza całej sesji konwersacji.

**Path Parameters:**
- `session_id` (required): ID sesji

**Response (200):**
```json
{
  "session_id": 7,
  "total_messages": 10,
  "grammar_score": 85,
  "vocabulary_score": 78,
  "fluency_score": 90,
  "suggestions": [
    "Try using more complex sentence structures",
    "Work on past tense agreements"
  ]
}
```

### POST `/api/conversation/question`
Generowanie pytania konwersacyjnego.

**Request Body:**
```json
{
  "user_id": 1,
  "topic": "Business",
  "cefr_level": "B2"
}
```

**Response (200):**
```json
{
  "question": "How would you handle a difficult client situation?",
  "context": "Business English",
  "suggested_vocabulary": ["negotiate", "compromise", "deadline"]
}
```

### POST `/api/conversation/translate`
Tłumaczenie tekstu.

**Request Body:**
```json
{
  "text": "Hello, how are you?",
  "source_lang": "en",
  "target_lang": "pl"
}
```

**Response (200):**
```json
{
  "translation": "Cześć, jak się masz?",
  "detected_source_lang": "en"
}
```

### POST `/api/conversation/analyze-text`
Analiza tekstu pod kątem błędów.

**Request Body:**
```json
{
  "text": "I has been to Spain.",
  "cefr_level": "B1"
}
```

**Response (200):**
```json
{
  "errors": [
    {
      "type": "grammar",
      "original": "I has",
      "corrected": "I have",
      "explanation": "Use 'have' with 'I' in Present Perfect"
    }
  ],
  "score": 70
}
```

### POST `/api/conversation/voice-chat`
Rozmowa głosowa (STT → AI → TTS).

**Request:** Multipart form-data z plikiem audio
- `user_id`: ID użytkownika
- `audio_file`: Plik audio (WAV/MP3)
- `session_id` (optional): ID istniejącej sesji

**Response (200):**
```json
{
  "user_text": "Hello, how are you?",
  "ai_response": "I'm fine, thank you! How about you?",
  "audio_url": "/api/audio/response_123.mp3"
}
```

---

## Stats API

**Prefix**: `/api/stats/`

### GET `/api/stats/{user_id}`
Pobieranie statystyk użytkownika.

**Path Parameters:**
- `user_id` (required): ID użytkownika

**Response (200):**
```json
{
  "user_id": 1,
  "username": "jan_kowalski",
  "xp": 250,
  "level": 4,
  "next_level_xp": 320,
  "total_lessons": 10,
  "total_tests": 8,
  "average_test_score": 82.5,
  "streak_days": 5,
  "new_achievements": [
    {"id": 2, "name": "Level Up!", "description": "Reach level 4"}
  ]
}
```

### GET `/api/stats/leaderboard`
Ranking użytkowników.

**Query Parameters:**
- `limit` (optional, default=50): Liczba miejsc
- `period` (optional, default="all"): "daily", "weekly", "monthly", "all"

**Response (200):**
```json
{
  "leaderboard": [
    {"rank": 1, "username": "user123", "xp": 1500, "level": 10},
    {"rank": 2, "username": "learner99", "xp": 1350, "level": 9}
  ]
}
```

### GET `/api/stats/tips`
Pobieranie codziennych porad nauki.

**Query Parameters:**
- `user_id` (required): ID użytkownika
- `cefr_level` (optional): Poziom CEFR

**Response (200):**
```json
{
  "tip": "Try to use new vocabulary in sentences immediately after learning it.",
  "category": "vocabulary"
}
```

---

## QuickMode API

**Prefix**: `/api/quickmode/`

### GET `/api/quickmode/today`
Generowanie 15-minutowego planu aktywności.

**Query Parameters:**
- `user_id` (required): ID użytkownika

**Response (200):**
```json
{
  "plan_id": 3,
  "date": "2026-05-08",
  "total_duration_minutes": 15,
  "activities": [
    {
      "type": "vocabulary_review",
      "duration_minutes": 5,
      "description": "Review 10 flashcards"
    },
    {
      "type": "quick_lesson",
      "duration_minutes": 7,
      "description": "Read a short i+1 text"
    },
    {
      "type": "quick_test",
      "duration_minutes": 3,
      "description": "5 questions on recent topics"
    }
  ]
}
```

---

## News API

**Prefix**: `/api/news/`

### GET `/api/news/latest`
Pobieranie najnowszych wiadomości uproszczonych pod poziom CEFR.

**Query Parameters:**
- `user_id` (required): ID użytkownika
- `cefr_level` (optional): Poziom (A1-C2)
- `limit` (optional, default=10)

**Response (200):**
```json
{
  "articles": [
    {
      "title": "Scientists Discover New Planet",
      "original_text": "Scientists have discovered a new exoplanet...",
      "simplified_text": "Scientists found a new planet...",
      "difficulty_level": "B1",
      "source": "BBC News",
      "published_at": "2026-05-08T10:00:00Z",
      "highlighted_words": ["discovered", "exoplanet"]
    }
  ]
}
```

---

## Pronunciation API

**Prefix**: `/api/pronunciation/`

### POST `/api/pronunciation/analyze`
Analiza wymowy na podstawie nagrania audio.

**Request:** Multipart form-data
- `user_id`: ID użytkownika
- `audio_file`: Plik audio (WAV)
- `reference_text` (optional): Tekst referencyjny

**Response (200):**
```json
{
  "transcription": "I went to the park yesterday.",
  "accuracy_score": 85,
  "word_scores": [
    {"word": "went", "score": 90, "phonemes": "wɛnt"},
    {"word": "park", "score": 80, "phonemes": "pɑrk"}
  ],
  "overall_feedback": "Good job! Work on 'park' pronunciation."
}
```

---

## Settings API

**Prefix**: `/api/settings/`

### GET `/api/settings/{user_id}`
Pobieranie ustawień użytkownika.

**Response (200):**
```json
{
  "user_id": 1,
  "cefr_level": "B1",
  "daily_goal_minutes": 30,
  "notification_enabled": true,
  "tts_voice": "en-US-JennyNeural",
  "theme": "light"
}
```

### PUT `/api/settings/{user_id}`
Aktualizacja ustawień.

**Request Body:**
```json
{
  "cefr_level": "B2",
  "daily_goal_minutes": 45,
  "notification_enabled": false
}
```

**Response (200):**
```json
{
  "message": "Settings updated successfully"
}
```

---

## Audio API

**Prefix**: `/api/audio/`

### GET `/api/audio/{filename}`
Serwowanie wygenerowanych plików audio.

**Path Parameters:**
- `filename` (required): Nazwa pliku audio

**Response:** Plik binarny audio

### POST `/api/audio/generate`
Generowanie audio z tekstu (edge-tts).

**Request Body:**
```json
{
  "text": "Hello, how are you today?",
  "voice": "en-US-JennyNeural",
  "rate": "+0%"
}
```

**Response (200):**
```json
{
  "audio_url": "/api/audio/tts_12345.mp3",
  "duration_seconds": 2.5
}
```

---

## YouTube API

**Prefix**: `/api/youtube/`

### GET `/api/youtube/search`
Wyszukiwanie filmów edukacyjnych.

**Query Parameters:**
- `query` (required): Hasło wyszukiwania
- `cefr_level` (optional): Poziom CEFR
- `max_results` (optional, default=10)

**Response (200):**
```json
{
  "videos": [
    {
      "video_id": "abc123",
      "title": "English Conversation Practice",
      "channel": "English Learning TV",
      "duration_seconds": 600,
      "cefr_level": "B1",
      "transcript_available": true
    }
  ]
}
```

### GET `/api/youtube/{video_id}/transcript`
Pobieranie transkrypcji filmu.

**Response (200):**
```json
{
  "video_id": "abc123",
  "transcript": [
    {"start": 0.0, "end": 2.5, "text": "Hello everyone..."}
  ]
}
```

---

## Voice Chat API

**Prefix**: `/api/voice-chat/`

### POST `/api/voice-chat/start`
Rozpoczęcie sesji voice chat.

**Request Body:**
```json
{
  "user_id": 1,
  "cefr_level": "B1"
}
```

**Response (201):**
```json
{
  "session_id": 12,
  "greeting_audio_url": "/api/audio/greeting_12.mp3"
}
```

### POST `/api/voice-chat/{session_id}/message`
Wysłanie wiadomości głosowej.

**Request:** Multipart form-data
- `audio_file`: Plik audio

**Response (200):**
```json
{
  "user_text": "Hello!",
  "ai_text": "Hi there! How can I help you today?",
  "ai_audio_url": "/api/audio/response_12.mp3"
}
```

---

## Kody Błędów

| Kod | Opis |
|-----|------|
| 200 | OK - żądanie zakończone sukcesem |
| 201 | Created - zasób utworzony |
| 400 | Bad Request - nieprawidłowe parametry |
| 401 | Unauthorized - brak autoryzacji |
| 404 | Not Found - zasób nie znaleziony |
| 422 | Unprocessable Entity - błąd walidacji (Pydantic) |
| 500 | Internal Server Error - błąd serwera |

## Uwagi Ogólne

- Wszystkie endpointy zwracają JSON (chyba że określono inaczej, np. PDF, audio)
- Frontend używa `responseType: 'blob'` dla pobierania plików binarnych
- Timeout dla zapytań API w frontendzie: 60 sekund
- Backend ma wbudowane fallbacki dla wywołań Gemini API
