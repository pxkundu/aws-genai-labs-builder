import os
import json
import boto3
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_REGION', 'us-east-1'))
s3 = boto3.client('s3', region_name=os.getenv('AWS_REGION', 'us-east-1'))

# Environment variables
TABLE_NAME = os.getenv('DYNAMODB_TABLE', 'github-actions-logs')
S3_BUCKET = os.getenv('S3_BUCKET', 'github-actions-artifacts')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'environment': os.getenv('ENVIRONMENT', 'development')
    })

@app.route('/webhook', methods=['POST'])
def webhook_handler():
    """Handle GitHub webhook events"""
    try:
        payload = request.get_json()
        
        # Log the webhook event
        log_webhook_event(payload)
        
        # Process the event based on type
        event_type = request.headers.get('X-GitHub-Event')
        
        if event_type == 'push':
            return handle_push_event(payload)
        elif event_type == 'pull_request':
            return handle_pull_request_event(payload)
        else:
            return jsonify({'message': 'Event type not supported'}), 200
            
    except Exception as e:
        app.logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

def log_webhook_event(payload):
    """Log webhook event to DynamoDB"""
    try:
        table = dynamodb.Table(TABLE_NAME)
        
        item = {
            'event_id': payload.get('repository', {}).get('id', 'unknown'),
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': request.headers.get('X-GitHub-Event', 'unknown'),
            'payload': json.dumps(payload),
            'ttl': int(datetime.utcnow().timestamp()) + 86400  # 24 hours TTL
        }
        
        table.put_item(Item=item)
        
    except Exception as e:
        app.logger.error(f"Error logging webhook event: {str(e)}")

def handle_push_event(payload):
    """Handle push events"""
    repository = payload.get('repository', {})
    commits = payload.get('commits', [])
    
    # Store artifacts in S3
    store_artifacts(repository, commits)
    
    return jsonify({
        'message': 'Push event processed successfully',
        'repository': repository.get('name'),
        'commits_count': len(commits)
    })

def handle_pull_request_event(payload):
    """Handle pull request events"""
    pr = payload.get('pull_request', {})
    
    return jsonify({
        'message': 'Pull request event processed successfully',
        'pr_number': pr.get('number'),
        'action': payload.get('action')
    })

def store_artifacts(repository, commits):
    """Store commit artifacts in S3"""
    try:
        for commit in commits:
            artifact_key = f"{repository.get('name')}/{commit.get('id')}/metadata.json"
            
            artifact_data = {
                'repository': repository.get('name'),
                'commit_id': commit.get('id'),
                'message': commit.get('message'),
                'author': commit.get('author', {}).get('name'),
                'timestamp': commit.get('timestamp')
            }
            
            s3.put_object(
                Bucket=S3_BUCKET,
                Key=artifact_key,
                Body=json.dumps(artifact_data, indent=2),
                ContentType='application/json'
            )
            
    except Exception as e:
        app.logger.error(f"Error storing artifacts: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=os.getenv('DEBUG', 'False').lower() == 'true')
