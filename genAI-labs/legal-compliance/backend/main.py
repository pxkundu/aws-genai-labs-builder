"""
Legal Compliance AI Platform - Main Application
Multi-LLM legal question answering system for Western and European law
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response

from api.routes import legal, health, admin
from core.config import get_settings
from core.database import init_database, get_db
from core.cache import init_cache
from core.logging_config import setup_logging
from models.legal_question import LegalQuestionRequest, LegalQuestionResponse
from services.llm_service import LLMService
from services.legal_service import LegalService

# Metrics
REQUEST_COUNT = Counter('legal_requests_total', 'Total legal requests', ['endpoint'])
REQUEST_DURATION = Histogram('legal_request_duration_seconds', 'Request duration', ['endpoint'])
LLM_RESPONSE_TIME = Histogram('llm_response_time_seconds', 'LLM response time', ['model'])

# Security
security = HTTPBearer(auto_error=False)
settings = get_settings()

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Legal Compliance AI Platform")
    
    # Initialize database
    await init_database()
    logger.info("Database initialized")
    
    # Initialize cache
    await init_cache()
    logger.info("Cache initialized")
    
    yield
    
    logger.info("Shutting down Legal Compliance AI Platform")


# Create FastAPI app
app = FastAPI(
    title="Legal Compliance AI Platform",
    description="Multi-LLM legal question answering system for Western and European law",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(legal.router, prefix="/api/v1", tags=["legal"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Legal Compliance AI Platform",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs" if settings.ENVIRONMENT != "production" else None
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type="text/plain")


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Global HTTP exception handler"""
    logger.error(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return {
        "error": exc.detail,
        "status_code": exc.status_code,
        "timestamp": asyncio.get_event_loop().time()
    }


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return {
        "error": "Internal server error",
        "status_code": 500,
        "timestamp": asyncio.get_event_loop().time()
    }


# Dependency injection
async def get_legal_service() -> LegalService:
    """Get legal service instance"""
    return LegalService()


async def get_llm_service() -> LLMService:
    """Get LLM service instance"""
    return LLMService()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower(),
    )
