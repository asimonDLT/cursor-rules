#!/usr/bin/env python3
"""
Cross-platform line count checker for .mdc files.
Ensures .mdc files don't exceed 150 lines with rich console output.
"""
import sys
from pathlib import Path
from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text


console = Console()


def check_file(file_path: Path) -> tuple[bool, int]:
    """
    Check if a file exceeds 150 lines and validate structure.
    
    Returns:
        tuple[bool, int]: (is_valid, line_count)
    """
    if not file_path.exists():
        console.print(f"[red]✗[/red] File {file_path} does not exist", style="red")
        return False, 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.count('\n') + 1
    except Exception as e:
        console.print(f"[red]✗[/red] Error reading {file_path}: {e}", style="red")
        return False, 0
    
    is_valid = True
    warnings = []
    
    # Check line count
    if lines > 150:
        console.print(
            f"[red]✗[/red] {file_path} exceeds limit: [red]{lines}[/red] lines (max: 150)",
            style="red"
        )
        is_valid = False
    
    # Check for unresolved template placeholders (single braces)
    import re
    single_brace_pattern = r'\{[^{][^}]*\}'
    single_braces = re.findall(single_brace_pattern, content)
    if single_braces:
        warnings.append(f"Unresolved placeholders: {', '.join(set(single_braces))}")
    
    # Check for required YAML front-matter
    if not content.startswith('---\n'):
        warnings.append("Missing YAML front-matter")
    
    # Check for required rule_type
    if 'rule_type: Agent Requested' not in content:
        warnings.append("Missing 'rule_type: Agent Requested'")
    
    # Check for five-bucket structure (executives need all 5, specialists need 3)
    required_sections_executive = [
        "## Identity & Context",
        "## Objectives, KPIs & Mandate", 
        "## Influence & Decision Power",
        "## Behaviors, Tools & Preferences",
        "## Motivations, Pain Points & Constraints"
    ]
    
    required_sections_specialist = [
        "## Identity & Context",
        "## Objectives & Quality Standards",
        "## Quality Gates & Behaviors"
    ]
    
    # Determine if this is executive or specialist based on content
    is_executive = any(section in content for section in ["## Influence & Decision Power", "## Motivations, Pain Points & Constraints"])
    
    if is_executive:
        missing_sections = [section for section in required_sections_executive if section not in content]
        if missing_sections:
            warnings.append(f"Missing executive sections: {', '.join(missing_sections)}")
    else:
        missing_sections = [section for section in required_sections_specialist if section not in content]
        if missing_sections:
            warnings.append(f"Missing specialist sections: {', '.join(missing_sections)}")
    
    # Display results
    if is_valid and not warnings:
        console.print(
            f"[green]✓[/green] {file_path} within limit: [green]{lines}[/green] lines",
            style="green"
        )
    elif is_valid and warnings:
        console.print(
            f"[yellow]⚠[/yellow] {file_path} within limit: [yellow]{lines}[/yellow] lines (warnings)",
            style="yellow"
        )
        for warning in warnings:
            console.print(f"  [yellow]•[/yellow] {warning}")
    
    return is_valid, lines


def display_summary(results: List[tuple[Path, bool, int]]) -> None:
    """Display a summary table of all checked files."""
    table = Table(title="MDC File Line Count Summary", show_header=True, header_style="bold magenta")
    table.add_column("File", style="cyan", no_wrap=True)
    table.add_column("Lines", justify="right", style="yellow")
    table.add_column("Status", justify="center")
    table.add_column("Limit", justify="right", style="dim")
    
    total_files = len(results)
    valid_files = sum(1 for _, is_valid, _ in results if is_valid)
    invalid_files = total_files - valid_files
    
    for file_path, is_valid, line_count in results:
        status = "[green]✓ PASS[/green]" if is_valid else "[red]✗ FAIL[/red]"
        table.add_row(
            str(file_path),
            str(line_count),
            status,
            "150"
        )
    
    console.print(table)
    
    # Separate valid and invalid files for detailed summary
    valid_results = [(path, lines) for path, is_valid, lines in results if is_valid]
    invalid_results = [(path, lines) for path, is_valid, lines in results if not is_valid]
    
    # Always show valid files summary
    if valid_results:
        console.print("\n[green]✓ PASSED FILES:[/green]")
        for file_path, line_count in valid_results:
            console.print(f"  [green]•[/green] {file_path} ([green]{line_count}[/green] lines)")
    else:
        console.print("\n[yellow]⚠ NO FILES PASSED[/yellow]")
    
    # Always show failed files summary
    if invalid_results:
        console.print("\n[red]✗ FAILED FILES:[/red]")
        for file_path, line_count in invalid_results:
            console.print(f"  [red]•[/red] {file_path} ([red]{line_count}[/red] lines - exceeds limit)")
    else:
        console.print("\n[green]✓ NO FILES FAILED[/green]")
    
    # Overall summary panel
    if invalid_files == 0:
        summary_text = f"[green]All {total_files} files passed validation![/green]"
        panel_style = "green"
    else:
        summary_text = f"[red]{invalid_files}[/red] of {total_files} files failed validation\n[green]{valid_files}[/green] files passed"
        panel_style = "red"
    
    console.print(
        Panel(
            summary_text,
            title="Validation Summary",
            border_style=panel_style
        )
    )


def main():
    """Main entry point for the MDC line count checker."""
    if len(sys.argv) < 2:
        console.print(
            Panel(
                "Usage: [cyan]python lint_mdc.py <file1> [file2] ...[/cyan]\n\n"
                "Checks .mdc files to ensure they don't exceed 150 lines.",
                title="MDC Line Count Checker",
                border_style="blue"
            )
        )
        sys.exit(1)
    
    console.print(
        Panel(
            "Checking .mdc files for line count compliance...",
            title="MDC Line Count Validator",
            border_style="blue"
        )
    )
    
    results: List[tuple[Path, bool, int]] = []
    all_valid = True
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("Validating files...", total=len(sys.argv[1:]))
        
        for file_arg in sys.argv[1:]:
            file_path = Path(file_arg)
            progress.update(task, description=f"Checking {file_path.name}...")
            
            is_valid, line_count = check_file(file_path)
            results.append((file_path, is_valid, line_count))
            
            if not is_valid:
                all_valid = False
            
            progress.advance(task)
    
    console.print()  # Add spacing
    display_summary(results)
    
    if not all_valid:
        console.print(
            "\n[red]Some files exceeded the 150-line limit. Please review and refactor.[/red]"
        )
        sys.exit(1)
    else:
        console.print(
            "\n[green]All files are compliant! 🎉[/green]"
        )


if __name__ == "__main__":
    main() 