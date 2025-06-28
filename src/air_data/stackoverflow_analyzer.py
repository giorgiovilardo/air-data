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
