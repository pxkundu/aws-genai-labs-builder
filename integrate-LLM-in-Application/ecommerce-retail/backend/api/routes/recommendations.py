"""
Recommendation Routes
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from ...services.recommendation_service import RecommendationService
from ...services.llm_service import LLMService
from ...services.database import DatabaseService
from ...services.cache import CacheService

logger = logging.getLogger(__name__)
router = APIRouter()


class RecommendationRequest(BaseModel):
    """Request model for recommendations"""
    user_id: str = Field(..., description="User ID")
    product_id: Optional[str] = Field(None, description="Optional product ID for similar products")
    context: Optional[dict] = Field(None, description="Additional context")


class RecommendationResponse(BaseModel):
    """Response model for recommendations"""
    recommendations: list[dict]
    user_id: str
    timestamp: str


# Initialize services
_llm_service: Optional[LLMService] = None
_recommendation_service: Optional[RecommendationService] = None


def get_llm_service() -> LLMService:
    """Get LLM service instance"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


def get_recommendation_service(
    llm_service: LLMService = Depends(get_llm_service)
) -> RecommendationService:
    """Get recommendation service instance"""
    global _recommendation_service
    if _recommendation_service is None:
        # Create mock services for now
        from ...services.database import DatabaseService
        from ...services.cache import CacheService
        from ...config.settings import get_settings
        settings = get_settings()
        db = DatabaseService(settings)
        cache = CacheService(settings)
        _recommendation_service = RecommendationService(llm_service, db, cache)
    return _recommendation_service


@router.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(
    request: RecommendationRequest,
    recommendation_service: RecommendationService = Depends(get_recommendation_service)
):
    """
    Get personalized product recommendations
    
    Uses AI to analyze user behavior and generate personalized product recommendations.
    """
    try:
        recommendations = await recommendation_service.get_recommendations(
            user_id=request.user_id,
            product_id=request.product_id,
            context=request.context
        )
        
        from datetime import datetime
        return RecommendationResponse(
            recommendations=recommendations,
            user_id=request.user_id,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get recommendations")

