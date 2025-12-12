"""
Chat Support Routes
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from ...services.chat_service import ChatService
from ...services.llm_service import LLMService
from ...services.database import DatabaseService
from ...services.cache import CacheService

logger = logging.getLogger(__name__)
router = APIRouter()


class ChatMessageRequest(BaseModel):
    """Request model for chat message"""
    message: str = Field(..., description="User message")
    session_id: str = Field(..., description="Chat session ID")
    user_id: Optional[str] = Field(None, description="User ID")
    context: Optional[dict] = Field(None, description="Additional context")


class ChatMessageResponse(BaseModel):
    """Response model for chat message"""
    response: str
    session_id: str
    provider: str
    model: str
    timestamp: str


# Initialize services
_llm_service: Optional[LLMService] = None
_chat_service: Optional[ChatService] = None


def get_llm_service() -> LLMService:
    """Get LLM service instance"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


def get_chat_service(
    llm_service: LLMService = Depends(get_llm_service)
) -> ChatService:
    """Get chat service instance"""
    global _chat_service
    if _chat_service is None:
        # Create mock services for now
        from ...services.database import DatabaseService
        from ...services.cache import CacheService
        from ...config.settings import get_settings
        settings = get_settings()
        db = DatabaseService(settings)
        cache = CacheService(settings)
        _chat_service = ChatService(llm_service, db, cache)
    return _chat_service


@router.post("/chat/message", response_model=ChatMessageResponse)
async def send_chat_message(
    request: ChatMessageRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Send a message to the AI customer support chat
    
    This endpoint processes customer messages and returns AI-generated responses
    with context awareness and conversation history.
    """
    try:
        response = await chat_service.send_message(
            message=request.message,
            session_id=request.session_id,
            user_id=request.user_id,
            context=request.context
        )
        
        return ChatMessageResponse(
            response=response["text"],
            session_id=request.session_id,
            provider=response["provider"],
            model=response["model"],
            timestamp=response["timestamp"]
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to process chat message")


@router.get("/chat/history/{session_id}")
async def get_chat_history(
    session_id: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Get chat history for a session"""
    try:
        history = await chat_service._get_conversation_history(session_id)
        return {
            "session_id": session_id,
            "messages": history
        }
    except Exception as e:
        logger.error(f"Error getting chat history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get chat history")

