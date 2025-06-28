#!/usr/bin/env python3
"""
CLI interface for StackOverflow Analyzer with star schema functionality.
"""

import sys

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from air_data.stackoverflow_analyzer import StackOverflowAnalyzer


def display_survey_structure(analyzer: StackOverflowAnalyzer, console: Console) -> None:
    """Display the survey structure (list of questions)."""
    console.print("\n[bold blue]Survey Structure[/bold blue]")

    structure = analyzer.get_survey_structure()

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=3)
    table.add_column("Column", style="cyan", width=25)
    table.add_column("Type", style="green", width=4)
    table.add_column("# Options", style="yellow", width=8)
    table.add_column("Question Text", width=80)

    for _, row in structure.iterrows():
        question_text = str(row["question_text"])
        table.add_row(
            str(row["question_id"]),
            str(row["column_name"]),
            str(row["type"]),
            str(row["num_answer_options"]),
            question_text[:77] + "..." if len(question_text) > 80 else question_text,
        )

    console.print(table)


def search_questions(analyzer: StackOverflowAnalyzer, console: Console) -> None:
    """Search for specific question or option."""
    search_term = Prompt.ask("\n[bold cyan]Enter search term[/bold cyan]")

    results = analyzer.search_questions(search_term)

    if results.empty:
        console.print(f"[red]No results found for '{search_term}'[/red]")
        return

    console.print(f"\n[bold blue]Search Results for '{search_term}'[/bold blue]")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Q ID", style="dim", width=4)
    table.add_column("Column", style="cyan", width=25)
    table.add_column("Type", style="green", width=4)
    table.add_column("Answer Option", style="yellow", width=30)
    table.add_column("Question Text", width=60)

    for _, row in results.iterrows():
        question_text = str(row["question_text"])
        answer_value = row["answer_value"]
        table.add_row(
            str(row["question_id"]),
            str(row["column_name"]),
            str(row["type"]),
            str(answer_value) if answer_value is not None else "",
            question_text[:57] + "..." if len(question_text) > 60 else question_text,
        )

    console.print(table)


def get_respondent_subset(analyzer: StackOverflowAnalyzer, console: Console) -> None:
    """Make respondents subsets based on question+option."""
    question_column = Prompt.ask("\n[bold cyan]Enter question column name[/bold cyan]")
    answer_option = Prompt.ask("[bold cyan]Enter answer option[/bold cyan]")

    subset = analyzer.get_respondent_subset(question_column, answer_option)

    if subset.empty:
        console.print(
            f"[red]No respondents found for {question_column} = '{answer_option}'[/red]"
        )
        return

    console.print(
        f"\n[bold blue]Respondents who answered '{answer_option}' for {question_column}[/bold blue]"
    )
    console.print(f"[green]Total: {len(subset)} respondents[/green]")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=4)
    table.add_column("Main Branch", style="cyan", width=20)
    table.add_column("Age", style="green", width=15)
    table.add_column("Country", style="yellow", width=20)
    table.add_column("Dev Type", width=25)
    table.add_column("Years Code", width=10)

    # Show first 20 rows
    for _, row in subset.head(20).iterrows():
        table.add_row(
            str(row["respondent_id"]),
            str(row["MainBranch"]) if row["MainBranch"] is not None else "N/A",
            str(row["Age"]) if row["Age"] is not None else "N/A",
            str(row["Country"]) if row["Country"] is not None else "N/A",
            str(row["DevType"]) if row["DevType"] is not None else "N/A",
            str(row["YearsCode"]) if row["YearsCode"] is not None else "N/A",
        )

    if len(subset) > 20:
        console.print(f"[dim]... and {len(subset) - 20} more respondents[/dim]")

    console.print(table)


def show_answer_distribution(analyzer: StackOverflowAnalyzer, console: Console) -> None:
    """Display distribution of answers for SC and MC questions."""
    question_column = Prompt.ask("\n[bold cyan]Enter question column name[/bold cyan]")

    distribution = analyzer.get_answer_distribution(question_column)

    if distribution.empty:
        console.print(f"[red]No distribution data found for '{question_column}'[/red]")
        return

    question_type = (
        distribution.iloc[0]["type"] if not distribution.empty else "Unknown"
    )
    console.print(
        f"\n[bold blue]Answer Distribution for {question_column} ({question_type})[/bold blue]"
    )

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Answer", style="cyan", width=40)
    table.add_column("Count", style="green", width=8)
    table.add_column("Percentage", style="yellow", width=10)
    table.add_column("Bar", width=30)

    max_count = distribution["response_count"].max()

    for _, row in distribution.iterrows():
        bar_length = int((row["response_count"] / max_count) * 25)
        bar = "█" * bar_length + "░" * (25 - bar_length)

        table.add_row(
            str(row["answer_value"]),
            str(row["response_count"]),
            f"{row['percentage']:.1f}%",
            bar,
        )

    console.print(table)


def main() -> None:
    """Main CLI interface."""
    console = Console()

    console.print(
        Panel.fit(
            "[bold blue]StackOverflow Survey Analyzer[/bold blue]\n"
            "Analyze survey data using star schema",
            border_style="blue",
        )
    )

    try:
        analyzer = StackOverflowAnalyzer()
        console.print(
            "[green]✓ Data loaded and star schema created successfully![/green]"
        )

        while True:
            console.print("\n[bold cyan]Available Commands:[/bold cyan]")
            console.print("1. Display survey structure")
            console.print("2. Search questions/options")
            console.print("3. Get respondent subset")
            console.print("4. Show answer distribution")
            console.print("5. Exit")

            choice = Prompt.ask(
                "\n[bold yellow]Enter your choice (1-5)[/bold yellow]",
                choices=["1", "2", "3", "4", "5"],
            )

            if choice == "1":
                display_survey_structure(analyzer, console)
            elif choice == "2":
                search_questions(analyzer, console)
            elif choice == "3":
                get_respondent_subset(analyzer, console)
            elif choice == "4":
                show_answer_distribution(analyzer, console)
            elif choice == "5":
                console.print("[green]Goodbye![/green]")
                break

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    finally:
        if "analyzer" in locals():
            analyzer.close()


if __name__ == "__main__":
    main()
