"""
Knowledge Base API routes
Handles knowledge management endpoints
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
import structlog

from services.ai_service import AIService
from services.database import DatabaseService

logger = structlog.get_logger(__name__)

router = APIRouter()


class KnowledgeArticle(BaseModel):
    """Knowledge article model"""
    id: Optional[str] = Field(None, description="Article ID")
    title: str = Field(..., description="Article title")
    content: str = Field(..., description="Article content")
    category: str = Field(..., description="Article category")
    tags: List[str] = Field(default=[], description="Article tags")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class KnowledgeSearchRequest(BaseModel):
    """Knowledge search request model"""
    query: str = Field(..., description="Search query")
    customer_id: str = Field(..., description="Customer ID")
    limit: int = Field(default=10, description="Maximum results")
    category: Optional[str] = Field(None, description="Filter by category")


class KnowledgeSearchResponse(BaseModel):
    """Knowledge search response model"""
    query: str = Field(..., description="Search query")
    results: List[Dict[str, Any]] = Field(..., description="Search results")
    total_results: int = Field(..., description="Total number of results")
    search_time: float = Field(..., description="Search time in seconds")


# Initialize AI service
ai_service = AIService()


@router.post("/knowledge/search", response_model=KnowledgeSearchResponse)
async def search_knowledge_base(
    request: KnowledgeSearchRequest,
    db: DatabaseService = Depends()
):
    """Search knowledge base"""
    try:
        logger.info("Searching knowledge base", 
                   query=request.query,
                   customer_id=request.customer_id)
        
        # Get customer context
        customer = await db.get_customer(request.customer_id)
        customer_context = {
            "customer_id": request.customer_id,
            "tier": customer.get("tier") if customer else None,
            "preferences": customer.get("preferences", {}) if customer else {}
        }
        
        # Search knowledge base
        search_results = await ai_service.search_knowledge_base(
            request.query, customer_context
        )
        
        # Filter by category if specified
        if request.category:
            search_results["results"] = [
                result for result in search_results["results"]
                if result.get("category") == request.category
            ]
        
        # Limit results
        search_results["results"] = search_results["results"][:request.limit]
        
        return KnowledgeSearchResponse(
            query=request.query,
            results=search_results["results"],
            total_results=len(search_results["results"]),
            search_time=search_results.get("search_time", 0.0)
        )
        
    except Exception as e:
        logger.error("Knowledge base search failed", error=str(e))
        raise HTTPException(status_code=500, detail="Knowledge base search failed")


@router.get("/knowledge/articles", response_model=List[KnowledgeArticle])
async def get_knowledge_articles(
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(10, description="Maximum results"),
    offset: int = Query(0, description="Offset for pagination"),
    db: DatabaseService = Depends()
):
    """Get knowledge articles"""
    try:
        # Build query
        query = {}
        if category:
            query["category"] = category
        
        # Get articles from database
        articles = await db.knowledge_collection.find(query).skip(offset).limit(limit).to_list(length=None)
        
        return [
            KnowledgeArticle(
                id=str(article["_id"]),
                title=article["title"],
                content=article["content"],
                category=article["category"],
                tags=article.get("tags", []),
                created_at=article.get("created_at"),
                updated_at=article.get("updated_at")
            )
            for article in articles
        ]
        
    except Exception as e:
        logger.error("Failed to get knowledge articles", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get knowledge articles")


@router.post("/knowledge/articles", response_model=KnowledgeArticle)
async def create_knowledge_article(
    article: KnowledgeArticle,
    db: DatabaseService = Depends()
):
    """Create knowledge article"""
    try:
        logger.info("Creating knowledge article", title=article.title)
        
        article_data = article.dict()
        article_data["created_at"] = datetime.utcnow()
        article_data["updated_at"] = datetime.utcnow()
        
        # Save to database
        result = await db.knowledge_collection.insert_one(article_data)
        
        # Return created article
        article_data["id"] = str(result.inserted_id)
        del article_data["_id"]
        
        return KnowledgeArticle(**article_data)
        
    except Exception as e:
        logger.error("Failed to create knowledge article", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create knowledge article")


@router.put("/knowledge/articles/{article_id}", response_model=KnowledgeArticle)
async def update_knowledge_article(
    article_id: str,
    article: KnowledgeArticle,
    db: DatabaseService = Depends()
):
    """Update knowledge article"""
    try:
        logger.info("Updating knowledge article", article_id=article_id)
        
        article_data = article.dict()
        article_data["updated_at"] = datetime.utcnow()
        
        # Update in database
        result = await db.knowledge_collection.update_one(
            {"_id": article_id},
            {"$set": article_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Return updated article
        article_data["id"] = article_id
        return KnowledgeArticle(**article_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update knowledge article", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to update knowledge article")


@router.delete("/knowledge/articles/{article_id}")
async def delete_knowledge_article(
    article_id: str,
    db: DatabaseService = Depends()
):
    """Delete knowledge article"""
    try:
        logger.info("Deleting knowledge article", article_id=article_id)
        
        result = await db.knowledge_collection.delete_one({"_id": article_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Article not found")
        
        return {"message": "Article deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete knowledge article", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to delete knowledge article")


@router.get("/knowledge/categories")
async def get_knowledge_categories(db: DatabaseService = Depends()):
    """Get knowledge base categories"""
    try:
        # Get distinct categories
        categories = await db.knowledge_collection.distinct("category")
        
        return {"categories": categories}
        
    except Exception as e:
        logger.error("Failed to get knowledge categories", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get knowledge categories")
