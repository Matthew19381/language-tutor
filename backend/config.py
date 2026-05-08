from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    GEMINI_API_KEY: str = ""
    AI_PROVIDER: str = "openrouter"  # "gemini" for direct API, "openrouter" for OpenRouter
    GEMINI_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta"
    DATABASE_URL: str = "sqlite:///./lingua_ai.db"
    SECRET_KEY: str = ""  # Must be set in .env file
    TARGET_LANGUAGE: str = "German"
    NATIVE_LANGUAGE: str = "Polish"
    DISCORD_WEBHOOK_URL: str = ""
    NOTIFY_LESSON_HOUR: int = 8
    NOTIFY_REVIEW_HOUR: int = 18
    GDRIVE_FOLDER_ID: str = ""
    GDRIVE_CLIENT_SECRETS_FILE: str = "backend/gdrive_credentials.json"
    YOUTUBE_API_KEY: str = ""

    class Config:
        env_file = "backend/.env"
        extra = "ignore"


settings = Settings()
