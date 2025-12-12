"""
Health Check Routes
"""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "ecommerce-ai-platform"
    }


@router.get("/health/live")
async def liveness():
    """Liveness probe"""
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness():
    """Readiness probe"""
    return {"status": "ready"}

