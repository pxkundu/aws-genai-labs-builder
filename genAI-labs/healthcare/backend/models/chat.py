"""
Healthcare ChatGPT Clone - Chat Data Models
This module defines the database models for chat functionality.
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, Text, DateTime, Integer, Float, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()


class ChatSession(Base):
    """Model for chat sessions."""
    
    __tablename__ = "chat_sessions"
    
    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    message_count = Column(Integer, default=0, nullable=False)
    last_message = Column(Text, nullable=True)
    session_metadata = Column(JSON, nullable=True)
    
    # Relationships
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_chat_sessions_user_id_created_at', 'user_id', 'created_at'),
        Index('idx_chat_sessions_updated_at', 'updated_at'),
    )
    
    def __repr__(self):
        return f"<ChatSession(session_id={self.session_id}, user_id={self.user_id})>"


class ChatMessage(Base):
    """Model for chat messages."""
    
    __tablename__ = "chat_messages"
    
    message_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.session_id"), nullable=False, index=True)
    message = Column(Text, nullable=False)
    message_type = Column(String(20), nullable=False, index=True)  # 'user' or 'ai'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    metadata = Column(JSON, nullable=True)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")
    
    # Indexes
    __table_args__ = (
        Index('idx_chat_messages_session_id_created_at', 'session_id', 'created_at'),
        Index('idx_chat_messages_type_created_at', 'message_type', 'created_at'),
    )
    
    def __repr__(self):
        return f"<ChatMessage(message_id={self.message_id}, session_id={self.session_id}, type={self.message_type})>"


class User(Base):
    """Model for users."""
    
    __tablename__ = "users"
    
    user_id = Column(String(255), primary_key=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), default="user", nullable=False)
    is_active = Column(String(10), default="true", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    user_metadata = Column(JSON, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_users_role_active', 'role', 'is_active'),
        Index('idx_users_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<User(user_id={self.user_id}, username={self.username})>"


class ChatAnalytics(Base):
    """Model for chat analytics data."""
    
    __tablename__ = "chat_analytics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.session_id"), nullable=False, index=True)
    user_id = Column(String(255), nullable=True, index=True)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    model_used = Column(String(100), nullable=False)
    response_time = Column(Float, nullable=False)  # in seconds
    confidence_score = Column(Float, nullable=True)
    user_satisfaction = Column(Integer, nullable=True)  # 1-5 scale
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    metadata = Column(JSON, nullable=True)
    
    # Relationships
    session = relationship("ChatSession")
    
    # Indexes
    __table_args__ = (
        Index('idx_chat_analytics_user_id_created_at', 'user_id', 'created_at'),
        Index('idx_chat_analytics_model_created_at', 'model_used', 'created_at'),
        Index('idx_chat_analytics_satisfaction', 'user_satisfaction'),
    )
    
    def __repr__(self):
        return f"<ChatAnalytics(id={self.id}, session_id={self.session_id}, model={self.model_used})>"


class SystemMetrics(Base):
    """Model for system performance metrics."""
    
    __tablename__ = "system_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(20), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    metadata = Column(JSON, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_system_metrics_name_timestamp', 'metric_name', 'timestamp'),
        Index('idx_system_metrics_timestamp', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<SystemMetrics(id={self.id}, name={self.metric_name}, value={self.metric_value})>"


class KnowledgeBaseItem(Base):
    """Model for knowledge base items."""
    
    __tablename__ = "knowledge_base_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False, index=True)
    content = Column(Text, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    source = Column(String(255), nullable=False)
    tags = Column(JSON, nullable=True)  # List of tags
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_active = Column(String(10), default="true", nullable=False)
    metadata = Column(JSON, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_knowledge_base_category_active', 'category', 'is_active'),
        Index('idx_knowledge_base_updated_at', 'updated_at'),
        Index('idx_knowledge_base_title', 'title'),
    )
    
    def __repr__(self):
        return f"<KnowledgeBaseItem(id={self.id}, title={self.title}, category={self.category})>"


class KnowledgeBaseSearch(Base):
    """Model for knowledge base search analytics."""
    
    __tablename__ = "knowledge_base_searches"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query = Column(Text, nullable=False, index=True)
    results_count = Column(Integer, nullable=False)
    search_time = Column(Float, nullable=False)  # in milliseconds
    user_id = Column(String(255), nullable=True, index=True)
    session_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    metadata = Column(JSON, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_knowledge_base_searches_user_id_created_at', 'user_id', 'created_at'),
        Index('idx_knowledge_base_searches_query_created_at', 'query', 'created_at'),
    )
    
    def __repr__(self):
        return f"<KnowledgeBaseSearch(id={self.id}, query={self.query}, results={self.results_count})>"


class AuditLog(Base):
    """Model for audit logging."""
    
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False, index=True)
    resource_id = Column(String(255), nullable=True, index=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_audit_logs_user_id_created_at', 'user_id', 'created_at'),
        Index('idx_audit_logs_action_created_at', 'action', 'created_at'),
        Index('idx_audit_logs_resource_type_id', 'resource_type', 'resource_id'),
    )
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, user_id={self.user_id}, action={self.action})>"
