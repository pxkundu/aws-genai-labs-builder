"""
Healthcare ChatGPT Clone - Test Configuration
This module provides shared test fixtures and configuration.
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock

from backend.main import app
from backend.models.chat import Base
from backend.services.database import get_db
from backend.services.cache import get_cache
from backend.services.ai_service import AIService
from backend.services.chat_service import ChatService
from backend.services.knowledge_service import KnowledgeService
from backend.services.analytics_service import AnalyticsService


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a test database session."""
    # Create tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop tables
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def mock_cache() -> Mock:
    """Create a mock cache service."""
    cache = Mock()
    cache.get_cache = AsyncMock(return_value=None)
    cache.set_cache = AsyncMock(return_value=True)
    cache.delete_cache = AsyncMock(return_value=True)
    cache.exists_cache = AsyncMock(return_value=False)
    return cache


@pytest.fixture(scope="function")
def mock_ai_service() -> Mock:
    """Create a mock AI service."""
    ai_service = Mock(spec=AIService)
    ai_service.generate_response = AsyncMock(return_value={
        "response": "This is a test response",
        "model": "test-model",
        "response_time": 0.5,
        "confidence_score": 0.9,
        "sources": [],
        "timestamp": 1234567890
    })
    ai_service.detect_emergency = Mock(return_value=False)
    ai_service.get_emergency_response = Mock(return_value="Emergency response")
    return ai_service


@pytest.fixture(scope="function")
def chat_service(db_session: Session) -> ChatService:
    """Create a chat service instance."""
    return ChatService(db_session)


@pytest.fixture(scope="function")
def knowledge_service(db_session: Session) -> KnowledgeService:
    """Create a knowledge service instance."""
    return KnowledgeService(db_session)


@pytest.fixture(scope="function")
def analytics_service(db_session: Session) -> AnalyticsService:
    """Create an analytics service instance."""
    return AnalyticsService(db_session)


@pytest.fixture(scope="function")
def sample_chat_session():
    """Create a sample chat session for testing."""
    return {
        "session_id": "test-session-123",
        "user_id": "test-user-456",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture(scope="function")
def sample_chat_message():
    """Create a sample chat message for testing."""
    return {
        "message_id": "test-message-789",
        "session_id": "test-session-123",
        "message": "What are the symptoms of diabetes?",
        "message_type": "user",
        "created_at": "2024-01-01T00:00:00Z",
        "metadata": {}
    }


@pytest.fixture(scope="function")
def sample_knowledge_item():
    """Create a sample knowledge base item for testing."""
    return {
        "id": "test-knowledge-123",
        "title": "Diabetes Management",
        "content": "Diabetes is a chronic condition that affects how your body processes blood sugar...",
        "category": "medical_guidelines",
        "source": "medical_guidelines/diabetes-management.md",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "tags": ["diabetes", "chronic", "blood sugar"],
        "is_active": "true"
    }


@pytest.fixture(scope="function")
def sample_healthcare_data():
    """Create sample healthcare data for testing."""
    return {
        "age": 45,
        "medical_record_number": "MRN123456",
        "department": "cardiology",
        "medical_history": ["hypertension", "diabetes"],
        "allergies": ["penicillin"],
        "medications": ["metformin", "lisinopril"]
    }


@pytest.fixture(scope="function")
def mock_s3_client():
    """Create a mock S3 client for testing."""
    s3_client = Mock()
    s3_client.list_objects_v2 = Mock(return_value={
        'Contents': [
            {
                'Key': 'medical_guidelines/diabetes-management.md',
                'Size': 1024,
                'LastModified': '2024-01-01T00:00:00Z'
            }
        ]
    })
    s3_client.get_object = Mock(return_value={
        'Body': Mock(read=Mock(return_value=b'# Diabetes Management\n\nDiabetes is a chronic condition...'))
    })
    return s3_client


@pytest.fixture(scope="function")
def mock_openai_client():
    """Create a mock OpenAI client for testing."""
    openai_client = Mock()
    openai_client.ChatCompletion.create = Mock(return_value={
        'choices': [
            {
                'message': {
                    'content': 'This is a test response from OpenAI'
                }
            }
        ]
    })
    return openai_client


@pytest.fixture(scope="function")
def mock_bedrock_client():
    """Create a mock Bedrock client for testing."""
    bedrock_client = Mock()
    bedrock_client.invoke_model = Mock(return_value={
        'body': Mock(read=Mock(return_value=b'{"completion": "This is a test response from Bedrock"}'))
    })
    return bedrock_client


# Test data fixtures
@pytest.fixture(scope="function")
def test_messages():
    """Create test messages for chat testing."""
    return [
        {
            "message_id": "msg-1",
            "session_id": "session-1",
            "message": "Hello, I have a question about diabetes",
            "message_type": "user",
            "created_at": "2024-01-01T00:00:00Z",
            "metadata": {}
        },
        {
            "message_id": "msg-2",
            "session_id": "session-1",
            "message": "I'd be happy to help you with questions about diabetes. What specific information are you looking for?",
            "message_type": "assistant",
            "created_at": "2024-01-01T00:01:00Z",
            "metadata": {
                "model": "openai",
                "confidence_score": 0.9
            }
        }
    ]


@pytest.fixture(scope="function")
def test_knowledge_items():
    """Create test knowledge items for knowledge base testing."""
    return [
        {
            "id": "kb-1",
            "title": "Diabetes Management",
            "content": "Diabetes is a chronic condition...",
            "category": "medical_guidelines",
            "source": "medical_guidelines/diabetes-management.md",
            "tags": ["diabetes", "chronic"],
            "is_active": "true"
        },
        {
            "id": "kb-2",
            "title": "Common Symptoms",
            "content": "Common symptoms include...",
            "category": "symptoms",
            "source": "symptoms/common-symptoms.md",
            "tags": ["symptoms", "common"],
            "is_active": "true"
        }
    ]


# Async test fixtures
@pytest.fixture(scope="function")
async def async_db_session() -> AsyncGenerator[Session, None]:
    """Create an async test database session."""
    # This would be used for async database operations
    # For now, we'll use the sync version
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


# Performance test fixtures
@pytest.fixture(scope="function")
def performance_test_data():
    """Create data for performance testing."""
    return {
        "large_message": "x" * 10000,  # 10KB message
        "many_messages": [{"message": f"Test message {i}"} for i in range(1000)],
        "complex_query": "What are the symptoms, causes, treatments, and complications of type 2 diabetes mellitus in elderly patients with cardiovascular disease?"
    }


# Integration test fixtures
@pytest.fixture(scope="function")
def integration_test_config():
    """Configuration for integration tests."""
    return {
        "api_base_url": "http://localhost:8000",
        "test_timeout": 30,
        "retry_attempts": 3,
        "test_user_id": "integration-test-user",
        "test_session_id": "integration-test-session"
    }
