"""
Healthcare ChatGPT Clone - AI Service Tests
Tests for the AI service functionality.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
from datetime import datetime

from backend.services.ai_service import AIService


class TestAIService:
    """Test class for AI service functionality."""

    @pytest.fixture
    def ai_service(self):
        """Create an AI service instance for testing."""
        with patch('backend.services.ai_service.openai'), \
             patch('backend.services.ai_service.boto3'):
            service = AIService()
            service.openai_client = Mock()
            service.bedrock_client = Mock()
            return service

    @pytest.mark.asyncio
    async def test_generate_response_openai(self, ai_service):
        """Test generating response using OpenAI."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "This is a test response"
        
        ai_service.openai_client.ChatCompletion.create.return_value = mock_response
        
        response = await ai_service.generate_response(
            message="What are the symptoms of diabetes?",
            session_id="test-session-123"
        )
        
        assert response["response"] == "This is a test response"
        assert response["model"] == "openai"
        assert response["confidence_score"] > 0
        assert "response_time" in response

    @pytest.mark.asyncio
    async def test_generate_response_bedrock(self, ai_service):
        """Test generating response using AWS Bedrock."""
        # Mock Bedrock response
        mock_response = {
            'body': Mock(read=Mock(return_value=b'{"completion": "This is a Bedrock response"}'))
        }
        
        ai_service.bedrock_client.invoke_model.return_value = mock_response
        
        response = await ai_service.generate_response(
            message="What are the symptoms of diabetes?",
            session_id="test-session-123",
            model="bedrock"
        )
        
        assert response["response"] == "This is a Bedrock response"
        assert response["model"] == "bedrock"
        assert response["confidence_score"] > 0

    @pytest.mark.asyncio
    async def test_generate_response_with_context(self, ai_service):
        """Test generating response with healthcare context."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Context-aware response"
        
        ai_service.openai_client.ChatCompletion.create.return_value = mock_response
        
        context = {
            "patient_age": 45,
            "medical_history": ["hypertension"],
            "department": "cardiology"
        }
        
        response = await ai_service.generate_response(
            message="What should I know about my condition?",
            session_id="test-session-123",
            context=context
        )
        
        assert response["response"] == "Context-aware response"
        # Verify context was used in system prompt
        ai_service.openai_client.ChatCompletion.create.assert_called_once()
        call_args = ai_service.openai_client.ChatCompletion.create.call_args
        messages = call_args[1]["messages"]
        system_message = messages[0]["content"]
        assert "45" in system_message  # Age should be in system prompt

    def test_detect_emergency_true(self, ai_service):
        """Test emergency detection with emergency keywords."""
        emergency_messages = [
            "I'm having chest pain",
            "I think I'm having a heart attack",
            "I can't breathe properly",
            "I'm bleeding severely",
            "I feel like I might overdose"
        ]
        
        for message in emergency_messages:
            assert ai_service.detect_emergency(message) is True

    def test_detect_emergency_false(self, ai_service):
        """Test emergency detection with non-emergency messages."""
        non_emergency_messages = [
            "I have a headache",
            "What are the symptoms of diabetes?",
            "How do I manage my blood pressure?",
            "I need to schedule an appointment"
        ]
        
        for message in non_emergency_messages:
            assert ai_service.detect_emergency(message) is False

    def test_get_emergency_response(self, ai_service):
        """Test emergency response generation."""
        response = ai_service.get_emergency_response()
        
        assert "EMERGENCY" in response
        assert "911" in response
        assert "emergency room" in response
        assert "immediate" in response

    def test_select_best_model_openai_available(self, ai_service):
        """Test model selection when OpenAI is available."""
        ai_service.openai_client = Mock()
        ai_service.bedrock_client = None
        
        model = ai_service._select_best_model()
        assert model == "openai"

    def test_select_best_model_bedrock_available(self, ai_service):
        """Test model selection when only Bedrock is available."""
        ai_service.openai_client = None
        ai_service.bedrock_client = Mock()
        
        model = ai_service._select_best_model()
        assert model == "bedrock"

    def test_select_best_model_no_models(self, ai_service):
        """Test model selection when no models are available."""
        ai_service.openai_client = None
        ai_service.bedrock_client = None
        
        with pytest.raises(RuntimeError, match="No AI models available"):
            ai_service._select_best_model()

    def test_get_healthcare_system_prompt(self, ai_service):
        """Test healthcare system prompt generation."""
        prompt = ai_service._get_healthcare_system_prompt()
        
        assert "healthcare AI assistant" in prompt
        assert "HIPAA" in prompt
        assert "medical information" in prompt
        assert "healthcare professionals" in prompt

    def test_get_healthcare_system_prompt_with_context(self, ai_service):
        """Test healthcare system prompt with context."""
        context = {
            "patient_age": 65,
            "medical_history": ["diabetes", "hypertension"],
            "department": "endocrinology"
        }
        
        prompt = ai_service._get_healthcare_system_prompt(context)
        
        assert "65" in prompt
        assert "diabetes" in prompt
        assert "hypertension" in prompt
        assert "endocrinology" in prompt

    @pytest.mark.asyncio
    async def test_generate_response_error_handling(self, ai_service):
        """Test error handling in response generation."""
        ai_service.openai_client.ChatCompletion.create.side_effect = Exception("API Error")
        
        response = await ai_service.generate_response(
            message="Test message",
            session_id="test-session-123"
        )
        
        assert "technical difficulties" in response["response"]
        assert response["model"] == "error"
        assert response["confidence_score"] == 0.0

    def test_calculate_confidence_score(self, ai_service):
        """Test confidence score calculation."""
        # Test with sources
        response = "This is a detailed response about diabetes management."
        sources = ["source1", "source2"]
        
        score = ai_service._calculate_confidence_score(response, sources)
        assert score > 0.7  # Should be high with sources and detailed response

    def test_calculate_confidence_score_no_sources(self, ai_service):
        """Test confidence score calculation without sources."""
        response = "Short response"
        sources = []
        
        score = ai_service._calculate_confidence_score(response, sources)
        assert 0.5 <= score <= 0.8  # Should be lower without sources

    @pytest.mark.asyncio
    async def test_generate_response_performance(self, ai_service):
        """Test response generation performance."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Performance test response"
        
        ai_service.openai_client.ChatCompletion.create.return_value = mock_response
        
        start_time = datetime.now()
        response = await ai_service.generate_response(
            message="Performance test message",
            session_id="test-session-123"
        )
        end_time = datetime.now()
        
        response_time = (end_time - start_time).total_seconds()
        assert response_time < 5.0  # Should complete within 5 seconds
        assert response["response_time"] > 0

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, ai_service):
        """Test handling of concurrent AI requests."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Concurrent test response"
        
        ai_service.openai_client.ChatCompletion.create.return_value = mock_response
        
        # Create multiple concurrent requests
        tasks = []
        for i in range(5):
            task = ai_service.generate_response(
                message=f"Concurrent message {i}",
                session_id=f"session-{i}"
            )
            tasks.append(task)
        
        # Wait for all requests to complete
        responses = await asyncio.gather(*tasks)
        
        assert len(responses) == 5
        for response in responses:
            assert response["response"] == "Concurrent test response"
            assert response["model"] == "openai"

    def test_initialization_without_api_keys(self):
        """Test AI service initialization without API keys."""
        with patch('backend.services.ai_service.openai'), \
             patch('backend.services.ai_service.boto3'):
            service = AIService()
            # Should not raise an exception
            assert service is not None

    @pytest.mark.asyncio
    async def test_bedrock_error_handling(self, ai_service):
        """Test Bedrock error handling."""
        ai_service.bedrock_client.invoke_model.side_effect = Exception("Bedrock Error")
        
        response = await ai_service.generate_response(
            message="Test message",
            session_id="test-session-123",
            model="bedrock"
        )
        
        assert "technical difficulties" in response["response"]
        assert response["model"] == "error"

    def test_emergency_keywords_comprehensive(self, ai_service):
        """Test comprehensive emergency keyword detection."""
        emergency_cases = [
            ("chest pain", True),
            ("heart attack", True),
            ("stroke symptoms", True),
            ("difficulty breathing", True),
            ("severe bleeding", True),
            ("unconscious patient", True),
            ("suicidal thoughts", True),
            ("drug overdose", True),
            ("severe allergic reaction", True),
            ("epileptic seizure", True),
            ("choking on food", True),
            ("regular headache", False),
            ("mild cough", False),
            ("routine checkup", False),
            ("medication question", False)
        ]
        
        for message, expected in emergency_cases:
            result = ai_service.detect_emergency(message)
            assert result == expected, f"Failed for message: '{message}'"
