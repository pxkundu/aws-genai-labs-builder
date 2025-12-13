"""
Healthcare Telemedicine AI Support System - Main Application
"""
import os
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import services
from services.symptom_checker import SymptomCheckerService
from services.triage_service import TriageService
from services.chat_service import ChatService
from services.document_analyzer import DocumentAnalyzerService

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize services
symptom_checker = SymptomCheckerService()
triage_service = TriageService()
chat_service = ChatService()
document_analyzer = DocumentAnalyzerService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    logger.info("Starting Healthcare Telemedicine AI System...")
    yield
    logger.info("Shutting down Healthcare Telemedicine AI System...")


# Create FastAPI app
app = FastAPI(
    title="Healthcare Telemedicine AI",
    description="AI-powered telemedicine support system with symptom assessment, triage, and patient support",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== Request/Response Models ==============

class SymptomAssessmentRequest(BaseModel):
    """Request model for symptom assessment"""
    patient_id: Optional[str] = Field(None, description="Patient identifier")
    symptoms: str = Field(..., description="Patient's symptoms description")
    age: Optional[int] = Field(None, description="Patient age")
    gender: Optional[str] = Field(None, description="Patient gender")
    medical_history: Optional[list[str]] = Field(default=[], description="Known medical conditions")
    current_medications: Optional[list[str]] = Field(default=[], description="Current medications")


class SymptomAssessmentResponse(BaseModel):
    """Response model for symptom assessment"""
    assessment_id: str
    risk_level: str
    risk_score: int
    possible_conditions: list[dict]
    follow_up_questions: list[str]
    recommendations: list[str]
    urgency: str
    disclaimer: str


class TriageRequest(BaseModel):
    """Request model for triage"""
    assessment_id: str
    patient_id: Optional[str] = None
    vital_signs: Optional[dict] = None


class TriageResponse(BaseModel):
    """Response model for triage"""
    triage_id: str
    triage_level: str
    priority: int
    recommended_action: str
    estimated_wait_time: str
    provider_notes: str


class ChatRequest(BaseModel):
    """Request model for chat"""
    session_id: Optional[str] = None
    patient_id: Optional[str] = None
    message: str


class ChatResponse(BaseModel):
    """Response model for chat"""
    session_id: str
    response: str
    suggestions: list[str]
    requires_human: bool


class DocumentAnalysisRequest(BaseModel):
    """Request model for document analysis"""
    document_url: str
    document_type: str = "general"
    patient_id: Optional[str] = None


class DocumentAnalysisResponse(BaseModel):
    """Response model for document analysis"""
    analysis_id: str
    document_type: str
    extracted_entities: dict
    summary: str
    key_findings: list[str]
    recommendations: list[str]


# ============== Health Check ==============

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Healthcare Telemedicine AI",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


# ============== Symptom Assessment Endpoints ==============

@app.post("/api/symptoms/assess", response_model=SymptomAssessmentResponse)
async def assess_symptoms(request: SymptomAssessmentRequest):
    """
    Assess patient symptoms using AI
    
    This endpoint analyzes patient-reported symptoms and provides:
    - Risk level assessment
    - Possible conditions
    - Follow-up questions
    - Recommendations
    """
    try:
        logger.info(f"Processing symptom assessment for patient: {request.patient_id}")
        
        result = await symptom_checker.assess_symptoms(
            symptoms=request.symptoms,
            patient_id=request.patient_id,
            age=request.age,
            gender=request.gender,
            medical_history=request.medical_history,
            current_medications=request.current_medications
        )
        
        return SymptomAssessmentResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in symptom assessment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process symptom assessment: {str(e)}"
        )


@app.post("/api/symptoms/followup")
async def process_followup(assessment_id: str, answers: dict):
    """Process follow-up question answers"""
    try:
        result = await symptom_checker.process_followup(assessment_id, answers)
        return result
    except Exception as e:
        logger.error(f"Error processing follow-up: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== Triage Endpoints ==============

@app.post("/api/triage/evaluate", response_model=TriageResponse)
async def evaluate_triage(request: TriageRequest):
    """
    Evaluate patient triage level
    
    Determines urgency and priority based on assessment results
    """
    try:
        logger.info(f"Processing triage for assessment: {request.assessment_id}")
        
        result = await triage_service.evaluate_triage(
            assessment_id=request.assessment_id,
            patient_id=request.patient_id,
            vital_signs=request.vital_signs
        )
        
        return TriageResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in triage evaluation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/triage/queue")
async def get_triage_queue():
    """Get current triage queue"""
    try:
        queue = await triage_service.get_queue()
        return {"queue": queue}
    except Exception as e:
        logger.error(f"Error getting triage queue: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== Chat Endpoints ==============

@app.post("/api/chat/message", response_model=ChatResponse)
async def send_chat_message(request: ChatRequest):
    """
    Send a message to the AI chatbot
    
    Handles patient queries about:
    - Health information
    - Appointments
    - Medications
    - General support
    """
    try:
        logger.info(f"Processing chat message for session: {request.session_id}")
        
        result = await chat_service.process_message(
            message=request.message,
            session_id=request.session_id,
            patient_id=request.patient_id
        )
        
        return ChatResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in chat processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    try:
        history = await chat_service.get_history(session_id)
        return {"session_id": session_id, "messages": history}
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== Document Analysis Endpoints ==============

@app.post("/api/documents/analyze", response_model=DocumentAnalysisResponse)
async def analyze_document(request: DocumentAnalysisRequest):
    """
    Analyze medical documents using AI
    
    Extracts and analyzes:
    - Medical entities
    - Key findings
    - Recommendations
    """
    try:
        logger.info(f"Processing document analysis: {request.document_type}")
        
        result = await document_analyzer.analyze_document(
            document_url=request.document_url,
            document_type=request.document_type,
            patient_id=request.patient_id
        )
        
        return DocumentAnalysisResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in document analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== Error Handlers ==============

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# ============== Main Entry Point ==============

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", 8000))
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=os.getenv("ENVIRONMENT") == "development"
    )
