from io import StringIO
from pathlib import Path
from typing import Self


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
        import pandas as pd
        import tempfile
        import os
        from pathlib import Path

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
        temp_fd, combined_path = tempfile.mkstemp(suffix='.csv')
        os.close(temp_fd)

        # Write the combined data to the temporary file
        combined_df.to_csv(combined_path, index=False)

        # Create and return a new analyzer instance
        return cls(
            data_file=combined_path,
            schema_file=str(schema_path)
        )
