import os
import logging
from fastapi import FastAPI
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
    from backend.models import achievement  # noqa
    Base.metadata.create_all(bind=engine)

    # Add language_profiles column to users table if missing (SQLite migration)
    try:
        with engine.connect() as conn:
            conn.execute(__import__('sqlalchemy').text(
                "ALTER TABLE users ADD COLUMN language_profiles TEXT DEFAULT '{}'"
            ))
            conn.commit()
            logger.info("Added language_profiles column to users table")
    except Exception:
        pass  # Column already exists

    # Ensure audio and exports directories exist
    audio_dir = os.path.join(os.path.dirname(__file__), "audio")
    exports_dir = os.path.join(os.path.dirname(__file__), "exports")
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(exports_dir, exist_ok=True)

    logger.info("Language Tutor API started successfully!")
    yield
    # Shutdown
    logger.info("Language Tutor API shutting down...")


app = FastAPI(
    title="Language Tutor API",
    description="AI-powered language learning application using Google Gemini",
    version="1.0.0",
    lifespan=lifespan
)

# CORS - allow all origins for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

# Serve frontend in production (if dist exists)
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/", include_in_schema=False)
    async def serve_frontend():
        return FileResponse(os.path.join(frontend_dist, "index.html"))

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        # Don't catch API routes
        if full_path.startswith("api/"):
            from fastapi import HTTPException
            raise HTTPException(status_code=404)
        index_path = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        from fastapi import HTTPException
        raise HTTPException(status_code=404)


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Language Tutor API",
        "version": "1.0.0"
    }
