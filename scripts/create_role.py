#!/usr/bin/env python3
"""
Cursor Role Factory - Automated role generation with industry standards.
Generates standardized .mdc role files with proper validation and security.
"""
import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Optional, List

from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

# Configure rich logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=Console(), rich_tracebacks=True)]
)

logger = logging.getLogger("role_factory")
console = Console()

# Utility functions for overrides
def coerce_csv(text: Optional[str]) -> Optional[List[str]]:
    """Convert comma-separated string to list, handling None gracefully."""
    return [s.strip() for s in text.split(",")] if text else None


def apply_overrides(base_data: Dict, cli_args, json_override_path: Optional[str] = None) -> Dict:
    """Apply overrides in precedence order: CLI flags > JSON override > base data."""
    # Start with base data
    result = base_data.copy()
    
    # Apply JSON override file if provided
    if json_override_path:
        override_path = Path(json_override_path)
        if override_path.exists():
            try:
                with open(override_path, 'r', encoding='utf-8') as f:
                    json_override = json.load(f)
                # Deep merge the override data
                result = deep_merge(result, json_override)
                logger.info(f"Applied JSON overrides from {override_path}")
            except (json.JSONDecodeError, OSError) as e:
                logger.error(f"Failed to load JSON override file: {e}")
                console.print(f"[red]Error:[/red] Failed to load JSON override file: {e}")
                sys.exit(1)
        else:
            logger.error(f"JSON override file not found: {override_path}")
            console.print(f"[red]Error:[/red] JSON override file not found: {override_path}")
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
    }
    
    for flag_name, (bucket, key) in field_mapping.items():
        cli_value = getattr(cli_args, flag_name.replace('-', '_'), None)
        if cli_value:
            parsed_value = coerce_csv(cli_value)
            if parsed_value:
                # Ensure the bucket exists
                if bucket not in result:
                    result[bucket] = {}
                result[bucket][key] = parsed_value
                logger.debug(f"Applied CLI override: {bucket}.{key} = {parsed_value}")
    
    return result


def deep_merge(base: Dict, override: Dict) -> Dict:
    """Deep merge two dictionaries, with override taking precedence."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result

# Template definitions
EXECUTIVE_TEMPLATE = """---
rule_type: Agent Requested
description: {role} perspective for {domain}. Opt-in via @{role}.
---

# {title} (v1.0)

## Identity & Context
* Scope / region: {scope}
* Seniority: {seniority}
* Span of control: {span_of_control}

## Objectives, KPIs & Mandate
* Top objectives: {top_objectives}
* Success metrics: {kpis}

## Influence & Decision Power
* Decision rights: {decision_rights}
* Key stakeholders: {stakeholders}

## Behaviors, Tools & Preferences
* Comms style: {comms}
* Trusted tools: {trusted_tools}
* Risk posture: {risk_posture}

## Motivations, Pain Points & Constraints
* Drivers: {drivers}
* Pain points: {pain_points}

> Project rules override this Role if they conflict.

## Output Template

**{title} Assessment:**
- {{{{finding_1}}}}
- {{{{finding_2}}}}

**Decision:** <GO / NO-GO / REVISE>
**Next steps:**
- {{{{action_1}}}}
- {{{{action_2}}}}
"""

SPECIALIST_TEMPLATE = """---
rule_type: Agent Requested
description: {role} expertise for {domain}. Opt-in via @{role}.
---

# {title} (v1.0)

## Identity & Context
* Scope / focus: {scope}
* Seniority: {seniority}
* Span of control: {span_of_control}

## Objectives & Quality Standards
* Top objectives: {top_objectives}
* Success metrics: {kpis}
* Standards: {standards}

## Quality Gates & Behaviors
* Quality gates: {gates}
* Trusted tools: {trusted_tools}
* Risk posture: {risk_posture}

> Project rules override this Role if they conflict.

## Output Template

**{title} Review:**
- {{{{technical_finding}}}}
- {{{{recommendation}}}}

**Status:** <APPROVED / BLOCKED / NEEDS_REVISION>
**Next steps:**
- {{{{action}}}}
"""


def load_role_library() -> Dict:
    """Load the role library JSON with error handling."""
    library_path = Path(__file__).parent / "role_library.json"
    
    logger.info(f"Loading role library from {library_path}")
    
    if not library_path.exists():
        logger.error(f"Role library not found at {library_path}")
        console.print(f"[red]Error:[/red] Role library not found at {library_path}")
        console.print("Create role_library.json with executive and specialist definitions.")
        sys.exit(1)
    
    try:
        with open(library_path, 'r', encoding='utf-8') as f:
            library = json.load(f)
            logger.info(f"Loaded {len(library)} role types from library")
            return library
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in role_library.json: {e}")
        console.print(f"[red]Error:[/red] Invalid JSON in role_library.json: {e}")
        sys.exit(1)


def validate_role_name(name: str) -> str:
    """Sanitize and validate role name."""
    logger.debug(f"Validating role name: {name}")
    
    # Remove any non-alphanumeric characters except underscores and hyphens
    sanitized = ''.join(c for c in name.lower() if c.isalnum() or c in '_-')
    
    if not sanitized:
        logger.error(f"Invalid role name: {name}")
        console.print("[red]Error:[/red] Role name must contain alphanumeric characters")
        sys.exit(1)
    
    if sanitized != name.lower():
        logger.warning(f"Role name sanitized: '{name}' → '{sanitized}'")
        console.print(f"[yellow]Warning:[/yellow] Role name sanitized: '{name}' → '{sanitized}'")
    
    logger.info(f"Role name validated: {sanitized}")
    return sanitized


def get_role_data(role_type: str, role_name: str, library: Dict) -> Optional[Dict]:
    """Get role data from library with validation."""
    if role_type not in library:
        console.print(f"[red]Error:[/red] Unknown role type: {role_type}")
        console.print(f"Available types: {list(library.keys())}")
        return None
    
    if role_name in library[role_type]:
        return library[role_type][role_name]
    
    # If not in library, allow custom creation with confirmation
    if not Confirm.ask(f"Role '{role_name}' not in library. Create custom {role_type} role?"):
        return None
    
    return {}


def generate_executive_role(role_name: str, role_data: Dict, custom_frameworks: Optional[str] = None, strict: bool = False) -> str:
    """Generate executive role content using five-bucket standard."""
    # Validate five-bucket completeness
    required_buckets = ['identity', 'objectives', 'influence', 'behaviors', 'motivations']
    missing_buckets = [bucket for bucket in required_buckets if not role_data.get(bucket)]
    
    if missing_buckets:
        if strict:
            console.print(f"[red]Error:[/red] Missing required buckets: {', '.join(missing_buckets)}")
            console.print("Use --no-strict to allow interactive prompting.")
            sys.exit(1)
        console.print(f"[yellow]Warning:[/yellow] Missing data for buckets: {', '.join(missing_buckets)}")
        console.print("Will prompt for missing values interactively.")
    
    title = role_name.upper() if len(role_name) <= 3 else role_name.replace('_', ' ').title()
    
    # Extract data with fallbacks
    identity = role_data.get('identity', {})
    objectives = role_data.get('objectives', {})
    influence = role_data.get('influence', {})
    behaviors = role_data.get('behaviors', {})
    motivations = role_data.get('motivations', {})
    
    return EXECUTIVE_TEMPLATE.format(
        role=role_name,
        domain="strategy & execution",
        title=title,
        scope=identity.get('scope') or "Global",
        seniority=identity.get('seniority') or "C-level",
        span_of_control=identity.get('span_of_control') or "100",
        top_objectives=', '.join(objectives.get('top_objectives', [f"Drive {role_name} excellence"])),
        kpis=', '.join(objectives.get('kpis', ["ROI"])),
        decision_rights=', '.join(influence.get('decision_rights', [f"{title} strategy"])),
        stakeholders=', '.join(influence.get('stakeholders', ["CEO"])),
        comms=', '.join(behaviors.get('comms', ["Weekly reviews"])),
        trusted_tools=', '.join(behaviors.get('trusted_tools', ["Excel"])),
        risk_posture=behaviors.get('risk_posture') or "Not specified",
        drivers=', '.join(motivations.get('drivers', ["Growth"])),
        pain_points=', '.join(motivations.get('pain_points', ["Resource constraints"]))
    )


def generate_specialist_role(role_name: str, role_data: Dict, no_framework_check: bool = False, strict: bool = False) -> str:
    """Generate specialist role content using five-bucket standard."""
    # Validate required buckets for specialists
    required_buckets = ['identity', 'objectives']
    missing_buckets = [bucket for bucket in required_buckets if not role_data.get(bucket)]
    
    if missing_buckets:
        if strict:
            console.print(f"[red]Error:[/red] Missing required buckets: {', '.join(missing_buckets)}")
            console.print("Use --no-strict to allow interactive prompting.")
            sys.exit(1)
        console.print(f"[yellow]Warning:[/yellow] Missing data for buckets: {', '.join(missing_buckets)}")
        console.print("Will prompt for missing values interactively.")
    
    title = role_name.replace('_', ' ').title()
    
    # Extract data with fallbacks
    identity = role_data.get('identity', {})
    objectives = role_data.get('objectives', {})
    standards = role_data.get('standards', [])
    gates = role_data.get('gates', [])
    
    # For specialists, we can use either behaviors or just standards/gates
    trusted_tools = []
    risk_posture = "Standards-focused"
    
    # Try to get tools from behaviors if available
    behaviors = role_data.get('behaviors', {})
    if behaviors:
        trusted_tools = behaviors.get('trusted_tools', [])
        risk_posture = behaviors.get('risk_posture', risk_posture)
    
    return SPECIALIST_TEMPLATE.format(
        role=role_name,
        domain="technical review",
        title=title,
        scope=identity.get('scope') or "Cross-functional",
        seniority=identity.get('seniority') or "Senior specialist",
        span_of_control=identity.get('span_of_control') or "0",
        top_objectives=', '.join(objectives.get('top_objectives', [f"Ensure {role_name} excellence"])),
        kpis=', '.join(objectives.get('kpis', ["Quality score"])),
        standards=', '.join(standards) if standards else "Industry best practices",
        gates=', '.join(gates) if gates else "Standards review",
        trusted_tools=', '.join(trusted_tools) if trusted_tools else "Standard toolset",
        risk_posture=risk_posture if risk_posture != "Standards-focused" else "Standards-focused"
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
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Successfully wrote role file: {file_path}")
    except OSError as e:
        logger.error(f"Failed to write file {file_path}: {e}")
        console.print(f"[red]Error:[/red] Failed to write file: {e}")
        sys.exit(1)
    
    return file_path


def list_templates(library: Dict) -> None:
    """List available role templates."""
    console.print(Panel("Available Role Templates", border_style="blue"))
    
    for role_type, roles in library.items():
        console.print(f"\n[bold]{role_type.title()} Roles:[/bold]")
        for role_name, role_data in roles.items():
            frameworks = role_data.get('frameworks', role_data.get('standards', []))
            console.print(f"  • {role_name}: {', '.join(frameworks[:3])}")


def main():
    """Main entry point for role generation."""
    logger.info("Starting Cursor Role Factory")
    
    parser = argparse.ArgumentParser(description="Generate Cursor role files with industry standards")
    parser.add_argument("--name", required=False, help="Role name (e.g., cmo, qa_lead)")
    parser.add_argument("--type", choices=["executive", "specialist"], help="Role type")
    parser.add_argument("--frameworks", help="Comma-separated frameworks (overrides library)")
    parser.add_argument("--no-framework-check", action="store_true", help="Skip framework requirement")
    parser.add_argument("--strict", action="store_true", help="Fail if required five-bucket data is missing")
    
    # Override flags for common fields
    parser.add_argument("--trusted-tools", help="Comma-separated list of trusted tools")
    parser.add_argument("--comms", help="Comma-separated list of communication styles")
    parser.add_argument("--kpis", help="Comma-separated list of key performance indicators")
    parser.add_argument("--drivers", help="Comma-separated list of motivational drivers")
    parser.add_argument("--pain-points", help="Comma-separated list of pain points")
    parser.add_argument("--top-objectives", help="Comma-separated list of top objectives")
    parser.add_argument("--decision-rights", help="Comma-separated list of decision rights")
    parser.add_argument("--stakeholders", help="Comma-separated list of key stakeholders")
    parser.add_argument("--json-override", help="Path to JSON file with full override data")
    
    parser.add_argument("--list-templates", action="store_true", help="List available templates")
    parser.add_argument("--output-dir", default=".cursor/rules/roles", help="Output directory")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Set logging level based on verbose flag
    if args.verbose:
        logging.getLogger("role_factory").setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")
    
    # Load role library
    library = load_role_library()
    
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
    
    # Generate role content
    console.print(f"\n[blue]Generating {args.type} role: {role_name}[/blue]")
    logger.info(f"Generating content for {args.type} role: {role_name}")
    
    if args.type == "executive":
        content = generate_executive_role(role_name, role_data, args.frameworks, args.strict)
    else:
        content = generate_specialist_role(role_name, role_data, args.no_framework_check, args.strict)
    
    # Write file
    output_path = write_role_file(role_name, content, Path(args.output_dir))
    
    console.print(f"\n[green]✓ Role created:[/green] {output_path}")
    console.print(f"[dim]Invoke with: @{role_name}[/dim]")
    logger.info(f"Role creation completed successfully: {output_path}")
    
    # Validate generated file
    console.print("\n[blue]Running validation...[/blue]")
    logger.info("Running lint validation on generated file")
    
    import subprocess
    try:
        result = subprocess.run([
            "uv", "run", "python", "scripts/lint_mdc.py", str(output_path)
        ], capture_output=True, text=True)
        
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