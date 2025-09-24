"""
Pydantic data models for the AWS GenAI Learning Platform API.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ExerciseRequest(BaseModel):
    """Request model for exercise execution."""
    user_input: str = Field(..., description="User input for the exercise")
    user_id: str = Field(..., description="User identifier")
    context: Optional[Dict[str, Any]] = Field(None, description="Optional context information")


class ExerciseResponse(BaseModel):
    """Response model for exercise execution."""
    exercise_id: str = Field(..., description="Exercise identifier")
    response: str = Field(..., description="Exercise response")
    success: bool = Field(..., description="Whether the exercise was successful")
    confidence: float = Field(0.0, description="Confidence score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class SessionRequest(BaseModel):
    """Request model for starting a learning session."""
    module_name: str = Field(..., description="Name of the learning module")
    user_id: str = Field(..., description="User identifier")


class SessionResponse(BaseModel):
    """Response model for learning session."""
    session_id: str = Field(..., description="Session identifier")
    module_name: str = Field(..., description="Name of the learning module")
    user_id: str = Field(..., description="User identifier")
    started_at: datetime = Field(..., description="Session start time")


class AgentInfo(BaseModel):
    """Information about an agent."""
    name: str = Field(..., description="Agent name")
    type: str = Field(..., description="Agent type")
    capabilities: List[str] = Field(default_factory=list, description="Agent capabilities")
    tools: List[str] = Field(default_factory=list, description="Available tools")


class ExerciseInfo(BaseModel):
    """Information about an exercise."""
    exercise_id: str = Field(..., description="Exercise identifier")
    name: str = Field(..., description="Exercise name")
    description: str = Field(..., description="Exercise description")
    difficulty: str = Field(..., description="Exercise difficulty level")
    estimated_time: str = Field(..., description="Estimated completion time")


class ModuleInfo(BaseModel):
    """Information about a learning module."""
    name: str = Field(..., description="Module name")
    description: str = Field(..., description="Module description")
    agents: List[AgentInfo] = Field(default_factory=list, description="Module agents")
    exercises: List[ExerciseInfo] = Field(default_factory=list, description="Module exercises")
    difficulty_level: str = Field(..., description="Module difficulty level")
    estimated_duration: str = Field(..., description="Estimated module duration")


class ModuleOverview(BaseModel):
    """Overview of a learning module."""
    name: str = Field(..., description="Module name")
    description: str = Field(..., description="Module description")
    agent_count: int = Field(..., description="Number of agents")
    exercise_count: int = Field(..., description="Number of exercises")
    difficulty_level: str = Field(..., description="Module difficulty level")


class PlatformOverview(BaseModel):
    """Overview of the learning platform."""
    platform_name: str = Field(..., description="Platform name")
    version: str = Field(..., description="Platform version")
    total_modules: int = Field(..., description="Total number of modules")
    total_agents: int = Field(..., description="Total number of agents")
    modules: Dict[str, ModuleOverview] = Field(..., description="Module overviews")
    statistics: Dict[str, Any] = Field(..., description="Platform statistics")
    last_updated: datetime = Field(..., description="Last update timestamp")


class LearningStep(BaseModel):
    """A step in the learning path."""
    module: str = Field(..., description="Module name")
    order: int = Field(..., description="Step order")
    description: str = Field(..., description="Step description")
    estimated_time: str = Field(..., description="Estimated time to complete")


class LearningPath(BaseModel):
    """Learning path for a user level."""
    user_level: str = Field(..., description="User level")
    learning_path: List[LearningStep] = Field(..., description="Learning steps")
    total_estimated_time: int = Field(..., description="Total estimated time in hours")
    recommendations: List[str] = Field(default_factory=list, description="Learning recommendations")


class ModuleHealth(BaseModel):
    """Health status of a module."""
    status: str = Field(..., description="Health status")
    timestamp: datetime = Field(..., description="Health check timestamp")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional health details")


class HealthCheck(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Overall health status")
    timestamp: datetime = Field(..., description="Health check timestamp")
    modules: Dict[str, ModuleHealth] = Field(..., description="Module health status")
    overall_health: str = Field(..., description="Overall platform health")


class AgentMessage(BaseModel):
    """Message for agent communication."""
    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Message metadata")


class AgentResponse(BaseModel):
    """Response from an agent."""
    content: str = Field(..., description="Response content")
    confidence: float = Field(0.0, description="Response confidence score")
    reasoning: Optional[str] = Field(None, description="Agent reasoning")
    tools_used: List[str] = Field(default_factory=list, description="Tools used")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Response metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class WorkflowStep(BaseModel):
    """A step in a workflow."""
    step_id: str = Field(..., description="Step identifier")
    name: str = Field(..., description="Step name")
    agent_type: str = Field(..., description="Agent type for this step")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Step parameters")
    dependencies: List[str] = Field(default_factory=list, description="Step dependencies")


class WorkflowDefinition(BaseModel):
    """Definition of a workflow."""
    name: str = Field(..., description="Workflow name")
    description: str = Field(..., description="Workflow description")
    steps: List[WorkflowStep] = Field(..., description="Workflow steps")


class WorkflowExecution(BaseModel):
    """Workflow execution details."""
    workflow_id: str = Field(..., description="Workflow identifier")
    status: str = Field(..., description="Execution status")
    started_at: datetime = Field(..., description="Start time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")
    results: Dict[str, Any] = Field(default_factory=dict, description="Execution results")


class AnalyticsEvent(BaseModel):
    """Analytics event for tracking user interactions."""
    event_type: str = Field(..., description="Event type")
    user_id: str = Field(..., description="User identifier")
    module_name: Optional[str] = Field(None, description="Module name")
    exercise_id: Optional[str] = Field(None, description="Exercise identifier")
    agent_name: Optional[str] = Field(None, description="Agent name")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Event metadata")
