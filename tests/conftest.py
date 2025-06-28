from pathlib import Path

import pytest

# Get the project root directory (parent of tests directory)
PROJECT_ROOT = Path(__file__).parent.parent
SO_DATA_DIR = PROJECT_ROOT / "src" / "air_data" / "so_data"


@pytest.fixture
def sample_csv():
    csv_path = SO_DATA_DIR / "so_2024_sample.csv"
    with open(csv_path, "r") as file:
        content = file.read()
    return content


@pytest.fixture
def schema_csv():
    csv_path = SO_DATA_DIR / "so_2024_raw_schema.csv"
    with open(csv_path, "r") as file:
        content = file.read()
    return content


@pytest.fixture
def sample_csv_file():
    return SO_DATA_DIR / "so_2024_sample.csv"


@pytest.fixture
def schema_csv_file():
    return SO_DATA_DIR / "so_2024_raw_schema.csv"
