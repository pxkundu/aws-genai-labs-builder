"""
Healthcare ChatGPT Clone - Chat Service
This module handles chat session and message management.
"""

import logging
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from models.chat import ChatSession, ChatMessage, ChatAnalytics
from services.cache import cache_chat_history, get_chat_history

logger = logging.getLogger(__name__)


class ChatService:
    """Service for managing chat sessions and messages."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_or_create_session(
        self,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> ChatSession:
        """Get existing session or create a new one."""
        try:
            if session_id:
                session = self.db.query(ChatSession).filter(
                    ChatSession.session_id == session_id
                ).first()
                
                if session:
                    return session
            
            # Create new session
            new_session = ChatSession(
                session_id=str(uuid.uuid4()),
                user_id=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db.add(new_session)
            self.db.commit()
            self.db.refresh(new_session)
            
            logger.info(f"Created new chat session: {new_session.session_id}")
            return new_session
            
        except Exception as e:
            logger.error(f"Error getting/creating session: {e}")
            self.db.rollback()
            raise
    
    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get a chat session by ID."""
        try:
            return self.db.query(ChatSession).filter(
                ChatSession.session_id == session_id
            ).first()
        except Exception as e:
            logger.error(f"Error getting session {session_id}: {e}")
            return None
    
    async def get_sessions(
        self,
        user_id: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[ChatSession]:
        """Get chat sessions with optional filtering."""
        try:
            query = self.db.query(ChatSession)
            
            if user_id:
                query = query.filter(ChatSession.user_id == user_id)
            
            sessions = query.order_by(desc(ChatSession.updated_at)).offset(offset).limit(limit).all()
            
            # Update message counts and last messages
            for session in sessions:
                message_count = self.db.query(ChatMessage).filter(
                    ChatMessage.session_id == session.session_id
                ).count()
                
                last_message = self.db.query(ChatMessage).filter(
                    ChatMessage.session_id == session.session_id
                ).order_by(desc(ChatMessage.created_at)).first()
                
                session.message_count = message_count
                session.last_message = last_message.message if last_message else None
            
            return sessions
            
        except Exception as e:
            logger.error(f"Error getting sessions: {e}")
            return []
    
    async def save_message(
        self,
        session_id: str,
        message: str,
        message_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChatMessage:
        """Save a chat message."""
        try:
            chat_message = ChatMessage(
                message_id=str(uuid.uuid4()),
                session_id=session_id,
                message=message,
                message_type=message_type,
                created_at=datetime.utcnow(),
                metadata=metadata or {}
            )
            
            self.db.add(chat_message)
            self.db.commit()
            self.db.refresh(chat_message)
            
            # Update session
            await self.update_session(session_id)
            
            # Cache the updated chat history
            await self._update_cached_history(session_id)
            
            logger.info(f"Saved message {chat_message.message_id} for session {session_id}")
            return chat_message
            
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            self.db.rollback()
            raise
    
    async def get_messages(
        self,
        session_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[ChatMessage]:
        """Get messages for a chat session."""
        try:
            # Try to get from cache first
            cached_messages = await get_chat_history(session_id)
            if cached_messages and offset == 0:
                return cached_messages[:limit]
            
            # Get from database
            messages = self.db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).order_by(ChatMessage.created_at).offset(offset).limit(limit).all()
            
            # Cache the messages
            if offset == 0:
                await cache_chat_history(session_id, messages)
            
            return messages
            
        except Exception as e:
            logger.error(f"Error getting messages for session {session_id}: {e}")
            return []
    
    async def update_session(self, session_id: str) -> bool:
        """Update session timestamp and metadata."""
        try:
            session = self.db.query(ChatSession).filter(
                ChatSession.session_id == session_id
            ).first()
            
            if session:
                session.updated_at = datetime.utcnow()
                self.db.commit()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating session {session_id}: {e}")
            self.db.rollback()
            return False
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a chat session and all its messages."""
        try:
            # Delete messages first
            self.db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).delete()
            
            # Delete session
            self.db.query(ChatSession).filter(
                ChatSession.session_id == session_id
            ).delete()
            
            self.db.commit()
            
            # Clear cache
            await self._clear_cached_history(session_id)
            
            logger.info(f"Deleted session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {e}")
            self.db.rollback()
            return False
    
    async def record_analytics(
        self,
        session_id: str,
        user_message: str,
        ai_response: str
    ) -> bool:
        """Record chat analytics for monitoring and improvement."""
        try:
            analytics = ChatAnalytics(
                id=str(uuid.uuid4()),
                session_id=session_id,
                query=user_message,
                response=ai_response,
                model_used="ai_service",
                response_time=0.0,  # This would be passed from the AI service
                created_at=datetime.utcnow()
            )
            
            self.db.add(analytics)
            self.db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error recording analytics: {e}")
            self.db.rollback()
            return False
    
    async def get_session_analytics(
        self,
        session_id: str
    ) -> List[ChatAnalytics]:
        """Get analytics for a specific session."""
        try:
            return self.db.query(ChatAnalytics).filter(
                ChatAnalytics.session_id == session_id
            ).order_by(ChatAnalytics.created_at).all()
            
        except Exception as e:
            logger.error(f"Error getting session analytics: {e}")
            return []
    
    async def _update_cached_history(self, session_id: str):
        """Update cached chat history for a session."""
        try:
            messages = self.db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).order_by(ChatMessage.created_at).all()
            
            await cache_chat_history(session_id, messages)
            
        except Exception as e:
            logger.error(f"Error updating cached history: {e}")
    
    async def _clear_cached_history(self, session_id: str):
        """Clear cached chat history for a session."""
        try:
            from services.cache import delete_cache
            await delete_cache(f"chat_history:{session_id}")
            
        except Exception as e:
            logger.error(f"Error clearing cached history: {e}")
    
    async def get_user_chat_stats(self, user_id: str) -> Dict[str, Any]:
        """Get chat statistics for a user."""
        try:
            # Get total sessions
            total_sessions = self.db.query(ChatSession).filter(
                ChatSession.user_id == user_id
            ).count()
            
            # Get total messages
            total_messages = self.db.query(ChatMessage).join(
                ChatSession, ChatMessage.session_id == ChatSession.session_id
            ).filter(ChatSession.user_id == user_id).count()
            
            # Get recent activity
            recent_sessions = self.db.query(ChatSession).filter(
                ChatSession.user_id == user_id
            ).order_by(desc(ChatSession.updated_at)).limit(5).all()
            
            return {
                "total_sessions": total_sessions,
                "total_messages": total_messages,
                "recent_sessions": [
                    {
                        "session_id": session.session_id,
                        "updated_at": session.updated_at,
                        "message_count": session.message_count
                    }
                    for session in recent_sessions
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting user chat stats: {e}")
            return {
                "total_sessions": 0,
                "total_messages": 0,
                "recent_sessions": []
            }
