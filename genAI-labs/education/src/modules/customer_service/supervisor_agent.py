"""
Supervisor Agent for Customer Service System

The supervisor agent acts as the orchestrator, analyzing customer inquiries and
delegating tasks to appropriate specialist agents. It demonstrates agent coordination
and intelligent routing patterns.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from langchain.tools import BaseTool
from langchain.agents import Tool

from ...core.agent_base import BaseAgent, AgentConfig, AgentResponse


class SupervisorAgent(BaseAgent):
    """
    Supervisor agent that orchestrates customer service interactions.
    
    This agent analyzes incoming customer inquiries and delegates them to
    appropriate specialist agents based on the inquiry type and complexity.
    """
    
    def __init__(self, config: AgentConfig, specialist_agents: Dict[str, BaseAgent]):
        """Initialize the supervisor agent with specialist agents."""
        super().__init__(config)
        self.specialist_agents = specialist_agents
        self.delegation_history: List[Dict[str, Any]] = []
        
        # Initialize delegation tools
        self._initialize_delegation_tools()
        
        self.logger.info(f"Supervisor agent initialized with {len(specialist_agents)} specialist agents")
    
    def _initialize_delegation_tools(self) -> None:
        """Initialize tools for delegating to specialist agents."""
        for agent_name, agent in self.specialist_agents.items():
            tool = Tool(
                name=f"delegate_to_{agent_name}",
                description=f"Delegate customer inquiry to {agent_name}",
                func=lambda inquiry, agent=agent: self._delegate_to_agent(inquiry, agent)
            )
            self.tools[f"delegate_to_{agent_name}"] = tool
    
    def _create_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Create delegation tools."""
        if tool_name.startswith("delegate_to_"):
            agent_name = tool_name.replace("delegate_to_", "")
            if agent_name in self.specialist_agents:
                return Tool(
                    name=tool_name,
                    description=f"Delegate to {agent_name}",
                    func=lambda inquiry: self._delegate_to_agent(inquiry, self.specialist_agents[agent_name])
                )
        return None
    
    async def _delegate_to_agent(self, inquiry: str, agent: BaseAgent) -> str:
        """Delegate an inquiry to a specialist agent."""
        try:
            self.logger.info(f"Delegating inquiry to {agent.config.name}")
            
            # Record delegation
            delegation_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "target_agent": agent.config.name,
                "inquiry": inquiry,
                "status": "delegated"
            }
            self.delegation_history.append(delegation_record)
            
            # Process with specialist agent
            response = await agent.process_message(inquiry)
            
            # Update delegation record
            delegation_record["status"] = "completed"
            delegation_record["response"] = response.content
            delegation_record["confidence"] = response.confidence
            
            return response.content
            
        except Exception as e:
            self.logger.error(f"Error delegating to {agent.config.name}: {str(e)}")
            delegation_record["status"] = "failed"
            delegation_record["error"] = str(e)
            return f"I apologize, but I encountered an error while processing your request with our {agent.config.name}. Please try again or contact our support team."
    
    async def process_customer_inquiry(self, inquiry: str, customer_context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Process a customer inquiry by analyzing and delegating appropriately.
        
        Args:
            inquiry: Customer inquiry text
            customer_context: Optional customer context information
            
        Returns:
            AgentResponse: Response from the appropriate specialist agent
        """
        try:
            # Analyze the inquiry to determine the best specialist agent
            analysis = await self._analyze_inquiry(inquiry, customer_context)
            
            # Select the appropriate specialist agent
            selected_agent = self._select_specialist_agent(analysis)
            
            if selected_agent:
                # Delegate to specialist agent
                specialist_response = await self._delegate_to_agent(inquiry, selected_agent)
                
                return AgentResponse(
                    content=specialist_response,
                    confidence=0.9,  # High confidence in delegation
                    reasoning=f"Delegated to {selected_agent.config.name} based on inquiry analysis",
                    tools_used=[f"delegate_to_{selected_agent.config.name}"],
                    metadata={
                        "delegation_analysis": analysis,
                        "selected_agent": selected_agent.config.name,
                        "customer_context": customer_context
                    }
                )
            else:
                # Handle directly if no specialist is needed
                return await self._handle_directly(inquiry, customer_context)
                
        except Exception as e:
            self.logger.error(f"Error processing customer inquiry: {str(e)}")
            return AgentResponse(
                content="I apologize, but I'm experiencing technical difficulties. Please try again or contact our support team directly.",
                confidence=0.0,
                reasoning="Error occurred during inquiry processing",
                metadata={"error": str(e)}
            )
    
    async def _analyze_inquiry(self, inquiry: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze the customer inquiry to determine the appropriate specialist agent."""
        
        analysis_prompt = f"""
        Analyze this customer inquiry and determine the best specialist agent to handle it.
        
        Customer Inquiry: {inquiry}
        Context: {json.dumps(context or {}, indent=2)}
        
        Available specialist agents:
        - ProductSpecialist: Product information, features, specifications, comparisons
        - TechnicalSupport: Technical issues, troubleshooting, system problems
        - BillingAgent: Billing questions, payments, refunds, account issues
        - KnowledgeBaseAgent: General information, FAQs, documentation
        
        Provide analysis in JSON format:
        {{
            "inquiry_type": "product|technical|billing|general",
            "complexity": "simple|moderate|complex",
            "urgency": "low|medium|high",
            "recommended_agent": "agent_name",
            "confidence": 0.0-1.0,
            "reasoning": "explanation of recommendation",
            "keywords": ["keyword1", "keyword2"],
            "sentiment": "positive|neutral|negative"
        }}
        """
        
        try:
            response = await self._invoke_model(analysis_prompt)
            analysis = json.loads(response)
            return analysis
        except Exception as e:
            self.logger.error(f"Error analyzing inquiry: {str(e)}")
            return {
                "inquiry_type": "general",
                "complexity": "moderate",
                "urgency": "medium",
                "recommended_agent": "KnowledgeBaseAgent",
                "confidence": 0.5,
                "reasoning": "Default fallback due to analysis error",
                "keywords": [],
                "sentiment": "neutral"
            }
    
    def _select_specialist_agent(self, analysis: Dict[str, Any]) -> Optional[BaseAgent]:
        """Select the appropriate specialist agent based on analysis."""
        recommended_agent = analysis.get("recommended_agent")
        confidence = analysis.get("confidence", 0.0)
        
        # Only delegate if confidence is high enough
        if confidence >= 0.7 and recommended_agent in self.specialist_agents:
            return self.specialist_agents[recommended_agent]
        
        # Fallback to knowledge base agent for general inquiries
        if "KnowledgeBaseAgent" in self.specialist_agents:
            return self.specialist_agents["KnowledgeBaseAgent"]
        
        return None
    
    async def _handle_directly(self, inquiry: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Handle inquiry directly without delegation."""
        
        direct_response_prompt = f"""
        You are a customer service supervisor. Handle this customer inquiry directly:
        
        Inquiry: {inquiry}
        Context: {json.dumps(context or {}, indent=2)}
        
        Provide a helpful, professional response. If you cannot fully resolve the inquiry,
        suggest next steps or offer to connect them with a specialist.
        """
        
        try:
            response = await self._invoke_model(direct_response_prompt)
            return AgentResponse(
                content=response,
                confidence=0.7,
                reasoning="Handled directly by supervisor",
                tools_used=[],
                metadata={"handling_method": "direct", "customer_context": context}
            )
        except Exception as e:
            self.logger.error(f"Error handling inquiry directly: {str(e)}")
            return AgentResponse(
                content="I apologize, but I'm unable to process your request at the moment. Please try again or contact our support team.",
                confidence=0.0,
                reasoning="Error in direct handling",
                metadata={"error": str(e)}
            )
    
    async def execute_task(self, task: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute supervisor-specific tasks."""
        if task == "analyze_inquiry":
            inquiry = parameters.get("inquiry", "") if parameters else ""
            context = parameters.get("context") if parameters else None
            analysis = await self._analyze_inquiry(inquiry, context)
            return {"analysis": analysis}
        
        elif task == "get_delegation_history":
            return {"delegation_history": self.delegation_history}
        
        elif task == "get_agent_status":
            agent_status = {}
            for name, agent in self.specialist_agents.items():
                agent_status[name] = {
                    "available": True,
                    "conversation_length": len(agent.conversation_history),
                    "capabilities": agent.get_capabilities(),
                    "tools": agent.get_tools()
                }
            return {"agent_status": agent_status}
        
        else:
            return {"error": f"Unknown task: {task}"}
    
    def get_delegation_statistics(self) -> Dict[str, Any]:
        """Get statistics about delegation patterns."""
        if not self.delegation_history:
            return {"total_delegations": 0}
        
        # Count delegations by agent
        agent_counts = {}
        success_count = 0
        
        for record in self.delegation_history:
            agent = record.get("target_agent", "unknown")
            agent_counts[agent] = agent_counts.get(agent, 0) + 1
            
            if record.get("status") == "completed":
                success_count += 1
        
        return {
            "total_delegations": len(self.delegation_history),
            "successful_delegations": success_count,
            "success_rate": success_count / len(self.delegation_history) if self.delegation_history else 0,
            "delegations_by_agent": agent_counts,
            "recent_delegations": self.delegation_history[-5:]  # Last 5 delegations
        }
