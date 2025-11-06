"""
Generate AWS CDK Infrastructure Code using Claude Code
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from basic_claude_code import ClaudeCodeClient
import json


class InfrastructureCodeGenerator:
    """Generate AWS infrastructure code using Claude Code"""
    
    def __init__(self):
        self.client = ClaudeCodeClient()
    
    def generate_cdk_stack(self, requirements: dict) -> str:
        """
        Generate AWS CDK stack code
        
        Args:
            requirements: Dictionary containing infrastructure requirements
        
        Returns:
            Generated CDK stack code
        """
        prompt = f"""
Create an AWS CDK stack in Python that includes:

1. Lambda Function:
   - Runtime: {requirements.get('lambda_runtime', 'python3.11')}
   - Handler: {requirements.get('lambda_handler', 'handler')}
   - Environment variables: {json.dumps(requirements.get('lambda_env', {}))}
   - Timeout: {requirements.get('lambda_timeout', 300)} seconds
   - Memory: {requirements.get('lambda_memory', 512)} MB

2. API Gateway:
   - REST API endpoint
   - Integration with Lambda function
   - CORS enabled
   - API key authentication (optional)

3. DynamoDB Table:
   - Table name: {requirements.get('table_name', 'default-table')}
   - Partition key: {requirements.get('partition_key', 'id')}
   - Sort key: {requirements.get('sort_key', None)}
   - Billing mode: {requirements.get('billing_mode', 'PAY_PER_REQUEST')}

4. IAM Roles:
   - Lambda execution role with necessary permissions
   - DynamoDB read/write permissions

5. S3 Bucket (if needed):
   - Bucket name: {requirements.get('bucket_name', None)}
   - Versioning: {requirements.get('versioning', False)}

Requirements:
- Use AWS CDK v2
- Include proper imports
- Add comments and documentation
- Include error handling
- Follow AWS CDK best practices
- Export outputs for stack references
"""
        
        result = self.client.generate_code(
            prompt,
            language="python",
            max_tokens=6000
        )
        
        if result['status'] == 'success':
            return result['code']
        else:
            raise Exception(f"Code generation failed: {result['error']}")


def main():
    """Example usage"""
    generator = InfrastructureCodeGenerator()
    
    # Example: Generate CDK stack for a simple API
    requirements = {
        'lambda_runtime': 'python3.11',
        'lambda_handler': 'handler.lambda_handler',
        'lambda_env': {
            'TABLE_NAME': 'users-table',
            'REGION': 'us-east-1'
        },
        'lambda_timeout': 300,
        'lambda_memory': 512,
        'table_name': 'users-table',
        'partition_key': 'user_id',
        'billing_mode': 'PAY_PER_REQUEST'
    }
    
    cdk_code = generator.generate_cdk_stack(requirements)
    
    # Save generated code
    with open('generated_stack.py', 'w') as f:
        f.write(cdk_code)
    
    print("✅ CDK stack generated successfully!")


if __name__ == "__main__":
    main()

