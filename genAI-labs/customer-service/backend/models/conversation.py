"""
Conversation and message models
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class MessageRole(str, Enum):
    """Message role enumeration"""
    CUSTOMER = "customer"
    ASSISTANT = "assistant"
    AGENT = "agent"
    SYSTEM = "system"


class ConversationStatus(str, Enum):
    """Conversation status enumeration"""
    ACTIVE = "active"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Message(BaseModel):
    """Message model"""
    role: MessageRole = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class CustomerContext(BaseModel):
    """Customer context model"""
    customer_id: str = Field(..., description="Customer ID")
    name: Optional[str] = Field(None, description="Customer name")
    email: Optional[str] = Field(None, description="Customer email")
    tier: Optional[str] = Field(None, description="Customer tier")
    preferences: Optional[Dict[str, Any]] = Field(default=None, description="Customer preferences")
    history: Optional[List[Dict[str, Any]]] = Field(default=None, description="Interaction history")


class Conversation(BaseModel):
    """Conversation model"""
    id: Optional[str] = Field(None, description="Conversation ID")
    customer_id: str = Field(..., description="Customer ID")
    session_id: str = Field(..., description="Session ID")
    messages: List[Message] = Field(default=[], description="Conversation messages")
    status: ConversationStatus = Field(default=ConversationStatus.ACTIVE, description="Conversation status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    
    class Config:
        use_enum_values = True


class IntentAnalysis(BaseModel):
    """Intent analysis model"""
    intent: str = Field(..., description="Detected intent")
    confidence: float = Field(..., description="Confidence score")
    entities: List[Dict[str, Any]] = Field(default=[], description="Detected entities")
    sentiment: Dict[str, Any] = Field(default={}, description="Sentiment analysis")
    urgency: str = Field(default="Low", description="Urgency level")
    suggested_actions: List[str] = Field(default=[], description="Suggested actions")


class AIResponse(BaseModel):
    """AI response model"""
    response_text: str = Field(..., description="Generated response text")
    intent: str = Field(..., description="Detected intent")
    confidence: float = Field(..., description="Confidence score")
    escalation_needed: bool = Field(default=False, description="Whether escalation is needed")
    suggested_actions: List[str] = Field(default=[], description="Suggested actions")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")
