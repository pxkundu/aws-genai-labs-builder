"""
Healthcare ChatGPT Clone - Analytics Service
This module handles analytics and reporting for the healthcare application.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_

from models.chat import ChatSession, ChatMessage, ChatAnalytics, KnowledgeBaseSearch

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for analytics and reporting."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_chat_analytics(
        self,
        start_date: datetime,
        end_date: datetime,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get comprehensive chat analytics."""
        try:
            # Base query with date filter
            base_query = self.db.query(ChatSession).filter(
                and_(
                    ChatSession.created_at >= start_date,
                    ChatSession.created_at <= end_date
                )
            )
            
            if user_id:
                base_query = base_query.filter(ChatSession.user_id == user_id)
            
            # Total sessions
            total_sessions = base_query.count()
            
            # Total messages
            total_messages = self.db.query(ChatMessage).join(
                ChatSession, ChatMessage.session_id == ChatSession.session_id
            ).filter(
                and_(
                    ChatSession.created_at >= start_date,
                    ChatSession.created_at <= end_date
                )
            )
            
            if user_id:
                total_messages = total_messages.filter(ChatSession.user_id == user_id)
            
            total_messages = total_messages.count()
            
            # Unique users
            unique_users = base_query.with_entities(ChatSession.user_id).distinct().count()
            
            # Average session length (messages per session)
            average_session_length = total_messages / total_sessions if total_sessions > 0 else 0
            
            # Average response time (from analytics table)
            avg_response_time = self.db.query(func.avg(ChatAnalytics.response_time)).filter(
                and_(
                    ChatAnalytics.created_at >= start_date,
                    ChatAnalytics.created_at <= end_date
                )
            ).scalar() or 0
            
            # Most common queries
            common_queries = self.db.query(
                ChatAnalytics.query,
                func.count(ChatAnalytics.query).label('count')
            ).filter(
                and_(
                    ChatAnalytics.created_at >= start_date,
                    ChatAnalytics.created_at <= end_date
                )
            ).group_by(ChatAnalytics.query).order_by(desc('count')).limit(10).all()
            
            most_common_queries = [
                {"query": query, "count": count}
                for query, count in common_queries
            ]
            
            # User satisfaction score (if available)
            satisfaction_scores = self.db.query(ChatAnalytics.user_satisfaction).filter(
                and_(
                    ChatAnalytics.created_at >= start_date,
                    ChatAnalytics.created_at <= end_date,
                    ChatAnalytics.user_satisfaction.isnot(None)
                )
            ).all()
            
            user_satisfaction_score = None
            if satisfaction_scores:
                scores = [score[0] for score in satisfaction_scores if score[0] is not None]
                if scores:
                    user_satisfaction_score = sum(scores) / len(scores)
            
            return {
                "total_sessions": total_sessions,
                "total_messages": total_messages,
                "unique_users": unique_users,
                "average_session_length": round(average_session_length, 2),
                "average_response_time": round(avg_response_time, 2),
                "most_common_queries": most_common_queries,
                "user_satisfaction_score": round(user_satisfaction_score, 2) if user_satisfaction_score else None
            }
            
        except Exception as e:
            logger.error(f"Error getting chat analytics: {e}")
            return {
                "total_sessions": 0,
                "total_messages": 0,
                "unique_users": 0,
                "average_session_length": 0,
                "average_response_time": 0,
                "most_common_queries": [],
                "user_satisfaction_score": None
            }
    
    async def get_usage_analytics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get usage analytics."""
        try:
            # Daily active users
            daily_active_users = self.db.query(
                func.date(ChatSession.created_at).label('date'),
                func.count(func.distinct(ChatSession.user_id)).label('users')
            ).filter(
                and_(
                    ChatSession.created_at >= start_date,
                    ChatSession.created_at <= end_date
                )
            ).group_by(func.date(ChatSession.created_at)).order_by(desc('date')).first()
            
            daily_active_users = daily_active_users.users if daily_active_users else 0
            
            # Weekly active users
            week_start = start_date - timedelta(days=start_date.weekday())
            weekly_active_users = self.db.query(func.count(func.distinct(ChatSession.user_id))).filter(
                and_(
                    ChatSession.created_at >= week_start,
                    ChatSession.created_at <= end_date
                )
            ).scalar() or 0
            
            # Monthly active users
            month_start = start_date.replace(day=1)
            monthly_active_users = self.db.query(func.count(func.distinct(ChatSession.user_id))).filter(
                and_(
                    ChatSession.created_at >= month_start,
                    ChatSession.created_at <= end_date
                )
            ).scalar() or 0
            
            # Peak usage hours
            peak_hours = self.db.query(
                func.extract('hour', ChatSession.created_at).label('hour'),
                func.count(ChatSession.session_id).label('sessions')
            ).filter(
                and_(
                    ChatSession.created_at >= start_date,
                    ChatSession.created_at <= end_date
                )
            ).group_by(func.extract('hour', ChatSession.created_at)).order_by(desc('sessions')).limit(5).all()
            
            peak_usage_hours = [int(hour[0]) for hour in peak_hours]
            
            # Usage by category (from knowledge base searches)
            usage_by_category = self.db.query(
                KnowledgeBaseSearch.query,
                func.count(KnowledgeBaseSearch.id).label('searches')
            ).filter(
                and_(
                    KnowledgeBaseSearch.created_at >= start_date,
                    KnowledgeBaseSearch.created_at <= end_date
                )
            ).group_by(KnowledgeBaseSearch.query).order_by(desc('searches')).limit(10).all()
            
            usage_by_category_dict = {
                query: searches for query, searches in usage_by_category
            }
            
            # Model usage (from analytics)
            model_usage = self.db.query(
                ChatAnalytics.model_used,
                func.count(ChatAnalytics.id).label('count')
            ).filter(
                and_(
                    ChatAnalytics.created_at >= start_date,
                    ChatAnalytics.created_at <= end_date
                )
            ).group_by(ChatAnalytics.model_used).all()
            
            model_usage_dict = {
                model: count for model, count in model_usage
            }
            
            return {
                "daily_active_users": daily_active_users,
                "weekly_active_users": weekly_active_users,
                "monthly_active_users": monthly_active_users,
                "peak_usage_hours": peak_usage_hours,
                "usage_by_category": usage_by_category_dict,
                "model_usage": model_usage_dict
            }
            
        except Exception as e:
            logger.error(f"Error getting usage analytics: {e}")
            return {
                "daily_active_users": 0,
                "weekly_active_users": 0,
                "monthly_active_users": 0,
                "peak_usage_hours": [],
                "usage_by_category": {},
                "model_usage": {}
            }
    
    async def get_performance_analytics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get performance analytics."""
        try:
            # Response time metrics
            response_times = self.db.query(ChatAnalytics.response_time).filter(
                and_(
                    ChatAnalytics.created_at >= start_date,
                    ChatAnalytics.created_at <= end_date,
                    ChatAnalytics.response_time.isnot(None)
                )
            ).all()
            
            if response_times:
                times = [rt[0] for rt in response_times]
                times.sort()
                
                avg_response_time = sum(times) / len(times)
                p95_index = int(len(times) * 0.95)
                p99_index = int(len(times) * 0.99)
                
                p95_response_time = times[p95_index] if p95_index < len(times) else times[-1]
                p99_response_time = times[p99_index] if p99_index < len(times) else times[-1]
            else:
                avg_response_time = 0
                p95_response_time = 0
                p99_response_time = 0
            
            # Error rate
            total_requests = self.db.query(ChatAnalytics).filter(
                and_(
                    ChatAnalytics.created_at >= start_date,
                    ChatAnalytics.created_at <= end_date
                )
            ).count()
            
            error_requests = self.db.query(ChatAnalytics).filter(
                and_(
                    ChatAnalytics.created_at >= start_date,
                    ChatAnalytics.created_at <= end_date,
                    ChatAnalytics.model_used == "error"
                )
            ).count()
            
            error_rate = (error_requests / total_requests) if total_requests > 0 else 0
            success_rate = 1 - error_rate
            
            # System uptime (this would typically come from monitoring data)
            system_uptime = 99.9  # Placeholder
            
            # Resource utilization (this would come from system metrics)
            resource_utilization = {
                "cpu": 45.2,  # Placeholder
                "memory": 67.8,  # Placeholder
                "disk": 23.1  # Placeholder
            }
            
            return {
                "average_response_time": round(avg_response_time, 2),
                "p95_response_time": round(p95_response_time, 2),
                "p99_response_time": round(p99_response_time, 2),
                "error_rate": round(error_rate, 4),
                "success_rate": round(success_rate, 4),
                "system_uptime": system_uptime,
                "resource_utilization": resource_utilization
            }
            
        except Exception as e:
            logger.error(f"Error getting performance analytics: {e}")
            return {
                "average_response_time": 0,
                "p95_response_time": 0,
                "p99_response_time": 0,
                "error_rate": 0,
                "success_rate": 1,
                "system_uptime": 0,
                "resource_utilization": {}
            }
    
    async def get_recent_activity(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent activity."""
        try:
            recent_sessions = self.db.query(ChatSession).order_by(
                desc(ChatSession.updated_at)
            ).limit(limit).all()
            
            activity = []
            for session in recent_sessions:
                activity.append({
                    "session_id": session.session_id,
                    "user_id": session.user_id,
                    "updated_at": session.updated_at,
                    "message_count": session.message_count,
                    "last_message": session.last_message
                })
            
            return activity
            
        except Exception as e:
            logger.error(f"Error getting recent activity: {e}")
            return []
    
    async def get_top_users(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top users by activity."""
        try:
            top_users = self.db.query(
                ChatSession.user_id,
                func.count(ChatSession.session_id).label('session_count'),
                func.count(ChatMessage.message_id).label('message_count')
            ).join(
                ChatMessage, ChatSession.session_id == ChatMessage.session_id
            ).group_by(ChatSession.user_id).order_by(
                desc('session_count')
            ).limit(limit).all()
            
            users = []
            for user_id, session_count, message_count in top_users:
                users.append({
                    "user_id": user_id,
                    "session_count": session_count,
                    "message_count": message_count
                })
            
            return users
            
        except Exception as e:
            logger.error(f"Error getting top users: {e}")
            return []
    
    async def get_system_alerts(self) -> List[Dict[str, Any]]:
        """Get system alerts (placeholder for monitoring integration)."""
        # This would typically integrate with monitoring systems
        return [
            {
                "type": "info",
                "message": "System running normally",
                "timestamp": datetime.utcnow(),
                "severity": "low"
            }
        ]
    
    async def get_all_analytics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get all analytics data."""
        try:
            chat_analytics = await self.get_chat_analytics(start_date, end_date)
            usage_analytics = await self.get_usage_analytics(start_date, end_date)
            performance_analytics = await self.get_performance_analytics(start_date, end_date)
            
            return {
                "chat": chat_analytics,
                "usage": usage_analytics,
                "performance": performance_analytics,
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting all analytics: {e}")
            return {}
    
    async def generate_daily_report(self, date: datetime) -> Dict[str, Any]:
        """Generate daily analytics report."""
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        
        analytics = await self.get_all_analytics(start_date, end_date)
        
        return {
            "date": date.date().isoformat(),
            "analytics": analytics,
            "summary": {
                "total_sessions": analytics.get("chat", {}).get("total_sessions", 0),
                "total_messages": analytics.get("chat", {}).get("total_messages", 0),
                "unique_users": analytics.get("chat", {}).get("unique_users", 0),
                "average_response_time": analytics.get("performance", {}).get("average_response_time", 0)
            }
        }
    
    async def generate_weekly_report(self, week_start: datetime) -> Dict[str, Any]:
        """Generate weekly analytics report."""
        end_date = week_start + timedelta(days=7)
        
        analytics = await self.get_all_analytics(week_start, end_date)
        
        return {
            "week_start": week_start.date().isoformat(),
            "week_end": end_date.date().isoformat(),
            "analytics": analytics,
            "summary": {
                "total_sessions": analytics.get("chat", {}).get("total_sessions", 0),
                "total_messages": analytics.get("chat", {}).get("total_messages", 0),
                "unique_users": analytics.get("chat", {}).get("unique_users", 0),
                "weekly_active_users": analytics.get("usage", {}).get("weekly_active_users", 0)
            }
        }
