from typing import cast

import typer
from rich.console import Console
from rich.markup import escape  # Import escape
from rich.table import Table
from rich.text import Text  # Import Text

from library_explorer.data.loader import DataRepository
from library_explorer.data.models import Tool  # Import Tool for type hinting
from library_explorer.data.validator import validate_data

app = typer.Typer(
    name="library-explorer",
    help="A CLI tool to explore Role Library and Tool Registry.",
    add_completion=False,
)
console = Console()

# Create a subcommand for browse
browse_app = typer.Typer(help="Browse Roles, Tools, or Domains.")
app.add_typer(browse_app, name="browse")


@browse_app.command("tools")
def browse_tools(
    data_path: str = typer.Option(
        ".cursor/rules/tools",
        "--data-path",
        "-p",
        help="Path to the data directory containing tool_registry.json.",
    ),
    format_output: str = typer.Option(
        "table",
        "--format",
        "-f",
        help="Output format: table, list.",
        case_sensitive=False,
    ),
    # TODO: Add --no-emoji options later
) -> None:
    """Browse available tools from the Tool Registry."""
    repo = DataRepository(data_path=data_path)
    repo.load_data()

    if not validate_data(repo):
        # Validation itself prints detailed errors. We might add a summary here.
        console.print("[bold red]Data validation failed. Cannot browse tools.[/bold]")
        raise typer.Exit(code=1)

    if not repo.tools:
        console.print(
            "[yellow]No tools found or loaded even after validation. "
            "Ensure 'tool_registry.json' exists and is correctly formatted.[/yellow]"
        )
        raise typer.Exit(code=1)

    # Cast to List[Tool] for sorted_tools if your loader guarantees Tool instances
    sorted_tools: list[Tool] = cast(
        list[Tool], sorted(repo.list_tools(), key=lambda t: (t.category, t.name))
    )

    if not sorted_tools:
        console.print("[yellow]No tools to display.[/yellow]")
        return

    if format_output == "list":
        for tool in sorted_tools:
            name_text = Text(escape(tool.name), style="bold cyan")
            console.print(name_text)

            category_text = Text(
                f"  Category: {escape(tool.category)}", style="magenta"
            )
            console.print(category_text)

            description_text = Text(
                f"  Description: {escape(tool.description or '-')}", style="green"
            )
            console.print(description_text)
            console.print()  # Add a blank line for separation
    elif format_output == "table":
        table = Table(title="Available Tools", show_lines=True)
        table.add_column("Name", style="cyan", no_wrap=True, min_width=20)
        table.add_column("Category", style="magenta", min_width=15)
        table.add_column("Description", style="green", min_width=30, overflow="fold")
        # table.add_column("Domains", style="blue", min_width=15)
        # Add when domains are populated for tools

        for tool in sorted_tools:
            table.add_row(
                tool.name,
                tool.category,
                tool.description or "-",
                # ", ".join(tool.domains) or "-" # Add when domains are populated
            )
        console.print(table)
    else:
        console.print(
            f"[red]Error: Invalid format '{format_output}'. "
            "Choose from 'table' or 'list'.[/red]"
        )
        raise typer.Exit(code=1)


@app.command()
def load(
    data_path: str = typer.Option(
        ".cursor/rules/tools", "--data-path", "-p", help="Path to the data directory."
    ),
) -> None:
    """Load and print tool names from the data repository. Runs validation."""
    console.print(f"Loading data from: {data_path}")
    repo = DataRepository(data_path=data_path)
    repo.load_data()

    validate_data(repo)  # Run validation, it will print its own summary

    if repo.tools:
        console.print("\nLoaded Tools:")
        for tool_id, tool in repo.tools.items():
            console.print(f"- {tool.name} (ID: {tool_id})")
    else:
        console.print("No tools found or loaded.")


@app.command()
def validate(
    data_path: str = typer.Option(
        ".cursor/rules/tools", help="Path to the data directory."
    ),
) -> None:
    """Load and validate data from the repository."""
    console.print(f"Validating data from: {data_path}")
    repo = DataRepository(data_path=data_path)
    repo.load_data()
    validate_data(repo)


@app.command()
def main() -> None:
    """
    A CLI tool to explore Role Library and Tool Registry.
    """
    console.print("Library Explorer initialized! Use --help to see commands.")


if __name__ == "__main__":
    app()
