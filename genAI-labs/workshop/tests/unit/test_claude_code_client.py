"""
Unit tests for Claude Code Client
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../code/examples'))
from basic_claude_code import ClaudeCodeClient


class TestClaudeCodeClient:
    """Unit tests for ClaudeCodeClient"""
    
    @pytest.fixture
    def client(self):
        """Create ClaudeCodeClient instance"""
        return ClaudeCodeClient()
    
    @patch('code.examples.basic_claude_code.boto3.client')
    def test_generate_code_success(self, mock_boto3, client):
        """Test successful code generation"""
        # Mock Bedrock response
        mock_response = {
            'body': MagicMock(read=lambda: b'{"content":[{"text":"def hello():\\n    print(\\"Hello\\")"}],"usage":{"input_tokens":10,"output_tokens":20}}')
        }
        
        mock_bedrock = Mock()
        mock_bedrock.invoke_model.return_value = mock_response
        mock_boto3.return_value = mock_bedrock
        
        result = client.generate_code(
            prompt="Generate a hello world function",
            language="python"
        )
        
        assert result['status'] == 'success'
        assert 'def hello()' in result['code']
        mock_bedrock.invoke_model.assert_called_once()
    
    @patch('code.examples.basic_claude_code.boto3.client')
    def test_generate_code_error(self, mock_boto3, client):
        """Test code generation error handling"""
        # Mock Bedrock error
        mock_bedrock = Mock()
        mock_bedrock.invoke_model.side_effect = Exception("Bedrock error")
        mock_boto3.return_value = mock_bedrock
        
        result = client.generate_code(
            prompt="Generate a hello world function",
            language="python"
        )
        
        assert result['status'] == 'error'
        assert 'error' in result
    
    @patch('code.examples.basic_claude_code.boto3.client')
    def test_refactor_code_success(self, mock_boto3, client):
        """Test successful code refactoring"""
        original_code = "def add(a,b): return a+b"
        
        mock_response = {
            'body': MagicMock(read=lambda: b'{"content":[{"text":"def add(a: int, b: int) -> int:\\n    return a + b"}]}')
        }
        
        mock_bedrock = Mock()
        mock_bedrock.invoke_model.return_value = mock_response
        mock_boto3.return_value = mock_bedrock
        
        result = client.refactor_code(
            code=original_code,
            instructions="Add type hints",
            language="python"
        )
        
        assert result['status'] == 'success'
        assert 'refactored_code' in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

