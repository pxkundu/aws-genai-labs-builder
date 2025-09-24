"""
Basic Agent Example for AWS GenAI Learning Platform

This example demonstrates how to create and use a basic agent with simple
capabilities and tools.
"""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from core.agent_base import BaseAgent, AgentConfig
from shared.logging_config import setup_logging


class SimpleAgent(BaseAgent):
    """
    A simple agent that demonstrates basic agent functionality.
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.logger.info("Simple agent initialized")
    
    def _create_tool(self, tool_name: str):
        """Create simple tools for the agent."""
        if tool_name == "calculator":
            return CalculatorTool()
        elif tool_name == "search":
            return SearchTool()
        return None
    
    async def execute_task(self, task: str, parameters=None):
        """Execute simple tasks."""
        if task == "calculate":
            if parameters and "expression" in parameters:
                return {"result": self._calculate(parameters["expression"])}
        elif task == "search":
            if parameters and "query" in parameters:
                return {"results": self._search(parameters["query"])}
        return {"error": f"Unknown task: {task}"}
    
    def _calculate(self, expression: str) -> str:
        """Simple calculation function."""
        try:
            # Basic safety check - only allow numbers and basic operators
            allowed_chars = set('0123456789+-*/.() ')
            if not all(c in allowed_chars for c in expression):
                return "Error: Invalid characters in expression"
            
            result = eval(expression)
            return str(result)
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _search(self, query: str) -> str:
        """Simple search function."""
        # Simulated search results
        results = {
            "python": "Python is a high-level programming language known for its simplicity and readability.",
            "aws": "Amazon Web Services (AWS) is a comprehensive cloud computing platform.",
            "ai": "Artificial Intelligence (AI) refers to the simulation of human intelligence in machines.",
            "machine learning": "Machine Learning is a subset of AI that enables computers to learn without being explicitly programmed."
        }
        
        query_lower = query.lower()
        for key, value in results.items():
            if key in query_lower:
                return value
        
        return f"No specific information found for '{query}'. This is a simple search demonstration."


class CalculatorTool:
    """Simple calculator tool."""
    
    name = "calculator"
    description = "Perform basic arithmetic calculations"
    
    def _run(self, expression: str) -> str:
        """Calculate the result of an expression."""
        try:
            allowed_chars = set('0123456789+-*/.() ')
            if not all(c in allowed_chars for c in expression):
                return "Error: Invalid characters in expression"
            
            result = eval(expression)
            return str(result)
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def _arun(self, expression: str) -> str:
        """Async version of calculation."""
        return self._run(expression)


class SearchTool:
    """Simple search tool."""
    
    name = "search"
    description = "Search for information on various topics"
    
    def _run(self, query: str) -> str:
        """Search for information."""
        results = {
            "python": "Python is a high-level programming language known for its simplicity and readability.",
            "aws": "Amazon Web Services (AWS) is a comprehensive cloud computing platform.",
            "ai": "Artificial Intelligence (AI) refers to the simulation of human intelligence in machines.",
            "machine learning": "Machine Learning is a subset of AI that enables computers to learn without being explicitly programmed."
        }
        
        query_lower = query.lower()
        for key, value in results.items():
            if key in query_lower:
                return value
        
        return f"No specific information found for '{query}'. This is a simple search demonstration."
    
    async def _arun(self, query: str) -> str:
        """Async version of search."""
        return self._run(query)


async def main():
    """Main function to demonstrate the basic agent."""
    # Setup logging
    setup_logging(level="INFO", format_type="text")
    
    print("Basic Agent Example")
    print("==================")
    print()
    
    # Create agent configuration
    config = AgentConfig(
        name="SimpleAgent",
        model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
        max_tokens=1000,
        temperature=0.7,
        system_prompt="You are a helpful assistant that can perform calculations and search for information. Be friendly and concise in your responses.",
        capabilities=["conversation", "calculation", "information_retrieval"],
        tools=["calculator", "search"]
    )
    
    # Create the agent
    agent = SimpleAgent(config)
    
    print(f"Agent: {agent.config.name}")
    print(f"Capabilities: {agent.get_capabilities()}")
    print(f"Tools: {agent.get_tools()}")
    print()
    
    # Example conversations
    conversations = [
        "Hello, can you help me with a simple calculation?",
        "What is 15 * 8?",
        "Can you search for information about Python?",
        "What is 100 / 4?",
        "Thank you for your help!"
    ]
    
    for user_message in conversations:
        print(f"User: {user_message}")
        
        # Process the message
        response = await agent.process_message(user_message)
        
        print(f"Agent: {response.content}")
        print(f"Confidence: {response.confidence:.2f}")
        if response.tools_used:
            print(f"Tools used: {', '.join(response.tools_used)}")
        print()
    
    # Demonstrate task execution
    print("Task Execution Examples:")
    print("=======================")
    
    # Calculate task
    calc_result = await agent.execute_task("calculate", {"expression": "25 + 17"})
    print(f"Calculate 25 + 17: {calc_result}")
    
    # Search task
    search_result = await agent.execute_task("search", {"query": "AWS"})
    print(f"Search for AWS: {search_result}")
    
    print()
    print("Example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
