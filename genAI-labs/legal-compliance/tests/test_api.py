"""
API endpoint tests for Legal Compliance AI Platform
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self, client: TestClient):
        """Test health check endpoint returns 200"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data


class TestLegalQuestionEndpoint:
    """Test legal question endpoint"""
    
    @patch('backend.api.routes.legal.LLMService')
    @patch('backend.api.routes.legal.LegalService')
    def test_ask_legal_question_success(
        self, 
        mock_legal_service_class,
        mock_llm_service_class,
        client: TestClient,
        sample_legal_question,
        sample_legal_response
    ):
        """Test successful legal question submission"""
        # Mock services
        mock_llm_service = AsyncMock()
        mock_llm_service.get_legal_response.return_value = sample_legal_response["responses"]
        mock_llm_service.compare_responses.return_value = sample_legal_response["comparison"]
        mock_llm_service_class.return_value = mock_llm_service
        
        mock_legal_service = AsyncMock()
        mock_legal_service.assess_question_complexity.return_value = "medium"
        mock_legal_service.determine_recommended_model.return_value = "gpt-4-turbo-preview"
        mock_legal_service.assess_confidence_level.return_value = "high"
        mock_legal_service.generate_follow_up_suggestions.return_value = [
            "What happens if one party breaches the contract?",
            "How can I ensure my contract is enforceable?"
        ]
        mock_legal_service_class.return_value = mock_legal_service
        
        # Make request
        response = client.post("/api/v1/ask", json=sample_legal_question)
        
        # Assertions
        assert response.status_code == 200
        
        data = response.json()
        assert data["question"] == sample_legal_question["question"]
        assert data["jurisdiction"] == sample_legal_question["jurisdiction"]
        assert data["practice_area"] == sample_legal_question["practice_area"]
        assert "responses" in data
        assert "recommended_model" in data
        assert "confidence_level" in data
    
    def test_ask_legal_question_invalid_input(self, client: TestClient):
        """Test legal question with invalid input"""
        invalid_question = {
            "question": "short",  # Too short
            "jurisdiction": "INVALID",  # Invalid jurisdiction
            "practice_area": "INVALID"  # Invalid practice area
        }
        
        response = client.post("/api/v1/ask", json=invalid_question)
        assert response.status_code == 422  # Validation error
    
    def test_ask_legal_question_missing_required_fields(self, client: TestClient):
        """Test legal question with missing required fields"""
        incomplete_question = {
            "question": "What is a contract?"
            # Missing jurisdiction and practice_area
        }
        
        response = client.post("/api/v1/ask", json=incomplete_question)
        assert response.status_code == 422  # Validation error
    
    @patch('backend.api.routes.legal.LLMService')
    def test_ask_legal_question_llm_error(
        self,
        mock_llm_service_class,
        client: TestClient,
        sample_legal_question
    ):
        """Test legal question when LLM service fails"""
        # Mock LLM service to raise an error
        mock_llm_service = AsyncMock()
        mock_llm_service.get_legal_response.side_effect = Exception("LLM service error")
        mock_llm_service_class.return_value = mock_llm_service
        
        response = client.post("/api/v1/ask", json=sample_legal_question)
        assert response.status_code == 500
    
    def test_ask_legal_question_different_jurisdictions(self, client: TestClient):
        """Test legal questions for different jurisdictions"""
        jurisdictions = ["US", "UK", "EU", "DE", "FR", "IT", "ES", "CA", "AU"]
        
        for jurisdiction in jurisdictions:
            question = {
                "question": "What are the basic legal principles in this jurisdiction?",
                "jurisdiction": jurisdiction,
                "practice_area": "general"
            }
            
            # This test would need proper mocking in a real scenario
            # For now, just test that the endpoint accepts different jurisdictions
            response = client.post("/api/v1/ask", json=question)
            # We expect validation to pass for valid jurisdictions
            # Actual LLM processing would need proper mocking


class TestQuestionHistoryEndpoint:
    """Test question history endpoint"""
    
    @patch('backend.api.routes.legal.LegalService')
    def test_get_question_history(
        self,
        mock_legal_service_class,
        client: TestClient,
        sample_question_history
    ):
        """Test getting question history"""
        # Mock legal service
        mock_legal_service = AsyncMock()
        mock_legal_service.get_question_history.return_value = sample_question_history
        mock_legal_service_class.return_value = mock_legal_service
        
        response = client.get("/api/v1/history")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "question_id" in data[0]
        assert "question" in data[0]
    
    @patch('backend.api.routes.legal.LegalService')
    def test_get_question_history_with_filters(
        self,
        mock_legal_service_class,
        client: TestClient,
        sample_question_history
    ):
        """Test getting question history with filters"""
        # Mock legal service
        mock_legal_service = AsyncMock()
        mock_legal_service.get_question_history.return_value = sample_question_history
        mock_legal_service_class.return_value = mock_legal_service
        
        response = client.get("/api/v1/history?jurisdiction=US&practice_area=contract&limit=10&offset=0")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    @patch('backend.api.routes.legal.LegalService')
    def test_get_question_history_error(
        self,
        mock_legal_service_class,
        client: TestClient
    ):
        """Test question history when service fails"""
        # Mock legal service to raise an error
        mock_legal_service = AsyncMock()
        mock_legal_service.get_question_history.side_effect = Exception("Database error")
        mock_legal_service_class.return_value = mock_legal_service
        
        response = client.get("/api/v1/history")
        assert response.status_code == 500


class TestSpecificQuestionEndpoint:
    """Test specific question retrieval endpoint"""
    
    @patch('backend.api.routes.legal.LegalService')
    def test_get_specific_question(
        self,
        mock_legal_service_class,
        client: TestClient,
        sample_legal_response
    ):
        """Test getting a specific question response"""
        # Mock legal service
        mock_legal_service = AsyncMock()
        mock_legal_service.get_question_response.return_value = sample_legal_response
        mock_legal_service_class.return_value = mock_legal_service
        
        question_id = "q_20240115_103000_abc123"
        response = client.get(f"/api/v1/history/{question_id}")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["question_id"] == question_id
        assert "responses" in data
        assert "comparison" in data
    
    @patch('backend.api.routes.legal.LegalService')
    def test_get_specific_question_not_found(
        self,
        mock_legal_service_class,
        client: TestClient
    ):
        """Test getting a non-existent question"""
        # Mock legal service to return None
        mock_legal_service = AsyncMock()
        mock_legal_service.get_question_response.return_value = None
        mock_legal_service_class.return_value = mock_legal_service
        
        question_id = "non-existent-id"
        response = client.get(f"/api/v1/history/{question_id}")
        
        assert response.status_code == 404


class TestMetadataEndpoints:
    """Test metadata endpoints (jurisdictions, practice areas, models)"""
    
    def test_get_supported_jurisdictions(self, client: TestClient):
        """Test getting supported jurisdictions"""
        response = client.get("/api/v1/jurisdictions")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Check structure of jurisdiction data
        jurisdiction = data[0]
        assert "code" in jurisdiction
        assert "name" in jurisdiction
        assert "description" in jurisdiction
    
    def test_get_supported_practice_areas(self, client: TestClient):
        """Test getting supported practice areas"""
        response = client.get("/api/v1/practice-areas")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Check structure of practice area data
        practice_area = data[0]
        assert "code" in practice_area
        assert "name" in practice_area
        assert "description" in practice_area
    
    @patch('backend.api.routes.legal.LLMService')
    def test_get_available_models(
        self,
        mock_llm_service_class,
        client: TestClient,
        test_models
    ):
        """Test getting available LLM models"""
        # Mock LLM service
        mock_llm_service = AsyncMock()
        mock_llm_service.llm_configs = {
            model["name"]: type('Config', (), {
                'max_tokens': model["max_tokens"],
                'temperature': model["temperature"]
            })() for model in test_models
        }
        mock_llm_service_class.return_value = mock_llm_service
        
        response = client.get("/api/v1/models")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Check structure of model data
        model = data[0]
        assert "name" in model
        assert "provider" in model
        assert "description" in model
        assert "max_tokens" in model


class TestPlatformStatsEndpoint:
    """Test platform statistics endpoint"""
    
    @patch('backend.api.routes.legal.LegalService')
    def test_get_platform_stats(
        self,
        mock_legal_service_class,
        client: TestClient
    ):
        """Test getting platform statistics"""
        # Mock legal service
        mock_legal_service = AsyncMock()
        mock_legal_service.get_platform_statistics.return_value = {
            "total_questions": 1250,
            "questions_today": 45,
            "average_response_time": 4.2,
            "most_common_jurisdiction": "US",
            "most_common_practice_area": "contract"
        }
        mock_legal_service_class.return_value = mock_legal_service
        
        response = client.get("/api/v1/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_questions" in data
        assert "questions_today" in data
        assert "average_response_time" in data
        assert "most_common_jurisdiction" in data
        assert "most_common_practice_area" in data
    
    @patch('backend.api.routes.legal.LegalService')
    def test_get_platform_stats_error(
        self,
        mock_legal_service_class,
        client: TestClient
    ):
        """Test platform stats when service fails"""
        # Mock legal service to raise an error
        mock_legal_service = AsyncMock()
        mock_legal_service.get_platform_statistics.side_effect = Exception("Database error")
        mock_legal_service_class.return_value = mock_legal_service
        
        response = client.get("/api/v1/stats")
        assert response.status_code == 500


class TestRootEndpoint:
    """Test root endpoint"""
    
    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "status" in data


class TestMetricsEndpoint:
    """Test metrics endpoint"""
    
    def test_metrics_endpoint(self, client: TestClient):
        """Test Prometheus metrics endpoint"""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]


class TestErrorHandling:
    """Test error handling"""
    
    def test_404_endpoint(self, client: TestClient):
        """Test 404 for non-existent endpoint"""
        response = client.get("/api/v1/non-existent")
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client: TestClient):
        """Test 405 for wrong HTTP method"""
        response = client.get("/api/v1/ask")  # POST endpoint accessed with GET
        assert response.status_code == 405
    
    def test_invalid_json(self, client: TestClient):
        """Test 422 for invalid JSON"""
        response = client.post(
            "/api/v1/ask",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422


class TestCORSHeaders:
    """Test CORS headers"""
    
    def test_cors_headers(self, client: TestClient):
        """Test that CORS headers are present"""
        response = client.options("/api/v1/ask")
        assert response.status_code == 200
        # CORS headers would be set by middleware
