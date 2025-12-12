"""
Review Routes
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from ...services.llm_service import LLMService
from ...services.database import DatabaseService
from ...services.cache import CacheService

logger = logging.getLogger(__name__)
router = APIRouter()


class AnalyzeReviewRequest(BaseModel):
    """Request model for review analysis"""
    review_text: str = Field(..., description="Review text to analyze")
    product_id: Optional[str] = Field(None, description="Product ID")


class AnalyzeReviewResponse(BaseModel):
    """Response model for review analysis"""
    sentiment: str
    confidence: float
    key_points: list[str]
    summary: str
    timestamp: str


# Initialize services
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get LLM service instance"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


@router.post("/reviews/analyze", response_model=AnalyzeReviewResponse)
async def analyze_review(
    request: AnalyzeReviewRequest,
    llm_service: LLMService = Depends(get_llm_service)
):
    """
    Analyze customer review sentiment and extract insights
    
    Uses AI to analyze review text, determine sentiment, and extract
    key points for product improvement.
    """
    try:
        # Analyze sentiment
        sentiment_result = await llm_service.analyze_sentiment(request.review_text)
        
        # Extract key points
        system_prompt = """You are a review analysis expert.
        Extract key points from the review including:
        - What the customer liked
        - What the customer didn't like
        - Specific issues mentioned
        - Suggestions for improvement
        
        Provide a brief summary and list of key points."""
        
        prompt = f"Analyze this review and extract key insights: {request.review_text}"
        
        analysis_response = await llm_service.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=300
        )
        
        # Parse response (in real implementation, use structured output)
        return AnalyzeReviewResponse(
            sentiment=sentiment_result.get("sentiment", "neutral"),
            confidence=sentiment_result.get("confidence", 0.5),
            key_points=[],  # Would parse from analysis_response
            summary=analysis_response["text"],
            timestamp=sentiment_result.get("timestamp", "")
        )
        
    except Exception as e:
        logger.error(f"Error analyzing review: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to analyze review")

