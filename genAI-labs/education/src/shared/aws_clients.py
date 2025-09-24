"""
AWS service clients for the learning platform.
"""

import boto3
import logging
from typing import Dict, Any, Optional
from botocore.config import Config

logger = logging.getLogger(__name__)

# Global clients cache
_aws_clients: Dict[str, Any] = {}


def get_aws_clients(region: str = "us-east-1", config: Optional[Config] = None) -> Dict[str, Any]:
    """
    Get AWS service clients with caching.
    
    Args:
        region: AWS region
        config: Botocore configuration
        
    Returns:
        Dictionary of AWS service clients
    """
    global _aws_clients
    
    # Use default config if none provided
    if config is None:
        config = Config(
            retries={'max_attempts': 3, 'mode': 'adaptive'},
            max_pool_connections=50
        )
    
    # Create cache key
    cache_key = f"{region}_{hash(str(config))}"
    
    if cache_key not in _aws_clients:
        try:
            _aws_clients[cache_key] = {
                "bedrock": boto3.client('bedrock-runtime', region_name=region, config=config),
                "sagemaker": boto3.client('sagemaker-runtime', region_name=region, config=config),
                "comprehend": boto3.client('comprehend', region_name=region, config=config),
                "polly": boto3.client('polly', region_name=region, config=config),
                "translate": boto3.client('translate', region_name=region, config=config),
                "textract": boto3.client('textract', region_name=region, config=config),
                "dynamodb": boto3.resource('dynamodb', region_name=region, config=config),
                "s3": boto3.client('s3', region_name=region, config=config),
                "lambda": boto3.client('lambda', region_name=region, config=config),
                "apigateway": boto3.client('apigateway', region_name=region, config=config),
                "cloudwatch": boto3.client('cloudwatch', region_name=region, config=config),
                "logs": boto3.client('logs', region_name=region, config=config)
            }
            logger.info(f"AWS clients initialized for region: {region}")
            
        except Exception as e:
            logger.error(f"Failed to initialize AWS clients: {str(e)}")
            raise
    
    return _aws_clients[cache_key]


def get_bedrock_client(region: str = "us-east-1") -> Any:
    """Get Bedrock client."""
    clients = get_aws_clients(region)
    return clients["bedrock"]


def get_sagemaker_client(region: str = "us-east-1") -> Any:
    """Get SageMaker client."""
    clients = get_aws_clients(region)
    return clients["sagemaker"]


def get_comprehend_client(region: str = "us-east-1") -> Any:
    """Get Comprehend client."""
    clients = get_aws_clients(region)
    return clients["comprehend"]


def get_polly_client(region: str = "us-east-1") -> Any:
    """Get Polly client."""
    clients = get_aws_clients(region)
    return clients["polly"]


def get_translate_client(region: str = "us-east-1") -> Any:
    """Get Translate client."""
    clients = get_aws_clients(region)
    return clients["translate"]


def get_textract_client(region: str = "us-east-1") -> Any:
    """Get Textract client."""
    clients = get_aws_clients(region)
    return clients["textract"]


def get_dynamodb_resource(region: str = "us-east-1") -> Any:
    """Get DynamoDB resource."""
    clients = get_aws_clients(region)
    return clients["dynamodb"]


def get_s3_client(region: str = "us-east-1") -> Any:
    """Get S3 client."""
    clients = get_aws_clients(region)
    return clients["s3"]


def get_lambda_client(region: str = "us-east-1") -> Any:
    """Get Lambda client."""
    clients = get_aws_clients(region)
    return clients["lambda"]


def get_apigateway_client(region: str = "us-east-1") -> Any:
    """Get API Gateway client."""
    clients = get_aws_clients(region)
    return clients["apigateway"]


def get_cloudwatch_client(region: str = "us-east-1") -> Any:
    """Get CloudWatch client."""
    clients = get_aws_clients(region)
    return clients["cloudwatch"]


def get_logs_client(region: str = "us-east-1") -> Any:
    """Get CloudWatch Logs client."""
    clients = get_aws_clients(region)
    return clients["logs"]


def clear_aws_clients_cache():
    """Clear the AWS clients cache."""
    global _aws_clients
    _aws_clients.clear()
    logger.info("AWS clients cache cleared")
