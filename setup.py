from setuptools import setup, find_packages

setup(
    name="pytestgen",
    version="0.2.0",
    description="AI-Powered Test-Case Generator for Python",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "pytest>=7.4.0",
        "click>=8.1.7",
        "astor>=0.8.1",
    ],
    entry_points={
        "console_scripts": [
            "pytestgen=pytestgen:cli",
        ],
    },
)
