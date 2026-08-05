from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    APP_NAME: str = "BATIP"
    APP_VERSION: str = "0.1.0"

    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000

    DEBUG: bool = True

    DATABASE_URL: str = "sqlite:///batip.db"

    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()