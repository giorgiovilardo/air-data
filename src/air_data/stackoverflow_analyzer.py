from pathlib import Path

import duckdb


class StackOverflowAnalyzer:
    def __init__(self):
        # Initialize in-memory DuckDB connection
        self.conn = duckdb.connect(":memory:")

        # Get paths to CSV files relative to this module
        base_path = Path(__file__).parent / "so_data"
        self.data_csv_path = base_path / "so_2024_raw.csv"
        self.schema_csv_path = base_path / "so_2024_raw_schema.csv"

        # Read CSV files into DuckDB tables
        self._load_data()

    def _load_data(self):
        """Load CSV files into DuckDB tables using native CSV reading facilities."""
        # Load the main data CSV
        self.conn.execute(f"""
            CREATE TABLE survey_data AS
            SELECT * FROM read_csv_auto('{self.data_csv_path}')
        """)

        # Load the schema CSV
        self.conn.execute(f"""
            CREATE TABLE survey_schema AS
            SELECT * FROM read_csv_auto('{self.schema_csv_path}')
        """)

    def get_data_table(self):
        """Return the survey data table."""
        return self.conn.execute("SELECT * FROM survey_data").fetchdf()

    def get_schema_table(self):
        """Return the survey schema table."""
        return self.conn.execute("SELECT * FROM survey_schema").fetchdf()

    def get_table_info(self, table_name):
        """Get information about a table's structure."""
        return self.conn.execute(f"DESCRIBE {table_name}").fetchdf()

    def close(self):
        """Close the DuckDB connection."""
        if self.conn:
            self.conn.close()
