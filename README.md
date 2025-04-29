# PyTest-Gen

AI-Powered Test-Case Generator for Python

## Overview

PyTest-Gen is a command-line tool that automatically generates pytest test cases for your Python functions using AI. It scans your Python project, identifies functions, and generates appropriate test cases using large language models.

## Features

- 🔄 Automatic test case generation for Python functions
- 🤖 Powered by OpenAI's GPT models
- 📝 Supports function docstrings and signatures
- 📦 Ready-to-use pytest test files
- 🔄 Configurable options for customization

## Installation

You can install PyTest-Gen using pip:

```bash
pip install pytestgen
```

## Usage

```bash
pytestgen generate --project-dir . --api-key $OPENAI_API_KEY
```

### Options

- `--project-dir`: Directory to scan for Python files (default: current directory)
- `--api-key`: OpenAI API key (can also be set via OPENAI_API_KEY env var)
- `--max-functions`: Maximum number of functions to process
- `--overwrite`: Overwrite existing test files
- `--model`: LLM model to use (default: gpt-4)
- `--dry-run`: Print generated tests to the console instead of writing files
- `--output-dir`: Directory to write generated test files (default: ./tests)

## Example Output

Given a function:

```python
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b
```

PyTest-Gen might generate:

```python
def test_add_positive_numbers():
    assert add(1, 2) == 3

def test_add_negative_numbers():
    assert add(-1, -2) == -3

def test_add_mixed_numbers():
    assert add(-1, 2) == 1
```

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key. Can be set as an environment variable or passed with `--api-key`.

## Requirements

- Python 3.8 or higher
- OpenAI API access

## Troubleshooting

- **No API Key Provided:** Ensure you set the `OPENAI_API_KEY` environment variable or pass `--api-key`.
- **Test Files Not Written:** Use `--overwrite` to allow overwriting existing files, or specify a different `--output-dir`.
- **Dry Run:** Use `--dry-run` to preview generated tests without writing files.

## Contributing

Contributions are welcome! Please open an issue or pull request.

1. Fork the repository
2. Create a new branch
3. Make your changes with tests
4. Run all tests with `pytest`
5. Submit a pull request

## License

MIT License
