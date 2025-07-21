import logging
from dotenv import load_dotenv

# app/core/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str
    OPENROUTER_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()