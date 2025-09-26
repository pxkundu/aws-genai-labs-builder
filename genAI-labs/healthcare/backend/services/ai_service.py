"""
Healthcare ChatGPT Clone - AI Service
This module handles AI/LLM integration for healthcare-specific responses.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
import openai
import boto3
from botocore.exceptions import ClientError
import json
import time

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class AIService:
    """Service for handling AI/LLM interactions with healthcare-specific prompts."""
    
    def __init__(self):
        self.openai_client = None
        self.bedrock_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize AI service clients."""
        try:
            # Initialize OpenAI client
            if settings.OPENAI_API_KEY:
                openai.api_key = settings.OPENAI_API_KEY
                self.openai_client = openai
            
            # Initialize Bedrock client
            if settings.AWS_REGION:
                self.bedrock_client = boto3.client(
                    'bedrock-runtime',
                    region_name=settings.BEDROCK_REGION
                )
            
            logger.info("AI service clients initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI service clients: {e}")
            raise
    
    async def generate_response(
        self,
        message: str,
        session_id: str,
        context: Optional[Dict] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate AI response for healthcare queries.
        
        Args:
            message: User's message
            session_id: Chat session ID
            context: Additional context (patient info, etc.)
            model: AI model to use (openai, bedrock)
        
        Returns:
            Dict containing response, model used, confidence score, and sources
        """
        try:
            start_time = time.time()
            
            # Select model
            selected_model = model or self._select_best_model()
            
            # Get healthcare-specific prompt
            system_prompt = self._get_healthcare_system_prompt(context)
            
            # Generate response based on selected model
            if selected_model.startswith("openai"):
                response = await self._generate_openai_response(
                    message, system_prompt, selected_model
                )
            elif selected_model.startswith("bedrock"):
                response = await self._generate_bedrock_response(
                    message, system_prompt, selected_model
                )
            else:
                raise ValueError(f"Unsupported model: {selected_model}")
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Get knowledge base sources
            sources = await self._get_relevant_sources(message)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(response, sources)
            
            return {
                "response": response,
                "model": selected_model,
                "response_time": response_time,
                "confidence_score": confidence_score,
                "sources": sources,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return {
                "response": "I apologize, but I'm experiencing technical difficulties. Please try again or contact your healthcare provider for assistance.",
                "model": "error",
                "response_time": 0,
                "confidence_score": 0.0,
                "sources": [],
                "timestamp": time.time()
            }
    
    def _select_best_model(self) -> str:
        """Select the best available AI model."""
        if self.openai_client and settings.OPENAI_API_KEY:
            return "openai"
        elif self.bedrock_client:
            return "bedrock"
        else:
            raise RuntimeError("No AI models available")
    
    def _get_healthcare_system_prompt(self, context: Optional[Dict] = None) -> str:
        """Get healthcare-specific system prompt."""
        base_prompt = """
You are a healthcare AI assistant designed to help patients, staff, and healthcare providers with medical information and support.

Guidelines:
1. Provide accurate, evidence-based medical information
2. Always recommend consulting healthcare professionals for medical decisions
3. Maintain patient privacy and confidentiality
4. Use clear, understandable language
5. Include appropriate disclaimers
6. Escalate to human providers when necessary

Your responses should be:
- Accurate and evidence-based
- Empathetic and supportive
- Clear and concise
- HIPAA compliant
- Culturally sensitive

Remember: You are not a replacement for professional medical care.
"""
        
        if context:
            if context.get("patient_age"):
                base_prompt += f"\nPatient age: {context['patient_age']}"
            
            if context.get("medical_history"):
                base_prompt += f"\nMedical history: {context['medical_history']}"
            
            if context.get("department"):
                base_prompt += f"\nDepartment: {context['department']}"
        
        return base_prompt
    
    async def _generate_openai_response(
        self,
        message: str,
        system_prompt: str,
        model: str
    ) -> str:
        """Generate response using OpenAI API."""
        try:
            response = await asyncio.to_thread(
                self.openai_client.ChatCompletion.create,
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=settings.OPENAI_MAX_TOKENS,
                temperature=settings.OPENAI_TEMPERATURE
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def _generate_bedrock_response(
        self,
        message: str,
        system_prompt: str,
        model: str
    ) -> str:
        """Generate response using AWS Bedrock."""
        try:
            # Prepare the prompt for Claude
            prompt = f"{system_prompt}\n\nHuman: {message}\n\nAssistant:"
            
            body = json.dumps({
                "prompt": prompt,
                "max_tokens_to_sample": 2000,
                "temperature": 0.7,
                "top_p": 1.0
            })
            
            response = await asyncio.to_thread(
                self.bedrock_client.invoke_model,
                modelId=settings.BEDROCK_MODEL_ID,
                body=body,
                contentType="application/json"
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['completion'].strip()
            
        except Exception as e:
            logger.error(f"Bedrock API error: {e}")
            raise
    
    async def _get_relevant_sources(self, message: str) -> List[str]:
        """Get relevant knowledge base sources for the query."""
        # This would integrate with the knowledge base service
        # For now, return empty list
        return []
    
    def _calculate_confidence_score(self, response: str, sources: List[str]) -> float:
        """Calculate confidence score for the response."""
        # Simple confidence calculation based on response length and sources
        base_confidence = 0.7
        
        # Increase confidence if we have sources
        if sources:
            base_confidence += 0.2
        
        # Increase confidence for longer, more detailed responses
        if len(response) > 200:
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def detect_emergency(self, message: str) -> bool:
        """Detect if the message indicates an emergency situation."""
        emergency_keywords = [
            "chest pain", "heart attack", "stroke", "difficulty breathing",
            "severe bleeding", "unconscious", "suicidal", "overdose",
            "severe allergic reaction", "seizure", "choking"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in emergency_keywords)
    
    def get_emergency_response(self) -> str:
        """Get emergency response message."""
        return """
🚨 **EMERGENCY DETECTED** 🚨

If you are experiencing a medical emergency, please:

1. **Call 911 immediately**
2. **Go to the nearest emergency room**
3. **Do not wait for a response**

This AI assistant cannot provide emergency medical care. Please seek immediate professional medical attention.

**Emergency Services:** 911
**Poison Control:** 1-800-222-1222
**Suicide Prevention:** 988
        """
