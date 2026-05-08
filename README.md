# LinguaAI - Inteligentny Tutor Językowy

Nowoczesna platforma do nauki języków obcych wspierana przez AI (Google Gemini). Konwersacje, lekcje, testy, system fiszek i analiza wymowy w jednym miejscu.

## Spis treści

- [Funkcje](#funkcje)
- [Architektura](#architektura)
- [Tech Stack](#tech-stack)
- [Szybki start](#szybki-start)
- [Dokumentacja API](#dokumentacja-api)
- [Struktura projektu](#struktura-projektu)
- [Rozwój](#rozwój)
- [Testy](#testy)
- [Wdrożenie](#wdrożenie)
- [Pamięć Claude](#pamięć-claude)

---

## Funkcje

### 1. Test placujący CEFR
- 20-pytańowy test diagnostyczny
- Poziomy: A1, A2, B1, B2, C1, C2
- Automatyczne generowanie pytań przez AI (Google Gemini)
- Typy pytań: `fill_blank`, `correct_sentence`, `word_order`, `translation`, `comprehension`
- Personalizacja na podstawie języka ojczystego

### 2. Codzienne lekcje
- AI-generowane lekcje dopasowane do poziomu
- Sekcje: słownictwo, gramatyka, cel lekcji, dialogi, ćwiczenia
- **Comprehensible Input** — teksty i+1 z podświetlonymi nowymi słowami
- **Interleaved Review** — powtórka materiału z ostatnich 7 dni
- **Output Forcing** — dwufazowe karty do wymuszania produkcji językowej
- Eksport do PDF z tabelą słówek
- Audio TTS (Text-to-Speech) dla tekstów

### 3. System fiszek (Spaced Repetition)
- Algorytm SM-2 (SuperMemo-2)
- Automatyczne planowanie powtórek na podstawie jakości odpowiedzi
- Eksport do Anki (.apkg)
- Integracja ze słownictwem z lekcji

### 4. Konwersacja z AI
- Rozmowy tekstowe i głosowe
- AI konwersacyjne jako partner językowy
- Automatyczna analiza rozmowy (błędy, wynik, rekomendacje)
- Wsparcie dla wklejonego tekstu (analyze pasted text)
- Tłumaczenie słówek i fraz

### 5. Testy i ocena
- Codzienne testy ze znajomości materiału
- Testy tygodniowe (zszyte z planem nauki)
- Automatyczna ocena i analiza błędów
- Śledzenie słabych stron (weak areas)

### 6. System XP i osiągnięcia
- 50 poziomów postępu
- Krzywa poziomów: `(n-1)² × 20` XP
- XP za: lekcje (+25), testy (score × 0.5, max 50), konwersacje, fiszki
- System osiągnięć z powiadomieniami toast
- Tablica liderów (leaderboard)

### 7. Quick Mode — 15-minutowy plan dnia
- Inteligentny dobór aktywności na 15 minut
- Lekcja, test, fiszki, konwersacja, czytanie newsów
- Śledzenie ukończonych zadań w czasie rzeczywistym

### 8. Czytanie newsów
- RSS feed dla różnych języków
- AI upraszcza artykuły do poziomu użytkownika (CEFR)
- Cache 6-godzinny dla optymalizacji
- Limit artykułów (parametr `limit`)

### 9. Trener wymowy
- Transkrypcja audio przez faster-whisper (model tiny, ~75 MB)
- Ocena wymowy słowo po słowie (word-level scoring)
- Frazy z lekcji jako materiał do ćwiczeń

### 10. YouTube Learning
- Wyszukiwanie filmów edukacyjnych na podstawie tematu lekcji
- Napisy (captions) w formacie SRT
- Integracja z planem nauki

### 11. Google Drive Backup
- Autoryzacja OAuth2 z Google
- Automatyczny backup bazy danych (SQLite → Google Drive)
- Harmonogram zapisu (codziennie o 2:00 w nocy)

---

## Architektura

```
┌────────────────────────────────────────┐
│                        Frontend (React)                        │
│  React 18 + React Router v6 + Axios + Tailwind CSS + Vite  │
│                     :5173 (dev server)                      │
└────────────────────────────┬───────────────────────────────────┘
                             │
                     /api, /audio proxy
                             │
┌────────────────────────────▼───────────────────────────────────┐
│                      Backend (FastAPI)                       │
│   FastAPI + SQLAlchemy + SQLite + Google Gemini 2.0 Flash  │
│                     :8000 (API server)                     │
└────────────────────────────┬───────────────────────────────────┘
                             │
        ┌────────────────────┼─────────────────┐
        ▼                    ▼                    ▼
┌───────────┐    ┌───────────────┐    ┌───────────┐
│ Routers   │    │  Services    │    │ Models     │
│ /api/*    │◄──►│ - Gemini   │    │ - User      │
│ placement  │    │ - Lesson    │    │ - Lesson    │
│ lessons   │    │ - Test      │    │ - TestResult│
│ tests     │    │ - PDF       │    │ - StudyPlan │
│ flashcards │    │ - News      │    │ - Flashcard │
│ conversation│    │ - Audio     │    │ - Achievement│
│ stats     │    │ - Pronunciation│ │             │
│ quickmode  │    │ - Anki      │    │             │
│ news      │    │ - Obsidian  │    │             │
│ pronunciation│    │ - GoogleDrive│    │             │
│ voice-chat│    └───────────────┘    └───────────┘
│ youtube   │
│ settings  │
│ audio     │
└───────────┘
```

### Przepływ żądania (Request Flow)

```
Router → Service → SQLAlchemy Session (get_db dependency)
```

Przykład:
1. `POST /api/lessons/{user_id}` → `routers/lessons.py`
2. Wywołanie `services/lesson_generator.py` → budowa promptu dla AI
3. `services/gemini_service.py` → wywołanie OpenRouter API (Google Gemini 2.0 Flash)
4. Zapis do bazy przez SQLAlchemy session
5. Zwrot JSON odpowiedzi do frontendu

---

## Tech Stack

### Backend

| Komponent | Technologia | Uwagi |
|-----------|-------------|--------|
| Framework | **FastAPI** | Async API, automatyczna dokumentacja OpenAPI |
| ORM | **SQLAlchemy** | Wersja 2.0, deklaratywne modele |
| Baza danych | **SQLite** | Dla dewelopmentu, PostgreSQL-ready |
| AI Model | **Google Gemini 2.0 Flash** | Przez OpenRouter API |
| TTS | **edge-tts** | Szybkie generowanie audio |
| PDF | **fpdf2** | Generowanie eksportów lekcji |
| RSS | **feedparser** | Czytanie newsów |
| Speech-to-Text | **faster-whisper** | Model `tiny` (~75 MB, CPU, int8) |
| Async HTTP | **httpx** | Nowoczesny klient HTTP |

### Frontend

| Komponent | Technologia | Uwagi |
|-----------|-------------|--------|
| Framework | **React 18** | Funkcyjne komponenty, hooki |
| Routing | **React Router v6** | SPA, nested routes |
| HTTP Client | **Axios** | Interceptory, unwrap `response.data` |
| Styling | **Tailwind CSS** | Utility-first CSS |
| Build Tool | **Vite** | Szybki dev server, HMR |
| Icons | **lucide-react** | Nowoczesny zestaw ikon |

---

## Szybki start

### Wymagania

- **Python** 3.10+
- **Node.js** 18+
- **Google Gemini API Key** (przez OpenRouter)

### 1. Klonowanie repozytorium

```bash
git clone https://github.com/Matthew19381/language-tutor.git
cd language-tutor
```

### 2. Konfiguracja backendu

```bash
# Skopiuj przykładowy plik środowiskowy
copy .env.example .env   # Windows CMD
# cp .env.example .env            # Linux/Mac

# Edytuj .env i ustaw GEMINI_API_KEY oraz OPENROUTER_API_KEY
```

**Zawartość `.env`:**
```env
GEMINI_API_KEY=your_gemini_api_key_here
OPENROUTER_API_KEY=sk-or-v1_your_openrouter_key_here
TARGET_LANGUAGE=German
NATIVE_LANGUAGE=Polish
DATABASE_URL=sqlite:///./lingua_ai.db
DEBUG=True
```

### 3. Instalacja zależności backendu

```bash
pip install -r requirements.txt
```

### 4. Instalacja zależności frontendu

```bash
cd ../frontend
npm install
```

### 5. Uruchomienie (z katalogu głównego projektu)

**Opcja A — Skrypty startowe:**
```bash
# Windows CMD (otwiera dwa okna terminala)
start.bat

# PowerShell
.\start.ps1
```

**Opcja B — Ręcznie:**
```bash
# Terminal 1 - Backend (z katalogu głównego!)
uvicorn backend.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 6. Dostęp

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/docs
- **API Docs (ReDoc):** http://localhost:8000/redoc

> **Ważne:** Frontend dev server na `:5173` proxyzuje `/api` i `/audio` do `http://localhost:8000` (skonfigurowane w `frontend/vite.config.js`).

---

## Dokumentacja API

Pełna dokumentacja API znajduje się w [docs/api.md](docs/api.md).

Dostępne endpointy:
- `POST /api/placement/create` — Tworzenie użytkownika + test placujący
- `GET /api/lessons/today/{user_id}` — Dzisiejsza lekcja
- `POST /api/tests/submit` — Zaliczenie testu (XP)
- `GET /api/flashcards/due/{user_id}` — Fiszki do powtórki
- `POST /api/conversation/message` — Wiadomość w konwersacji
- `GET /api/stats/{user_id}` — Statystyki, poziom, XP
- `GET /api/quickmode/{user_id}` — 15-minutowy plan
- `GET /api/news/{user_id}` — Artykuły newsowe
- `POST /api/pronunciation/analyze` — Analiza wymowy

Interaktywna dokumentacja Swagger dostępna pod adresem: http://localhost:8000/docs

---

## Struktura projektu

```
lingua-ai/
├── backend/
│   ├── main.py                    # FastAPI app, lifespan, CORS, routers
│   ├── config.py                  # Pydantic Settings
│   ├── database.py                # SQLAlchemy engine, SessionLocal, Base
│   ├── models/                   # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── lesson.py
│   │   ├── test_result.py
│   │   ├── flashcard.py
│   │   ├── study_plan.py
│   │   └── achievement.py
│   ├── routers/                  # FastAPI route handlers
│   │   ├── __init__.py
│   │   ├── placement.py
│   │   ├── lessons.py
│   │   ├── tests.py
│   │   ├── flashcards.py
│   │   ├── conversation.py
│   │   ├── stats.py
│   │   ├── quickmode.py
│   │   ├── news.py
│   │   ├── pronunciation.py
│   │   ├── settings.py
│   │   ├── audio.py
│   │   ├── youtube.py
│   │   └── voice_chat.py
│   ├── services/                 # Business logic + AI calls
│   │   ├── __init__.py
│   │   ├── gemini_service.py     # OpenRouter API calls
│   │   ├── lesson_generator.py   # AI prompts for lessons, tests
│   │   ├── test_generator.py     # Test creation + XP award
│   │   ├── achievement_service.py # Level/XP math, achievements
│   │   ├── audio_service.py     # edge-tts TTS
│   │   ├── pdf_service.py       # fpdf2 PDF export
│   │   ├── news_service.py      # RSS + AI simplification
│   │   ├── pronunciation_service.py # faster-whisper
│   │   ├── anki_service.py      # .apkg export
│   │   ├── google_drive_service.py # OAuth2 + backup
│   │   ├── obsidian_service.py   # Markdown export
│   │   └── model_router.py     # Smart model selection
│   ├── schemas/                  # Pydantic request/response models
│   ├── audio/                    # Generated TTS audio files
│   ├── exports/                 # PDF, Anki exports
│   ├── tests/                   # pytest test suite (127 tests)
│   │   ├── conftest.py
│   │   ├── test_achievement_service.py
│   │   ├── test_placement.py
│   │   ├── test_lessons.py
│   │   ├── test_tests.py
│   │   ├── test_flashcards.py
│   │   ├── test_conversation.py
│   │   ├── test_stats.py
│   │   ├── test_quickmode.py
│   │   ├── test_news.py
│   │   ├── test_pronunciation.py
│   │   ├── test_settings.py
│   │   ├── test_audio.py
│   │   ├── test_youtube.py
│   │   └── test_voice_chat.py
│   ├── .env.example
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.js         # Axios instance + interceptors
│   │   ├── components/
│   │   │   ├── Layout.jsx       # Shell with NavBar + toasts
│   │   │   ├── NavBar.jsx
│   │   │   ├── LoadingSpinner.jsx
│   │   │   ├── NotificationManager.jsx
│   │   │   └── PlayButton.jsx
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── PlacementTest.jsx
│   │   │   ├── DailyLesson.jsx
│   │   │   ├── DailyTest.jsx
│   │   │   ├── Flashcards.jsx
│   │   │   ├── Conversation.jsx
│   │   │   ├── Stats.jsx
│   │   │   ├── QuickMode.jsx
│   │   │   ├── News.jsx
│   │   │   ├── PronunciationTrainer.jsx
│   │   │   ├── LessonHistory.jsx
│   │   │   ├── Videos.jsx
│   │   │   └── ErrorReview.jsx
│   │   ├── i18n/
│   │   │   └── translations.js   # UI translations
│   │   ├── App.jsx               # React Router setup
│   │   └── main.jsx              # React entry point
│   ├── vite.config.js             # Vite + proxy config
│   ├── package.json
│   └── tailwind.config.js
│
├── docs/                          # Documentation
│   ├── architecture.md
│   ├── api.md
│   ├── user-guide.md
│   ├── developer-guide.md
│   ├── deployment.md
│   └── backup-instructions.md
│
├── .gitignore
├── CLAUDE.md                     # Instructions for Claude Code
├── README.md                      # This file
├── start.bat                      # Windows CMD starter
└── start.ps1                      # PowerShell starter
```

---

## Rozwój

Szczegółowy poradnik dla deweloperów: [docs/developer-guide.md](docs/developer-guide.md)

### Dodawanie nowego routera

1. Utwórz plik w `backend/routers/`
2. Zarejestruj w `backend/main.py`: `app.include_router(router, tags=["Name"])`

### Dodawanie nowego modelu SQLAlchemy

1. Utwórz model w `backend/models/`
2. Dodaj import w `backend/models/__init__.py`
3. Dodaj import w `backend/main.py` (w bloku lifespan, przed `Base.metadata.create_all`)

### Dodawanie nowej strony frontendu

1. Utwórz plik w `frontend/src/pages/ExamplePage.jsx`
2. Dodaj routing w `frontend/src/App.jsx`
3. Dodaj link w `frontend/src/components/NavBar.jsx`

---

## Testy

```bash
cd "C:/Projects/LinguaAI"

# Wszystkie testy
python -m pytest backend/tests/ -v

# Z pokazaniem stdout
python -m pytest backend/tests/ -v -s

# Tylko jeden plik testowy
python -m pytest backend/tests/test_lessons.py -v

# Z logami błędów (short)
python -m pytest backend/tests/ --tb=short
```

### Statystyki testów

- **Łączna liczba testów:** 127
- **Pliki testowe:** 13
- **Framework:** pytest + pytest-asyncio
- **Coverage:** routers, services, models

| Plik | Liczba testów | Testowane routery/serwisy |
|------|---------------|--------------------------------|
| test_achievement_service.py | 11 | Achievement service (XP, level math) |
| test_placement.py | 8 | Placement router |
| test_lessons.py | 12 | Lessons router |
| test_tests.py | 9 | Tests router + test_generator |
| test_flashcards.py | 10 | Flashcards router |
| test_conversation.py | 8 | Conversation router |
| test_stats.py | 7 | Stats router |
| test_quickmode.py | 7 | QuickMode router |
| test_news.py | 6 | News router |
| test_pronunciation.py | 6 | Pronunciation router |
| test_settings.py | 7 | Settings router |
| test_audio.py | 5 | Audio router |
| test_youtube.py | 6 | YouTube router |
| test_voice_chat.py | 6 | Voice Chat router |

---

## Wdrożenie

Szczegółowa dokumentacja wdrożeniowa: [docs/deployment.md](docs/deployment.md)

### Szybki przegląd

1. **Przygotowanie serwera** (Linux VPS):
   ```bash
   sudo apt update
   sudo apt install python3.10+ nodejs nginx certbot
   ```

2. **Backend** (systemd service):
   - Zainstaluj zależności: `pip install -r requirements.txt`
   - Ustaw zmienne środowiskowe w `.env`
   - Uruchom jako systemd service (uvicorn z pracownikami)

3. **Frontend** (build statyczny):
   ```bash
   cd frontend
   npm run build
   # Serwuj `dist/` przez Nginx
   ```

4. **Nginx** (reverse proxy):
   - Proxy `/api/` → `localhost:8000`
   - Serwuj statyczne pliki frontendu
   - SSL przez Certbot (Let's Encrypt)

5. **Baza danych:**
   - SQLite (dla małych instalacji)
   - Lub migracja do PostgreSQL (dla skali)

---

## Pamięć Claude

System wykorzystuje trwałą pamięć w `C:\Users\Acer\.claude\projects\G--M-j-dysk-NowaNadzieja\memory\`.

### Typy pamięci

| Typ | Opis | Kiedy zapisywać |
|------|-------|-------------------|
| user | Informacje o użytkowniku (rola, preferencje) | Gdy poznasz użytkownika |
| feedback | Wskazówki od użytkownika (co robić/nie robić) | Po korekcie lub potwierdzeniu |
| project | Cele, daty, inicjatywy w projekcie | Gdy poznasz kontekst zadania |
| reference | Zewnętrzne systemy (GitHub, Linear, itp.) | Gdy poznasz zewnętrzne zasoby |

### Pliki pamięci

- `MEMORY.md` — indeks wszystkich wpisów (pierwsza linia każdego pliku pamięci)
- Poszczególne pliki `.md` w katalogu pamięci — zawartość w formacie Markdown z frontmatter YAML

---

## Licencja

MIT License — możesz używać, modyfikować i rozprowadzać kod.

---

## Autorzy

- **Matthew** — główny deweloper
- **AI Assistance** — Claude (Anthropic) przez Claude Code

---

## Linki

- Repozytorium GitHub: https://github.com/Matthew19381/language-tutor
- API Docs (lokalnie): http://localhost:8000/docs
- Issue Tracker: https://github.com/Matthew19381/language-tutor/issues
