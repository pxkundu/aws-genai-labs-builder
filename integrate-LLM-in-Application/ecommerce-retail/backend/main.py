"""
E-Commerce AI Platform - Main FastAPI Application
Production-ready e-commerce backend with integrated LLM capabilities
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from api.routes import (
    products,
    recommendations,
    chat,
    reviews,
    analytics,
    health
)
from services.database import DatabaseService
from services.cache import CacheService
from config.settings import get_settings
from utils.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Load settings
settings = get_settings()

# Global services
db_service: DatabaseService = None
cache_service: CacheService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown"""
    global db_service, cache_service
    
    # Startup
    logger.info("Starting E-Commerce AI Platform Backend")
    
    try:
        # Initialize database service
        db_service = DatabaseService(settings)
        await db_service.connect()
        await db_service.init_db()
        logger.info("Database service initialized")
        
        # Initialize cache service
        cache_service = CacheService(settings)
        await cache_service.connect()
        logger.info("Cache service initialized")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}", exc_info=True)
        raise
    
    finally:
        # Shutdown
        logger.info("Shutting down E-Commerce AI Platform Backend")
        if db_service:
            await db_service.disconnect()
        if cache_service:
            await cache_service.disconnect()


# Create FastAPI application
app = FastAPI(
    title="E-Commerce AI Platform API",
    description="AI-powered e-commerce platform with LLM integration for recommendations, chat support, and analytics",
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
app.include_router(products.router, prefix="/api/v1", tags=["Products"])
app.include_router(recommendations.router, prefix="/api/v1", tags=["Recommendations"])
app.include_router(chat.router, prefix="/api/v1", tags=["Chat Support"])
app.include_router(reviews.router, prefix="/api/v1", tags=["Reviews"])
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
        "message": "E-Commerce AI Platform API",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs",
        "features": [
            "Smart Product Recommendations",
            "AI Customer Support Chat",
            "Product Description Generation",
            "Review Sentiment Analysis",
            "Business Analytics & Insights"
        ]
    }


@app.get("/info")
async def info():
    """API information endpoint"""
    return {
        "name": "E-Commerce AI Platform API",
        "version": "1.0.0",
        "description": "AI-powered e-commerce platform with LLM integration",
        "environment": settings.ENVIRONMENT,
        "endpoints": {
            "health": "/api/v1/health",
            "products": "/api/v1/products",
            "recommendations": "/api/v1/recommendations",
            "chat": "/api/v1/chat",
            "reviews": "/api/v1/reviews",
            "analytics": "/api/v1/analytics"
        }
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

