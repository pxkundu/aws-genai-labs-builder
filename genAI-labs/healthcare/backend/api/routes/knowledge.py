"""
Healthcare ChatGPT Clone - Knowledge Base API Routes
This module handles knowledge base management and search endpoints.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from services.knowledge_service import KnowledgeService
from services.database import get_db
from config.settings import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


# Request/Response Models
class KnowledgeSearchRequest(BaseModel):
    """Request model for knowledge base search."""
    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    category: Optional[str] = Field(None, description="Knowledge category filter")
    limit: int = Field(default=10, ge=1, le=50, description="Maximum number of results")
    include_content: bool = Field(default=True, description="Include full content in results")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "diabetes symptoms",
                "category": "medical_guidelines",
                "limit": 5,
                "include_content": True
            }
        }


class KnowledgeItem(BaseModel):
    """Model for knowledge base items."""
    id: str
    title: str
    content: str
    category: str
    source: str
    created_at: datetime
    updated_at: datetime
    tags: List[str] = []
    relevance_score: Optional[float] = None
    
    class Config:
        schema_extra = {
            "example": {
                "id": "kb_123",
                "title": "Diabetes Symptoms and Management",
                "content": "Common symptoms of diabetes include...",
                "category": "medical_guidelines",
                "source": "medical_guidelines.pdf",
                "created_at": "2024-01-15T10:00:00Z",
                "updated_at": "2024-01-15T10:00:00Z",
                "tags": ["diabetes", "symptoms", "management"],
                "relevance_score": 0.95
            }
        }


class KnowledgeSearchResponse(BaseModel):
    """Response model for knowledge base search."""
    query: str
    results: List[KnowledgeItem]
    total_results: int
    search_time_ms: int
    suggestions: Optional[List[str]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "query": "diabetes symptoms",
                "results": [
                    {
                        "id": "kb_123",
                        "title": "Diabetes Symptoms and Management",
                        "content": "Common symptoms of diabetes include...",
                        "category": "medical_guidelines",
                        "source": "medical_guidelines.pdf",
                        "created_at": "2024-01-15T10:00:00Z",
                        "updated_at": "2024-01-15T10:00:00Z",
                        "tags": ["diabetes", "symptoms", "management"],
                        "relevance_score": 0.95
                    }
                ],
                "total_results": 1,
                "search_time_ms": 150,
                "suggestions": ["diabetes treatment", "diabetes prevention"]
            }
        }


class KnowledgeUploadRequest(BaseModel):
    """Request model for knowledge base upload."""
    title: str = Field(..., min_length=1, max_length=200, description="Title of the knowledge item")
    content: str = Field(..., min_length=1, description="Content of the knowledge item")
    category: str = Field(..., min_length=1, max_length=50, description="Category of the knowledge item")
    source: str = Field(..., min_length=1, max_length=100, description="Source of the knowledge item")
    tags: List[str] = Field(default=[], description="Tags for the knowledge item")
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Hypertension Management Guidelines",
                "content": "Hypertension, or high blood pressure, is a common condition...",
                "category": "medical_guidelines",
                "source": "cardiovascular_guidelines.pdf",
                "tags": ["hypertension", "blood pressure", "cardiovascular"]
            }
        }


# Dependencies
async def get_knowledge_service(db: Session = Depends(get_db)) -> KnowledgeService:
    """Get knowledge service instance."""
    return KnowledgeService(db)


# API Endpoints
@router.post("/search", response_model=KnowledgeSearchResponse)
async def search_knowledge(
    request: KnowledgeSearchRequest,
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """
    Search the knowledge base for relevant information.
    
    Performs semantic search across the healthcare knowledge base
    to find relevant information for user queries.
    """
    try:
        start_time = datetime.utcnow()
        
        # Perform search
        results = await knowledge_service.search(
            query=request.query,
            category=request.category,
            limit=request.limit,
            include_content=request.include_content
        )
        
        # Calculate search time
        search_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Get suggestions
        suggestions = await knowledge_service.get_suggestions(request.query)
        
        logger.info(f"Knowledge search completed for query: {request.query}")
        
        return KnowledgeSearchResponse(
            query=request.query,
            results=[
                KnowledgeItem(
                    id=item["id"],
                    title=item["title"],
                    content=item["content"],
                    category=item["category"],
                    source=item["source"],
                    created_at=item["created_at"],
                    updated_at=item["updated_at"],
                    tags=item["tags"],
                    relevance_score=item["relevance_score"]
                )
                for item in results["items"]
            ],
            total_results=results["total"],
            search_time_ms=int(search_time),
            suggestions=suggestions
        )
        
    except Exception as e:
        logger.error(f"Error searching knowledge base: {e}")
        raise HTTPException(status_code=500, detail="Failed to search knowledge base")


@router.get("/search", response_model=KnowledgeSearchResponse)
async def search_knowledge_get(
    query: str = Query(..., min_length=1, max_length=500, description="Search query"),
    category: Optional[str] = Query(None, description="Knowledge category filter"),
    limit: int = Query(default=10, ge=1, le=50, description="Maximum number of results"),
    include_content: bool = Query(default=True, description="Include full content in results"),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """
    Search the knowledge base using GET method.
    
    Alternative GET endpoint for knowledge base search.
    """
    request = KnowledgeSearchRequest(
        query=query,
        category=category,
        limit=limit,
        include_content=include_content
    )
    
    return await search_knowledge(request, knowledge_service)


@router.get("/categories")
async def get_categories(knowledge_service: KnowledgeService = Depends(get_knowledge_service)):
    """
    Get all available knowledge base categories.
    
    Returns a list of all categories in the knowledge base.
    """
    try:
        categories = await knowledge_service.get_categories()
        
        return {
            "categories": categories,
            "total": len(categories)
        }
        
    except Exception as e:
        logger.error(f"Error retrieving categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve categories")


@router.get("/items/{item_id}", response_model=KnowledgeItem)
async def get_knowledge_item(
    item_id: str,
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """
    Get a specific knowledge base item by ID.
    
    Returns detailed information about a specific knowledge item.
    """
    try:
        item = await knowledge_service.get_item(item_id)
        
        if not item:
            raise HTTPException(status_code=404, detail="Knowledge item not found")
        
        return KnowledgeItem(
            id=item["id"],
            title=item["title"],
            content=item["content"],
            category=item["category"],
            source=item["source"],
            created_at=item["created_at"],
            updated_at=item["updated_at"],
            tags=item["tags"],
            relevance_score=item.get("relevance_score")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving knowledge item: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve knowledge item")


@router.post("/items", response_model=KnowledgeItem)
async def create_knowledge_item(
    request: KnowledgeUploadRequest,
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """
    Create a new knowledge base item.
    
    Adds a new item to the healthcare knowledge base.
    """
    try:
        item = await knowledge_service.create_item(
            title=request.title,
            content=request.content,
            category=request.category,
            source=request.source,
            tags=request.tags
        )
        
        logger.info(f"Knowledge item created: {item['id']}")
        
        return KnowledgeItem(
            id=item["id"],
            title=item["title"],
            content=item["content"],
            category=item["category"],
            source=item["source"],
            created_at=item["created_at"],
            updated_at=item["updated_at"],
            tags=item["tags"]
        )
        
    except Exception as e:
        logger.error(f"Error creating knowledge item: {e}")
        raise HTTPException(status_code=500, detail="Failed to create knowledge item")


@router.put("/items/{item_id}", response_model=KnowledgeItem)
async def update_knowledge_item(
    item_id: str,
    request: KnowledgeUploadRequest,
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """
    Update an existing knowledge base item.
    
    Updates an existing item in the healthcare knowledge base.
    """
    try:
        # Check if item exists
        existing_item = await knowledge_service.get_item(item_id)
        if not existing_item:
            raise HTTPException(status_code=404, detail="Knowledge item not found")
        
        # Update item
        item = await knowledge_service.update_item(
            item_id=item_id,
            title=request.title,
            content=request.content,
            category=request.category,
            source=request.source,
            tags=request.tags
        )
        
        logger.info(f"Knowledge item updated: {item_id}")
        
        return KnowledgeItem(
            id=item["id"],
            title=item["title"],
            content=item["content"],
            category=item["category"],
            source=item["source"],
            created_at=item["created_at"],
            updated_at=item["updated_at"],
            tags=item["tags"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating knowledge item: {e}")
        raise HTTPException(status_code=500, detail="Failed to update knowledge item")


@router.delete("/items/{item_id}")
async def delete_knowledge_item(
    item_id: str,
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """
    Delete a knowledge base item.
    
    Removes an item from the healthcare knowledge base.
    """
    try:
        # Check if item exists
        existing_item = await knowledge_service.get_item(item_id)
        if not existing_item:
            raise HTTPException(status_code=404, detail="Knowledge item not found")
        
        # Delete item
        await knowledge_service.delete_item(item_id)
        
        logger.info(f"Knowledge item deleted: {item_id}")
        
        return {"message": "Knowledge item deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting knowledge item: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete knowledge item")


@router.post("/sync")
async def sync_knowledge_base(knowledge_service: KnowledgeService = Depends(get_knowledge_service)):
    """
    Sync knowledge base with S3 storage.
    
    Synchronizes the local knowledge base with the S3 storage bucket.
    """
    try:
        result = await knowledge_service.sync_with_s3()
        
        logger.info("Knowledge base sync completed")
        
        return {
            "message": "Knowledge base sync completed",
            "items_processed": result["items_processed"],
            "items_updated": result["items_updated"],
            "items_created": result["items_created"],
            "sync_time": result["sync_time"]
        }
        
    except Exception as e:
        logger.error(f"Error syncing knowledge base: {e}")
        raise HTTPException(status_code=500, detail="Failed to sync knowledge base")
