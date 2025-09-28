"""
Legal Service for the Legal Compliance AI Platform
Handles legal-specific logic, question analysis, and response processing
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from core.cache import get_cache
from models.legal_question import (
    LegalQuestionResponse, 
    QuestionHistory, 
    QuestionComplexity,
    LLMResponse,
    Jurisdiction,
    PracticeArea
)

logger = logging.getLogger(__name__)


class LegalService:
    """Service for legal-specific operations"""
    
    def __init__(self):
        self.cache = get_cache()
        
        # Legal complexity assessment criteria
        self.complexity_keywords = {
            "high": [
                "litigation", "appeal", "constitutional", "supreme court", "precedent",
                "multi-jurisdictional", "regulatory compliance", "securities law",
                "international law", "tax implications", "intellectual property",
                "merger", "acquisition", "due diligence", "antitrust"
            ],
            "medium": [
                "contract", "liability", "damages", "breach", "enforceability",
                "statute of limitations", "jurisdiction", "venue", "evidence",
                "negligence", "tort", "employment", "discrimination"
            ],
            "low": [
                "what is", "definition", "basic", "simple", "explain",
                "difference between", "how to", "requirements for"
            ]
        }
        
        # Follow-up question templates
        self.follow_up_templates = {
            PracticeArea.CONTRACT: [
                "What are the consequences of breaching this type of contract?",
                "How can I ensure this contract is legally enforceable?",
                "What are common pitfalls to avoid in contract formation?",
                "How do I terminate this contract legally?",
                "What remedies are available if the other party breaches?"
            ],
            PracticeArea.TORT: [
                "What damages can be recovered in this type of case?",
                "How do I prove negligence in this situation?",
                "What defenses are available to the defendant?",
                "What is the statute of limitations for this type of claim?",
                "How do I calculate economic and non-economic damages?"
            ],
            PracticeArea.CORPORATE: [
                "What are the fiduciary duties in this situation?",
                "How do I ensure corporate compliance?",
                "What are the liability implications for directors?",
                "How do I handle shareholder disputes?",
                "What are the reporting requirements?"
            ],
            PracticeArea.EMPLOYMENT: [
                "What are the anti-discrimination protections?",
                "How do I handle workplace harassment claims?",
                "What are the requirements for termination?",
                "How do I ensure wage and hour compliance?",
                "What are the employee privacy rights?"
            ]
        }
    
    async def assess_question_complexity(
        self, 
        question: str, 
        jurisdiction: Jurisdiction, 
        practice_area: PracticeArea
    ) -> QuestionComplexity:
        """Assess the complexity of a legal question"""
        
        question_lower = question.lower()
        
        # Check for high complexity indicators
        high_complexity_count = sum(
            1 for keyword in self.complexity_keywords["high"] 
            if keyword in question_lower
        )
        
        # Check for medium complexity indicators
        medium_complexity_count = sum(
            1 for keyword in self.complexity_keywords["medium"] 
            if keyword in question_lower
        )
        
        # Check for low complexity indicators
        low_complexity_count = sum(
            1 for keyword in self.complexity_keywords["low"] 
            if keyword in question_lower
        )
        
        # Additional complexity factors
        word_count = len(question.split())
        has_multiple_questions = question.count('?') > 1
        has_specific_facts = any(word in question_lower for word in [
            "company", "individual", "specific", "case", "situation", "circumstances"
        ])
        
        # Determine complexity
        if high_complexity_count > 0 or (word_count > 50 and has_specific_facts):
            return QuestionComplexity.HIGH
        elif medium_complexity_count > 0 or word_count > 30 or has_multiple_questions:
            return QuestionComplexity.MEDIUM
        elif low_complexity_count > 0 or word_count < 20:
            return QuestionComplexity.LOW
        else:
            return QuestionComplexity.MEDIUM
    
    async def determine_recommended_model(
        self, 
        responses: Dict[str, LLMResponse], 
        comparison: Optional[Dict[str, Any]] = None
    ) -> str:
        """Determine the recommended model based on response quality"""
        
        if not responses:
            return "gpt-4-turbo-preview"  # Default fallback
        
        # If we have comparison data, use the quality ranking
        if comparison and "quality_ranking" in comparison:
            quality_ranking = comparison["quality_ranking"]
            if quality_ranking:
                return quality_ranking[0]["model"]
        
        # Fallback to simple heuristic
        best_model = None
        best_score = -1
        
        for model, response in responses.items():
            if response.error:
                continue  # Skip models with errors
            
            # Simple scoring based on response characteristics
            score = 0
            
            # Length score (longer responses generally better for legal questions)
            if len(response.response) > 1000:
                score += 3
            elif len(response.response) > 500:
                score += 2
            else:
                score += 1
            
            # Confidence score
            score += response.confidence * 2
            
            # Processing time bonus (faster is better)
            if response.processing_time < 5:
                score += 1
            
            if score > best_score:
                best_score = score
                best_model = model
        
        return best_model or list(responses.keys())[0]
    
    async def assess_confidence_level(
        self, 
        responses: Dict[str, LLMResponse], 
        comparison: Optional[Dict[str, Any]] = None
    ) -> str:
        """Assess overall confidence level"""
        
        if not responses:
            return "low"
        
        # Calculate average confidence
        valid_responses = [r for r in responses.values() if not r.error]
        if not valid_responses:
            return "low"
        
        avg_confidence = sum(r.confidence for r in valid_responses) / len(valid_responses)
        
        # Factor in consensus if available
        consensus_bonus = 0
        if comparison and "consensus_analysis" in comparison:
            consensus_score = comparison["consensus_analysis"].get("consensus_score", 0)
            if consensus_score > 80:
                consensus_bonus = 0.2
            elif consensus_score > 60:
                consensus_bonus = 0.1
        
        final_confidence = avg_confidence + consensus_bonus
        
        if final_confidence > 0.8:
            return "high"
        elif final_confidence > 0.6:
            return "medium"
        else:
            return "low"
    
    async def generate_follow_up_suggestions(
        self, 
        question: str, 
        jurisdiction: Jurisdiction, 
        practice_area: PracticeArea
    ) -> List[str]:
        """Generate relevant follow-up question suggestions"""
        
        suggestions = []
        
        # Get practice area specific suggestions
        if practice_area in self.follow_up_templates:
            suggestions.extend(self.follow_up_templates[practice_area][:2])
        
        # Generate contextual suggestions based on question content
        question_lower = question.lower()
        
        if "contract" in question_lower:
            suggestions.extend([
                "What are the key elements that make a contract legally binding?",
                "How can I protect myself from contract disputes?"
            ])
        elif "liability" in question_lower or "negligence" in question_lower:
            suggestions.extend([
                "What types of damages can be recovered in negligence cases?",
                "How do I prove causation in a negligence claim?"
            ])
        elif "employment" in question_lower:
            suggestions.extend([
                "What are the key employment law protections I should know?",
                "How do I handle workplace discrimination issues?"
            ])
        
        # Add jurisdiction-specific suggestions
        if jurisdiction in [Jurisdiction.US, Jurisdiction.UK]:
            suggestions.append("What are the key differences between state/federal law in this area?")
        elif jurisdiction == Jurisdiction.EU:
            suggestions.append("How do EU regulations interact with national law?")
        
        # Remove duplicates and limit to 5 suggestions
        unique_suggestions = list(dict.fromkeys(suggestions))
        return unique_suggestions[:5]
    
    async def get_question_history(
        self,
        limit: int = 50,
        offset: int = 0,
        jurisdiction: Optional[Jurisdiction] = None,
        practice_area: Optional[PracticeArea] = None,
        db: Session = None
    ) -> List[QuestionHistory]:
        """Get question history from database"""
        
        # TODO: Implement actual database queries
        # This is a placeholder implementation
        
        mock_history = [
            QuestionHistory(
                question_id="q_20240115_103000_abc123",
                question="What are the requirements for a valid contract?",
                jurisdiction=Jurisdiction.US,
                practice_area=PracticeArea.CONTRACT,
                timestamp=datetime.utcnow() - timedelta(hours=1),
                response_count=3,
                recommended_model="gpt-4-turbo-preview",
                confidence_level="high"
            ),
            QuestionHistory(
                question_id="q_20240115_102000_def456",
                question="How do I handle workplace harassment?",
                jurisdiction=Jurisdiction.US,
                practice_area=PracticeArea.EMPLOYMENT,
                timestamp=datetime.utcnow() - timedelta(hours=2),
                response_count=3,
                recommended_model="claude-3-5-sonnet-20241022",
                confidence_level="medium"
            )
        ]
        
        # Apply filters
        filtered_history = mock_history
        
        if jurisdiction:
            filtered_history = [h for h in filtered_history if h.jurisdiction == jurisdiction]
        
        if practice_area:
            filtered_history = [h for h in filtered_history if h.practice_area == practice_area]
        
        # Apply pagination
        return filtered_history[offset:offset + limit]
    
    async def get_question_response(
        self, 
        question_id: str, 
        db: Session
    ) -> Optional[LegalQuestionResponse]:
        """Get full response for a specific question ID"""
        
        # TODO: Implement actual database query
        # This is a placeholder implementation
        
        if question_id == "q_20240115_103000_abc123":
            return LegalQuestionResponse(
                question_id=question_id,
                question="What are the requirements for a valid contract?",
                jurisdiction=Jurisdiction.US,
                practice_area=PracticeArea.CONTRACT,
                complexity=QuestionComplexity.MEDIUM,
                responses={
                    "gpt-4-turbo-preview": LLMResponse(
                        model="gpt-4-turbo-preview",
                        response="Under US contract law, a valid contract requires...",
                        confidence=0.95,
                        tokens_used=1250,
                        processing_time=3.2,
                        timestamp=datetime.utcnow().isoformat()
                    )
                },
                comparison=None,
                timestamp=datetime.utcnow().isoformat(),
                processing_time=5.1,
                cached=False,
                recommended_model="gpt-4-turbo-preview",
                confidence_level="high",
                follow_up_suggestions=[
                    "What happens if one party breaches the contract?",
                    "How can I ensure my contract is enforceable?"
                ]
            )
        
        return None
    
    async def get_platform_statistics(self, db: Session) -> Dict[str, Any]:
        """Get platform usage statistics"""
        
        # TODO: Implement actual database queries
        # This is a placeholder implementation
        
        return {
            "total_questions": 1250,
            "questions_today": 45,
            "questions_this_week": 280,
            "questions_this_month": 1100,
            "average_response_time": 4.2,
            "most_common_jurisdiction": "US",
            "most_common_practice_area": "contract",
            "total_tokens_used": 2500000,
            "cache_hit_rate": 0.75,
            "user_satisfaction_score": 4.6,
            "active_models": [
                "gpt-4-turbo-preview",
                "claude-3-5-sonnet-20241022", 
                "gemini-pro"
            ],
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def validate_legal_question(
        self, 
        question: str, 
        jurisdiction: Jurisdiction, 
        practice_area: PracticeArea
    ) -> Dict[str, Any]:
        """Validate and analyze a legal question"""
        
        validation_result = {
            "is_valid": True,
            "warnings": [],
            "suggestions": [],
            "complexity": await self.assess_question_complexity(question, jurisdiction, practice_area)
        }
        
        # Check question length
        if len(question) < 10:
            validation_result["is_valid"] = False
            validation_result["warnings"].append("Question is too short. Please provide more details.")
        
        if len(question) > 2000:
            validation_result["warnings"].append("Question is very long. Consider breaking it into smaller parts.")
        
        # Check for legal terminology
        legal_terms = ["law", "legal", "rights", "liability", "contract", "court", "statute", "regulation"]
        has_legal_terms = any(term in question.lower() for term in legal_terms)
        
        if not has_legal_terms:
            validation_result["suggestions"].append("Consider including more specific legal terminology for better results.")
        
        # Check for jurisdiction-specific considerations
        if jurisdiction in [Jurisdiction.EU, Jurisdiction.DE, Jurisdiction.FR]:
            validation_result["suggestions"].append("For EU/German/French law, consider specifying if you need EU-level or national-level guidance.")
        
        return validation_result
