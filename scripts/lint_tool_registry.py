#!/usr/bin/env python3
"""
Tool Registry Linter - Validates tool_registry.json structure and integrity.
Ensures tool registry maintains proper structure and referential integrity.
"""

import json
import logging
import sys
import uuid
from pathlib import Path
from typing import Dict, List, Tuple

from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

# Configure structured logging with correlation IDs
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(console=Console(), rich_tracebacks=True)],
)
logger = logging.getLogger("lint_tool_registry")

console = Console()


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
        if not path.exists():
            raise ValueError(f"File does not exist: {file_path_str}")
        return path
    except OSError as e:
        raise ValueError(f"Invalid file path: {file_path_str}") from e


def validate_json_structure(
    registry_data: Dict, correlation_id: str
) -> Tuple[bool, List[str]]:
    """
    Validate the basic JSON structure of the tool registry.

    Args:
        registry_data: Parsed JSON data
        correlation_id: Unique identifier for this validation run

    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)
    """
    logger.info(f"[{correlation_id}] Validating JSON structure")

    errors = []

    # Check for required top-level keys
    required_keys = ["tool_categories", "domain_mappings"]
    for key in required_keys:
        if key not in registry_data:
            errors.append(f"Missing required top-level key: '{key}'")

    # Validate tool_categories structure
    if "tool_categories" in registry_data:
        tool_categories = registry_data["tool_categories"]
        if not isinstance(tool_categories, dict):
            errors.append("'tool_categories' must be a dictionary")
        else:
            for category_name, category_data in tool_categories.items():
                if not isinstance(category_data, dict):
                    errors.append(f"Category '{category_name}' must be a dictionary")
                    continue

                # Check required fields in each category
                if "description" not in category_data:
                    errors.append(
                        f"Category '{category_name}' missing 'description' field"
                    )
                if "tools" not in category_data:
                    errors.append(f"Category '{category_name}' missing 'tools' field")
                elif not isinstance(category_data["tools"], list):
                    errors.append(f"Category '{category_name}' 'tools' must be a list")

    # Validate domain_mappings structure
    if "domain_mappings" in registry_data:
        domain_mappings = registry_data["domain_mappings"]
        if not isinstance(domain_mappings, dict):
            errors.append("'domain_mappings' must be a dictionary")
        else:
            for domain_name, categories in domain_mappings.items():
                if not isinstance(categories, list):
                    errors.append(
                        f"Domain '{domain_name}' mapping must be a list of strings"
                    )
                elif not all(isinstance(cat, str) for cat in categories):
                    errors.append(
                        f"Domain '{domain_name}' mapping must contain only strings"
                    )

    is_valid = len(errors) == 0

    if is_valid:
        logger.info(f"[{correlation_id}] JSON structure validation passed")
    else:
        logger.error(
            f"[{correlation_id}] JSON structure validation failed with {len(errors)} errors"
        )

    return is_valid, errors


def validate_referential_integrity(
    registry_data: Dict, correlation_id: str
) -> Tuple[bool, List[str]]:
    """
    Validate referential integrity between domain_mappings and tool_categories.

    Args:
        registry_data: Parsed JSON data
        correlation_id: Unique identifier for this validation run

    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)
    """
    logger.info(f"[{correlation_id}] Validating referential integrity")

    errors = []

    if "tool_categories" not in registry_data or "domain_mappings" not in registry_data:
        # Structure validation should have caught this
        return False, ["Cannot validate referential integrity without required keys"]

    tool_categories = registry_data["tool_categories"]
    domain_mappings = registry_data["domain_mappings"]

    # Get all available category names
    available_categories = set(tool_categories.keys())

    # Check that all referenced categories exist
    for domain_name, categories in domain_mappings.items():
        for category in categories:
            if category not in available_categories:
                errors.append(
                    f"Domain '{domain_name}' references non-existent category '{category}'"
                )

    # Check for unused categories (warning, not error)
    referenced_categories = set()
    for categories in domain_mappings.values():
        referenced_categories.update(categories)

    unused_categories = available_categories - referenced_categories
    if unused_categories:
        logger.warning(
            f"[{correlation_id}] Unused categories found: {', '.join(sorted(unused_categories))}"
        )
        console.print(
            f"[yellow]⚠[/yellow] Unused categories: {', '.join(sorted(unused_categories))}"
        )

    is_valid = len(errors) == 0

    if is_valid:
        logger.info(f"[{correlation_id}] Referential integrity validation passed")
    else:
        logger.error(
            f"[{correlation_id}] Referential integrity validation failed with {len(errors)} errors"
        )

    return is_valid, errors


def validate_tool_registry(file_path: Path, correlation_id: str) -> Tuple[bool, Dict]:
    """
    Validate the tool registry file.

    Args:
        file_path: Path to the tool registry file
        correlation_id: Unique identifier for this validation run

    Returns:
        Tuple[bool, Dict]: (is_valid, registry_data)
    """
    logger.info(f"[{correlation_id}] Validating tool registry: {file_path}")

    # Load and parse JSON
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            registry_data = json.load(f)
        logger.info(f"[{correlation_id}] Successfully loaded JSON from {file_path}")
    except json.JSONDecodeError as e:
        logger.error(f"[{correlation_id}] Invalid JSON in {file_path}: {e}")
        console.print(f"[red]✗[/red] Invalid JSON in {file_path}: {e}", style="red")
        return False, {}
    except Exception as e:
        logger.error(f"[{correlation_id}] Error reading {file_path}: {e}")
        console.print(f"[red]✗[/red] Error reading {file_path}: {e}", style="red")
        return False, {}

    all_errors = []

    # Validate JSON structure
    structure_valid, structure_errors = validate_json_structure(
        registry_data, correlation_id
    )
    all_errors.extend(structure_errors)

    # Only validate referential integrity if structure is valid
    if structure_valid:
        integrity_valid, integrity_errors = validate_referential_integrity(
            registry_data, correlation_id
        )
        all_errors.extend(integrity_errors)
    else:
        integrity_valid = False

    is_valid = structure_valid and integrity_valid

    # Display results
    if is_valid:
        logger.info(f"[{correlation_id}] Tool registry validation passed")
        console.print(f"[green]✓[/green] {file_path} validation passed", style="green")
    else:
        logger.error(f"[{correlation_id}] Tool registry validation failed")
        console.print(f"[red]✗[/red] {file_path} validation failed", style="red")
        for error in all_errors:
            console.print(f"  [red]•[/red] {error}")

    return is_valid, registry_data


def display_summary(
    file_path: Path, is_valid: bool, registry_data: Dict, correlation_id: str
) -> None:
    """Display a summary of the tool registry validation."""
    logger.info(f"[{correlation_id}] Generating validation summary")

    table = Table(
        title="Tool Registry Validation Summary",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right", style="yellow")
    table.add_column("Status", justify="center")

    if registry_data:
        tool_categories_count = len(registry_data.get("tool_categories", {}))
        domain_mappings_count = len(registry_data.get("domain_mappings", {}))

        # Count total tools
        total_tools = 0
        for category_data in registry_data.get("tool_categories", {}).values():
            if isinstance(category_data, dict) and "tools" in category_data:
                total_tools += len(category_data["tools"])
    else:
        tool_categories_count = 0
        domain_mappings_count = 0
        total_tools = 0

    status = "[green]✓ VALID[/green]" if is_valid else "[red]✗ INVALID[/red]"

    table.add_row("File", str(file_path), status)
    table.add_row("Tool Categories", str(tool_categories_count), "")
    table.add_row("Domain Mappings", str(domain_mappings_count), "")
    table.add_row("Total Tools", str(total_tools), "")

    console.print(table)

    if is_valid:
        console.print(
            "\n[green]✓ Tool registry validation completed successfully[/green]"
        )
    else:
        console.print("\n[red]✗ Tool registry validation failed[/red]")


def main():
    """Main entry point for tool registry linting."""
    correlation_id = str(uuid.uuid4())[:8]
    logger.info(f"[{correlation_id}] Starting tool registry linter")

    if len(sys.argv) != 2:
        console.print(
            "[red]Error:[/red] Usage: python lint_tool_registry.py <path_to_tool_registry.json>"
        )
        sys.exit(1)

    registry_path_str = sys.argv[1]

    try:
        registry_path = sanitize_file_path(registry_path_str)
    except ValueError as e:
        logger.error(f"[{correlation_id}] {e}")
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)

    # Validate the tool registry
    is_valid, registry_data = validate_tool_registry(registry_path, correlation_id)

    # Display summary
    display_summary(registry_path, is_valid, registry_data, correlation_id)

    # Exit with appropriate code
    if is_valid:
        logger.info(f"[{correlation_id}] Tool registry linter completed successfully")
        sys.exit(0)
    else:
        logger.error(f"[{correlation_id}] Tool registry linter failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
