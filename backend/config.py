from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GEMINI_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434/v1"
    OLLAMA_MODEL: str = "qwen2.5:7b"
    DATABASE_URL: str = "sqlite:///./LinguaAI.db"
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
