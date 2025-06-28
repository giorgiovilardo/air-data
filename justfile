default:
    just --list

_format:
    ruff format src tests

_isort:
    ruff check --select I --fix src tests

fmt: _isort _format

lint:
    ruff check --fix src tests
    basedpyright src tests

test:
    pytest

# Run the CLI application (uses sample data by default)
run:
    python -m air_data.cli

# Run the CLI application using the installed script
run-script:
    so-analyzer

# Install the package in development mode
install:
    pip install -e .

# Run the CLI application with custom data files
run-custom data_file schema_file:
    python -c "from air_data.stackoverflow_analyzer import StackOverflowAnalyzer; from air_data.cli import main; import os; os.environ['SO_DATA_FILE'] = '{{data_file}}'; os.environ['SO_SCHEMA_FILE'] = '{{schema_file}}'; main()"

# Clean up temporary files and directories
clean:
    rm -rf build dist .pytest_cache .ruff_cache
    find . -type d -name __pycache__ -exec rm -rf {} +
    find . -type d -name "*.egg-info" -exec rm -rf {} +

# Run all checks (lint and test)
check: lint test
