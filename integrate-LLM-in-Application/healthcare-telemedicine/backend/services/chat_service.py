"""
Chat Service - 24/7 AI-powered patient support chatbot
"""
import os
import json
import uuid
import logging
from datetime import datetime
from typing import Optional, List

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class ChatService:
    """AI chatbot service for patient support"""
    
    # System prompt for the healthcare chatbot
    SYSTEM_PROMPT = """You are a helpful healthcare assistant for a telemedicine platform. Your role is to:

1. Answer general health-related questions
2. Help patients schedule or manage appointments
3. Provide medication reminders and information
4. Offer post-visit follow-up support
5. Answer billing and insurance queries
6. Guide patients to appropriate resources

IMPORTANT GUIDELINES:
- Never provide specific medical diagnoses or treatment recommendations
- Always recommend consulting a healthcare professional for medical concerns
- Be empathetic, clear, and professional
- If a patient describes emergency symptoms, immediately advise them to call emergency services
- Protect patient privacy - never ask for unnecessary personal information
- If you cannot help with a request, offer to connect them with a human representative

Emergency keywords to watch for: chest pain, difficulty breathing, severe bleeding, stroke symptoms, suicidal thoughts, loss of consciousness."""

    def __init__(self):
        self.bedrock = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
        self.conversations_table = os.getenv('DYNAMODB_CONVERSATIONS_TABLE', 'telemedicine-conversations')
        
        # In-memory session cache (use Redis in production)
        self._session_cache = {}
    
    async def process_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        patient_id: Optional[str] = None
    ) -> dict:
        """
        Process a chat message and generate AI response
        
        Args:
            message: User's message
            session_id: Optional session identifier
            patient_id: Optional patient identifier
            
        Returns:
            Response with AI message and suggestions
        """
        # Create or retrieve session
        if not session_id:
            session_id = str(uuid.uuid4())
        
        try:
            # Check for emergency keywords
            if self._check_emergency(message):
                return await self._handle_emergency(session_id, message)
            
            # Get conversation history
            history = await self._get_conversation_history(session_id)
            
            # Generate AI response
            response = await self._generate_response(message, history)
            
            # Store conversation
            await self._store_message(session_id, patient_id, "user", message)
            await self._store_message(session_id, patient_id, "assistant", response["message"])
            
            # Generate suggestions
            suggestions = await self._generate_suggestions(message, response["message"])
            
            return {
                "session_id": session_id,
                "response": response["message"],
                "suggestions": suggestions,
                "requires_human": response.get("requires_human", False)
            }
            
        except Exception as e:
            logger.error(f"Error processing chat message: {str(e)}")
            return {
                "session_id": session_id,
                "response": "I apologize, but I'm having trouble processing your request. Please try again or contact our support team for assistance.",
                "suggestions": ["Contact support", "Try again"],
                "requires_human": True
            }
    
    def _check_emergency(self, message: str) -> bool:
        """Check if message contains emergency keywords"""
        emergency_keywords = [
            "chest pain", "heart attack", "can't breathe", "difficulty breathing",
            "severe bleeding", "stroke", "unconscious", "suicide", "kill myself",
            "overdose", "poisoning", "severe allergic", "anaphylaxis"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in emergency_keywords)
    
    async def _handle_emergency(self, session_id: str, message: str) -> dict:
        """Handle emergency situations"""
        emergency_response = """🚨 **EMERGENCY DETECTED**

Based on what you've described, this may be a medical emergency.

**Please take immediate action:**
1. **Call 911** (or your local emergency number) immediately
2. If you're with someone, ask them to stay with you
3. Do not drive yourself to the hospital

If this is a mental health crisis:
- **National Suicide Prevention Lifeline**: 988
- **Crisis Text Line**: Text HOME to 741741

Your safety is our top priority. Emergency services are equipped to help you right now.

Is there someone with you who can help?"""

        return {
            "session_id": session_id,
            "response": emergency_response,
            "suggestions": ["Call 911", "I'm safe now", "Connect me to a nurse"],
            "requires_human": True
        }
    
    async def _get_conversation_history(self, session_id: str) -> List[dict]:
        """Get conversation history for context"""
        # Check cache first
        if session_id in self._session_cache:
            return self._session_cache[session_id][-10:]  # Last 10 messages
        
        try:
            table = self.dynamodb.Table(self.conversations_table)
            
            response = table.query(
                KeyConditionExpression="session_id = :sid",
                ExpressionAttributeValues={":sid": session_id},
                ScanIndexForward=True,  # Oldest first
                Limit=10
            )
            
            history = []
            for item in response.get('Items', []):
                history.append({
                    "role": item.get('role'),
                    "content": item.get('content')
                })
            
            self._session_cache[session_id] = history
            return history
            
        except ClientError as e:
            logger.error(f"Error getting conversation history: {str(e)}")
            return []
    
    async def _generate_response(self, message: str, history: List[dict]) -> dict:
        """Generate AI response using Bedrock"""
        
        # Build messages array
        messages = []
        
        # Add conversation history
        for msg in history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": message
        })
        
        try:
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1024,
                    "system": self.SYSTEM_PROMPT,
                    "messages": messages
                })
            )
            
            response_body = json.loads(response['body'].read())
            ai_message = response_body['content'][0]['text']
            
            # Check if human handoff is needed
            requires_human = self._check_requires_human(message, ai_message)
            
            return {
                "message": ai_message,
                "requires_human": requires_human
            }
            
        except ClientError as e:
            logger.error(f"Bedrock error: {str(e)}")
            return {
                "message": "I'm having trouble connecting right now. Would you like me to connect you with a human representative?",
                "requires_human": True
            }
    
    def _check_requires_human(self, user_message: str, ai_response: str) -> bool:
        """Determine if human handoff is needed"""
        handoff_triggers = [
            "speak to a human", "talk to someone", "real person",
            "complaint", "frustrated", "angry", "not helpful",
            "billing issue", "insurance problem", "refund"
        ]
        
        message_lower = user_message.lower()
        return any(trigger in message_lower for trigger in handoff_triggers)
    
    async def _generate_suggestions(self, user_message: str, ai_response: str) -> List[str]:
        """Generate follow-up suggestions"""
        # Default suggestions based on common intents
        default_suggestions = [
            "Schedule an appointment",
            "Check my medications",
            "Talk to a nurse"
        ]
        
        # Context-aware suggestions
        message_lower = user_message.lower()
        
        if "appointment" in message_lower:
            return ["View available times", "Cancel appointment", "Reschedule"]
        elif "medication" in message_lower or "medicine" in message_lower:
            return ["Set medication reminder", "Check drug interactions", "Refill prescription"]
        elif "symptom" in message_lower or "feeling" in message_lower:
            return ["Start symptom assessment", "View past assessments", "Schedule consultation"]
        elif "bill" in message_lower or "payment" in message_lower:
            return ["View my bills", "Payment options", "Contact billing"]
        
        return default_suggestions
    
    async def _store_message(
        self,
        session_id: str,
        patient_id: Optional[str],
        role: str,
        content: str
    ):
        """Store message in DynamoDB"""
        try:
            table = self.dynamodb.Table(self.conversations_table)
            
            message_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat()
            
            item = {
                "session_id": session_id,
                "message_id": message_id,
                "patient_id": patient_id or "anonymous",
                "role": role,
                "content": content,
                "timestamp": timestamp,
                "ttl": int(datetime.utcnow().timestamp()) + (30 * 24 * 60 * 60)  # 30 days
            }
            
            table.put_item(Item=item)
            
            # Update cache
            if session_id not in self._session_cache:
                self._session_cache[session_id] = []
            self._session_cache[session_id].append({"role": role, "content": content})
            
        except ClientError as e:
            logger.error(f"Error storing message: {str(e)}")
    
    async def get_history(self, session_id: str) -> List[dict]:
        """Get full conversation history"""
        try:
            table = self.dynamodb.Table(self.conversations_table)
            
            response = table.query(
                KeyConditionExpression="session_id = :sid",
                ExpressionAttributeValues={":sid": session_id},
                ScanIndexForward=True
            )
            
            messages = []
            for item in response.get('Items', []):
                messages.append({
                    "message_id": item.get('message_id'),
                    "role": item.get('role'),
                    "content": item.get('content'),
                    "timestamp": item.get('timestamp')
                })
            
            return messages
            
        except ClientError as e:
            logger.error(f"Error getting history: {str(e)}")
            return []
    
    async def end_session(self, session_id: str) -> bool:
        """End a chat session"""
        try:
            # Clear from cache
            if session_id in self._session_cache:
                del self._session_cache[session_id]
            
            # Update session status in DB
            table = self.dynamodb.Table(self.conversations_table)
            
            # Add session end marker
            table.put_item(Item={
                "session_id": session_id,
                "message_id": "SESSION_END",
                "role": "system",
                "content": "Session ended",
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return True
            
        except ClientError as e:
            logger.error(f"Error ending session: {str(e)}")
            return False
