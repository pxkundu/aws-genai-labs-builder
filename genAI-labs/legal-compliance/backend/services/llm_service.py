"""
Multi-LLM Service for Legal Compliance AI Platform
Integrates OpenAI GPT-4, Anthropic Claude, and Google Gemini
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

import openai
import anthropic
import google.generativeai as genai
from core.config import get_settings
from core.cache import get_cache
from models.legal_question import LegalQuestionRequest, LLMResponse

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class LLMConfig:
    """LLM configuration"""
    model: str
    max_tokens: int
    temperature: float
    top_p: float
    timeout: int = 30


class LLMService:
    """Multi-LLM service for legal question answering"""
    
    def __init__(self):
        self.settings = get_settings()
        self.cache = get_cache()
        
        # Initialize LLM clients
        self._init_openai()
        self._init_anthropic()
        self._init_google()
        
        # LLM configurations
        self.llm_configs = {
            "gpt-4-turbo-preview": LLMConfig(
                model="gpt-4-turbo-preview",
                max_tokens=4000,
                temperature=0.1,
                top_p=0.9
            ),
            "claude-3-5-sonnet-20241022": LLMConfig(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0.1,
                top_p=0.9
            ),
            "gemini-pro": LLMConfig(
                model="gemini-pro",
                max_tokens=4000,
                temperature=0.1,
                top_p=0.9
            )
        }
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        if self.settings.OPENAI_API_KEY:
            openai.api_key = self.settings.OPENAI_API_KEY
            self.openai_client = openai.AsyncOpenAI(api_key=self.settings.OPENAI_API_KEY)
        else:
            logger.warning("OpenAI API key not provided")
            self.openai_client = None
    
    def _init_anthropic(self):
        """Initialize Anthropic client"""
        if self.settings.ANTHROPIC_API_KEY:
            self.anthropic_client = anthropic.AsyncAnthropic(
                api_key=self.settings.ANTHROPIC_API_KEY
            )
        else:
            logger.warning("Anthropic API key not provided")
            self.anthropic_client = None
    
    def _init_google(self):
        """Initialize Google AI client"""
        if self.settings.GOOGLE_API_KEY:
            genai.configure(api_key=self.settings.GOOGLE_API_KEY)
            self.google_model = genai.GenerativeModel('gemini-pro')
        else:
            logger.warning("Google API key not provided")
            self.google_model = None
    
    async def get_legal_response(
        self, 
        question: str, 
        jurisdiction: str = "US",
        practice_area: str = "general",
        models: List[str] = None
    ) -> Dict[str, LLMResponse]:
        """
        Get legal response from multiple LLMs
        
        Args:
            question: Legal question
            jurisdiction: Legal jurisdiction (US, EU, UK, etc.)
            practice_area: Legal practice area
            models: List of models to use (default: all available)
        
        Returns:
            Dictionary of model responses
        """
        if models is None:
            models = list(self.llm_configs.keys())
        
        # Check cache first
        cache_key = f"legal_response:{hash(question)}:{jurisdiction}:{practice_area}"
        cached_response = await self.cache.get(cache_key)
        if cached_response:
            logger.info(f"Cache hit for question: {question[:50]}...")
            return json.loads(cached_response)
        
        # Generate legal context
        legal_context = await self._generate_legal_context(question, jurisdiction, practice_area)
        
        # Prepare tasks for concurrent execution
        tasks = []
        for model in models:
            if model in self.llm_configs:
                task = self._get_model_response(model, question, legal_context, jurisdiction, practice_area)
                tasks.append(task)
        
        # Execute all models concurrently
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process responses
        result = {}
        for i, response in enumerate(responses):
            model = models[i]
            if isinstance(response, Exception):
                logger.error(f"Error from {model}: {str(response)}")
                result[model] = LLMResponse(
                    model=model,
                    response=f"Error: {str(response)}",
                    confidence=0.0,
                    tokens_used=0,
                    processing_time=0.0,
                    timestamp=datetime.utcnow().isoformat(),
                    error=str(response)
                )
            else:
                result[model] = response
        
        # Cache the response
        await self.cache.set(cache_key, json.dumps(result, default=str), ttl=self.settings.CACHE_TTL)
        
        return result
    
    async def _get_model_response(
        self, 
        model: str, 
        question: str, 
        legal_context: str,
        jurisdiction: str,
        practice_area: str
    ) -> LLMResponse:
        """Get response from a specific model"""
        start_time = datetime.utcnow()
        
        try:
            if model.startswith("gpt-"):
                response = await self._get_openai_response(model, question, legal_context, jurisdiction, practice_area)
            elif model.startswith("claude-"):
                response = await self._get_anthropic_response(model, question, legal_context, jurisdiction, practice_area)
            elif model.startswith("gemini-"):
                response = await self._get_google_response(model, question, legal_context, jurisdiction, practice_area)
            else:
                raise ValueError(f"Unsupported model: {model}")
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            response.processing_time = processing_time
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting response from {model}: {str(e)}")
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            return LLMResponse(
                model=model,
                response=f"Error: {str(e)}",
                confidence=0.0,
                tokens_used=0,
                processing_time=processing_time,
                timestamp=datetime.utcnow().isoformat(),
                error=str(e)
            )
    
    async def _get_openai_response(
        self, 
        model: str, 
        question: str, 
        legal_context: str,
        jurisdiction: str,
        practice_area: str
    ) -> LLMResponse:
        """Get response from OpenAI"""
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized")
        
        config = self.llm_configs[model]
        
        system_prompt = self._get_legal_system_prompt(jurisdiction, practice_area)
        user_prompt = f"{legal_context}\n\nLegal Question: {question}"
        
        response = await self.openai_client.chat.completions.create(
            model=config.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            top_p=config.top_p
        )
        
        return LLMResponse(
            model=model,
            response=response.choices[0].message.content,
            confidence=0.9,  # OpenAI doesn't provide confidence scores
            tokens_used=response.usage.total_tokens,
            processing_time=0.0,  # Will be set by caller
            timestamp=datetime.utcnow().isoformat()
        )
    
    async def _get_anthropic_response(
        self, 
        model: str, 
        question: str, 
        legal_context: str,
        jurisdiction: str,
        practice_area: str
    ) -> LLMResponse:
        """Get response from Anthropic Claude"""
        if not self.anthropic_client:
            raise ValueError("Anthropic client not initialized")
        
        config = self.llm_configs[model]
        
        system_prompt = self._get_legal_system_prompt(jurisdiction, practice_area)
        user_prompt = f"{legal_context}\n\nLegal Question: {question}"
        
        response = await self.anthropic_client.messages.create(
            model=config.model,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        return LLMResponse(
            model=model,
            response=response.content[0].text,
            confidence=0.9,  # Claude doesn't provide confidence scores
            tokens_used=response.usage.input_tokens + response.usage.output_tokens,
            processing_time=0.0,  # Will be set by caller
            timestamp=datetime.utcnow().isoformat()
        )
    
    async def _get_google_response(
        self, 
        model: str, 
        question: str, 
        legal_context: str,
        jurisdiction: str,
        practice_area: str
    ) -> LLMResponse:
        """Get response from Google Gemini"""
        if not self.google_model:
            raise ValueError("Google AI client not initialized")
        
        config = self.llm_configs[model]
        
        system_prompt = self._get_legal_system_prompt(jurisdiction, practice_area)
        user_prompt = f"{system_prompt}\n\n{legal_context}\n\nLegal Question: {question}"
        
        response = await self.google_model.generate_content_async(
            user_prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=config.max_tokens,
                temperature=config.temperature,
                top_p=config.top_p
            )
        )
        
        return LLMResponse(
            model=model,
            response=response.text,
            confidence=0.9,  # Gemini doesn't provide confidence scores
            tokens_used=len(response.text.split()),  # Approximate token count
            processing_time=0.0,  # Will be set by caller
            timestamp=datetime.utcnow().isoformat()
        )
    
    def _get_legal_system_prompt(self, jurisdiction: str, practice_area: str) -> str:
        """Generate legal system prompt based on jurisdiction and practice area"""
        
        jurisdiction_context = {
            "US": "United States federal and state law, including common law principles",
            "UK": "English and Welsh law, including common law and statutory law",
            "EU": "European Union law, including regulations, directives, and ECJ case law",
            "DE": "German civil law system (Bürgerliches Gesetzbuch)",
            "FR": "French civil law system (Code civil)",
            "IT": "Italian civil law system (Codice civile)",
            "ES": "Spanish civil law system (Código civil)",
            "CA": "Canadian federal and provincial law",
            "AU": "Australian federal and state law"
        }
        
        practice_area_context = {
            "general": "general legal principles and procedures",
            "contract": "contract law, formation, performance, and remedies",
            "tort": "tort law, negligence, and civil liability",
            "criminal": "criminal law and procedure",
            "corporate": "corporate law, business entities, and governance",
            "employment": "employment law and labor relations",
            "intellectual_property": "intellectual property law and protection",
            "real_estate": "real estate law and property rights",
            "family": "family law and domestic relations",
            "immigration": "immigration law and procedures"
        }
        
        jurisdiction_desc = jurisdiction_context.get(jurisdiction, "general legal principles")
        practice_desc = practice_area_context.get(practice_area, "general legal principles")
        
        return f"""You are a specialized legal AI assistant with expertise in {jurisdiction_desc} and {practice_desc}.

Your role is to provide accurate, helpful, and comprehensive legal information while maintaining the highest standards of legal accuracy and professionalism.

Guidelines:
1. Provide clear, well-structured legal analysis
2. Cite relevant legal principles, statutes, and case law when applicable
3. Distinguish between settled law and areas of legal uncertainty
4. Highlight important deadlines, procedures, and requirements
5. Recommend consulting with qualified legal counsel for specific situations
6. Maintain objectivity and avoid providing legal advice for specific cases
7. Use clear, accessible language while maintaining legal precision

Important Disclaimers:
- This information is for educational and informational purposes only
- It does not constitute legal advice
- Laws vary by jurisdiction and change over time
- Users should consult with qualified legal counsel for specific legal matters
- No attorney-client relationship is formed through this interaction

Please provide a comprehensive response to the legal question, including:
- Relevant legal principles and authorities
- Practical considerations and procedures
- Potential risks and considerations
- Recommendations for further action
- Important disclaimers and limitations"""
    
    async def _generate_legal_context(
        self, 
        question: str, 
        jurisdiction: str, 
        practice_area: str
    ) -> str:
        """Generate legal context for the question"""
        
        # This could be enhanced with legal knowledge base integration
        context_parts = [
            f"Jurisdiction: {jurisdiction}",
            f"Practice Area: {practice_area}",
            f"Question Type: {self._classify_question_type(question)}",
            f"Complexity: {self._assess_question_complexity(question)}"
        ]
        
        return "\n".join(context_parts)
    
    def _classify_question_type(self, question: str) -> str:
        """Classify the type of legal question"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ["contract", "agreement", "breach", "performance"]):
            return "contract_law"
        elif any(word in question_lower for word in ["liability", "negligence", "damages", "injury"]):
            return "tort_law"
        elif any(word in question_lower for word in ["criminal", "arrest", "charge", "penalty"]):
            return "criminal_law"
        elif any(word in question_lower for word in ["corporation", "company", "board", "shareholder"]):
            return "corporate_law"
        elif any(word in question_lower for word in ["employee", "workplace", "discrimination", "harassment"]):
            return "employment_law"
        elif any(word in question_lower for word in ["patent", "trademark", "copyright", "intellectual property"]):
            return "intellectual_property"
        else:
            return "general_legal"
    
    def _assess_question_complexity(self, question: str) -> str:
        """Assess the complexity of the legal question"""
        # Simple heuristic based on question length and legal terminology
        legal_terms = [
            "jurisdiction", "precedent", "statute", "regulation", "compliance",
            "litigation", "arbitration", "mediation", "liability", "indemnification"
        ]
        
        question_lower = question.lower()
        legal_term_count = sum(1 for term in legal_terms if term in question_lower)
        
        if len(question.split()) > 50 or legal_term_count > 3:
            return "high"
        elif len(question.split()) > 20 or legal_term_count > 1:
            return "medium"
        else:
            return "low"
    
    async def compare_responses(self, responses: Dict[str, LLMResponse]) -> Dict[str, Any]:
        """Compare and analyze responses from different models"""
        
        if len(responses) < 2:
            return {"message": "Need at least 2 responses to compare"}
        
        # Extract response texts
        response_texts = {model: response.response for model, response in responses.items()}
        
        # Analyze consensus
        consensus_analysis = await self._analyze_consensus(response_texts)
        
        # Identify key differences
        differences = await self._identify_differences(response_texts)
        
        # Rank responses by quality
        quality_ranking = await self._rank_response_quality(responses)
        
        return {
            "consensus_analysis": consensus_analysis,
            "key_differences": differences,
            "quality_ranking": quality_ranking,
            "summary": self._generate_comparison_summary(consensus_analysis, differences, quality_ranking)
        }
    
    async def _analyze_consensus(self, response_texts: Dict[str, str]) -> Dict[str, Any]:
        """Analyze consensus between responses"""
        # This is a simplified implementation
        # In a real system, you might use semantic similarity models
        
        responses = list(response_texts.values())
        
        # Simple consensus analysis based on common keywords
        all_words = []
        for response in responses:
            words = response.lower().split()
            all_words.extend(words)
        
        # Find common legal terms
        legal_terms = [
            "law", "legal", "rights", "liability", "contract", "statute",
            "regulation", "jurisdiction", "precedent", "court", "judge"
        ]
        
        consensus_score = 0
        for term in legal_terms:
            term_count = sum(1 for response in responses if term in response.lower())
            if term_count > len(responses) / 2:
                consensus_score += 1
        
        consensus_percentage = (consensus_score / len(legal_terms)) * 100
        
        return {
            "consensus_score": consensus_percentage,
            "consensus_level": "high" if consensus_percentage > 70 else "medium" if consensus_percentage > 40 else "low",
            "common_themes": self._extract_common_themes(responses)
        }
    
    def _extract_common_themes(self, responses: List[str]) -> List[str]:
        """Extract common themes from responses"""
        # Simplified theme extraction
        themes = []
        
        # Check for common legal concepts
        legal_concepts = [
            "contract formation", "liability", "damages", "jurisdiction",
            "statute of limitations", "burden of proof", "precedent"
        ]
        
        for concept in legal_concepts:
            concept_count = sum(1 for response in responses if concept in response.lower())
            if concept_count > len(responses) / 2:
                themes.append(concept)
        
        return themes
    
    async def _identify_differences(self, response_texts: Dict[str, str]) -> List[Dict[str, str]]:
        """Identify key differences between responses"""
        # Simplified difference identification
        differences = []
        
        models = list(response_texts.keys())
        for i in range(len(models)):
            for j in range(i + 1, len(models)):
                model1, model2 = models[i], models[j]
                response1, response2 = response_texts[model1], response_texts[model2]
                
                # Simple length comparison
                if abs(len(response1) - len(response2)) > 100:
                    differences.append({
                        "models": f"{model1} vs {model2}",
                        "difference": "Response length significantly different",
                        "details": f"{model1}: {len(response1)} chars, {model2}: {len(response2)} chars"
                    })
        
        return differences
    
    async def _rank_response_quality(self, responses: Dict[str, LLMResponse]) -> List[Dict[str, Any]]:
        """Rank responses by quality"""
        
        # Simple quality ranking based on response length, processing time, and error status
        ranked_responses = []
        
        for model, response in responses.items():
            quality_score = 0
            
            # Length score (longer responses generally better for legal questions)
            if len(response.response) > 500:
                quality_score += 3
            elif len(response.response) > 200:
                quality_score += 2
            else:
                quality_score += 1
            
            # Processing time score (faster is better)
            if response.processing_time < 5:
                quality_score += 2
            elif response.processing_time < 10:
                quality_score += 1
            
            # Error penalty
            if response.error:
                quality_score -= 5
            
            # Token usage score
            if response.tokens_used > 1000:
                quality_score += 2
            elif response.tokens_used > 500:
                quality_score += 1
            
            ranked_responses.append({
                "model": model,
                "quality_score": quality_score,
                "response": response,
                "ranking_factors": {
                    "length": len(response.response),
                    "processing_time": response.processing_time,
                    "tokens_used": response.tokens_used,
                    "has_error": bool(response.error)
                }
            })
        
        # Sort by quality score
        ranked_responses.sort(key=lambda x: x["quality_score"], reverse=True)
        
        return ranked_responses
    
    def _generate_comparison_summary(
        self, 
        consensus_analysis: Dict[str, Any],
        differences: List[Dict[str, str]],
        quality_ranking: List[Dict[str, Any]]
    ) -> str:
        """Generate a summary of the comparison"""
        
        best_model = quality_ranking[0]["model"] if quality_ranking else "unknown"
        consensus_level = consensus_analysis.get("consensus_level", "unknown")
        
        summary = f"""
Comparison Summary:
- Best Quality Response: {best_model}
- Consensus Level: {consensus_level.title()}
- Key Differences: {len(differences)} differences identified
- Common Themes: {', '.join(consensus_analysis.get('common_themes', []))}

Recommendation: {'High consensus - responses are generally aligned' if consensus_level == 'high' else 'Mixed consensus - consider multiple perspectives' if consensus_level == 'medium' else 'Low consensus - responses vary significantly'}
        """.strip()
        
        return summary
