"""
Healthcare ChatGPT Clone - Main FastAPI Application
This is the main entry point for the healthcare AI chat backend API.
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from config.settings import get_settings
from utils.logging_config import setup_logging
from api.routes import chat, knowledge, health, analytics
from services.database import init_database, close_database
from services.cache import init_cache, close_cache

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Healthcare ChatGPT Clone API...")
    
    try:
        # Initialize database
        await init_database()
        logger.info("Database initialized successfully")
        
        # Initialize cache
        await init_cache()
        logger.info("Cache initialized successfully")
        
        logger.info("Healthcare ChatGPT Clone API started successfully")
        yield
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    finally:
        # Shutdown
        logger.info("Shutting down Healthcare ChatGPT Clone API...")
        
        try:
            await close_database()
            await close_cache()
            logger.info("Application shutdown completed")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title="Healthcare ChatGPT Clone API",
    description="Backend API for Healthcare ChatGPT Clone - AI-powered chat interface for healthcare organizations",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "prod" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "prod" else None,
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

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(knowledge.router, prefix="/api/v1/knowledge", tags=["knowledge"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])


@app.get("/")
async def root():
    """Root endpoint with basic API information."""
    return {
        "message": "Healthcare ChatGPT Clone API",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "status": "running",
        "docs_url": "/docs" if settings.ENVIRONMENT != "prod" else None
    }


@app.get("/info")
async def info():
    """API information endpoint."""
    return {
        "name": "Healthcare ChatGPT Clone API",
        "version": "1.0.0",
        "description": "AI-powered chat interface for healthcare organizations",
        "environment": settings.ENVIRONMENT,
        "features": [
            "Multi-LLM support (OpenAI, AWS Bedrock)",
            "Healthcare knowledge base integration",
            "Secure chat storage",
            "HIPAA-compliant architecture",
            "Real-time analytics",
            "Customizable responses"
        ],
        "endpoints": {
            "health": "/health",
            "chat": "/api/v1/chat",
            "knowledge": "/api/v1/knowledge",
            "analytics": "/api/v1/analytics"
        }
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Global HTTP exception handler."""
    logger.error(f"HTTP error: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler for unhandled exceptions."""
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "path": str(request.url)
        }
    )


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "dev",
        log_level="info"
    )
