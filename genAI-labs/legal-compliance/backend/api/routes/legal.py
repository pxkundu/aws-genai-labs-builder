"""
Legal API Routes for the Legal Compliance AI Platform
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from core.database import get_db
from core.cache import get_cache
from models.legal_question import (
    LegalQuestionRequest, 
    LegalQuestionResponse, 
    QuestionHistory,
    ErrorResponse,
    Jurisdiction,
    PracticeArea,
    QuestionComplexity
)
from services.llm_service import LLMService
from services.legal_service import LegalService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/ask",
    response_model=LegalQuestionResponse,
    summary="Ask a legal question",
    description="Submit a legal question and get responses from multiple LLMs with comparison analysis"
)
async def ask_legal_question(
    request: LegalQuestionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    legal_service: LegalService = Depends(),
    llm_service: LLMService = Depends()
) -> LegalQuestionResponse:
    """
    Ask a legal question and get comprehensive responses from multiple LLMs
    
    This endpoint:
    1. Validates the legal question
    2. Assesses question complexity
    3. Gets responses from multiple LLMs (OpenAI, Claude, Gemini)
    4. Compares and analyzes responses
    5. Provides recommendations and follow-up suggestions
    """
    start_time = datetime.utcnow()
    
    try:
        # Generate unique question ID
        question_id = f"q_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid4())[:8]}"
        
        # Assess question complexity
        complexity = await legal_service.assess_question_complexity(
            request.question, 
            request.jurisdiction, 
            request.practice_area
        )
        
        # Get LLM responses
        logger.info(f"Getting LLM responses for question: {question_id}")
        llm_responses = await llm_service.get_legal_response(
            question=request.question,
            jurisdiction=request.jurisdiction.value,
            practice_area=request.practice_area.value,
            models=request.models
        )
        
        # Compare responses if requested
        comparison = None
        if request.include_comparison and len(llm_responses) > 1:
            logger.info(f"Comparing responses for question: {question_id}")
            comparison_data = await llm_service.compare_responses(llm_responses)
            comparison = comparison_data
        
        # Determine recommended model and confidence level
        recommended_model = await legal_service.determine_recommended_model(llm_responses, comparison)
        confidence_level = await legal_service.assess_confidence_level(llm_responses, comparison)
        
        # Generate follow-up suggestions
        follow_up_suggestions = await legal_service.generate_follow_up_suggestions(
            request.question, 
            request.jurisdiction, 
            request.practice_area
        )
        
        # Calculate total processing time
        total_processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Create response
        response = LegalQuestionResponse(
            question_id=question_id,
            question=request.question,
            jurisdiction=request.jurisdiction,
            practice_area=request.practice_area,
            complexity=complexity,
            responses=llm_responses,
            comparison=comparison,
            timestamp=datetime.utcnow().isoformat(),
            processing_time=total_processing_time,
            cached=False,  # TODO: Implement cache checking
            recommended_model=recommended_model,
            confidence_level=confidence_level,
            follow_up_suggestions=follow_up_suggestions
        )
        
        # Store question in database (background task)
        background_tasks.add_task(
            store_question_history,
            question_id,
            request.question,
            request.jurisdiction,
            request.practice_area,
            db
        )
        
        logger.info(f"Successfully processed question: {question_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing legal question: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing legal question: {str(e)}"
        )


@router.get(
    "/history",
    response_model=List[QuestionHistory],
    summary="Get question history",
    description="Retrieve the history of previously asked legal questions"
)
async def get_question_history(
    limit: int = 50,
    offset: int = 0,
    jurisdiction: Jurisdiction = None,
    practice_area: PracticeArea = None,
    db: Session = Depends(get_db),
    legal_service: LegalService = Depends()
) -> List[QuestionHistory]:
    """Get the history of previously asked legal questions"""
    
    try:
        history = await legal_service.get_question_history(
            limit=limit,
            offset=offset,
            jurisdiction=jurisdiction,
            practice_area=practice_area,
            db=db
        )
        
        return history
        
    except Exception as e:
        logger.error(f"Error retrieving question history: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving question history: {str(e)}"
        )


@router.get(
    "/history/{question_id}",
    response_model=LegalQuestionResponse,
    summary="Get specific question response",
    description="Retrieve the full response for a specific question ID"
)
async def get_question_response(
    question_id: str,
    db: Session = Depends(get_db),
    legal_service: LegalService = Depends()
) -> LegalQuestionResponse:
    """Get the full response for a specific question ID"""
    
    try:
        response = await legal_service.get_question_response(question_id, db)
        
        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question with ID {question_id} not found"
            )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving question response: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving question response: {str(e)}"
        )


@router.get(
    "/jurisdictions",
    response_model=List[Dict[str, str]],
    summary="Get supported jurisdictions",
    description="Get list of supported legal jurisdictions"
)
async def get_supported_jurisdictions():
    """Get list of supported legal jurisdictions"""
    
    jurisdictions = []
    for jurisdiction in Jurisdiction:
        jurisdictions.append({
            "code": jurisdiction.value,
            "name": jurisdiction.value,
            "description": get_jurisdiction_description(jurisdiction)
        })
    
    return jurisdictions


@router.get(
    "/practice-areas",
    response_model=List[Dict[str, str]],
    summary="Get supported practice areas",
    description="Get list of supported legal practice areas"
)
async def get_supported_practice_areas():
    """Get list of supported legal practice areas"""
    
    practice_areas = []
    for area in PracticeArea:
        practice_areas.append({
            "code": area.value,
            "name": area.value.replace("_", " ").title(),
            "description": get_practice_area_description(area)
        })
    
    return practice_areas


@router.get(
    "/models",
    response_model=List[Dict[str, str]],
    summary="Get available LLM models",
    description="Get list of available LLM models for legal questions"
)
async def get_available_models(
    llm_service: LLMService = Depends()
):
    """Get list of available LLM models"""
    
    models = []
    for model_name, config in llm_service.llm_configs.items():
        models.append({
            "name": model_name,
            "provider": get_model_provider(model_name),
            "description": get_model_description(model_name),
            "max_tokens": config.max_tokens,
            "temperature": config.temperature
        })
    
    return models


@router.get(
    "/stats",
    response_model=Dict[str, Any],
    summary="Get platform statistics",
    description="Get statistics about questions asked and platform usage"
)
async def get_platform_stats(
    db: Session = Depends(get_db),
    legal_service: LegalService = Depends()
):
    """Get platform statistics"""
    
    try:
        stats = await legal_service.get_platform_statistics(db)
        return stats
        
    except Exception as e:
        logger.error(f"Error retrieving platform stats: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving platform statistics: {str(e)}"
        )


# Helper functions

async def store_question_history(
    question_id: str,
    question: str,
    jurisdiction: Jurisdiction,
    practice_area: PracticeArea,
    db: Session
):
    """Store question in history (background task)"""
    try:
        # This would be implemented in the legal service
        logger.info(f"Storing question history: {question_id}")
        # TODO: Implement database storage
    except Exception as e:
        logger.error(f"Error storing question history: {str(e)}")


def get_jurisdiction_description(jurisdiction: Jurisdiction) -> str:
    """Get description for a jurisdiction"""
    descriptions = {
        Jurisdiction.US: "United States federal and state law",
        Jurisdiction.UK: "United Kingdom law (England and Wales)",
        Jurisdiction.EU: "European Union law and regulations",
        Jurisdiction.DE: "German civil law system",
        Jurisdiction.FR: "French civil law system",
        Jurisdiction.IT: "Italian civil law system",
        Jurisdiction.ES: "Spanish civil law system",
        Jurisdiction.CA: "Canadian federal and provincial law",
        Jurisdiction.AU: "Australian federal and state law"
    }
    return descriptions.get(jurisdiction, "General legal principles")


def get_practice_area_description(practice_area: PracticeArea) -> str:
    """Get description for a practice area"""
    descriptions = {
        PracticeArea.GENERAL: "General legal principles and procedures",
        PracticeArea.CONTRACT: "Contract law, formation, performance, and remedies",
        PracticeArea.TORT: "Tort law, negligence, and civil liability",
        PracticeArea.CRIMINAL: "Criminal law and procedure",
        PracticeArea.CORPORATE: "Corporate law, business entities, and governance",
        PracticeArea.EMPLOYMENT: "Employment law and labor relations",
        PracticeArea.INTELLECTUAL_PROPERTY: "Intellectual property law and protection",
        PracticeArea.REAL_ESTATE: "Real estate law and property rights",
        PracticeArea.FAMILY: "Family law and domestic relations",
        PracticeArea.IMMIGRATION: "Immigration law and procedures",
        PracticeArea.TAX: "Tax law and regulations",
        PracticeArea.REGULATORY: "Regulatory compliance and administrative law"
    }
    return descriptions.get(practice_area, "General legal area")


def get_model_provider(model_name: str) -> str:
    """Get provider for a model"""
    if model_name.startswith("gpt-"):
        return "OpenAI"
    elif model_name.startswith("claude-"):
        return "Anthropic"
    elif model_name.startswith("gemini-"):
        return "Google"
    else:
        return "Unknown"


def get_model_description(model_name: str) -> str:
    """Get description for a model"""
    descriptions = {
        "gpt-4-turbo-preview": "OpenAI's most advanced GPT-4 model with enhanced capabilities",
        "claude-3-5-sonnet-20241022": "Anthropic's Claude 3.5 Sonnet with improved reasoning",
        "gemini-pro": "Google's Gemini Pro model with strong analytical capabilities"
    }
    return descriptions.get(model_name, "Advanced language model for legal analysis")
