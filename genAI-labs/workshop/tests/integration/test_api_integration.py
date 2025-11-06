"""
Integration tests for Claude Code API
Note: These tests require actual AWS infrastructure to be deployed
"""

import pytest
import requests
import json
import os
from typing import Dict, Any


class TestClaudeCodeAPI:
    """Integration tests for Claude Code API"""
    
    @pytest.fixture
    def api_base_url(self):
        """API base URL from environment or default"""
        return os.environ.get(
            'API_BASE_URL',
            'https://your-api-id.execute-api.us-east-1.amazonaws.com/prod'
        )
    
    @pytest.mark.skipif(
        not os.environ.get('API_BASE_URL'),
        reason="API_BASE_URL not set - skipping integration test"
    )
    def test_generate_code_endpoint(self, api_base_url):
        """Test code generation endpoint"""
        url = f"{api_base_url}/generate"
        
        payload = {
            "prompt": "Generate a Python function to calculate factorial",
            "language": "python",
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=300
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'code' in data
        assert 'language' in data
        assert data['language'] == 'python'
    
    @pytest.mark.skipif(
        not os.environ.get('API_BASE_URL'),
        reason="API_BASE_URL not set - skipping integration test"
    )
    def test_generate_code_missing_prompt(self, api_base_url):
        """Test code generation with missing prompt"""
        url = f"{api_base_url}/generate"
        
        payload = {
            "language": "python"
        }
        
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        assert response.status_code == 400
        data = response.json()
        assert 'error' in data
    
    @pytest.mark.skipif(
        not os.environ.get('API_BASE_URL'),
        reason="API_BASE_URL not set - skipping integration test"
    )
    def test_health_endpoint(self, api_base_url):
        """Test health check endpoint"""
        url = f"{api_base_url}/health"
        
        response = requests.get(url, timeout=10)
        
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

