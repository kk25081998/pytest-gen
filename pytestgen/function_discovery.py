"""
Function discovery module for PyTest-Gen
"""

import ast
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class FunctionDiscovery:
    """
    Discover and analyze Python functions in a project directory
    """

    def __init__(self, project_dir: Path):
        """
        Initialize the function discovery
        
        Args:
            project_dir: Path to the project directory to scan
        """
        self.project_dir = project_dir
        self.visited_files = set()
        self.discovered_functions = []

    def discover(self, max_files: int = None) -> List[Dict[str, Any]]:
        """
        Discover functions in the project directory
        
        Args:
            max_files: Maximum number of files to process
        
        Returns:
            List of discovered functions with their metadata
        """
        self.discovered_functions = []
        python_files = self._find_python_files(max_files)
        
        for file_path in python_files:
            try:
                functions = self._process_file(file_path)
                self.discovered_functions.extend(functions)
            except Exception as e:
                logger.warning(f"Error processing {file_path}: {str(e)}")
                continue
        
        return self.discovered_functions

    def _find_python_files(self, max_files: int = None) -> List[Path]:
        """
        Find all Python files in the project directory
        
        Args:
            max_files: Maximum number of files to return
        
        Returns:
            List of Python file paths
        """
        python_files = []
        for file in self.project_dir.rglob("*.py"):
            if file not in self.visited_files:
                python_files.append(file)
                self.visited_files.add(file)
                if max_files and len(python_files) >= max_files:
                    break
        return python_files

    def _process_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Process a single Python file and extract function information
        
        Args:
            file_path: Path to the Python file
        
        Returns:
            List of functions found in the file
        """
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        try:
            tree = ast.parse(content)
            functions = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = self._extract_function_info(node, file_path)
                    functions.append(func_info)
            return functions
        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {str(e)}")
            return []

    def _extract_function_info(self, node: ast.FunctionDef, file_path: Path) -> Dict[str, Any]:
        """
        Extract detailed information about a function
        
        Args:
            node: AST node representing the function
            file_path: Path to the file containing the function
        
        Returns:
            Dictionary containing function information
        """
        # Get function arguments
        args = []
        for arg in node.args.args:
            args.append({
                "name": arg.arg,
                "annotation": getattr(arg.annotation, "id", None) if arg.annotation else None
            })

        # Get docstring
        docstring = ast.get_docstring(node)

        return {
            "file_path": str(file_path),
            "function_name": node.name,
            "args": args,
            "docstring": docstring,
            "line_number": node.lineno,
            "is_test": self._is_test_function(node.name)
        }

    def _is_test_function(self, function_name: str) -> bool:
        """
        Check if a function is a test function
        
        Args:
            function_name: Name of the function
        
        Returns:
            True if the function is a test function, False otherwise
        """
        return function_name.startswith("test_") or "test" in function_name.lower()

    def get_untested_functions(self) -> List[Dict[str, Any]]:
        """
        Get functions that don't have corresponding test functions
        
        Returns:
            List of functions that need tests
        """
        functions = self.discovered_functions
        untested = []
        
        for func in functions:
            if not func["is_test"]:
                # Check if there's a corresponding test function
                test_name = f"test_{func['function_name']}"
                has_test = any(
                    f["is_test"] and f["function_name"] == test_name
                    for f in functions
                )
                
                if not has_test:
                    untested.append(func)
        
        return untested
