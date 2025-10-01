import pytest
import json
from unittest.mock import Mock, patch
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from main import app

@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_aws_clients():
    """Mock AWS clients"""
    with patch('main.dynamodb') as mock_dynamodb, \
         patch('main.s3') as mock_s3:
        
        # Mock DynamoDB table
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        
        # Mock S3 client
        mock_s3_client = Mock()
        mock_s3.return_value = mock_s3_client
        
        yield {
            'dynamodb': mock_dynamodb,
            's3': mock_s3,
            'table': mock_table,
            's3_client': mock_s3_client
        }

class TestHealthEndpoint:
    """Test the health check endpoint"""
    
    def test_health_check_success(self, client):
        """Test successful health check"""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert data['environment'] == 'development'

class TestWebhookHandler:
    """Test the webhook handler"""
    
    def test_webhook_push_event(self, client, mock_aws_clients):
        """Test webhook handling for push events"""
        payload = {
            'repository': {
                'id': '12345',
                'name': 'test-repo'
            },
            'commits': [
                {
                    'id': 'abc123',
                    'message': 'Test commit',
                    'author': {'name': 'Test Author'},
                    'timestamp': '2023-01-01T00:00:00Z'
                }
            ]
        }
        
        headers = {'X-GitHub-Event': 'push'}
        
        response = client.post('/webhook', 
                             json=payload, 
                             headers=headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['message'] == 'Push event processed successfully'
        assert data['repository'] == 'test-repo'
        assert data['commits_count'] == 1
        
        # Verify DynamoDB put_item was called
        mock_aws_clients['table'].put_item.assert_called_once()
        
        # Verify S3 put_object was called
        mock_aws_clients['s3_client'].put_object.assert_called_once()
    
    def test_webhook_pull_request_event(self, client, mock_aws_clients):
        """Test webhook handling for pull request events"""
        payload = {
            'action': 'opened',
            'pull_request': {
                'number': 123
            }
        }
        
        headers = {'X-GitHub-Event': 'pull_request'}
        
        response = client.post('/webhook', 
                             json=payload, 
                             headers=headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['message'] == 'Pull request event processed successfully'
        assert data['pr_number'] == 123
        assert data['action'] == 'opened'
    
    def test_webhook_unsupported_event(self, client, mock_aws_clients):
        """Test webhook handling for unsupported events"""
        payload = {'test': 'data'}
        headers = {'X-GitHub-Event': 'unsupported'}
        
        response = client.post('/webhook', 
                             json=payload, 
                             headers=headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['message'] == 'Event type not supported'
    
    def test_webhook_error_handling(self, client, mock_aws_clients):
        """Test webhook error handling"""
        # Make DynamoDB put_item raise an exception
        mock_aws_clients['table'].put_item.side_effect = Exception('DynamoDB error')
        
        payload = {
            'repository': {'id': '12345', 'name': 'test-repo'},
            'commits': []
        }
        headers = {'X-GitHub-Event': 'push'}
        
        response = client.post('/webhook', 
                             json=payload, 
                             headers=headers)
        
        assert response.status_code == 500
        data = json.loads(response.data)
        
        assert 'error' in data
        assert data['error'] == 'Internal server error'

class TestLogWebhookEvent:
    """Test webhook event logging"""
    
    def test_log_webhook_event_success(self, mock_aws_clients):
        """Test successful webhook event logging"""
        from main import log_webhook_event
        
        payload = {
            'repository': {'id': '12345', 'name': 'test-repo'}
        }
        
        # Mock request headers
        with patch('main.request') as mock_request:
            mock_request.headers.get.return_value = 'push'
            
            log_webhook_event(payload)
            
            # Verify DynamoDB put_item was called with correct data
            mock_aws_clients['table'].put_item.assert_called_once()
            
            call_args = mock_aws_clients['table'].put_item.call_args[1]['Item']
            assert call_args['event_id'] == '12345'
            assert call_args['event_type'] == 'push'
            assert 'payload' in call_args
            assert 'ttl' in call_args

class TestStoreArtifacts:
    """Test artifact storage"""
    
    def test_store_artifacts_success(self, mock_aws_clients):
        """Test successful artifact storage"""
        from main import store_artifacts
        
        repository = {'name': 'test-repo'}
        commits = [
            {
                'id': 'abc123',
                'message': 'Test commit',
                'author': {'name': 'Test Author'},
                'timestamp': '2023-01-01T00:00:00Z'
            }
        ]
        
        store_artifacts(repository, commits)
        
        # Verify S3 put_object was called
        mock_aws_clients['s3_client'].put_object.assert_called_once()
        
        call_args = mock_aws_clients['s3_client'].put_object.call_args[1]
        assert call_args['Bucket'] == 'github-actions-artifacts'
        assert call_args['Key'] == 'test-repo/abc123/metadata.json'
        assert call_args['ContentType'] == 'application/json'
        
        # Verify the artifact data
        artifact_data = json.loads(call_args['Body'])
        assert artifact_data['repository'] == 'test-repo'
        assert artifact_data['commit_id'] == 'abc123'
        assert artifact_data['message'] == 'Test commit'
        assert artifact_data['author'] == 'Test Author'

if __name__ == '__main__':
    pytest.main([__file__])
