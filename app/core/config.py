from functools import lru_cache

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/intellimeeter"
    )
    debug: bool = False

    secret_key: str = "secret-key-keep-it-hidden"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    openai_api_key: str = "openai api key"
    
    discord_webhook_url: str = "webhook url"

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE) if ENV_FILE.exists() else ".env",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    return settings
