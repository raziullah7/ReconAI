from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import load_settings


def get_engine(database_url: str) -> Engine:
    """Create the SQLAlchemy engine for local PostgreSQL access.

    What: Builds the synchronous engine used by migrations, tests, and
        repository sessions.
    Why: Milestone 1 needs one explicit DB boundary before persistence code can
        be tested.

    Args:
        database_url: PostgreSQL connection URL from validated settings.

    Returns:
        Engine: Configured SQLAlchemy engine.
    """
    return create_engine(database_url, pool_pre_ping=True)


def get_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create the session factory used by repositories.

    What: Binds SQLAlchemy sessions to the configured engine.
    Why: Repositories need injected sessions instead of reading global state.

    Args:
        engine: SQLAlchemy engine created from settings.

    Returns:
        sessionmaker[Session]: Factory that creates synchronous sessions.
    """
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@lru_cache
def _get_cached_engine(database_url: str) -> Engine:
    return get_engine(database_url)


def get_session() -> Iterator[Session]:
    """Yield one request-scoped database session.

    What: Loads settings, creates or reuses the cached engine/session factory,
        then opens, yields, commits, rolls back on error, and closes one
        SQLAlchemy session.
    Why: Later API routes need a FastAPI dependency with predictable cleanup.

    Yields:
        Session: Active database session.

    States / Side Effects:
        Opens and closes a database connection.
    """
    settings = load_settings()
    engine = _get_cached_engine(settings.database_url)
    session_factory = get_session_factory(engine)
    session = session_factory()

    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
