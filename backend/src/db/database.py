"""
Database setup module for the AI Todo Chatbot application.
This module handles database connection, session management, and initialization.
Updated with advanced features support.
"""

from sqlmodel import create_engine, Session, SQLModel
from typing import Generator
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:password@localhost:5432/todo_db"
)

# Create the engine with connection pooling
engine = create_engine(
    DATABASE_URL, 
    echo=False,  # Set to True for SQL debugging
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True  # Enable connection health checks
)


def get_session() -> Generator[Session, None, None]:
    """Get a database session.
    
    Yields:
        Database session object
    """
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_session_sync() -> Session:
    """Get a synchronous database session.
    
    Returns:
        Database session object
    """
    return Session(engine)


def init_db():
    """Initialize the database by creating all tables.
    
    Note: In production, use Alembic migrations instead.
    """
    from src.models import Task, User, Conversation, Message, Tag, TaskTag, Reminder, TaskEvent
    SQLModel.metadata.create_all(engine)


def get_engine():
    """Get the database engine.
    
    Returns:
        SQLAlchemy engine instance
    """
    return engine
