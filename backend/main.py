import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from backend.database import engine, Base
from backend.routers import placement, lessons, tests, flashcards, conversation, stats
from backend.routers import quickmode, news, pronunciation, settings, audio, youtube

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create database tables and required directories
    logger.info("Creating database tables...")
    # Import all models so SQLAlchemy registers them before create_all
    from backend.models import achievement, user, lesson, test_result, study_plan, flashcard  # noqa
    Base.metadata.create_all(bind=engine)

    _sa = __import__('sqlalchemy')
    # SQLite migrations — add missing columns safely
    _migrations = [
        ("users", "ALTER TABLE users ADD COLUMN language_profiles TEXT DEFAULT '{}'"),
        ("flashcards", "ALTER TABLE flashcards ADD COLUMN lesson_id INTEGER"),
        ("flashcards", "ALTER TABLE flashcards ADD COLUMN lesson_day INTEGER"),
        ("flashcards", "ALTER TABLE flashcards ADD COLUMN lesson_topic TEXT"),
    ]
    with engine.connect() as conn:
        for table, sql in _migrations:
            try:
                conn.execute(_sa.text(sql))
                conn.commit()
            except Exception:
                pass  # Column already exists

    # Ensure audio and exports directories exist
    audio_dir = os.path.join(os.path.dirname(__file__), "audio")
    exports_dir = os.path.join(os.path.dirname(__file__), "exports")
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(exports_dir, exist_ok=True)

    logger.info("LinguaAI API started successfully!")
    yield
    # Shutdown
    logger.info("LinguaAI API shutting down...")


app = FastAPI(
    title="LinguaAI API",
    description="AI-powered language learning application using Google Gemini",
    version="1.0.0",
    lifespan=lifespan
)

# CORS - restrict to trusted origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Development frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(placement.router, tags=["Placement"])
app.include_router(lessons.router, tags=["Lessons"])
app.include_router(tests.router, tags=["Tests"])
app.include_router(flashcards.router, tags=["Flashcards"])
app.include_router(conversation.router, tags=["Conversation"])
app.include_router(stats.router, tags=["Stats"])
app.include_router(quickmode.router, tags=["QuickMode"])
app.include_router(news.router, tags=["News"])
app.include_router(pronunciation.router, tags=["Pronunciation"])
app.include_router(settings.router, tags=["Settings"])
app.include_router(audio.router, tags=["Audio"])
app.include_router(youtube.router, tags=["YouTube"])

# Serve audio files
audio_dir = os.path.join(os.path.dirname(__file__), "audio")
os.makedirs(audio_dir, exist_ok=True)
app.mount("/audio", StaticFiles(directory=audio_dir), name="audio")

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "LinguaAI API",
        "version": "1.0.0"
    }

# Serve simple frontend (no Vite, just static files)
# Use relative path to avoid Unicode issues in absolute paths
frontend_simple_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend-simple"))
if os.path.exists(frontend_simple_dir):
    app.mount("/static", StaticFiles(directory=frontend_simple_dir), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_frontend():
        return FileResponse(os.path.join(frontend_simple_dir, "index.html"))

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        # Don't catch API routes
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404)
        index_path = os.path.join(frontend_simple_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        raise HTTPException(status_code=404)
