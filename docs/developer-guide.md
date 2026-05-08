# Przewodnik Dewelopera LinguaAI

## Wstęp

Ten przewodnik opisuje proces konfiguracji środowiska programistycznego, strukturę projektu oraz najlepsze praktyki podczas pracy z kodem LinguaAI.

## Konfiguracja Środowiska

### Wymagania Systemowe

- **Python**: 3.10+ (zalecane 3.11)
- **Node.js**: 18+ (zalecane 20 LTS)
- **npm**: 9+ (dostarczane z Node.js)
- **Git**: najnowsza stabilna wersja
- **SQLite**: (wbudowane w Pythona/SQLAlchemy)
- **System operacyjny**: Windows 10/11, Linux, macOS

### 1. Klonowanie Repozytorium

```bash
git clone https://github.com/twoj-uzytkownik/lingua-ai.git
cd lingua-ai
```

### 2. Konfiguracja Backendu (Python/FastAPI)

#### Tworzenie środowiska wirtualnego:

```bash
# Windows (CMD)
cd backend
python -m venv venv
venv\Scripts\activate

# Windows (PowerShell)
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux/macOS
cd backend
python3 -m venv venv
source venv/bin/activate
```

#### Instalacja zależności:

```bash
pip install -r requirements.txt
```

**Kluczowe pakiety** (requirements.txt):
```
fastapi==0.110.0
uvicorn==0.27.0
sqlalchemy==2.0.25
pydantic==2.5.0
google-generativeai==0.3.0
edge-tts==6.1.9
fpdf2==2.7.0
feedparser==6.0.10
faster-whisper==0.10.0
python-dotenv==1.0.0
```

#### Konfiguracja zmiennych środowiskowych:

Skopiuj `backend/.env.example` do `backend/.env`:

```bash
cp backend/.env.example backend/.env
```

Edytuj `backend/.env`:
```env
GEMINI_API_KEY=twoj_klucz_api_openrouter
DATABASE_URL=sqlite:///./lingua_ai.db
ENVIRONMENT=development
DEBUG=true
```

**Uzyskanie klucza GEMINI_API_KEY**:
1. Wejdź na https://openrouter.ai/
2. Zarejestruj się i utwórz klucz API
3. Skopiuj klucz do pliku `.env`

### 3. Konfiguracja Frontendu (React/Vite)

```bash
cd frontend
npm install
```

**Kluczowe pakiety** (package.json):
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-router-dom": "^6.22.0",
    "axios": "^1.6.0",
    "tailwindcss": "^3.4.0",
    "lucide-react": "^0.303.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.0",
    "vite": "^5.0.0"
  }
}
```

### 4. Uruchomienie Aplikacji

#### Metoda 1: Skrypt automatyczny (Windows)

```bash
# Uruchamia backend i frontend w osobnych oknach
start.bat    # CMD
.\start.ps1   # PowerShell
```

#### Metoda 2: Ręczne uruchomienie

**Terminal 1 (Backend)** - z katalogu głównego `lingua-ai/`:
```bash
uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 (Frontend)** - z katalogu `frontend/`:
```bash
cd frontend
npm run dev
```

**Ważne**: Backend musi być uruchomiony z katalogu głównego (`lingua-ai/`), a nie z `backend/` - w przeciwnym razie importy `backend.*` nie zadziałają.

### 5. Weryfikacja Instalacji

- **Frontend**: http://localhost:5173
- **Backend API Docs**: http://localhost:8000/docs (Swagger UI)
- **Backend ReDoc**: http://localhost:8000/redoc

---

## Struktura Projektu

```
lingua-ai/
├── backend/
│   ├── main.py                 # Punkt wejścia FastAPI, lifespan handler
│   ├── .env                    # Zmienne środowiskowe (gitignored)
│   ├── .env.example            # Przykładowy plik env
│   ├── lingua_ai.db            # Baza SQLite (gitignored)
│   ├── audio/                  # Wygenerowane pliki audio (gitignored)
│   ├── exports/                # Wyeksportowane PDF (gitignored)
│   ├── models/                 # Modele SQLAlchemy
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── lesson.py
│   │   ├── test_result.py
│   │   ├── flashcard.py
│   │   ├── study_plan.py
│   │   └── achievement.py
│   ├── routers/                # Endpointy API (FastAPI routers)
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
│   └── services/               # Logika biznesowa
│       ├── __init__.py
│       ├── gemini_service.py    # Komunikacja z Gemini AI
│       ├── lesson_generator.py   # Generowanie lekcji (prompty)
│       ├── test_generator.py     # Logika testów
│       ├── achievement_service.py # System XP i poziomów
│       ├── audio_service.py      # Generowanie audio (edge-tts)
│       ├── pdf_service.py        # Generowanie PDF (fpdf2)
│       ├── news_service.py       # Pobieranie i przetwarzanie RSS
│       ├── pronunciation_service.py # Transkrypcja (faster-whisper)
│       ├── anki_service.py       # Eksport do Anki
│       ├── google_drive_service.py # Backup na Google Drive
│       └── model_router.py     # Routing modeli AI
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── api/
│   │   │   └── client.js       # Axios client + interceptors
│   │   ├── components/          # Komponenty wielokrotnego użytku
│   │   │   ├── Layout.jsx
│   │   │   ├── NavBar.jsx
│   │   │   ├── LoadingSpinner.jsx
│   │   │   ├── NotificationManager.jsx
│   │   │   ├── PlayButton.jsx
│   │   │   └── OutputForcingCard.jsx
│   │   ├── pages/               # Strony aplikacji
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
│   │   ├── App.jsx              # Główny komponent z routingiem
│   │   ├── main.jsx             # Punkt wejścia React
│   │   └── index.css            # Główne style (Tailwind)
│   ├── vite.config.js           # Konfiguracja Vite + proxy
│   ├── tailwind.config.js       # Konfiguracja Tailwind CSS
│   ├── postcss.config.js        # Konfiguracja PostCSS
│   └── package.json
├── start.bat                    # Skrypt startowy (Windows CMD)
├── start.ps1                    # Skrypt startowy (PowerShell)
├── CLAUDE.md                   # Instrukcje dla Claude Code
├── .gitignore
└── README.md
```

---

## Dodawanie Nowych Komponentów

### Dodawanie Nowego Routera (Backend)

1. **Utwórz plik w `backend/routers/`**:

```python
# backend/routers/nowy_router.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db

router = APIRouter(prefix="/api/nowy", tags=["nowy"])

@router.get("/example")
def example_endpoint(db: Session = Depends(get_db)):
    return {"message": "Nowy endpoint"}
```

2. **Zaimportuj i zarejestruj w `backend/main.py`**:

```python
# backend/main.py
from backend.routers import nowy_router

app.include_router(nowy_router.router)
```

### Dodawanie Nowego Modelu SQLAlchemy

1. **Utwórz plik w `backend/models/`**:

```python
# backend/models/nowy_model.py
from sqlalchemy import Column, Integer, String, ForeignKey
from backend.database import Base

class NowyModel(Base):
    __tablename__ = "nowy_model"
    
    id = Column(Integer, primary_key=True, index=True)
    nazwa = Column(String)
```

2. **Zaimportuj w bloku lifespan w `main.py`** (obok istniejących importów):

```python
# backend/main.py
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Import models so they register with Base
    from backend.models.user import User
    from backend.models.lesson import Lesson
    from backend.models.achievement import Achievement
    from backend.models.nowy_model import NowyModel  # NOWY IMPORT
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
```

### Dodawanie Nowej Strony (Frontend)

1. **Utwórz plik w `frontend/src/pages/`**:

```jsx
// frontend/src/pages/NowaStrona.jsx
import React from 'react';

const NowaStrona = () => {
  return (
    <div>
      <h1>Nowa Strona</h1>
    </div>
  );
};

export default NowaStrona;
```

2. **Dodaj routing w `frontend/src/App.jsx`**:

```jsx
import NowaStrona from './pages/NowaStrona';

function App() {
  return (
    <Routes>
      {/* ... inne trasy ... */}
      <Route path="/nowa-strona" element={<NowaStrona />} />
    </Routes>
  );
}
```

3. **(Opcjonalnie) Dodaj link w `NavBar.jsx`**

---

## Testowanie

### Backend Tests (pytest)

Projekt zawiera **127 testów** pokrywających backend.

#### Uruchamianie testów:

```bash
cd backend
python -m pytest
```

#### Uruchamianie z pokryciem (coverage):

```bash
python -m pytest --cov=backend --cov-report=html
```

#### Struktura testów:

```
backend/tests/
├── test_placement.py
├── test_lessons.py
├── test_tests.py
├── test_flashcards.py
├── test_conversation.py
├── test_stats.py
└── test_achievements.py
```

### Frontend Tests

```bash
cd frontend
npm test          # Jest + React Testing Library
npm run test:coverage  # Z raportem pokrycia
```

---

## Style Kodowania

### Python (Backend)

- **Formatter**: Black (zalecany)
- **Linter**: Flake8 / Pylint
- **Konwencja nazewnicza**: snake_case dla funkcji i zmiennych, PascalCase dla klas

```python
# DOBRZE
def calculate_user_xp(user_id: int) -> int:
    pass

class UserAchievement(Base):
    pass

# ŹLE
def CalculateUserXP(userID):
    pass
```

### JavaScript/React (Frontend)

- **Formatter**: Prettier
- **Linter**: ESLint
- **Konwencja nazewnicza**: camelCase dla zmiennych/funkcji, PascalCase dla komponentów

```jsx
// DOBRZE
const DailyLesson = () => {
  const [lessonData, setLessonData] = useState(null);
  return <div>{/* ... */}</div>;
};

// ŹLE
const daily_lesson = () => {
  const [lesson_data, set_lesson_data] = useState(null);
};
```

---

## Korzystanie z Usług AI

### gemini_service.py - Główne funkcje:

```python
from backend.services.gemini_service import generate_json, generate_text

# Generowanie JSON (dodaje "Respond ONLY with valid JSON")
response = generate_json("Wygeneruj lekcję o Present Perfect")

# Generowanie tekstu (surowa odpowiedź)
text = generate_text("Napisz przykłady użycia...")
```

### Obsługa błędów (Fallback):

Każda funkcja wywołująca Gemini ma wkodowany fallback:

```python
def generate_lesson(topic: str) -> dict:
    try:
        return generate_json(f"Generate lesson about {topic}")
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        # Fallback - zwróć domyślną strukturę
        return {
            "title": f"Lesson: {topic}",
            "vocabulary": [],
            "grammar": {"topic": topic, "explanation": "..."}
        }
```

---

## Migracje Bazy Danych

### Development (SQLite)

Baza jest tworzona automatycznie przez `Base.metadata.create_all()` w handlerze lifespan.

### Production (PostgreSQL + Alembic)

W produkcji zaleca się użycie **Alembic** do zarządzania migracjami:

```bash
pip install alembic
alembic init migrations
```

Konfiguracja `migrations/env.py`:
```python
from backend.database import Base
from backend.models import *  # Import wszystkich modeli

target_metadata = Base.metadata
```

Tworzenie migracji:
```bash
alembic revision --autogenerate -m "Add new column"
alembic upgrade head
```

---

## Git - Dobre Praktyki

### Kiedy commitować i pushować?

**Zawsze pushuj do GitHub po każdej znaczącej zmianie:**

- Utworzenie nowego pliku (router, service, komponent, strona)
- Naprawienie błędu
- Ukończenie (nawet częściowe) funkcjonalności
- Refaktoryzacja kodu
- Aktualizacja dokumentacji
- Przed zakończeniem sesji pracy

### Format wiadomości commit:

```
<typ>: <co zmieniono i dlaczego>

- Szczegół 1 (który plik, co dokładnie)
- Szczegół 2
- Szczegół 3 (jeśli istotne)
```

**Typy**: `feat` (nowa funkcja), `fix` (poprawka), `refactor`, `style`, `docs`, `chore`

**Dobre przykłady**:
```
feat: add PDF export endpoint for lessons

- backend/routers/lessons.py: GET /api/lessons/{id}/export-pdf
- backend/services/pdf_service.py: fpdf2-based generator
- frontend/src/pages/DailyLesson.jsx: Download PDF button
```

```
fix: correct uvicorn launch path in start.bat

- Before: cd backend && uvicorn main:app
- Now: uvicorn backend.main:app (run from project root)
- Fixes ImportError on relative backend.* imports
```

### Komendy Git:

```bash
# Sprawdź co zostanie zcommitowane
git status
git diff --staged

# Commit i push
git add -A
git commit -m "feat: description

- file.py: what changed
- component.jsx: what changed"
git push
```

**Pliki gitignorowane** (nigdy nie będą commitowane):
- `backend/.env`
- `*.db`
- `backend/audio/`
- `backend/exports/`
- `frontend/dist/`

---

## Deployment - Podstawy

Podstawowe informacje o wdrożeniu znajdują się w pliku `deployment.md`. Kluczowe kroki:

1. Konfiguracja serwera Linux VPS
2. Migracja z SQLite na PostgreSQL
3. Konfiguracja systemd dla backendu
4. Build frontendu i serwowanie przez Nginx
5. Konfiguracja reverse proxy z SSL (Let's Encrypt)

---

## Debugowanie

### Backend - Uruchamianie z logami:

```bash
uvicorn backend.main:app --reload --log-level debug
```

### Frontend - DevTools:

- Otwórz narzędzia deweloperskie w przeglądarce (F12)
- Sprawdź zakładkę Console dla błędów JavaScript
- Sprawdź zakładkę Network dla zapytań API

### Częste problemy:

| Problem | Rozwiązanie |
|---------|--------------|
| `ImportError: attempted relative import beyond top-level package` | Uruchom backend z katalogu głównego: `uvicorn backend.main:app` |
| `ModuleNotFoundError: No module named 'backend'` | Sprawdź czy jesteś w katalogu `lingua-ai/` |
| Błąd połączenia z Gemini API | Sprawdź klucz API w `backend/.env` |
| Frontend nie widzi API | Sprawdź czy backend działa na porcie 8000, sprawdź proxy w `vite.config.js` |

---

## Zasoby Pomocnicze

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Vite Guide](https://vitejs.dev/guide/)
