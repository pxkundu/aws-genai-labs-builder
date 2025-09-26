"""
Healthcare ChatGPT Clone - Analytics API Routes
This module handles analytics and reporting endpoints.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from services.analytics_service import AnalyticsService
from services.database import get_db
from config.settings import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


# Request/Response Models
class AnalyticsRequest(BaseModel):
    """Request model for analytics queries."""
    start_date: Optional[datetime] = Field(None, description="Start date for analytics")
    end_date: Optional[datetime] = Field(None, description="End date for analytics")
    user_id: Optional[str] = Field(None, description="Filter by user ID")
    session_id: Optional[str] = Field(None, description="Filter by session ID")
    category: Optional[str] = Field(None, description="Filter by category")
    
    class Config:
        schema_extra = {
            "example": {
                "start_date": "2024-01-01T00:00:00Z",
                "end_date": "2024-01-31T23:59:59Z",
                "user_id": "user_123",
                "category": "medical_guidelines"
            }
        }


class ChatAnalytics(BaseModel):
    """Model for chat analytics data."""
    total_sessions: int
    total_messages: int
    unique_users: int
    average_session_length: float
    average_response_time: float
    most_common_queries: List[Dict[str, Any]]
    user_satisfaction_score: Optional[float] = None
    
    class Config:
        schema_extra = {
            "example": {
                "total_sessions": 150,
                "total_messages": 750,
                "unique_users": 45,
                "average_session_length": 5.2,
                "average_response_time": 2.3,
                "most_common_queries": [
                    {"query": "diabetes symptoms", "count": 25},
                    {"query": "blood pressure", "count": 20}
                ],
                "user_satisfaction_score": 4.2
            }
        }


class UsageAnalytics(BaseModel):
    """Model for usage analytics data."""
    daily_active_users: int
    weekly_active_users: int
    monthly_active_users: int
    peak_usage_hours: List[int]
    usage_by_category: Dict[str, int]
    model_usage: Dict[str, int]
    
    class Config:
        schema_extra = {
            "example": {
                "daily_active_users": 12,
                "weekly_active_users": 35,
                "monthly_active_users": 120,
                "peak_usage_hours": [9, 10, 14, 15],
                "usage_by_category": {
                    "medical_guidelines": 45,
                    "symptoms": 30,
                    "treatment": 25
                },
                "model_usage": {
                    "gpt-3.5-turbo": 60,
                    "claude-3-sonnet": 40
                }
            }
        }
    }


class PerformanceAnalytics(BaseModel):
    """Model for performance analytics data."""
    average_response_time: float
    p95_response_time: float
    p99_response_time: float
    error_rate: float
    success_rate: float
    system_uptime: float
    resource_utilization: Dict[str, float]
    
    class Config:
        schema_extra = {
            "example": {
                "average_response_time": 2.3,
                "p95_response_time": 5.1,
                "p99_response_time": 8.7,
                "error_rate": 0.02,
                "success_rate": 0.98,
                "system_uptime": 99.9,
                "resource_utilization": {
                    "cpu": 45.2,
                    "memory": 67.8,
                    "disk": 23.1
                }
            }
        }
    }


# Dependencies
async def get_analytics_service(db: Session = Depends(get_db)) -> AnalyticsService:
    """Get analytics service instance."""
    return AnalyticsService(db)


# API Endpoints
@router.get("/chat", response_model=ChatAnalytics)
async def get_chat_analytics(
    start_date: Optional[datetime] = Query(None, description="Start date for analytics"),
    end_date: Optional[datetime] = Query(None, description="End date for analytics"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Get chat analytics data.
    
    Returns comprehensive analytics about chat usage, including
    session statistics, message counts, and user engagement metrics.
    """
    try:
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        analytics = await analytics_service.get_chat_analytics(
            start_date=start_date,
            end_date=end_date,
            user_id=user_id
        )
        
        return ChatAnalytics(
            total_sessions=analytics["total_sessions"],
            total_messages=analytics["total_messages"],
            unique_users=analytics["unique_users"],
            average_session_length=analytics["average_session_length"],
            average_response_time=analytics["average_response_time"],
            most_common_queries=analytics["most_common_queries"],
            user_satisfaction_score=analytics.get("user_satisfaction_score")
        )
        
    except Exception as e:
        logger.error(f"Error retrieving chat analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat analytics")


@router.get("/usage", response_model=UsageAnalytics)
async def get_usage_analytics(
    start_date: Optional[datetime] = Query(None, description="Start date for analytics"),
    end_date: Optional[datetime] = Query(None, description="End date for analytics"),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Get usage analytics data.
    
    Returns analytics about system usage patterns, including
    active users, peak usage times, and feature utilization.
    """
    try:
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        analytics = await analytics_service.get_usage_analytics(
            start_date=start_date,
            end_date=end_date
        )
        
        return UsageAnalytics(
            daily_active_users=analytics["daily_active_users"],
            weekly_active_users=analytics["weekly_active_users"],
            monthly_active_users=analytics["monthly_active_users"],
            peak_usage_hours=analytics["peak_usage_hours"],
            usage_by_category=analytics["usage_by_category"],
            model_usage=analytics["model_usage"]
        )
        
    except Exception as e:
        logger.error(f"Error retrieving usage analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve usage analytics")


@router.get("/performance", response_model=PerformanceAnalytics)
async def get_performance_analytics(
    start_date: Optional[datetime] = Query(None, description="Start date for analytics"),
    end_date: Optional[datetime] = Query(None, description="End date for analytics"),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Get performance analytics data.
    
    Returns system performance metrics including response times,
    error rates, and resource utilization.
    """
    try:
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=7)
        
        analytics = await analytics_service.get_performance_analytics(
            start_date=start_date,
            end_date=end_date
        )
        
        return PerformanceAnalytics(
            average_response_time=analytics["average_response_time"],
            p95_response_time=analytics["p95_response_time"],
            p99_response_time=analytics["p99_response_time"],
            error_rate=analytics["error_rate"],
            success_rate=analytics["success_rate"],
            system_uptime=analytics["system_uptime"],
            resource_utilization=analytics["resource_utilization"]
        )
        
    except Exception as e:
        logger.error(f"Error retrieving performance analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve performance analytics")


@router.get("/dashboard")
async def get_dashboard_data(
    start_date: Optional[datetime] = Query(None, description="Start date for analytics"),
    end_date: Optional[datetime] = Query(None, description="End date for analytics"),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Get comprehensive dashboard data.
    
    Returns all analytics data needed for the admin dashboard,
    including chat, usage, and performance metrics.
    """
    try:
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Get all analytics data
        chat_analytics = await analytics_service.get_chat_analytics(start_date, end_date)
        usage_analytics = await analytics_service.get_usage_analytics(start_date, end_date)
        performance_analytics = await analytics_service.get_performance_analytics(start_date, end_date)
        
        # Get additional dashboard-specific data
        recent_activity = await analytics_service.get_recent_activity(limit=10)
        top_users = await analytics_service.get_top_users(limit=10)
        system_alerts = await analytics_service.get_system_alerts()
        
        return {
            "chat": chat_analytics,
            "usage": usage_analytics,
            "performance": performance_analytics,
            "recent_activity": recent_activity,
            "top_users": top_users,
            "system_alerts": system_alerts,
            "date_range": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error retrieving dashboard data: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dashboard data")


@router.get("/export")
async def export_analytics(
    format: str = Query("json", regex="^(json|csv|xlsx)$", description="Export format"),
    start_date: Optional[datetime] = Query(None, description="Start date for analytics"),
    end_date: Optional[datetime] = Query(None, description="End date for analytics"),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Export analytics data.
    
    Exports analytics data in the specified format (JSON, CSV, or Excel).
    """
    try:
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Get analytics data
        analytics_data = await analytics_service.get_all_analytics(start_date, end_date)
        
        # Export in requested format
        if format == "json":
            return analytics_data
        elif format == "csv":
            csv_data = await analytics_service.export_to_csv(analytics_data)
            return {"data": csv_data, "format": "csv"}
        elif format == "xlsx":
            excel_data = await analytics_service.export_to_excel(analytics_data)
            return {"data": excel_data, "format": "xlsx"}
        
    except Exception as e:
        logger.error(f"Error exporting analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to export analytics")


@router.get("/reports/daily")
async def get_daily_report(
    date: Optional[datetime] = Query(None, description="Date for daily report"),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Get daily analytics report.
    
    Returns a comprehensive daily report with key metrics and insights.
    """
    try:
        if not date:
            date = datetime.utcnow().date()
        
        report = await analytics_service.generate_daily_report(date)
        
        return report
        
    except Exception as e:
        logger.error(f"Error generating daily report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate daily report")


@router.get("/reports/weekly")
async def get_weekly_report(
    week_start: Optional[datetime] = Query(None, description="Week start date"),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Get weekly analytics report.
    
    Returns a comprehensive weekly report with trends and insights.
    """
    try:
        if not week_start:
            # Get start of current week
            today = datetime.utcnow().date()
            week_start = today - timedelta(days=today.weekday())
        
        report = await analytics_service.generate_weekly_report(week_start)
        
        return report
        
    except Exception as e:
        logger.error(f"Error generating weekly report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate weekly report")
