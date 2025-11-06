"""
Pytest configuration and shared fixtures
"""

import pytest
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@pytest.fixture(scope="session")
def aws_credentials():
    """Ensure AWS credentials are available"""
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    if not access_key or not secret_key:
        pytest.skip("AWS credentials not configured")
    
    return {
        'access_key_id': access_key,
        'secret_access_key': secret_key,
        'region': os.getenv('AWS_REGION', 'us-east-1')
    }


@pytest.fixture(scope="session")
def bedrock_model_id():
    """Get Bedrock model ID"""
    return os.getenv(
        'BEDROCK_MODEL_ID',
        'anthropic.claude-3-5-sonnet-20241022-v2:0'
    )

