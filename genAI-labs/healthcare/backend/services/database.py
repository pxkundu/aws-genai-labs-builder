"""
Healthcare ChatGPT Clone - Database Service
This module handles database connections and operations.
"""

import logging
import asyncio
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session
from contextlib import asynccontextmanager

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Global database engine
_engine = None
_async_engine = None
_session_factory = None
_async_session_factory = None


def get_engine():
    """Get the database engine."""
    global _engine
    if _engine is None:
        _engine = create_engine(
            settings.database_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            echo=settings.DEBUG
        )
    return _engine


def get_async_engine():
    """Get the async database engine."""
    global _async_engine
    if _async_engine is None:
        # Convert postgresql:// to postgresql+asyncpg://
        async_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
        _async_engine = create_async_engine(
            async_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            echo=settings.DEBUG
        )
    return _async_engine


def get_session_factory():
    """Get the session factory."""
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(bind=get_engine())
    return _session_factory


def get_async_session_factory():
    """Get the async session factory."""
    global _async_session_factory
    if _async_session_factory is None:
        _async_session_factory = sessionmaker(
            bind=get_async_engine(),
            class_=AsyncSession,
            expire_on_commit=False
        )
    return _async_session_factory


def get_db() -> Session:
    """Get a database session."""
    session_factory = get_session_factory()
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


async def get_async_db() -> AsyncSession:
    """Get an async database session."""
    session_factory = get_async_session_factory()
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_database():
    """Initialize the database connection."""
    try:
        # Test the connection
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        logger.info("Database connection initialized successfully")
        
        # Create tables if they don't exist
        from models.chat import Base
        Base.metadata.create_all(bind=engine)
        
        logger.info("Database tables created/verified successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def close_database():
    """Close database connections."""
    global _engine, _async_engine
    
    try:
        if _async_engine:
            await _async_engine.dispose()
            logger.info("Async database engine disposed")
        
        if _engine:
            _engine.dispose()
            logger.info("Database engine disposed")
            
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")


async def test_connection() -> bool:
    """Test database connection."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


async def get_database_info() -> dict:
    """Get database information."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # Get database version
            version_result = conn.execute(text("SELECT version()"))
            version = version_result.fetchone()[0]
            
            # Get database size
            size_result = conn.execute(text("SELECT pg_size_pretty(pg_database_size(current_database()))"))
            size = size_result.fetchone()[0]
            
            # Get connection count
            conn_result = conn.execute(text("SELECT count(*) FROM pg_stat_activity"))
            connections = conn_result.fetchone()[0]
            
            return {
                "version": version,
                "size": size,
                "connections": connections,
                "status": "healthy"
            }
            
    except Exception as e:
        logger.error(f"Failed to get database info: {e}")
        return {
            "version": "unknown",
            "size": "unknown",
            "connections": 0,
            "status": "error",
            "error": str(e)
        }
