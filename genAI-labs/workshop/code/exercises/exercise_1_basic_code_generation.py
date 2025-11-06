"""
Exercise 1: Basic Code Generation
Generate a simple Python function using Claude Code
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../examples'))
from basic_claude_code import ClaudeCodeClient


def exercise_1():
    """
    Exercise: Generate a Python function that calculates the factorial of a number
    
    Steps:
    1. Create a ClaudeCodeClient instance
    2. Generate code for a factorial function
    3. Print the generated code
    4. Test the generated code (optional)
    """
    # TODO: Create ClaudeCodeClient instance
    # client = ClaudeCodeClient()
    
    # TODO: Generate code with prompt "Create a Python function that calculates factorial"
    # result = client.generate_code(...)
    
    # TODO: Print the generated code
    # print(result['code'])
    
    print("Exercise 1: Basic Code Generation")
    print("Complete the TODO items above to finish this exercise")


if __name__ == "__main__":
    exercise_1()

