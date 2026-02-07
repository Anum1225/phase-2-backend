"""
Database connection and session management for Task API Backend.

Implements connection pooling for performance and provides session dependency
for dependency injection in FastAPI endpoints.
"""

from typing import Generator
from sqlmodel import Session, create_engine
from sqlalchemy.pool import QueuePool

from .config import settings


# Create database engine with connection pooling
# pool_size: Number of permanent connections (default: 5)
# max_overflow: Maximum additional connections beyond pool_size (default: 10)
# pool_pre_ping: Test connection health before using (prevents stale connections)
# echo: Log all SQL statements (set to True for debugging)
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    echo=False,  # Set to True to see SQL queries in logs
)


def get_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides database session.

    Usage in endpoints:
        @app.get("/endpoint")
        def endpoint(session: Session = Depends(get_session)):
            # Use session for database operations
            pass

    The session is automatically committed on success and rolled back on error.
    Connection is returned to pool after request completes.

    Yields:
        Session: SQLModel database session
    """
    with Session(engine) as session:
        try:
            yield session
            # Commit is automatic on successful yield completion
        except Exception:
            # Rollback on any exception
            session.rollback()
            raise
        finally:
            # Session cleanup handled by context manager
            pass


def init_db() -> None:
    """
    Initialize database tables.

    Note: In production, use explicit SQL migrations instead of this method.
    This is provided for development/testing convenience only.

    Usage:
        from src.core.database import init_db
        from src.models.user import User
        from src.models.task import Task

        # Import all models first, then call init_db()
        init_db()
    """
    from sqlmodel import SQLModel

    # Create all tables defined in SQLModel models
    SQLModel.metadata.create_all(engine)


def close_db() -> None:
    """
    Close database connections and dispose of engine.

    Call this on application shutdown to gracefully close all connections.

    Usage:
        @app.on_event("shutdown")
        def shutdown():
            close_db()
    """
    engine.dispose()
