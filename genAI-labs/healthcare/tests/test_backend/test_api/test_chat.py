"""
Healthcare ChatGPT Clone - Chat API Tests
Tests for the chat-related API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import json


class TestChatAPI:
    """Test class for chat API endpoints."""

    def test_send_message_success(self, client: TestClient, mock_ai_service):
        """Test successful message sending."""
        with patch('backend.api.routes.chat.AIService', return_value=mock_ai_service):
            response = client.post(
                "/api/chat/send",
                json={
                    "message": "What are the symptoms of diabetes?",
                    "session_id": "test-session-123",
                    "user_id": "test-user-456"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            assert "message_id" in data
            assert "session_id" in data
            assert data["session_id"] == "test-session-123"

    def test_send_message_emergency_detection(self, client: TestClient, mock_ai_service):
        """Test emergency message detection."""
        mock_ai_service.detect_emergency.return_value = True
        mock_ai_service.get_emergency_response.return_value = "Emergency detected. Call 911."
        
        with patch('backend.api.routes.chat.AIService', return_value=mock_ai_service):
            response = client.post(
                "/api/chat/send",
                json={
                    "message": "I'm having chest pain",
                    "session_id": "test-session-123",
                    "user_id": "test-user-456"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["is_emergency"] is True
            assert "Emergency detected" in data["response"]

    def test_send_message_validation_error(self, client: TestClient):
        """Test message validation errors."""
        # Test empty message
        response = client.post(
            "/api/chat/send",
            json={
                "message": "",
                "session_id": "test-session-123",
                "user_id": "test-user-456"
            }
        )
        assert response.status_code == 422

        # Test missing required fields
        response = client.post(
            "/api/chat/send",
            json={
                "message": "Test message"
            }
        )
        assert response.status_code == 422

    def test_get_chat_history(self, client: TestClient, test_messages):
        """Test retrieving chat history."""
        with patch('backend.api.routes.chat.ChatService') as mock_chat_service:
            mock_chat_service.return_value.get_messages.return_value = test_messages
            
            response = client.get(
                "/api/chat/history/test-session-123"
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "messages" in data
            assert len(data["messages"]) == 2

    def test_get_chat_sessions(self, client: TestClient):
        """Test retrieving chat sessions."""
        mock_sessions = [
            {
                "session_id": "session-1",
                "user_id": "user-1",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "message_count": 5
            }
        ]
        
        with patch('backend.api.routes.chat.ChatService') as mock_chat_service:
            mock_chat_service.return_value.get_sessions.return_value = mock_sessions
            
            response = client.get(
                "/api/chat/sessions?user_id=user-1&limit=10"
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "sessions" in data
            assert len(data["sessions"]) == 1

    def test_delete_chat_session(self, client: TestClient):
        """Test deleting a chat session."""
        with patch('backend.api.routes.chat.ChatService') as mock_chat_service:
            mock_chat_service.return_value.delete_session.return_value = True
            
            response = client.delete(
                "/api/chat/sessions/test-session-123"
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_clear_chat_history(self, client: TestClient):
        """Test clearing chat history."""
        with patch('backend.api.routes.chat.ChatService') as mock_chat_service:
            mock_chat_service.return_value.delete_session.return_value = True
            
            response = client.post(
                "/api/chat/clear/test-session-123"
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_chat_analytics(self, client: TestClient):
        """Test chat analytics endpoint."""
        mock_analytics = {
            "total_sessions": 10,
            "total_messages": 50,
            "average_session_length": 5.0,
            "most_common_queries": [
                {"query": "diabetes symptoms", "count": 5}
            ]
        }
        
        with patch('backend.api.routes.chat.AnalyticsService') as mock_analytics_service:
            mock_analytics_service.return_value.get_chat_analytics.return_value = mock_analytics
            
            response = client.get(
                "/api/chat/analytics?start_date=2024-01-01&end_date=2024-01-31"
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "analytics" in data
            assert data["analytics"]["total_sessions"] == 10

    def test_message_validation(self, client: TestClient):
        """Test message content validation."""
        # Test malicious content
        malicious_message = "<script>alert('xss')</script>"
        
        response = client.post(
            "/api/chat/send",
            json={
                "message": malicious_message,
                "session_id": "test-session-123",
                "user_id": "test-user-456"
            }
        )
        
        # Should return 422 for validation error
        assert response.status_code == 422

    def test_rate_limiting(self, client: TestClient, mock_ai_service):
        """Test rate limiting functionality."""
        with patch('backend.api.routes.chat.AIService', return_value=mock_ai_service):
            # Send multiple requests rapidly
            for i in range(10):
                response = client.post(
                    "/api/chat/send",
                    json={
                        "message": f"Test message {i}",
                        "session_id": f"test-session-{i}",
                        "user_id": "test-user-456"
                    }
                )
                
                # All should succeed in test environment
                assert response.status_code in [200, 429]

    def test_healthcare_context_injection(self, client: TestClient, mock_ai_service):
        """Test healthcare context injection in messages."""
        with patch('backend.api.routes.chat.AIService', return_value=mock_ai_service):
            response = client.post(
                "/api/chat/send",
                json={
                    "message": "I have a headache",
                    "session_id": "test-session-123",
                    "user_id": "test-user-456",
                    "context": {
                        "age": 45,
                        "department": "neurology",
                        "medical_history": ["hypertension"]
                    }
                }
            )
            
            assert response.status_code == 200
            # Verify that context was passed to AI service
            mock_ai_service.generate_response.assert_called_once()
            call_args = mock_ai_service.generate_response.call_args
            assert "context" in call_args.kwargs

    def test_error_handling(self, client: TestClient):
        """Test error handling in chat API."""
        with patch('backend.api.routes.chat.AIService') as mock_ai_service:
            mock_ai_service.side_effect = Exception("AI service error")
            
            response = client.post(
                "/api/chat/send",
                json={
                    "message": "Test message",
                    "session_id": "test-session-123",
                    "user_id": "test-user-456"
                }
            )
            
            assert response.status_code == 500
            data = response.json()
            assert "error" in data

    def test_concurrent_requests(self, client: TestClient, mock_ai_service):
        """Test handling of concurrent requests."""
        import threading
        import time
        
        results = []
        
        def send_request():
            with patch('backend.api.routes.chat.AIService', return_value=mock_ai_service):
                response = client.post(
                    "/api/chat/send",
                    json={
                        "message": "Concurrent test message",
                        "session_id": "test-session-123",
                        "user_id": "test-user-456"
                    }
                )
                results.append(response.status_code)
        
        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=send_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        assert len(results) == 5
