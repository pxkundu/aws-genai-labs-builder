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

