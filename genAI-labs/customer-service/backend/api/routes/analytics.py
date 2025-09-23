"""
Analytics API routes
Handles customer analytics and insights endpoints
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
import structlog

from services.ai_service import AIService
from services.database import DatabaseService

logger = structlog.get_logger(__name__)

router = APIRouter()


class AnalyticsRequest(BaseModel):
    """Analytics request model"""
    customer_id: Optional[str] = Field(None, description="Customer ID")
    start_date: Optional[datetime] = Field(None, description="Start date")
    end_date: Optional[datetime] = Field(None, description="End date")
    metrics: List[str] = Field(default=["sentiment", "intent", "satisfaction"], description="Metrics to analyze")


class SentimentAnalysis(BaseModel):
    """Sentiment analysis model"""
    customer_id: str = Field(..., description="Customer ID")
    average_sentiment: float = Field(..., description="Average sentiment score")
    sentiment_trend: List[Dict[str, Any]] = Field(..., description="Sentiment trend over time")
    total_interactions: int = Field(..., description="Total interactions")
    analysis_period_days: int = Field(..., description="Analysis period in days")


class PerformanceMetrics(BaseModel):
    """Performance metrics model"""
    total_conversations: int = Field(..., description="Total conversations")
    resolved_conversations: int = Field(..., description="Resolved conversations")
    escalated_conversations: int = Field(..., description="Escalated conversations")
    average_response_time: float = Field(..., description="Average response time in seconds")
    customer_satisfaction_score: float = Field(..., description="Customer satisfaction score")
    first_contact_resolution_rate: float = Field(..., description="First contact resolution rate")


# Initialize AI service
ai_service = AIService()


@router.get("/analytics/sentiment/{customer_id}", response_model=SentimentAnalysis)
async def get_customer_sentiment(
    customer_id: str,
    days: int = Query(30, description="Number of days to analyze"),
    db: DatabaseService = Depends()
):
    """Get customer sentiment analysis"""
    try:
        logger.info("Analyzing customer sentiment", 
                   customer_id=customer_id,
                   days=days)
        
        # Get recent conversations
        start_date = datetime.utcnow() - timedelta(days=days)
        conversations = await db.get_conversations(
            customer_id=customer_id,
            limit=100,
            days_back=days
        )
        
        # Analyze sentiment
        sentiment_scores = []
        for conv in conversations:
            for message in conv.messages:
                if message.role == "customer":
                    sentiment = await ai_service.analyze_sentiment(message.content)
                    sentiment_scores.append({
                        "timestamp": message.timestamp,
                        "sentiment": sentiment["sentiment"],
                        "score": sentiment["sentiment_scores"]["Positive"] - sentiment["sentiment_scores"]["Negative"]
                    })
        
        # Calculate average sentiment
        if sentiment_scores:
            avg_sentiment = sum(s["score"] for s in sentiment_scores) / len(sentiment_scores)
        else:
            avg_sentiment = 0.0
        
        return SentimentAnalysis(
            customer_id=customer_id,
            average_sentiment=avg_sentiment,
            sentiment_trend=sentiment_scores[-10:] if len(sentiment_scores) > 10 else sentiment_scores,
            total_interactions=len(sentiment_scores),
            analysis_period_days=days
        )
        
    except Exception as e:
        logger.error("Failed to analyze customer sentiment", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to analyze customer sentiment")


@router.get("/analytics/performance", response_model=PerformanceMetrics)
async def get_performance_metrics(
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    db: DatabaseService = Depends()
):
    """Get performance metrics"""
    try:
        logger.info("Getting performance metrics")
        
        # Set default date range
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Get conversation analytics
        analytics = await db.get_conversation_analytics(start_date, end_date)
        
        # Calculate metrics
        total_conversations = analytics["total_conversations"]
        resolved_conversations = sum(
            stat["count"] for stat in analytics["statistics"] 
            if stat["_id"] == "resolved"
        )
        escalated_conversations = sum(
            stat["count"] for stat in analytics["statistics"] 
            if stat["_id"] == "escalated"
        )
        
        # Calculate rates
        resolution_rate = (resolved_conversations / total_conversations * 100) if total_conversations > 0 else 0
        escalation_rate = (escalated_conversations / total_conversations * 100) if total_conversations > 0 else 0
        
        return PerformanceMetrics(
            total_conversations=total_conversations,
            resolved_conversations=resolved_conversations,
            escalated_conversations=escalated_conversations,
            average_response_time=2.5,  # Placeholder - would calculate from actual data
            customer_satisfaction_score=4.2,  # Placeholder - would calculate from feedback
            first_contact_resolution_rate=resolution_rate
        )
        
    except Exception as e:
        logger.error("Failed to get performance metrics", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get performance metrics")


@router.get("/analytics/trends")
async def get_analytics_trends(
    metric: str = Query("conversations", description="Metric to analyze"),
    period: str = Query("daily", description="Time period (daily, weekly, monthly)"),
    days: int = Query(30, description="Number of days to analyze"),
    db: DatabaseService = Depends()
):
    """Get analytics trends"""
    try:
        logger.info("Getting analytics trends", metric=metric, period=period)
        
        # This would implement trend analysis
        # For now, return placeholder data
        trends = []
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=days-i)
            trends.append({
                "date": date.isoformat(),
                "value": 10 + (i % 5),  # Placeholder trend data
                "metric": metric
            })
        
        return {
            "metric": metric,
            "period": period,
            "trends": trends,
            "summary": {
                "total": sum(t["value"] for t in trends),
                "average": sum(t["value"] for t in trends) / len(trends),
                "growth_rate": 5.2  # Placeholder
            }
        }
        
    except Exception as e:
        logger.error("Failed to get analytics trends", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get analytics trends")


@router.get("/analytics/customers/{customer_id}/insights")
async def get_customer_insights(
    customer_id: str,
    db: DatabaseService = Depends()
):
    """Get customer insights and recommendations"""
    try:
        logger.info("Getting customer insights", customer_id=customer_id)
        
        # Get customer data
        customer = await db.get_customer(customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Get recent conversations
        conversations = await db.get_conversations(customer_id=customer_id, limit=20)
        
        # Analyze patterns
        intents = []
        sentiments = []
        
        for conv in conversations:
            for message in conv.messages:
                if message.role == "customer":
                    # Analyze intent and sentiment
                    intent_analysis = await ai_service.analyze_customer_intent(
                        message.content, {"customer_id": customer_id}
                    )
                    sentiment_analysis = await ai_service.analyze_sentiment(message.content)
                    
                    intents.append(intent_analysis.get("intent", "Unknown"))
                    sentiments.append(sentiment_analysis["sentiment"])
        
        # Generate insights
        insights = {
            "customer_id": customer_id,
            "total_interactions": len(conversations),
            "most_common_intents": _get_most_common(intents),
            "sentiment_distribution": _get_sentiment_distribution(sentiments),
            "recommendations": _generate_recommendations(intents, sentiments),
            "risk_factors": _identify_risk_factors(sentiments, intents),
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return insights
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get customer insights", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get customer insights")


def _get_most_common(items: List[str]) -> List[Dict[str, Any]]:
    """Get most common items with counts"""
    from collections import Counter
    counter = Counter(items)
    return [{"item": item, "count": count} for item, count in counter.most_common(5)]


def _get_sentiment_distribution(sentiments: List[str]) -> Dict[str, int]:
    """Get sentiment distribution"""
    from collections import Counter
    return dict(Counter(sentiments))


def _generate_recommendations(intents: List[str], sentiments: List[str]) -> List[str]:
    """Generate recommendations based on patterns"""
    recommendations = []
    
    # Check for high escalation intent
    if intents.count("Escalation Request") > len(intents) * 0.3:
        recommendations.append("Consider proactive outreach to address recurring issues")
    
    # Check for negative sentiment
    if sentiments.count("NEGATIVE") > len(sentiments) * 0.4:
        recommendations.append("Customer satisfaction intervention may be needed")
    
    # Check for technical support frequency
    if intents.count("Technical Support") > len(intents) * 0.5:
        recommendations.append("Provide additional technical resources or training")
    
    return recommendations


def _identify_risk_factors(sentiments: List[str], intents: List[str]) -> List[str]:
    """Identify risk factors for customer churn"""
    risk_factors = []
    
    # High negative sentiment
    if sentiments.count("NEGATIVE") > len(sentiments) * 0.5:
        risk_factors.append("High negative sentiment")
    
    # Multiple escalation requests
    if intents.count("Escalation Request") > 3:
        risk_factors.append("Multiple escalation requests")
    
    # Billing complaints
    if intents.count("Billing Question") > 2:
        risk_factors.append("Billing issues")
    
    return risk_factors
