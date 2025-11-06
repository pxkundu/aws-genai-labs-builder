"""
Exercise 2: API Generation
Generate a REST API endpoint using Claude Code
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../examples'))
from basic_claude_code import ClaudeCodeClient


def exercise_2():
    """
    Exercise: Generate a FastAPI endpoint for user management
    
    Steps:
    1. Create a ClaudeCodeClient instance
    2. Generate code for a FastAPI endpoint that:
       - Accepts POST requests with user data
       - Validates input using Pydantic
       - Returns created user data
    3. Save the generated code to a file
    """
    # TODO: Create ClaudeCodeClient instance
    
    # TODO: Generate FastAPI endpoint code
    prompt = """
    Create a FastAPI endpoint that:
    1. Accepts POST requests with JSON data (name, email, age)
    2. Validates input using Pydantic models
    3. Stores user in a dictionary (simulating database)
    4. Returns the created user with success message
    """
    
    # TODO: Generate code and save to file
    # result = client.generate_code(prompt, language="python")
    # with open('generated_api.py', 'w') as f:
    #     f.write(result['code'])
    
    print("Exercise 2: API Generation")
    print("Complete the TODO items above to finish this exercise")


if __name__ == "__main__":
    exercise_2()

