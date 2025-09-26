"""
Healthcare ChatGPT Clone - Health Check API Routes
This module handles health check and system status endpoints.
"""

import logging
import psutil
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from services.database import get_db
from services.cache import get_cache
from config.settings import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


@router.get("/")
async def health_check():
    """
    Basic health check endpoint.
    
    Returns the current status of the API service.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "healthcare-chatgpt-api",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


@router.get("/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """
    Detailed health check endpoint.
    
    Returns comprehensive system health information including
    database connectivity, cache status, and system metrics.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "healthcare-chatgpt-api",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "checks": {}
    }
    
    # Database health check
    try:
        db.execute("SELECT 1")
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }
        health_status["status"] = "unhealthy"
    
    # Cache health check
    try:
        cache = get_cache()
        await cache.ping()
        health_status["checks"]["cache"] = {
            "status": "healthy",
            "message": "Cache connection successful"
        }
    except Exception as e:
        health_status["checks"]["cache"] = {
            "status": "unhealthy",
            "message": f"Cache connection failed: {str(e)}"
        }
        health_status["status"] = "unhealthy"
    
    # System metrics
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        health_status["checks"]["system"] = {
            "status": "healthy",
            "metrics": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_free_gb": round(disk.free / (1024**3), 2)
            }
        }
        
        # Check if system resources are critically low
        if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
            health_status["checks"]["system"]["status"] = "warning"
            health_status["checks"]["system"]["message"] = "High resource utilization detected"
            
    except Exception as e:
        health_status["checks"]["system"] = {
            "status": "unhealthy",
            "message": f"System metrics collection failed: {str(e)}"
        }
        health_status["status"] = "unhealthy"
    
    # Configuration check
    try:
        required_configs = [
            "OPENAI_API_KEY",
            "DB_HOST",
            "DB_NAME",
            "S3_BUCKET"
        ]
        
        missing_configs = []
        for config in required_configs:
            if not getattr(settings, config, None):
                missing_configs.append(config)
        
        if missing_configs:
            health_status["checks"]["configuration"] = {
                "status": "unhealthy",
                "message": f"Missing required configurations: {', '.join(missing_configs)}"
            }
            health_status["status"] = "unhealthy"
        else:
            health_status["checks"]["configuration"] = {
                "status": "healthy",
                "message": "All required configurations present"
            }
            
    except Exception as e:
        health_status["checks"]["configuration"] = {
            "status": "unhealthy",
            "message": f"Configuration check failed: {str(e)}"
        }
        health_status["status"] = "unhealthy"
    
    return health_status


@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """
    Readiness check endpoint for Kubernetes/container orchestration.
    
    Returns whether the service is ready to accept traffic.
    """
    try:
        # Check database connectivity
        db.execute("SELECT 1")
        
        # Check cache connectivity
        cache = get_cache()
        await cache.ping()
        
        # Check if required configurations are present
        if not settings.OPENAI_API_KEY:
            return {
                "status": "not_ready",
                "message": "OpenAI API key not configured"
            }, 503
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {
            "status": "not_ready",
            "message": str(e)
        }, 503


@router.get("/live")
async def liveness_check():
    """
    Liveness check endpoint for Kubernetes/container orchestration.
    
    Returns whether the service is alive and should not be restarted.
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/metrics")
async def metrics_endpoint():
    """
    Basic metrics endpoint.
    
    Returns key application metrics for monitoring.
    """
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_free_gb": round(disk.free / (1024**3), 2)
            },
            "application": {
                "version": settings.APP_VERSION,
                "environment": settings.ENVIRONMENT,
                "uptime": "N/A"  # Could be implemented with startup time tracking
            }
        }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Metrics collection failed: {e}")
        return {
            "error": "Failed to collect metrics",
            "message": str(e)
        }, 500
