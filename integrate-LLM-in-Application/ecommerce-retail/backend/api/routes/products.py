"""
Product Routes
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from ...services.llm_service import LLMService
from ...services.database import DatabaseService
from ...services.cache import CacheService

logger = logging.getLogger(__name__)
router = APIRouter()


class GenerateDescriptionRequest(BaseModel):
    """Request model for generating product description"""
    product_name: str = Field(..., description="Product name")
    features: list[str] = Field(default=[], description="Product features")
    category: Optional[str] = Field(None, description="Product category")
    tone: str = Field(default="professional", description="Writing tone")
    max_length: int = Field(default=200, description="Maximum description length")


class GenerateDescriptionResponse(BaseModel):
    """Response model for generated description"""
    description: str
    provider: str
    model: str
    timestamp: str


# Initialize services (in production, use dependency injection)
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get LLM service instance"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


@router.post("/products/generate-description", response_model=GenerateDescriptionResponse)
async def generate_product_description(
    request: GenerateDescriptionRequest,
    llm_service: LLMService = Depends(get_llm_service)
):
    """
    Generate product description using LLM
    
    This endpoint uses AI to generate compelling, SEO-friendly product descriptions
    based on product features and specifications.
    """
    try:
        system_prompt = f"""You are an expert e-commerce copywriter.
        Generate a compelling product description with the following requirements:
        - Tone: {request.tone}
        - Maximum length: {request.max_length} words
        - Include key features naturally
        - SEO-friendly and engaging
        - Highlight benefits, not just features
        - Create urgency and desire"""
        
        prompt = f"""
        Product Name: {request.product_name}
        Category: {request.category or 'General'}
        Features: {', '.join(request.features)}
        
        Generate a compelling product description.
        """
        
        response = await llm_service.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.8,
            max_tokens=500
        )
        
        return GenerateDescriptionResponse(
            description=response["text"],
            provider=response["provider"],
            model=response["model"],
            timestamp=response["timestamp"]
        )
        
    except Exception as e:
        logger.error(f"Error generating product description: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate product description")


@router.get("/products/{product_id}")
async def get_product(product_id: str):
    """Get product by ID"""
    # In real implementation, fetch from database
    return {
        "product_id": product_id,
        "name": "Sample Product",
        "description": "Sample description",
        "price": 99.99,
        "category": "Electronics"
    }

