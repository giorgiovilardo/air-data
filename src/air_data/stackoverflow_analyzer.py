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

        # Load the raw data into temporary tables
        self._load_raw_data()

        # Create the star schema
        self._create_star_schema()

    def _load_raw_data(self) -> None:
        """
        Load the raw data from CSV files into temporary DuckDB tables.
        """
        # Load the schema file into a temporary DuckDB table
        self.conn.execute(f"""
            CREATE TABLE so_schema AS 
            SELECT * FROM read_csv_auto('{self.schema_file}')
        """)

        # Load the data file into a temporary DuckDB table
        self.conn.execute(f"""
            CREATE TABLE so_data AS 
            SELECT * FROM read_csv_auto('{self.data_file}')
        """)

    def _create_star_schema(self) -> None:
        """
        Create a star schema from the raw data.

        This creates the following tables:
        - dim_questions: Dimension table for questions
        - dim_respondents: Dimension table for respondents
        - fact_responses_sc: Fact table for single-choice responses
        - fact_responses_mc: Fact table for multiple-choice responses
        """
        # Create dimension table for questions
        self.conn.execute("""
            CREATE TABLE dim_questions AS
            SELECT 
                ROW_NUMBER() OVER () as question_id,
                "column" as column_name,
                question_text,
                type
            FROM so_schema
        """)

        # Create dimension table for respondents
        # Extract demographic columns that are single-choice
        demographic_columns = (
            self.conn.execute("""
            SELECT column_name
            FROM dim_questions
            WHERE type = 'SC' AND column_name IN (
                'MainBranch', 'Age', 'RemoteWork', 'EdLevel', 'YearsCode', 
                'YearsCodePro', 'DevType', 'Country'
            )
        """)
            .df()["column_name"]
            .tolist()
        )

        # Create a comma-separated list of demographic columns for the SQL query
        demographic_cols_sql = ", ".join([f'"{col}"' for col in demographic_columns])

        # Create the respondents dimension table with a unique ID and demographic information
        self.conn.execute(f"""
            CREATE TABLE dim_respondents AS
            SELECT 
                ROW_NUMBER() OVER () as respondent_id,
                {demographic_cols_sql}
            FROM so_data
        """)

        # Get all columns from the data
        data_columns = (
            self.conn.execute("SELECT * FROM so_data LIMIT 0").df().columns.tolist()
        )

        # Get SC and MC questions
        sc_questions = self.conn.execute("""
            SELECT question_id, column_name
            FROM dim_questions
            WHERE type = 'SC'
        """).df()

        mc_questions = self.conn.execute("""
            SELECT question_id, column_name
            FROM dim_questions
            WHERE type = 'MC'
        """).df()

        # Create empty fact tables
        self.conn.execute("""
            CREATE TABLE fact_responses_sc (
                respondent_id INTEGER,
                question_id INTEGER,
                response VARCHAR
            )
        """)

        self.conn.execute("""
            CREATE TABLE fact_responses_mc (
                respondent_id INTEGER,
                question_id INTEGER,
                response VARCHAR
            )
        """)

        # Process each SC question
        for _, row in sc_questions.iterrows():
            question_id = row["question_id"]
            column_name = row["column_name"]

            if column_name in data_columns:
                # Insert data for this column
                self.conn.execute(f"""
                    INSERT INTO fact_responses_sc
                    SELECT 
                        ROW_NUMBER() OVER () as respondent_id,
                        {question_id} as question_id,
                        CASE 
                            WHEN "{column_name}" IS NULL THEN 'NA'
                            WHEN CAST("{column_name}" AS VARCHAR) = '' THEN 'NA'
                            ELSE CAST("{column_name}" AS VARCHAR)
                        END as response
                    FROM so_data
                """)

        # Process each MC question
        for _, row in mc_questions.iterrows():
            question_id = row["question_id"]
            column_name = row["column_name"]

            if column_name in data_columns:
                # Insert data for this column
                self.conn.execute(f"""
                    WITH mc_data AS (
                        SELECT 
                            ROW_NUMBER() OVER () as respondent_id,
                            {question_id} as question_id,
                            CAST("{column_name}" AS VARCHAR) as response_combined
                        FROM so_data
                        WHERE "{column_name}" IS NOT NULL AND CAST("{column_name}" AS VARCHAR) != ''
                    )
                    INSERT INTO fact_responses_mc
                    SELECT 
                        respondent_id,
                        question_id,
                        unnest(string_split(response_combined, ';')) as response
                    FROM mc_data
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
        # Query the dimension table for questions
        query = """
            SELECT 
                column_name as column,
                question_text,
                type
            FROM dim_questions
        """

        # Add sorting if specified
        if sort_by:
            query += f' ORDER BY "{sort_by}"'
        else:
            query += " ORDER BY question_id"  # Default sort by question_id to maintain original order

        # Execute the query and return the result as a DataFrame
        return self.conn.execute(query).df()

    def search_questions(self, *, search_term: str) -> pd.DataFrame:
        """
        Searches for questions containing the specified search term.

        Args:
            search_term: The term to search for in question text, column name, or answers.

        Returns:
            pd.DataFrame: DataFrame containing the matching questions and answers.
        """
        # Query the dimension table for questions to find those containing the search term
        # in either the question_text or column_name
        questions_query = f"""
            SELECT 
                column_name as column,
                question_text,
                type,
                'question' as match_type
            FROM dim_questions 
            WHERE question_text ILIKE '%{search_term}%' OR column_name ILIKE '%{search_term}%'
        """

        # Query the fact tables for answers containing the search term
        sc_answers_query = f"""
            SELECT 
                q.column_name as column,
                q.question_text,
                q.type,
                'answer' as match_type
            FROM fact_responses_sc r
            JOIN dim_questions q ON r.question_id = q.question_id
            WHERE r.response ILIKE '%{search_term}%'
            GROUP BY q.column_name, q.question_text, q.type
        """

        mc_answers_query = f"""
            SELECT 
                q.column_name as column,
                q.question_text,
                q.type,
                'answer' as match_type
            FROM fact_responses_mc r
            JOIN dim_questions q ON r.question_id = q.question_id
            WHERE r.response ILIKE '%{search_term}%'
            GROUP BY q.column_name, q.question_text, q.type
        """

        # Combine the results
        combined_query = f"""
            SELECT * FROM ({questions_query}) q
            UNION
            SELECT * FROM ({sc_answers_query}) sc
            UNION
            SELECT * FROM ({mc_answers_query}) mc
            ORDER BY "column"
        """

        # Execute the query and return the result as a DataFrame
        return self.conn.execute(combined_query).df()

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
        # Get the question type and ID from the dimension table
        query_info = f"""
            SELECT question_id, type 
            FROM dim_questions 
            WHERE column_name = '{column}'
        """
        result = self.conn.execute(query_info).fetchone()
        if not result:
            return pd.DataFrame(columns=["option", "count", "percentage"])

        question_id, question_type = result  # type: ignore

        # Create the base query depending on the question type
        if question_type == "SC":
            # For single choice questions
            if option:
                # Filter for the specific option
                query = f"""
                    SELECT 
                        response as option, 
                        COUNT(*) as count,
                        COUNT(*) * 100.0 / (
                            SELECT COUNT(*) 
                            FROM fact_responses_sc 
                            WHERE question_id = {question_id} AND response != 'NA'
                        ) as percentage
                    FROM fact_responses_sc
                    WHERE question_id = {question_id} AND response = '{option}'
                    GROUP BY response
                    ORDER BY count DESC
                """
            else:
                # Show distribution of all options
                query = f"""
                    SELECT 
                        response as option, 
                        COUNT(*) as count,
                        COUNT(*) * 100.0 / (
                            SELECT COUNT(*) 
                            FROM fact_responses_sc 
                            WHERE question_id = {question_id} AND response != 'NA'
                        ) as percentage
                    FROM fact_responses_sc
                    WHERE question_id = {question_id} AND response != 'NA'
                    GROUP BY response
                    ORDER BY count DESC
                """
        elif question_type == "MC":
            # For multiple choice questions
            if option:
                # Filter for the specific option
                query = f"""
                    WITH filtered_respondents AS (
                        SELECT DISTINCT respondent_id
                        FROM fact_responses_mc
                        WHERE question_id = {question_id} AND response = '{option}'
                    )
                    SELECT 
                        response as option, 
                        COUNT(*) as count,
                        COUNT(*) * 100.0 / (
                            SELECT COUNT(*) 
                            FROM fact_responses_mc f
                            JOIN filtered_respondents r ON f.respondent_id = r.respondent_id
                            WHERE f.question_id = {question_id}
                        ) as percentage
                    FROM fact_responses_mc f
                    JOIN filtered_respondents r ON f.respondent_id = r.respondent_id
                    WHERE f.question_id = {question_id}
                    GROUP BY response
                    ORDER BY count DESC
                """
            else:
                # Show distribution of all options
                query = f"""
                    SELECT 
                        response as option, 
                        COUNT(*) as count,
                        COUNT(*) * 100.0 / (
                            SELECT COUNT(*) 
                            FROM fact_responses_mc 
                            WHERE question_id = {question_id}
                        ) as percentage
                    FROM fact_responses_mc
                    WHERE question_id = {question_id}
                    GROUP BY response
                    ORDER BY count DESC
                """
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
        # Get the question type and ID from the dimension table
        query_info = f"""
            SELECT question_id, type 
            FROM dim_questions 
            WHERE column_name = '{column}'
        """
        result = self.conn.execute(query_info).fetchone()
        if not result:
            return pd.DataFrame(columns=["option", "count", "percentage"])

        question_id, question_type = result  # type: ignore

        if question_type == "SC":
            # For single choice questions, count each value
            query = f"""
                SELECT 
                    response as option, 
                    COUNT(*) as count,
                    COUNT(*) * 100.0 / (
                        SELECT COUNT(*) 
                        FROM fact_responses_sc 
                        WHERE question_id = {question_id} AND response != 'NA'
                    ) as percentage
                FROM fact_responses_sc
                WHERE question_id = {question_id} AND response != 'NA'
                GROUP BY response
                ORDER BY count DESC
            """
        elif question_type == "MC":
            # For multiple choice questions, count each option
            query = f"""
                SELECT 
                    response as option, 
                    COUNT(*) as count,
                    COUNT(*) * 100.0 / (
                        SELECT COUNT(*) 
                        FROM fact_responses_mc 
                        WHERE question_id = {question_id}
                    ) as percentage
                FROM fact_responses_mc
                WHERE question_id = {question_id}
                GROUP BY response
                ORDER BY count DESC
            """
        else:
            # For other question types, return an empty DataFrame
            return pd.DataFrame(columns=["option", "count", "percentage"])

        # Execute the query and return the result as a DataFrame
        return self.conn.execute(query).df()
