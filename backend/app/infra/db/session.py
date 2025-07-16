# backend/app/infra/db/session.py
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from app.core.settings import settings
from unidecode import unidecode

engine = create_engine(
    settings.DATABASE_URL,
    # The connect_args are only needed for SQLite
    connect_args={"check_same_thread": False},
)

# This event listener registers the 'unaccent' function for every new SQLite connection.
# It's wrapped in a check to ensure it only runs for SQLite databases.
if "sqlite" in settings.DATABASE_URL:
    @event.listens_for(engine, "connect")
    def connect(dbapi_connection, connection_record):
        """Registers the unaccent function on connection."""
        dbapi_connection.create_function("unaccent", 1, unidecode)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
