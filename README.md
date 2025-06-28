# Air Data - StackOverflow Survey Analyzer

A powerful tool for analyzing StackOverflow Survey data using a star schema design in DuckDB.

## Implementation details

In the end, the impl from air and the impl from junie has converged to something
very very similar. The CLI is basically the same. Junie however, took a lot more time
to get to a correct state, even with me knowing beforehand what was wrong or right.
Air struggled a bit from the start, not knowing well duckdb methods, but got it very
fast once it was able to import the CSVs. Air got the whole implementation basically
zeroshot, after building the constructor.
Junie needed a lot more babysitting, fewshot, was wrong many times.
A big important thing is that Junie at some point went over the maximum context,
leaving the project in a broken state. Luckily enough I had git!

## Features

- **Star Schema Design**: Efficiently organized data with fact and dimension tables
- **Multi-Choice Question Support**: Handles both Single Choice (SC) and Multiple Choice (MC) questions
- **Rich CLI Interface**: Interactive command-line interface with beautiful tables and visualizations
- **Flexible Analysis**: Query and analyze survey data with various filtering options

## Prerequisites

- **Python 3.13+**: Required for modern Python features and type hints
- **UV**: Fast Python package installer and resolver ([install guide](https://docs.astral.sh/uv/getting-started/installation/))
- **Just**: Command runner for development tasks ([install guide](https://github.com/casey/just#installation))

## Installation

### Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd air-data

# Install dependencies and the package (recommended)
just install

# Or install manually with uv
uv sync --dev
uv pip install -e .
```

### Alternative Installation Methods

```bash
# Using pip directly (not recommended for development)
pip install -e .

# Using uv without just
uv sync --dev
uv pip install -e .
```

## Running the Application

### Using Just Commands (Recommended)

```bash
# Install and run in one command
just start

# Just run the CLI (after installation)
just run

# Alternative CLI command
just cli

# Show available commands
just --list
```

### Manual Commands

```bash
# Run the interactive CLI
air-data

# Or run with uv
uv run air-data

# Or run the module directly
uv run python -m air_data.cli
```

## CLI Interface

The interactive CLI provides the following operations:

1. **Display Survey Structure**: View all questions with metadata (ID, column, type, options count)
2. **Search Questions/Options**: Find questions and answer options by keyword
3. **Get Respondent Subsets**: Filter respondents by their answers to specific questions
4. **Show Answer Distributions**: Analyze response patterns with percentages and counts

### CLI Usage Example

```bash
$ just run
# or
$ air-data

Air Data - StackOverflow Survey Analyzer
========================================

1. Display Survey Structure
2. Search Questions/Options
3. Get Respondent Subset
4. Show Answer Distribution
5. Exit

Enter your choice (1-5): 1
# Displays a formatted table of all survey questions...
```

## Architecture

The analyzer uses a star schema with the following tables:

- `dim_questions`: Question metadata (ID, column name, question text, type)
- `dim_respondents`: Respondent demographics and key attributes
- `dim_answer_options`: All possible answer values for each question
- `fact_responses`: Normalized responses linking respondents to questions and answers

## Programmatic Usage

```python
from air_data.stackoverflow_analyzer import StackOverflowAnalyzer

# Initialize analyzer (loads data and creates star schema)
analyzer = StackOverflowAnalyzer()

# Get survey structure
structure = analyzer.get_survey_structure()

# Search for questions containing 'python'
results = analyzer.search_questions("python")

# Get all respondents who work remotely
remote_workers = analyzer.get_respondent_subset("RemoteWork", "Remote")

# Get distribution of age ranges
age_distribution = analyzer.get_answer_distribution("Age")

# Clean up
analyzer.close()
```

## Data Processing

The analyzer automatically:
- Loads CSV data using DuckDB's native `read_csv_auto()` function
- Creates a star schema with proper normalization
- Handles semicolon-separated multiple choice answers using `unnest()` and `string_split()`
- Generates unique IDs for all dimension tables
- Links fact table to dimensions via foreign keys

## Development

### Available Just Commands

```bash
# Development workflow
just install         # Install dependencies and package
just run            # Run the CLI
just cli            # Alternative CLI command
just start          # Install and run in one command

# Code quality
just fmt            # Format code with ruff
just lint           # Run linting (ruff + basedpyright)
just test           # Run tests
just test-verbose   # Run tests with verbose output

# Utilities
just clean          # Clean build artifacts
just info           # Show project information
just --list         # Show all available commands
```

### Manual Development Commands

```bash
# Install dependencies
uv sync --dev

# Run tests
uv run pytest

# Run linting
uv run ruff check --fix src tests
uv run basedpyright src tests

# Format code
uv run ruff format src tests
```

## Technology Stack

- **DuckDB**: High-performance analytical database with CSV reading capabilities
- **Pandas**: Data manipulation and analysis
- **Rich**: Beautiful terminal output and tables
- **Python 3.13+**: Modern Python features and type hints
- **UV**: Fast Python package management
- **Just**: Command runner for development tasks

## Project Structure

```
air-data/
├── src/air_data/           # Main package source code
│   ├── cli.py             # CLI interface
│   ├── stackoverflow_analyzer.py  # Core analyzer logic
│   └── so_data/           # Sample data files
├── tests/                 # Test suite
├── justfile              # Development commands
├── pyproject.toml        # Project configuration
├── uv.lock              # Dependency lock file
└── README.md            # This file
```

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure you've installed the package with `just install` or `uv pip install -e .`
2. **UV not found**: Install UV from [here](https://docs.astral.sh/uv/getting-started/installation/)
3. **Just not found**: Install Just from [here](https://github.com/casey/just#installation)
4. **Python version**: Ensure you're using Python 3.13 or later

### Getting Help

```bash
# Show project info and dependencies
just info

# List all available commands
just --list

# Run tests to verify installation
just test
```
