#!/usr/bin/env python3
"""
Role Library Linter - Validates role_library.json structure and integrity.
Ensures role library maintains proper structure and cross-references.
"""

import json
import logging
import sys
import uuid
from pathlib import Path
from typing import Dict, List, Tuple, Any

from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

# Configure structured logging with correlation IDs
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(console=Console(), rich_tracebacks=True)],
)
logger = logging.getLogger("lint_role_library")

console = Console()

# Role type validation constants
VALID_ROLE_TYPES = {"executive", "specialist"}

REQUIRED_EXECUTIVE_BUCKETS = {
    "identity",
    "objectives",
    "influence",
    "behaviors",
    "motivations",
}

REQUIRED_SPECIALIST_BUCKETS = {"identity", "objectives"}

REQUIRED_IDENTITY_FIELDS = {"scope", "seniority", "span_of_control"}

REQUIRED_OBJECTIVES_FIELDS = {"top_objectives", "kpis"}


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


def load_tool_registry(correlation_id: str) -> Dict[str, Any]:
    """
    Load tool registry for cross-reference validation.

    Args:
        correlation_id: Unique identifier for this validation run

    Returns:
        Dict: Tool registry data or empty dict if not found
    """
    tool_registry_path = (
        Path(__file__).parent.parent / ".cursor/rules/tools/tool_registry.json"
    )

    if not tool_registry_path.exists():
        logger.warning(
            f"[{correlation_id}] Tool registry not found at {tool_registry_path}"
        )
        return {}

    try:
        with open(tool_registry_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        logger.warning(f"[{correlation_id}] Could not load tool registry: {e}")
        return {}


def validate_json_structure(
    library_data: Dict, correlation_id: str
) -> Tuple[bool, List[str]]:
    """
    Validate the basic JSON structure of the role library.

    Args:
        library_data: Parsed JSON data
        correlation_id: Unique identifier for this validation run

    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)
    """
    logger.info(f"[{correlation_id}] Validating JSON structure")

    errors = []

    # Check for required top-level role types
    if not isinstance(library_data, dict):
        errors.append("Role library must be a dictionary")
        return False, errors

    # Validate that we have at least one valid role type
    found_role_types = set(library_data.keys()) & VALID_ROLE_TYPES
    if not found_role_types:
        errors.append(
            f"No valid role types found. Expected one of: {', '.join(VALID_ROLE_TYPES)}"
        )

    # Check for unknown role types
    unknown_types = set(library_data.keys()) - VALID_ROLE_TYPES
    if unknown_types:
        errors.append(f"Unknown role types found: {', '.join(unknown_types)}")

    # Validate structure of each role type
    for role_type, roles_by_type in library_data.items():
        if role_type not in VALID_ROLE_TYPES:
            continue  # Already flagged above

        if not isinstance(roles_by_type, dict):
            errors.append(f"Role type '{role_type}' must contain a dictionary of roles")
            continue

        for role_name, role_data in roles_by_type.items():
            if not isinstance(role_data, dict):
                errors.append(
                    f"Role '{role_name}' in '{role_type}' must be a dictionary"
                )
                continue

            # Validate required buckets based on role type
            if role_type == "executive":
                missing_buckets = REQUIRED_EXECUTIVE_BUCKETS - set(role_data.keys())
                if missing_buckets:
                    errors.append(
                        f"Executive role '{role_name}' missing required buckets: {', '.join(sorted(missing_buckets))}"
                    )
            elif role_type == "specialist":
                missing_buckets = REQUIRED_SPECIALIST_BUCKETS - set(role_data.keys())
                if missing_buckets:
                    errors.append(
                        f"Specialist role '{role_name}' missing required buckets: {', '.join(sorted(missing_buckets))}"
                    )

                # Specialists need either standards OR behaviors
                has_standards_or_behaviors = (
                    "standards" in role_data or "behaviors" in role_data
                )
                if not has_standards_or_behaviors:
                    errors.append(
                        f"Specialist role '{role_name}' missing both 'standards' and 'behaviors' buckets"
                    )

    is_valid = len(errors) == 0

    if is_valid:
        logger.info(f"[{correlation_id}] JSON structure validation passed")
    else:
        logger.error(
            f"[{correlation_id}] JSON structure validation failed with {len(errors)} errors"
        )

    return is_valid, errors


def validate_field_structure(
    library_data: Dict, correlation_id: str
) -> Tuple[bool, List[str]]:
    """
    Validate the structure of individual fields within roles.

    Args:
        library_data: Parsed JSON data
        correlation_id: Unique identifier for this validation run

    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)
    """
    logger.info(f"[{correlation_id}] Validating field structures")

    errors = []

    for role_type, roles_by_type in library_data.items():
        if role_type not in VALID_ROLE_TYPES:
            continue

        for role_name, role_data in roles_by_type.items():
            if not isinstance(role_data, dict):
                continue  # Already flagged in structure validation

            # Validate identity fields
            if "identity" in role_data:
                identity = role_data["identity"]
                if not isinstance(identity, dict):
                    errors.append(f"Role '{role_name}' identity must be a dictionary")
                else:
                    missing_fields = REQUIRED_IDENTITY_FIELDS - set(identity.keys())
                    if missing_fields:
                        errors.append(
                            f"Role '{role_name}' identity missing fields: {', '.join(sorted(missing_fields))}"
                        )

            # Validate objectives fields
            if "objectives" in role_data:
                objectives = role_data["objectives"]
                if not isinstance(objectives, dict):
                    errors.append(f"Role '{role_name}' objectives must be a dictionary")
                else:
                    missing_fields = REQUIRED_OBJECTIVES_FIELDS - set(objectives.keys())
                    if missing_fields:
                        errors.append(
                            f"Role '{role_name}' objectives missing fields: {', '.join(sorted(missing_fields))}"
                        )

                    # Validate that objectives fields are arrays
                    for field in ["top_objectives", "kpis"]:
                        if field in objectives and not isinstance(
                            objectives[field], list
                        ):
                            errors.append(
                                f"Role '{role_name}' objectives.{field} must be an array"
                            )

            # Validate behaviors structure (for specialists with tool_domains)
            if "behaviors" in role_data:
                behaviors = role_data["behaviors"]
                if not isinstance(behaviors, dict):
                    errors.append(f"Role '{role_name}' behaviors must be a dictionary")
                else:
                    # Validate tool_domains if present
                    if "tool_domains" in behaviors:
                        tool_domains = behaviors["tool_domains"]
                        if not isinstance(tool_domains, list):
                            errors.append(
                                f"Role '{role_name}' behaviors.tool_domains must be an array"
                            )
                        elif not all(
                            isinstance(domain, str) for domain in tool_domains
                        ):
                            errors.append(
                                f"Role '{role_name}' behaviors.tool_domains must contain only strings"
                            )

                    # Validate trusted_tools if present
                    if "trusted_tools" in behaviors:
                        trusted_tools = behaviors["trusted_tools"]
                        if not isinstance(trusted_tools, list):
                            errors.append(
                                f"Role '{role_name}' behaviors.trusted_tools must be an array"
                            )
                        elif not all(isinstance(tool, str) for tool in trusted_tools):
                            errors.append(
                                f"Role '{role_name}' behaviors.trusted_tools must contain only strings"
                            )

            # Validate standards structure (for specialists)
            if "standards" in role_data:
                standards = role_data["standards"]
                if not isinstance(standards, list):
                    errors.append(f"Role '{role_name}' standards must be an array")
                elif not all(isinstance(standard, str) for standard in standards):
                    errors.append(
                        f"Role '{role_name}' standards must contain only strings"
                    )

            # Validate gates structure (for specialists)
            if "gates" in role_data:
                gates = role_data["gates"]
                if not isinstance(gates, list):
                    errors.append(f"Role '{role_name}' gates must be an array")
                elif not all(isinstance(gate, str) for gate in gates):
                    errors.append(f"Role '{role_name}' gates must contain only strings")

    is_valid = len(errors) == 0

    if is_valid:
        logger.info(f"[{correlation_id}] Field structure validation passed")
    else:
        logger.error(
            f"[{correlation_id}] Field structure validation failed with {len(errors)} errors"
        )

    return is_valid, errors


def validate_tool_registry_references(
    library_data: Dict, tool_registry: Dict, correlation_id: str
) -> Tuple[bool, List[str]]:
    """
    Validate references to tool registry domains and categories.

    Args:
        library_data: Parsed JSON data
        tool_registry: Tool registry data
        correlation_id: Unique identifier for this validation run

    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)
    """
    logger.info(f"[{correlation_id}] Validating tool registry references")

    errors = []

    if not tool_registry:
        logger.warning(
            f"[{correlation_id}] Skipping tool registry validation - registry not available"
        )
        return True, []

    # Get available domains from tool registry
    available_domains = set(tool_registry.get("domain_mappings", {}).keys())

    for role_type, roles_by_type in library_data.items():
        if role_type not in VALID_ROLE_TYPES:
            continue

        for role_name, role_data in roles_by_type.items():
            if not isinstance(role_data, dict):
                continue

            # Check tool_domains references
            behaviors = role_data.get("behaviors", {})
            if isinstance(behaviors, dict) and "tool_domains" in behaviors:
                tool_domains = behaviors["tool_domains"]
                if isinstance(tool_domains, list):
                    for domain in tool_domains:
                        if isinstance(domain, str) and domain not in available_domains:
                            errors.append(
                                f"Role '{role_name}' references unknown tool domain: '{domain}'"
                            )

    # Check for unused domains (warning only)
    used_domains = set()
    for role_type, roles_by_type in library_data.items():
        if role_type not in VALID_ROLE_TYPES:
            continue

        for role_data in roles_by_type.values():
            if isinstance(role_data, dict):
                behaviors = role_data.get("behaviors", {})
                if isinstance(behaviors, dict) and "tool_domains" in behaviors:
                    tool_domains = behaviors["tool_domains"]
                    if isinstance(tool_domains, list):
                        used_domains.update(tool_domains)

    unused_domains = available_domains - used_domains
    if unused_domains:
        logger.warning(
            f"[{correlation_id}] Unused tool domains found: {', '.join(sorted(unused_domains))}"
        )
        console.print(
            f"[yellow]⚠[/yellow] Unused tool domains: {', '.join(sorted(unused_domains))}"
        )

    is_valid = len(errors) == 0

    if is_valid:
        logger.info(f"[{correlation_id}] Tool registry reference validation passed")
    else:
        logger.error(
            f"[{correlation_id}] Tool registry reference validation failed with {len(errors)} errors"
        )

    return is_valid, errors


def validate_role_consistency(
    library_data: Dict, correlation_id: str
) -> Tuple[bool, List[str]]:
    """
    Validate consistency across roles (duplicates, naming conventions, etc.).

    Args:
        library_data: Parsed JSON data
        correlation_id: Unique identifier for this validation run

    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)
    """
    logger.info(f"[{correlation_id}] Validating role consistency")

    errors = []
    warnings = []

    # Check for duplicate role names across types
    all_role_names = []
    for role_type, roles_by_type in library_data.items():
        if role_type in VALID_ROLE_TYPES and isinstance(roles_by_type, dict):
            all_role_names.extend(roles_by_type.keys())

    duplicate_names = set(
        name for name in all_role_names if all_role_names.count(name) > 1
    )
    if duplicate_names:
        errors.append(
            f"Duplicate role names found across types: {', '.join(sorted(duplicate_names))}"
        )

    # Check naming conventions (snake_case)
    for role_type, roles_by_type in library_data.items():
        if role_type not in VALID_ROLE_TYPES or not isinstance(roles_by_type, dict):
            continue

        for role_name in roles_by_type.keys():
            if not isinstance(role_name, str):
                continue

            # Check for snake_case (allow underscores, lowercase letters, numbers)
            if not role_name.replace("_", "").replace("-", "").islower():
                warnings.append(
                    f"Role name '{role_name}' should use snake_case convention"
                )

            # Check for reasonable length
            if len(role_name) > 50:
                warnings.append(
                    f"Role name '{role_name}' is unusually long ({len(role_name)} characters)"
                )

    # Log warnings
    for warning in warnings:
        logger.warning(f"[{correlation_id}] {warning}")
        console.print(f"[yellow]⚠[/yellow] {warning}")

    is_valid = len(errors) == 0

    if is_valid:
        logger.info(f"[{correlation_id}] Role consistency validation passed")
    else:
        logger.error(
            f"[{correlation_id}] Role consistency validation failed with {len(errors)} errors"
        )

    return is_valid, errors


def validate_role_library(file_path: Path, correlation_id: str) -> Tuple[bool, Dict]:
    """
    Validate the role library file.

    Args:
        file_path: Path to the role library file
        correlation_id: Unique identifier for this validation run

    Returns:
        Tuple[bool, Dict]: (is_valid, library_data)
    """
    logger.info(f"[{correlation_id}] Validating role library: {file_path}")

    # Load and parse JSON
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            library_data = json.load(f)
        logger.info(f"[{correlation_id}] Successfully loaded JSON from {file_path}")
    except json.JSONDecodeError as e:
        logger.error(f"[{correlation_id}] Invalid JSON in {file_path}: {e}")
        console.print(f"[red]✗[/red] Invalid JSON in {file_path}: {e}", style="red")
        return False, {}
    except Exception as e:
        logger.error(f"[{correlation_id}] Error reading {file_path}: {e}")
        console.print(f"[red]✗[/red] Error reading {file_path}: {e}", style="red")
        return False, {}

    # Load tool registry for cross-reference validation
    tool_registry = load_tool_registry(correlation_id)

    all_errors = []

    # Validate JSON structure
    structure_valid, structure_errors = validate_json_structure(
        library_data, correlation_id
    )
    all_errors.extend(structure_errors)

    # Validate field structures (only if basic structure is valid)
    if structure_valid:
        field_valid, field_errors = validate_field_structure(
            library_data, correlation_id
        )
        all_errors.extend(field_errors)

        # Validate tool registry references
        registry_valid, registry_errors = validate_tool_registry_references(
            library_data, tool_registry, correlation_id
        )
        all_errors.extend(registry_errors)

        # Validate role consistency
        consistency_valid, consistency_errors = validate_role_consistency(
            library_data, correlation_id
        )
        all_errors.extend(consistency_errors)
    else:
        field_valid = registry_valid = consistency_valid = False

    is_valid = structure_valid and field_valid and registry_valid and consistency_valid

    # Display results
    if is_valid:
        logger.info(f"[{correlation_id}] Role library validation passed")
        console.print(f"[green]✓[/green] {file_path} validation passed", style="green")
    else:
        logger.error(f"[{correlation_id}] Role library validation failed")
        console.print(f"[red]✗[/red] {file_path} validation failed", style="red")
        for error in all_errors:
            console.print(f"  [red]•[/red] {error}")

    return is_valid, library_data


def display_summary(
    file_path: Path, is_valid: bool, library_data: Dict, correlation_id: str
) -> None:
    """Display a summary of the role library validation."""
    logger.info(f"[{correlation_id}] Generating validation summary")

    table = Table(
        title="Role Library Validation Summary",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right", style="yellow")
    table.add_column("Status", justify="center")

    if library_data:
        executive_count = len(library_data.get("executive", {}))
        specialist_count = len(library_data.get("specialist", {}))
        total_roles = executive_count + specialist_count

        # Count roles with tool_domains
        roles_with_tool_domains = 0
        for role_type, roles_by_type in library_data.items():
            if role_type in VALID_ROLE_TYPES and isinstance(roles_by_type, dict):
                for role_data in roles_by_type.values():
                    if isinstance(role_data, dict):
                        behaviors = role_data.get("behaviors", {})
                        if isinstance(behaviors, dict) and "tool_domains" in behaviors:
                            roles_with_tool_domains += 1
    else:
        executive_count = specialist_count = total_roles = roles_with_tool_domains = 0

    status = "[green]✓ VALID[/green]" if is_valid else "[red]✗ INVALID[/red]"

    table.add_row("File", str(file_path), status)
    table.add_row("Executive Roles", str(executive_count), "")
    table.add_row("Specialist Roles", str(specialist_count), "")
    table.add_row("Total Roles", str(total_roles), "")
    table.add_row("Roles with Tool Domains", str(roles_with_tool_domains), "")

    console.print(table)

    if is_valid:
        console.print(
            "\n[green]✓ Role library validation completed successfully[/green]"
        )
    else:
        console.print("\n[red]✗ Role library validation failed[/red]")


def main():
    """Main entry point for role library linting."""
    correlation_id = str(uuid.uuid4())[:8]
    logger.info(f"[{correlation_id}] Starting role library linter")

    if len(sys.argv) != 2:
        console.print(
            "[red]Error:[/red] Usage: python lint_role_library.py <path_to_role_library.json>"
        )
        sys.exit(1)

    library_path_str = sys.argv[1]

    try:
        library_path = sanitize_file_path(library_path_str)
    except ValueError as e:
        logger.error(f"[{correlation_id}] {e}")
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)

    # Validate the role library
    is_valid, library_data = validate_role_library(library_path, correlation_id)

    # Display summary
    display_summary(library_path, is_valid, library_data, correlation_id)

    # Exit with appropriate code
    if is_valid:
        logger.info(f"[{correlation_id}] Role library linter completed successfully")
        sys.exit(0)
    else:
        logger.error(f"[{correlation_id}] Role library linter failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
