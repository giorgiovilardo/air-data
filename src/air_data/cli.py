from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from air_data.stackoverflow_analyzer import StackOverflowAnalyzer


def display_survey_structure(
    analyzer: StackOverflowAnalyzer, *, sort_by: Optional[str] = None
) -> None:
    """
    Display the survey structure (list of questions) to the console.

    Args:
        analyzer: The StackOverflowAnalyzer instance
        sort_by: Optional column to sort by
    """
    console = Console()

    # Get the survey structure
    survey_structure = analyzer.get_survey_structure(sort_by=sort_by)

    # Create a table
    table = Table(title="Survey Structure")
    table.add_column("Column", style="cyan")
    table.add_column("Question", style="green")
    table.add_column("Type", style="magenta")

    # Add rows to the table
    for _, row in survey_structure.iterrows():
        table.add_row(row["column"], row["question_text"], row["type"])

    # Display the table
    console.print(table)


def search_questions(analyzer: StackOverflowAnalyzer, *, search_term: str) -> None:
    """
    Search for questions containing the specified search term.

    Args:
        analyzer: The StackOverflowAnalyzer instance
        search_term: The term to search for
    """
    console = Console()

    # Search for questions
    results = analyzer.search_questions(search_term=search_term)

    if len(results) == 0:
        console.print(
            f"No questions found containing '{search_term}'", style="bold red"
        )
        return

    # Create a table
    table = Table(title=f"Questions containing '{search_term}'")
    table.add_column("Column", style="cyan")
    table.add_column("Question", style="green")
    table.add_column("Type", style="magenta")

    # Add rows to the table
    for _, row in results.iterrows():
        table.add_row(row["column"], row["question_text"], row["type"])

    # Display the table
    console.print(table)


def display_answer_distribution(
    analyzer: StackOverflowAnalyzer, *, column: str
) -> None:
    """
    Display the distribution of answers for a specific question.

    Args:
        analyzer: The StackOverflowAnalyzer instance
        column: The column (question) to get the distribution for
    """
    console = Console()

    # Get the question text and type
    question_info = analyzer.search_questions(search_term=column)
    if len(question_info) == 0:
        console.print(f"Question '{column}' not found", style="bold red")
        return

    question_text = question_info.iloc[0]["question_text"]
    question_type = question_info.iloc[0]["type"]

    # Get the distribution
    distribution = analyzer.get_answer_distribution(column=column)

    if len(distribution) == 0:
        console.print(f"No data available for question '{column}'", style="bold red")
        return

    # Create a table
    table = Table(title=f"Answer Distribution for '{question_text}' ({question_type})")
    table.add_column("Option", style="cyan")
    table.add_column("Count", style="green", justify="right")
    table.add_column("Percentage", style="magenta", justify="right")

    # Add rows to the table
    for _, row in distribution.iterrows():
        table.add_row(
            str(row["option"]), str(row["count"]), f"{row['percentage']:.2f}%"
        )

    # Display the table
    console.print(table)


def main() -> None:
    """
    Main CLI function.
    """
    import os

    console = Console()

    # Welcome message
    console.print("Stack Overflow Survey Analyzer", style="bold blue")
    console.print("--------------------------------", style="bold blue")

    # Check for custom data files in environment variables
    data_file = os.environ.get("SO_DATA_FILE")
    schema_file = os.environ.get("SO_SCHEMA_FILE")

    # If environment variables are not set, use sample data
    if not data_file or not schema_file:
        base_dir = Path(__file__).parent / "so_data"
        data_file = str(base_dir / "so_2024_sample.csv")
        schema_file = str(base_dir / "so_2024_raw_schema.csv")
        console.print("Using sample data files", style="dim")
    else:
        console.print(f"Using custom data file: {data_file}", style="dim")
        console.print(f"Using custom schema file: {schema_file}", style="dim")

    analyzer = StackOverflowAnalyzer(
        data_file=data_file,
        schema_file=schema_file,
    )

    while True:
        console.print("\nOptions:", style="bold")
        console.print("1. Display survey structure")
        console.print("2. Search for questions")
        console.print("3. Create respondent subset")
        console.print("4. Display answer distribution")
        console.print("5. Exit")

        choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4", "5"])

        if choice == "1":
            display_survey_structure(analyzer)

        elif choice == "2":
            search_term = Prompt.ask("Enter search term")
            search_questions(analyzer, search_term=search_term)

        elif choice == "3":
            column = Prompt.ask("Enter column name")
            option = Prompt.ask("Enter option (leave empty for all non-null values)")

            try:
                subset = analyzer.create_respondent_subset(column=column, option=option)
                count = subset.conn.execute("SELECT COUNT(*) FROM so_data").fetchone()[  # type: ignore
                    0
                ]
                console.print(
                    f"Created subset with {count} respondents", style="bold green"
                )

                # Use the subset for further analysis
                analyzer = subset
            except Exception as e:
                console.print(f"Error creating subset: {e}", style="bold red")

        elif choice == "4":
            column = Prompt.ask("Enter column name")
            display_answer_distribution(analyzer, column=column)

        elif choice == "5":
            console.print("Goodbye!", style="bold blue")
            break


if __name__ == "__main__":
    main()
