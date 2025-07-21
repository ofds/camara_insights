import logging
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

# Determine the environment and load the corresponding .env file
CI_ENV = os.getenv("CI_ENV", "development")
env_file = f".env.{CI_ENV}"
load_dotenv(dotenv_path=env_file)

logging.info(f"Loading settings from {env_file}")

class Settings(BaseSettings):
    DATABASE_URL: str
    OPENROUTER_API_KEY: Optional[str] = None
    CI_ENV: str = CI_ENV

    model_config = SettingsConfigDict(env_file=env_file, extra="ignore")

settings = Settings()