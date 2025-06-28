import pandas as pd

from src.air_data.stackoverflow_analyzer import StackOverflowAnalyzer


def test_stackoverflow_analyzer_init(so_schema_file: str, so_sample_file: str):
    """
    Test that the StackOverflowAnalyzer constructor accepts two string parameters:
    a data file path and a schema file path, and properly initializes the object.
    """
    # Create a StackOverflowAnalyzer instance with the sample and schema files
    analyzer = StackOverflowAnalyzer(
        data_file=so_sample_file,
        schema_file=so_schema_file,
    )

    # Verify that the analyzer has been properly initialized with the provided files
    assert hasattr(analyzer, "data_file")
    assert hasattr(analyzer, "schema_file")
    assert analyzer.data_file == so_sample_file
    assert analyzer.schema_file == so_schema_file

    # Verify that the data has been loaded into DuckDB tables
    assert hasattr(analyzer, "conn")  # DuckDB connection

    # Check if the tables exist in the database
    cursor = analyzer.conn.cursor()

    # Check if the data table exists
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='so_data'"
    )
    assert cursor.fetchone() is not None, "so_data table not found in the database"

    # Check if the schema table exists
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='so_schema'"
    )
    assert cursor.fetchone() is not None, "so_schema table not found in the database"

    # Verify that the tables have data
    cursor.execute("SELECT COUNT(*) FROM so_data")
    assert cursor.fetchone()[0] > 0, "so_data table is empty"  # type: ignore

    cursor.execute("SELECT COUNT(*) FROM so_schema")
    assert cursor.fetchone()[0] > 0, "so_schema table is empty"  # type: ignore


def test_get_survey_structure(so_schema_file: str, so_sample_file: str):
    """
    Test that the get_survey_structure method returns a DataFrame with the survey structure.
    """
    # Create a StackOverflowAnalyzer instance
    analyzer = StackOverflowAnalyzer(
        data_file=so_sample_file,
        schema_file=so_schema_file,
    )

    # Call the method
    survey_structure = analyzer.get_survey_structure()

    # Verify that the result is a DataFrame
    assert isinstance(survey_structure, pd.DataFrame)

    # Verify that the DataFrame has the expected columns
    assert "column" in survey_structure.columns
    assert "question_text" in survey_structure.columns
    assert "type" in survey_structure.columns

    # Verify that the DataFrame has data
    assert len(survey_structure) > 0


def test_search_questions(so_schema_file: str, so_sample_file: str):
    """
    Test that the search_questions method returns questions matching the search term.
    """
    # Create a StackOverflowAnalyzer instance
    analyzer = StackOverflowAnalyzer(
        data_file=so_sample_file,
        schema_file=so_schema_file,
    )

    # Search for a term that should exist in the questions
    search_term = "code"
    results = analyzer.search_questions(search_term=search_term)

    # Verify that the result is a DataFrame
    assert isinstance(results, pd.DataFrame)

    # Verify that the DataFrame has the expected columns
    assert "column" in results.columns
    assert "question_text" in results.columns
    assert "type" in results.columns

    # Verify that the search term is in the results
    assert any(results["question_text"].str.contains(search_term, case=False))


def test_search_questions_in_column_name(so_schema_file: str, so_sample_file: str):
    """
    Test that the search_questions method returns questions matching the search term in column name.
    """
    # Create a StackOverflowAnalyzer instance
    analyzer = StackOverflowAnalyzer(
        data_file=so_sample_file,
        schema_file=so_schema_file,
    )

    # Get a column name from the schema
    cursor = analyzer.conn.cursor()
    cursor.execute('SELECT "column" FROM so_schema LIMIT 1')
    column = cursor.fetchone()[0]  # type: ignore

    # Extract a substring from the column name to use as search term
    search_term = column[:3]  # Use first 3 characters of the column name

    # Search for the column name
    results = analyzer.search_questions(search_term=search_term)

    # Verify that the result is a DataFrame
    assert isinstance(results, pd.DataFrame)

    # Verify that the search term is found in the column names
    assert any(results["column"].str.contains(search_term, case=False))


def test_create_respondent_subset(so_schema_file: str, so_sample_file: str):
    """
    Test that the create_respondent_subset method returns a DataFrame with the distribution
    of respondents grouped by their answers to the specified question.
    """
    # Create a StackOverflowAnalyzer instance
    analyzer = StackOverflowAnalyzer(
        data_file=so_sample_file,
        schema_file=so_schema_file,
    )

    # Get a column name from the schema
    cursor = analyzer.conn.cursor()
    cursor.execute('SELECT "column" FROM so_schema LIMIT 1')
    column = cursor.fetchone()[0]  # type: ignore

    # Create a subset based on the column
    subset_df = analyzer.create_respondent_subset(column=column, option="")

    # Verify that the result is a DataFrame
    assert isinstance(subset_df, pd.DataFrame)

    # Verify that the DataFrame has the expected columns
    assert "option" in subset_df.columns
    assert "count" in subset_df.columns
    assert "percentage" in subset_df.columns

    # Verify that the DataFrame has data
    assert len(subset_df) > 0


def test_get_answer_distribution(so_schema_file: str, so_sample_file: str):
    """
    Test that the get_answer_distribution method returns the distribution of answers.
    """
    # Create a StackOverflowAnalyzer instance
    analyzer = StackOverflowAnalyzer(
        data_file=so_sample_file,
        schema_file=so_schema_file,
    )

    # Get a column name from the schema
    cursor = analyzer.conn.cursor()
    cursor.execute(
        "SELECT \"column\" FROM so_schema WHERE \"type\" IN ('SC', 'MC') LIMIT 1"
    )
    column = cursor.fetchone()[0]  # type: ignore

    # Get the distribution of answers
    distribution = analyzer.get_answer_distribution(column=column)

    # Verify that the result is a DataFrame
    assert isinstance(distribution, pd.DataFrame)

    # Verify that the DataFrame has data
    assert len(distribution) > 0
