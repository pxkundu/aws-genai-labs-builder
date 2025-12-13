"""
Tests for Symptom Checker Service
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import json

# Mock boto3 before importing the service
with patch.dict('os.environ', {
    'AWS_REGION': 'us-east-1',
    'BEDROCK_MODEL_ID': 'anthropic.claude-3-sonnet-20240229-v1:0',
    'DYNAMODB_ASSESSMENTS_TABLE': 'test-assessments'
}):
    import sys
    sys.path.insert(0, '../backend')


class TestSymptomChecker:
    """Test cases for SymptomCheckerService"""

    @pytest.fixture
    def mock_bedrock_response(self):
        """Mock Bedrock API response"""
        return {
            'body': MagicMock(read=lambda: json.dumps({
                'content': [{
                    'text': json.dumps({
                        'possible_conditions': [
                            {'name': 'Common Cold', 'likelihood': 'high', 'description': 'Viral infection'}
                        ],
                        'follow_up_questions': ['How long have you had these symptoms?'],
                        'recommendations': ['Rest and stay hydrated'],
                        'urgency': 'routine',
                        'red_flags': []
                    })
                }]
            }).encode())
        }

    @pytest.fixture
    def mock_comprehend_response(self):
        """Mock Comprehend Medical response"""
        return {
            'Entities': [
                {
                    'Category': 'MEDICAL_CONDITION',
                    'Type': 'SYMPTOM',
                    'Text': 'headache',
                    'Score': 0.95
                },
                {
                    'Category': 'MEDICAL_CONDITION',
                    'Type': 'SYMPTOM',
                    'Text': 'fever',
                    'Score': 0.92
                }
            ]
        }

    def test_risk_calculation_high(self):
        """Test high risk calculation"""
        assessment = {
            'urgency': 'emergency',
            'red_flags': ['chest pain', 'difficulty breathing']
        }
        entities = {'symptoms': ['chest pain']}
        
        # Import and test
        from backend.services.symptom_checker import SymptomCheckerService
        service = SymptomCheckerService()
        
        risk_level, risk_score = service._calculate_risk(assessment, entities)
        
        assert risk_level == 'high'
        assert risk_score >= 80

    def test_risk_calculation_low(self):
        """Test low risk calculation"""
        assessment = {
            'urgency': 'routine',
            'red_flags': []
        }
        entities = {'symptoms': ['mild headache']}
        
        from backend.services.symptom_checker import SymptomCheckerService
        service = SymptomCheckerService()
        
        risk_level, risk_score = service._calculate_risk(assessment, entities)
        
        assert risk_level == 'low'
        assert risk_score < 50

    def test_fallback_assessment(self):
        """Test fallback assessment when AI is unavailable"""
        from backend.services.symptom_checker import SymptomCheckerService
        service = SymptomCheckerService()
        
        fallback = service._get_fallback_assessment()
        
        assert 'possible_conditions' in fallback
        assert 'follow_up_questions' in fallback
        assert 'recommendations' in fallback
        assert fallback['urgency'] == 'routine'


class TestTriageService:
    """Test cases for TriageService"""

    def test_triage_levels_defined(self):
        """Test that all triage levels are properly defined"""
        from backend.services.triage_service import TriageService
        
        expected_levels = ['emergency', 'urgent', 'semi-urgent', 'non-urgent', 'routine']
        
        for level in expected_levels:
            assert level in TriageService.TRIAGE_LEVELS
            assert 'priority' in TriageService.TRIAGE_LEVELS[level]
            assert 'max_wait' in TriageService.TRIAGE_LEVELS[level]

    def test_emergency_has_highest_priority(self):
        """Test that emergency has the highest priority (lowest number)"""
        from backend.services.triage_service import TriageService
        
        emergency_priority = TriageService.TRIAGE_LEVELS['emergency']['priority']
        routine_priority = TriageService.TRIAGE_LEVELS['routine']['priority']
        
        assert emergency_priority < routine_priority


class TestChatService:
    """Test cases for ChatService"""

    def test_emergency_detection(self):
        """Test emergency keyword detection"""
        from backend.services.chat_service import ChatService
        service = ChatService()
        
        # Should detect emergency
        assert service._check_emergency("I have severe chest pain") == True
        assert service._check_emergency("I can't breathe") == True
        assert service._check_emergency("I'm having a heart attack") == True
        
        # Should not detect emergency
        assert service._check_emergency("I have a mild headache") == False
        assert service._check_emergency("When is my appointment?") == False

    def test_human_handoff_detection(self):
        """Test human handoff trigger detection"""
        from backend.services.chat_service import ChatService
        service = ChatService()
        
        # Should trigger handoff
        assert service._check_requires_human("I want to speak to a human", "") == True
        assert service._check_requires_human("I have a billing issue", "") == True
        
        # Should not trigger handoff
        assert service._check_requires_human("What time is my appointment?", "") == False


class TestDocumentAnalyzer:
    """Test cases for DocumentAnalyzerService"""

    def test_supported_document_types(self):
        """Test that document types are properly defined"""
        from backend.services.document_analyzer import DocumentAnalyzerService
        
        expected_types = ['lab_results', 'prescription', 'medical_history', 'general']
        
        for doc_type in expected_types:
            assert doc_type in DocumentAnalyzerService.SUPPORTED_DOCUMENT_TYPES

    def test_fallback_analysis(self):
        """Test fallback analysis when AI is unavailable"""
        from backend.services.document_analyzer import DocumentAnalyzerService
        service = DocumentAnalyzerService()
        
        fallback = service._get_fallback_analysis('lab_results')
        
        assert 'summary' in fallback
        assert 'key_findings' in fallback
        assert 'recommendations' in fallback
        assert fallback['confidence_score'] == 0.5


# Integration test placeholder
class TestAPIEndpoints:
    """Integration tests for API endpoints"""

    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        """Test health check endpoint"""
        # This would use TestClient in a real implementation
        pass

    @pytest.mark.asyncio
    async def test_symptom_assessment_endpoint(self):
        """Test symptom assessment endpoint"""
        # This would use TestClient in a real implementation
        pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
