"""
Shared utilities and components for the AWS GenAI Learning Platform.
"""

from .data_models import (
    ExerciseRequest, ExerciseResponse, SessionRequest, SessionResponse,
    ModuleInfo, PlatformOverview, LearningPath, HealthCheck
)
from .aws_clients import get_aws_clients
from .logging_config import setup_logging

__all__ = [
    "ExerciseRequest",
    "ExerciseResponse", 
    "SessionRequest",
    "SessionResponse",
    "ModuleInfo",
    "PlatformOverview",
    "LearningPath",
    "HealthCheck",
    "get_aws_clients",
    "setup_logging"
]
