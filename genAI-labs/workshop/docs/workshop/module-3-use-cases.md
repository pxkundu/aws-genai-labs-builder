# Module 3: Real-World Use Cases

## Overview
This module focuses on practical, real-world applications of Claude Code. You'll learn how to use Claude Code to solve common development challenges, automate repetitive tasks, and build production-ready applications.

## Learning Objectives
- Apply Claude Code to real-world development scenarios
- Generate AWS infrastructure code (CDK/Terraform)
- Create API integration code
- Generate database schemas and migrations
- Build test suites and documentation
- Automate common development tasks

## Prerequisites
- Completed Module 2: Claude Code Basics
- Understanding of AWS services
- Basic knowledge of Infrastructure as Code
- Familiarity with REST APIs

## Step 1: AWS Infrastructure Code Generation

### 1.1 Generate AWS CDK Code
Create `code/examples/infrastructure/cdk_generator.py`:

```python
"""
Generate AWS CDK Infrastructure Code using Claude Code
"""

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
    
    def generate_terraform_config(self, requirements: dict) -> str:
        """
        Generate Terraform configuration
        
        Args:
            requirements: Dictionary containing infrastructure requirements
        
        Returns:
            Generated Terraform configuration
        """
        prompt = f"""
Create a Terraform configuration that includes:

1. AWS Lambda Function:
   - Runtime: {requirements.get('lambda_runtime', 'python3.11')}
   - Handler: {requirements.get('lambda_handler', 'handler')}
   - Environment variables: {json.dumps(requirements.get('lambda_env', {}))}
   - Timeout: {requirements.get('lambda_timeout', 300)} seconds
   - Memory: {requirements.get('lambda_memory', 512)} MB

2. API Gateway:
   - REST API endpoint
   - Integration with Lambda function
   - CORS enabled

3. DynamoDB Table:
   - Table name: {requirements.get('table_name', 'default-table')}
   - Partition key: {requirements.get('partition_key', 'id')}
   - Billing mode: {requirements.get('billing_mode', 'PAY_PER_REQUEST')}

4. IAM Roles and Policies:
   - Lambda execution role
   - DynamoDB permissions

Requirements:
- Use Terraform AWS provider
- Include variable definitions
- Add outputs
- Follow Terraform best practices
- Include proper resource naming
"""
        
        result = self.client.generate_code(
            prompt,
            language="hcl",
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
```

### 1.2 Generate Terraform Configuration
Create `code/examples/infrastructure/terraform_generator.py`:

```python
"""
Generate Terraform Infrastructure Code using Claude Code
"""

from basic_claude_code import ClaudeCodeClient


class TerraformGenerator:
    """Generate Terraform configurations"""
    
    def __init__(self):
        self.client = ClaudeCodeClient()
    
    def generate_terraform(self, resources: list) -> str:
        """
        Generate Terraform configuration for resources
        
        Args:
            resources: List of resource types to include
        
        Returns:
            Generated Terraform configuration
        """
        prompt = f"""
Create a Terraform configuration that includes:
{', '.join(resources)}

Requirements:
- Use Terraform AWS provider
- Include provider configuration
- Add variable definitions
- Include outputs
- Follow Terraform best practices
- Use proper resource naming conventions
"""
        
        result = self.client.generate_code(
            prompt,
            language="hcl",
            max_tokens=6000
        )
        
        if result['status'] == 'success':
            return result['code']
        else:
            raise Exception(f"Code generation failed: {result['error']}")


if __name__ == "__main__":
    generator = TerraformGenerator()
    resources = [
        "Lambda function",
        "API Gateway",
        "DynamoDB table",
        "IAM roles and policies"
    ]
    
    terraform_code = generator.generate_terraform(resources)
    
    with open('generated_terraform.tf', 'w') as f:
        f.write(terraform_code)
    
    print("✅ Terraform configuration generated successfully!")
```

## Step 2: API Integration Code Generation

### 2.1 Generate REST API Client
Create `code/examples/api/api_client_generator.py`:

```python
"""
Generate API Client Code using Claude Code
"""

from basic_claude_code import ClaudeCodeClient
import json


class APIClientGenerator:
    """Generate API client code"""
    
    def __init__(self):
        self.client = ClaudeCodeClient()
    
    def generate_client(self, api_spec: dict) -> str:
        """
        Generate API client from specification
        
        Args:
            api_spec: API specification dictionary
        
        Returns:
            Generated API client code
        """
        prompt = f"""
Create a Python REST API client class that:

1. Base Configuration:
   - Base URL: {api_spec.get('base_url', 'https://api.example.com')}
   - API Key authentication: {api_spec.get('api_key', True)}
   - Timeout: {api_spec.get('timeout', 30)} seconds
   - Retry logic with exponential backoff

2. Endpoints:
{self._format_endpoints(api_spec.get('endpoints', []))}

3. Features:
   - Request/response logging
   - Error handling (HTTP errors, network errors)
   - Response validation
   - Type hints
   - Async support (optional)
   - Rate limiting (optional)

4. Requirements:
   - Use requests library (or httpx for async)
   - Include proper error handling
   - Add docstrings for all methods
   - Include example usage
   - Follow Python best practices
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
    
    def _format_endpoints(self, endpoints: list) -> str:
        """Format endpoints for prompt"""
        formatted = []
        for endpoint in endpoints:
            formatted.append(f"   - {endpoint.get('method', 'GET')} {endpoint.get('path', '/')}: {endpoint.get('description', '')}")
        return '\n'.join(formatted)


def main():
    """Example usage"""
    generator = APIClientGenerator()
    
    # Example API specification
    api_spec = {
        'base_url': 'https://api.example.com/v1',
        'api_key': True,
        'timeout': 30,
        'endpoints': [
            {
                'method': 'GET',
                'path': '/users',
                'description': 'Get list of users'
            },
            {
                'method': 'POST',
                'path': '/users',
                'description': 'Create a new user'
            },
            {
                'method': 'GET',
                'path': '/users/{id}',
                'description': 'Get user by ID'
            },
            {
                'method': 'PUT',
                'path': '/users/{id}',
                'description': 'Update user by ID'
            },
            {
                'method': 'DELETE',
                'path': '/users/{id}',
                'description': 'Delete user by ID'
            }
        ]
    }
    
    client_code = generator.generate_client(api_spec)
    
    with open('generated_api_client.py', 'w') as f:
        f.write(client_code)
    
    print("✅ API client generated successfully!")


if __name__ == "__main__":
    main()
```

### 2.2 Generate FastAPI Endpoints
Create `code/examples/api/fastapi_generator.py`:

```python
"""
Generate FastAPI Endpoints using Claude Code
"""

from basic_claude_code import ClaudeCodeClient
import json


class FastAPIGenerator:
    """Generate FastAPI endpoint code"""
    
    def __init__(self):
        self.client = ClaudeCodeClient()
    
    def generate_endpoints(self, endpoints: list) -> str:
        """
        Generate FastAPI endpoints
        
        Args:
            endpoints: List of endpoint specifications
        
        Returns:
            Generated FastAPI code
        """
        prompt = f"""
Create FastAPI endpoints for the following:

Endpoints:
{self._format_endpoints(endpoints)}

Requirements:
- Use FastAPI framework
- Include Pydantic models for request/response
- Add proper error handling
- Include authentication (JWT or API key)
- Add request validation
- Include response models
- Add docstrings and OpenAPI documentation
- Follow FastAPI best practices
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
    
    def _format_endpoints(self, endpoints: list) -> str:
        """Format endpoints for prompt"""
        formatted = []
        for endpoint in endpoints:
            formatted.append(f"   - {endpoint.get('method', 'GET')} {endpoint.get('path', '/')}: {endpoint.get('description', '')}")
            if endpoint.get('request_body'):
                formatted.append(f"     Request: {json.dumps(endpoint.get('request_body'))}")
            if endpoint.get('response_body'):
                formatted.append(f"     Response: {json.dumps(endpoint.get('response_body'))}")
        return '\n'.join(formatted)


def main():
    """Example usage"""
    generator = FastAPIGenerator()
    
    endpoints = [
        {
            'method': 'POST',
            'path': '/users',
            'description': 'Create a new user',
            'request_body': {
                'name': 'string',
                'email': 'string',
                'password': 'string'
            },
            'response_body': {
                'id': 'string',
                'name': 'string',
                'email': 'string',
                'created_at': 'datetime'
            }
        },
        {
            'method': 'GET',
            'path': '/users/{user_id}',
            'description': 'Get user by ID',
            'response_body': {
                'id': 'string',
                'name': 'string',
                'email': 'string'
            }
        }
    ]
    
    api_code = generator.generate_endpoints(endpoints)
    
    with open('generated_fastapi.py', 'w') as f:
        f.write(api_code)
    
    print("✅ FastAPI endpoints generated successfully!")


if __name__ == "__main__":
    main()
```

## Step 3: Database Schema Generation

### 3.1 Generate Database Schema
Create `code/examples/database/schema_generator.py`:

```python
"""
Generate Database Schema Code using Claude Code
"""

from basic_claude_code import ClaudeCodeClient
import json


class SchemaGenerator:
    """Generate database schema code"""
    
    def __init__(self):
        self.client = ClaudeCodeClient()
    
    def generate_schema(self, tables: list, db_type: str = 'dynamodb') -> str:
        """
        Generate database schema
        
        Args:
            tables: List of table specifications
            db_type: Database type (dynamodb, postgresql, mysql)
        
        Returns:
            Generated schema code
        """
        if db_type == 'dynamodb':
            return self._generate_dynamodb_schema(tables)
        elif db_type in ['postgresql', 'mysql']:
            return self._generate_sql_schema(tables, db_type)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    def _generate_dynamodb_schema(self, tables: list) -> str:
        """Generate DynamoDB schema"""
        prompt = f"""
Create AWS CDK code to define DynamoDB tables with the following specifications:

Tables:
{self._format_tables(tables)}

Requirements:
- Use AWS CDK DynamoDB constructs
- Include proper partition keys and sort keys
- Add GSI (Global Secondary Index) where needed
- Include billing mode configuration
- Add encryption configuration
- Include point-in-time recovery
- Add proper IAM permissions
- Follow AWS CDK best practices
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
    
    def _generate_sql_schema(self, tables: list, db_type: str) -> str:
        """Generate SQL schema"""
        prompt = f"""
Create {db_type.upper()} SQL schema for the following tables:

Tables:
{self._format_tables(tables)}

Requirements:
- Include CREATE TABLE statements
- Add proper primary keys and foreign keys
- Include indexes for frequently queried columns
- Add constraints (NOT NULL, UNIQUE, CHECK)
- Include appropriate data types
- Add comments for documentation
- Follow SQL best practices
"""
        
        result = self.client.generate_code(
            prompt,
            language="sql",
            max_tokens=6000
        )
        
        if result['status'] == 'success':
            return result['code']
        else:
            raise Exception(f"Code generation failed: {result['error']}")
    
    def _format_tables(self, tables: list) -> str:
        """Format tables for prompt"""
        formatted = []
        for table in tables:
            formatted.append(f"   - {table.get('name', 'table')}:")
            formatted.append(f"     Description: {table.get('description', '')}")
            formatted.append(f"     Fields: {json.dumps(table.get('fields', []))}")
            if table.get('indexes'):
                formatted.append(f"     Indexes: {json.dumps(table.get('indexes', []))}")
        return '\n'.join(formatted)


def main():
    """Example usage"""
    generator = SchemaGenerator()
    
    tables = [
        {
            'name': 'users',
            'description': 'User accounts table',
            'fields': [
                {'name': 'user_id', 'type': 'string', 'primary_key': True},
                {'name': 'email', 'type': 'string', 'unique': True},
                {'name': 'name', 'type': 'string'},
                {'name': 'created_at', 'type': 'datetime'},
                {'name': 'updated_at', 'type': 'datetime'}
            ],
            'indexes': [
                {'name': 'email-index', 'fields': ['email']}
            ]
        },
        {
            'name': 'orders',
            'description': 'Customer orders table',
            'fields': [
                {'name': 'order_id', 'type': 'string', 'primary_key': True},
                {'name': 'user_id', 'type': 'string', 'foreign_key': 'users.user_id'},
                {'name': 'total', 'type': 'decimal'},
                {'name': 'status', 'type': 'string'},
                {'name': 'created_at', 'type': 'datetime'}
            ]
        }
    ]
    
    # Generate DynamoDB schema
    dynamodb_schema = generator.generate_schema(tables, 'dynamodb')
    with open('generated_dynamodb_schema.py', 'w') as f:
        f.write(dynamodb_schema)
    
    # Generate PostgreSQL schema
    postgresql_schema = generator.generate_schema(tables, 'postgresql')
    with open('generated_postgresql_schema.sql', 'w') as f:
        f.write(postgresql_schema)
    
    print("✅ Database schemas generated successfully!")


if __name__ == "__main__":
    main()
```

## Step 4: Test Generation

### 4.1 Generate Unit Tests
Create `code/examples/testing/test_generator.py`:

```python
"""
Generate Test Code using Claude Code
"""

from basic_claude_code import ClaudeCodeClient


class TestGenerator:
    """Generate test code"""
    
    def __init__(self):
        self.client = ClaudeCodeClient()
    
    def generate_tests(self, code: str, test_framework: str = 'pytest') -> str:
        """
        Generate unit tests for code
        
        Args:
            code: Source code to test
            test_framework: Test framework (pytest, unittest)
        
        Returns:
            Generated test code
        """
        prompt = f"""
Create comprehensive {test_framework} unit tests for the following code:

```python
{code}
```

Requirements:
- Test all functions/methods
- Include edge cases
- Test error conditions
- Include positive and negative test cases
- Use fixtures where appropriate
- Achieve at least 80% code coverage
- Follow {test_framework} best practices
- Include proper test organization
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
    generator = TestGenerator()
    
    # Example code to test
    code = """
def calculate_factorial(n):
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
"""
    
    test_code = generator.generate_tests(code, 'pytest')
    
    with open('generated_tests.py', 'w') as f:
        f.write(test_code)
    
    print("✅ Test code generated successfully!")


if __name__ == "__main__":
    main()
```

## Step 5: Documentation Generation

### 5.1 Generate README
Create `code/examples/documentation/doc_generator.py`:

```python
"""
Generate Documentation using Claude Code
"""

from basic_claude_code import ClaudeCodeClient


class DocumentationGenerator:
    """Generate documentation"""
    
    def __init__(self):
        self.client = ClaudeCodeClient()
    
    def generate_readme(self, project_info: dict) -> str:
        """
        Generate README.md
        
        Args:
            project_info: Project information dictionary
        
        Returns:
            Generated README content
        """
        prompt = f"""
Create a comprehensive README.md file for the following project:

Project Name: {project_info.get('name', 'Project')}
Description: {project_info.get('description', '')}
Features: {', '.join(project_info.get('features', []))}
Technologies: {', '.join(project_info.get('technologies', []))}
Installation Steps: {project_info.get('installation', '')}
Usage: {project_info.get('usage', '')}

Requirements:
- Include project title and description
- Add installation instructions
- Include usage examples
- Add API documentation
- Include contributing guidelines
- Add license information
- Follow Markdown best practices
- Make it comprehensive and professional
"""
        
        result = self.client.generate_code(
            prompt,
            language="markdown",
            max_tokens=4000
        )
        
        if result['status'] == 'success':
            return result['code']
        else:
            raise Exception(f"Code generation failed: {result['error']}")


def main():
    """Example usage"""
    generator = DocumentationGenerator()
    
    project_info = {
        'name': 'Claude Code Workshop',
        'description': 'A workshop for learning Claude Code on AWS',
        'features': [
            'Code generation',
            'API integration',
            'Infrastructure as Code',
            'Test generation'
        ],
        'technologies': [
            'Python',
            'AWS Bedrock',
            'Claude Code',
            'FastAPI'
        ],
        'installation': 'pip install -r requirements.txt',
        'usage': 'python main.py'
    }
    
    readme = generator.generate_readme(project_info)
    
    with open('generated_README.md', 'w') as f:
        f.write(readme)
    
    print("✅ README generated successfully!")


if __name__ == "__main__":
    main()
```

## Step 6: Exercises

### Exercise 1: Generate Infrastructure Code
Generate AWS CDK code for a serverless API with Lambda, API Gateway, and DynamoDB.

### Exercise 2: Generate API Client
Generate a REST API client for a third-party service (e.g., GitHub API, AWS API).

### Exercise 3: Generate Database Schema
Generate DynamoDB table definitions for an e-commerce application.

### Exercise 4: Generate Tests
Generate unit tests for a complex function or class.

### Exercise 5: Generate Documentation
Generate comprehensive documentation for a project.

## Troubleshooting

### Common Issues

#### Generated Code Doesn't Work
- Review and refine your prompt
- Check for syntax errors
- Test generated code incrementally
- Add more specific requirements

#### Infrastructure Code Fails
- Verify AWS permissions
- Check resource naming conventions
- Validate Terraform/CDK syntax
- Review AWS service limits

#### API Client Issues
- Verify API specifications
- Check authentication requirements
- Test with actual API endpoints
- Review error handling

## Next Steps

✅ **Module 3 Complete!**

You have successfully:
- Generated AWS infrastructure code
- Created API integration code
- Generated database schemas
- Created test suites
- Generated documentation

**Ready for [Module 4: AWS Services Integration](./module-4-aws-integration.md)?**

## Additional Resources

- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pytest Documentation](https://docs.pytest.org/)

