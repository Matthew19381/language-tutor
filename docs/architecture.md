# Architektura Systemu LinguaAI

## Przegląd Systemu

LinguaAI to nowoczesna platforma do nauki języków obcych wspomagana przez sztuczną inteligencję. System został zaprojektowany jako aplikacja typu **Single Page Application (SPA)** z architekturą rozdzieloną na frontend i backend komunikujące się przez RESTful API.

### Główne Komponenty

```
┌─────────────────────────────────────────────────────────────┐
│                        Użytkownik                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Frontend (React + Vite)                 │
│  Port: 5173  │  Tailwind CSS  │  React Router v6        │
└─────────────────────────────────────────────────────────────┘
                              │
                     /api, /audio (proxy)
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Backend (FastAPI + Uvicorn)               │
│  Port: 8000  │  SQLAlchemy  │  SQLite/PostgreSQL        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Usługi AI (Google Gemini 2.0 Flash)          │
│  edge-tts (TTS)  │  faster-whisper (STT)  │  fpdf2     │
└─────────────────────────────────────────────────────────────┘
```

## Przepływ Żądań (Request Flow)

Podstawowy przepływ żądań w aplikacji następuje według schematu:

```
┌──────────┐    HTTP Request    ┌──────────┐    Dependency     ┌──────────┐
│ Frontend │ ─────────────────> │  Router  │ ──────────────> │ Service  │
│  (React) │                    │ (FastAPI)│                   │ Layer    │
└──────────┘                    └──────────┘                   └──────────┘
     ▲                                   │                           │
     │         HTTP Response              │                           │
     └───────────────────────────────────┘                           │
                                                                    ▼
                                                         ┌──────────────────┐
                                                         │   SQLAlchemy    │
                                                         │   Session       │
                                                         └──────────────────┘
                                                                    │
                                                                    ▼
                                                         ┌──────────────────┐
                                                         │   Database      │
                                                         │   (SQLite/PG)   │
                                                         └──────────────────┘
```

### Szczegółowy Opis Przepływu

1. **Frontend** wysyła żądanie HTTP do backendu (przez proxy Vite lub bezpośrednio)
2. **Router** (FastAPI) odbiera żądanie, waliduje parametry i wywołuje odpowiednią funkcję
3. **Dependency Injection** dostarcza sesję bazy danych poprzez `get_db`
4. **Service Layer** przetwarza logikę biznesową, komunikując się z bazą i usługami AI
5. **SQLAlchemy Session** wykonuje operacje na bazie danych
6. **Response** wraca do frontendu jako JSON

## Komponenty Backendu

### Routers (Kontrolery API)

Routers definiują endpointy API i obsługują żądania HTTP. Każdy router ma własny prefix API.

```
backend/routers/
├── placement.py        # /api/placement/
├── lessons.py          # /api/lessons/
├── tests.py            # /api/tests/
├── flashcards.py       # /api/flashcards/
├── conversation.py     # /api/conversation/
├── stats.py            # /api/stats/ + /api/tips/
├── quickmode.py        # /api/quickmode/
├── news.py             # /api/news/
├── pronunciation.py     # /api/pronunciation/
├── settings.py         # /api/settings/
├── audio.py            # /api/audio/
├── youtube.py          # /api/youtube/
└── voice_chat.py       # /api/voice-chat/
```

| Router | Prefix API | Odpowiedzialność |
|--------|-----------|-----------------|
| placement.py | `/api/placement/` | Tworzenie użytkownika, 20-pytań test CEFR, plan nauki |
| lessons.py | `/api/lessons/` | Pobieranie/tworzenie lekcji, kompletowanie (+25 XP), audio, PDF |
| tests.py | `/api/tests/` | Testy dzienne/tygodniowe, zapis wyników (deleguje do test_generator) |
| flashcards.py | `/api/flashcards/` | Powtórki metodą spaced repetition, eksport Anki |
| conversation.py | `/api/conversation/` | Sesje rozmów AI i analiza wypowiedzi |
| stats.py | `/api/stats/`, `/api/tips/` | XP/poziomy, osiągnięcia, ranking, porady |
| quickmode.py | `/api/quickmode/` | 15-minutowy plan aktywności dziennej |
| news.py | `/api/news/` | Pobieranie RSS + uproszczenie tekstów przez Gemini |
| pronunciation.py | `/api/pronunciation/` | Transkrypcja faster-whisper + ocena słów |
| settings.py | `/api/settings/` | Ustawienia użytkownika i preferencje |
| audio.py | `/api/audio/` | Generowanie i serwowanie plików audio (edge-tts) |
| youtube.py | `/api/youtube/` | Integracja z filmami YouTube do nauki |
| voice_chat.py | `/api/voice-chat/` | Rozmowy głosowe z AI w czasie rzeczywistym |

### Services (Warstwa Logiki Biznesowej)

```
backend/services/
├── gemini_service.py         # Komunikacja z Google Gemini 2.0 Flash
├── lesson_generator.py        # Logika generowania lekcji (prompty AI)
├── test_generator.py         # Tworzenie i ocena testów
├── achievement_service.py     # System XP, poziomów i osiągnięć
├── audio_service.py          # Generowanie audio (edge-tts)
├── pdf_service.py            # Generowanie PDF (fpdf2)
├── news_service.py          # Pobieranie i przetwarzanie RSS
├── pronunciation_service.py  # Transkrypcja (faster-whisper)
├── anki_service.py          # Eksport do formatu Anki
├── google_drive_service.py  # Backup na Google Drive
└── model_router.py          # Routing modeli AI (przyszłościowe)
```

#### gemini_service.py

Główny punkt kontaktu z AI. Zawiera tylko dwie funkcje:

- `generate_json(prompt)` - dodaje "Respond ONLY with valid JSON" i usuwa markdown przed parsowaniem
- `generate_text(prompt)` - zwraca surowy string odpowiedzi

Każda funkcja wywołująca Gemini ma wkodowany fallback (słownik/string), aby aplikacja działała poprawnie przy braku API.

#### lesson_generator.py

Zawiera całą logikę promptów AI:
- Test poziomujący
- Plan nauki
- Lekcja dzienna
- Testy dzienne/tygodniowe
- Rozmowy
- Porady

Funkcja `generate_daily_lesson()` akceptuje `recent_topics` (lista tematów z ostatnich 7 dni), aby tworzyć sekcję `interleaved_review`.

#### achievement_service.py

Zarządza całą matematyką XP i poziomów:
- `calculate_level_from_xp(xp)` - 50 poziomów, krzywa kwadratowa: poziom `n` wymaga `(n-1)² × 20` XP
- `check_and_award_achievements(user, db)` - wywołaj po każdej akcji przyznającej XP; zwraca listę nowo odblokowanych osiągnięć
- `get_unnotified_achievements(user_id, db)` - zwraca niepowiadomione osiągnięcia i oznacza je jako powiadomione

### Models (Modele Danych SQLAlchemy)

```
backend/models/
├── user.py           # User - użytkownik
├── lesson.py         # Lesson - lekcja (content jako JSON blob)
├── test_result.py    # TestResult - wynik testu
├── flashcard.py      # Flashcard - fiszka
├── study_plan.py     # StudyPlan - plan nauki
└── achievement.py    # Achievement - osiągnięcie
```

#### Diagram Relacji Bazy Danych

```
┌────────────────┐
│     User      │
├────────────────┤
│ id (PK)       │
│ username      │
│ xp            │
│ level         │
│ created_at    │
└───────┬────────┘
        │
        │ 1:N
        │
┌───────┴────────┐      ┌────────────────┐      ┌────────────────┐
│    Lesson       │      │  TestResult    │      │   Flashcard    │
├────────────────┤      ├────────────────┤      ├────────────────┤
│ id (PK)        │      │ id (PK)        │      │ id (PK)        │
│ user_id (FK)   │      │ user_id (FK)   │      │ user_id (FK)   │
│ content (JSON)  │      │ score          │      │ front/back     │
│ completed      │      │ total_questions │      │ next_review    │
│ created_at     │      │ created_at      │      │ interval       │
└────────────────┘      └────────────────┘      └────────────────┘

┌────────────────┐      ┌────────────────┐
│  StudyPlan     │      │ Achievement    │
├────────────────┤      ├────────────────┤
│ id (PK)        │      │ id (PK)        │
│ user_id (FK)   │      │ user_id (FK)   │
│ topics []      │      │ type           │
│ created_at     │      │ notified       │
└────────────────┘      │ unlocked_at    │
                        └────────────────┘
```

**Przechowywanie treści lekcji**: `Lesson.content` to JSON blob (kolumna Text SQLAlchemy). Wszystkie sekcje lekcji - w tym nowsze (`comprehensible_input`, `interleaved_review`, `output_forcing`) - żyją wewnątrz tego bloba. Nie jest potrzebna migracja przy dodawaniu nowych sekcji; frontend sprawdza ich obecność przed renderowaniem.

## Komponenty Frontendu

### Pages (Strony)

```
frontend/src/pages/
├── Home.jsx                # Strona główna
├── PlacementTest.jsx        # Test poziomujący CEFR
├── DailyLesson.jsx          # Lekcja dzienna
├── DailyTest.jsx            # Test dzienny
├── Flashcards.jsx           # Fiszki (spaced repetition)
├── Conversation.jsx         # Rozmowa z AI
├── Stats.jsx                # Statystyki i osiągnięcia
├── QuickMode.jsx            # Szybki tryb (15 min)
├── News.jsx                 # Wiadomości (i+1)
├── PronunciationTrainer.jsx # Trener wymowy
├── LessonHistory.jsx        # Historia lekcji
├── Videos.jsx               # Filmy YouTube
└── ErrorReview.jsx          # Powtórka błędów
```

### Components (Komponenty Wielokrotnego Użytku)

```
frontend/src/components/
├── Layout.jsx              # Główny layout (toasty osiągnięć)
├── NavBar.jsx              # Pasek nawigacyjny
├── LoadingSpinner.jsx      # Wskaźnik ładowania
├── NotificationManager.jsx # Zarządzanie powiadomieniami
├── PlayButton.jsx          # Przycisk odtwarzania audio
└── OutputForcingCard.jsx   # Karta output forcing
```

### API Client (`frontend/src/api/client.js`)

Wszystkie wywołania API przechodzą przez ten plik. Instancja `api` (Axios) ma interceptor odpowiedzi, który rozpakowuje `response.data`.

**Wyjątek**: Eksport PDF (`exportLessonPDF`) i analiza wymowy używają surowego `axios` bezpośrednio, aby wspierać `responseType: 'blob'` i `multipart/form-data`.

### State Management

Brak globalnego menedżera stanu. Każda strona pobiera własne dane przy montowaniu. `userId` jest przechowywane w `localStorage` i odczytywane przez `getUserId()` z `client.js`.

### Layout.jsx

Wywołuje `getStats(userId)` przy montowaniu. Wszelkie `new_achievements` w odpowiedzi są renderowane jako automatycznie znikające toasty (4 s). W ten sposób backendowy flag `notified` na osiągnięciach steruje frontendowymi toastami.

## Baza Danych

### SQLite (Development)

Domyślna baza danych używana podczas rozwoju. Plik `lingua_ai.db` jest tworzony automatycznie w `backend/` przy pierwszym uruchomieniu poprzez `Base.metadata.create_all()` w handlerze lifespan w `main.py`.

### PostgreSQL (Production-Ready)

System jest zaprojektowany do łatwej migracji na PostgreSQL w produkcji. Wystarczy zmienić连接字符串 w `backend/.env`.

```
┌─────────────────────────────────────────────────────────────┐
│                    Database Layer                           │
├─────────────────────────────────────────────────────────────┤
│  Development: SQLite (lingua_ai.db)                      │
│  Production:  PostgreSQL (elephantsql.com / supabase)     │
├─────────────────────────────────────────────────────────────┤
│  ORM: SQLAlchemy                                         │
│  Migrations: Automatyczne (create_all) / Alembic (prod)  │
└─────────────────────────────────────────────────────────────┘
```

## Usługi AI

### Google Gemini 2.0 Flash

Główny model AI używany poprzez OpenRouter.

**Konfiguracja**: `backend/.env`
```
GEMINI_API_KEY=your_api_key_here
```

**Model**: `gemini-2.0-flash`

### Text-to-Speech: edge-tts

Używany do generowania audio dla lekcji i słówek. Szybki i darmowy, oparty na Edge browser TTS.

### Speech-to-Text: faster-whisper

Model `tiny` (~75 MB, CPU, int8 quantization) używany w `pronunciation_service.py` do transkrypcji wypowiedzi użytkownika.

### PDF Generation: fpdf2

Generowanie eksportów lekcji do PDF.

## Diagram Pełnego系统u

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           LinguaAI System                                │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────┐         ┌──────────────────┐         ┌───────────┐ │
│  │   Frontend       │         │    Backend       │         │  AI APIs   │ │
│  │                  │         │                  │         │            │ │
│  │ React 18         │◄───────│ FastAPI         │◄───────│ Gemini 2.0 │ │
│  │ Vite             │ HTTP    │ SQLAlchemy      │  JSON   │ Flash      │ │
│  │ Tailwind CSS     │         │ SQLite/PostgreSQL│         │            │ │
│  │ React Router     │         │                  │         └───────────┘ │
│  │ Axios            │         │ Services:        │         ┌───────────┐ │
│  └──────────────────┘         │ - gemini        │◄───────│ edge-tts  │ │
│                              │ - lesson_gen    │         │ (TTS)     │ │
│                              │ - achievement   │         └───────────┘ │
│                              │ - pronunciation  │         ┌───────────┐ │
│                              └──────────────────┘◄───────│ faster-   │ │
│                                                        │ whisper    │ │
│                                                        │ (STT)      │ │
│                                                        └───────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Kluczowe Stałe

| Stała | Wartość | Lokalizacja |
|--------|---------|------------|
| XP za lekcję | +25 | `routers/lessons.py` |
| XP za test | `score × 0.5` (max 50) | `services/test_generator.py` |
| Krzywa poziomu | `(n-1)² × 20` XP, 50 poziomów | `services/achievement_service.py` |
| Model Gemini | `gemini-2.0-flash` | `services/gemini_service.py` |
| Model Whisper | `tiny` (~75 MB, CPU, int8) | `services/pronunciation_service.py` |
| Timeout API (frontend) | 60 s | `api/client.js` |

## Dodawanie Nowych Komponentów

### Nowy Router

1. Utwórz plik w `backend/routers/`
2. Zaimportuj go w `main.py` i wywołaj `app.include_router(...)`

### Nowy Model SQLAlchemy

1. Utwórz plik w `backend/models/`
2. Zaimportuj go wewnątrz bloku lifespan w `main.py` (obok istniejącego importu `achievement`), aby zarejestrował się w `Base` przed uruchomieniem `create_all`

### Nowa Strona Frontend

1. Utwórz plik w `frontend/src/pages/`
2. Dodaj routing w `frontend/src/App.jsx`
3. Jeśli potrzebne, dodaj link w `NavBar.jsx`

## Git - Zasady Commitów

Zawsze pushuj do GitHub po każdej znaczącej zmianie. Nie pozwalaj pracy gromadzić się w niezapisanym stanie lokalnym. Commituj i pushuj natychmiast po:
- Utworzeniu nowego pliku (router, service, component, page)
- Naprawieniu buga
- Ukończeniu (nawet częściowym) funkcjonalności
- Refaktoryzacji
- Aktualizacji CLAUDE.md
