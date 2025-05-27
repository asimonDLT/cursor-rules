#!/usr/bin/env python3
"""
Domain Rule Creator - Scaffolds new domain rule files with proper structure.
Ensures all new domain rules are created as invocable agents with required YAML front-matter.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler
from rich.prompt import Confirm

# Configure rich logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=Console(), rich_tracebacks=True)],
)

logger = logging.getLogger("domain_rule_creator")
console = Console()

# Constants
DANGEROUS_INPUT_PATTERNS = ["{{", "}}", "<script", "javascript:", "data:", "${", "`"]
MAX_INPUT_LENGTH = 100
VALID_CATEGORIES = [
    "frontend",
    "backend",
    "cloud",
    "data",
    "security",
    "docs",
    "martech",
]

# Domain rule template
DOMAIN_RULE_TEMPLATE = """---
rule_type: Agent Requested
description: {description}
---

# {title}

## Core Principles
- {principle_placeholder}

## Best Practices
- {practice_placeholder}

## Standards & Guidelines
- {standard_placeholder}

## Common Patterns
- {pattern_placeholder}
"""


def validate_input(value: str, field_name: str) -> bool:
    """
    Validate input for security and length constraints.

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


def sanitize_name(name: str) -> str:
    """
    Sanitize and validate domain rule name.

    Args:
        name: Raw domain rule name input

    Returns:
        Sanitized domain rule name

    Raises:
        SystemExit: If name is invalid or contains dangerous patterns
    """
    logger.debug(f"Validating domain rule name: {name}")

    # Enhanced validation
    if not validate_input(name, "domain rule name"):
        sys.exit(1)

    # Remove any non-alphanumeric characters except underscores and hyphens
    sanitized = "".join(c for c in name.lower() if c.isalnum() or c in "_-")

    if not sanitized:
        logger.error(f"Invalid domain rule name: {name}")
        console.print(
            "[red]Error:[/red] Domain rule name must contain alphanumeric characters"
        )
        sys.exit(1)

    if sanitized != name.lower():
        logger.warning(f"Domain rule name sanitized: '{name}' → '{sanitized}'")
        console.print(
            f"[yellow]Warning:[/yellow] Domain rule name sanitized: '{name}' → '{sanitized}'"
        )

    logger.info(f"Domain rule name validated: {sanitized}")
    return sanitized


def generate_domain_rule_content(
    name: str, category: str, description: Optional[str] = None
) -> str:
    """
    Generate domain rule content with proper structure.

    Args:
        name: Domain rule name
        category: Category/directory for the rule
        description: Optional custom description

    Returns:
        Generated domain rule content
    """
    title = name.replace("_", " ").replace("-", " ").title()

    if not description:
        description = f"Standards and best practices for {title.lower()}."

    # Generate contextual placeholders based on category
    if category == "frontend":
        principle_placeholder = "Prioritize user experience and performance"
        practice_placeholder = "Use semantic HTML and accessible design patterns"
        standard_placeholder = "Follow WCAG 2.1 AA accessibility guidelines"
        pattern_placeholder = "Component-based architecture with reusable UI elements"
    elif category == "backend":
        principle_placeholder = "Design for scalability and maintainability"
        practice_placeholder = "Use proper error handling and logging"
        standard_placeholder = "Follow RESTful API design principles"
        pattern_placeholder = "Layered architecture with clear separation of concerns"
    elif category == "cloud":
        principle_placeholder = "Design for cloud-native scalability and resilience"
        practice_placeholder = "Use infrastructure as code for all deployments"
        standard_placeholder = "Follow cloud security best practices"
        pattern_placeholder = "Microservices with proper service mesh configuration"
    elif category == "data":
        principle_placeholder = "Ensure data quality and governance"
        practice_placeholder = "Implement proper data validation and monitoring"
        standard_placeholder = "Follow data privacy and compliance requirements"
        pattern_placeholder = "ETL pipelines with proper error handling and recovery"
    elif category == "security":
        principle_placeholder = "Apply defense in depth security strategy"
        practice_placeholder = "Use principle of least privilege for all access"
        standard_placeholder = "Follow OWASP security guidelines"
        pattern_placeholder = "Zero-trust architecture with proper authentication"
    elif category == "martech":
        principle_placeholder = "Respect user privacy and consent preferences"
        practice_placeholder = "Use consistent naming conventions for tracking events"
        standard_placeholder = "Follow GDPR and privacy compliance requirements"
        pattern_placeholder = "Centralized tag management with proper data governance"
    else:
        principle_placeholder = f"Follow {title.lower()} best practices"
        practice_placeholder = f"Implement proper {title.lower()} patterns"
        standard_placeholder = f"Adhere to industry {title.lower()} standards"
        pattern_placeholder = f"Use established {title.lower()} architectural patterns"

    return DOMAIN_RULE_TEMPLATE.format(
        description=description,
        title=title,
        principle_placeholder=principle_placeholder,
        practice_placeholder=practice_placeholder,
        standard_placeholder=standard_placeholder,
        pattern_placeholder=pattern_placeholder,
    )


def create_domain_rule_file(
    name: str,
    category: str,
    description: Optional[str] = None,
    output_base_dir: str = ".cursor/rules",
) -> Path:
    """
    Create a new domain rule file.

    Args:
        name: Domain rule name
        category: Category/directory for the rule
        description: Optional custom description
        output_base_dir: Base directory for rule files

    Returns:
        Path to the created file
    """
    # Sanitize inputs
    name = sanitize_name(name)

    if category not in VALID_CATEGORIES:
        logger.warning(
            f"Category '{category}' not in standard categories: {VALID_CATEGORIES}"
        )
        console.print(
            f"[yellow]Warning:[/yellow] Category '{category}' not in standard categories"
        )
        if not Confirm.ask(f"Continue with category '{category}'?"):
            logger.info("Operation cancelled by user")
            console.print("Operation cancelled.")
            sys.exit(1)

    # Create output directory
    output_dir = Path(output_base_dir) / category
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create file path
    file_path = output_dir / f"{name}.mdc"

    # Check if file already exists
    if file_path.exists():
        logger.warning(f"File {file_path} already exists")
        if not Confirm.ask(f"File {file_path} exists. Overwrite?"):
            logger.info("Operation cancelled by user")
            console.print("Operation cancelled.")
            sys.exit(1)

    # Generate content
    content = generate_domain_rule_content(name, category, description)

    # Write file
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Successfully created domain rule file: {file_path}")
    except OSError as e:
        logger.error(f"Failed to write file {file_path}: {e}")
        console.print(f"[red]Error:[/red] Failed to write file: {e}")
        sys.exit(1)

    return file_path


def main() -> None:
    """Main entry point for domain rule creation."""
    logger.info("Starting Domain Rule Creator")

    parser = argparse.ArgumentParser(
        description="Create new domain rule files with proper structure"
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Domain rule name (e.g., mobile, api_design, monitoring)",
    )
    parser.add_argument(
        "--category",
        required=True,
        choices=VALID_CATEGORIES,
        help="Category/directory for the rule",
    )
    parser.add_argument("--description", help="Custom description for the domain rule")
    parser.add_argument(
        "--output-dir",
        default=".cursor/rules",
        help="Base output directory for rule files",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Set logging level based on verbose flag
    if args.verbose:
        logging.getLogger("domain_rule_creator").setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")

    logger.info(f"Creating domain rule: {args.name} in category: {args.category}")

    # Create the domain rule file
    file_path = create_domain_rule_file(
        args.name, args.category, args.description, args.output_dir
    )

    console.print(f"\n[green]✓ Domain rule created:[/green] {file_path}")
    console.print(f"[dim]Invoke with: @{args.name}[/dim]")
    logger.info(f"Domain rule creation completed successfully: {file_path}")

    # Validate generated file using existing linter
    console.print("\n[blue]Running validation...[/blue]")
    logger.info("Running lint validation on generated file")

    import subprocess

    try:
        result = subprocess.run(
            ["uv", "run", "python", "scripts/lint_mdc.py", str(file_path)],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            logger.info("Validation passed successfully")
            console.print("[green]✓ Validation passed[/green]")
        else:
            logger.warning(f"Validation warnings: {result.stdout}")
            console.print(f"[yellow]⚠ Validation warnings:[/yellow]\n{result.stdout}")
    except FileNotFoundError:
        logger.warning("lint_mdc.py not found - skipping validation")
        console.print("[yellow]⚠ lint_mdc.py not found - skipping validation[/yellow]")


if __name__ == "__main__":
    main()
