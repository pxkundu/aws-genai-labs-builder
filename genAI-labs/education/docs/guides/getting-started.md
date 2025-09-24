# Getting Started with AWS GenAI Learning Platform

Welcome to the AWS GenAI Learning Platform! This guide will help you get started with learning AWS Generative AI services through hands-on, agent-based solution architectures.

## 🎯 What You'll Learn

By the end of this guide, you'll understand:
- How to set up and run the learning platform
- Basic concepts of LLM agents and multi-agent systems
- How to interact with different learning modules
- How to build and customize your own agents

## 🚀 Quick Start

### Prerequisites

Before you begin, ensure you have:

- **Python 3.9+** installed
- **AWS CLI** configured with appropriate permissions
- **Docker** (optional, for containerized development)
- **Git** for cloning the repository

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd genAI-labs/education
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp config/environments/development.env.example config/environments/development.env
   # Edit the .env file with your AWS credentials and settings
   ```

5. **Start the platform**
   ```bash
   python -m src.api.main
   ```

The platform will be available at `http://localhost:8000`

## 📚 Learning Modules Overview

The platform includes 5 comprehensive learning modules:

### Module 1: Customer Service Agent System
**Difficulty**: Beginner  
**Duration**: 2-3 hours  
**Focus**: Multi-agent customer support with specialized roles

- **Supervisor Agent**: Orchestrates customer inquiries
- **Product Specialist Agent**: Handles product-related questions
- **Technical Support Agent**: Resolves technical issues
- **Billing Agent**: Manages billing inquiries
- **Knowledge Base Agent**: Retrieves relevant information

### Module 2: Content Creation Agent System
**Difficulty**: Beginner  
**Duration**: 2-3 hours  
**Focus**: AI-powered content generation and management

- **Content Strategy Agent**: Plans content themes and topics
- **Writer Agent**: Generates articles and marketing copy
- **Editor Agent**: Reviews and improves content quality
- **SEO Agent**: Optimizes content for search engines
- **Publishing Agent**: Manages content distribution

### Module 3: Code Generation Agent System
**Difficulty**: Intermediate  
**Duration**: 3-4 hours  
**Focus**: Intelligent software development assistance

- **Requirements Agent**: Analyzes and clarifies software requirements
- **Architecture Agent**: Designs system architecture
- **Developer Agent**: Generates code for specific components
- **Testing Agent**: Creates test cases and validates code
- **Documentation Agent**: Generates technical documentation

### Module 4: Data Analysis Agent System
**Difficulty**: Intermediate  
**Duration**: 3-4 hours  
**Focus**: Automated data processing and insights

- **Data Ingestion Agent**: Collects and validates data
- **Cleaning Agent**: Preprocesses and cleans raw data
- **Analysis Agent**: Performs statistical and ML analysis
- **Visualization Agent**: Creates charts and dashboards
- **Reporting Agent**: Generates insights and recommendations

### Module 5: Multi-Agent Orchestration System
**Difficulty**: Advanced  
**Duration**: 4-5 hours  
**Focus**: Complex workflow management with agent coordination

- **Workflow Orchestrator**: Manages complex multi-step processes
- **Task Scheduler Agent**: Optimizes task execution order
- **Resource Manager Agent**: Allocates computational resources
- **Quality Assurance Agent**: Monitors and validates outputs
- **Error Handler Agent**: Manages failures and recovery

## 🎮 Your First Exercise

Let's start with a simple exercise from Module 1 (Customer Service):

1. **Access the platform** at `http://localhost:8000`

2. **Navigate to Module 1** (Customer Service)

3. **Start Exercise 1**: "Basic Customer Inquiry Handling"

4. **Follow the instructions** to interact with the supervisor agent

5. **Observe how** the supervisor delegates to specialist agents

## 🔧 Understanding Agent Architecture

### Basic Agent Structure

Every agent in the platform follows this structure:

```python
class MyAgent(BaseAgent):
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        # Initialize agent-specific components
    
    def _create_tool(self, tool_name: str):
        # Create and return tools
        pass
    
    async def execute_task(self, task: str, parameters=None):
        # Execute specific tasks
        pass
```

### Key Components

- **Agent Config**: Defines the agent's behavior and capabilities
- **Tools**: Functions the agent can use to perform tasks
- **Knowledge Base**: Information the agent can access
- **Conversation History**: Context from previous interactions

## 🛠️ Customizing Agents

### Creating Custom Tools

```python
class MyCustomTool(BaseTool):
    name = "my_tool"
    description = "Description of what this tool does"
    
    def _run(self, input_data: str) -> str:
        # Tool implementation
        return "Tool result"
    
    async def _arun(self, input_data: str) -> str:
        # Async version
        return self._run(input_data)
```

### Modifying Agent Behavior

```python
# Create custom agent configuration
config = AgentConfig(
    name="MyCustomAgent",
    model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
    system_prompt="You are a specialized agent that...",
    capabilities=["custom_capability"],
    tools=["my_tool"]
)
```

## 📊 Learning Analytics

The platform tracks your progress and provides insights:

- **Exercise Completion**: Track which exercises you've completed
- **Agent Interactions**: Monitor your interactions with different agents
- **Learning Path**: See your progress through the learning modules
- **Performance Metrics**: Understand how well you're performing

## 🔍 Troubleshooting

### Common Issues

1. **AWS Credentials Not Found**
   ```bash
   aws configure
   # Enter your AWS Access Key ID and Secret Access Key
   ```

2. **Port Already in Use**
   ```bash
   # Change the port in config/environments/development.env
   API_PORT=8001
   ```

3. **Module Import Errors**
   ```bash
   # Ensure you're in the correct directory and virtual environment
   cd genAI-labs/education
   source venv/bin/activate
   ```

### Getting Help

- **Documentation**: Check the docs/ directory for detailed guides
- **Examples**: Look at the examples/ directory for code samples
- **Issues**: Report problems via GitHub issues
- **Community**: Join discussions for questions and ideas

## 🎯 Next Steps

Now that you're set up, here's what to do next:

1. **Complete Module 1**: Start with the Customer Service module
2. **Explore Examples**: Try the examples in the examples/ directory
3. **Build Custom Agents**: Create your own agents for specific use cases
4. **Join the Community**: Connect with other learners and share experiences

## 📖 Additional Resources

- **[API Documentation](./api/README.md)**: Complete API reference
- **[Agent Development Guide](./agent-development.md)**: Building custom agents
- **[Multi-Agent Patterns](./multi-agent-patterns.md)**: Advanced coordination
- **[Best Practices](./best-practices.md)**: Development guidelines

---

**Ready to start learning? Begin with Module 1 and build your way up to complex multi-agent systems! 🚀**
