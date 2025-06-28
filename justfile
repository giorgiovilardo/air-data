default:
    just --list

# Install the project in development mode
install:
    uv sync --dev
    uv pip install -e .

# Run the interactive CLI
run:
    uv run air-data

# Run CLI with uv (alternative)
cli:
    uv run python -m air_data.cli

# Install and run in one command
start: install run

# Format code
_format:
    ruff format src tests

# Sort imports
_isort:
    ruff check --select I --fix src tests

# Format and sort imports
fmt: && _isort _format

# Run linting
lint:
    ruff check --fix src tests
    basedpyright src tests

# Run tests
test:
    pytest

# Run tests with verbose output
test-verbose:
    pytest -v

# Clean up build artifacts
clean:
    rm -rf dist/
    rm -rf build/
    rm -rf *.egg-info/
    find . -type d -name __pycache__ -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete

# Show project information
info:
    @echo "Air Data - StackOverflow Survey Analyzer"
    @echo "========================================"
    @echo "Python version: $(python --version)"
    @echo "UV version: $(uv --version)"
    @echo "Project dependencies:"
    @uv tree
