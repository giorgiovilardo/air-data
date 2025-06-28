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
