from pathlib import Path
from typing import Optional, Self

import pandas as pd


class StackOverflowAnalyzer:
    def __init__(
        self,
        *,
        data_file: str,
        schema_file: str,
    ):
        """
        Initialize the StackOverflowAnalyzer with data and schema files.

        Args:
            data_file: Path to the CSV file containing Stack Overflow survey data
            schema_file: Path to the CSV file containing the schema for the survey data
        """
        import duckdb

        self.data_file = data_file
        self.schema_file = schema_file

        # Create a DuckDB connection
        self.conn = duckdb.connect(":memory:")

        # Load the schema file into a DuckDB table
        self.conn.execute(f"""
            CREATE TABLE so_schema AS 
            SELECT * FROM read_csv_auto('{schema_file}')
        """)

        # Load the data file into a DuckDB table
        self.conn.execute(f"""
            CREATE TABLE so_data AS 
            SELECT * FROM read_csv_auto('{data_file}')
        """)

    @classmethod
    def from_split_files(cls) -> Self:
        """
        Reads and combines so_2024_raw_1.csv and so_2024_raw_2.csv into a single temporary file,
        then initializes a new StackOverflowAnalyzer instance with the combined data
        and the schema from so_2024_raw_schema.csv.

        Returns:
            Self: A new StackOverflowAnalyzer instance.
        """
        import os
        import tempfile

        import pandas as pd

        # Hardcoded paths for input files
        base_dir = Path(__file__).parent / "so_data"
        file1_path = base_dir / "so_2024_raw_1.csv"
        file2_path = base_dir / "so_2024_raw_2.csv"
        schema_path = base_dir / "so_2024_raw_schema.csv"

        # Read the CSV files into pandas DataFrames
        df1 = pd.read_csv(file1_path)
        df2 = pd.read_csv(file2_path)

        # Combine the DataFrames
        combined_df = pd.concat([df1, df2], ignore_index=True)

        # Create a temporary file for the combined data
        temp_fd, combined_path = tempfile.mkstemp(suffix=".csv")
        os.close(temp_fd)

        # Write the combined data to the temporary file
        combined_df.to_csv(combined_path, index=False)

        # Create and return a new analyzer instance
        return cls(data_file=combined_path, schema_file=str(schema_path))

    def get_survey_structure(self, *, sort_by: Optional[str] = None) -> pd.DataFrame:
        """
        Returns the survey structure (list of questions) as a DataFrame.

        Args:
            sort_by: Optional column to sort by. If None, sorts by the original order.

        Returns:
            pd.DataFrame: DataFrame containing the survey structure.
        """
        # Query the schema table to get the survey structure
        query = "SELECT * FROM so_schema"

        # Add sorting if specified
        if sort_by:
            query += f' ORDER BY "{sort_by}"'

        # Execute the query and return the result as a DataFrame
        return self.conn.execute(query).df()

    def search_questions(self, *, search_term: str) -> pd.DataFrame:
        """
        Searches for questions containing the specified search term.

        Args:
            search_term: The term to search for in question text.

        Returns:
            pd.DataFrame: DataFrame containing the matching questions.
        """
        # Query the schema table to find questions containing the search term
        query = f"""
            SELECT * FROM so_schema 
            WHERE "question_text" ILIKE '%{search_term}%'
        """

        # Execute the query and return the result as a DataFrame
        return self.conn.execute(query).df()

    def create_respondent_subset(self, *, column: str, option: str) -> pd.DataFrame:
        """
        Returns a DataFrame showing the distribution of respondents grouped by their answers
        to the specified question.

        Args:
            column: The column (question) to analyze.
            option: The option (answer) to filter for. If empty, includes all non-null values.

        Returns:
            pd.DataFrame: DataFrame containing the distribution of respondents grouped by their answers.
        """
        # Get the question type from the schema
        query_type = f"""
            SELECT "type" FROM so_schema 
            WHERE "column" = '{column}'
        """
        question_type = self.conn.execute(query_type).fetchone()[0]  # type: ignore

        # Create the base query depending on the question type
        if question_type == "SC":
            # For single choice questions
            if option:
                # Filter for the specific option
                query = f'''
                    SELECT "{column}" as option, COUNT(*) as count,
                           COUNT(*) * 100.0 / (SELECT COUNT(*) FROM so_data WHERE "{column}" = '{option}') as percentage
                    FROM so_data
                    WHERE "{column}" = '{option}'
                    GROUP BY "{column}"
                    ORDER BY count DESC
                '''
            else:
                # Show distribution of all options
                query = f'''
                    SELECT "{column}" as option, COUNT(*) as count,
                           COUNT(*) * 100.0 / (SELECT COUNT(*) FROM so_data WHERE "{column}" IS NOT NULL) as percentage
                    FROM so_data
                    WHERE "{column}" IS NOT NULL
                    GROUP BY "{column}"
                    ORDER BY count DESC
                '''
        elif question_type == "MC":
            # For multiple choice questions
            if option:
                # Filter for the specific option in semicolon-separated values
                query = f'''
                    WITH filtered_data AS (
                        SELECT * FROM so_data 
                        WHERE "{column}" = '{option}' OR "{column}" LIKE '{option};%' OR 
                              "{column}" LIKE '%;{option}' OR "{column}" LIKE '%;{option};%'
                    ),
                    unnested AS (
                        SELECT unnest(string_split("{column}", ';')) as option
                        FROM filtered_data
                        WHERE "{column}" IS NOT NULL
                    )
                    SELECT option, COUNT(*) as count,
                           COUNT(*) * 100.0 / (SELECT COUNT(*) FROM unnested) as percentage
                    FROM unnested
                    GROUP BY option
                    ORDER BY count DESC
                '''
            else:
                # Show distribution of all options
                query = f'''
                    WITH unnested AS (
                        SELECT unnest(string_split("{column}", ';')) as option
                        FROM so_data
                        WHERE "{column}" IS NOT NULL
                    )
                    SELECT option, COUNT(*) as count,
                           COUNT(*) * 100.0 / (SELECT COUNT(*) FROM unnested) as percentage
                    FROM unnested
                    GROUP BY option
                    ORDER BY count DESC
                '''
        else:
            # For other question types, return an empty DataFrame
            return pd.DataFrame(columns=["option", "count", "percentage"])

        # Execute the query and return the result as a DataFrame
        return self.conn.execute(query).df()

    def get_answer_distribution(self, *, column: str) -> pd.DataFrame:
        """
        Returns the distribution of answers for a specific question.

        Args:
            column: The column (question) to get the distribution for.

        Returns:
            pd.DataFrame: DataFrame containing the distribution of answers.
        """
        # Get the question type from the schema
        query_type = f"""
            SELECT "type" FROM so_schema 
            WHERE "column" = '{column}'
        """
        question_type = self.conn.execute(query_type).fetchone()[0]  # type: ignore

        if question_type == "SC":
            # For single choice questions, count each value
            query = f'''
                SELECT "{column}" as option, COUNT(*) as count,
                       COUNT(*) * 100.0 / (SELECT COUNT(*) FROM so_data WHERE "{column}" IS NOT NULL) as percentage
                FROM so_data
                WHERE "{column}" IS NOT NULL
                GROUP BY "{column}"
                ORDER BY count DESC
            '''
        elif question_type == "MC":
            # For multiple choice questions, need to unnest the semicolon-separated values
            query = f'''
                WITH unnested AS (
                    SELECT unnest(string_split("{column}", ';')) as option
                    FROM so_data
                    WHERE "{column}" IS NOT NULL
                )
                SELECT option, COUNT(*) as count,
                       COUNT(*) * 100.0 / (SELECT COUNT(*) FROM unnested) as percentage
                FROM unnested
                GROUP BY option
                ORDER BY count DESC
            '''
        else:
            # For other question types, return an empty DataFrame
            return pd.DataFrame(columns=["option", "count", "percentage"])

        # Execute the query and return the result as a DataFrame
        return self.conn.execute(query).df()
