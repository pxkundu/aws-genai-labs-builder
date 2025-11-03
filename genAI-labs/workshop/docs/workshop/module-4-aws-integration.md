# Module 4: AWS Services Integration

## Overview
This module focuses on integrating Claude Code with AWS services. You'll learn how to build applications that use Claude Code with Lambda functions, API Gateway, S3, DynamoDB, and other AWS services.

## Learning Objectives
- Integrate Claude Code with AWS Lambda
- Build API Gateway endpoints with Claude Code
- Use Claude Code with S3 for code storage
- Integrate Claude Code with DynamoDB
- Implement error handling and monitoring
- Optimize AWS service integration

## Prerequisites
- Completed Module 3: Real-World Use Cases
- Understanding of AWS Lambda, API Gateway, S3, DynamoDB
- Basic knowledge of AWS IAM permissions
- Familiarity with AWS SDK (boto3)

## Step 1: Lambda Function Integration

### 1.1 Create Lambda Function with Claude Code
Create `code/examples/aws/lambda_claude_code.py`:

```python
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
```

### 1.2 Create Lambda Deployment Package
Create `code/examples/aws/deploy_lambda.sh`:

```bash
#!/bin/bash
# Deploy Lambda function with Claude Code

# Configuration
FUNCTION_NAME="claude-code-generator"
REGION="us-east-1"
ROLE_ARN="arn:aws:iam::ACCOUNT_ID:role/lambda-bedrock-role"

# Create deployment package
zip -r lambda_function.zip lambda_claude_code.py

# Create or update Lambda function
aws lambda create-function \
  --function-name $FUNCTION_NAME \
  --runtime python3.11 \
  --role $ROLE_ARN \
  --handler lambda_claude_code.lambda_handler \
  --zip-file fileb://lambda_function.zip \
  --environment Variables="{
    AWS_REGION=$REGION,
    BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0,
    TABLE_NAME=claude-code-results
  }" \
  --region $REGION

# Update function code
aws lambda update-function-code \
  --function-name $FUNCTION_NAME \
  --zip-file fileb://lambda_function.zip \
  --region $REGION
```

## Step 2: API Gateway Integration

### 2.1 Create API Gateway with Lambda
Create `code/examples/aws/api_gateway_integration.py`:

```python
"""
API Gateway Integration with Claude Code Lambda
Example: REST API for code generation
"""

import json
import boto3
from typing import Dict, Any

# Initialize Lambda client
lambda_client = boto3.client('lambda', region_name='us-east-1')
apigateway = boto3.client('apigateway', region_name='us-east-1')


def create_api_gateway():
    """Create API Gateway with Lambda integration"""
    
    # Create REST API
    api = apigateway.create_rest_api(
        name='claude-code-api',
        description='API for Claude Code generation',
        endpointConfiguration={
            'types': ['REGIONAL']
        }
    )
    
    api_id = api['id']
    
    # Get root resource ID
    resources = apigateway.get_resources(restApiId=api_id)
    root_id = [r['id'] for r in resources['items'] if r['path'] == '/'][0]
    
    # Create /generate resource
    generate_resource = apigateway.create_resource(
        restApiId=api_id,
        parentId=root_id,
        pathPart='generate'
    )
    
    # Create POST method
    apigateway.put_method(
        restApiId=api_id,
        resourceId=generate_resource['id'],
        httpMethod='POST',
        authorizationType='NONE'
    )
    
    # Create Lambda integration
    lambda_arn = 'arn:aws:lambda:us-east-1:ACCOUNT_ID:function:claude-code-generator'
    
    apigateway.put_integration(
        restApiId=api_id,
        resourceId=generate_resource['id'],
        httpMethod='POST',
        type='AWS_PROXY',
        integrationHttpMethod='POST',
        uri=f'arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{lambda_arn}/invocations'
    )
    
    # Enable CORS
    apigateway.put_method_response(
        restApiId=api_id,
        resourceId=generate_resource['id'],
        httpMethod='POST',
        statusCode='200',
        responseParameters={
            'method.response.header.Access-Control-Allow-Origin': True
        }
    )
    
    # Deploy API
    deployment = apigateway.create_deployment(
        restApiId=api_id,
        stageName='prod',
        description='Production deployment'
    )
    
    return {
        'api_id': api_id,
        'endpoint': f'https://{api_id}.execute-api.us-east-1.amazonaws.com/prod/generate'
    }


if __name__ == "__main__":
    result = create_api_gateway()
    print(f"API Gateway created: {result['endpoint']}")
```

## Step 3: S3 Integration

### 3.1 Store Generated Code in S3
Create `code/examples/aws/s3_integration.py`:

```python
"""
S3 Integration for storing generated code
"""

import boto3
import json
from datetime import datetime
from typing import Dict, Any


class S3CodeStorage:
    """Store and retrieve generated code in S3"""
    
    def __init__(self, bucket_name: str, region: str = 'us-east-1'):
        """Initialize S3 client"""
        self.bucket_name = bucket_name
        self.s3 = boto3.client('s3', region_name=region)
    
    def store_code(
        self,
        code: str,
        language: str,
        prompt: str,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Store generated code in S3
        
        Args:
            code: Generated code
            language: Programming language
            prompt: Original prompt
            metadata: Additional metadata
        
        Returns:
            S3 object key
        """
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        key = f"generated-code/{language}/{timestamp}.py"
        
        # Create metadata
        file_metadata = {
            'language': language,
            'prompt': prompt[:500],  # Truncate if too long
            'generated_at': datetime.utcnow().isoformat(),
            'code_length': len(code),
            **(metadata or {})
        }
        
        # Upload to S3
        self.s3.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=code.encode('utf-8'),
            ContentType='text/plain',
            Metadata=file_metadata
        )
        
        return key
    
    def retrieve_code(self, key: str) -> Dict[str, Any]:
        """
        Retrieve code from S3
        
        Args:
            key: S3 object key
        
        Returns:
            Dictionary with code and metadata
        """
        response = self.s3.get_object(
            Bucket=self.bucket_name,
            Key=key
        )
        
        code = response['Body'].read().decode('utf-8')
        metadata = response.get('Metadata', {})
        
        return {
            'code': code,
            'metadata': metadata,
            'key': key
        }
    
    def list_codes(self, language: str = None, prefix: str = 'generated-code/') -> list:
        """
        List stored code files
        
        Args:
            language: Filter by language
            prefix: S3 prefix
        
        Returns:
            List of code files
        """
        prefix = f"{prefix}{language}/" if language else prefix
        
        response = self.s3.list_objects_v2(
            Bucket=self.bucket_name,
            Prefix=prefix
        )
        
        files = []
        for obj in response.get('Contents', []):
            files.append({
                'key': obj['Key'],
                'size': obj['Size'],
                'last_modified': obj['LastModified'].isoformat()
            })
        
        return files


def main():
    """Example usage"""
    storage = S3CodeStorage(bucket_name='claude-code-workshop')
    
    # Store code
    code = """
def hello_world():
    print("Hello, World!")
"""
    
    key = storage.store_code(
        code=code,
        language='python',
        prompt='Generate a hello world function',
        metadata={'example': 'true'}
    )
    
    print(f"Code stored at: {key}")
    
    # Retrieve code
    result = storage.retrieve_code(key)
    print(f"Retrieved code: {result['code']}")
    
    # List codes
    files = storage.list_codes(language='python')
    print(f"Found {len(files)} Python files")


if __name__ == "__main__":
    main()
```

## Step 4: DynamoDB Integration

### 4.1 Store Results in DynamoDB
Create `code/examples/aws/dynamodb_integration.py`:

```python
"""
DynamoDB Integration for storing Claude Code results
"""

import boto3
import json
from datetime import datetime
from typing import Dict, Any, Optional
from boto3.dynamodb.conditions import Key


class DynamoDBResults:
    """Store and query Claude Code generation results"""
    
    def __init__(self, table_name: str, region: str = 'us-east-1'):
        """Initialize DynamoDB client"""
        self.table_name = table_name
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.table = self.dynamodb.Table(table_name)
    
    def store_result(
        self,
        prompt: str,
        generated_code: str,
        language: str,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Store generation result in DynamoDB
        
        Args:
            prompt: Original prompt
            generated_code: Generated code
            language: Programming language
            metadata: Additional metadata
        
        Returns:
            Result ID
        """
        result_id = f"{datetime.utcnow().timestamp()}"
        
        item = {
            'id': result_id,
            'prompt': prompt[:500],  # Truncate if too long
            'language': language,
            'generated_at': datetime.utcnow().isoformat(),
            'code_length': len(generated_code),
            'metadata': metadata or {}
        }
        
        # Store code in S3 if too large
        if len(generated_code) > 40000:  # DynamoDB item size limit
            s3_key = self._store_code_in_s3(result_id, generated_code)
            item['s3_key'] = s3_key
            item['code'] = None
        else:
            item['code'] = generated_code
        
        self.table.put_item(Item=item)
        
        return result_id
    
    def get_result(self, result_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve result from DynamoDB
        
        Args:
            result_id: Result ID
        
        Returns:
            Result dictionary
        """
        response = self.table.get_item(
            Key={'id': result_id}
        )
        
        item = response.get('Item')
        if not item:
            return None
        
        # Retrieve code from S3 if stored there
        if item.get('s3_key') and not item.get('code'):
            item['code'] = self._retrieve_code_from_s3(item['s3_key'])
        
        return item
    
    def query_by_language(self, language: str, limit: int = 10) -> list:
        """
        Query results by language
        
        Args:
            language: Programming language
            limit: Maximum number of results
        
        Returns:
            List of results
        """
        response = self.table.query(
            IndexName='language-index',  # GSI on language
            KeyConditionExpression=Key('language').eq(language),
            Limit=limit,
            ScanIndexForward=False  # Most recent first
        )
        
        return response.get('Items', [])
    
    def _store_code_in_s3(self, result_id: str, code: str) -> str:
        """Store large code in S3"""
        s3 = boto3.client('s3')
        bucket_name = 'claude-code-workshop'
        key = f"code/{result_id}.py"
        
        s3.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=code.encode('utf-8')
        )
        
        return key
    
    def _retrieve_code_from_s3(self, s3_key: str) -> str:
        """Retrieve code from S3"""
        s3 = boto3.client('s3')
        bucket_name = 'claude-code-workshop'
        
        response = s3.get_object(
            Bucket=bucket_name,
            Key=s3_key
        )
        
        return response['Body'].read().decode('utf-8')


def main():
    """Example usage"""
    results = DynamoDBResults(table_name='claude-code-results')
    
    # Store result
    result_id = results.store_result(
        prompt='Generate a Python function to calculate factorial',
        generated_code='def factorial(n): ...',
        language='python',
        metadata={'example': 'true'}
    )
    
    print(f"Result stored with ID: {result_id}")
    
    # Retrieve result
    result = results.get_result(result_id)
    print(f"Retrieved result: {result['prompt']}")
    
    # Query by language
    python_results = results.query_by_language('python', limit=5)
    print(f"Found {len(python_results)} Python results")


if __name__ == "__main__":
    main()
```

## Step 5: Error Handling and Monitoring

### 5.1 Implement Error Handling
Create `code/examples/aws/error_handling.py`:

```python
"""
Error Handling and Monitoring for Claude Code Integration
"""

import boto3
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize CloudWatch client
cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')


class ClaudeCodeService:
    """Service with error handling and monitoring"""
    
    def __init__(self, model_id: str = None):
        """Initialize service"""
        self.bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.model_id = model_id or 'anthropic.claude-3-5-sonnet-20241022-v2:0'
        self.metrics_namespace = 'ClaudeCode/Workshop'
    
    def generate_code_with_retry(
        self,
        prompt: str,
        language: str = 'python',
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Generate code with retry logic and error handling
        
        Args:
            prompt: Natural language description
            language: Programming language
            max_retries: Maximum retry attempts
        
        Returns:
            Dictionary with result or error
        """
        for attempt in range(max_retries):
            try:
                result = self._generate_code(prompt, language)
                
                # Log success
                self._log_metric('Success', 1)
                logger.info(f"Code generated successfully on attempt {attempt + 1}")
                
                return {
                    'status': 'success',
                    'code': result,
                    'attempts': attempt + 1
                }
                
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                
                if attempt == max_retries - 1:
                    # Log failure
                    self._log_metric('Failure', 1)
                    
                    return {
                        'status': 'error',
                        'error': str(e),
                        'attempts': attempt + 1
                    }
                
                # Wait before retry (exponential backoff)
                import time
                time.sleep(2 ** attempt)
    
    def _generate_code(self, prompt: str, language: str) -> str:
        """Internal code generation method"""
        try:
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    'anthropic_version': 'bedrock-2023-05-31',
                    'max_tokens': 4000,
                    'messages': [{
                        'role': 'user',
                        'content': f'Generate {language} code: {prompt}'
                    }]
                })
            )
            
            result = json.loads(response['body'].read())
            return result['content'][0]['text']
            
        except Exception as e:
            logger.error(f"Code generation failed: {str(e)}")
            raise
    
    def _log_metric(self, metric_name: str, value: float):
        """Log custom metric to CloudWatch"""
        try:
            cloudwatch.put_metric_data(
                Namespace=self.metrics_namespace,
                MetricData=[{
                    'MetricName': metric_name,
                    'Value': value,
                    'Timestamp': datetime.utcnow(),
                    'Unit': 'Count'
                }]
            )
        except Exception as e:
            logger.warning(f"Failed to log metric: {str(e)}")


def main():
    """Example usage"""
    service = ClaudeCodeService()
    
    result = service.generate_code_with_retry(
        prompt='Generate a Python function to calculate factorial',
        language='python'
    )
    
    if result['status'] == 'success':
        print(f"✅ Code generated successfully in {result['attempts']} attempt(s)")
        print(result['code'])
    else:
        print(f"❌ Code generation failed: {result['error']}")


if __name__ == "__main__":
    main()
```

## Step 6: Exercises

### Exercise 1: Lambda Function
Create a Lambda function that generates code using Claude Code and stores results in DynamoDB.

### Exercise 2: API Gateway
Create an API Gateway endpoint that triggers the Lambda function for code generation.

### Exercise 3: S3 Storage
Create a service that stores generated code in S3 with metadata and retrieval capabilities.

### Exercise 4: Monitoring
Add CloudWatch metrics and logging to your Claude Code integration.

## Troubleshooting

### Common Issues

#### Lambda Timeout
- Increase Lambda timeout (max 15 minutes)
- Optimize code generation prompts
- Use streaming for large responses

#### API Gateway Errors
- Check Lambda permissions
- Verify integration configuration
- Review CORS settings

#### DynamoDB Errors
- Check item size limits (400KB)
- Use S3 for large code storage
- Verify IAM permissions

#### Cost Optimization
- Use appropriate model (Haiku for simple tasks)
- Implement caching for repeated requests
- Monitor usage with CloudWatch

## Next Steps

✅ **Module 4 Complete!**

You have successfully:
- Integrated Claude Code with Lambda
- Created API Gateway endpoints
- Integrated with S3 and DynamoDB
- Implemented error handling and monitoring

**Ready for [Module 5: Infrastructure Deployment](./module-5-infrastructure.md)?**

## Additional Resources

- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [S3 Documentation](https://docs.aws.amazon.com/s3/)
- [DynamoDB Documentation](https://docs.aws.amazon.com/dynamodb/)
- [CloudWatch Documentation](https://docs.aws.amazon.com/cloudwatch/)

