"""
Legal Question Models for the Legal Compliance AI Platform
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class Jurisdiction(str, Enum):
    """Supported legal jurisdictions"""
    US = "US"
    UK = "UK"
    EU = "EU"
    DE = "DE"  # Germany
    FR = "FR"  # France
    IT = "IT"  # Italy
    ES = "ES"  # Spain
    CA = "CA"  # Canada
    AU = "AU"  # Australia


class PracticeArea(str, Enum):
    """Legal practice areas"""
    GENERAL = "general"
    CONTRACT = "contract"
    TORT = "tort"
    CRIMINAL = "criminal"
    CORPORATE = "corporate"
    EMPLOYMENT = "employment"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    REAL_ESTATE = "real_estate"
    FAMILY = "family"
    IMMIGRATION = "immigration"
    TAX = "tax"
    REGULATORY = "regulatory"


class QuestionComplexity(str, Enum):
    """Question complexity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class LegalQuestionRequest(BaseModel):
    """Request model for legal questions"""
    
    question: str = Field(..., min_length=10, max_length=2000, description="The legal question to be answered")
    jurisdiction: Jurisdiction = Field(default=Jurisdiction.US, description="Legal jurisdiction")
    practice_area: PracticeArea = Field(default=PracticeArea.GENERAL, description="Legal practice area")
    context: Optional[str] = Field(None, max_length=1000, description="Additional context for the question")
    models: Optional[List[str]] = Field(None, description="Specific LLM models to use")
    include_comparison: bool = Field(default=True, description="Include response comparison analysis")
    
    @validator('question')
    def validate_question(cls, v):
        if not v.strip():
            raise ValueError('Question cannot be empty')
        return v.strip()
    
    @validator('context')
    def validate_context(cls, v):
        if v is not None and not v.strip():
            return None
        return v.strip() if v else None
    
    class Config:
        schema_extra = {
            "example": {
                "question": "What are the key requirements for a valid contract under US law?",
                "jurisdiction": "US",
                "practice_area": "contract",
                "context": "This is for a business partnership agreement",
                "models": ["gpt-4-turbo-preview", "claude-3-5-sonnet-20241022"],
                "include_comparison": True
            }
        }


class LLMResponse(BaseModel):
    """Response from a single LLM"""
    
    model: str = Field(..., description="LLM model name")
    response: str = Field(..., description="The generated response")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    tokens_used: int = Field(..., ge=0, description="Number of tokens used")
    processing_time: float = Field(..., ge=0.0, description="Processing time in seconds")
    timestamp: str = Field(..., description="Response timestamp")
    error: Optional[str] = Field(None, description="Error message if any")
    
    class Config:
        schema_extra = {
            "example": {
                "model": "gpt-4-turbo-preview",
                "response": "Under US contract law, a valid contract requires...",
                "confidence": 0.95,
                "tokens_used": 1250,
                "processing_time": 3.2,
                "timestamp": "2024-01-15T10:30:00Z",
                "error": None
            }
        }


class ResponseComparison(BaseModel):
    """Comparison analysis between multiple LLM responses"""
    
    consensus_analysis: Dict[str, Any] = Field(..., description="Consensus analysis between responses")
    key_differences: List[Dict[str, str]] = Field(..., description="Key differences identified")
    quality_ranking: List[Dict[str, Any]] = Field(..., description="Quality ranking of responses")
    summary: str = Field(..., description="Summary of the comparison")
    
    class Config:
        schema_extra = {
            "example": {
                "consensus_analysis": {
                    "consensus_score": 85.5,
                    "consensus_level": "high",
                    "common_themes": ["contract formation", "consideration", "legal capacity"]
                },
                "key_differences": [
                    {
                        "models": "gpt-4 vs claude-3.5",
                        "difference": "Response length significantly different",
                        "details": "gpt-4: 1200 chars, claude-3.5: 800 chars"
                    }
                ],
                "quality_ranking": [
                    {
                        "model": "gpt-4-turbo-preview",
                        "quality_score": 8.5,
                        "ranking_factors": {
                            "length": 1200,
                            "processing_time": 3.2,
                            "tokens_used": 1250,
                            "has_error": False
                        }
                    }
                ],
                "summary": "High consensus - responses are generally aligned. GPT-4 provides the most comprehensive response."
            }
        }


class LegalQuestionResponse(BaseModel):
    """Complete response to a legal question"""
    
    question_id: str = Field(..., description="Unique question identifier")
    question: str = Field(..., description="The original question")
    jurisdiction: Jurisdiction = Field(..., description="Legal jurisdiction")
    practice_area: PracticeArea = Field(..., description="Legal practice area")
    complexity: QuestionComplexity = Field(..., description="Assessed question complexity")
    
    # LLM Responses
    responses: Dict[str, LLMResponse] = Field(..., description="Responses from different LLMs")
    comparison: Optional[ResponseComparison] = Field(None, description="Response comparison analysis")
    
    # Metadata
    timestamp: str = Field(..., description="Response timestamp")
    processing_time: float = Field(..., ge=0.0, description="Total processing time")
    cached: bool = Field(default=False, description="Whether response was served from cache")
    
    # Recommendations
    recommended_model: str = Field(..., description="Recommended model based on quality analysis")
    confidence_level: str = Field(..., description="Overall confidence level")
    follow_up_suggestions: List[str] = Field(default_factory=list, description="Suggested follow-up questions")
    
    class Config:
        schema_extra = {
            "example": {
                "question_id": "q_20240115_103000_abc123",
                "question": "What are the key requirements for a valid contract under US law?",
                "jurisdiction": "US",
                "practice_area": "contract",
                "complexity": "medium",
                "responses": {
                    "gpt-4-turbo-preview": {
                        "model": "gpt-4-turbo-preview",
                        "response": "Under US contract law...",
                        "confidence": 0.95,
                        "tokens_used": 1250,
                        "processing_time": 3.2,
                        "timestamp": "2024-01-15T10:30:00Z",
                        "error": None
                    }
                },
                "comparison": {
                    "consensus_analysis": {
                        "consensus_score": 85.5,
                        "consensus_level": "high"
                    },
                    "key_differences": [],
                    "quality_ranking": [],
                    "summary": "High consensus among responses"
                },
                "timestamp": "2024-01-15T10:30:05Z",
                "processing_time": 5.1,
                "cached": False,
                "recommended_model": "gpt-4-turbo-preview",
                "confidence_level": "high",
                "follow_up_suggestions": [
                    "What happens if one party breaches the contract?",
                    "How can I ensure my contract is enforceable?",
                    "What are common contract pitfalls to avoid?"
                ]
            }
        }


class QuestionHistory(BaseModel):
    """Question history entry"""
    
    question_id: str = Field(..., description="Unique question identifier")
    question: str = Field(..., description="The original question")
    jurisdiction: Jurisdiction = Field(..., description="Legal jurisdiction")
    practice_area: PracticeArea = Field(..., description="Legal practice area")
    timestamp: datetime = Field(..., description="When the question was asked")
    response_count: int = Field(..., ge=0, description="Number of responses received")
    recommended_model: str = Field(..., description="Recommended model")
    confidence_level: str = Field(..., description="Overall confidence level")


class LegalKnowledgeEntry(BaseModel):
    """Legal knowledge base entry"""
    
    id: str = Field(..., description="Unique identifier")
    title: str = Field(..., description="Entry title")
    content: str = Field(..., description="Entry content")
    jurisdiction: Jurisdiction = Field(..., description="Applicable jurisdiction")
    practice_area: PracticeArea = Field(..., description="Practice area")
    tags: List[str] = Field(default_factory=list, description="Content tags")
    last_updated: datetime = Field(..., description="Last update timestamp")
    source: Optional[str] = Field(None, description="Source of the information")
    authority_level: str = Field(default="medium", description="Authority level (high/medium/low)")


class ErrorResponse(BaseModel):
    """Error response model"""
    
    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code")
    timestamp: str = Field(..., description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Request identifier for tracking")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    
    class Config:
        schema_extra = {
            "example": {
                "error": "Invalid jurisdiction specified",
                "error_code": "INVALID_JURISDICTION",
                "timestamp": "2024-01-15T10:30:00Z",
                "request_id": "req_abc123",
                "details": {
                    "provided_jurisdiction": "XX",
                    "supported_jurisdictions": ["US", "UK", "EU", "DE", "FR", "IT", "ES", "CA", "AU"]
                }
            }
        }


class HealthCheck(BaseModel):
    """Health check response"""
    
    status: str = Field(..., description="Service status")
    timestamp: str = Field(..., description="Check timestamp")
    version: str = Field(..., description="Service version")
    uptime: float = Field(..., description="Service uptime in seconds")
    dependencies: Dict[str, str] = Field(..., description="Dependency status")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-15T10:30:00Z",
                "version": "1.0.0",
                "uptime": 3600.5,
                "dependencies": {
                    "database": "healthy",
                    "redis": "healthy",
                    "openai": "healthy",
                    "anthropic": "healthy",
                    "google": "healthy"
                }
            }
        }
