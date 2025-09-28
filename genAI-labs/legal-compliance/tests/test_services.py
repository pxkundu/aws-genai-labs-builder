"""
Service layer tests for Legal Compliance AI Platform
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.services.llm_service import LLMService
from backend.services.legal_service import LegalService
from backend.models.legal_question import Jurisdiction, PracticeArea, QuestionComplexity


class TestLLMService:
    """Test LLM service functionality"""
    
    @pytest.fixture
    def llm_service(self):
        """Create LLM service instance for testing"""
        service = LLMService()
        # Mock the API clients to avoid actual API calls
        service.openai_client = AsyncMock()
        service.anthropic_client = AsyncMock()
        service.google_model = AsyncMock()
        return service
    
    @pytest.mark.asyncio
    async def test_get_legal_response_success(self, llm_service):
        """Test successful legal response generation"""
        # Mock OpenAI response
        mock_openai_response = MagicMock()
        mock_openai_response.choices = [MagicMock()]
        mock_openai_response.choices[0].message.content = "OpenAI legal response"
        mock_openai_response.usage.total_tokens = 100
        llm_service.openai_client.chat.completions.create.return_value = mock_openai_response
        
        # Mock Anthropic response
        mock_anthropic_response = MagicMock()
        mock_anthropic_response.content = [MagicMock()]
        mock_anthropic_response.content[0].text = "Anthropic legal response"
        mock_anthropic_response.usage.input_tokens = 50
        mock_anthropic_response.usage.output_tokens = 50
        llm_service.anthropic_client.messages.create.return_value = mock_anthropic_response
        
        # Mock Google response
        mock_google_response = MagicMock()
        mock_google_response.text = "Google legal response"
        llm_service.google_model.generate_content_async.return_value = mock_google_response
        
        # Test
        result = await llm_service.get_legal_response(
            question="What is a contract?",
            jurisdiction="US",
            practice_area="contract",
            models=["gpt-4-turbo-preview", "claude-3-5-sonnet-20241022", "gemini-pro"]
        )
        
        # Assertions
        assert len(result) == 3
        assert "gpt-4-turbo-preview" in result
        assert "claude-3-5-sonnet-20241022" in result
        assert "gemini-pro" in result
        
        # Check response structure
        gpt_response = result["gpt-4-turbo-preview"]
        assert gpt_response.model == "gpt-4-turbo-preview"
        assert gpt_response.response == "OpenAI legal response"
        assert gpt_response.tokens_used == 100
        assert gpt_response.confidence == 0.9
    
    @pytest.mark.asyncio
    async def test_get_legal_response_with_error(self, llm_service):
        """Test legal response generation with API error"""
        # Mock OpenAI to raise an error
        llm_service.openai_client.chat.completions.create.side_effect = Exception("API Error")
        
        # Mock other services to work normally
        mock_anthropic_response = MagicMock()
        mock_anthropic_response.content = [MagicMock()]
        mock_anthropic_response.content[0].text = "Anthropic legal response"
        mock_anthropic_response.usage.input_tokens = 50
        mock_anthropic_response.usage.output_tokens = 50
        llm_service.anthropic_client.messages.create.return_value = mock_anthropic_response
        
        # Test
        result = await llm_service.get_legal_response(
            question="What is a contract?",
            jurisdiction="US",
            practice_area="contract",
            models=["gpt-4-turbo-preview", "claude-3-5-sonnet-20241022"]
        )
        
        # Assertions
        assert len(result) == 2
        
        # Check that error is handled gracefully
        gpt_response = result["gpt-4-turbo-preview"]
        assert "Error" in gpt_response.response
        assert gpt_response.confidence == 0.0
        assert gpt_response.error is not None
        
        # Check that other models still work
        claude_response = result["claude-3-5-sonnet-20241022"]
        assert claude_response.response == "Anthropic legal response"
        assert claude_response.confidence == 0.9
    
    @pytest.mark.asyncio
    async def test_compare_responses(self, llm_service):
        """Test response comparison functionality"""
        # Mock responses
        responses = {
            "gpt-4-turbo-preview": MagicMock(),
            "claude-3-5-sonnet-20241022": MagicMock(),
            "gemini-pro": MagicMock()
        }
        
        # Set response texts
        responses["gpt-4-turbo-preview"].response = "This is about contract law and legal requirements for formation."
        responses["claude-3-5-sonnet-20241022"].response = "Contract law involves legal principles and formation requirements."
        responses["gemini-pro"].response = "Legal contracts require specific elements for validity and enforcement."
        
        # Test comparison
        result = await llm_service.compare_responses(responses)
        
        # Assertions
        assert "consensus_analysis" in result
        assert "key_differences" in result
        assert "quality_ranking" in result
        assert "summary" in result
        
        consensus = result["consensus_analysis"]
        assert "consensus_score" in consensus
        assert "consensus_level" in consensus
        assert "common_themes" in consensus
    
    def test_get_legal_system_prompt(self, llm_service):
        """Test legal system prompt generation"""
        # Test US jurisdiction
        prompt = llm_service._get_legal_system_prompt("US", "contract")
        assert "United States federal and state law" in prompt
        assert "contract law" in prompt
        
        # Test EU jurisdiction
        prompt = llm_service._get_legal_system_prompt("EU", "employment")
        assert "European Union law" in prompt
        assert "employment law" in prompt
        
        # Test with general practice area
        prompt = llm_service._get_legal_system_prompt("UK", "general")
        assert "English and Welsh law" in prompt
        assert "general legal principles" in prompt
    
    def test_classify_question_type(self, llm_service):
        """Test question type classification"""
        # Test contract question
        question_type = llm_service._classify_question_type("What are the elements of a valid contract?")
        assert question_type == "contract_law"
        
        # Test tort question
        question_type = llm_service._classify_question_type("How do I prove negligence in a personal injury case?")
        assert question_type == "tort_law"
        
        # Test criminal question
        question_type = llm_service._classify_question_type("What are the penalties for criminal fraud?")
        assert question_type == "criminal_law"
        
        # Test general question
        question_type = llm_service._classify_question_type("What is the legal system?")
        assert question_type == "general_legal"
    
    def test_assess_question_complexity(self, llm_service):
        """Test question complexity assessment"""
        # Test low complexity
        complexity = llm_service._assess_question_complexity("What is a contract?")
        assert complexity == "low"
        
        # Test medium complexity
        complexity = llm_service._assess_question_complexity("What are the requirements for a valid contract and what happens if one party breaches it?")
        assert complexity == "medium"
        
        # Test high complexity
        complexity = llm_service._assess_question_complexity("In a complex multi-jurisdictional merger involving intellectual property assets and regulatory compliance requirements, what are the key legal considerations for due diligence and how do employment law obligations transfer between entities?")
        assert complexity == "high"


class TestLegalService:
    """Test legal service functionality"""
    
    @pytest.fixture
    def legal_service(self):
        """Create legal service instance for testing"""
        return LegalService()
    
    @pytest.mark.asyncio
    async def test_assess_question_complexity(self, legal_service):
        """Test question complexity assessment"""
        # Test low complexity
        complexity = await legal_service.assess_question_complexity(
            "What is a contract?", Jurisdiction.US, PracticeArea.CONTRACT
        )
        assert complexity == QuestionComplexity.LOW
        
        # Test medium complexity
        complexity = await legal_service.assess_question_complexity(
            "What are the requirements for a valid contract and what are the consequences of breach?",
            Jurisdiction.US, PracticeArea.CONTRACT
        )
        assert complexity == QuestionComplexity.MEDIUM
        
        # Test high complexity
        complexity = await legal_service.assess_question_complexity(
            "In a complex multi-jurisdictional merger involving intellectual property assets, regulatory compliance requirements, and employment law considerations, what are the key legal issues for due diligence and how do various legal obligations transfer between entities?",
            Jurisdiction.US, PracticeArea.CORPORATE
        )
        assert complexity == QuestionComplexity.HIGH
    
    @pytest.mark.asyncio
    async def test_determine_recommended_model(self, legal_service):
        """Test model recommendation logic"""
        # Mock responses
        responses = {
            "gpt-4-turbo-preview": MagicMock(),
            "claude-3-5-sonnet-20241022": MagicMock(),
            "gemini-pro": MagicMock()
        }
        
        # Set response characteristics
        responses["gpt-4-turbo-preview"].response = "A" * 1000  # Long response
        responses["gpt-4-turbo-preview"].confidence = 0.95
        responses["gpt-4-turbo-preview"].processing_time = 2.0
        responses["gpt-4-turbo-preview"].error = None
        
        responses["claude-3-5-sonnet-20241022"].response = "A" * 500  # Medium response
        responses["claude-3-5-sonnet-20241022"].confidence = 0.90
        responses["claude-3-5-sonnet-20241022"].processing_time = 3.0
        responses["claude-3-5-sonnet-20241022"].error = None
        
        responses["gemini-pro"].response = "A" * 200  # Short response
        responses["gemini-pro"].confidence = 0.85
        responses["gemini-pro"].processing_time = 4.0
        responses["gemini-pro"].error = None
        
        # Test recommendation
        recommended = await legal_service.determine_recommended_model(responses)
        assert recommended == "gpt-4-turbo-preview"  # Should recommend GPT-4 for best quality
    
    @pytest.mark.asyncio
    async def test_assess_confidence_level(self, legal_service):
        """Test confidence level assessment"""
        # Mock high confidence responses
        responses = {
            "gpt-4-turbo-preview": MagicMock(),
            "claude-3-5-sonnet-20241022": MagicMock()
        }
        responses["gpt-4-turbo-preview"].confidence = 0.95
        responses["gpt-4-turbo-preview"].error = None
        responses["claude-3-5-sonnet-20241022"].confidence = 0.90
        responses["claude-3-5-sonnet-20241022"].error = None
        
        confidence = await legal_service.assess_confidence_level(responses)
        assert confidence == "high"
        
        # Mock medium confidence responses
        responses["gpt-4-turbo-preview"].confidence = 0.70
        responses["claude-3-5-sonnet-20241022"].confidence = 0.65
        
        confidence = await legal_service.assess_confidence_level(responses)
        assert confidence == "medium"
        
        # Mock low confidence responses
        responses["gpt-4-turbo-preview"].confidence = 0.50
        responses["claude-3-5-sonnet-20241022"].confidence = 0.45
        
        confidence = await legal_service.assess_confidence_level(responses)
        assert confidence == "low"
    
    @pytest.mark.asyncio
    async def test_generate_follow_up_suggestions(self, legal_service):
        """Test follow-up suggestion generation"""
        # Test contract law suggestions
        suggestions = await legal_service.generate_follow_up_suggestions(
            "What are the requirements for a valid contract?",
            Jurisdiction.US,
            PracticeArea.CONTRACT
        )
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        assert all(isinstance(s, str) for s in suggestions)
        
        # Test employment law suggestions
        suggestions = await legal_service.generate_follow_up_suggestions(
            "How do I handle workplace discrimination?",
            Jurisdiction.US,
            PracticeArea.EMPLOYMENT
        )
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
    
    @pytest.mark.asyncio
    async def test_get_question_history(self, legal_service):
        """Test question history retrieval"""
        # Mock database session
        mock_db = MagicMock()
        
        # Test without filters
        history = await legal_service.get_question_history(
            limit=10,
            offset=0,
            db=mock_db
        )
        
        assert isinstance(history, list)
        # Should return mock data from the service
    
    @pytest.mark.asyncio
    async def test_get_platform_statistics(self, legal_service):
        """Test platform statistics retrieval"""
        # Mock database session
        mock_db = MagicMock()
        
        stats = await legal_service.get_platform_statistics(mock_db)
        
        assert isinstance(stats, dict)
        assert "total_questions" in stats
        assert "questions_today" in stats
        assert "average_response_time" in stats
        assert "most_common_jurisdiction" in stats
        assert "most_common_practice_area" in stats
    
    @pytest.mark.asyncio
    async def test_validate_legal_question(self, legal_service):
        """Test legal question validation"""
        # Test valid question
        result = await legal_service.validate_legal_question(
            "What are the requirements for a valid contract under US law?",
            Jurisdiction.US,
            PracticeArea.CONTRACT
        )
        
        assert result["is_valid"] == True
        assert len(result["warnings"]) == 0
        
        # Test invalid question (too short)
        result = await legal_service.validate_legal_question(
            "What?",
            Jurisdiction.US,
            PracticeArea.CONTRACT
        )
        
        assert result["is_valid"] == False
        assert len(result["warnings"]) > 0
        
        # Test question without legal terms
        result = await legal_service.validate_legal_question(
            "How do I cook pasta?",
            Jurisdiction.US,
            PracticeArea.GENERAL
        )
        
        assert result["is_valid"] == True  # Should still be valid
        assert len(result["suggestions"]) > 0  # Should have suggestions


class TestServiceIntegration:
    """Test integration between services"""
    
    @pytest.mark.asyncio
    async def test_llm_and_legal_service_integration(self):
        """Test integration between LLM and Legal services"""
        # This would test how the services work together
        # In a real implementation, you might test the full flow
        
        llm_service = LLMService()
        legal_service = LegalService()
        
        # Mock the LLM service
        llm_service.openai_client = AsyncMock()
        llm_service.anthropic_client = AsyncMock()
        llm_service.google_model = AsyncMock()
        
        # Test the full workflow
        question = "What are the requirements for a valid contract?"
        
        # Assess complexity
        complexity = await legal_service.assess_question_complexity(
            question, Jurisdiction.US, PracticeArea.CONTRACT
        )
        assert complexity in [QuestionComplexity.LOW, QuestionComplexity.MEDIUM, QuestionComplexity.HIGH]
        
        # Generate follow-up suggestions
        suggestions = await legal_service.generate_follow_up_suggestions(
            question, Jurisdiction.US, PracticeArea.CONTRACT
        )
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0


class TestErrorHandling:
    """Test error handling in services"""
    
    @pytest.mark.asyncio
    async def test_llm_service_error_handling(self):
        """Test LLM service error handling"""
        llm_service = LLMService()
        
        # Mock all clients to raise errors
        llm_service.openai_client = AsyncMock()
        llm_service.openai_client.chat.completions.create.side_effect = Exception("OpenAI API Error")
        
        llm_service.anthropic_client = AsyncMock()
        llm_service.anthropic_client.messages.create.side_effect = Exception("Anthropic API Error")
        
        llm_service.google_model = AsyncMock()
        llm_service.google_model.generate_content_async.side_effect = Exception("Google API Error")
        
        # Test that errors are handled gracefully
        result = await llm_service.get_legal_response(
            question="What is a contract?",
            jurisdiction="US",
            practice_area="contract"
        )
        
        # All responses should have errors
        for model, response in result.items():
            assert "Error" in response.response
            assert response.confidence == 0.0
            assert response.error is not None
    
    @pytest.mark.asyncio
    async def test_legal_service_error_handling(self):
        """Test legal service error handling"""
        legal_service = LegalService()
        
        # Test with invalid inputs
        try:
            await legal_service.assess_question_complexity("", Jurisdiction.US, PracticeArea.CONTRACT)
        except Exception:
            # Should handle empty question gracefully
            pass
        
        # Test with None inputs
        try:
            await legal_service.determine_recommended_model({})
        except Exception:
            # Should handle empty responses gracefully
            pass
