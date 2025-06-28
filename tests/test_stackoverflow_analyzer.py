
import pandas as pd

from air_data.stackoverflow_analyzer import StackOverflowAnalyzer


class TestStackOverflowAnalyzer:
    def test_initialization(self):
        """Test that the analyzer initializes correctly."""
        analyzer = StackOverflowAnalyzer()
        assert analyzer.conn is not None
        assert analyzer.data_csv_path.exists()
        assert analyzer.schema_csv_path.exists()
        analyzer.close()

    def test_data_loading(self):
        """Test that CSV data is loaded correctly into DuckDB tables."""
        analyzer = StackOverflowAnalyzer()

        # Check that tables exist
        tables = analyzer.conn.execute("SHOW TABLES").fetchall()
        table_names = [table[0] for table in tables]
        assert "survey_data" in table_names
        assert "survey_schema" in table_names

        analyzer.close()

    def test_get_data_table(self):
        """Test getting the survey data table."""
        analyzer = StackOverflowAnalyzer()

        data_df = analyzer.get_data_table()
        assert isinstance(data_df, pd.DataFrame)
        assert len(data_df) > 0
        assert len(data_df.columns) > 0

        # Check some expected columns from the sample data
        expected_columns = ["MainBranch", "Age", "Employment", "RemoteWork"]
        for col in expected_columns:
            assert col in data_df.columns

        analyzer.close()

    def test_get_schema_table(self):
        """Test getting the survey schema table."""
        analyzer = StackOverflowAnalyzer()

        schema_df = analyzer.get_schema_table()
        assert isinstance(schema_df, pd.DataFrame)
        assert len(schema_df) > 0

        # Check expected schema columns
        expected_columns = ["column", "question_text", "type"]
        for col in expected_columns:
            assert col in schema_df.columns

        analyzer.close()

    def test_get_table_info(self):
        """Test getting table structure information."""
        analyzer = StackOverflowAnalyzer()

        # Test for survey_data table
        data_info = analyzer.get_table_info("survey_data")
        assert isinstance(data_info, pd.DataFrame)
        assert "column_name" in data_info.columns
        assert "column_type" in data_info.columns

        # Test for survey_schema table
        schema_info = analyzer.get_table_info("survey_schema")
        assert isinstance(schema_info, pd.DataFrame)
        assert "column_name" in schema_info.columns
        assert "column_type" in schema_info.columns

        analyzer.close()

    def test_csv_files_exist(self, sample_csv_file, schema_csv_file):
        """Test that the required CSV files exist using fixtures."""
        assert sample_csv_file.exists()
        assert schema_csv_file.exists()

        # Verify file sizes are reasonable
        assert sample_csv_file.stat().st_size > 1000  # At least 1KB
        assert schema_csv_file.stat().st_size > 1000  # At least 1KB

    def test_csv_content_structure(self, sample_csv, schema_csv):
        """Test the structure of CSV content using fixtures."""
        # Test that sample CSV has header and data
        sample_lines = sample_csv.strip().split("\n")
        assert len(sample_lines) > 1  # At least header + 1 data row

        # Test that schema CSV has expected structure
        schema_lines = schema_csv.strip().split("\n")
        assert len(schema_lines) > 1  # At least header + 1 data row

        # Check schema header
        schema_header = schema_lines[0].split(",")
        assert "column" in schema_header
        assert "question_text" in schema_header
        assert "type" in schema_header

    def test_data_schema_consistency(self):
        """Test that data columns match schema definitions."""
        analyzer = StackOverflowAnalyzer()

        data_df = analyzer.get_data_table()
        schema_df = analyzer.get_schema_table()

        # Get column names from both sources
        data_columns = set(data_df.columns)
        schema_columns = set(schema_df["column"].tolist())

        # Check that most schema columns exist in data
        # (allowing for some differences in case of sample vs full data)
        common_columns = data_columns.intersection(schema_columns)
        assert len(common_columns) > 0, (
            "No common columns found between data and schema"
        )

        analyzer.close()

    def test_duckdb_native_csv_reading(self):
        """Test that DuckDB's native CSV reading is working correctly."""
        analyzer = StackOverflowAnalyzer()

        # Test direct CSV reading capability
        result = analyzer.conn.execute(f"""
            SELECT COUNT(*) as row_count
            FROM read_csv_auto('{analyzer.data_csv_path}')
        """).fetchone()

        assert result[0] > 0, "No rows found when reading CSV directly"

        analyzer.close()

    def test_memory_database(self):
        """Test that we're using an in-memory database."""
        analyzer = StackOverflowAnalyzer()

        # Check database info - for in-memory DuckDB, the name is 'memory' and file is None
        db_info = analyzer.conn.execute("PRAGMA database_list").fetchall()
        # In-memory databases have name 'memory' and file path None
        assert any(db[1] == "memory" and db[2] is None for db in db_info)

        analyzer.close()
