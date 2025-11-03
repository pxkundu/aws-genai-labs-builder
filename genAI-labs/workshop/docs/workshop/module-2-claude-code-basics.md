# Module 2: Claude Code Basics

## Overview
This module introduces you to Claude Code's core capabilities and how to use them with Amazon Bedrock. You'll learn the fundamentals of code generation, understand prompt engineering for code, and create your first Claude Code applications.

## Learning Objectives
- Understand Claude Code capabilities and use cases
- Learn how to interact with Claude models via Bedrock
- Master prompt engineering for code generation
- Generate your first code examples
- Understand best practices for Claude Code

## Prerequisites
- Completed Module 1: Environment Setup
- Python 3.11+ installed
- AWS credentials configured
- Bedrock access with Claude models

## Step 1: Understanding Claude Code

### 1.1 What is Claude Code?
Claude Code is a specialized AI capability that helps developers:
- Generate code from natural language descriptions
- Refactor and improve existing code
- Debug and fix code issues
- Write documentation and comments
- Create tests and test cases
- Explain complex code

### 1.2 Key Features
- **Code Generation**: Create code from scratch based on requirements
- **Code Refactoring**: Improve existing code structure and quality
- **Code Review**: Analyze code for bugs, security issues, and best practices
- **Documentation**: Generate documentation, comments, and README files
- **Test Generation**: Create unit tests and integration tests
- **Code Explanation**: Explain complex code in simple terms

### 1.3 Use Cases
- **Rapid Prototyping**: Quickly generate working prototypes
- **Code Migration**: Migrate code between languages or frameworks
- **API Integration**: Generate client code for APIs
- **Infrastructure as Code**: Generate AWS CDK/Terraform configurations
- **Database Operations**: Generate SQL queries and schema definitions
- **Testing**: Generate comprehensive test suites

## Step 2: Basic Claude Code Integration

### 2.1 Create Basic Claude Code Client
Create `code/examples/basic_claude_code.py`:

```python
"""
Basic Claude Code Example
Demonstrates how to use Claude Code with Amazon Bedrock
"""

import boto3
import json
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class ClaudeCodeClient:
    """Client for interacting with Claude Code via Bedrock"""
    
    def __init__(
        self,
        model_id: Optional[str] = None,
        region: Optional[str] = None
    ):
        """Initialize Claude Code client"""
        self.model_id = model_id or os.getenv(
            'BEDROCK_MODEL_ID',
            'anthropic.claude-3-5-sonnet-20241022-v2:0'
        )
        self.region = region or os.getenv('BEDROCK_REGION', 'us-east-1')
        
        self.bedrock = boto3.client(
            'bedrock-runtime',
            region_name=self.region
        )
    
    def generate_code(
        self,
        prompt: str,
        language: str = "python",
        max_tokens: int = 4000,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Generate code from natural language prompt
        
        Args:
            prompt: Natural language description of code to generate
            language: Programming language (python, javascript, etc.)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0-1.0)
        
        Returns:
            Dictionary containing generated code and metadata
        """
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
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
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
            
            return {
                'code': generated_code,
                'model': self.model_id,
                'tokens_used': result.get('usage', {}),
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'code': None,
                'error': str(e),
                'status': 'error'
            }
    
    def refactor_code(
        self,
        code: str,
        instructions: str,
        language: str = "python"
    ) -> Dict[str, Any]:
        """
        Refactor existing code based on instructions
        
        Args:
            code: Existing code to refactor
            instructions: Instructions for refactoring
            language: Programming language
        
        Returns:
            Dictionary containing refactored code
        """
        prompt = f"""Refactor the following {language} code based on these instructions:

Instructions: {instructions}

Original Code:
```{language}
{code}
```

Refactored Code:"""

        try:
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    'anthropic_version': 'bedrock-2023-05-31',
                    'max_tokens': 4000,
                    'messages': [{
                        'role': 'user',
                        'content': prompt
                    }]
                })
            )
            
            result = json.loads(response['body'].read())
            refactored_code = result['content'][0]['text']
            
            return {
                'refactored_code': refactored_code,
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'refactored_code': None,
                'error': str(e),
                'status': 'error'
            }


def main():
    """Main function to demonstrate Claude Code"""
    client = ClaudeCodeClient()
    
    # Example 1: Generate a simple function
    print("=" * 60)
    print("Example 1: Generate a Simple Function")
    print("=" * 60)
    
    prompt = "Create a Python function that calculates the factorial of a number"
    result = client.generate_code(prompt, language="python")
    
    if result['status'] == 'success':
        print("\nGenerated Code:")
        print(result['code'])
    else:
        print(f"Error: {result['error']}")
    
    # Example 2: Generate a REST API endpoint
    print("\n" + "=" * 60)
    print("Example 2: Generate a REST API Endpoint")
    print("=" * 60)
    
    prompt = """Create a FastAPI endpoint that:
1. Accepts a POST request with JSON data
2. Validates the input using Pydantic
3. Stores the data in a dictionary (simulating database)
4. Returns the stored data with a success message"""
    
    result = client.generate_code(prompt, language="python")
    
    if result['status'] == 'success':
        print("\nGenerated Code:")
        print(result['code'])
    else:
        print(f"Error: {result['error']}")


if __name__ == "__main__":
    main()
```

### 2.2 Run the Example
```bash
cd code/examples
python basic_claude_code.py
```

## Step 3: Prompt Engineering for Code

### 3.1 Effective Prompt Patterns

#### Pattern 1: Specific Requirements
```python
# Good: Specific and clear
prompt = """
Create a Python class for a TaskManager that:
- Has methods: add_task(), remove_task(), list_tasks(), complete_task()
- Uses a dictionary to store tasks
- Each task has: id, title, description, status, created_at
- Include proper error handling and type hints
"""

# Bad: Vague
prompt = "Make a task manager"
```

#### Pattern 2: Include Context
```python
# Good: Provides context
prompt = """
I'm building a REST API using FastAPI. Create an endpoint that:
- Accepts user registration data (name, email, password)
- Validates email format and password strength (min 8 chars)
- Hashes password using bcrypt
- Returns JWT token upon successful registration
- Handles duplicate email errors
"""
```

#### Pattern 3: Specify Output Format
```python
# Good: Specifies format
prompt = """
Generate a Python function that validates AWS S3 bucket names.
Return a tuple: (is_valid: bool, error_message: str)
Include docstring with examples.
"""
```

### 3.2 Create Prompt Template
Create `code/examples/prompt_templates.py`:

```python
"""
Prompt Templates for Common Code Generation Tasks
"""

PROMPT_TEMPLATES = {
    'function': """
Create a {language} function named {function_name} that:
{requirements}

Requirements:
- Include type hints
- Add docstring with parameter descriptions
- Include error handling
- Add example usage in docstring
""",
    
    'class': """
Create a {language} class named {class_name} that:
{requirements}

Requirements:
- Include __init__ method
- Add docstrings for class and methods
- Include proper error handling
- Follow {language} best practices
""",
    
    'api_endpoint': """
Create a {framework} API endpoint that:
{requirements}

Requirements:
- Use Pydantic for request validation
- Include proper error handling
- Return appropriate HTTP status codes
- Add docstring with example request/response
""",
    
    'test': """
Create {language} unit tests for the following code:

{code}

Requirements:
- Test all functions/methods
- Include edge cases
- Use {test_framework}
- Achieve at least 80% code coverage
""",
    
    'refactor': """
Refactor the following {language} code:

{code}

Instructions:
{instructions}

Requirements:
- Maintain functionality
- Improve code readability
- Follow best practices
- Add proper documentation
"""
}


def build_prompt(template_type: str, **kwargs) -> str:
    """Build prompt from template"""
    template = PROMPT_TEMPLATES.get(template_type)
    if not template:
        raise ValueError(f"Unknown template type: {template_type}")
    
    return template.format(**kwargs)


# Example usage
if __name__ == "__main__":
    prompt = build_prompt(
        'function',
        language='python',
        function_name='calculate_fibonacci',
        requirements="""- Takes an integer n as input
- Returns the nth Fibonacci number
- Uses memoization for efficiency
- Handles negative numbers and edge cases"""
    )
    print(prompt)
```

## Step 4: Code Generation Examples

### 4.1 Generate a Data Processing Function
Create `code/examples/data_processing_example.py`:

```python
"""
Example: Generate data processing code using Claude Code
"""

from basic_claude_code import ClaudeCodeClient


def generate_data_processor():
    """Generate data processing code"""
    client = ClaudeCodeClient()
    
    prompt = """
Create a Python class DataProcessor that:
1. Reads CSV files using pandas
2. Cleans data (removes duplicates, handles missing values)
3. Performs basic statistics (mean, median, std)
4. Exports processed data to JSON
5. Includes logging for each operation
6. Has error handling for file operations
"""
    
    result = client.generate_code(prompt, language="python")
    
    if result['status'] == 'success':
        # Save generated code to file
        with open('generated_data_processor.py', 'w') as f:
            f.write(result['code'])
        print("✅ Code generated and saved to generated_data_processor.py")
        return result['code']
    else:
        print(f"❌ Error: {result['error']}")
        return None


if __name__ == "__main__":
    generate_data_processor()
```

### 4.2 Generate API Client
Create `code/examples/api_client_example.py`:

```python
"""
Example: Generate API client code using Claude Code
"""

from basic_claude_code import ClaudeCodeClient


def generate_api_client():
    """Generate API client code"""
    client = ClaudeCodeClient()
    
    prompt = """
Create a Python class AWSServiceClient that:
1. Uses boto3 to interact with AWS services
2. Has methods for: S3 (upload, download, list), DynamoDB (put, get, query)
3. Includes retry logic with exponential backoff
4. Has proper error handling and logging
5. Uses environment variables for AWS credentials
6. Includes type hints and docstrings
"""
    
    result = client.generate_code(prompt, language="python")
    
    if result['status'] == 'success':
        with open('generated_aws_client.py', 'w') as f:
            f.write(result['code'])
        print("✅ Code generated and saved to generated_aws_client.py")
        return result['code']
    else:
        print(f"❌ Error: {result['error']}")
        return None


if __name__ == "__main__":
    generate_api_client()
```

## Step 5: Code Refactoring

### 5.1 Refactor Example
Create `code/examples/refactor_example.py`:

```python
"""
Example: Refactor code using Claude Code
"""

from basic_claude_code import ClaudeCodeClient


def refactor_example():
    """Example of refactoring code"""
    client = ClaudeCodeClient()
    
    # Original code (needs refactoring)
    original_code = """
def process_data(data):
    result = []
    for i in range(len(data)):
        if data[i] > 0:
            result.append(data[i] * 2)
        else:
            result.append(0)
    return result

def calculate_stats(data):
    total = 0
    count = 0
    for i in range(len(data)):
        total += data[i]
        count += 1
    return total / count if count > 0 else 0
"""
    
    instructions = """
1. Use list comprehensions where appropriate
2. Add type hints
3. Add docstrings
4. Improve variable names
5. Add error handling
6. Follow PEP 8 style guide
"""
    
    result = client.refactor_code(
        code=original_code,
        instructions=instructions,
        language="python"
    )
    
    if result['status'] == 'success':
        print("✅ Refactored Code:")
        print(result['refactored_code'])
        return result['refactored_code']
    else:
        print(f"❌ Error: {result['error']}")
        return None


if __name__ == "__main__":
    refactor_example()
```

## Step 6: Best Practices

### 6.1 Prompt Engineering Best Practices

1. **Be Specific**: Clearly state what you want
2. **Provide Context**: Include relevant background information
3. **Specify Format**: Define the output format you need
4. **Include Examples**: Show examples when possible
5. **Iterate**: Refine prompts based on results

### 6.2 Code Generation Best Practices

1. **Review Generated Code**: Always review and test generated code
2. **Test Thoroughly**: Test edge cases and error conditions
3. **Document**: Add documentation for complex logic
4. **Security**: Review for security vulnerabilities
5. **Performance**: Consider performance implications

### 6.3 Error Handling

```python
def safe_generate_code(client, prompt, max_retries=3):
    """Generate code with retry logic"""
    for attempt in range(max_retries):
        try:
            result = client.generate_code(prompt)
            if result['status'] == 'success':
                return result
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            print(f"Attempt {attempt + 1} failed, retrying...")
            time.sleep(2 ** attempt)  # Exponential backoff
```

## Step 7: Exercises

### Exercise 1: Generate a Calculator Class
Create a Python class that performs basic arithmetic operations with error handling.

### Exercise 2: Generate a File Manager
Create a Python class that manages file operations (read, write, delete) with proper error handling.

### Exercise 3: Refactor Legacy Code
Take a piece of legacy code and refactor it using Claude Code to improve readability and maintainability.

## Troubleshooting

### Common Issues

#### Code Generation Not Working
- Check Bedrock access and model availability
- Verify prompt clarity and specificity
- Check token limits and response size

#### Generated Code Has Errors
- Review and refine your prompt
- Add more specific requirements
- Test generated code thoroughly

#### Performance Issues
- Use appropriate model (Haiku for simple tasks, Sonnet for complex)
- Adjust temperature for consistency
- Implement caching for repeated requests

## Next Steps

✅ **Module 2 Complete!**

You have successfully:
- Learned Claude Code fundamentals
- Created basic code generation examples
- Mastered prompt engineering techniques
- Generated and refactored code

**Ready for [Module 3: Real-World Use Cases](./module-3-use-cases.md)?**

## Additional Resources

- [Claude Code Documentation](https://docs.anthropic.com/claude/docs/claude-code)
- [Prompt Engineering Guide](https://docs.anthropic.com/claude/docs/prompt-engineering)
- [Python Best Practices](https://docs.python-guide.org/writing/style/)
- [Code Review Checklist](https://github.com/google/eng-practices/blob/master/review/checklist.md)

