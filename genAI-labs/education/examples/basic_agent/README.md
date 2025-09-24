# Basic Agent Example

This example demonstrates how to create and use a basic agent in the AWS GenAI Learning Platform.

## Overview

The basic agent example shows:
- Creating a simple agent with basic capabilities
- Processing user messages
- Using tools and knowledge bases
- Handling agent responses

## Files

- `basic_agent_example.py` - Main example script
- `simple_agent.py` - Simple agent implementation
- `basic_tools.py` - Basic tools for the agent

## Running the Example

```bash
# Navigate to the example directory
cd examples/basic_agent

# Install dependencies
pip install -r requirements.txt

# Run the example
python basic_agent_example.py
```

## Example Output

```
Basic Agent Example
==================

Agent: SimpleAgent
Capabilities: ['conversation', 'information_retrieval']
Tools: ['search_tool', 'calculator_tool']

User: Hello, can you help me with a simple calculation?
Agent: Hello! I'd be happy to help you with a calculation. I can perform basic arithmetic operations like addition, subtraction, multiplication, and division. What calculation would you like me to perform?

User: What is 15 * 8?
Agent: 15 * 8 = 120

User: Thank you!
Agent: You're welcome! Is there anything else I can help you with?
```

## Key Concepts Demonstrated

1. **Agent Creation**: How to create a basic agent with configuration
2. **Message Processing**: How agents process user messages
3. **Tool Usage**: How agents use tools to perform tasks
4. **Response Generation**: How agents generate appropriate responses
5. **Conversation Management**: How agents maintain conversation context

## Next Steps

After understanding this basic example, you can:
- Explore the multi-agent examples
- Learn about agent orchestration
- Build custom agents for specific use cases
- Integrate with AWS services
