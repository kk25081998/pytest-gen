import pytest
from unittest.mock import patch, MagicMock
from pytestgen.test_generator import TestGenerator, TestGenerationResult

def test_generate_prompt():
    # Create a mock function info
    function_info = {
        "function_name": "add",
        "args": [
            {"name": "a", "annotation": "int"},
            {"name": "b", "annotation": "int"}
        ],
        "docstring": "Add two numbers",
        "line_number": 1,
        "is_test": False
    }

    # Create test generator
    generator = TestGenerator(api_key="test-key")

    # Generate prompt
    prompt = generator._generate_prompt(function_info)

    # Check prompt contains expected elements
    assert "def add(a: int, b: int)" in prompt
    assert "Add two numbers" in prompt
    assert "Write pytest test cases" in prompt
    assert "Return only the test code" in prompt

def test_generate_test_success():
    # Create mock response
    mock_response = MagicMock()
    choice = MagicMock()
    choice.text = """
def test_add_positive_numbers():
    assert add(1, 2) == 3

def test_add_negative_numbers():
    assert add(-1, -2) == -3

def test_add_mixed_numbers():
    assert add(-1, 2) == 1
"""
    mock_response.choices = [choice]

    # Mock OpenAI API
    with patch("openai.Completion.create", return_value=mock_response):
        # Create test generator
        generator = TestGenerator(api_key="test-key")

        # Create mock function info
        function_info = {
            "function_name": "add",
            "args": [
                {"name": "a", "annotation": "int"},
                {"name": "b", "annotation": "int"}
            ],
            "docstring": "Add two numbers",
            "line_number": 1,
            "is_test": False
        }

        # Generate test
        result = generator.generate_test(function_info)

        # Check result
        assert isinstance(result, TestGenerationResult)
        assert result.function_info == function_info
        assert "def test_add_positive_numbers" in result.test_code
        assert "def test_add_negative_numbers" in result.test_code
        assert "def test_add_mixed_numbers" in result.test_code

def test_generate_test_error():
    # Mock OpenAI API to raise an error
    with patch("openai.Completion.create", side_effect=Exception("API error")):
        # Create test generator
        generator = TestGenerator(api_key="test-key")

        # Create mock function info
        function_info = {
            "function_name": "add",
            "args": [
                {"name": "a", "annotation": "int"},
                {"name": "b", "annotation": "int"}
            ],
            "docstring": "Add two numbers",
            "line_number": 1,
            "is_test": False
        }

        # Generate test
        result = generator.generate_test(function_info)

        # Check result
        assert isinstance(result, TestGenerationResult)
        assert result.function_info == function_info
        assert result.test_code == ""
        assert "API error" in result.error
