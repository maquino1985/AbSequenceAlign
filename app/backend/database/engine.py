"""
SQLAlchemy async engine setup for AbSequenceAlign.
Provides async database engine and session management.
"""

from typing import Optional, AsyncGenerator
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.pool import NullPool

from .config import get_database_url, get_engine_kwargs


class DatabaseEngine:
    """Database engine manager for async SQLAlchemy operations."""

    def __init__(self, environment: Optional[str] = None):
        self.environment = environment
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker[AsyncSession]] = (
            None
        )

    @property
    def engine(self) -> AsyncEngine:
        """Get the async database engine."""
        if self._engine is None:
            self._engine = self._create_engine()
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Get the async session factory."""
        if self._session_factory is None:
            self._session_factory = self._create_session_factory()
        return self._session_factory

    def _create_engine(self) -> AsyncEngine:
        """Create the async database engine."""
        database_url = get_database_url(self.environment)
        engine_kwargs = get_engine_kwargs(self.environment)

        # Use NullPool for testing to avoid connection pool issues
        if self.environment == "test":
            engine_kwargs["poolclass"] = NullPool

        engine = create_async_engine(
            database_url,
            **engine_kwargs,
            future=True,  # Use SQLAlchemy 2.0 style
        )

        return engine

    def _create_session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Create the async session factory."""
        return async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,  # Don't expire objects after commit
            autoflush=True,  # Auto-flush changes
            autocommit=False,  # Use explicit transactions
        )

    async def dispose(self) -> None:
        """Dispose of the engine and close all connections."""
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get an async database session."""
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


# Global engine instances
development_engine = DatabaseEngine("development")
test_engine = DatabaseEngine("test")
production_engine = DatabaseEngine("production")


def get_database_engine(environment: Optional[str] = None) -> DatabaseEngine:
    """Get database engine for specified environment."""
    if environment == "production":
        return production_engine
    elif environment == "test":
        return test_engine
    else:
        return development_engine


async def get_session(
    environment: Optional[str] = None,
) -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session for the specified environment."""
    engine = get_database_engine(environment)
    async for session in engine.get_session():
        yield session


# Convenience function for dependency injection
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session for dependency injection."""
    async for session in get_session():
        yield session
