# LinguaAI — AI-Powered Language Learning App

Aplikacja do nauki języków obcych wspierana przez AI. Interfejs w języku polskim. Uczy się z Tobą — dostosowuje poziom, generuje lekcje, analizuje błędy i motywuje systemem osiągnięć.

## Spis treści

- [Funkcje](#funkcje)
- [Architektura](#architektura)
- [Tech Stack](#tech-stack)
- [Szybki start](#szybki-start)
- [Dokumentacja API](#dokumentacja-api)
- [Struktura projektu](#struktura-projektu)
- [Testy](#testy)
- [Wdrożenie Docker](#wdrożenie-docker)
- [Rozwiązywanie problemów](#rozwiązywanie-problemów)

---

## Funkcje

### 1. Test poziomujący CEFR
- 20-pytańowy test diagnostyczny
- Poziomy: A1, A2, B1, B2, C1, C2
- Automatyczne generowanie pytań przez AI
- Konserwatywna kalibracja (fallback przy niskim wyniku)
- Personalizacja na podstawie języka ojczystego

### 2. Codzienne lekcje
- AI-generowane lekcje dopasowane do poziomu
- Sekcje: słownictwo, gramatyka, dialogi, ćwiczenia, zadanie produkcyjne
- **Comprehensible Input** — teksty i+1 z podświetlonymi nowymi słowami
- **Interleaved Review** — powtórka materiału z ostatnich 7 dni
- **Output Forcing** — dwufazowe karty wymuszające produkcję językową
- Eksport do PDF z tabelą słówek
- Audio TTS (Text-to-Speech) dla całej lekcji

### 3. System fiszek (Spaced Repetition)
- Algorytm **FSRS v6** (Free Spaced Repetition Scheduler)
- Automatyczne planowanie powtórek na podstawie jakości odpowiedzi (1-4)
- Eksport do Anki (.apki)
- Audio dla każdej fiszki
- Filtry: po dacie dodania (dzisiaj/tydzień/miesiąc), po poziomie CEFR
- Dodawanie fiszek przez AI — wystarczy wpisać słowo

### 4. Konwersacja z AI
- Rozmowy tekstowe i głosowe
- AI jako partner językowy
- Automatyczna analiza rozmowy (błędy, wynik, rekomendacje)
- Tłumaczenie słówek i fraz

### 5. Testy i ocena
- Codzienne testy ze znajomości materiału
- Testy tygodniowe
- Automatyczna ocena i analiza błędów
- XP za testy: `wynik × 0.5` (max 50 XP)

### 6. System XP i osiągnięcia
- 50 poziomów postępu
- Krzywa poziomów: `(n-1)² × 20` XP
- **57 osiągnięć** w 10 kategoriach (lekcje, serie, testy, XP, poziomy, fiszki, konwersacje, wymowa, tematy, newsy, filmy, błędy, wiele języków)
- Powiadomienia toast przy odblokowaniu osiągnięcia
- Tablica liderów (leaderboard)

### 7. Tryb szybki (Quick Mode)
- Inteligentny plan dzienny (5-120 minut, własny czas)
- Timer niezależny od zakładki
- Lekcja, test, fiszki, konwersacja, czytanie newsów

### 8. Czytanie newsów
- RSS feed dla różnych języków
- AI upraszcza artykuły do poziomu użytkownika (CEFR)
- Zaznaczanie tekstu → tworzenie fiszki przez AI
- Pytania kontrolne do artykułu

### 9. Trener wymowy
- Transkrypcja audio przez faster-whisper (model tiny, ~75 MB)
- Ocena wymowy słowo po słowie (word-level scoring)
- Podsumowanie sesji: średnia, najlepszy wynik, problemowe słowa
- Audio z wymową poprawną

### 10. YouTube Learning
- Wyszukiwanie filmów edukacyjnych dopasowanych do poziomu CEFR
- Sugestie na podstawie tematu lekcji

### 11. Backup i administracja
- Automatyczny backup bazy danych (codzienny, retencja 7 dni)
- Admin API: tworzenie, lista, przywracanie backupów
- Ochrona kluczem API (header `X-Admin-Key`)

---

## Architektura

```
┌──────────────────────────────────────────────────────┐
│                  Frontend (React)                     │
│    React 19 + React Router v7 + Axios + Tailwind     │
│                   :5173 (dev server)                  │
└──────────────────────────┬───────────────────────────┘
                           │ /api, /audio proxy
┌──────────────────────────▼───────────────────────────┐
│                Backend (FastAPI)                      │
│   FastAPI + SQLAlchemy 2.0 + SQLite + AI Provider    │
│                   :8001 (API server)                  │
└──────────────────────────┬───────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                   ▼
┌──────────────┐  ┌───────────────┐  ┌────────────────┐
│   Routers    │  │   Services    │  │    Models      │
│ /api/*       │◄─┤ - AI calls    │  │ - User         │
│ placement    │  │ - Lessons     │  │ - Lesson       │
│ lessons      │  │ - Tests       │  │ - TestResult   │
│ tests        │  │ - Audio (TTS) │  │ - Flashcard    │
│ flashcards   │  │ - PDF export  │  │ - Achievement  │
│ conversation │  │ - News (RSS)  │  │ - StudyPlan    │
│ stats        │  │ - Anki export │  │ - Topic        │
│ quickmode    │  │ - Backup      │  │ - ...          │
│ news         │  │ - Achievements│  │                │
│ pronunciation│  └───────────────┘  └────────────────┘
│ admin        │
│ youtube      │
│ voice-chat   │
│ settings     │
│ audio        │
│ topics       │
└──────────────┘
```

### Przepływ żądania

```
Router → Service → SQLAlchemy Session (get_db dependency)
```

---

## Tech Stack

### Backend

| Komponent | Technologia | Uwagi |
|-----------|-------------|--------|
| Framework | **FastAPI** | Async API, automatyczna dokumentacja OpenAPI |
| ORM | **SQLAlchemy 2.0** | Deklaratywne modele |
| Baza danych | **SQLite** | PostgreSQL-ready |
| AI Provider | **OpenRouter** lub **Google Gemini** | Konfigurowalny w .env |
| TTS | **edge-tts** | Szybkie generowanie audio |
| PDF | **fpdf2** | Eksport lekcji |
| RSS | **feedparser** | Czytanie newsów |
| Speech-to-Text | **faster-whisper** | Model `tiny` (~75 MB, CPU, int8) |
| Spaced Repetition | **FSRS v6** | Free Spaced Repetition Scheduler |
| Anki Export | **genanki** | Generowanie plików .apkg |

### Frontend

| Komponent | Technologia | Uwagi |
|-----------|-------------|--------|
| Framework | **React 19** | Funkcyjne komponenty, hooki |
| Routing | **React Router v7** | SPA, nested routes |
| HTTP Client | **Axios** | Interceptory, unwrap `response.data` |
| Styling | **Tailwind CSS** | Utility-first CSS |
| Build Tool | **Vite** | Szybki dev server, HMR |
| Icons | **lucide-react** | Nowoczesny zestaw ikon |

---

## Szybki start

### Wymagania

- **Python** 3.11+
- **Node.js** 20+
- **Klucz API** — OpenRouter lub Gemini (wystarczy jeden)

### 1. Klonowanie repozytorium

```bash
git clone <repo-url>
cd LinguaAI
```

### 2. Konfiguracja

```bash
copy backend\.env.example backend\.env   # Windows
```

Edytuj `backend\.env`:

```env
# Wybór dostawcy AI: "openrouter" lub "gemini"
AI_PROVIDER=openrouter

# Klucz OpenRouter (https://openrouter.ai/keys)
OPENROUTER_API_KEY=sk-or-v1-...

# LUB klucz Gemini (https://aistudio.google.com/app/apikey)
# GEMINI_API_KEY=AIza...

# Opcjonalnie: klucz admina (backup/restore)
ADMIN_API_KEY=your-secret-key

# Opcjonalnie: YouTube API
YOUTUBE_API_KEY=AIza...
```

### 3. Uruchomienie — tryb deweloperski

**Windows (CMD):**
```cmd
start.bat
```

**Windows (PowerShell):**
```powershell
.\start.ps1
```

**Ręcznie (dwie terminale):**

Terminal 1 — backend (z katalogu głównego projektu):
```bash
py -3.11 -m uvicorn backend.main:app --reload --port 8001
```

Terminal 2 — frontend:
```bash
cd frontend
npm install
npm run dev
```

### 4. Dostęp

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8001
- **API Docs (Swagger):** http://localhost:8001/docs

> **Ważne:** Uruchamiaj backend z katalogu głównego projektu (nie z `backend/`), żeby importy `backend.*` działały poprawnie.

---

## Dokumentacja API

Interaktywna dokumentacja Swagger: http://localhost:8001/docs

| Metoda | Ścieżka | Opis |
|--------|---------|------|
| `POST` | `/api/placement/start` | Rozpocznij test poziomujący |
| `POST` | `/api/placement/answer` | Odpowiedz na pytanie |
| `GET` | `/api/placement/{user_id}/study-plan` | Pobierz plan nauki |
| `GET` | `/api/lessons/{user_id}/daily` | Pobierz lekcję dzienną |
| `POST` | `/api/lessons/{lesson_id}/complete` | Ukończ lekcję (+25 XP) |
| `GET` | `/api/lessons/{lesson_id}/export-pdf` | Eksport lekcji do PDF |
| `GET` | `/api/tests/{user_id}/daily` | Pobierz test dzienny |
| `POST` | `/api/tests/{test_id}/submit` | Wyślij odpowiedzi |
| `GET` | `/api/flashcards/{user_id}` | Lista fiszek |
| `GET` | `/api/flashcards/{user_id}/due` | Fiszki do powtórki |
| `POST` | `/api/flashcards/{user_id}/add` | Dodaj fiszkę ręcznie |
| `POST` | `/api/flashcards/{user_id}/add-ai` | Dodaj fiszkę (AI generuje tłumaczenie) |
| `POST` | `/api/flashcards/{id}/review` | Powtórz fiszkę (FSRS) |
| `POST` | `/api/flashcards/{user_id}/export-anki` | Eksport do Anki |
| `POST` | `/api/flashcards/{id}/audio` | Generuj audio fiszki |
| `POST` | `/api/conversation/start` | Rozpocznij rozmowę |
| `POST` | `/api/conversation/message` | Wyślij wiadomość |
| `GET` | `/api/stats/{user_id}` | Statystyki, XP, osiągnięcia |
| `GET` | `/api/tips/{user_id}` | Dzienne wskazówki |
| `GET` | `/api/news/{user_id}` | Artykuły newsowe |
| `POST` | `/api/pronunciation/analyze` | Analiza wymowy |
| `GET` | `/api/quickmode/{user_id}` | Plan trybu szybkiego |
| `GET` | `/api/videos/{user_id}` | Sugestie filmów YouTube |
| `POST` | `/api/admin/backup` | Utwórz backup (wymaga `X-Admin-Key`) |
| `GET` | `/api/admin/backups` | Lista backupów |
| `POST` | `/api/admin/restore` | Przywróć backup |

---

## Struktura projektu

```
LinguaAI/
├── backend/
│   ├── main.py                    # FastAPI app, lifespan, CORS, routers
│   ├── config.py                  # Pydantic Settings
│   ├── database.py                # SQLAlchemy engine, SessionLocal, Base
│   ├── models/                    # Modele SQLAlchemy
│   │   ├── user.py
│   │   ├── lesson.py
│   │   ├── test_result.py
│   │   ├── flashcard.py
│   │   ├── study_plan.py
│   │   ├── achievement.py
│   │   ├── topic.py
│   │   └── ...
│   ├── routers/                   # Endpointy API
│   │   ├── placement.py           # Test poziomujący + plan nauki
│   │   ├── lessons.py             # Lekcje, PDF, audio
│   │   ├── tests.py               # Testy dzienne/tygodniowe
│   │   ├── flashcards.py          # FSRS, Anki, audio
│   │   ├── conversation.py        # Rozmowy tekstowe
│   │   ├── voice_chat.py          # Rozmowy głosowe
│   │   ├── stats.py               # XP, poziomy, osiągnięcia, tips
│   │   ├── quickmode.py           # Tryb szybki
│   │   ├── news.py                # Artykuły RSS
│   │   ├── pronunciation.py       # Analiza wymowy
│   │   ├── youtube.py             # Filmy YouTube
│   │   ├── settings.py            # Zmiana języka
│   │   ├── audio.py               # Generowanie audio
│   │   ├── topics.py              # Tematy użytkownika
│   │   └── admin.py               # Backup/restore
│   ├── services/                  # Logika biznesowa
│   │   ├── gemini_service.py      # Komunikacja z AI
│   │   ├── lesson_generator.py    # Generowanie lekcji/testów
│   │   ├── test_generator.py      # Testy + XP
│   │   ├── achievement_service.py # XP, poziomy, 57 osiągnięć
│   │   ├── audio_service.py       # edge-tts TTS
│   │   ├── pdf_service.py         # fpdf2 PDF export
│   │   ├── anki_service.py        # Eksport Anki (.apkg)
│   │   ├── news_service.py        # RSS + AI simplification
│   │   ├── pronunciation_service.py # faster-whisper
│   │   ├── backup_service.py      # Backup bazy danych
│   │   └── fsrs_service.py        # Algorytm FSRS v6
│   ├── schemas/                   # Schematy Pydantic
│   ├── audio/                     # Wygenerowane pliki audio
│   ├── exports/                   # PDF, Anki exports
│   ├── tests/                     # Testy pytest (244 testy)
│   │   ├── conftest.py
│   │   ├── test_flashcards.py
│   │   ├── test_backup_service.py
│   │   └── ...
│   ├── .env.example
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.js          # Axios instance + interceptors
│   │   ├── components/
│   │   │   ├── Layout.jsx         # Layout + achievement toasts
│   │   │   ├── NavBar.jsx
│   │   │   ├── PlayButton.jsx
│   │   │   └── ...
│   │   ├── pages/
│   │   │   ├── PlacementTest.jsx
│   │   │   ├── DailyLesson.jsx
│   │   │   ├── DailyTest.jsx
│   │   │   ├── Flashcards.jsx
│   │   │   ├── Conversation.jsx
│   │   │   ├── Stats.jsx
│   │   │   ├── QuickMode.jsx
│   │   │   ├── News.jsx
│   │   │   ├── PronunciationTrainer.jsx
│   │   │   ├── Videos.jsx
│   │   │   └── ...
│   │   ├── App.jsx                # React Router
│   │   └── main.jsx               # Entry point
│   ├── vite.config.js             # Vite + proxy
│   ├── package.json
│   └── tailwind.config.js
│
├── docker-compose.yml             # Backend + Frontend + Backup
├── Dockerfile.backend             # Obraz backendu
├── Dockerfile.frontend            # Obraz frontendu (nginx)
├── start.bat                      # Launcher Windows CMD
├── start.ps1                      # Launcher PowerShell
├── CLAUDE.md                      # Instrukcje dla Claude Code
└── README.md                      # Ten plik
```

---

## Testy

```bash
# Wszystkie testy (244)
py -3.11 -m pytest backend/tests/ -v

# Konkretny plik
py -3.11 -m pytest backend/tests/test_flashcards.py -v

# Z pokryciem
py -3.11 -m pytest backend/tests/ --cov=backend --cov-report=term-missing
```

### Statystyki

- **Łączna liczba testów:** 244
- **Framework:** pytest + pytest-asyncio
- **Pokrycie:** routers, services, models

---

## Wdrożenie Docker

```bash
# Budowanie i uruchomienie
docker-compose up --build

# W tle
docker-compose up -d --build

# Logi
docker-compose logs -f backend

# Zatrzymanie
docker-compose down
```

Usługi:
- **Backend:** http://localhost:8001
- **Frontend:** http://localhost:5173
- **Backup:** automatyczny, co 24h, retencja 7 dni

### Wolumeny Docker

| Wolumen | Zawartość |
|---------|-----------|
| `lingua_ai_db` | Baza danych SQLite |
| `lingua_ai_audio` | Wygenerowane pliki audio |
| `lingua_ai_exports` | Eksporty PDF/Anki |
| `lingua_ai_backups` | Kopie zapasowe bazy |

---

## Rozwiązywanie problemów

### Backend nie startuje — `ModuleNotFoundError`
```bash
# ✅ Dobrze (z katalogu głównego)
py -3.11 -m uvicorn backend.main:app --reload --port 8001

# Źle
cd backend
py -3.11 -m uvicorn main:app --reload --port 8001
```

### Frontend nie łączy się z backendiem
Sprawdź `VITE_API_URL` w `vite.config.js` — powinno wskazywać na `http://localhost:8001`.

### Błąd AI — `401 Unauthorized`
Sprawdź klucz API w `backend\.env`.

### Błąd bazy danych — `table does not exist`
Usuń stary plik `backend\lingua_ai.db` — zostanie utworzony nowy.

### Testy nie przechodzą
```bash
# Usuń stary plik testowej bazy
del backend\test_lingua_ai.db
py -3.11 -m pytest backend/tests/ -v
```

### Błąd `can't subtract offset-naive and offset-aware datetimes`
Znany bug z SQLite — upewnij się, że masz najnowszą wersję `backend/routers/flashcards.py` z fixem timezone.

---

## Kluczowe numery

| Parametr | Wartość | Gdzie |
|----------|---------|-------|
| XP za lekcję | +25 | `routers/lessons.py` |
| XP za test | `score × 0.5` (max 50) | `services/test_generator.py` |
| Krzywa poziomów | `(n-1)² × 20` XP, 50 poziomów | `services/achievement_service.py` |
| Port backendu | 8001 | `start.bat`, `docker-compose.yml` |
| Port frontendu | 5173 | `vite.config.js` |
| Timeout API (frontend) | 60 s | `frontend/src/api/client.js` |
| Retencja backupów | 7 dni | `services/backup_service.py` |
| Osiągnięcia | 57 typów | `services/achievement_service.py` |

---

## Licencja

MIT
