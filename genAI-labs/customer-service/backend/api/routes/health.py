"""
Health check API routes
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from datetime import datetime

from services.database import DatabaseService
from services.cache import CacheService

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: datetime
    services: dict


@router.get("/health", response_model=HealthResponse)
async def health_check(
    db: DatabaseService = Depends(),
    cache: CacheService = Depends()
):
    """Health check endpoint"""
    
    services = {
        "database": "healthy",
        "cache": "healthy",
        "ai_services": "healthy"
    }
    
    # Check database connection
    try:
        await db.client.admin.command('ping')
    except Exception:
        services["database"] = "unhealthy"
    
    # Check cache connection
    try:
        await cache.redis_client.ping()
    except Exception:
        services["cache"] = "unhealthy"
    
    # Determine overall status
    overall_status = "healthy" if all(
        status == "healthy" for status in services.values()
    ) else "unhealthy"
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        services=services
    )


@router.get("/health/ready")
async def readiness_check():
    """Readiness check endpoint"""
    return {"status": "ready", "timestamp": datetime.utcnow()}


@router.get("/health/live")
async def liveness_check():
    """Liveness check endpoint"""
    return {"status": "alive", "timestamp": datetime.utcnow()}
