"""
Healthcare ChatGPT Clone - Chat API Routes
This module handles all chat-related API endpoints.
"""

import logging
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from models.chat import ChatSession, ChatMessage
from services.chat_service import ChatService
from services.ai_service import AIService
from services.database import get_db
from utils.validators import validate_chat_input
from config.settings import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


# Request/Response Models
class ChatMessageRequest(BaseModel):
    """Request model for chat messages."""
    message: str = Field(..., min_length=1, max_length=4000, description="The user's message")
    session_id: Optional[str] = Field(None, description="Chat session ID")
    user_id: Optional[str] = Field(None, description="User ID")
    context: Optional[dict] = Field(None, description="Additional context for the conversation")
    model: Optional[str] = Field(None, description="AI model to use (openai, bedrock)")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "What are the symptoms of diabetes?",
                "session_id": "session_123",
                "user_id": "user_456",
                "context": {"patient_age": 45, "medical_history": "hypertension"},
                "model": "openai"
            }
        }


class ChatMessageResponse(BaseModel):
    """Response model for chat messages."""
    message_id: str
    session_id: str
    user_message: str
    ai_response: str
    timestamp: datetime
    model_used: str
    confidence_score: Optional[float] = None
    sources: Optional[List[str]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "message_id": "msg_123",
                "session_id": "session_123",
                "user_message": "What are the symptoms of diabetes?",
                "ai_response": "Common symptoms of diabetes include...",
                "timestamp": "2024-01-15T10:30:00Z",
                "model_used": "gpt-3.5-turbo",
                "confidence_score": 0.95,
                "sources": ["medical_guidelines.pdf", "diabetes_faq.txt"]
            }
        }


class ChatSessionResponse(BaseModel):
    """Response model for chat sessions."""
    session_id: str
    user_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    message_count: int
    last_message: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "session_id": "session_123",
                "user_id": "user_456",
                "created_at": "2024-01-15T10:00:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
                "message_count": 5,
                "last_message": "What are the symptoms of diabetes?"
            }
        }


class ChatHistoryResponse(BaseModel):
    """Response model for chat history."""
    session_id: str
    messages: List[ChatMessageResponse]
    total_messages: int
    
    class Config:
        schema_extra = {
            "example": {
                "session_id": "session_123",
                "messages": [
                    {
                        "message_id": "msg_123",
                        "session_id": "session_123",
                        "user_message": "What are the symptoms of diabetes?",
                        "ai_response": "Common symptoms of diabetes include...",
                        "timestamp": "2024-01-15T10:30:00Z",
                        "model_used": "gpt-3.5-turbo",
                        "confidence_score": 0.95,
                        "sources": ["medical_guidelines.pdf"]
                    }
                ],
                "total_messages": 1
            }
        }
    }


# Dependencies
async def get_chat_service(db: Session = Depends(get_db)) -> ChatService:
    """Get chat service instance."""
    return ChatService(db)


async def get_ai_service() -> AIService:
    """Get AI service instance."""
    return AIService()


# API Endpoints
@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
    request: ChatMessageRequest,
    background_tasks: BackgroundTasks,
    chat_service: ChatService = Depends(get_chat_service),
    ai_service: AIService = Depends(get_ai_service)
):
    """
    Send a message and get AI response.
    
    This endpoint processes user messages and returns AI-generated responses
    tailored for healthcare contexts.
    """
    try:
        # Validate input
        validate_chat_input(request.message)
        
        # Get or create chat session
        session = await chat_service.get_or_create_session(
            session_id=request.session_id,
            user_id=request.user_id
        )
        
        # Get AI response
        ai_response = await ai_service.generate_response(
            message=request.message,
            session_id=session.session_id,
            context=request.context,
            model=request.model
        )
        
        # Save messages to database
        user_message = await chat_service.save_message(
            session_id=session.session_id,
            message=request.message,
            message_type="user",
            metadata={"context": request.context}
        )
        
        ai_message = await chat_service.save_message(
            session_id=session.session_id,
            message=ai_response["response"],
            message_type="ai",
            metadata={
                "model_used": ai_response["model"],
                "confidence_score": ai_response.get("confidence_score"),
                "sources": ai_response.get("sources", [])
            }
        )
        
        # Update session
        await chat_service.update_session(session.session_id)
        
        # Background task for analytics
        if settings.ENABLE_CHAT_ANALYTICS:
            background_tasks.add_task(
                chat_service.record_analytics,
                session.session_id,
                request.message,
                ai_response["response"]
            )
        
        logger.info(f"Chat message processed successfully for session {session.session_id}")
        
        return ChatMessageResponse(
            message_id=ai_message.message_id,
            session_id=session.session_id,
            user_message=request.message,
            ai_response=ai_response["response"],
            timestamp=ai_message.created_at,
            model_used=ai_response["model"],
            confidence_score=ai_response.get("confidence_score"),
            sources=ai_response.get("sources", [])
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail="Failed to process chat message")


@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_chat_sessions(
    user_id: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Get chat sessions for a user.
    
    Returns a list of chat sessions with metadata.
    """
    try:
        sessions = await chat_service.get_sessions(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        return [
            ChatSessionResponse(
                session_id=session.session_id,
                user_id=session.user_id,
                created_at=session.created_at,
                updated_at=session.updated_at,
                message_count=session.message_count,
                last_message=session.last_message
            )
            for session in sessions
        ]
        
    except Exception as e:
        logger.error(f"Error retrieving chat sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat sessions")


@router.get("/sessions/{session_id}/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: str,
    limit: int = 50,
    offset: int = 0,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Get chat history for a specific session.
    
    Returns the conversation history for a given session ID.
    """
    try:
        # Verify session exists
        session = await chat_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        # Get messages
        messages = await chat_service.get_messages(
            session_id=session_id,
            limit=limit,
            offset=offset
        )
        
        return ChatHistoryResponse(
            session_id=session_id,
            messages=[
                ChatMessageResponse(
                    message_id=msg.message_id,
                    session_id=msg.session_id,
                    user_message=msg.message if msg.message_type == "user" else "",
                    ai_response=msg.message if msg.message_type == "ai" else "",
                    timestamp=msg.created_at,
                    model_used=msg.metadata.get("model_used", ""),
                    confidence_score=msg.metadata.get("confidence_score"),
                    sources=msg.metadata.get("sources", [])
                )
                for msg in messages
            ],
            total_messages=len(messages)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving chat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat history")


@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Delete a chat session and all its messages.
    
    Permanently removes a chat session and all associated messages.
    """
    try:
        # Verify session exists
        session = await chat_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        # Delete session and messages
        await chat_service.delete_session(session_id)
        
        logger.info(f"Chat session {session_id} deleted successfully")
        
        return {"message": "Chat session deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting chat session: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete chat session")


@router.get("/sessions/{session_id}")
async def get_chat_session(
    session_id: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Get details of a specific chat session.
    
    Returns metadata about a chat session.
    """
    try:
        session = await chat_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        return ChatSessionResponse(
            session_id=session.session_id,
            user_id=session.user_id,
            created_at=session.created_at,
            updated_at=session.updated_at,
            message_count=session.message_count,
            last_message=session.last_message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving chat session: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat session")
