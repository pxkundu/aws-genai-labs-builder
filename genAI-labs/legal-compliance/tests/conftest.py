"""
Test configuration and fixtures for Legal Compliance AI Platform
"""

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.main import app
from backend.core.database import Base, get_db
from backend.core.config import TestingSettings
from backend.services.llm_service import LLMService
from backend.services.legal_service import LegalService


# Test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create test database engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings():
    """Get test settings"""
    return TestingSettings()


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database session"""
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def mock_llm_service():
    """Mock LLM service for testing"""
    
    class MockLLMService:
        def __init__(self):
            self.responses = {
                "gpt-4-turbo-preview": {
                    "model": "gpt-4-turbo-preview",
                    "response": "This is a mock response from GPT-4 for testing purposes.",
                    "confidence": 0.95,
                    "tokens_used": 100,
                    "processing_time": 1.5,
                    "timestamp": "2024-01-15T10:30:00Z"
                },
                "claude-3-5-sonnet-20241022": {
                    "model": "claude-3-5-sonnet-20241022",
                    "response": "This is a mock response from Claude 3.5 for testing purposes.",
                    "confidence": 0.92,
                    "tokens_used": 95,
                    "processing_time": 1.8,
                    "timestamp": "2024-01-15T10:30:00Z"
                },
                "gemini-pro": {
                    "model": "gemini-pro",
                    "response": "This is a mock response from Gemini Pro for testing purposes.",
                    "confidence": 0.90,
                    "tokens_used": 105,
                    "processing_time": 2.0,
                    "timestamp": "2024-01-15T10:30:00Z"
                }
            }
        
        async def get_legal_response(self, question, jurisdiction="US", practice_area="general", models=None):
            """Mock legal response generation"""
            if models is None:
                models = list(self.responses.keys())
            
            result = {}
            for model in models:
                if model in self.responses:
                    result[model] = self.responses[model]
            
            return result
        
        async def compare_responses(self, responses):
            """Mock response comparison"""
            return {
                "consensus_analysis": {
                    "consensus_score": 85.5,
                    "consensus_level": "high",
                    "common_themes": ["contract formation", "legal requirements"]
                },
                "key_differences": [],
                "quality_ranking": [
                    {
                        "model": "gpt-4-turbo-preview",
                        "quality_score": 9.5,
                        "ranking_factors": {
                            "length": 100,
                            "processing_time": 1.5,
                            "tokens_used": 100,
                            "has_error": False
                        }
                    }
                ],
                "summary": "High consensus among responses"
            }
    
    return MockLLMService()


@pytest_asyncio.fixture
async def mock_legal_service():
    """Mock legal service for testing"""
    
    class MockLegalService:
        def __init__(self):
            pass
        
        async def assess_question_complexity(self, question, jurisdiction, practice_area):
            """Mock complexity assessment"""
            if len(question.split()) > 50:
                return "high"
            elif len(question.split()) > 20:
                return "medium"
            else:
                return "low"
        
        async def determine_recommended_model(self, responses, comparison=None):
            """Mock model recommendation"""
            return "gpt-4-turbo-preview"
        
        async def assess_confidence_level(self, responses, comparison=None):
            """Mock confidence assessment"""
            return "high"
        
        async def generate_follow_up_suggestions(self, question, jurisdiction, practice_area):
            """Mock follow-up suggestions"""
            return [
                "What are the key elements of contract formation?",
                "How can I ensure my contract is legally binding?",
                "What are common contract pitfalls to avoid?"
            ]
    
    return MockLegalService()


@pytest.fixture
def sample_legal_question():
    """Sample legal question for testing"""
    return {
        "question": "What are the requirements for a valid contract under US law?",
        "jurisdiction": "US",
        "practice_area": "contract",
        "context": "This is for a business partnership agreement",
        "models": ["gpt-4-turbo-preview", "claude-3-5-sonnet-20241022"],
        "include_comparison": True
    }


@pytest.fixture
def sample_legal_response():
    """Sample legal response for testing"""
    return {
        "question_id": "q_20240115_103000_abc123",
        "question": "What are the requirements for a valid contract under US law?",
        "jurisdiction": "US",
        "practice_area": "contract",
        "complexity": "medium",
        "responses": {
            "gpt-4-turbo-preview": {
                "model": "gpt-4-turbo-preview",
                "response": "Under US contract law, a valid contract requires four essential elements: offer, acceptance, consideration, and mutual assent. Additionally, the parties must have legal capacity and the contract must be for a legal purpose.",
                "confidence": 0.95,
                "tokens_used": 1250,
                "processing_time": 3.2,
                "timestamp": "2024-01-15T10:30:00Z"
            },
            "claude-3-5-sonnet-20241022": {
                "model": "claude-3-5-sonnet-20241022",
                "response": "A valid contract under US law typically requires: 1) An offer by one party, 2) Acceptance of that offer by another party, 3) Consideration (something of value exchanged), and 4) Mutual intent to be bound. The parties must also have legal capacity and the subject matter must be legal.",
                "confidence": 0.92,
                "tokens_used": 1180,
                "processing_time": 2.8,
                "timestamp": "2024-01-15T10:30:00Z"
            }
        },
        "comparison": {
            "consensus_analysis": {
                "consensus_score": 88.5,
                "consensus_level": "high",
                "common_themes": ["contract formation", "legal requirements", "essential elements"]
            },
            "key_differences": [],
            "quality_ranking": [
                {
                    "model": "gpt-4-turbo-preview",
                    "quality_score": 9.2,
                    "ranking_factors": {
                        "length": 1250,
                        "processing_time": 3.2,
                        "tokens_used": 1250,
                        "has_error": False
                    }
                }
            ],
            "summary": "High consensus among responses. Both models identify the four essential elements of contract formation."
        },
        "timestamp": "2024-01-15T10:30:05Z",
        "processing_time": 5.1,
        "cached": False,
        "recommended_model": "gpt-4-turbo-preview",
        "confidence_level": "high",
        "follow_up_suggestions": [
            "What happens if one party breaches the contract?",
            "How can I ensure my contract is enforceable?",
            "What are common contract pitfalls to avoid?"
        ]
    }


@pytest.fixture
def sample_question_history():
    """Sample question history for testing"""
    return [
        {
            "question_id": "q_20240115_103000_abc123",
            "question": "What are the requirements for a valid contract?",
            "jurisdiction": "US",
            "practice_area": "contract",
            "timestamp": "2024-01-15T10:30:00Z",
            "response_count": 3,
            "recommended_model": "gpt-4-turbo-preview",
            "confidence_level": "high"
        },
        {
            "question_id": "q_20240115_102000_def456",
            "question": "How do I handle workplace harassment?",
            "jurisdiction": "US",
            "practice_area": "employment",
            "timestamp": "2024-01-15T10:20:00Z",
            "response_count": 3,
            "recommended_model": "claude-3-5-sonnet-20241022",
            "confidence_level": "medium"
        }
    ]


@pytest.fixture
def mock_cache():
    """Mock cache for testing"""
    
    class MockCache:
        def __init__(self):
            self._cache = {}
        
        async def get(self, key):
            return self._cache.get(key)
        
        async def set(self, key, value, ttl=None):
            self._cache[key] = value
            return True
        
        async def delete(self, key):
            if key in self._cache:
                del self._cache[key]
            return True
        
        async def exists(self, key):
            return key in self._cache
    
    return MockCache()


# Test data fixtures
@pytest.fixture
def test_jurisdictions():
    """Test jurisdictions data"""
    return [
        {"code": "US", "name": "United States", "description": "United States federal and state law"},
        {"code": "UK", "name": "United Kingdom", "description": "United Kingdom law (England and Wales)"},
        {"code": "EU", "name": "European Union", "description": "European Union law and regulations"},
        {"code": "DE", "name": "Germany", "description": "German civil law system"},
        {"code": "FR", "name": "France", "description": "French civil law system"}
    ]


@pytest.fixture
def test_practice_areas():
    """Test practice areas data"""
    return [
        {"code": "general", "name": "General Law", "description": "General legal principles and procedures"},
        {"code": "contract", "name": "Contract Law", "description": "Contract law, formation, performance, and remedies"},
        {"code": "tort", "name": "Tort Law", "description": "Tort law, negligence, and civil liability"},
        {"code": "criminal", "name": "Criminal Law", "description": "Criminal law and procedure"},
        {"code": "corporate", "name": "Corporate Law", "description": "Corporate law, business entities, and governance"}
    ]


@pytest.fixture
def test_models():
    """Test LLM models data"""
    return [
        {
            "name": "gpt-4-turbo-preview",
            "provider": "OpenAI",
            "description": "Most advanced OpenAI model",
            "max_tokens": 4000,
            "temperature": 0.1
        },
        {
            "name": "claude-3-5-sonnet-20241022",
            "provider": "Anthropic",
            "description": "Anthropic's latest model",
            "max_tokens": 4000,
            "temperature": 0.1
        },
        {
            "name": "gemini-pro",
            "provider": "Google",
            "description": "Google's advanced model",
            "max_tokens": 4000,
            "temperature": 0.1
        }
    ]


# Async test utilities
@pytest.fixture
def async_client():
    """Async test client"""
    return TestClient(app)


@pytest.fixture
def event_loop_policy():
    """Event loop policy for async tests"""
    import asyncio
    policy = asyncio.get_event_loop_policy()
    return policy
