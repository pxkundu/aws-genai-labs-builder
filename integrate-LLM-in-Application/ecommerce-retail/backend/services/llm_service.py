"""
Multi-LLM Service for E-Commerce Platform
Supports OpenAI and AWS Bedrock with intelligent routing and caching
"""

import json
import logging
import asyncio
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime
from functools import lru_cache

import openai
import boto3
from botocore.exceptions import ClientError

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMService:
    """Multi-LLM service with intelligent routing and caching"""
    
    def __init__(self):
        """Initialize LLM service with multiple providers"""
        self.settings = get_settings()
        self.openai_client = None
        self.bedrock_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize LLM provider clients"""
        try:
            # Initialize OpenAI
            if self.settings.OPENAI_API_KEY:
                self.openai_client = openai.AsyncOpenAI(
                    api_key=self.settings.OPENAI_API_KEY
                )
                logger.info("OpenAI client initialized")
            
            # Initialize AWS Bedrock
            if self.settings.AWS_ACCESS_KEY_ID and self.settings.AWS_SECRET_ACCESS_KEY:
                self.bedrock_client = boto3.client(
                    'bedrock-runtime',
                    region_name=self.settings.BEDROCK_REGION,
                    aws_access_key_id=self.settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=self.settings.AWS_SECRET_ACCESS_KEY
                )
                logger.info("AWS Bedrock client initialized")
            
            if not self.openai_client and not self.bedrock_client:
                logger.warning("No LLM providers configured")
                
        except Exception as e:
            logger.error(f"Failed to initialize LLM clients: {e}")
            raise
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        use_cache: bool = True,
        provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate text using LLM
        
        Args:
            prompt: User prompt
            system_prompt: System prompt for context
            model: Specific model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            use_cache: Whether to use response caching
            provider: Specific provider to use (openai, bedrock)
        
        Returns:
            Dict with response text and metadata
        """
        try:
            # Select provider
            selected_provider = provider or self.settings.LLM_PROVIDER
            
            # Generate cache key
            cache_key = None
            if use_cache and self.settings.LLM_CACHE_ENABLED:
                cache_key = self._generate_cache_key(
                    prompt, system_prompt, model, temperature
                )
                # Check cache (would integrate with Redis here)
                # cached_response = await cache.get(cache_key)
                # if cached_response:
                #     return json.loads(cached_response)
            
            # Generate response based on provider
            if selected_provider == "openai" and self.openai_client:
                response = await self._generate_openai(
                    prompt, system_prompt, model, temperature, max_tokens
                )
            elif selected_provider == "bedrock" and self.bedrock_client:
                response = await self._generate_bedrock(
                    prompt, system_prompt, model, temperature, max_tokens
                )
            else:
                # Fallback to available provider
                if self.openai_client:
                    response = await self._generate_openai(
                        prompt, system_prompt, model, temperature, max_tokens
                    )
                elif self.bedrock_client:
                    response = await self._generate_bedrock(
                        prompt, system_prompt, model, temperature, max_tokens
                    )
                else:
                    raise RuntimeError("No LLM providers available")
            
            # Cache response
            if cache_key and use_cache:
                # await cache.set(cache_key, json.dumps(response), ttl=3600)
                pass
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}", exc_info=True)
            raise
    
    async def _generate_openai(
        self,
        prompt: str,
        system_prompt: Optional[str],
        model: Optional[str],
        temperature: Optional[float],
        max_tokens: Optional[int]
    ) -> Dict[str, Any]:
        """Generate response using OpenAI"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = await self.openai_client.chat.completions.create(
                model=model or self.settings.OPENAI_MODEL,
                messages=messages,
                temperature=temperature or self.settings.OPENAI_TEMPERATURE,
                max_tokens=max_tokens or self.settings.OPENAI_MAX_TOKENS
            )
            
            return {
                "text": response.choices[0].message.content,
                "provider": "openai",
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def _generate_bedrock(
        self,
        prompt: str,
        system_prompt: Optional[str],
        model: Optional[str],
        temperature: Optional[float],
        max_tokens: Optional[int]
    ) -> Dict[str, Any]:
        """Generate response using AWS Bedrock"""
        try:
            # Prepare prompt for Claude
            full_prompt = ""
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n"
            full_prompt += f"Human: {prompt}\n\nAssistant:"
            
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens or 2000,
                "temperature": temperature or 0.7,
                "messages": [
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ]
            })
            
            response = self.bedrock_client.invoke_model(
                modelId=model or self.settings.BEDROCK_MODEL_ID,
                body=body,
                contentType="application/json"
            )
            
            response_body = json.loads(response['body'].read())
            content = response_body.get('content', [])
            text = content[0]['text'] if content else ""
            
            return {
                "text": text,
                "provider": "bedrock",
                "model": model or self.settings.BEDROCK_MODEL_ID,
                "usage": response_body.get('usage', {}),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except ClientError as e:
            logger.error(f"Bedrock API error: {e}")
            raise
    
    async def generate_batch(
        self,
        prompts: List[str],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Generate responses for multiple prompts in parallel"""
        tasks = [
            self.generate(prompt, system_prompt, **kwargs)
            for prompt in prompts
        ]
        return await asyncio.gather(*tasks)
    
    def _generate_cache_key(
        self,
        prompt: str,
        system_prompt: Optional[str],
        model: Optional[str],
        temperature: Optional[float]
    ) -> str:
        """Generate cache key for prompt"""
        key_data = {
            "prompt": prompt,
            "system_prompt": system_prompt or "",
            "model": model or "",
            "temperature": temperature or 0.7
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text using LLM"""
        system_prompt = """You are a sentiment analysis expert. 
        Analyze the sentiment of the given text and provide:
        1. Overall sentiment (positive, negative, neutral)
        2. Confidence score (0-1)
        3. Key emotions detected
        4. Brief explanation
        
        Respond in JSON format."""
        
        prompt = f"Analyze the sentiment of this text: {text}"
        
        response = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=200
        )
        
        try:
            sentiment_data = json.loads(response["text"])
            return {
                **sentiment_data,
                "original_text": text,
                "timestamp": datetime.utcnow().isoformat()
            }
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "text": response["text"],
                "original_text": text
            }
    
    async def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities from text using LLM"""
        system_prompt = """You are an entity extraction expert.
        Extract entities from the text including:
        - Product names
        - Brands
        - Categories
        - Prices
        - Dates
        - Locations
        
        Respond in JSON format with a list of entities."""
        
        prompt = f"Extract entities from this text: {text}"
        
        response = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.2,
            max_tokens=500
        )
        
        try:
            entities_data = json.loads(response["text"])
            return {
                "entities": entities_data.get("entities", []),
                "original_text": text,
                "timestamp": datetime.utcnow().isoformat()
            }
        except json.JSONDecodeError:
            return {
                "entities": [],
                "text": response["text"],
                "original_text": text
            }

