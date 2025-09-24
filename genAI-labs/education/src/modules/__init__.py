"""
Learning modules for the AWS GenAI Learning Platform.

Each module demonstrates different agent-based solution architectures
and provides hands-on learning experiences.
"""

from .customer_service import CustomerServiceModule
from .content_creation import ContentCreationModule
from .code_generation import CodeGenerationModule
from .data_analysis import DataAnalysisModule
from .orchestration import OrchestrationModule

__all__ = [
    "CustomerServiceModule",
    "ContentCreationModule", 
    "CodeGenerationModule",
    "DataAnalysisModule",
    "OrchestrationModule"
]
