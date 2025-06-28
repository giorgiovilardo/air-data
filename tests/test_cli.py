from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from rich.table import Table

from src.air_data.cli import (
    display_answer_distribution,
    display_survey_structure,
    search_questions,
)


@pytest.fixture
def mock_analyzer():
    """
    Fixture that returns a mock StackOverflowAnalyzer.
    """
    mock = MagicMock()

    # Mock get_survey_structure
    mock.get_survey_structure.return_value = pd.DataFrame(
        {
            "column": ["Age", "DevType"],
            "question_text": ["What is your age?", "What is your role?"],
            "type": ["SC", "MC"],
        }
    )

    # Mock search_questions
    mock.search_questions.return_value = pd.DataFrame(
        {
            "column": ["Age"],
            "question_text": ["What is your age?"],
            "type": ["SC"],
        }
    )

    # Mock get_answer_distribution
    mock.get_answer_distribution.return_value = pd.DataFrame(
        {
            "option": ["18-24", "25-34", "35-44"],
            "count": [10, 20, 15],
            "percentage": [22.22, 44.44, 33.33],
        }
    )

    return mock


@patch("src.air_data.cli.Console")
def test_display_survey_structure(
    mock_console_class: MagicMock, mock_analyzer: MagicMock
):
    """
    Test that display_survey_structure correctly displays the survey structure.
    """
    # Create a mock console
    mock_console = MagicMock()
    mock_console_class.return_value = mock_console

    # Call the function
    display_survey_structure(mock_analyzer)

    # Verify that get_survey_structure was called
    mock_analyzer.get_survey_structure.assert_called_once_with(sort_by=None)

    # Verify that console.print was called with a Table
    mock_console.print.assert_called_once()
    args, _ = mock_console.print.call_args
    assert isinstance(args[0], Table)
    assert args[0].title == "Survey Structure"


@patch("src.air_data.cli.Console")
def test_search_questions(mock_console_class: MagicMock, mock_analyzer: MagicMock):
    """
    Test that search_questions correctly displays the search results.
    """
    # Create a mock console
    mock_console = MagicMock()
    mock_console_class.return_value = mock_console

    # Call the function
    search_questions(mock_analyzer, search_term="age")

    # Verify that search_questions was called with the correct search term
    mock_analyzer.search_questions.assert_called_once_with(search_term="age")

    # Verify that console.print was called with a Table
    mock_console.print.assert_called_once()
    args, _ = mock_console.print.call_args
    assert isinstance(args[0], Table)
    assert args[0].title == "Questions containing 'age'"


@patch("src.air_data.cli.Console")
def test_display_answer_distribution(
    mock_console_class: MagicMock, mock_analyzer: MagicMock
):
    """
    Test that display_answer_distribution correctly displays the answer distribution.
    """
    # Create a mock console
    mock_console = MagicMock()
    mock_console_class.return_value = mock_console

    # Call the function
    display_answer_distribution(mock_analyzer, column="Age")

    # Verify that search_questions was called to get the question info
    mock_analyzer.search_questions.assert_called_once_with(search_term="Age")

    # Verify that get_answer_distribution was called with the correct column
    mock_analyzer.get_answer_distribution.assert_called_once_with(column="Age")

    # Verify that console.print was called with a Table
    mock_console.print.assert_called_once()
    args, _ = mock_console.print.call_args
    assert isinstance(args[0], Table)
    assert "Answer Distribution for" in args[0].title
