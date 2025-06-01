#!/usr/bin/env python3
"""
Cursor Role Factory - Automated role generation with industry standards.
Generates standardized .mdc role files with proper validation and security.
"""

import argparse
import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.prompt import Confirm

# Configure rich logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=Console(), rich_tracebacks=True)],
)

logger = logging.getLogger("role_factory")
console = Console()

# Constants
DANGEROUS_INPUT_PATTERNS = ["{{", "}}", "<script", "javascript:", "data:", "${", "`"]
MAX_INPUT_LENGTH = 500
VALID_ROLE_TYPES = ["executive", "specialist"]
REQUIRED_EXECUTIVE_BUCKETS = [
    "identity",
    "objectives",
    "influence",
    "behaviors",
    "motivations",
]
REQUIRED_SPECIALIST_BUCKETS = ["identity", "objectives"]


# Tool registry functions
def load_tool_registry() -> dict[str, Any]:
    """Load the tool registry with error handling."""
    registry_path = (
        Path(__file__).parent.parent.parent / ".cursor/rules/tools/tool_registry.json"
    )

    if not registry_path.exists():
        logger.warning(f"Tool registry not found at {registry_path}")
        return {}

    try:
        with open(registry_path, encoding="utf-8") as f:
            registry = json.load(f)
            logger.debug(
                f"Loaded tool registry with {len(registry.get('tool_categories', {}))} categories"
            )
            return registry
    except json.JSONDecodeError as e:
        logger.warning(f"Invalid JSON in tool_registry.json: {e}")
        return {}


def resolve_tools_from_registry(
    domain_or_categories: list[str], registry: dict[str, Any]
) -> list[str]:
    """Resolve tools from registry based on domain mappings or direct categories."""
    if not registry:
        return []

    tool_categories = registry.get("tool_categories", {})
    domain_mappings = registry.get("domain_mappings", {})
    resolved_tools = []

    for item in domain_or_categories:
        # First check if it's a domain mapping
        if item in domain_mappings:
            categories = domain_mappings[item]
            for category in categories:
                if category in tool_categories:
                    resolved_tools.extend(tool_categories[category].get("tools", []))
        # Otherwise check if it's a direct category
        elif item in tool_categories:
            resolved_tools.extend(tool_categories[item].get("tools", []))
        else:
            logger.warning(f"Unknown tool domain/category: {item}")

    # Remove duplicates while preserving order
    return list(dict.fromkeys(resolved_tools))


# Utility functions for overrides
def coerce_csv(text: str | None) -> list[str] | None:
    """Convert comma-separated string to list, handling None gracefully."""
    return [s.strip() for s in text.split(",")] if text else None


def apply_overrides(
    base_data: dict[str, Any],
    cli_args: argparse.Namespace,
    json_override_path: str | None = None,
) -> dict[str, Any]:
    """Apply overrides in precedence order: CLI flags > JSON override > base data.

    Args:
        base_data: Base role data from library
        cli_args: Parsed command line arguments
        json_override_path: Optional path to JSON override file

    Returns:
        Merged role data with overrides applied

    Raises:
        SystemExit: If JSON file is invalid or not found
    """
    # Start with base data
    result = base_data.copy()

    # Apply JSON override file if provided
    if json_override_path:
        override_path = Path(json_override_path)
        if override_path.exists():
            try:
                with open(override_path, encoding="utf-8") as f:
                    json_override = json.load(f)
                # Deep merge the override data
                result = deep_merge(result, json_override)
                logger.info(f"Applied JSON overrides from {override_path}")
            except (json.JSONDecodeError, OSError) as e:
                logger.error(f"Failed to load JSON override file: {e}")
                console.print(
                    f"[red]Error:[/red] Failed to load JSON override file: {e}"
                )
                sys.exit(1)
        else:
            logger.error(f"JSON override file not found: {override_path}")
            console.print(
                f"[red]Error:[/red] JSON override file not found: {override_path}"
            )
            sys.exit(1)

    # Apply CLI flag overrides (highest precedence)
    field_mapping = {
        "trusted_tools": ("behaviors", "trusted_tools"),
        "comms": ("behaviors", "comms"),
        "kpis": ("objectives", "kpis"),
        "drivers": ("motivations", "drivers"),
        "pain_points": ("motivations", "pain_points"),
        "top_objectives": ("objectives", "top_objectives"),
        "decision_rights": ("influence", "decision_rights"),
        "stakeholders": ("influence", "stakeholders"),
        "scope": ("identity", "scope"),
        "seniority": ("identity", "seniority"),
        "span_of_control": ("identity", "span_of_control"),
    }

    for flag_name, (bucket, key) in field_mapping.items():
        cli_value = getattr(cli_args, flag_name.replace("-", "_"), None)
        if cli_value:
            # Validate input for security
            if not validate_cli_input(cli_value, flag_name):
                sys.exit(1)

            # Handle special cases for non-CSV fields
            if key in ["scope", "seniority", "span_of_control"]:
                parsed_value = cli_value
            else:
                parsed_value = coerce_csv(cli_value)

            if parsed_value:
                # Ensure the bucket exists
                if bucket not in result:
                    result[bucket] = {}
                result[bucket][key] = parsed_value
                logger.debug(f"Applied CLI override: {bucket}.{key} = {parsed_value}")

    return result


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Deep merge two dictionaries, with override taking precedence."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


# Template loading functions
def load_template(template_name: str) -> str:
    """Load a template file from the templates directory.

    Args:
        template_name: Name of the template file (without .template extension)

    Returns:
        Template content as string

    Raises:
        SystemExit: If template file is not found or cannot be read
    """
    template_path = (
        Path(__file__).parent.parent.parent
        / "templates"
        / "roles"
        / f"{template_name}.mdc.template"
    )

    try:
        with open(template_path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"Template file not found: {template_path}")
        console.print(f"[red]Error:[/red] Template file not found: {template_path}")
        sys.exit(1)
    except OSError as e:
        logger.error(f"Failed to read template file {template_path}: {e}")
        console.print(f"[red]Error:[/red] Failed to read template file: {e}")
        sys.exit(1)


def get_executive_template() -> str:
    """Get the executive role template."""
    return load_template("executive_role")


def get_specialist_template() -> str:
    """Get the specialist role template."""
    return load_template("specialist_role")


def validate_role_library(library: dict[str, Any]) -> None:
    """Validate role library structure and required fields."""
    for role_type, roles_by_type in library.items():
        if role_type not in VALID_ROLE_TYPES:
            logger.warning(f"Unknown role type in library: {role_type}")
            continue

        for role_name, role_data in roles_by_type.items():
            if role_type == "executive":
                missing_buckets = [
                    bucket
                    for bucket in REQUIRED_EXECUTIVE_BUCKETS
                    if bucket not in role_data
                ]
                if missing_buckets:
                    logger.warning(
                        f"Executive role '{role_name}' missing buckets: {missing_buckets}"
                    )
            else:
                missing_buckets = [
                    bucket
                    for bucket in REQUIRED_SPECIALIST_BUCKETS
                    if bucket not in role_data
                ]
                # Specialists need either standards OR behaviors
                has_standards_or_behaviors = (
                    "standards" in role_data or "behaviors" in role_data
                )
                if missing_buckets:
                    logger.warning(
                        f"Specialist role '{role_name}' missing buckets: {missing_buckets}"
                    )
                if not has_standards_or_behaviors:
                    logger.warning(
                        f"Specialist role '{role_name}' missing both 'standards' and 'behaviors'"
                    )


def load_role_library() -> dict[str, Any]:
    """Load the role library JSON with error handling."""
    library_path = (
        Path(__file__).parent.parent.parent / ".cursor/rules/tools/role_library.json"
    )

    logger.info(f"Loading role library from {library_path}")

    if not library_path.exists():
        logger.error(f"Role library not found at {library_path}")
        console.print(f"[red]Error:[/red] Role library not found at {library_path}")
        console.print(
            "Create role_library.json with executive and specialist definitions."
        )
        sys.exit(1)

    try:
        with open(library_path, encoding="utf-8") as f:
            library = json.load(f)
            logger.info(f"Loaded {len(library)} role types from library")

            # Validate the library structure
            validate_role_library(library)

            return library
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in role_library.json: {e}")
        console.print(f"[red]Error:[/red] Invalid JSON in role_library.json: {e}")
        sys.exit(1)


def validate_cli_input(value: str, field_name: str) -> bool:
    """Enhanced validation for CLI inputs to prevent injection.

    Args:
        value: Input value to validate
        field_name: Name of the field for error reporting

    Returns:
        True if input is safe, False otherwise
    """
    # Check for potentially dangerous patterns
    if any(pattern in value.lower() for pattern in DANGEROUS_INPUT_PATTERNS):
        logger.error(f"Potentially dangerous input in {field_name}: {value}")
        console.print(f"[red]Error:[/red] Invalid characters detected in {field_name}")
        return False

    # Check for excessive length
    if len(value) > MAX_INPUT_LENGTH:
        logger.error(f"Input too long for {field_name}: {len(value)} characters")
        console.print(
            f"[red]Error:[/red] Input for {field_name} exceeds {MAX_INPUT_LENGTH} character limit"
        )
        return False

    return True


def validate_role_name(name: str) -> str:
    """Sanitize and validate role name.

    Args:
        name: Raw role name input

    Returns:
        Sanitized role name

    Raises:
        SystemExit: If role name is invalid or contains dangerous patterns
    """
    logger.debug(f"Validating role name: {name}")

    # Enhanced validation
    if not validate_cli_input(name, "role name"):
        sys.exit(1)

    # Remove any non-alphanumeric characters except underscores and hyphens
    sanitized = "".join(c for c in name.lower() if c.isalnum() or c in "_-")

    if not sanitized:
        logger.error(f"Invalid role name: {name}")
        console.print(
            "[red]Error:[/red] Role name must contain alphanumeric characters"
        )
        sys.exit(1)

    if sanitized != name.lower():
        logger.warning(f"Role name sanitized: '{name}' → '{sanitized}'")
        console.print(
            f"[yellow]Warning:[/yellow] Role name sanitized: '{name}' → '{sanitized}'"
        )

    logger.info(f"Role name validated: {sanitized}")
    return sanitized


def get_role_data(
    role_type: str, role_name: str, library: dict[str, Any]
) -> dict[str, Any] | None:
    """Get role data from library with validation."""
    if role_type not in library:
        console.print(f"[red]Error:[/red] Unknown role type: {role_type}")
        console.print(f"Available types: {list(library.keys())}")
        return None

    if role_name in library[role_type]:
        return library[role_type][role_name]

    # If not in library, allow custom creation with confirmation
    if not Confirm.ask(
        f"Role '{role_name}' not in library. Create custom {role_type} role?"
    ):
        return None

    return {}


def generate_synthesis_instructions(tool_domains: list[str]) -> str:
    """Generate dynamic synthesis instructions based on tool domains."""
    domain_instructions = {
        "aws": "* For AWS/cloud guidance: Invoke @aws for infrastructure standards and best practices",
        "python": "* For Python development: Invoke @python for coding standards and tooling recommendations",
        "database": "* For database work: Invoke @database for query optimization and schema design",
        "martech": "* For MarTech guidance: Invoke @martech for marketing analytics and campaign best practices",
    }

    instructions = []
    for domain in tool_domains:
        if domain in domain_instructions:
            instructions.append(domain_instructions[domain])
        else:
            # Generic instruction for unknown domains
            instructions.append(
                f"* For {domain} guidance: Invoke @{domain} for domain-specific standards"
            )

    # Add default domains if none provided
    if not instructions:
        instructions = [
            "* For AWS/cloud guidance: Invoke @aws for infrastructure standards and best practices",
            "* For Python development: Invoke @python for coding standards and tooling recommendations",
            "* For database work: Invoke @database for query optimization and schema design",
        ]

    return "\n".join(instructions)


def generate_executive_role(
    role_name: str,
    role_data: dict[str, Any],
    custom_frameworks: str | None = None,
    strict: bool = False,
) -> str:
    """Generate executive role content using five-bucket standard."""
    # Validate five-bucket completeness
    required_buckets = [
        "identity",
        "objectives",
        "influence",
        "behaviors",
        "motivations",
    ]
    missing_buckets = [
        bucket for bucket in required_buckets if not role_data.get(bucket)
    ]

    if missing_buckets:
        if strict:
            console.print(
                f"[red]Error:[/red] Missing required buckets: {', '.join(missing_buckets)}"
            )
            console.print("Use --no-strict to allow interactive prompting.")
            sys.exit(1)
        console.print(
            f"[yellow]Warning:[/yellow] Missing data for buckets: {', '.join(missing_buckets)}"
        )
        console.print("Will prompt for missing values interactively.")

    title = (
        role_name.upper()
        if len(role_name) <= 3
        else role_name.replace("_", " ").title()
    )

    # Extract data with fallbacks
    identity = role_data.get("identity", {})
    objectives = role_data.get("objectives", {})
    influence = role_data.get("influence", {})
    behaviors = role_data.get("behaviors", {})
    motivations = role_data.get("motivations", {})

    # Generate synthesis instructions based on tool domains
    tool_domains = behaviors.get("tool_domains", [])
    synthesis_instructions = generate_synthesis_instructions(tool_domains)

    template = get_executive_template()
    return template.format(
        role=role_name,
        domain="strategy & execution",
        title=title,
        scope=identity.get("scope") or "Global",
        seniority=identity.get("seniority") or "C-level",
        span_of_control=identity.get("span_of_control") or "100",
        top_objectives=", ".join(
            objectives.get("top_objectives", [f"Drive {role_name} excellence"])
        ),
        kpis=", ".join(objectives.get("kpis", ["ROI"])),
        decision_rights=", ".join(
            influence.get("decision_rights", [f"{title} strategy"])
        ),
        stakeholders=", ".join(influence.get("stakeholders", ["CEO"])),
        comms=", ".join(behaviors.get("comms", ["Weekly reviews"])),
        trusted_tools=", ".join(behaviors.get("trusted_tools", ["Excel"])),
        risk_posture=behaviors.get("risk_posture") or "Not specified",
        drivers=", ".join(motivations.get("drivers", ["Growth"])),
        pain_points=", ".join(motivations.get("pain_points", ["Resource constraints"])),
        synthesis_instructions=synthesis_instructions,
    )


def generate_specialist_role(
    role_name: str,
    role_data: dict[str, Any],
    no_framework_check: bool = False,
    strict: bool = False,
) -> str:
    """Generate specialist role content using five-bucket standard."""
    # Validate required buckets for specialists
    required_buckets = ["identity", "objectives"]
    missing_buckets = [
        bucket for bucket in required_buckets if not role_data.get(bucket)
    ]

    if missing_buckets:
        if strict:
            console.print(
                f"[red]Error:[/red] Missing required buckets: {', '.join(missing_buckets)}"
            )
            console.print("Use --no-strict to allow interactive prompting.")
            sys.exit(1)
        console.print(
            f"[yellow]Warning:[/yellow] Missing data for buckets: {', '.join(missing_buckets)}"
        )
        console.print("Will prompt for missing values interactively.")

    title = role_name.replace("_", " ").title()

    # Extract data with fallbacks
    identity = role_data.get("identity", {})
    objectives = role_data.get("objectives", {})
    standards = role_data.get("standards", [])
    gates = role_data.get("gates", [])

    # For specialists, we can use either behaviors or just standards/gates
    trusted_tools = []
    risk_posture = "Standards-focused"

    # Try to get tools from behaviors if available
    behaviors = role_data.get("behaviors", {})
    if behaviors:
        trusted_tools = behaviors.get("trusted_tools", [])
        risk_posture = behaviors.get("risk_posture", risk_posture)

    # Generate synthesis instructions based on tool domains
    tool_domains = behaviors.get("tool_domains", [])
    synthesis_instructions = generate_synthesis_instructions(tool_domains)

    template = get_specialist_template()
    return template.format(
        role=role_name,
        domain="technical review",
        title=title,
        scope=identity.get("scope") or "Cross-functional",
        seniority=identity.get("seniority") or "Senior specialist",
        span_of_control=identity.get("span_of_control") or "0",
        top_objectives=", ".join(
            objectives.get("top_objectives", [f"Ensure {role_name} excellence"])
        ),
        kpis=", ".join(objectives.get("kpis", ["Quality score"])),
        standards=", ".join(standards) if standards else "Industry best practices",
        gates=", ".join(gates) if gates else "Standards review",
        trusted_tools=", ".join(trusted_tools) if trusted_tools else "Standard toolset",
        risk_posture=risk_posture
        if risk_posture != "Standards-focused"
        else "Standards-focused",
        synthesis_instructions=synthesis_instructions,
    )


def write_role_file(role_name: str, content: str, output_dir: Path) -> Path:
    """Write role content to .mdc file."""
    logger.info(f"Writing role file for {role_name} to {output_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / f"{role_name}.mdc"

    if file_path.exists():
        logger.warning(f"File {file_path} already exists")
        if not Confirm.ask(f"File {file_path} exists. Overwrite?"):
            logger.info("Operation cancelled by user")
            console.print("Operation cancelled.")
            sys.exit(1)

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Successfully wrote role file: {file_path}")
    except OSError as e:
        logger.error(f"Failed to write file {file_path}: {e}")
        console.print(f"[red]Error:[/red] Failed to write file: {e}")
        sys.exit(1)

    return file_path


def list_templates(library: dict[str, Any]) -> None:
    """List available role templates."""
    console.print(Panel("Available Role Templates", border_style="blue"))

    for role_type, roles in library.items():
        console.print(f"\n[bold]{role_type.title()} Roles:[/bold]")
        for role_name, role_data in roles.items():
            frameworks = role_data.get("frameworks", role_data.get("standards", []))
            console.print(f"  • {role_name}: {', '.join(frameworks[:3])}")


def main() -> None:
    """Main entry point for role generation."""
    logger.info("Starting Cursor Role Factory")

    parser = argparse.ArgumentParser(
        description="Generate Cursor role files with industry standards"
    )
    parser.add_argument("--name", required=False, help="Role name (e.g., cmo, qa_lead)")
    parser.add_argument("--type", choices=["executive", "specialist"], help="Role type")
    parser.add_argument(
        "--frameworks", help="Comma-separated frameworks (overrides library)"
    )
    parser.add_argument(
        "--no-framework-check", action="store_true", help="Skip framework requirement"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail if required five-bucket data is missing",
    )

    # Override flags for common fields
    parser.add_argument("--trusted-tools", help="Comma-separated list of trusted tools")
    parser.add_argument(
        "--tool-domains",
        help="Comma-separated list of tool domains from registry (e.g., aws,python,database)",
    )
    parser.add_argument("--comms", help="Comma-separated list of communication styles")
    parser.add_argument(
        "--kpis", help="Comma-separated list of key performance indicators"
    )
    parser.add_argument(
        "--drivers", help="Comma-separated list of motivational drivers"
    )
    parser.add_argument("--pain-points", help="Comma-separated list of pain points")
    parser.add_argument(
        "--top-objectives", help="Comma-separated list of top objectives"
    )
    parser.add_argument(
        "--decision-rights", help="Comma-separated list of decision rights"
    )
    parser.add_argument(
        "--stakeholders", help="Comma-separated list of key stakeholders"
    )
    parser.add_argument(
        "--scope", help="Role scope/region (e.g., Global, Regional EMEA)"
    )
    parser.add_argument(
        "--seniority", help="Role seniority level (e.g., C-level, Senior specialist)"
    )
    parser.add_argument("--span-of-control", help="Number of people in span of control")
    parser.add_argument(
        "--json-override", help="Path to JSON file with full override data"
    )

    parser.add_argument(
        "--list-templates", action="store_true", help="List available templates"
    )
    parser.add_argument(
        "--output-dir", default=".cursor/rules/roles", help="Output directory"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Set logging level based on verbose flag
    if args.verbose:
        logging.getLogger("role_factory").setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")

    # Load role library and tool registry
    library = load_role_library()
    tool_registry = load_tool_registry()

    # Handle list templates
    if args.list_templates:
        logger.info("Listing available templates")
        list_templates(library)
        return

    # Validate required arguments
    if not args.name or not args.type:
        logger.error("Missing required arguments: --name and --type")
        console.print("[red]Error:[/red] --name and --type are required")
        parser.print_help()
        sys.exit(1)

    logger.info(f"Creating {args.type} role: {args.name}")

    # Sanitize role name
    role_name = validate_role_name(args.name)

    # Get role data
    role_data = get_role_data(args.type, role_name, library)
    if role_data is None:
        logger.error("Failed to get role data")
        sys.exit(1)

    # Apply overrides in precedence order: CLI flags > JSON override > base data
    role_data = apply_overrides(role_data, args, args.json_override)

    # Apply tool domain resolution from registry
    # First check for tool_domains in role library data
    domains_to_resolve = []

    # Get domains from role library data
    behaviors = role_data.get("behaviors", {})
    if "tool_domains" in behaviors:
        domains_to_resolve.extend(behaviors["tool_domains"])
        logger.info(f"Found tool_domains in role library: {behaviors['tool_domains']}")

    # Override with CLI domains if provided
    if args.tool_domains:
        domains_to_resolve = coerce_csv(args.tool_domains)
        logger.info(f"Using CLI tool_domains override: {domains_to_resolve}")

    if domains_to_resolve:
        resolved_tools = resolve_tools_from_registry(domains_to_resolve, tool_registry)
        if resolved_tools:
            # Ensure behaviors bucket exists
            if "behaviors" not in role_data:
                role_data["behaviors"] = {}
            # Merge with existing trusted tools
            existing_tools = role_data["behaviors"].get("trusted_tools", [])
            all_tools = existing_tools + resolved_tools
            role_data["behaviors"]["trusted_tools"] = list(
                dict.fromkeys(all_tools)
            )  # Remove duplicates
            logger.info(
                f"Applied tool domains {domains_to_resolve}, resolved {len(resolved_tools)} tools"
            )

    # Generate role content
    console.print(f"\n[blue]Generating {args.type} role: {role_name}[/blue]")
    logger.info(f"Generating content for {args.type} role: {role_name}")

    if args.type == "executive":
        content = generate_executive_role(
            role_name, role_data, args.frameworks, args.strict
        )
    else:
        content = generate_specialist_role(
            role_name, role_data, args.no_framework_check, args.strict
        )

    # Write file
    output_dir = Path(args.output_dir) / args.type
    output_path = write_role_file(role_name, content, output_dir)

    console.print(f"\n[green]✓ Role created:[/green] {output_path}")
    console.print(f"[dim]Invoke with: @{role_name}[/dim]")
    logger.info(f"Role creation completed successfully: {output_path}")

    # Validate generated file
    console.print("\n[blue]Running validation...[/blue]")
    logger.info("Running lint validation on generated file")

    try:
        # Use uv run consistently and add Ruff validation
        result = subprocess.run(
            ["uv", "run", "ruff", "check", "--select", "E,W,F", str(output_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            logger.info("Ruff validation passed successfully")
            console.print("[green]✓ Ruff validation passed[/green]")
        else:
            logger.warning(f"Ruff validation issues: {result.stdout}")
            console.print(
                f"[yellow]⚠ Ruff validation issues:[/yellow]\n{result.stdout}"
            )

        # Also run the custom MDC linter if available
        mdc_result = subprocess.run(
            ["uv", "run", "python", "scripts/validation/lint_mdc.py", str(output_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if mdc_result.returncode == 0:
            logger.info("MDC validation passed successfully")
            console.print("[green]✓ MDC validation passed[/green]")
        else:
            logger.warning(f"MDC validation warnings: {mdc_result.stdout}")
            console.print(
                f"[yellow]⚠ MDC validation warnings:[/yellow]\n{mdc_result.stdout}"
            )

    except subprocess.TimeoutExpired:
        logger.error("Validation timed out")
        console.print("[red]✗ Validation timed out[/red]")
    except FileNotFoundError as e:
        logger.warning(f"Validation tool not found: {e}")
        console.print(f"[yellow]⚠ Validation tool not found: {e}[/yellow]")


if __name__ == "__main__":
    main()
