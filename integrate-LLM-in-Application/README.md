# 🤖 Integrate LLM in Your Applications

> **A comprehensive guide and industry-specific examples for integrating LLM and AI capabilities into real-world applications**

[![AWS](https://img.shields.io/badge/AWS-Bedrock-orange?logo=amazon-aws)](https://aws.amazon.com/bedrock/)
[![OpenAI](https://img.shields.io/badge/OpenAI-API-green)](https://openai.com/)
[![LangChain](https://img.shields.io/badge/LangChain-Framework-blue)](https://langchain.com/)

## 🎯 Overview

This repository provides a practical, production-ready approach to integrating Large Language Models (LLMs) and AI capabilities into your applications. It includes industry-specific implementations, complete codebases, and best practices for real-world deployment.

## 📦 Industry Solutions

### 🛒 E-Commerce & Retail
**Location:** `ecommerce-retail/`

A complete e-commerce platform with AI-powered features:
- **Smart Product Recommendations** - Personalized suggestions using customer behavior
- **AI Customer Support** - 24/7 intelligent chatbot for order inquiries
- **Product Description Generation** - Auto-generate compelling product descriptions
- **Review Sentiment Analysis** - Understand customer feedback at scale
- **Inventory Insights** - AI-powered demand forecasting and insights

**Key Features:**
- Multi-LLM support (OpenAI, AWS Bedrock)
- RAG-based product knowledge base
- Real-time recommendation engine
- Sentiment analysis for reviews
- Production-ready infrastructure

[📖 View E-Commerce Solution](./ecommerce-retail/README.md) | [🏗️ Architecture](./ecommerce-retail/architecture.md)

---

## 🚀 Quick Start

### For E-Commerce Solution

```bash
cd ecommerce-retail
# Setup environment
cp config/.env.example config/.env
# Install dependencies
pip install -r requirements.txt
# Run locally
docker-compose up
```

### General Integration Guide

See the sections below for step-by-step integration approaches.

## 📋 Table of Contents

- [Why Integrate LLMs?](#-why-integrate-llms)
- [Integration Approaches](#-integration-approaches)
- [Quick Start Examples](#-quick-start-examples)
- [Common Use Cases](#-common-use-cases)
- [Best Practices](#-best-practices)
- [Architecture Patterns](#-architecture-patterns)
- [Cost Considerations](#-cost-considerations)

## 💡 Why Integrate LLMs?

LLMs can enhance your applications with:

| Capability | Description | Example Use Case |
|------------|-------------|------------------|
| **Text Generation** | Create human-like content | Product descriptions, emails |
| **Summarization** | Condense long documents | Meeting notes, articles |
| **Q&A** | Answer questions from context | Customer support, documentation |
| **Code Assistance** | Generate and explain code | Developer tools, automation |
| **Translation** | Multi-language support | Global applications |
| **Sentiment Analysis** | Understand user emotions | Feedback analysis, social media |

## 🔧 Integration Approaches

### 1. Direct API Integration (Simplest)

The fastest way to add LLM capabilities — call the API directly from your application.

```python
# Example: Using OpenAI API
import openai

client = openai.OpenAI(api_key="your-api-key")

def generate_response(prompt):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Usage
result = generate_response("Summarize this article: ...")
```

```python
# Example: Using AWS Bedrock
import boto3
import json

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

def invoke_claude(prompt):
    response = bedrock.invoke_model(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}]
        })
    )
    return json.loads(response['body'].read())['content'][0]['text']

# Usage
result = invoke_claude("Explain quantum computing in simple terms")
```

### 2. Framework-Based Integration (Recommended)

Use frameworks like LangChain for more complex workflows.

```python
# Example: LangChain with conversation memory
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

llm = ChatOpenAI(model="gpt-4", temperature=0.7)
memory = ConversationBufferMemory()
conversation = ConversationChain(llm=llm, memory=memory)

# Maintains context across interactions
response1 = conversation.predict(input="My name is John")
response2 = conversation.predict(input="What's my name?")  # Remembers "John"
```

### 3. RAG (Retrieval-Augmented Generation)

Combine LLMs with your own data for accurate, contextual responses.

```python
# Example: Simple RAG implementation
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter

# 1. Load and split your documents
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
documents = text_splitter.split_documents(your_documents)

# 2. Create embeddings and vector store
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(documents, embeddings)

# 3. Query with context
def ask_with_context(question):
    relevant_docs = vectorstore.similarity_search(question, k=3)
    context = "\n".join([doc.page_content for doc in relevant_docs])
    
    llm = ChatOpenAI(model="gpt-4")
    prompt = f"Context: {context}\n\nQuestion: {question}\nAnswer:"
    return llm.predict(prompt)
```

## 🚀 Quick Start Examples

### Add a Chatbot to Your Web App

```javascript
// Frontend: React component
import { useState } from 'react';

function ChatBot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  const sendMessage = async () => {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: input })
    });
    const data = await response.json();
    setMessages([...messages, 
      { role: 'user', content: input },
      { role: 'assistant', content: data.response }
    ]);
    setInput('');
  };

  return (
    <div className="chatbot">
      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={msg.role}>{msg.content}</div>
        ))}
      </div>
      <input value={input} onChange={e => setInput(e.target.value)} />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
}
```

```python
# Backend: FastAPI endpoint
from fastapi import FastAPI
from pydantic import BaseModel
import openai

app = FastAPI()
client = openai.OpenAI()

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat(request: ChatRequest):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": request.message}
        ]
    )
    return {"response": response.choices[0].message.content}
```

### Add Smart Search to Your Application

```python
# Semantic search with embeddings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

class SmartSearch:
    def __init__(self, documents):
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = Chroma.from_documents(documents, self.embeddings)
    
    def search(self, query, top_k=5):
        results = self.vectorstore.similarity_search(query, k=top_k)
        return [{"content": r.page_content, "metadata": r.metadata} for r in results]

# Usage
search = SmartSearch(your_documents)
results = search.search("How do I reset my password?")
```

### Automate Content Generation

```python
# Generate product descriptions
def generate_product_description(product_name, features, tone="professional"):
    prompt = f"""
    Generate a compelling product description for:
    Product: {product_name}
    Features: {', '.join(features)}
    Tone: {tone}
    
    Keep it under 150 words and highlight key benefits.
    """
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Usage
description = generate_product_description(
    "Smart Water Bottle",
    ["Temperature display", "Hydration reminders", "BPA-free"],
    tone="friendly"
)
```

## 📦 Common Use Cases

### 1. Customer Support Automation

```python
class SupportBot:
    def __init__(self, knowledge_base):
        self.kb = knowledge_base  # Your FAQ/documentation
        
    def handle_query(self, user_query):
        # Find relevant context from knowledge base
        context = self.kb.search(user_query)
        
        prompt = f"""
        You are a helpful customer support agent.
        Use the following context to answer the question.
        If you don't know, say "I'll connect you with a human agent."
        
        Context: {context}
        Question: {user_query}
        """
        
        return self.generate_response(prompt)
```

### 2. Document Summarization

```python
def summarize_document(document, max_length=200):
    prompt = f"""
    Summarize the following document in {max_length} words or less.
    Focus on key points and actionable insights.
    
    Document:
    {document}
    """
    return generate_response(prompt)
```

### 3. Code Review Assistant

```python
def review_code(code, language="python"):
    prompt = f"""
    Review this {language} code and provide:
    1. Potential bugs or issues
    2. Performance improvements
    3. Best practice suggestions
    
    Code:
    ```{language}
    {code}
    ```
    """
    return generate_response(prompt)
```

## ✅ Best Practices

### 1. Prompt Engineering

```python
# ❌ Bad: Vague prompt
response = generate("Write something about dogs")

# ✅ Good: Specific, structured prompt
response = generate("""
    Write a 100-word blog introduction about:
    Topic: Benefits of adopting rescue dogs
    Tone: Warm and encouraging
    Target audience: First-time pet owners
    Include: One surprising statistic
""")
```

### 2. Error Handling & Retries

```python
import time
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def safe_llm_call(prompt):
    try:
        return client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
    except openai.RateLimitError:
        time.sleep(60)
        raise
    except openai.APIError as e:
        print(f"API error: {e}")
        raise
```

### 3. Caching Responses

```python
import hashlib
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_llm_call(prompt_hash):
    # Actual LLM call
    pass

def generate_with_cache(prompt):
    prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
    return cached_llm_call(prompt_hash)
```

### 4. Input Validation & Safety

```python
def safe_generate(user_input, max_input_length=4000):
    # Truncate long inputs
    if len(user_input) > max_input_length:
        user_input = user_input[:max_input_length]
    
    # Add safety system prompt
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Refuse harmful requests."},
        {"role": "user", "content": user_input}
    ]
    
    return client.chat.completions.create(model="gpt-4", messages=messages)
```

## 🏗️ Architecture Patterns

### Simple Integration
```
User → Your App → LLM API → Response
```

### With Caching
```
User → Your App → Cache Check → [Hit] → Cached Response
                      ↓ [Miss]
                  LLM API → Cache Store → Response
```

### RAG Architecture
```
Documents → Embeddings → Vector DB
                            ↓
User Query → Retrieval → Context + Query → LLM → Response
```

### Production Architecture
```
                    ┌──────────-───┐
                    │ Load Balancer│
                    └──────┬───-───┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐       ┌───-─▼───┐       ┌──--──▼──┐
   │ App Pod │       │ App Pod │       │ App Pod │
   └────┬────┘       └───-─┬───┘       └──--──┬──┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
         ┌────▼────┐  ┌────▼────┐  ┌────▼────┐
         │  Cache  │  │Vector DB│  │ LLM API │
         └─────────┘  └─────────┘  └─────────┘
```

## 💰 Cost Considerations

### Token Usage Optimization

| Strategy | Savings | Implementation |
|----------|---------|----------------|
| **Caching** | 30-50% | Cache frequent queries |
| **Prompt optimization** | 20-30% | Shorter, focused prompts |
| **Model selection** | 50-80% | Use smaller models when possible |
| **Batching** | 10-20% | Batch similar requests |

### Model Selection Guide

| Use Case | Recommended Model | Cost Level |
|----------|-------------------|------------|
| Simple Q&A | GPT-3.5 / Claude Instant | $ |
| Complex reasoning | GPT-4 / Claude 3 Opus | $$$ |
| Code generation | GPT-4 / Claude 3 Sonnet | $$ |
| Embeddings | text-embedding-3-small | $ |

### Cost Estimation Formula

```
Monthly Cost = (Input Tokens + Output Tokens) × Price per 1K tokens × Requests per month
```

## 🔒 Security Checklist

- [ ] Store API keys in environment variables or secrets manager
- [ ] Implement rate limiting on your endpoints
- [ ] Validate and sanitize user inputs
- [ ] Add content moderation for user-generated prompts
- [ ] Log requests for audit and debugging
- [ ] Use HTTPS for all API communications
- [ ] Implement proper authentication on your LLM endpoints

## 📚 Resources

### Official Documentation
- [OpenAI API Docs](https://platform.openai.com/docs)
- [AWS Bedrock Docs](https://docs.aws.amazon.com/bedrock/)
- [LangChain Docs](https://python.langchain.com/docs/)

### Recommended Libraries
- `openai` - OpenAI Python SDK
- `boto3` - AWS SDK for Python
- `langchain` - LLM application framework
- `chromadb` - Vector database
- `tiktoken` - Token counting

## 🏭 Industry Examples

### 🏥 Healthcare Telemedicine AI
A complete, production-ready example of integrating LLM into a healthcare telemedicine application.

**[📁 View Healthcare Telemedicine Example](./healthcare-telemedicine/)**

Features:
- 🩺 AI-powered symptom assessment
- 🚨 Intelligent virtual triage system
- 💬 24/7 patient support chatbot
- 📄 Medical document analysis
- 🔒 HIPAA-compliant architecture

```bash
# Quick start
cd healthcare-telemedicine
pip install -r requirements.txt
python backend/app.py
```

---

### 📱 React Native Todo App with AI Chat
A simple, beginner-friendly example showing how to integrate LLM chat into a React Native mobile application.

**[📁 View React Native Todo AI Example](./react-native-todo-ai/)**

Features:
- ✅ Basic Todo CRUD operations
- 💬 AI chat assistant for task help
- 🤖 Natural language task creation ("Add task to buy groceries tomorrow")
- 📱 Clean, production-ready React Native code
- 🔧 Multiple LLM provider options (OpenAI, Bedrock, Backend Proxy)

```bash
# Quick start
cd react-native-todo-ai
npm install
npx expo start
```

**Perfect for learning:**
- How to structure AI services in mobile apps
- Custom hooks for AI interactions (`useAI`)
- Secure API key management with backend proxy
- Caching and error handling patterns

## 🚀 Next Steps

1. **Start Simple**: Begin with direct API integration
2. **Add Context**: Implement RAG for your specific data
3. **Optimize**: Add caching and prompt optimization
4. **Scale**: Move to production architecture
5. **Monitor**: Track costs, latency, and quality

---

**Ready to supercharge your application with AI? Start with the Quick Start examples above! 🎉**

> *"The best way to integrate LLM is to start small, iterate fast, and scale what works."*
