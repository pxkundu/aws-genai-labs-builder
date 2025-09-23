"""
Tests for AI Service
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from services.ai_service import AIService


class TestAIService:
    """Test cases for AI Service"""
    
    @pytest.fixture
    def ai_service(self):
        """Create AI service instance for testing"""
        with patch('services.ai_service.boto3.client') as mock_boto:
            mock_bedrock = Mock()
            mock_comprehend = Mock()
            mock_transcribe = Mock()
            mock_polly = Mock()
            
            mock_boto.side_effect = [mock_bedrock, mock_comprehend, mock_transcribe, mock_polly]
            
            service = AIService()
            service.bedrock = mock_bedrock
            service.comprehend = mock_comprehend
            service.transcribe = mock_transcribe
            service.polly = mock_polly
            
            return service
    
    @pytest.mark.asyncio
    async def test_analyze_customer_intent_success(self, ai_service):
        """Test successful intent analysis"""
        # Mock response
        mock_response = {
            'body': Mock()
        }
        mock_response['body'].read.return_value = json.dumps({
            'content': [{'text': json.dumps({
                'intent': 'Technical Support',
                'confidence': 0.95,
                'key_topics': ['login', 'password'],
                'urgency': 'Medium',
                'required_information': ['account_id'],
                'suggested_response_approach': 'Provide step-by-step guidance'
            })}]
        }).encode()
        
        ai_service.bedrock.invoke_model.return_value = mock_response
        
        # Test data
        message = "I can't log into my account"
        customer_context = {"customer_id": "123", "tier": "premium"}
        
        # Execute
        result = await ai_service.analyze_customer_intent(message, customer_context)
        
        # Assertions
        assert result['intent'] == 'Technical Support'
        assert result['confidence'] == 0.95
        assert 'login' in result['key_topics']
        assert result['urgency'] == 'Medium'
        
        # Verify Bedrock was called
        ai_service.bedrock.invoke_model.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_analyze_customer_intent_failure(self, ai_service):
        """Test intent analysis failure"""
        # Mock error
        ai_service.bedrock.invoke_model.side_effect = Exception("Bedrock error")
        
        # Test data
        message = "I need help"
        customer_context = {"customer_id": "123"}
        
        # Execute and assert
        with pytest.raises(Exception) as exc_info:
            await ai_service.analyze_customer_intent(message, customer_context)
        
        assert "Intent analysis failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_generate_response_success(self, ai_service):
        """Test successful response generation"""
        # Mock Bedrock response
        mock_bedrock_response = {
            'body': Mock()
        }
        mock_bedrock_response['body'].read.return_value = json.dumps({
            'content': [{'text': 'I understand you need help with your account. Let me assist you with that.'}]
        }).encode()
        
        # Mock Comprehend responses
        mock_sentiment = {
            'Sentiment': 'NEUTRAL',
            'SentimentScore': {'Positive': 0.3, 'Negative': 0.1, 'Neutral': 0.6, 'Mixed': 0.0}
        }
        
        mock_entities = {
            'Entities': [
                {'Text': 'account', 'Type': 'OTHER', 'Score': 0.8}
            ]
        }
        
        ai_service.bedrock.invoke_model.return_value = mock_bedrock_response
        ai_service.comprehend.detect_sentiment.return_value = mock_sentiment
        ai_service.comprehend.detect_entities.return_value = mock_entities
        
        # Test data
        message = "I need help with my account"
        intent_analysis = {'intent': 'Account Help', 'confidence': 0.9}
        customer_context = {"customer_id": "123"}
        
        # Execute
        result = await ai_service.generate_response(message, intent_analysis, customer_context)
        
        # Assertions
        assert 'response_text' in result
        assert result['sentiment']['Sentiment'] == 'NEUTRAL'
        assert len(result['entities']) == 1
        assert result['confidence_score'] == 0.9
        assert 'generated_at' in result
        
        # Verify services were called
        ai_service.comprehend.detect_sentiment.assert_called_once()
        ai_service.comprehend.detect_entities.assert_called_once()
        ai_service.bedrock.invoke_model.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_transcribe_audio_success(self, ai_service):
        """Test successful audio transcription"""
        # Mock transcription response
        mock_transcription_result = {
            'Transcript': {'TranscriptText': 'Hello, I need help with my order'}
        }
        
        ai_service.transcribe.start_transcription_job.return_value = {'TranscriptionJobName': 'test-job'}
        
        # Mock the wait_for_transcription_completion method
        with patch.object(ai_service, 'wait_for_transcription_completion', return_value=mock_transcription_result):
            # Test data
            audio_data = b"fake audio data"
            
            # Execute
            result = await ai_service.transcribe_audio(audio_data)
            
            # Assertions
            assert result == "Hello, I need help with my order"
            ai_service.transcribe.start_transcription_job.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_synthesize_speech_success(self, ai_service):
        """Test successful speech synthesis"""
        # Mock Polly response
        mock_audio_stream = Mock()
        mock_audio_stream.read.return_value = b"fake audio data"
        
        ai_service.polly.synthesize_speech.return_value = {
            'AudioStream': mock_audio_stream
        }
        
        # Test data
        text = "Hello, how can I help you today?"
        
        # Execute
        result = await ai_service.synthesize_speech(text)
        
        # Assertions
        assert result == b"fake audio data"
        ai_service.polly.synthesize_speech.assert_called_once_with(
            Text=text,
            OutputFormat='mp3',
            VoiceId='Joanna',
            Engine='neural'
        )
    
    @pytest.mark.asyncio
    async def test_analyze_sentiment_success(self, ai_service):
        """Test successful sentiment analysis"""
        # Mock Comprehend response
        mock_sentiment = {
            'Sentiment': 'POSITIVE',
            'SentimentScore': {'Positive': 0.8, 'Negative': 0.1, 'Neutral': 0.1, 'Mixed': 0.0}
        }
        
        ai_service.comprehend.detect_sentiment.return_value = mock_sentiment
        
        # Test data
        text = "I love your service! It's amazing!"
        
        # Execute
        result = await ai_service.analyze_sentiment(text)
        
        # Assertions
        assert result['sentiment'] == 'POSITIVE'
        assert result['sentiment_scores']['Positive'] == 0.8
        assert 'analyzed_at' in result
        
        ai_service.comprehend.detect_sentiment.assert_called_once_with(
            Text=text,
            LanguageCode='en'
        )
    
    @pytest.mark.asyncio
    async def test_detect_entities_success(self, ai_service):
        """Test successful entity detection"""
        # Mock Comprehend response
        mock_entities = {
            'Entities': [
                {'Text': 'John Doe', 'Type': 'PERSON', 'Score': 0.95},
                {'Text': 'john@example.com', 'Type': 'EMAIL', 'Score': 0.98}
            ]
        }
        
        ai_service.comprehend.detect_entities.return_value = mock_entities
        
        # Test data
        text = "My name is John Doe and my email is john@example.com"
        
        # Execute
        result = await ai_service.detect_entities(text)
        
        # Assertions
        assert len(result) == 2
        assert result[0]['Text'] == 'John Doe'
        assert result[0]['Type'] == 'PERSON'
        assert result[1]['Text'] == 'john@example.com'
        assert result[1]['Type'] == 'EMAIL'
        
        ai_service.comprehend.detect_entities.assert_called_once_with(
            Text=text,
            LanguageCode='en'
        )
    
    def test_should_escalate_high_confidence(self, ai_service):
        """Test escalation decision with high confidence"""
        intent_analysis = {'confidence': 0.9}
        sentiment = {'SentimentScore': {'Negative': 0.2}}
        
        result = ai_service._should_escalate(intent_analysis, sentiment)
        
        assert result is False
    
    def test_should_escalate_low_confidence(self, ai_service):
        """Test escalation decision with low confidence"""
        intent_analysis = {'confidence': 0.5}
        sentiment = {'SentimentScore': {'Negative': 0.2}}
        
        result = ai_service._should_escalate(intent_analysis, sentiment)
        
        assert result is True
    
    def test_should_escalate_negative_sentiment(self, ai_service):
        """Test escalation decision with negative sentiment"""
        intent_analysis = {'confidence': 0.9}
        sentiment = {'SentimentScore': {'Negative': 0.9}}
        
        result = ai_service._should_escalate(intent_analysis, sentiment)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_search_knowledge_base_success(self, ai_service):
        """Test successful knowledge base search"""
        # Test data
        query = "How do I reset my password?"
        customer_context = {"customer_id": "123", "tier": "premium"}
        
        # Execute
        result = await ai_service.search_knowledge_base(query, customer_context)
        
        # Assertions
        assert result['query'] == query
        assert 'results' in result
        assert 'total_results' in result
        assert 'search_time' in result
        assert len(result['results']) > 0
        assert result['results'][0]['title'] == 'Sample Knowledge Article'
