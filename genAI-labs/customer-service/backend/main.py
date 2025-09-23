"""
GenAI Customer Service Backend
Main FastAPI application entry point
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Dict, Any

import structlog
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from api.routes import (
    conversational_ai,
    voice_ai,
    knowledge_base,
    analytics,
    health
)
from services.database import DatabaseService
from services.cache import CacheService
from config.settings import Settings
from utils.logging_config import setup_logging

# Setup structured logging
setup_logging()
logger = structlog.get_logger(__name__)

# Load settings
settings = Settings()

# Global services
db_service: DatabaseService = None
cache_service: CacheService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global db_service, cache_service
    
    # Startup
    logger.info("Starting GenAI Customer Service Backend")
    
    try:
        # Initialize database service
        db_service = DatabaseService(settings)
        await db_service.connect()
        logger.info("Database service initialized")
        
        # Initialize cache service
        cache_service = CacheService(settings)
        await cache_service.connect()
        logger.info("Cache service initialized")
        
        yield
        
    except Exception as e:
        logger.error("Failed to initialize services", error=str(e))
        raise
    
    finally:
        # Shutdown
        logger.info("Shutting down GenAI Customer Service Backend")
        if db_service:
            await db_service.disconnect()
        if cache_service:
            await cache_service.disconnect()


# Create FastAPI application
app = FastAPI(
    title="GenAI Customer Service API",
    description="AI-powered customer service platform with AWS GenAI services",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)


# Dependency injection
async def get_db_service() -> DatabaseService:
    """Get database service dependency"""
    if not db_service:
        raise HTTPException(status_code=503, detail="Database service not available")
    return db_service


async def get_cache_service() -> CacheService:
    """Get cache service dependency"""
    if not cache_service:
        raise HTTPException(status_code=503, detail="Cache service not available")
    return cache_service


# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(conversational_ai.router, prefix="/api/v1", tags=["Conversational AI"])
app.include_router(voice_ai.router, prefix="/api/v1", tags=["Voice AI"])
app.include_router(knowledge_base.router, prefix="/api/v1", tags=["Knowledge Base"])
app.include_router(analytics.router, prefix="/api/v1", tags=["Analytics"])


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(
        "Unhandled exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "request_id": getattr(request.state, "request_id", None)
        }
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "GenAI Customer Service API",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
