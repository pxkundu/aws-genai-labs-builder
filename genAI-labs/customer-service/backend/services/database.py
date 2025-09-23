"""
Database service for GenAI Customer Service
Handles all database operations
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

import motor.motor_asyncio
from pymongo import MongoClient
import structlog

from config.settings import settings
from models.conversation import Conversation, Message, ConversationStatus

logger = structlog.get_logger(__name__)


class DatabaseService:
    """Database service for handling all database operations"""
    
    def __init__(self, settings):
        """Initialize database service"""
        self.settings = settings
        self.client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
        self.db = None
        self.conversations_collection = None
        self.customers_collection = None
        self.knowledge_collection = None
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(
                self.settings.MONGODB_URL
            )
            self.db = self.client[self.settings.MONGODB_DATABASE]
            
            # Initialize collections
            self.conversations_collection = self.db.conversations
            self.customers_collection = self.db.customers
            self.knowledge_collection = self.db.knowledge_base
            
            # Create indexes
            await self._create_indexes()
            
            logger.info("Database connected successfully")
            
        except Exception as e:
            logger.error("Failed to connect to database", error=str(e))
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Database disconnected")
    
    async def _create_indexes(self):
        """Create database indexes"""
        try:
            # Conversations indexes
            await self.conversations_collection.create_index([
                ("customer_id", 1),
                ("session_id", 1)
            ], unique=True)
            
            await self.conversations_collection.create_index([
                ("customer_id", 1),
                ("created_at", -1)
            ])
            
            await self.conversations_collection.create_index([
                ("status", 1),
                ("created_at", -1)
            ])
            
            # Customers indexes
            await self.customers_collection.create_index("customer_id", unique=True)
            await self.customers_collection.create_index("email", unique=True)
            
            # Knowledge base indexes
            await self.knowledge_collection.create_index([
                ("title", "text"),
                ("content", "text")
            ])
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error("Failed to create indexes", error=str(e))
    
    async def save_conversation(self, conversation: Conversation) -> str:
        """Save conversation to database"""
        try:
            conversation_dict = conversation.dict()
            conversation_dict["updated_at"] = datetime.utcnow()
            
            result = await self.conversations_collection.insert_one(conversation_dict)
            
            logger.info("Conversation saved", 
                       conversation_id=str(result.inserted_id),
                       customer_id=conversation.customer_id)
            
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error("Failed to save conversation", error=str(e))
            raise
    
    async def get_conversation(self, customer_id: str, session_id: str) -> Optional[Conversation]:
        """Get specific conversation"""
        try:
            conversation_dict = await self.conversations_collection.find_one({
                "customer_id": customer_id,
                "session_id": session_id
            })
            
            if conversation_dict:
                conversation_dict["id"] = str(conversation_dict["_id"])
                del conversation_dict["_id"]
                return Conversation(**conversation_dict)
            
            return None
            
        except Exception as e:
            logger.error("Failed to get conversation", error=str(e))
            raise
    
    async def get_conversations(self, customer_id: str, 
                              limit: int = 10, 
                              offset: int = 0,
                              days_back: int = None) -> List[Conversation]:
        """Get conversations for a customer"""
        try:
            query = {"customer_id": customer_id}
            
            if days_back:
                start_date = datetime.utcnow() - timedelta(days=days_back)
                query["created_at"] = {"$gte": start_date}
            
            cursor = self.conversations_collection.find(query).sort(
                "created_at", -1
            ).skip(offset).limit(limit)
            
            conversations = []
            async for conversation_dict in cursor:
                conversation_dict["id"] = str(conversation_dict["_id"])
                del conversation_dict["_id"]
                conversations.append(Conversation(**conversation_dict))
            
            return conversations
            
        except Exception as e:
            logger.error("Failed to get conversations", error=str(e))
            raise
    
    async def update_conversation_status(self, customer_id: str, 
                                       session_id: str, 
                                       status: ConversationStatus,
                                       metadata: Dict[str, Any] = None):
        """Update conversation status"""
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow()
            }
            
            if metadata:
                update_data["metadata"] = metadata
            
            result = await self.conversations_collection.update_one(
                {"customer_id": customer_id, "session_id": session_id},
                {"$set": update_data}
            )
            
            if result.modified_count == 0:
                raise Exception("Conversation not found or not updated")
            
            logger.info("Conversation status updated", 
                       customer_id=customer_id,
                       session_id=session_id,
                       status=status)
            
        except Exception as e:
            logger.error("Failed to update conversation status", error=str(e))
            raise
    
    async def add_message_to_conversation(self, customer_id: str, 
                                        session_id: str, 
                                        message: Message):
        """Add message to existing conversation"""
        try:
            message_dict = message.dict()
            
            result = await self.conversations_collection.update_one(
                {"customer_id": customer_id, "session_id": session_id},
                {
                    "$push": {"messages": message_dict},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            if result.modified_count == 0:
                raise Exception("Conversation not found or not updated")
            
            logger.info("Message added to conversation", 
                       customer_id=customer_id,
                       session_id=session_id)
            
        except Exception as e:
            logger.error("Failed to add message to conversation", error=str(e))
            raise
    
    async def get_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Get customer information"""
        try:
            customer = await self.customers_collection.find_one({
                "customer_id": customer_id
            })
            
            if customer:
                customer["id"] = str(customer["_id"])
                del customer["_id"]
            
            return customer
            
        except Exception as e:
            logger.error("Failed to get customer", error=str(e))
            raise
    
    async def save_customer(self, customer_data: Dict[str, Any]) -> str:
        """Save customer information"""
        try:
            customer_data["updated_at"] = datetime.utcnow()
            
            result = await self.customers_collection.insert_one(customer_data)
            
            logger.info("Customer saved", customer_id=customer_data.get("customer_id"))
            
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error("Failed to save customer", error=str(e))
            raise
    
    async def search_knowledge_base(self, query: str, 
                                  limit: int = 10) -> List[Dict[str, Any]]:
        """Search knowledge base"""
        try:
            # Simple text search - in production, use vector search
            cursor = self.knowledge_collection.find({
                "$text": {"$search": query}
            }).limit(limit)
            
            results = []
            async for doc in cursor:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                results.append(doc)
            
            return results
            
        except Exception as e:
            logger.error("Failed to search knowledge base", error=str(e))
            raise
    
    async def save_knowledge_article(self, article_data: Dict[str, Any]) -> str:
        """Save knowledge base article"""
        try:
            article_data["created_at"] = datetime.utcnow()
            article_data["updated_at"] = datetime.utcnow()
            
            result = await self.knowledge_collection.insert_one(article_data)
            
            logger.info("Knowledge article saved", 
                       article_id=str(result.inserted_id))
            
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error("Failed to save knowledge article", error=str(e))
            raise
    
    async def get_conversation_analytics(self, 
                                       start_date: datetime = None,
                                       end_date: datetime = None) -> Dict[str, Any]:
        """Get conversation analytics"""
        try:
            start_date = start_date or datetime.utcnow() - timedelta(days=30)
            end_date = end_date or datetime.utcnow()
            
            pipeline = [
                {
                    "$match": {
                        "created_at": {"$gte": start_date, "$lte": end_date}
                    }
                },
                {
                    "$group": {
                        "_id": "$status",
                        "count": {"$sum": 1},
                        "avg_messages": {"$avg": {"$size": "$messages"}}
                    }
                }
            ]
            
            cursor = self.conversations_collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "statistics": results,
                "total_conversations": sum(r["count"] for r in results)
            }
            
        except Exception as e:
            logger.error("Failed to get conversation analytics", error=str(e))
            raise
