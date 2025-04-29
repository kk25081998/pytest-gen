#!/usr/bin/env python3
"""
PyTest-Gen - AI-Powered Test-Case Generator for Python
"""

import click
import os
import sys
from pathlib import Path
from .function_discovery import FunctionDiscovery
from .test_generator import TestGenerator

@click.group()
@click.version_option("0.1.0")
def cli():
    """PyTest-Gen - AI-Powered Test-Case Generator for Python"""
    pass

@cli.command(name="generate")
@click.option("--project-dir", default=".", type=click.Path(exists=True), help="Project directory to scan")
@click.option("--api-key", envvar="OPENAI_API_KEY", help="OpenAI API key")
@click.option("--max-functions", default=None, type=int, help="Maximum number of functions to process")
@click.option("--overwrite", is_flag=True, help="Overwrite existing test files")
@click.option("--model", default="gpt-4", help="LLM model to use")
@click.option("--dry-run", is_flag=True, help="Print generated tests to the console instead of writing files")
@click.option("--output-dir", default="tests", type=click.Path(), help="Directory to write generated test files (default: ./tests)")
def generate(project_dir, api_key, max_functions, overwrite, model, dry_run, output_dir):
    """Generate pytest test cases for Python functions."""
    if not api_key:
        click.echo("Error: API key is required. Please provide --api-key or set OPENAI_API_KEY environment variable.")
        sys.exit(1)

    project_path = Path(project_dir).resolve()
    click.echo(f"🔍 Scanning project at {project_path}")
    click.echo(f"🤖 Using model: {model}")

    # Discover functions
    discovery = FunctionDiscovery(project_path)
    functions = discovery.discover(max_files=max_functions)
    untested = discovery.get_untested_functions()
    
    if not untested:
        click.echo("✅ All functions have tests. No new tests needed!")
        return

    click.echo(f"Found {len(untested)} untested functions")
    
    # Generate tests
    generator = TestGenerator(api_key=api_key, model=model)
    results = generator.generate_tests_for_functions(untested)
    
    if dry_run:
        click.echo("\n--- DRY RUN: Generated Test Cases ---\n")
        for result in results:
            click.echo(f"# For function: {result.function_info['function_name']}")
            if result.error:
                click.echo(f"❌ Error: {result.error}")
            else:
                click.echo(result.test_code.strip() + "\n")
        click.echo("--- END DRY RUN ---\n")
        return

    # Write test files
    output_path = Path(output_dir).resolve()
    output_path.mkdir(exist_ok=True)
    for result in results:
        if result.error:
            click.echo(f"❌ Error generating tests for {result.function_info['function_name']}: {result.error}")
            continue

        module_name = Path(result.function_info.get("file_path", "module")).stem
        test_file = output_path / f"test_{module_name}.py"
        
        if test_file.exists() and not overwrite:
            click.echo(f"⚠️ Skipping {test_file.name} - file exists and --overwrite not specified")
            continue

        with open(test_file, "a") as f:
            f.write(result.test_code.strip())
            f.write("\n\n")

        click.echo(f"✅ Generated tests for {result.function_info['function_name']} in {test_file.name}")

if __name__ == "__main__":
    cli()
