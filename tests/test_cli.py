import pytest
import click
from click.testing import CliRunner
from pytestgen import cli
from unittest.mock import patch, MagicMock
import tempfile
from pathlib import Path

def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "PyTest-Gen - AI-Powered Test-Case Generator for Python" in result.output

def test_generate_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["generate", "--help"])
    assert result.exit_code == 0
    assert "Generate pytest test cases for Python functions" in result.output

def test_missing_api_key():
    runner = CliRunner()
    result = runner.invoke(cli, ["generate"])
    assert result.exit_code == 1
    assert "API key is required" in result.output

def mock_discover(self, max_files=None):
    # Return one fake function
    return [{
        "function_name": "add",
        "args": [
            {"name": "a", "annotation": "int"},
            {"name": "b", "annotation": "int"}
        ],
        "docstring": "Add two numbers",
        "line_number": 1,
        "is_test": False,
        "file_path": "sample.py"
    }]

def mock_get_untested_functions(self):
    return self.discover()

def mock_generate_tests_for_functions(self, functions):
    # Return a fake test code for the mock function
    return [
        MagicMock(function_info=functions[0], test_code="def test_add():\n    assert add(1, 2) == 3", error=None)
    ]

def test_generate_dry_run(monkeypatch):
    runner = CliRunner()
    monkeypatch.setenv("OPENAI_API_KEY", "dummy-key")
    
    with patch("pytestgen.function_discovery.FunctionDiscovery.discover", mock_discover), \
         patch("pytestgen.function_discovery.FunctionDiscovery.get_untested_functions", mock_get_untested_functions), \
         patch("pytestgen.test_generator.TestGenerator.generate_tests_for_functions", mock_generate_tests_for_functions):
        result = runner.invoke(cli, ["generate", "--dry-run"])
        assert result.exit_code == 0
        assert "DRY RUN" in result.output
        assert "def test_add()" in result.output
        assert "add(1, 2) == 3" in result.output

def test_generate_output_dir(monkeypatch):
    runner = CliRunner()
    monkeypatch.setenv("OPENAI_API_KEY", "dummy-key")
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("pytestgen.function_discovery.FunctionDiscovery.discover", mock_discover), \
             patch("pytestgen.function_discovery.FunctionDiscovery.get_untested_functions", mock_get_untested_functions), \
             patch("pytestgen.test_generator.TestGenerator.generate_tests_for_functions", mock_generate_tests_for_functions):
            result = runner.invoke(cli, ["generate", f"--output-dir={tmpdir}", "--overwrite"])
            assert result.exit_code == 0
            test_file = Path(tmpdir) / "test_sample.py"
            assert test_file.exists()
            content = test_file.read_text()
            assert "def test_add()" in content
            assert "add(1, 2) == 3" in content
