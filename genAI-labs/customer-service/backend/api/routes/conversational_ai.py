"""
Conversational AI API routes
Handles chat and messaging endpoints
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
import structlog

from services.ai_service import AIService
from services.database import DatabaseService
from services.cache import CacheService
from models.conversation import Conversation, Message, CustomerContext

logger = structlog.get_logger(__name__)

router = APIRouter()


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., description="Customer message")
    customer_id: str = Field(..., description="Customer ID")
    session_id: str = Field(..., description="Session ID")
    channel: str = Field(default="web", description="Communication channel")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str = Field(..., description="AI-generated response")
    intent: str = Field(..., description="Detected intent")
    confidence: float = Field(..., description="Confidence score")
    escalation_needed: bool = Field(..., description="Whether escalation is needed")
    suggested_actions: List[str] = Field(default=[], description="Suggested actions")
    session_id: str = Field(..., description="Session ID")
    timestamp: datetime = Field(..., description="Response timestamp")


class ConversationHistory(BaseModel):
    """Conversation history model"""
    conversation_id: str
    customer_id: str
    messages: List[Message]
    created_at: datetime
    updated_at: datetime
    status: str


# Initialize AI service
ai_service = AIService()


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    db: DatabaseService = Depends(),
    cache: CacheService = Depends()
):
    """Chat with AI assistant"""
    try:
        logger.info("Processing chat request", 
                   customer_id=request.customer_id,
                   session_id=request.session_id)
        
        # Get customer context
        customer_context = await _get_customer_context(
            request.customer_id, db, cache
        )
        
        # Add request context
        if request.context:
            customer_context.update(request.context)
        
        # Analyze intent
        intent_analysis = await ai_service.analyze_customer_intent(
            request.message, customer_context
        )
        
        # Generate response
        ai_response = await ai_service.generate_response(
            request.message, intent_analysis, customer_context
        )
        
        # Create message objects
        customer_message = Message(
            role="customer",
            content=request.message,
            timestamp=datetime.utcnow(),
            metadata={"channel": request.channel}
        )
        
        ai_message = Message(
            role="assistant",
            content=ai_response['response_text'],
            timestamp=datetime.utcnow(),
            metadata={
                "intent": intent_analysis.get('intent'),
                "confidence": intent_analysis.get('confidence'),
                "escalation_needed": ai_response['escalation_needed']
            }
        )
        
        # Save conversation to database
        background_tasks.add_task(
            _save_conversation,
            request.customer_id,
            request.session_id,
            [customer_message, ai_message],
            db
        )
        
        # Update customer context
        background_tasks.add_task(
            _update_customer_context,
            request.customer_id,
            customer_context,
            cache
        )
        
        return ChatResponse(
            response=ai_response['response_text'],
            intent=intent_analysis.get('intent', 'Unknown'),
            confidence=intent_analysis.get('confidence', 0.0),
            escalation_needed=ai_response['escalation_needed'],
            suggested_actions=intent_analysis.get('suggested_actions', []),
            session_id=request.session_id,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error("Chat processing failed", error=str(e))
        raise HTTPException(status_code=500, detail="Chat processing failed")


@router.get("/conversations/{customer_id}", response_model=List[ConversationHistory])
async def get_conversation_history(
    customer_id: str,
    limit: int = 10,
    offset: int = 0,
    db: DatabaseService = Depends()
):
    """Get conversation history for a customer"""
    try:
        conversations = await db.get_conversations(
            customer_id=customer_id,
            limit=limit,
            offset=offset
        )
        
        return [
            ConversationHistory(
                conversation_id=conv.id,
                customer_id=conv.customer_id,
                messages=conv.messages,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                status=conv.status
            )
            for conv in conversations
        ]
        
    except Exception as e:
        logger.error("Failed to get conversation history", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get conversation history")


@router.get("/conversations/{customer_id}/{session_id}", response_model=ConversationHistory)
async def get_conversation(
    customer_id: str,
    session_id: str,
    db: DatabaseService = Depends()
):
    """Get specific conversation"""
    try:
        conversation = await db.get_conversation(
            customer_id=customer_id,
            session_id=session_id
        )
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return ConversationHistory(
            conversation_id=conversation.id,
            customer_id=conversation.customer_id,
            messages=conversation.messages,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            status=conversation.status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get conversation", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get conversation")


@router.post("/conversations/{customer_id}/{session_id}/escalate")
async def escalate_conversation(
    customer_id: str,
    session_id: str,
    reason: str,
    db: DatabaseService = Depends()
):
    """Escalate conversation to human agent"""
    try:
        # Update conversation status
        await db.update_conversation_status(
            customer_id=customer_id,
            session_id=session_id,
            status="escalated",
            metadata={"escalation_reason": reason}
        )
        
        # In a real implementation, you would:
        # 1. Notify human agents
        # 2. Create support ticket
        # 3. Update customer context
        
        return {"message": "Conversation escalated successfully"}
        
    except Exception as e:
        logger.error("Failed to escalate conversation", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to escalate conversation")


@router.get("/analytics/sentiment/{customer_id}")
async def get_customer_sentiment(
    customer_id: str,
    days: int = 30,
    db: DatabaseService = Depends()
):
    """Get customer sentiment analysis"""
    try:
        # Get recent conversations
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
                    sentiment_scores.append(sentiment)
        
        # Calculate average sentiment
        if sentiment_scores:
            avg_sentiment = sum(
                s['sentiment_scores']['Positive'] - s['sentiment_scores']['Negative']
                for s in sentiment_scores
            ) / len(sentiment_scores)
        else:
            avg_sentiment = 0.0
        
        return {
            "customer_id": customer_id,
            "average_sentiment": avg_sentiment,
            "total_interactions": len(sentiment_scores),
            "sentiment_trend": sentiment_scores[-10:] if len(sentiment_scores) > 10 else sentiment_scores,
            "analysis_period_days": days
        }
        
    except Exception as e:
        logger.error("Failed to analyze customer sentiment", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to analyze customer sentiment")


async def _get_customer_context(
    customer_id: str, 
    db: DatabaseService, 
    cache: CacheService
) -> Dict[str, Any]:
    """Get customer context from cache or database"""
    # Try cache first
    context = await cache.get(f"customer_context:{customer_id}")
    if context:
        return context
    
    # Get from database
    customer = await db.get_customer(customer_id)
    if customer:
        context = {
            "customer_id": customer.id,
            "name": customer.name,
            "email": customer.email,
            "tier": customer.tier,
            "preferences": customer.preferences,
            "history": customer.interaction_history
        }
        
        # Cache for 1 hour
        await cache.set(f"customer_context:{customer_id}", context, ttl=3600)
        return context
    
    return {"customer_id": customer_id}


async def _save_conversation(
    customer_id: str,
    session_id: str,
    messages: List[Message],
    db: DatabaseService
):
    """Save conversation to database"""
    try:
        conversation = Conversation(
            customer_id=customer_id,
            session_id=session_id,
            messages=messages,
            status="active"
        )
        
        await db.save_conversation(conversation)
        
    except Exception as e:
        logger.error("Failed to save conversation", error=str(e))


async def _update_customer_context(
    customer_id: str,
    context: Dict[str, Any],
    cache: CacheService
):
    """Update customer context in cache"""
    try:
        await cache.set(f"customer_context:{customer_id}", context, ttl=3600)
        
    except Exception as e:
        logger.error("Failed to update customer context", error=str(e))
