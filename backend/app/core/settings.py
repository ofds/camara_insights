import logging

# app/core/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional 
class Settings(BaseSettings):
    DATABASE_URL: str
    OPENROUTER_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()