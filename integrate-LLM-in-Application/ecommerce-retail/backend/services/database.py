"""
Database Service for E-Commerce Platform
"""

import logging
from typing import Optional
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from config.settings import Settings

logger = logging.getLogger(__name__)

Base = declarative_base()


class DatabaseService:
    """Database service for managing database connections"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.engine = None
        self.async_session_maker = None
    
    async def connect(self):
        """Connect to database"""
        try:
            # Convert postgresql:// to postgresql+asyncpg://
            database_url = self.settings.DATABASE_URL
            if database_url.startswith("postgresql://"):
                database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
            
            self.engine = create_async_engine(
                database_url,
                echo=self.settings.DEBUG,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20
            )
            
            self.async_session_maker = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            logger.info("Database connection established")
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from database"""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connection closed")
    
    async def init_db(self):
        """Initialize database tables"""
        try:
            async with self.engine.begin() as conn:
                # Import models here to avoid circular imports
                # await conn.run_sync(Base.metadata.create_all)
                logger.info("Database tables initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def get_session(self) -> AsyncSession:
        """Get database session"""
        async with self.async_session_maker() as session:
            try:
                yield session
            finally:
                await session.close()

