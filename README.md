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

# Install the package
pip install -e .
```

## Usage

### Command Line Interface

The package provides a command-line interface (CLI) for interacting with the Stack Overflow survey data:

```bash
# Run the CLI
so-analyzer
```

The CLI provides the following options:

1. **Display survey structure**: Shows the list of questions in the survey
2. **Search for questions**: Searches for questions containing a specific term
3. **Create respondent subset**: Creates a subset of respondents based on their answer to a specific question
4. **Display answer distribution**: Shows the distribution of answers for a specific question

### Programmatic Usage

You can also use the library programmatically in your Python code:

```python
from air_data.stackoverflow_analyzer import StackOverflowAnalyzer

# Initialize the analyzer with data and schema files
analyzer = StackOverflowAnalyzer(
    data_file="path/to/data.csv",
    schema_file="path/to/schema.csv",
)

# Display the survey structure
survey_structure = analyzer.get_survey_structure()
print(survey_structure)

# Search for questions containing a specific term
questions = analyzer.search_questions(search_term="code")
print(questions)

# Create a subset of respondents based on their answer to a specific question
subset = analyzer.create_respondent_subset(column="Age", option="25-34")

# Display the distribution of answers for a specific question
distribution = analyzer.get_answer_distribution(column="Age")
print(distribution)
```

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

# Format code
just fmt

# Lint code
just lint

# Run tests
just test

# Run all checks (lint and test)
just check

# Clean up temporary files and directories
just clean
```

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

- **Fact Table**: The survey responses (so_data)
- **Dimension Table**: The survey questions (so_schema)

This allows for efficient querying and analysis of the survey data.
