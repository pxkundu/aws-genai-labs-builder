"""
AI Service for GenAI Customer Service
Handles all AI-related operations using AWS services
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

import boto3
from botocore.exceptions import ClientError
import structlog

from config.settings import settings

logger = structlog.get_logger(__name__)


class AIService:
    """AI service for handling GenAI operations"""
    
    def __init__(self):
        """Initialize AI service with AWS clients"""
        self.bedrock = boto3.client(
            'bedrock-runtime',
            region_name=settings.BEDROCK_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.comprehend = boto3.client(
            'comprehend',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.transcribe = boto3.client(
            'transcribe',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.polly = boto3.client(
            'polly',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
    
    async def analyze_customer_intent(self, message: str, 
                                    customer_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze customer intent using AI"""
        try:
            prompt = f"""
            Analyze this customer service message and determine the intent:
            
            Customer Message: {message}
            Customer Context: {json.dumps(customer_context, indent=2)}
            
            Classify the intent as one of:
            - General Inquiry
            - Technical Support
            - Billing Question
            - Complaint
            - Product Information
            - Order Status
            - Account Management
            - Refund/Return
            - Escalation Request
            - Other
            
            Also provide:
            1. Intent confidence score (0-1)
            2. Key topics mentioned
            3. Urgency level (Low/Medium/High)
            4. Required information to resolve
            5. Suggested response approach
            
            Format as JSON.
            """
            
            response = self.bedrock.invoke_model(
                modelId=settings.BEDROCK_MODEL_ID,
                body=json.dumps({
                    'anthropic_version': 'bedrock-2023-05-31',
                    'max_tokens': 1000,
                    'messages': [{'role': 'user', 'content': prompt}]
                })
            )
            
            result = json.loads(response['body'].read())
            intent_analysis = json.loads(result['content'][0]['text'])
            
            logger.info("Intent analysis completed", 
                       intent=intent_analysis.get('intent'),
                       confidence=intent_analysis.get('confidence'))
            
            return intent_analysis
            
        except ClientError as e:
            logger.error("Failed to analyze intent", error=str(e))
            raise Exception(f"Intent analysis failed: {str(e)}")
    
    async def generate_response(self, message: str, 
                              intent_analysis: Dict[str, Any],
                              customer_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered response"""
        try:
            # Get sentiment analysis
            sentiment = self.comprehend.detect_sentiment(
                Text=message, 
                LanguageCode='en'
            )
            
            # Get entities
            entities = self.comprehend.detect_entities(
                Text=message, 
                LanguageCode='en'
            )
            
            prompt = f"""
            Generate a helpful customer service response:
            
            Customer Message: {message}
            Intent: {intent_analysis.get('intent', 'Unknown')}
            Sentiment: {sentiment.get('Sentiment', 'Neutral')}
            Sentiment Score: {sentiment.get('SentimentScore', {})}
            Customer Context: {json.dumps(customer_context, indent=2)}
            
            Guidelines:
            1. Be helpful, empathetic, and professional
            2. Address the customer's specific need
            3. Provide actionable solutions
            4. Match the customer's tone and urgency
            5. Include relevant information from customer context
            6. Keep response concise but complete
            
            Generate:
            1. Main response text
            2. Suggested actions
            3. Next steps
            4. Additional resources if needed
            """
            
            response = self.bedrock.invoke_model(
                modelId=settings.BEDROCK_MODEL_ID,
                body=json.dumps({
                    'anthropic_version': 'bedrock-2023-05-31',
                    'max_tokens': 1500,
                    'messages': [{'role': 'user', 'content': prompt}]
                })
            )
            
            result = json.loads(response['body'].read())
            response_text = result['content'][0]['text']
            
            return {
                'response_text': response_text,
                'sentiment': sentiment,
                'entities': entities['Entities'],
                'confidence_score': intent_analysis.get('confidence', 0.0),
                'escalation_needed': self._should_escalate(intent_analysis, sentiment),
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except ClientError as e:
            logger.error("Failed to generate response", error=str(e))
            raise Exception(f"Response generation failed: {str(e)}")
    
    async def transcribe_audio(self, audio_data: bytes, 
                             language_code: str = None) -> str:
        """Transcribe audio to text"""
        try:
            language_code = language_code or settings.TRANSCRIBE_LANGUAGE
            
            # For real-time transcription, we would use streaming
            # For this example, we'll use batch transcription
            job_name = f"transcription_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # In a real implementation, you would upload to S3 first
            # For demo purposes, we'll simulate the transcription
            response = self.transcribe.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': 's3://your-bucket/audio-file.wav'},
                MediaFormat='wav',
                LanguageCode=language_code,
                Settings={
                    'ShowSpeakerLabels': True,
                    'MaxSpeakerLabels': 2
                }
            )
            
            # Wait for completion (in real implementation)
            # For demo, return a placeholder
            return "This is a placeholder transcription result"
            
        except ClientError as e:
            logger.error("Failed to transcribe audio", error=str(e))
            raise Exception(f"Audio transcription failed: {str(e)}")
    
    async def synthesize_speech(self, text: str, 
                              voice_id: str = None) -> bytes:
        """Convert text to speech"""
        try:
            voice_id = voice_id or settings.POLLY_VOICE_ID
            
            response = self.polly.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId=voice_id,
                Engine=settings.POLLY_ENGINE
            )
            
            return response['AudioStream'].read()
            
        except ClientError as e:
            logger.error("Failed to synthesize speech", error=str(e))
            raise Exception(f"Speech synthesis failed: {str(e)}")
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        try:
            response = self.comprehend.detect_sentiment(
                Text=text,
                LanguageCode='en'
            )
            
            return {
                'sentiment': response['Sentiment'],
                'sentiment_scores': response['SentimentScore'],
                'analyzed_at': datetime.utcnow().isoformat()
            }
            
        except ClientError as e:
            logger.error("Failed to analyze sentiment", error=str(e))
            raise Exception(f"Sentiment analysis failed: {str(e)}")
    
    async def detect_entities(self, text: str) -> List[Dict[str, Any]]:
        """Detect entities in text"""
        try:
            response = self.comprehend.detect_entities(
                Text=text,
                LanguageCode='en'
            )
            
            return response['Entities']
            
        except ClientError as e:
            logger.error("Failed to detect entities", error=str(e))
            raise Exception(f"Entity detection failed: {str(e)}")
    
    def _should_escalate(self, intent_analysis: Dict[str, Any], 
                        sentiment: Dict[str, Any]) -> bool:
        """Determine if escalation is needed"""
        confidence = intent_analysis.get('confidence', 0.0)
        sentiment_score = sentiment.get('SentimentScore', {})
        negative_score = sentiment_score.get('Negative', 0.0)
        
        # Escalate if confidence is low or sentiment is very negative
        return (confidence < settings.ESCALATION_THRESHOLD or 
                negative_score > 0.8)
    
    async def search_knowledge_base(self, query: str, 
                                  customer_context: Dict[str, Any]) -> Dict[str, Any]:
        """Search knowledge base using semantic search"""
        try:
            # This would integrate with OpenSearch for semantic search
            # For now, return a placeholder response
            return {
                'query': query,
                'results': [
                    {
                        'title': 'Sample Knowledge Article',
                        'content': 'This is a sample knowledge base article',
                        'relevance_score': 0.95,
                        'url': '/kb/sample-article'
                    }
                ],
                'total_results': 1,
                'search_time': 0.1
            }
            
        except Exception as e:
            logger.error("Failed to search knowledge base", error=str(e))
            raise Exception(f"Knowledge base search failed: {str(e)}")
