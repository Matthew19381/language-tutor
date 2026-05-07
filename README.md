# LinguaAI - Language Learning Platform

AI-powered language learning platform with personalized lessons, spaced repetition flashcards, and conversation practice.

## Features

- **CEFR Placement Test** - 20-question diagnostic test to determine your level (A1-C2)
- **Daily Lessons** - AI-generated lessons with vocabulary, grammar, and reading
- **Spaced Repetition** - SM-2 algorithm for long-term vocabulary retention
- **AI Conversation** - Practice speaking with AI conversation partner
- **Multiple Languages** - Learn German, English, Spanish, Russian, Chinese simultaneously
- **Progress Tracking** - XP system with 50 levels, achievements, leaderboard
- **News Reading** - Simplified articles based on your CEFR level

## Tech Stack

**Backend:** FastAPI · SQLAlchemy · Google Gemini 2.0 Flash · edge-tts · faster-whisper  
**Frontend:** React 18 · Vite · Tailwind CSS · Axios  
**Database:** SQLite (dev) / PostgreSQL (prod ready)

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Google Gemini API key

### Backend Setup
```bash
cd backend
copy .env.example .env
# Edit .env and set GEMINI_API_KEY

# Install dependencies
pip install -r requirements.txt

# Run server (from project root)
uvicorn backend.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install

# Run dev server
npm run dev
```

### Access
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Project Structure

```
LinguaAI/
├── backend/
│   ├── models/          # SQLAlchemy models
│   ├── routers/         # FastAPI route handlers
│   ├── services/        # Business logic + AI integration
│   ├── schemas/         # Pydantic request/response models
│   └── scripts/         # DB backup, utilities
├── frontend/src/
│   ├── pages/          # React page components
│   ├── components/     # Reusable UI components
│   └── api/            # Axios client + API calls
└── docs/               # Documentation
```

## Testing

```bash
# Backend tests (78 tests)
cd LinguaAI
python -m pytest backend/tests/ -v

# Frontend E2E (Playwright)
cd frontend
npx playwright test
```

## Documentation

- **User Guide** - See [USER_GUIDE.md](USER_GUIDE.md)
- **Backup Instructions** - See [BACKUP_INSTRUCTIONS.md](BACKUP_INSTRUCTIONS.md)
- **API Docs** - Available at `/docs` when backend is running

## License

MIT
