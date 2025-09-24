# Module 1: Customer Service Agent System Tutorial

This tutorial will guide you through building and understanding a multi-agent customer service system using AWS GenAI services.

## 🎯 Learning Objectives

By the end of this tutorial, you will:
- Understand how multi-agent systems work in customer service scenarios
- Learn agent delegation and coordination patterns
- Build a supervisor agent that orchestrates specialist agents
- Implement specialized agents for different types of customer inquiries
- Practice with real-world customer service workflows

## 🏗️ Architecture Overview

```
Customer Inquiry
       ↓
Supervisor Agent (Orchestrator)
       ↓
Specialist Agents:
├── Product Specialist Agent
├── Technical Support Agent
├── Billing Agent
└── Knowledge Base Agent
       ↓
Coordinated Response
```

## 📋 Prerequisites

- Completed the [Getting Started Guide](./getting-started.md)
- Basic understanding of Python and AWS services
- Access to AWS Bedrock (for LLM models)

## 🚀 Step 1: Understanding the Supervisor Agent

The supervisor agent is the orchestrator that:
- Analyzes incoming customer inquiries
- Determines the appropriate specialist agent
- Delegates tasks to specialist agents
- Coordinates responses

### Key Features

```python
class SupervisorAgent(BaseAgent):
    def __init__(self, config: AgentConfig, specialist_agents: Dict[str, BaseAgent]):
        super().__init__(config)
        self.specialist_agents = specialist_agents
        self.delegation_history = []
    
    async def process_customer_inquiry(self, inquiry: str, context: Optional[Dict[str, Any]] = None):
        # Analyze the inquiry
        analysis = await self._analyze_inquiry(inquiry, context)
        
        # Select appropriate specialist
        selected_agent = self._select_specialist_agent(analysis)
        
        # Delegate to specialist
        if selected_agent:
            response = await self._delegate_to_agent(inquiry, selected_agent)
            return response
```

## 🛠️ Step 2: Building Specialist Agents

### Product Specialist Agent

Handles product-related inquiries:

```python
class ProductSpecialistAgent(BaseAgent):
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.tools = {
            "product_search": ProductSearchTool(),
            "product_comparison": ProductComparisonTool(),
            "inventory_check": InventoryCheckTool()
        }
    
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None):
        # Analyze product inquiry
        analysis = await self._analyze_product_inquiry(message)
        
        # Gather product information
        product_info = await self._gather_product_information(analysis, message)
        
        # Generate response
        response = await self._generate_product_response(message, analysis, product_info)
        return response
```

### Technical Support Agent

Resolves technical issues:

```python
class TechnicalSupportAgent(BaseAgent):
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.tools = {
            "troubleshooting_guide": TroubleshootingTool(),
            "system_diagnostics": DiagnosticsTool(),
            "ticket_creation": TicketCreationTool()
        }
```

## 🎮 Step 3: Hands-On Exercise

### Exercise 1: Basic Customer Inquiry Handling

**Objective**: Process a simple customer inquiry through the supervisor agent

**Steps**:

1. **Start the Customer Service Module**
   ```bash
   python -m src.modules.customer_service.customer_service_module
   ```

2. **Send a Test Inquiry**
   ```python
   inquiry = "I need help with my laptop order. When will it be delivered?"
   
   response = await supervisor_agent.process_customer_inquiry(inquiry)
   print(f"Response: {response.content}")
   ```

3. **Observe the Delegation Process**
   - The supervisor analyzes the inquiry
   - Identifies it as a product-related question
   - Delegates to the Product Specialist Agent
   - Returns a coordinated response

### Exercise 2: Multi-Agent Coordination

**Objective**: Handle a complex inquiry requiring multiple agents

**Steps**:

1. **Send a Complex Inquiry**
   ```python
   complex_inquiry = """
   I'm having trouble with my laptop that I ordered last week. 
   The screen is flickering and I can't access my account to check the warranty. 
   Can you help me with both the technical issue and billing information?
   """
   ```

2. **Observe Multi-Agent Coordination**
   - Supervisor identifies multiple issues
   - Coordinates between Technical Support and Billing agents
   - Provides a comprehensive response

## 🔧 Step 4: Customizing Agent Behavior

### Adding Custom Tools

Create a new tool for the Product Specialist:

```python
class WarrantyCheckTool(BaseTool):
    name = "warranty_check"
    description = "Check product warranty information"
    
    def _run(self, product_id: str) -> str:
        # Simulate warranty check
        warranty_info = {
            "product_id": product_id,
            "warranty_status": "active",
            "expiry_date": "2025-12-31",
            "coverage": "2 years hardware, 1 year software"
        }
        return json.dumps(warranty_info, indent=2)
```

### Modifying Agent Prompts

Customize the supervisor agent's system prompt:

```python
config = AgentConfig(
    name="CustomerServiceSupervisor",
    system_prompt="""
    You are a customer service supervisor with expertise in:
    - Analyzing customer inquiries
    - Delegating to appropriate specialists
    - Ensuring customer satisfaction
    - Coordinating multi-agent responses
    
    Always be helpful, professional, and empathetic.
    """,
    capabilities=["delegation", "coordination", "customer_service"]
)
```

## 📊 Step 5: Monitoring and Analytics

### Tracking Agent Performance

```python
# Get delegation statistics
stats = supervisor_agent.get_delegation_statistics()
print(f"Total delegations: {stats['total_delegations']}")
print(f"Success rate: {stats['success_rate']:.2%}")
print(f"Delegations by agent: {stats['delegations_by_agent']}")
```

### Conversation Analytics

```python
# Analyze conversation patterns
conversation_history = supervisor_agent.get_conversation_history()
for message in conversation_history:
    print(f"{message.role}: {message.content}")
    print(f"Timestamp: {message.timestamp}")
```

## 🧪 Step 6: Testing Your Implementation

### Unit Tests

Create tests for your agents:

```python
import pytest

@pytest.mark.asyncio
async def test_supervisor_delegation():
    # Test supervisor delegation logic
    supervisor = SupervisorAgent(config, specialist_agents)
    
    inquiry = "I need help with my product order"
    response = await supervisor.process_customer_inquiry(inquiry)
    
    assert response.confidence > 0.7
    assert "delegate_to_" in response.tools_used[0]

@pytest.mark.asyncio
async def test_product_specialist():
    # Test product specialist functionality
    product_agent = ProductSpecialistAgent(config)
    
    inquiry = "What are the specifications of the ProBook X1?"
    response = await product_agent.process_message(inquiry)
    
    assert "ProBook X1" in response.content
    assert "product_search" in response.tools_used
```

### Integration Tests

Test the complete workflow:

```python
@pytest.mark.asyncio
async def test_complete_customer_service_workflow():
    # Test end-to-end customer service workflow
    module = CustomerServiceModule(config)
    
    # Start a customer service session
    session = await module.start_session("test_user")
    
    # Process multiple inquiries
    inquiries = [
        "I need help with my order",
        "What's the warranty on my laptop?",
        "I'm having technical issues"
    ]
    
    for inquiry in inquiries:
        response = await module.process_inquiry(session["session_id"], inquiry)
        assert response["success"] == True
```

## 🎯 Step 7: Advanced Features

### Implementing Guardrails

Add content filtering and safety measures:

```python
# Configure Bedrock guardrails
guardrail_config = {
    "guardrail_id": "customer-service-guardrail",
    "content_filters": ["PII", "inappropriate_content"],
    "word_policy": "block_profanity"
}

config = AgentConfig(
    name="SupervisorAgent",
    guardrail_id="customer-service-guardrail",
    # ... other config
)
```

### Knowledge Base Integration

Connect agents to knowledge bases:

```python
# Configure knowledge base
knowledge_base_config = {
    "knowledge_base_id": "customer-service-kb",
    "data_sources": ["product_catalog", "faq", "troubleshooting_guides"]
}

config = AgentConfig(
    name="ProductSpecialistAgent",
    knowledge_base_id="customer-service-kb",
    # ... other config
)
```

## 📈 Step 8: Performance Optimization

### Caching Responses

Implement response caching:

```python
import redis

class CachedAgent(BaseAgent):
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
    
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None):
        # Check cache first
        cache_key = f"agent:{self.config.name}:{hash(message)}"
        cached_response = self.redis_client.get(cache_key)
        
        if cached_response:
            return json.loads(cached_response)
        
        # Process message normally
        response = await super().process_message(message, context)
        
        # Cache the response
        self.redis_client.setex(cache_key, 3600, json.dumps(response.dict()))
        
        return response
```

### Load Balancing

Implement load balancing for multiple agent instances:

```python
class LoadBalancedAgentPool:
    def __init__(self, agent_configs: List[AgentConfig]):
        self.agents = [Agent(config) for config in agent_configs]
        self.current_index = 0
    
    def get_agent(self) -> Agent:
        agent = self.agents[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.agents)
        return agent
```

## 🎓 Step 9: Best Practices

### Agent Design Principles

1. **Single Responsibility**: Each agent should have a clear, focused purpose
2. **Loose Coupling**: Agents should be independent and communicate through well-defined interfaces
3. **Error Handling**: Implement robust error handling and fallback mechanisms
4. **Monitoring**: Track agent performance and usage patterns
5. **Scalability**: Design agents to handle varying loads

### Security Considerations

1. **Input Validation**: Validate all inputs to prevent injection attacks
2. **Access Control**: Implement proper authentication and authorization
3. **Data Privacy**: Protect customer data and PII
4. **Audit Logging**: Log all agent interactions for compliance

## 🚀 Next Steps

Congratulations! You've completed Module 1. Here's what to do next:

1. **Review Your Implementation**: Make sure you understand how the agents work together
2. **Experiment with Customizations**: Try adding new tools or modifying agent behavior
3. **Move to Module 2**: Learn about Content Creation Agent Systems
4. **Build Your Own**: Create a custom customer service system for your use case

## 📚 Additional Resources

- **[Customer Service API Reference](./api/customer-service.md)**
- **[Agent Development Best Practices](./best-practices.md)**
- **[Multi-Agent Coordination Patterns](./multi-agent-patterns.md)**
- **[AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)**

---

**Ready for the next challenge? Move on to Module 2: Content Creation Agent System! 🚀**
