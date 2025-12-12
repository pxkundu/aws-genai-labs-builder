"""
Chat Service for E-Commerce Platform
AI-powered customer support chat
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..services.llm_service import LLMService
from ..services.database import DatabaseService
from ..services.cache import CacheService

logger = logging.getLogger(__name__)


class ChatService:
    """Service for handling customer support chat"""
    
    def __init__(
        self,
        llm_service: LLMService,
        db_service: DatabaseService,
        cache_service: CacheService
    ):
        self.llm_service = llm_service
        self.db_service = db_service
        self.cache_service = cache_service
    
    async def send_message(
        self,
        message: str,
        session_id: str,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send a message and get AI response
        
        Args:
            message: User message
            session_id: Chat session ID
            user_id: Optional user ID
            context: Additional context
        
        Returns:
            AI response with metadata
        """
        try:
            # Get conversation history
            history = await self._get_conversation_history(session_id)
            
            # Get user context if available
            user_context = {}
            if user_id:
                user_context = await self._get_user_context(user_id)
            
            # Generate response
            response = await self._generate_response(
                message, history, user_context, context
            )
            
            # Save conversation
            await self._save_message(session_id, "user", message)
            await self._save_message(session_id, "assistant", response["text"])
            
            return response
            
        except Exception as e:
            logger.error(f"Error sending message: {e}", exc_info=True)
            raise
    
    async def _get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get conversation history for session"""
        # In real implementation, fetch from database
        cache_key = f"chat_history:{session_id}"
        cached = await self.cache_service.get(cache_key)
        if cached:
            return cached
        return []
    
    async def _get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Get user context (orders, preferences, etc.)"""
        # In real implementation, fetch from database
        return {
            "user_id": user_id,
            "recent_orders": [],
            "preferences": {}
        }
    
    async def _generate_response(
        self,
        message: str,
        history: List[Dict[str, Any]],
        user_context: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate AI response"""
        
        system_prompt = """You are a helpful customer support assistant for an e-commerce platform.
        Your role is to:
        1. Answer questions about products, orders, and services
        2. Help with order tracking and status
        3. Provide product information and recommendations
        4. Assist with returns, refunds, and exchanges
        5. Escalate complex issues when necessary
        
        Guidelines:
        - Be friendly, professional, and empathetic
        - Provide accurate information
        - If you don't know something, admit it and offer to connect with a human agent
        - Keep responses concise but helpful
        - Use the conversation history for context"""
        
        # Build prompt with context
        prompt = f"User message: {message}\n\n"
        
        if user_context:
            prompt += f"User context: {user_context}\n\n"
        
        if context:
            prompt += f"Additional context: {context}\n\n"
        
        if history:
            prompt += "Conversation history:\n"
            for msg in history[-5:]:  # Last 5 messages for context
                prompt += f"- {msg.get('role', 'user')}: {msg.get('content', '')}\n"
            prompt += "\n"
        
        prompt += "Please provide a helpful response."
        
        response = await self.llm_service.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=500
        )
        
        return {
            **response,
            "session_id": None,  # Will be set by caller
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _save_message(
        self,
        session_id: str,
        role: str,
        content: str
    ):
        """Save message to database"""
        # In real implementation, save to database
        cache_key = f"chat_history:{session_id}"
        history = await self._get_conversation_history(session_id)
        history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })
        await self.cache_service.set(cache_key, history, ttl=86400)  # 24 hours

