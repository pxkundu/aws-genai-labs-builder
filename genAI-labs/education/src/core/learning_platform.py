"""
Main Learning Platform Class

This class orchestrates all learning modules and provides a unified interface
for the AWS GenAI Learning Platform.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from .agent_base import BaseAgent, AgentConfig
from ..modules.customer_service import CustomerServiceModule
from ..modules.content_creation import ContentCreationModule
from ..modules.code_generation import CodeGenerationModule
from ..modules.data_analysis import DataAnalysisModule
from ..modules.orchestration import OrchestrationModule


class LearningPlatform:
    """
    Main learning platform that orchestrates all learning modules.
    
    This class provides a unified interface for accessing and managing
    all learning modules and their associated agents.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the learning platform."""
        self.config = config
        self.logger = logging.getLogger("learning_platform")
        
        # Initialize learning modules
        self.modules = {}
        self._initialize_modules()
        
        # Platform statistics
        self.stats = {
            "total_modules": len(self.modules),
            "total_agents": 0,
            "active_sessions": 0,
            "completed_exercises": 0,
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"Learning platform initialized with {len(self.modules)} modules")
    
    def _initialize_modules(self):
        """Initialize all learning modules."""
        try:
            # Module 1: Customer Service Agent System
            self.modules["customer_service"] = CustomerServiceModule(
                config=self.config.get("customer_service", {})
            )
            
            # Module 2: Content Creation Agent System
            self.modules["content_creation"] = ContentCreationModule(
                config=self.config.get("content_creation", {})
            )
            
            # Module 3: Code Generation Agent System
            self.modules["code_generation"] = CodeGenerationModule(
                config=self.config.get("code_generation", {})
            )
            
            # Module 4: Data Analysis Agent System
            self.modules["data_analysis"] = DataAnalysisModule(
                config=self.config.get("data_analysis", {})
            )
            
            # Module 5: Multi-Agent Orchestration System
            self.modules["orchestration"] = OrchestrationModule(
                config=self.config.get("orchestration", {})
            )
            
            # Update statistics
            for module in self.modules.values():
                self.stats["total_agents"] += len(module.get_agents())
            
        except Exception as e:
            self.logger.error(f"Error initializing modules: {str(e)}")
            raise
    
    def get_module(self, module_name: str) -> Optional[Any]:
        """Get a specific learning module."""
        return self.modules.get(module_name)
    
    def get_all_modules(self) -> Dict[str, Any]:
        """Get all learning modules."""
        return self.modules.copy()
    
    def get_module_info(self, module_name: str) -> Dict[str, Any]:
        """Get information about a specific module."""
        module = self.get_module(module_name)
        if not module:
            return {"error": f"Module {module_name} not found"}
        
        return {
            "name": module_name,
            "description": module.get_description(),
            "agents": module.get_agent_info(),
            "exercises": module.get_exercises(),
            "difficulty_level": module.get_difficulty_level(),
            "estimated_duration": module.get_estimated_duration()
        }
    
    def get_platform_overview(self) -> Dict[str, Any]:
        """Get an overview of the entire learning platform."""
        module_overviews = {}
        for name, module in self.modules.items():
            module_overviews[name] = {
                "name": name,
                "description": module.get_description(),
                "agent_count": len(module.get_agents()),
                "exercise_count": len(module.get_exercises()),
                "difficulty_level": module.get_difficulty_level()
            }
        
        return {
            "platform_name": "AWS GenAI Learning Platform",
            "version": "1.0.0",
            "total_modules": len(self.modules),
            "total_agents": self.stats["total_agents"],
            "modules": module_overviews,
            "statistics": self.stats,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def execute_exercise(self, module_name: str, exercise_id: str, 
                             user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a learning exercise."""
        module = self.get_module(module_name)
        if not module:
            return {"error": f"Module {module_name} not found"}
        
        try:
            result = await module.execute_exercise(exercise_id, user_input, context)
            self.stats["completed_exercises"] += 1
            return result
        except Exception as e:
            self.logger.error(f"Error executing exercise {exercise_id} in module {module_name}: {str(e)}")
            return {"error": str(e)}
    
    async def start_learning_session(self, module_name: str, user_id: str) -> Dict[str, Any]:
        """Start a new learning session."""
        module = self.get_module(module_name)
        if not module:
            return {"error": f"Module {module_name} not found"}
        
        try:
            session = await module.start_session(user_id)
            self.stats["active_sessions"] += 1
            return {
                "session_id": session.get("session_id"),
                "module_name": module_name,
                "user_id": user_id,
                "started_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error starting learning session: {str(e)}")
            return {"error": str(e)}
    
    async def end_learning_session(self, session_id: str) -> Dict[str, Any]:
        """End a learning session."""
        # Find the session across all modules
        for module_name, module in self.modules.items():
            try:
                result = await module.end_session(session_id)
                if "error" not in result:
                    self.stats["active_sessions"] = max(0, self.stats["active_sessions"] - 1)
                    return result
            except Exception as e:
                self.logger.error(f"Error ending session in module {module_name}: {str(e)}")
        
        return {"error": f"Session {session_id} not found"}
    
    def get_learning_path(self, user_level: str = "beginner") -> Dict[str, Any]:
        """Get a recommended learning path based on user level."""
        learning_paths = {
            "beginner": [
                {
                    "module": "customer_service",
                    "order": 1,
                    "description": "Start with customer service agents to understand basic agent patterns",
                    "estimated_time": "2-3 hours"
                },
                {
                    "module": "content_creation",
                    "order": 2,
                    "description": "Learn content creation agents for AI-powered content generation",
                    "estimated_time": "2-3 hours"
                }
            ],
            "intermediate": [
                {
                    "module": "code_generation",
                    "order": 1,
                    "description": "Explore code generation agents for software development",
                    "estimated_time": "3-4 hours"
                },
                {
                    "module": "data_analysis",
                    "order": 2,
                    "description": "Learn data analysis agents for automated data processing",
                    "estimated_time": "3-4 hours"
                }
            ],
            "advanced": [
                {
                    "module": "orchestration",
                    "order": 1,
                    "description": "Master multi-agent orchestration for complex workflows",
                    "estimated_time": "4-5 hours"
                }
            ]
        }
        
        return {
            "user_level": user_level,
            "learning_path": learning_paths.get(user_level, learning_paths["beginner"]),
            "total_estimated_time": sum(
                int(step["estimated_time"].split("-")[0]) 
                for step in learning_paths.get(user_level, learning_paths["beginner"])
            ),
            "recommendations": self._get_learning_recommendations(user_level)
        }
    
    def _get_learning_recommendations(self, user_level: str) -> List[str]:
        """Get learning recommendations based on user level."""
        recommendations = {
            "beginner": [
                "Start with the customer service module to understand basic agent concepts",
                "Practice with simple agent interactions before moving to complex workflows",
                "Focus on understanding agent communication patterns",
                "Complete all exercises in each module before proceeding"
            ],
            "intermediate": [
                "Experiment with different agent configurations and parameters",
                "Try combining multiple agents for complex tasks",
                "Focus on understanding agent coordination and delegation",
                "Practice building custom agent workflows"
            ],
            "advanced": [
                "Design and implement custom multi-agent systems",
                "Optimize agent performance and resource utilization",
                "Explore advanced orchestration patterns",
                "Build production-ready agent-based applications"
            ]
        }
        
        return recommendations.get(user_level, recommendations["beginner"])
    
    def get_platform_statistics(self) -> Dict[str, Any]:
        """Get platform usage statistics."""
        return {
            "platform_stats": self.stats,
            "module_stats": {
                name: {
                    "agent_count": len(module.get_agents()),
                    "exercise_count": len(module.get_exercises()),
                    "difficulty_level": module.get_difficulty_level()
                }
                for name, module in self.modules.items()
            },
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the platform."""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "modules": {},
            "overall_health": "healthy"
        }
        
        unhealthy_modules = 0
        
        for name, module in self.modules.items():
            try:
                module_health = await module.health_check()
                health_status["modules"][name] = module_health
                if module_health.get("status") != "healthy":
                    unhealthy_modules += 1
            except Exception as e:
                health_status["modules"][name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                unhealthy_modules += 1
        
        if unhealthy_modules > 0:
            health_status["overall_health"] = "degraded" if unhealthy_modules < len(self.modules) else "unhealthy"
            health_status["status"] = health_status["overall_health"]
        
        return health_status
