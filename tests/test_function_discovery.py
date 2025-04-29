import pytest
from pathlib import Path
import tempfile
from pytestgen.function_discovery import FunctionDiscovery

def test_discover_functions():
    # Create a temporary directory with test files
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Create a Python file with functions
        test_file = tmp_path / "test_module.py"
        test_content = '''
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

def multiply(x, y):
    """Multiply two numbers."""
    return x * y

def test_add():
    assert add(1, 2) == 3
'''
        test_file.write_text(test_content.strip(), encoding="utf-8")

        # Create another Python file
        another_file = tmp_path / "another_module.py"
        another_content = '''
def divide(x, y):
    """Divide two numbers."""
    return x / y
'''
        another_file.write_text(another_content.strip(), encoding="utf-8")

        # Discover functions
        discovery = FunctionDiscovery(tmp_path)
        functions = discovery.discover()

        # Check results
        assert len(functions) == 4
        function_names = [f["function_name"] for f in functions]
        assert "add" in function_names
        assert "multiply" in function_names
        assert "test_add" in function_names
        assert "divide" in function_names

def test_extract_function_info():
    # Create a temporary directory with a test file
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        test_file = tmp_path / "test_module.py"
        test_content = '''
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
'''
        test_file.write_text(test_content.strip(), encoding="utf-8")

        # Discover and process the function
        discovery = FunctionDiscovery(tmp_path)
        functions = discovery.discover()
        
        assert len(functions) == 1
        func_info = functions[0]
        
        # Check function info
        assert func_info["function_name"] == "add"
        assert func_info["docstring"] == "Add two numbers."
        assert func_info["line_number"] == 1
        assert not func_info["is_test"]
        
        # Check arguments
        args = func_info["args"]
        assert len(args) == 2
        assert args[0] == {"name": "a", "annotation": "int"}
        assert args[1] == {"name": "b", "annotation": "int"}

def test_get_untested_functions():
    # Create a temporary directory with test files
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Create a Python file with functions
        test_file = tmp_path / "test_module.py"
        test_content = '''
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

def multiply(x, y):
    """Multiply two numbers."""
    return x * y

def test_add():
    assert add(1, 2) == 3
'''
        test_file.write_text(test_content.strip(), encoding="utf-8")

        # Discover functions
        discovery = FunctionDiscovery(tmp_path)
        functions = discovery.discover()
        untested = discovery.get_untested_functions()

        # Check results
        assert len(untested) == 1
        assert untested[0]["function_name"] == "multiply"
