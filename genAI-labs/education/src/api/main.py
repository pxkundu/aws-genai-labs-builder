"""
FastAPI Application for AWS GenAI Learning Platform

This module provides the main API endpoints for the learning platform,
including module management, exercise execution, and learning analytics.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ..core.learning_platform import LearningPlatform
from ..shared.logging_config import setup_logging
from ..shared.data_models import (
    ExerciseRequest, ExerciseResponse, SessionRequest, SessionResponse,
    ModuleInfo, PlatformOverview, LearningPath, HealthCheck
)


# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AWS GenAI Learning Platform API",
    description="Comprehensive learning platform for AWS Generative AI services and LLM agent-based solution architectures",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global learning platform instance
learning_platform: Optional[LearningPlatform] = None


class PlatformConfig(BaseModel):
    """Platform configuration model."""
    customer_service: Dict[str, Any] = Field(default_factory=dict)
    content_creation: Dict[str, Any] = Field(default_factory=dict)
    code_generation: Dict[str, Any] = Field(default_factory=dict)
    data_analysis: Dict[str, Any] = Field(default_factory=dict)
    orchestration: Dict[str, Any] = Field(default_factory=dict)


@app.on_event("startup")
async def startup_event():
    """Initialize the learning platform on startup."""
    global learning_platform
    
    try:
        # Default configuration
        config = {
            "customer_service": {
                "supervisor_agent": {
                    "model_id": "anthropic.claude-3-5-sonnet-20241022-v2:0",
                    "max_tokens": 4000,
                    "temperature": 0.7
                }
            },
            "content_creation": {
                "strategy_agent": {
                    "model_id": "anthropic.claude-3-5-sonnet-20241022-v2:0",
                    "max_tokens": 4000,
                    "temperature": 0.7
                }
            },
            "code_generation": {
                "requirements_agent": {
                    "model_id": "anthropic.claude-3-5-sonnet-20241022-v2:0",
                    "max_tokens": 4000,
                    "temperature": 0.7
                }
            },
            "data_analysis": {
                "ingestion_agent": {
                    "model_id": "anthropic.claude-3-5-sonnet-20241022-v2:0",
                    "max_tokens": 4000,
                    "temperature": 0.7
                }
            },
            "orchestration": {
                "orchestrator_agent": {
                    "model_id": "anthropic.claude-3-5-sonnet-20241022-v2:0",
                    "max_tokens": 4000,
                    "temperature": 0.7
                }
            }
        }
        
        learning_platform = LearningPlatform(config)
        logger.info("Learning platform initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize learning platform: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down learning platform")


def get_learning_platform() -> LearningPlatform:
    """Dependency to get the learning platform instance."""
    if learning_platform is None:
        raise HTTPException(status_code=500, detail="Learning platform not initialized")
    return learning_platform


# Health Check Endpoint
@app.get("/health", response_model=HealthCheck)
async def health_check(platform: LearningPlatform = Depends(get_learning_platform)):
    """Health check endpoint."""
    try:
        health_data = await platform.health_check()
        return HealthCheck(**health_data)
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


# Platform Overview
@app.get("/", response_model=PlatformOverview)
async def get_platform_overview(platform: LearningPlatform = Depends(get_learning_platform)):
    """Get platform overview."""
    try:
        overview = platform.get_platform_overview()
        return PlatformOverview(**overview)
    except Exception as e:
        logger.error(f"Failed to get platform overview: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get platform overview: {str(e)}")


# Module Management
@app.get("/modules", response_model=List[str])
async def get_modules(platform: LearningPlatform = Depends(get_learning_platform)):
    """Get list of available modules."""
    try:
        modules = list(platform.get_all_modules().keys())
        return modules
    except Exception as e:
        logger.error(f"Failed to get modules: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get modules: {str(e)}")


@app.get("/modules/{module_name}", response_model=ModuleInfo)
async def get_module_info(module_name: str, platform: LearningPlatform = Depends(get_learning_platform)):
    """Get information about a specific module."""
    try:
        module_info = platform.get_module_info(module_name)
        if "error" in module_info:
            raise HTTPException(status_code=404, detail=module_info["error"])
        return ModuleInfo(**module_info)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get module info for {module_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get module info: {str(e)}")


# Learning Path
@app.get("/learning-path/{user_level}", response_model=LearningPath)
async def get_learning_path(user_level: str, platform: LearningPlatform = Depends(get_learning_platform)):
    """Get learning path for a specific user level."""
    try:
        learning_path = platform.get_learning_path(user_level)
        return LearningPath(**learning_path)
    except Exception as e:
        logger.error(f"Failed to get learning path for {user_level}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get learning path: {str(e)}")


# Exercise Execution
@app.post("/modules/{module_name}/exercises/{exercise_id}/execute", response_model=ExerciseResponse)
async def execute_exercise(
    module_name: str,
    exercise_id: str,
    request: ExerciseRequest,
    background_tasks: BackgroundTasks,
    platform: LearningPlatform = Depends(get_learning_platform)
):
    """Execute a learning exercise."""
    try:
        result = await platform.execute_exercise(
            module_name=module_name,
            exercise_id=exercise_id,
            user_input=request.user_input,
            context=request.context
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Log exercise execution in background
        background_tasks.add_task(
            log_exercise_execution,
            module_name, exercise_id, request.user_id, result
        )
        
        return ExerciseResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to execute exercise {exercise_id} in module {module_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to execute exercise: {str(e)}")


# Session Management
@app.post("/sessions", response_model=SessionResponse)
async def start_session(
    request: SessionRequest,
    platform: LearningPlatform = Depends(get_learning_platform)
):
    """Start a new learning session."""
    try:
        result = await platform.start_learning_session(
            module_name=request.module_name,
            user_id=request.user_id
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return SessionResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")


@app.delete("/sessions/{session_id}")
async def end_session(
    session_id: str,
    platform: LearningPlatform = Depends(get_learning_platform)
):
    """End a learning session."""
    try:
        result = await platform.end_learning_session(session_id)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return {"message": "Session ended successfully", "session_id": session_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to end session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to end session: {str(e)}")


# Platform Statistics
@app.get("/statistics")
async def get_statistics(platform: LearningPlatform = Depends(get_learning_platform)):
    """Get platform usage statistics."""
    try:
        stats = platform.get_platform_statistics()
        return stats
    except Exception as e:
        logger.error(f"Failed to get statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


# Agent Interaction
@app.post("/modules/{module_name}/agents/{agent_name}/chat")
async def chat_with_agent(
    module_name: str,
    agent_name: str,
    request: Dict[str, Any],
    platform: LearningPlatform = Depends(get_learning_platform)
):
    """Chat with a specific agent."""
    try:
        module = platform.get_module(module_name)
        if not module:
            raise HTTPException(status_code=404, detail=f"Module {module_name} not found")
        
        agent = module.get_agent(agent_name)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found in module {module_name}")
        
        message = request.get("message", "")
        context = request.get("context")
        
        response = await agent.process_message(message, context)
        
        return {
            "agent_name": agent_name,
            "response": response.content,
            "confidence": response.confidence,
            "reasoning": response.reasoning,
            "tools_used": response.tools_used,
            "metadata": response.metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to chat with agent {agent_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to chat with agent: {str(e)}")


# Configuration Management
@app.post("/config")
async def update_config(
    config: PlatformConfig,
    platform: LearningPlatform = Depends(get_learning_platform)
):
    """Update platform configuration."""
    try:
        # Note: In a real implementation, you would need to restart the platform
        # with the new configuration. This is a simplified version.
        return {"message": "Configuration update received", "status": "success"}
    except Exception as e:
        logger.error(f"Failed to update configuration: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update configuration: {str(e)}")


# Background Tasks
async def log_exercise_execution(module_name: str, exercise_id: str, user_id: str, result: Dict[str, Any]):
    """Log exercise execution for analytics."""
    try:
        # In a real implementation, this would log to a database or analytics service
        logger.info(f"Exercise executed - Module: {module_name}, Exercise: {exercise_id}, User: {user_id}")
    except Exception as e:
        logger.error(f"Failed to log exercise execution: {str(e)}")


# Error Handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found", "path": str(request.url)}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
