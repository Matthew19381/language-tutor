from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GEMINI_API_KEY: str
    DATABASE_URL: str = "sqlite:///./language_tutor.db"
    SECRET_KEY: str = "changeme"
    TARGET_LANGUAGE: str = "German"
    NATIVE_LANGUAGE: str = "Polish"

    class Config:
        env_file = ".env"


settings = Settings()
