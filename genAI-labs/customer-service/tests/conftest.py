"""
Pytest configuration and fixtures
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
import os
import sys

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Configure asyncio for pytest
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_settings():
    """Mock settings for testing"""
    return Mock(
        AWS_REGION="us-east-1",
        BEDROCK_MODEL_ID="anthropic.claude-3-5-sonnet-20241022-v2:0",
        BEDROCK_REGION="us-east-1",
        MONGODB_URL="mongodb://localhost:27017",
        REDIS_URL="redis://localhost:6379",
        S3_BUCKET="test-bucket",
        OPENSEARCH_ENDPOINT="https://test-endpoint.com",
        MAX_TOKENS=2000,
        TEMPERATURE=0.7,
        CONFIDENCE_THRESHOLD=0.8,
        ESCALATION_THRESHOLD=0.6,
        TRANSCRIBE_LANGUAGE="en-US",
        POLLY_VOICE_ID="Joanna",
        POLLY_ENGINE="neural"
    )


@pytest.fixture
def mock_aws_clients():
    """Mock AWS clients for testing"""
    return {
        'bedrock': Mock(),
        'comprehend': Mock(),
        'transcribe': Mock(),
        'polly': Mock(),
        's3': Mock(),
        'dynamodb': Mock(),
        'opensearch': Mock()
    }


@pytest.fixture
def sample_customer_data():
    """Sample customer data for testing"""
    return {
        "customer_id": "test-customer-123",
        "name": "John Doe",
        "email": "john.doe@example.com",
        "tier": "premium",
        "preferences": {
            "language": "en",
            "timezone": "UTC",
            "notifications": True
        },
        "interaction_history": [
            {
                "timestamp": "2024-01-01T10:00:00Z",
                "type": "chat",
                "outcome": "resolved"
            }
        ]
    }


@pytest.fixture
def sample_conversation_data():
    """Sample conversation data for testing"""
    return {
        "customer_id": "test-customer-123",
        "session_id": "test-session-456",
        "messages": [
            {
                "role": "customer",
                "content": "I need help with my account",
                "timestamp": "2024-01-01T10:00:00Z"
            },
            {
                "role": "assistant",
                "content": "I'd be happy to help you with your account. What specific issue are you experiencing?",
                "timestamp": "2024-01-01T10:00:05Z"
            }
        ],
        "status": "active",
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-01T10:00:05Z"
    }


@pytest.fixture
def sample_knowledge_article():
    """Sample knowledge article for testing"""
    return {
        "article_id": "kb-001",
        "title": "How to Reset Your Password",
        "content": "To reset your password, follow these steps...",
        "category": "Account Management",
        "tags": ["password", "reset", "account"],
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def mock_database_service():
    """Mock database service for testing"""
    service = Mock()
    service.connect = AsyncMock()
    service.disconnect = AsyncMock()
    service.save_conversation = AsyncMock(return_value="conversation-id-123")
    service.get_conversation = AsyncMock()
    service.get_conversations = AsyncMock(return_value=[])
    service.get_customer = AsyncMock()
    service.save_customer = AsyncMock(return_value="customer-id-123")
    service.search_knowledge_base = AsyncMock(return_value=[])
    service.save_knowledge_article = AsyncMock(return_value="article-id-123")
    return service


@pytest.fixture
def mock_cache_service():
    """Mock cache service for testing"""
    service = Mock()
    service.connect = AsyncMock()
    service.disconnect = AsyncMock()
    service.get = AsyncMock()
    service.set = AsyncMock(return_value=True)
    service.delete = AsyncMock(return_value=True)
    service.exists = AsyncMock(return_value=False)
    service.get_customer_context = AsyncMock()
    service.cache_customer_context = AsyncMock(return_value=True)
    service.get_conversation_state = AsyncMock()
    service.cache_conversation_state = AsyncMock(return_value=True)
    return service


@pytest.fixture
def mock_ai_service():
    """Mock AI service for testing"""
    service = Mock()
    service.analyze_customer_intent = AsyncMock(return_value={
        "intent": "Technical Support",
        "confidence": 0.95,
        "key_topics": ["login", "password"],
        "urgency": "Medium"
    })
    service.generate_response = AsyncMock(return_value={
        "response_text": "I understand you need help. Let me assist you.",
        "sentiment": {"Sentiment": "NEUTRAL"},
        "entities": [],
        "confidence_score": 0.95,
        "escalation_needed": False,
        "generated_at": "2024-01-01T10:00:00Z"
    })
    service.transcribe_audio = AsyncMock(return_value="Transcribed text")
    service.synthesize_speech = AsyncMock(return_value=b"audio data")
    service.analyze_sentiment = AsyncMock(return_value={
        "sentiment": "POSITIVE",
        "sentiment_scores": {"Positive": 0.8, "Negative": 0.1, "Neutral": 0.1, "Mixed": 0.0},
        "analyzed_at": "2024-01-01T10:00:00Z"
    })
    service.detect_entities = AsyncMock(return_value=[
        {"Text": "John Doe", "Type": "PERSON", "Score": 0.95}
    ])
    service.search_knowledge_base = AsyncMock(return_value={
        "query": "test query",
        "results": [{"title": "Test Article", "content": "Test content"}],
        "total_results": 1,
        "search_time": 0.1
    })
    return service


# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )


# Test data fixtures
@pytest.fixture
def test_intents():
    """Common test intents"""
    return [
        "General Inquiry",
        "Technical Support",
        "Billing Question",
        "Complaint",
        "Product Information",
        "Order Status",
        "Account Management",
        "Refund/Return",
        "Escalation Request"
    ]


@pytest.fixture
def test_sentiments():
    """Common test sentiments"""
    return [
        "POSITIVE",
        "NEGATIVE",
        "NEUTRAL",
        "MIXED"
    ]


@pytest.fixture
def test_entities():
    """Common test entities"""
    return [
        {"Text": "John Doe", "Type": "PERSON", "Score": 0.95},
        {"Text": "john@example.com", "Type": "EMAIL", "Score": 0.98},
        {"Text": "123-456-7890", "Type": "PHONE", "Score": 0.92},
        {"Text": "New York", "Type": "LOCATION", "Score": 0.88}
    ]
