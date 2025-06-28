"""Tests for CLI functionality."""

from io import StringIO
from unittest.mock import patch

from rich.console import Console

from air_data.cli import (
    display_survey_structure,
    get_respondent_subset,
    main,
    search_questions,
    show_answer_distribution,
)
from air_data.stackoverflow_analyzer import StackOverflowAnalyzer


class TestCLI:
    """Test CLI functions."""

    def test_display_survey_structure(self) -> None:
        """Test displaying survey structure."""
        analyzer = StackOverflowAnalyzer()
        output_buffer = StringIO()
        console = Console(file=output_buffer, width=120)

        # Should not raise an exception
        display_survey_structure(analyzer, console)

        output = output_buffer.getvalue()
        assert "Survey Structure" in output

        analyzer.close()

    def test_search_questions_with_results(self) -> None:
        """Test searching questions with results."""
        analyzer = StackOverflowAnalyzer()
        output_buffer = StringIO()
        console = Console(file=output_buffer, width=120)

        with patch("air_data.cli.Prompt.ask", return_value="age"):
            search_questions(analyzer, console)

        output = output_buffer.getvalue()
        assert "Search Results for 'age'" in output

        analyzer.close()

    def test_search_questions_no_results(self) -> None:
        """Test searching questions with no results."""
        analyzer = StackOverflowAnalyzer()
        output_buffer = StringIO()
        console = Console(file=output_buffer, width=120)

        with patch("air_data.cli.Prompt.ask", return_value="nonexistent_term_xyz"):
            search_questions(analyzer, console)

        output = output_buffer.getvalue()
        assert "No results found for 'nonexistent_term_xyz'" in output

        analyzer.close()

    def test_get_respondent_subset(self) -> None:
        """Test getting respondent subset."""
        analyzer = StackOverflowAnalyzer()
        output_buffer = StringIO()
        console = Console(file=output_buffer, width=120)

        with patch("air_data.cli.Prompt.ask", side_effect=["RemoteWork", "Remote"]):
            get_respondent_subset(analyzer, console)

        output = output_buffer.getvalue()
        # Should either show respondents or "No respondents found"
        assert "Remote" in output or "No respondents found" in output

        analyzer.close()

    def test_show_answer_distribution(self) -> None:
        """Test showing answer distribution."""
        analyzer = StackOverflowAnalyzer()
        output_buffer = StringIO()
        console = Console(file=output_buffer, width=120)

        with patch("air_data.cli.Prompt.ask", return_value="Age"):
            show_answer_distribution(analyzer, console)

        output = output_buffer.getvalue()
        assert "Answer Distribution for Age" in output

        analyzer.close()

    def test_main_exit_immediately(self) -> None:
        """Test main function with immediate exit."""
        with patch("air_data.cli.Prompt.ask", return_value="5"):
            with patch("sys.exit") as mock_exit:
                main()
                # Should not call sys.exit on normal exit
                mock_exit.assert_not_called()
