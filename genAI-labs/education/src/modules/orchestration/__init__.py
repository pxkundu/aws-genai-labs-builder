"""
Multi-Agent Orchestration System Module

This module demonstrates complex multi-agent workflow management with agent coordination,
task scheduling, resource management, quality assurance, and error handling patterns.
"""

from .workflow_orchestrator import WorkflowOrchestrator
from .task_scheduler_agent import TaskSchedulerAgent
from .resource_manager_agent import ResourceManagerAgent
from .quality_assurance_agent import QualityAssuranceAgent
from .error_handler_agent import ErrorHandlerAgent
from .orchestration_module import OrchestrationModule

__all__ = [
    "WorkflowOrchestrator",
    "TaskSchedulerAgent",
    "ResourceManagerAgent",
    "QualityAssuranceAgent",
    "ErrorHandlerAgent",
    "OrchestrationModule"
]
