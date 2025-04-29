"""
Test case generator using LLM for Python functions
"""

import logging
import os
from typing import Dict, Any, List
from dataclasses import dataclass
from openai import OpenAI

logger = logging.getLogger(__name__)

@dataclass
class TestGenerationResult:
    """
    Result of test case generation
    """
    function_info: Dict[str, Any]
    test_code: str
    error: str = None

class TestGenerator:
    """
    Generate pytest test cases using LLM
    """

    def __init__(self, api_key: str, model: str = "gpt-4o", output_dir: str = "output_tests"):
        """
        Initialize the test generator
        
        Args:
            api_key: OpenAI API key
            model: LLM model to use
            output_dir: Directory to write generated test files
        """
        self.api_key = api_key
        self.model = model
        self.output_dir = output_dir
        self._setup_openai()

    def _setup_openai(self):
        """Initialize OpenAI client"""
        self.client = OpenAI(api_key=self.api_key)

    def _generate_prompt(self, function_info: Dict[str, Any]) -> str:
        """
        Generate a prompt for test case generation
        
        Args:
            function_info: Dictionary containing function information
        
        Returns:
            Generated prompt string
        """
        args_info = ", ".join([
            f"{arg['name']}: {arg['annotation'] if arg['annotation'] else 'Any'}"
            for arg in function_info["args"]
        ])

        docstring = function_info["docstring"] or "No docstring available"

        prompt = '''Write pytest test cases for the following Python function:

Function signature:
```python
def {function_name}({args_info}):
    """{docstring}"""
```

Requirements:
1. Write at least 3 test cases that cover different scenarios
2. Use descriptive test names that indicate what's being tested
3. Include assertions that verify the function's behavior
4. Follow pytest best practices
5. If the function has type hints, use appropriate test data types

Return only the test code, without any additional text or explanations.
'''.format(
            function_name=function_info['function_name'],
            args_info=args_info,
            docstring=docstring
        )

        return prompt

    def generate_test(self, function_info: Dict[str, Any]) -> TestGenerationResult:
        """
        Generate test cases for a function
        
        Args:
            function_info: Dictionary containing function information
        
        Returns:
            TestGenerationResult object
        """
        try:
            prompt = self._generate_prompt(function_info)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )

            raw = response.choices[0].message.content if response.choices else ""
            # strip markdown code fences if present
            if raw.startswith("```"):
                lines = raw.splitlines()
                # drop opening fence
                if lines and lines[0].startswith("```"):
                    lines = lines[1:]
                # drop closing fence
                if lines and lines[-1].strip().startswith("```"):
                    lines = lines[:-1]
                test_code = "\n".join(lines).strip()
            else:
                test_code = raw.strip()
            return TestGenerationResult(function_info=function_info, test_code=test_code)

        except Exception as e:
            logger.error(f"Error generating tests for {function_info['function_name']}: {str(e)}")
            return TestGenerationResult(
                function_info=function_info,
                test_code="",
                error=str(e)
            )

    def generate_tests_for_functions(self, functions: List[Dict[str, Any]]) -> List[TestGenerationResult]:
        """
        Generate tests for multiple functions
        
        Args:
            functions: List of function information dictionaries
        
        Returns:
            List of TestGenerationResult objects
        """
        # ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        results = []
        for func_info in functions:
            result = self.generate_test(func_info)
            results.append(result)
            # write test file
            if result.test_code:
                fname = f"test_{func_info['function_name']}.py"
                path = os.path.join(self.output_dir, fname)
                with open(path, 'w') as f:
                    f.write(result.test_code)
        return results
