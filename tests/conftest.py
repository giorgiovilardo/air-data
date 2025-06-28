from pathlib import Path

import pytest


@pytest.fixture
def so_schema_file() -> str:
    """
    Fixture that returns the path to the Stack Overflow schema file.
    """
    base_dir = Path(__file__).parent.parent
    schema_file = base_dir / "src" / "air_data" / "so_data" / "so_2024_raw_schema.csv"
    assert schema_file.exists(), f"Schema file not found at {schema_file}"
    return str(schema_file)


@pytest.fixture
def so_sample_file() -> str:
    """
    Fixture that returns the path to the Stack Overflow sample data file.
    """
    base_dir = Path(__file__).parent.parent
    sample_file = base_dir / "src" / "air_data" / "so_data" / "so_2024_sample.csv"
    assert sample_file.exists(), f"Sample file not found at {sample_file}"
    return str(sample_file)
