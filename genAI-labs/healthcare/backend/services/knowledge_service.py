"""
Healthcare ChatGPT Clone - Knowledge Service
This module handles knowledge base management and search.
"""

import logging
import uuid
import boto3
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from botocore.exceptions import ClientError

from models.chat import KnowledgeBaseItem, KnowledgeBaseSearch
from services.cache import cache_knowledge_search, get_cached_knowledge_search
from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class KnowledgeService:
    """Service for managing healthcare knowledge base."""
    
    def __init__(self, db: Session):
        self.db = db
        self.s3_client = boto3.client('s3', region_name=settings.AWS_REGION)
    
    async def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10,
        include_content: bool = True
    ) -> Dict[str, Any]:
        """Search the knowledge base for relevant information."""
        try:
            # Check cache first
            cached_results = await get_cached_knowledge_search(query)
            if cached_results:
                return cached_results
            
            # Build search query
            search_query = self.db.query(KnowledgeBaseItem).filter(
                KnowledgeBaseItem.is_active == "true"
            )
            
            if category:
                search_query = search_query.filter(
                    KnowledgeBaseItem.category == category
                )
            
            # Simple text search (in production, you'd use full-text search)
            search_terms = query.lower().split()
            conditions = []
            
            for term in search_terms:
                conditions.append(
                    or_(
                        KnowledgeBaseItem.title.ilike(f"%{term}%"),
                        KnowledgeBaseItem.content.ilike(f"%{term}%")
                    )
                )
            
            if conditions:
                search_query = search_query.filter(and_(*conditions))
            
            # Execute search
            results = search_query.order_by(desc(KnowledgeBaseItem.updated_at)).limit(limit).all()
            
            # Format results
            formatted_results = []
            for item in results:
                result_item = {
                    "id": item.id,
                    "title": item.title,
                    "category": item.category,
                    "source": item.source,
                    "created_at": item.created_at,
                    "updated_at": item.updated_at,
                    "tags": item.tags or [],
                    "relevance_score": self._calculate_relevance_score(query, item)
                }
                
                if include_content:
                    result_item["content"] = item.content
                
                formatted_results.append(result_item)
            
            # Sort by relevance score
            formatted_results.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            # Record search analytics
            await self._record_search_analytics(query, len(formatted_results))
            
            # Cache results
            search_results = {
                "items": formatted_results,
                "total": len(formatted_results),
                "query": query,
                "category": category
            }
            await cache_knowledge_search(query, search_results)
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return {
                "items": [],
                "total": 0,
                "query": query,
                "category": category,
                "error": str(e)
            }
    
    def _calculate_relevance_score(self, query: str, item: KnowledgeBaseItem) -> float:
        """Calculate relevance score for search results."""
        query_terms = query.lower().split()
        title_score = 0
        content_score = 0
        
        # Check title matches
        title_lower = item.title.lower()
        for term in query_terms:
            if term in title_lower:
                title_score += 1
        
        # Check content matches
        content_lower = item.content.lower()
        for term in query_terms:
            content_score += content_lower.count(term)
        
        # Calculate final score
        total_score = (title_score * 2) + (content_score * 0.1)
        max_possible = len(query_terms) * 2
        
        return min(total_score / max_possible if max_possible > 0 else 0, 1.0)
    
    async def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific knowledge base item."""
        try:
            item = self.db.query(KnowledgeBaseItem).filter(
                KnowledgeBaseItem.id == item_id,
                KnowledgeBaseItem.is_active == "true"
            ).first()
            
            if item:
                return {
                    "id": item.id,
                    "title": item.title,
                    "content": item.content,
                    "category": item.category,
                    "source": item.source,
                    "created_at": item.created_at,
                    "updated_at": item.updated_at,
                    "tags": item.tags or [],
                    "metadata": item.metadata or {}
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting knowledge item {item_id}: {e}")
            return None
    
    async def create_item(
        self,
        title: str,
        content: str,
        category: str,
        source: str,
        tags: List[str] = None
    ) -> Dict[str, Any]:
        """Create a new knowledge base item."""
        try:
            item = KnowledgeBaseItem(
                id=str(uuid.uuid4()),
                title=title,
                content=content,
                category=category,
                source=source,
                tags=tags or [],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                is_active="true"
            )
            
            self.db.add(item)
            self.db.commit()
            self.db.refresh(item)
            
            logger.info(f"Created knowledge item: {item.id}")
            
            return {
                "id": item.id,
                "title": item.title,
                "content": item.content,
                "category": item.category,
                "source": item.source,
                "created_at": item.created_at,
                "updated_at": item.updated_at,
                "tags": item.tags
            }
            
        except Exception as e:
            logger.error(f"Error creating knowledge item: {e}")
            self.db.rollback()
            raise
    
    async def update_item(
        self,
        item_id: str,
        title: str,
        content: str,
        category: str,
        source: str,
        tags: List[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Update an existing knowledge base item."""
        try:
            item = self.db.query(KnowledgeBaseItem).filter(
                KnowledgeBaseItem.id == item_id
            ).first()
            
            if not item:
                return None
            
            item.title = title
            item.content = content
            item.category = category
            item.source = source
            item.tags = tags or []
            item.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(item)
            
            logger.info(f"Updated knowledge item: {item_id}")
            
            return {
                "id": item.id,
                "title": item.title,
                "content": item.content,
                "category": item.category,
                "source": item.source,
                "created_at": item.created_at,
                "updated_at": item.updated_at,
                "tags": item.tags
            }
            
        except Exception as e:
            logger.error(f"Error updating knowledge item {item_id}: {e}")
            self.db.rollback()
            raise
    
    async def delete_item(self, item_id: str) -> bool:
        """Delete a knowledge base item."""
        try:
            item = self.db.query(KnowledgeBaseItem).filter(
                KnowledgeBaseItem.id == item_id
            ).first()
            
            if item:
                item.is_active = "false"
                item.updated_at = datetime.utcnow()
                self.db.commit()
                
                logger.info(f"Deleted knowledge item: {item_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting knowledge item {item_id}: {e}")
            self.db.rollback()
            return False
    
    async def get_categories(self) -> List[str]:
        """Get all available knowledge base categories."""
        try:
            categories = self.db.query(KnowledgeBaseItem.category).filter(
                KnowledgeBaseItem.is_active == "true"
            ).distinct().all()
            
            return [category[0] for category in categories]
            
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            return []
    
    async def get_suggestions(self, query: str) -> List[str]:
        """Get search suggestions based on the query."""
        try:
            # Simple suggestion based on existing titles
            suggestions = self.db.query(KnowledgeBaseItem.title).filter(
                and_(
                    KnowledgeBaseItem.is_active == "true",
                    KnowledgeBaseItem.title.ilike(f"%{query}%")
                )
            ).limit(5).all()
            
            return [suggestion[0] for suggestion in suggestions]
            
        except Exception as e:
            logger.error(f"Error getting suggestions: {e}")
            return []
    
    async def sync_with_s3(self) -> Dict[str, Any]:
        """Sync knowledge base with S3 storage."""
        try:
            start_time = datetime.utcnow()
            items_processed = 0
            items_updated = 0
            items_created = 0
            
            # List objects in S3 bucket
            try:
                response = self.s3_client.list_objects_v2(
                    Bucket=settings.S3_BUCKET,
                    Prefix=settings.S3_PREFIX
                )
                
                if 'Contents' not in response:
                    return {
                        "items_processed": 0,
                        "items_updated": 0,
                        "items_created": 0,
                        "sync_time": 0
                    }
                
                for obj in response['Contents']:
                    if obj['Key'].endswith(('.md', '.txt', '.pdf')):
                        # Download and process file
                        file_content = self.s3_client.get_object(
                            Bucket=settings.S3_BUCKET,
                            Key=obj['Key']
                        )['Body'].read().decode('utf-8')
                        
                        # Extract metadata from filename
                        category = self._extract_category_from_key(obj['Key'])
                        title = self._extract_title_from_key(obj['Key'])
                        
                        # Check if item exists
                        existing_item = self.db.query(KnowledgeBaseItem).filter(
                            KnowledgeBaseItem.source == obj['Key']
                        ).first()
                        
                        if existing_item:
                            # Update existing item
                            existing_item.content = file_content
                            existing_item.updated_at = datetime.utcnow()
                            items_updated += 1
                        else:
                            # Create new item
                            new_item = KnowledgeBaseItem(
                                id=str(uuid.uuid4()),
                                title=title,
                                content=file_content,
                                category=category,
                                source=obj['Key'],
                                created_at=datetime.utcnow(),
                                updated_at=datetime.utcnow(),
                                is_active="true"
                            )
                            self.db.add(new_item)
                            items_created += 1
                        
                        items_processed += 1
                
                self.db.commit()
                
                sync_time = (datetime.utcnow() - start_time).total_seconds()
                
                logger.info(f"S3 sync completed: {items_processed} items processed")
                
                return {
                    "items_processed": items_processed,
                    "items_updated": items_updated,
                    "items_created": items_created,
                    "sync_time": sync_time
                }
                
            except ClientError as e:
                logger.error(f"S3 sync error: {e}")
                return {
                    "items_processed": 0,
                    "items_updated": 0,
                    "items_created": 0,
                    "sync_time": 0,
                    "error": str(e)
                }
                
        except Exception as e:
            logger.error(f"Error syncing with S3: {e}")
            self.db.rollback()
            raise
    
    def _extract_category_from_key(self, key: str) -> str:
        """Extract category from S3 object key."""
        parts = key.split('/')
        if len(parts) > 1:
            return parts[0]
        return "general"
    
    def _extract_title_from_key(self, key: str) -> str:
        """Extract title from S3 object key."""
        filename = key.split('/')[-1]
        return filename.replace('.md', '').replace('.txt', '').replace('.pdf', '').replace('_', ' ').title()
    
    async def _record_search_analytics(self, query: str, results_count: int):
        """Record search analytics."""
        try:
            search_analytics = KnowledgeBaseSearch(
                id=str(uuid.uuid4()),
                query=query,
                results_count=results_count,
                search_time=0.0,  # This would be calculated from actual search time
                created_at=datetime.utcnow()
            )
            
            self.db.add(search_analytics)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error recording search analytics: {e}")
            self.db.rollback()
