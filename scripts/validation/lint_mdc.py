#!/usr/bin/env python3
"""
Cross-platform line count checker for .mdc files.
Ensures .mdc files don't exceed configurable line limits with rich console output.
"""

import logging
import os
import re
import sys
import uuid
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Configure structured logging with correlation IDs
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(console=Console(), rich_tracebacks=True)],
)
logger = logging.getLogger("lint_mdc")

console = Console()

# Compile regex patterns at module level for performance
SINGLE_BRACE_PATTERN = re.compile(r"(?<!\{)\{[^{}]+\}(?!\})")
YAML_FRONTMATTER_PATTERN = re.compile(r"^---\n")

# Configuration with environment variable support
DEFAULT_LINE_LIMIT = 150
LINE_LIMIT = int(os.getenv("MDC_LINE_LIMIT", DEFAULT_LINE_LIMIT))


def sanitize_file_path(file_path_str: str) -> Path:
    """
    Sanitize and validate file path input.

    Args:
        file_path_str: Raw file path string

    Returns:
        Path: Sanitized Path object

    Raises:
        ValueError: If path contains dangerous patterns
    """
    # Check for dangerous patterns
    dangerous_patterns = ["../", "~/", "$", "`", ";", "|", "&"]
    if any(pattern in file_path_str for pattern in dangerous_patterns):
        raise ValueError(f"Potentially dangerous file path: {file_path_str}")

    # Resolve and validate path
    try:
        path = Path(file_path_str).resolve()
        # For test environments, allow paths outside CWD (like /tmp)
        # In production, you might want to be more restrictive
        if not path.exists():
            raise ValueError(f"File does not exist: {file_path_str}")
        return path
    except OSError as e:
        raise ValueError(f"Invalid file path: {file_path_str}") from e


def check_file(file_path: Path, correlation_id: str) -> tuple[bool, int]:
    """
    Check if a file exceeds line limits and validate structure.

    Args:
        file_path: Path to the file to check
        correlation_id: Unique identifier for this validation run

    Returns:
        Tuple[bool, int]: (is_valid, line_count)
    """
    logger.info(f"[{correlation_id}] Checking file: {file_path}")

    if not file_path.exists():
        logger.error(f"[{correlation_id}] File not found: {file_path}")
        console.print(f"[red]✗[/red] File {file_path} does not exist", style="red")
        return False, 0

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
            lines = content.count("\n") + 1
    except Exception as e:
        logger.error(f"[{correlation_id}] Error reading {file_path}: {e}")
        console.print(f"[red]✗[/red] Error reading {file_path}: {e}", style="red")
        return False, 0

    is_valid = True
    warnings = []

    # Check line count
    if lines > LINE_LIMIT:
        logger.warning(
            f"[{correlation_id}] Line limit exceeded: {file_path} ({lines} > {LINE_LIMIT})"
        )
        console.print(
            f"[red]✗[/red] {file_path} exceeds limit: [red]{lines}[/red] lines (max: {LINE_LIMIT})",
            style="red",
        )
        is_valid = False

    # Check for unresolved template placeholders (single braces)
    single_braces = SINGLE_BRACE_PATTERN.findall(content)
    if single_braces:
        warning_msg = f"Unresolved placeholders: {', '.join(set(single_braces))}"
        warnings.append(warning_msg)
        logger.warning(f"[{correlation_id}] {warning_msg} in {file_path}")

    # Check for required YAML front-matter
    if not YAML_FRONTMATTER_PATTERN.match(content):
        warning_msg = "Missing YAML front-matter"
        warnings.append(warning_msg)
        logger.warning(f"[{correlation_id}] {warning_msg} in {file_path}")

    # Check for required rule_type
    if "rule_type: Agent Requested" not in content:
        warning_msg = "Missing 'rule_type: Agent Requested'"
        warnings.append(warning_msg)
        logger.warning(f"[{correlation_id}] {warning_msg} in {file_path}")

    # Check for five-bucket structure (executives need all 5, specialists need 3)
    required_sections_executive = [
        "## Identity & Context",
        "## Objectives, KPIs & Mandate",
        "## Influence & Decision Power",
        "## Behaviors, Tools & Preferences",
        "## Motivations, Pain Points & Constraints",
    ]

    required_sections_specialist = [
        "## Identity & Context",
        "## Objectives & Quality Standards",
        "## Quality Gates & Behaviors",
    ]

    # Determine if this is executive or specialist based on content
    is_executive = any(
        section in content
        for section in [
            "## Influence & Decision Power",
            "## Motivations, Pain Points & Constraints",
        ]
    )

    if is_executive:
        missing_sections = [
            section for section in required_sections_executive if section not in content
        ]
        if missing_sections:
            warning_msg = f"Missing executive sections: {', '.join(missing_sections)}"
            warnings.append(warning_msg)
            logger.warning(f"[{correlation_id}] {warning_msg} in {file_path}")
    else:
        missing_sections = [
            section
            for section in required_sections_specialist
            if section not in content
        ]
        if missing_sections:
            warning_msg = f"Missing specialist sections: {', '.join(missing_sections)}"
            warnings.append(warning_msg)
            logger.warning(f"[{correlation_id}] {warning_msg} in {file_path}")

    # Display results
    if is_valid and not warnings:
        logger.info(
            f"[{correlation_id}] Validation passed: {file_path} ({lines} lines)"
        )
        console.print(
            f"[green]✓[/green] {file_path} within limit: [green]{lines}[/green] lines",
            style="green",
        )
    elif is_valid and warnings:
        logger.warning(
            f"[{correlation_id}] Validation passed with warnings: {file_path} ({lines} lines)"
        )
        console.print(
            f"[yellow]⚠[/yellow] {file_path} within limit: [yellow]{lines}[/yellow] lines (warnings)",
            style="yellow",
        )
        for warning in warnings:
            console.print(f"  [yellow]•[/yellow] {warning}")

    return is_valid, lines


def display_summary(results: list[tuple[Path, bool, int]], correlation_id: str) -> None:
    """Display a summary table of all checked files."""
    logger.info(
        f"[{correlation_id}] Generating validation summary for {len(results)} files"
    )

    table = Table(
        title="MDC File Line Count Summary",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("File", style="cyan", no_wrap=True)
    table.add_column("Lines", justify="right", style="yellow")
    table.add_column("Status", justify="center")
    table.add_column("Limit", justify="right", style="dim")

    total_files = len(results)
    valid_files = sum(1 for _, is_valid, _ in results if is_valid)
    invalid_files = total_files - valid_files

    for file_path, is_valid, line_count in results:
        status = "[green]✓ PASS[/green]" if is_valid else "[red]✗ FAIL[/red]"
        table.add_row(str(file_path), str(line_count), status, str(LINE_LIMIT))

    console.print(table)

    # Separate valid and invalid files for detailed summary
    valid_results = [(path, lines) for path, is_valid, lines in results if is_valid]
    invalid_results = [
        (path, lines) for path, is_valid, lines in results if not is_valid
    ]

    # Always show valid files summary
    if valid_results:
        console.print("\n[green]✓ PASSED FILES:[/green]")
        for file_path, line_count in valid_results:
            console.print(
                f"  [green]•[/green] {file_path} ([green]{line_count}[/green] lines)"
            )
    else:
        console.print("\n[yellow]⚠ NO FILES PASSED[/yellow]")

    # Always show failed files summary
    if invalid_results:
        console.print("\n[red]✗ FAILED FILES:[/red]")
        for file_path, line_count in invalid_results:
            console.print(
                f"  [red]•[/red] {file_path} ([red]{line_count}[/red] lines - exceeds limit)"
            )
    else:
        console.print("\n[green]✓ NO FILES FAILED[/green]")

    # Overall summary panel
    if invalid_files == 0:
        summary_text = f"[green]All {total_files} files passed validation![/green]"
        panel_style = "green"
        logger.info(f"[{correlation_id}] All files passed validation")
    else:
        summary_text = f"[red]{invalid_files}[/red] of {total_files} files failed validation\n[green]{valid_files}[/green] files passed"
        panel_style = "red"
        logger.error(
            f"[{correlation_id}] {invalid_files} of {total_files} files failed validation"
        )

    console.print(
        Panel(summary_text, title="Validation Summary", border_style=panel_style)
    )


def main():
    """Main entry point for the MDC line count checker."""
    # Generate correlation ID for this validation run
    correlation_id = str(uuid.uuid4())[:8]
    logger.info(
        f"[{correlation_id}] Starting MDC validation with line limit: {LINE_LIMIT}"
    )

    if len(sys.argv) < 2:
        console.print(
            Panel(
                f"Usage: [cyan]python lint_mdc.py <file1> [file2] ...[/cyan]\n\n"
                f"Checks .mdc files to ensure they don't exceed {LINE_LIMIT} lines.\n\n"
                f"Configuration:\n"
                f"• Set MDC_LINE_LIMIT environment variable to override default ({DEFAULT_LINE_LIMIT})\n"
                f"• Current limit: {LINE_LIMIT} lines",
                title="MDC Line Count Checker",
                border_style="blue",
            )
        )
        sys.exit(1)

    console.print(
        Panel(
            f"Checking .mdc files for line count compliance (limit: {LINE_LIMIT})...",
            title="MDC Line Count Validator",
            border_style="blue",
        )
    )

    results: list[tuple[Path, bool, int]] = []
    all_valid = True

    # Sanitize and validate all file paths first
    try:
        sanitized_paths = [sanitize_file_path(arg) for arg in sys.argv[1:]]
    except ValueError as e:
        logger.error(f"[{correlation_id}] Path validation failed: {e}")
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Validating files...", total=len(sanitized_paths))

        for file_path in sanitized_paths:
            progress.update(task, description=f"Checking {file_path.name}...")

            is_valid, line_count = check_file(file_path, correlation_id)
            results.append((file_path, is_valid, line_count))

            if not is_valid:
                all_valid = False

            progress.advance(task)

    console.print()  # Add spacing
    display_summary(results, correlation_id)

    if not all_valid:
        logger.error(
            f"[{correlation_id}] Validation failed - some files exceeded limits"
        )
        console.print(
            f"\n[red]Some files exceeded the {LINE_LIMIT}-line limit. Please review and refactor.[/red]"
        )
        sys.exit(1)
    else:
        logger.info(f"[{correlation_id}] All files are compliant")
        console.print("\n[green]All files are compliant! 🎉[/green]")


if __name__ == "__main__":
    main()
