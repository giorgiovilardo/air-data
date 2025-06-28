# Air Data - StackOverflow Survey Analyzer

A powerful tool for analyzing StackOverflow Survey data using a star schema design in DuckDB.

## Features

- **Star Schema Design**: Efficiently organized data with fact and dimension tables
- **Multi-Choice Question Support**: Handles both Single Choice (SC) and Multiple Choice (MC) questions
- **Rich CLI Interface**: Interactive command-line interface with beautiful tables and visualizations
- **Flexible Analysis**: Query and analyze survey data with various filtering options

## Architecture

The analyzer uses a star schema with the following tables:

- `dim_questions`: Question metadata (ID, column name, question text, type)
- `dim_respondents`: Respondent demographics and key attributes
- `dim_answer_options`: All possible answer values for each question
- `fact_responses`: Normalized responses linking respondents to questions and answers

## Usage

### CLI Interface

```bash
# Install the package
pip install -e .

# Run the interactive CLI
air-data
```

### Programmatic Usage

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

## Available Operations

1. **Display Survey Structure**: View all questions with metadata
2. **Search Questions/Options**: Find questions and answer options by keyword
3. **Get Respondent Subsets**: Filter respondents by their answers
4. **Show Answer Distributions**: Analyze response patterns with percentages

## Data Processing

The analyzer automatically:
- Loads CSV data using DuckDB's native `read_csv_auto()` function
- Creates a star schema with proper normalization
- Handles semicolon-separated multiple choice answers using `unnest()` and `string_split()`
- Generates unique IDs for all dimension tables
- Links fact table to dimensions via foreign keys

## Development

```bash
# Run tests
just test

# Run linting
just lint

# Format code
just fmt
```

## Technology Stack

- **DuckDB**: High-performance analytical database with CSV reading capabilities
- **Pandas**: Data manipulation and analysis
- **Rich**: Beautiful terminal output and tables
- **Python 3.13+**: Modern Python features and type hints
