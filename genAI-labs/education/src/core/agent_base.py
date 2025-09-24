"""
Base agent class for all learning platform agents.

This module provides the foundational agent class that all specialized agents inherit from,
ensuring consistent behavior and interface across the learning platform.
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field

import boto3
from langchain.agents import AgentExecutor
from langchain.tools import BaseTool


class AgentConfig(BaseModel):
    """Configuration model for agents."""
    
    name: str = Field(..., description="Agent name")
    model_id: str = Field(default="anthropic.claude-3-5-sonnet-20241022-v2:0", description="Bedrock model ID")
    max_tokens: int = Field(default=4000, description="Maximum tokens for responses")
    temperature: float = Field(default=0.7, description="Model temperature")
    system_prompt: str = Field(..., description="System prompt for the agent")
    capabilities: List[str] = Field(default_factory=list, description="Agent capabilities")
    tools: List[str] = Field(default_factory=list, description="Available tools")
    knowledge_base_id: Optional[str] = Field(None, description="Knowledge base ID")
    guardrail_id: Optional[str] = Field(None, description="Guardrail ID")


class AgentMessage(BaseModel):
    """Message model for agent communication."""
    
    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentResponse(BaseModel):
    """Response model for agent interactions."""
    
    content: str = Field(..., description="Response content")
    confidence: float = Field(default=0.0, description="Response confidence score")
    reasoning: Optional[str] = Field(None, description="Agent reasoning")
    tools_used: List[str] = Field(default_factory=list, description="Tools used")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class BaseAgent(ABC):
    """
    Base class for all learning platform agents.
    
    This class provides the foundational functionality that all specialized agents
    inherit from, including AWS Bedrock integration, conversation management,
    and standardized interfaces.
    """
    
    def __init__(self, config: AgentConfig):
        """Initialize the base agent."""
        self.config = config
        self.logger = logging.getLogger(f"agent.{config.name}")
        self.bedrock = boto3.client('bedrock-runtime')
        self.conversation_history: List[AgentMessage] = []
        self.tools: Dict[str, BaseTool] = {}
        
        # Initialize tools
        self._initialize_tools()
        
        self.logger.info(f"Initialized agent: {config.name}")
    
    def _initialize_tools(self) -> None:
        """Initialize agent tools based on configuration."""
        for tool_name in self.config.tools:
            tool = self._create_tool(tool_name)
            if tool:
                self.tools[tool_name] = tool
                self.logger.info(f"Initialized tool: {tool_name}")
    
    @abstractmethod
    def _create_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Create a specific tool instance."""
        pass
    
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Process a user message and return an agent response.
        
        Args:
            message: User message to process
            context: Optional context information
            
        Returns:
            AgentResponse: Structured response from the agent
        """
        try:
            # Add user message to conversation history
            user_message = AgentMessage(
                role="user",
                content=message,
                metadata=context or {}
            )
            self.conversation_history.append(user_message)
            
            # Prepare the prompt
            prompt = self._prepare_prompt(message, context)
            
            # Invoke the model
            response = await self._invoke_model(prompt)
            
            # Process the response
            agent_response = self._process_response(response, message)
            
            # Add assistant message to conversation history
            assistant_message = AgentMessage(
                role="assistant",
                content=agent_response.content,
                metadata=agent_response.metadata
            )
            self.conversation_history.append(assistant_message)
            
            self.logger.info(f"Processed message for {self.config.name}")
            return agent_response
            
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            return AgentResponse(
                content="I apologize, but I encountered an error processing your request. Please try again.",
                confidence=0.0,
                reasoning="Error occurred during message processing",
                metadata={"error": str(e)}
            )
    
    def _prepare_prompt(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Prepare the prompt for the model."""
        # Build conversation context
        conversation_context = ""
        if self.conversation_history:
            recent_messages = self.conversation_history[-5:]  # Last 5 messages
            for msg in recent_messages:
                conversation_context += f"{msg.role}: {msg.content}\n"
        
        # Add context information
        context_info = ""
        if context:
            context_info = f"\nContext: {json.dumps(context, indent=2)}\n"
        
        # Construct the full prompt
        prompt = f"""
{self.config.system_prompt}

{conversation_context}
{context_info}
User: {message}

Assistant:"""
        
        return prompt.strip()
    
    async def _invoke_model(self, prompt: str) -> str:
        """Invoke the Bedrock model."""
        try:
            response = self.bedrock.invoke_model(
                modelId=self.config.model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": self.config.max_tokens,
                    "temperature": self.config.temperature,
                    "messages": [{"role": "user", "content": prompt}]
                })
            )
            
            result = json.loads(response['body'].read())
            return result['content'][0]['text']
            
        except Exception as e:
            self.logger.error(f"Error invoking model: {str(e)}")
            raise
    
    def _process_response(self, response: str, original_message: str) -> AgentResponse:
        """Process the model response into a structured format."""
        # Extract confidence score (simplified)
        confidence = self._calculate_confidence(response, original_message)
        
        # Extract reasoning if present
        reasoning = self._extract_reasoning(response)
        
        # Identify tools used
        tools_used = self._identify_tools_used(response)
        
        return AgentResponse(
            content=response,
            confidence=confidence,
            reasoning=reasoning,
            tools_used=tools_used,
            metadata={
                "agent_name": self.config.name,
                "model_id": self.config.model_id,
                "original_message": original_message
            }
        )
    
    def _calculate_confidence(self, response: str, original_message: str) -> float:
        """Calculate confidence score for the response."""
        # Simplified confidence calculation
        # In a real implementation, this would be more sophisticated
        if len(response) > 50 and "I don't know" not in response.lower():
            return 0.8
        elif len(response) > 20:
            return 0.6
        else:
            return 0.4
    
    def _extract_reasoning(self, response: str) -> Optional[str]:
        """Extract reasoning from the response if present."""
        # Look for reasoning indicators
        reasoning_indicators = ["because", "since", "therefore", "reason", "explanation"]
        for indicator in reasoning_indicators:
            if indicator in response.lower():
                return f"Reasoning based on: {indicator}"
        return None
    
    def _identify_tools_used(self, response: str) -> List[str]:
        """Identify which tools were used in generating the response."""
        tools_used = []
        for tool_name in self.tools.keys():
            if tool_name.lower() in response.lower():
                tools_used.append(tool_name)
        return tools_used
    
    def get_conversation_history(self) -> List[AgentMessage]:
        """Get the conversation history."""
        return self.conversation_history.copy()
    
    def clear_conversation_history(self) -> None:
        """Clear the conversation history."""
        self.conversation_history.clear()
        self.logger.info(f"Cleared conversation history for {self.config.name}")
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities."""
        return self.config.capabilities.copy()
    
    def get_tools(self) -> List[str]:
        """Get available tools."""
        return list(self.tools.keys())
    
    def add_tool(self, tool_name: str, tool: BaseTool) -> None:
        """Add a new tool to the agent."""
        self.tools[tool_name] = tool
        self.logger.info(f"Added tool: {tool_name}")
    
    def remove_tool(self, tool_name: str) -> None:
        """Remove a tool from the agent."""
        if tool_name in self.tools:
            del self.tools[tool_name]
            self.logger.info(f"Removed tool: {tool_name}")
    
    @abstractmethod
    async def execute_task(self, task: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a specific task for this agent.
        
        Args:
            task: Task to execute
            parameters: Optional parameters for the task
            
        Returns:
            Dict containing task results
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary representation."""
        return {
            "name": self.config.name,
            "model_id": self.config.model_id,
            "capabilities": self.config.capabilities,
            "tools": list(self.tools.keys()),
            "conversation_length": len(self.conversation_history),
            "knowledge_base_id": self.config.knowledge_base_id,
            "guardrail_id": self.config.guardrail_id
        }
