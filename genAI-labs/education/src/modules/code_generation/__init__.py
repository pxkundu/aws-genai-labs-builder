"""
Code Generation Agent System Module

This module demonstrates an AI-powered code generation system with specialized agents
for different aspects of software development. It showcases requirements analysis,
architecture design, code generation, testing, and documentation workflows.
"""

from .requirements_agent import RequirementsAgent
from .architecture_agent import ArchitectureAgent
from .developer_agent import DeveloperAgent
from .testing_agent import TestingAgent
from .documentation_agent import DocumentationAgent
from .code_generation_module import CodeGenerationModule

__all__ = [
    "RequirementsAgent",
    "ArchitectureAgent",
    "DeveloperAgent",
    "TestingAgent",
    "DocumentationAgent",
    "CodeGenerationModule"
]
