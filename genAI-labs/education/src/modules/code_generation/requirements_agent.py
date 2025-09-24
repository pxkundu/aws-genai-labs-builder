"""
Requirements Agent for Code Generation System

This agent specializes in analyzing and clarifying software requirements,
breaking down complex requirements into actionable development tasks,
and ensuring requirements are complete and testable.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from langchain.tools import BaseTool
from langchain.agents import Tool

from ...core.agent_base import BaseAgent, AgentConfig, AgentResponse


class RequirementsAnalysisTool(BaseTool):
    """Tool for analyzing and breaking down software requirements."""
    
    name = "requirements_analysis"
    description = "Analyze software requirements and break them down into actionable tasks"
    
    def _run(self, requirements: str) -> str:
        """Analyze requirements and create structured breakdown."""
        # Simulated requirements analysis
        analysis_result = {
            "original_requirements": requirements,
            "analysis_date": datetime.utcnow().isoformat(),
            "requirements_breakdown": {
                "functional_requirements": [],
                "non_functional_requirements": [],
                "user_stories": [],
                "acceptance_criteria": [],
                "technical_constraints": [],
                "assumptions": []
            },
            "complexity_assessment": {
                "overall_complexity": "medium",
                "estimated_effort": "2-4 weeks",
                "risk_level": "low",
                "dependencies": []
            },
            "recommendations": [
                "Clarify user interface requirements",
                "Define data storage requirements",
                "Specify integration points",
                "Establish testing criteria"
            ]
        }
        
        # Simple keyword-based analysis
        requirements_lower = requirements.lower()
        
        # Identify functional requirements
        if any(keyword in requirements_lower for keyword in ["create", "add", "delete", "update", "search", "filter"]):
            analysis_result["requirements_breakdown"]["functional_requirements"].append(
                "Data management operations (CRUD)"
            )
        
        if any(keyword in requirements_lower for keyword in ["user", "login", "authentication", "authorization"]):
            analysis_result["requirements_breakdown"]["functional_requirements"].append(
                "User authentication and authorization"
            )
        
        if any(keyword in requirements_lower for keyword in ["api", "integration", "webhook", "service"]):
            analysis_result["requirements_breakdown"]["functional_requirements"].append(
                "API integration and external services"
            )
        
        # Identify non-functional requirements
        if any(keyword in requirements_lower for keyword in ["performance", "speed", "fast", "optimize"]):
            analysis_result["requirements_breakdown"]["non_functional_requirements"].append(
                "Performance optimization requirements"
            )
        
        if any(keyword in requirements_lower for keyword in ["security", "secure", "encrypt", "protect"]):
            analysis_result["requirements_breakdown"]["non_functional_requirements"].append(
                "Security and data protection"
            )
        
        if any(keyword in requirements_lower for keyword in ["scalable", "scale", "handle", "concurrent"]):
            analysis_result["requirements_breakdown"]["non_functional_requirements"].append(
                "Scalability and concurrency"
            )
        
        # Generate user stories
        if "user" in requirements_lower:
            analysis_result["requirements_breakdown"]["user_stories"].append(
                "As a user, I want to interact with the system so that I can accomplish my goals"
            )
        
        if "admin" in requirements_lower:
            analysis_result["requirements_breakdown"]["user_stories"].append(
                "As an administrator, I want to manage system settings so that I can control system behavior"
            )
        
        # Generate acceptance criteria
        analysis_result["requirements_breakdown"]["acceptance_criteria"].extend([
            "System meets all functional requirements",
            "Performance requirements are satisfied",
            "Security requirements are implemented",
            "User interface is intuitive and responsive"
        ])
        
        return json.dumps(analysis_result, indent=2)
    
    async def _arun(self, requirements: str) -> str:
        """Async version of requirements analysis."""
        return self._run(requirements)


class UserStoryGeneratorTool(BaseTool):
    """Tool for generating user stories from requirements."""
    
    name = "user_story_generator"
    description = "Generate user stories and acceptance criteria from requirements"
    
    def _run(self, requirements: str) -> str:
        """Generate user stories from requirements."""
        # Simulated user story generation
        user_stories = {
            "requirements": requirements,
            "generated_stories": [
                {
                    "story_id": "US-001",
                    "title": "User Authentication",
                    "description": "As a user, I want to log into the system so that I can access my personalized content",
                    "acceptance_criteria": [
                        "User can enter username and password",
                        "System validates credentials",
                        "User is redirected to dashboard on successful login",
                        "Error message is shown for invalid credentials"
                    ],
                    "priority": "high",
                    "story_points": 5
                },
                {
                    "story_id": "US-002",
                    "title": "Data Management",
                    "description": "As a user, I want to create, read, update, and delete data so that I can manage my information",
                    "acceptance_criteria": [
                        "User can create new records",
                        "User can view existing records",
                        "User can edit record information",
                        "User can delete records with confirmation"
                    ],
                    "priority": "high",
                    "story_points": 8
                },
                {
                    "story_id": "US-003",
                    "title": "Search and Filter",
                    "description": "As a user, I want to search and filter data so that I can find specific information quickly",
                    "acceptance_criteria": [
                        "User can enter search terms",
                        "System returns relevant results",
                        "User can apply multiple filters",
                        "Search results are sorted by relevance"
                    ],
                    "priority": "medium",
                    "story_points": 5
                }
            ],
            "epic_mapping": {
                "Authentication Epic": ["US-001"],
                "Data Management Epic": ["US-002", "US-003"]
            }
        }
        
        return json.dumps(user_stories, indent=2)
    
    async def _arun(self, requirements: str) -> str:
        """Async version of user story generation."""
        return self._run(requirements)


class TechnicalSpecificationTool(BaseTool):
    """Tool for generating technical specifications."""
    
    name = "technical_specification"
    description = "Generate technical specifications and architecture recommendations"
    
    def _run(self, requirements: str) -> str:
        """Generate technical specifications."""
        # Simulated technical specification
        tech_spec = {
            "requirements": requirements,
            "technical_specifications": {
                "architecture": {
                    "pattern": "MVC (Model-View-Controller)",
                    "layers": ["Presentation", "Business Logic", "Data Access"],
                    "components": ["Controllers", "Services", "Repositories", "Models"]
                },
                "technology_stack": {
                    "backend": {
                        "language": "Python",
                        "framework": "FastAPI",
                        "database": "PostgreSQL",
                        "cache": "Redis"
                    },
                    "frontend": {
                        "framework": "React",
                        "language": "TypeScript",
                        "styling": "Tailwind CSS",
                        "state_management": "Redux"
                    },
                    "infrastructure": {
                        "cloud_provider": "AWS",
                        "containerization": "Docker",
                        "orchestration": "Kubernetes",
                        "monitoring": "CloudWatch"
                    }
                },
                "database_design": {
                    "type": "Relational Database",
                    "tables": ["users", "sessions", "data_records"],
                    "relationships": "One-to-many relationships",
                    "indexes": ["user_id", "created_at", "status"]
                },
                "api_design": {
                    "style": "RESTful API",
                    "authentication": "JWT tokens",
                    "versioning": "URL versioning (/api/v1/)",
                    "documentation": "OpenAPI/Swagger"
                },
                "security_considerations": [
                    "Input validation and sanitization",
                    "SQL injection prevention",
                    "XSS protection",
                    "CSRF protection",
                    "Rate limiting",
                    "HTTPS enforcement"
                ],
                "performance_requirements": {
                    "response_time": "< 200ms for API calls",
                    "throughput": "1000 requests per minute",
                    "availability": "99.9% uptime",
                    "scalability": "Horizontal scaling support"
                }
            },
            "implementation_phases": [
                {
                    "phase": 1,
                    "name": "Foundation",
                    "duration": "1-2 weeks",
                    "tasks": ["Project setup", "Database design", "Basic API structure"]
                },
                {
                    "phase": 2,
                    "name": "Core Features",
                    "duration": "2-3 weeks",
                    "tasks": ["Authentication", "CRUD operations", "Basic UI"]
                },
                {
                    "phase": 3,
                    "name": "Advanced Features",
                    "duration": "1-2 weeks",
                    "tasks": ["Search functionality", "Advanced UI", "Testing"]
                }
            ]
        }
        
        return json.dumps(tech_spec, indent=2)
    
    async def _arun(self, requirements: str) -> str:
        """Async version of technical specification generation."""
        return self._run(requirements)


class RequirementsAgent(BaseAgent):
    """
    Requirements agent for analyzing and clarifying software requirements.
    
    This agent specializes in understanding user needs, breaking down complex
    requirements into actionable tasks, and ensuring requirements are complete
    and implementable.
    """
    
    def __init__(self, config: AgentConfig):
        """Initialize the requirements agent."""
        super().__init__(config)
        
        # Initialize requirements-specific tools
        self.requirements_analysis_tool = RequirementsAnalysisTool()
        self.user_story_generator_tool = UserStoryGeneratorTool()
        self.technical_specification_tool = TechnicalSpecificationTool()
        
        # Add tools to the agent
        self.tools["requirements_analysis"] = self.requirements_analysis_tool
        self.tools["user_story_generator"] = self.user_story_generator_tool
        self.tools["technical_specification"] = self.technical_specification_tool
        
        self.logger.info("Requirements agent initialized with analysis tools")
    
    def _create_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Create requirements-specific tools."""
        if tool_name == "requirements_analysis":
            return RequirementsAnalysisTool()
        elif tool_name == "user_story_generator":
            return UserStoryGeneratorTool()
        elif tool_name == "technical_specification":
            return TechnicalSpecificationTool()
        return None
    
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Process requirements analysis requests.
        
        Args:
            message: Requirements or project description
            context: Optional context information
            
        Returns:
            AgentResponse: Comprehensive requirements analysis and recommendations
        """
        try:
            # Analyze the requirements request
            analysis = await self._analyze_requirements_request(message)
            
            # Gather requirements data
            requirements_data = await self._gather_requirements_data(analysis, message)
            
            # Generate comprehensive requirements response
            requirements_response = await self._generate_requirements_response(message, analysis, requirements_data)
            
            return AgentResponse(
                content=requirements_response,
                confidence=0.9,
                reasoning=f"Analyzed requirements and generated specifications based on: {analysis.get('analysis_type', 'general')}",
                tools_used=analysis.get("tools_used", []),
                metadata={
                    "requirements_analysis": analysis,
                    "requirements_data": requirements_data,
                    "context": context
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error processing requirements request: {str(e)}")
            return AgentResponse(
                content="I apologize, but I'm having trouble analyzing your requirements right now. Please try again or provide more specific details about your project.",
                confidence=0.0,
                reasoning="Error occurred during requirements processing",
                metadata={"error": str(e)}
            )
    
    async def _analyze_requirements_request(self, message: str) -> Dict[str, Any]:
        """Analyze the requirements request to understand what analysis is needed."""
        
        analysis_prompt = f"""
        Analyze this requirements request:
        
        Request: {message}
        
        Determine:
        1. What type of requirements analysis is needed
        2. What information should be gathered
        3. Which tools should be used
        4. The complexity and scope of the project
        
        Provide analysis in JSON format:
        {{
            "analysis_type": "requirements_analysis|user_stories|technical_spec|comprehensive_analysis",
            "project_type": "web_app|mobile_app|api|desktop_app|data_pipeline",
            "complexity": "simple|moderate|complex",
            "scope": "small|medium|large",
            "tools_needed": ["requirements_analysis", "user_story_generator", "technical_specification"],
            "key_domains": ["authentication", "data_management", "ui_ux", "integration"],
            "estimated_effort": "1-2 weeks|2-4 weeks|1-3 months|3+ months",
            "risk_level": "low|medium|high"
        }}
        """
        
        try:
            response = await self._invoke_model(analysis_prompt)
            analysis = json.loads(response)
            return analysis
        except Exception as e:
            self.logger.error(f"Error analyzing requirements request: {str(e)}")
            return {
                "analysis_type": "comprehensive_analysis",
                "project_type": "web_app",
                "complexity": "moderate",
                "scope": "medium",
                "tools_needed": ["requirements_analysis", "user_story_generator"],
                "key_domains": ["data_management", "ui_ux"],
                "estimated_effort": "2-4 weeks",
                "risk_level": "medium"
            }
    
    async def _gather_requirements_data(self, analysis: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Gather requirements data based on the analysis."""
        requirements_data = {}
        tools_used = []
        
        try:
            # Perform requirements analysis if needed
            if "requirements_analysis" in analysis.get("tools_needed", []):
                analysis_result = await self.requirements_analysis_tool._arun(message)
                requirements_data["requirements_analysis"] = analysis_result
                tools_used.append("requirements_analysis")
            
            # Generate user stories if needed
            if "user_story_generator" in analysis.get("tools_needed", []):
                stories_result = await self.user_story_generator_tool._arun(message)
                requirements_data["user_stories"] = stories_result
                tools_used.append("user_story_generator")
            
            # Generate technical specifications if needed
            if "technical_specification" in analysis.get("tools_needed", []):
                tech_spec_result = await self.technical_specification_tool._arun(message)
                requirements_data["technical_specification"] = tech_spec_result
                tools_used.append("technical_specification")
            
            requirements_data["tools_used"] = tools_used
            
        except Exception as e:
            self.logger.error(f"Error gathering requirements data: {str(e)}")
            requirements_data["error"] = str(e)
        
        return requirements_data
    
    async def _generate_requirements_response(self, message: str, analysis: Dict[str, Any], requirements_data: Dict[str, Any]) -> str:
        """Generate a comprehensive requirements response."""
        
        response_prompt = f"""
        You are a requirements analysis expert. Generate a comprehensive requirements analysis based on this request:
        
        Original Request: {message}
        Analysis: {json.dumps(analysis, indent=2)}
        Requirements Data: {json.dumps(requirements_data, indent=2)}
        
        Create a detailed requirements analysis that includes:
        1. Executive summary of the project requirements
        2. Functional requirements breakdown
        3. Non-functional requirements
        4. User stories and acceptance criteria
        5. Technical specifications and recommendations
        6. Implementation phases and timeline
        7. Risk assessment and mitigation strategies
        8. Next steps and recommendations
        
        Be thorough, actionable, and provide specific guidance that can be used
        for development planning and implementation.
        """
        
        try:
            response = await self._invoke_model(response_prompt)
            return response
        except Exception as e:
            self.logger.error(f"Error generating requirements response: {str(e)}")
            return "I apologize, but I'm having trouble generating your requirements analysis right now. Please try again with more specific project details."
    
    async def execute_task(self, task: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute requirements-specific tasks."""
        if task == "analyze_requirements":
            requirements = parameters.get("requirements", "") if parameters else ""
            result = await self.requirements_analysis_tool._arun(requirements)
            return {"requirements_analysis": result}
        
        elif task == "generate_user_stories":
            requirements = parameters.get("requirements", "") if parameters else ""
            result = await self.user_story_generator_tool._arun(requirements)
            return {"user_stories": result}
        
        elif task == "generate_tech_spec":
            requirements = parameters.get("requirements", "") if parameters else ""
            result = await self.technical_specification_tool._arun(requirements)
            return {"technical_specification": result}
        
        elif task == "comprehensive_analysis":
            requirements = parameters.get("requirements", "") if parameters else ""
            analysis = await self._analyze_requirements_request(requirements)
            requirements_data = await self._gather_requirements_data(analysis, requirements)
            response = await self._generate_requirements_response(requirements, analysis, requirements_data)
            return {
                "requirements_analysis": response,
                "analysis": analysis,
                "data": requirements_data
            }
        
        else:
            return {"error": f"Unknown task: {task}"}
