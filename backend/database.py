"""
backend/database.py - SQLite Database Configuration with SQLAlchemy
Provides the engine, sessionmaker, and Base model for the application.
Configures SQLite to enforce foreign key constraints.
"""

import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

# Path to the single-file SQLite database
DATABASE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "transport.db")
DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

# create_engine for SQLite:
# - check_same_thread=False allows FastAPI multi-threaded request handling to share the engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Enable Foreign Key enforcement in SQLite (disabled by default in SQLite)
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Session factory for generating scoped database sessions per request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy ORM models
Base = declarative_base()

def get_db():
    """
    FastAPI dependency that provides an isolated SQLAlchemy session per request
    and ensures the session is closed cleanly when the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
