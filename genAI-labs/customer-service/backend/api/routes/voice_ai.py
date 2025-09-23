"""
Voice AI API routes
Handles voice processing endpoints
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel, Field
import structlog

from services.ai_service import AIService
from services.database import DatabaseService
from services.cache import CacheService

logger = structlog.get_logger(__name__)

router = APIRouter()


class VoiceRequest(BaseModel):
    """Voice request model"""
    customer_id: str = Field(..., description="Customer ID")
    session_id: str = Field(..., description="Session ID")
    language_code: Optional[str] = Field(default="en-US", description="Language code")


class VoiceResponse(BaseModel):
    """Voice response model"""
    transcription: str = Field(..., description="Transcribed text")
    response_text: str = Field(..., description="AI response text")
    audio_response: Optional[bytes] = Field(None, description="Audio response")
    intent: str = Field(..., description="Detected intent")
    confidence: float = Field(..., description="Confidence score")
    session_id: str = Field(..., description="Session ID")
    timestamp: datetime = Field(..., description="Response timestamp")


# Initialize AI service
ai_service = AIService()


@router.post("/voice/transcribe", response_model=VoiceResponse)
async def transcribe_and_respond(
    customer_id: str,
    session_id: str,
    audio_file: UploadFile = File(...),
    language_code: str = "en-US",
    db: DatabaseService = Depends(),
    cache: CacheService = Depends()
):
    """Transcribe audio and generate AI response"""
    try:
        logger.info("Processing voice request", 
                   customer_id=customer_id,
                   session_id=session_id)
        
        # Read audio file
        audio_data = await audio_file.read()
        
        # Transcribe audio
        transcription = await ai_service.transcribe_audio(
            audio_data, language_code
        )
        
        # Get customer context
        customer_context = await _get_customer_context(
            customer_id, db, cache
        )
        
        # Analyze intent
        intent_analysis = await ai_service.analyze_customer_intent(
            transcription, customer_context
        )
        
        # Generate response
        ai_response = await ai_service.generate_response(
            transcription, intent_analysis, customer_context
        )
        
        # Generate speech response
        audio_response = await ai_service.synthesize_speech(
            ai_response['response_text']
        )
        
        return VoiceResponse(
            transcription=transcription,
            response_text=ai_response['response_text'],
            audio_response=audio_response,
            intent=intent_analysis.get('intent', 'Unknown'),
            confidence=intent_analysis.get('confidence', 0.0),
            session_id=session_id,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error("Voice processing failed", error=str(e))
        raise HTTPException(status_code=500, detail="Voice processing failed")


@router.post("/voice/synthesize")
async def synthesize_speech(
    text: str,
    voice_id: str = "Joanna"
):
    """Convert text to speech"""
    try:
        audio_data = await ai_service.synthesize_speech(text, voice_id)
        
        return {
            "audio_data": audio_data,
            "voice_id": voice_id,
            "text_length": len(text)
        }
        
    except Exception as e:
        logger.error("Speech synthesis failed", error=str(e))
        raise HTTPException(status_code=500, detail="Speech synthesis failed")


async def _get_customer_context(
    customer_id: str, 
    db: DatabaseService, 
    cache: CacheService
) -> Dict[str, Any]:
    """Get customer context from cache or database"""
    # Try cache first
    context = await cache.get_customer_context(customer_id)
    if context:
        return context
    
    # Get from database
    customer = await db.get_customer(customer_id)
    if customer:
        context = {
            "customer_id": customer["customer_id"],
            "name": customer.get("name"),
            "email": customer.get("email"),
            "tier": customer.get("tier"),
            "preferences": customer.get("preferences", {}),
            "history": customer.get("interaction_history", [])
        }
        
        # Cache for 1 hour
        await cache.cache_customer_context(customer_id, context, ttl=3600)
        return context
    
    return {"customer_id": customer_id}
