"""
Lambda Function with Claude Code Integration
Example: Code generation Lambda function
"""

import json
import boto3
import os
from typing import Dict, Any
from datetime import datetime

# Initialize Bedrock client
bedrock = boto3.client(
    'bedrock-runtime',
    region_name=os.environ.get('AWS_REGION', 'us-east-1')
)

# Initialize DynamoDB client (optional, for storing results)
dynamodb = boto3.client('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-1'))


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for Claude Code generation
    
    Args:
        event: Lambda event containing request data
        context: Lambda context
    
    Returns:
        Response dictionary with generated code
    """
    try:
        # Parse request
        body = json.loads(event.get('body', '{}'))
        prompt = body.get('prompt', '')
        language = body.get('language', 'python')
        max_tokens = body.get('max_tokens', 4000)
        temperature = body.get('temperature', 0.7)
        
        if not prompt:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Missing required parameter: prompt'
                })
            }
        
        # Generate code using Claude Code
        generated_code = generate_code(
            prompt=prompt,
            language=language,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        # Store result in DynamoDB (optional)
        if os.environ.get('TABLE_NAME'):
            store_result(
                prompt=prompt,
                generated_code=generated_code,
                language=language
            )
        
        # Return response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'code': generated_code,
                'language': language,
                'generated_at': datetime.utcnow().isoformat()
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }


def generate_code(
    prompt: str,
    language: str = 'python',
    max_tokens: int = 4000,
    temperature: float = 0.7
) -> str:
    """
    Generate code using Claude Code via Bedrock
    
    Args:
        prompt: Natural language description
        language: Programming language
        max_tokens: Maximum tokens in response
        temperature: Sampling temperature
    
    Returns:
        Generated code
    """
    model_id = os.environ.get(
        'BEDROCK_MODEL_ID',
        'anthropic.claude-3-5-sonnet-20241022-v2:0'
    )
    
    system_prompt = f"""You are an expert {language} developer. 
Generate clean, well-documented, and production-ready code based on user requirements.
Follow best practices and include appropriate error handling."""
    
    user_prompt = f"""Generate {language} code for the following requirement:

{prompt}

Requirements:
1. Include proper error handling
2. Add docstrings and comments
3. Follow {language} best practices
4. Make the code production-ready"""
    
    try:
        response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': max_tokens,
                'temperature': temperature,
                'system': system_prompt,
                'messages': [{
                    'role': 'user',
                    'content': user_prompt
                }]
            })
        )
        
        result = json.loads(response['body'].read())
        generated_code = result['content'][0]['text']
        
        return generated_code
        
    except Exception as e:
        raise Exception(f"Code generation failed: {str(e)}")


def store_result(prompt: str, generated_code: str, language: str):
    """Store generation result in DynamoDB"""
    try:
        table_name = os.environ.get('TABLE_NAME')
        if not table_name:
            return
        
        item = {
            'id': {'S': f"{datetime.utcnow().isoformat()}"},
            'prompt': {'S': prompt[:500]},  # Truncate if too long
            'language': {'S': language},
            'generated_at': {'S': datetime.utcnow().isoformat()},
            'code_length': {'N': str(len(generated_code))}
        }
        
        dynamodb.put_item(
            TableName=table_name,
            Item=item
        )
        
    except Exception as e:
        print(f"Failed to store result: {str(e)}")
        # Don't fail the request if storage fails

