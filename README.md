# Air Data

A Python library for analyzing Stack Overflow Developer Survey data.

## Features

- Display the survey structure (list of questions)
- Search for specific questions/options
- Create respondent subsets based on question+option
- Display distribution of answers for SC (single choice) and MC (multiple choice) questions

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/air-data.git
cd air-data

# Install the package using uv (recommended)
uv pip install -e .

# Or using pip
pip install -e .
```

This project recommends using [uv](https://github.com/astral-sh/uv) for faster and more reliable Python package management.

## Usage

### Command Line Interface

The package provides a command-line interface (CLI) for interacting with the Stack Overflow survey data:

```bash
# Run the CLI using the installed script
so-analyzer

# Or run the module directly
python -m air_data.cli
```

By default, the CLI uses sample data included with the package. You can specify custom data files using environment variables:

```bash
# Run with custom data files
SO_DATA_FILE=/path/to/data.csv SO_SCHEMA_FILE=/path/to/schema.csv so-analyzer
```

The CLI provides an interactive menu with the following options:

1. **Display survey structure**: Shows the list of questions in the survey
2. **Search for questions**: Searches for questions containing a specific term
3. **Create respondent subset**: Creates a subset of respondents based on their answer to a specific question
4. **Display answer distribution**: Shows the distribution of answers for a specific question
5. **Exit**: Exits the CLI

### Programmatic Usage

You can also use the library programmatically in your Python code:

```python
from air_data.stackoverflow_analyzer import StackOverflowAnalyzer

# Initialize the analyzer with specific data and schema files
analyzer = StackOverflowAnalyzer(
    data_file="path/to/data.csv",
    schema_file="path/to/schema.csv",
)

# Or use the sample data included with the package
analyzer = StackOverflowAnalyzer.from_split_files()

# Display the survey structure (optionally sort by a specific column)
survey_structure = analyzer.get_survey_structure(sort_by="column")
print(survey_structure)

# Search for questions containing a specific term
questions = analyzer.search_questions(search_term="code")
print(questions)

# Create a subset of respondents based on their answer to a specific question
subset = analyzer.create_respondent_subset(column="Age", option="25-34")
print(subset)  # Returns a DataFrame with the distribution of respondents

# Display the distribution of answers for a specific question
distribution = analyzer.get_answer_distribution(column="Age")
print(distribution)  # Returns a DataFrame with the distribution of answers
```

All methods use keyword-only arguments, so you must specify the parameter names when calling them.

## Development

### Available Commands

The project uses [just](https://github.com/casey/just) as a command runner. Here are the available commands:

```bash
# Show all available commands
just

# Install the package in development mode
just install

# Run the CLI application (uses sample data by default)
just run

# Run the CLI application using the installed script
just run-script

# Run the CLI application with custom data files
just run-custom path/to/data.csv path/to/schema.csv

# Format code (runs ruff formatter and isort)
just fmt

# Lint code (runs ruff linter and basedpyright)
just lint

# Run tests (using pytest)
just test

# Run all checks (lint and test)
just check

# Clean up temporary files and directories
just clean
```

The project uses the following tools:
- [ruff](https://github.com/astral-sh/ruff) for code formatting and linting
- [basedpyright](https://github.com/detachhead/basedpyright) for type checking
- [pytest](https://docs.pytest.org/) for testing
- [uv](https://github.com/astral-sh/uv) for package management (recommended)

### Running Tests

```bash
# Run tests
just test
```

### Formatting and Linting

```bash
# Format code
just fmt

# Lint code
just lint
```

## Data Model

The library uses a star schema approach for analyzing the survey data:

### Dimension Tables
- **dim_questions**: Contains information about each question (question_id, column_name, question_text, type)
- **dim_respondents**: Contains demographic information about respondents (respondent_id, demographic columns)

### Fact Tables
- **fact_responses_sc**: Contains single-choice responses (respondent_id, question_id, response)
- **fact_responses_mc**: Contains multiple-choice responses (respondent_id, question_id, response)

The raw data is initially loaded into temporary tables (`so_data` and `so_schema`) and then transformed into this star schema, which allows for efficient querying and analysis of the survey data.
