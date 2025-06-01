#!/usr/bin/env python3
"""
Migration script to upgrade role_library.json to five-bucket persona standard.
Wraps existing data into new schema and adds placeholders for missing fields.
"""

import json
import logging
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel

console = Console()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("migrate_roles")


def migrate_executive_role(role_name: str, old_data: dict[str, Any]) -> dict[str, Any]:
    """Migrate an executive role to five-bucket format."""
    new_data = {
        "identity": {
            "scope": "Global",  # Default placeholder
            "seniority": "C-level",  # Default for executives
            "span_of_control": 100,  # Placeholder
        },
        "objectives": {
            "top_objectives": [""],  # Placeholder
            "kpis": old_data.get("metrics", [""]),
        },
        "influence": {
            "decision_rights": [""],  # Placeholder
            "stakeholders": ["CEO"],  # Default placeholder
        },
        "behaviors": {
            "comms": [""],  # Placeholder
            "trusted_tools": [""],  # Placeholder
            "risk_posture": "Balanced",  # Default placeholder
        },
        "motivations": {
            "drivers": [""],  # Placeholder
            "pain_points": [""],  # Placeholder
        },
    }

    # Preserve existing data
    for key in ["frameworks", "metrics", "voice_style", "primary_goal"]:
        if key in old_data:
            new_data[key] = old_data[key]

    return new_data


def migrate_specialist_role(role_name: str, old_data: dict[str, Any]) -> dict[str, Any]:
    """Migrate a specialist role to five-bucket format."""
    new_data = {
        "identity": {
            "scope": "Cross-functional",  # Default placeholder
            "seniority": "Senior specialist",  # Default for specialists
            "span_of_control": 0,  # Default for specialists
        },
        "objectives": {
            "top_objectives": [""],  # Placeholder
            "kpis": [""],  # Placeholder
        },
    }

    # Preserve existing data
    for key in ["standards", "gates", "voice_style", "primary_goal"]:
        if key in old_data:
            new_data[key] = old_data[key]

    return new_data


def migrate_library(library_path: Path) -> dict[str, Any]:
    """Migrate the entire role library to five-bucket format."""
    logger.info(f"Loading library from {library_path}")

    with open(library_path, encoding="utf-8") as f:
        old_library = json.load(f)

    new_library = {"executive": {}, "specialist": {}}

    # Migrate executives
    if "executive" in old_library:
        console.print("[blue]Migrating executive roles...[/blue]")
        for role_name, role_data in old_library["executive"].items():
            console.print(f"  • {role_name}")
            new_library["executive"][role_name] = migrate_executive_role(
                role_name, role_data
            )

    # Migrate specialists
    if "specialist" in old_library:
        console.print("[blue]Migrating specialist roles...[/blue]")
        for role_name, role_data in old_library["specialist"].items():
            console.print(f"  • {role_name}")
            new_library["specialist"][role_name] = migrate_specialist_role(
                role_name, role_data
            )

    return new_library


def main():
    """Main migration entry point."""
    console.print(
        Panel("Role Library Migration to Five-Bucket Standard", border_style="blue")
    )

    library_path = (
        Path(__file__).parent.parent / ".cursor/rules/tools/role_library.json"
    )
    backup_path = (
        Path(__file__).parent.parent / ".cursor/rules/tools/role_library.json.backup"
    )

    if not library_path.exists():
        console.print(f"[red]Error:[/red] {library_path} not found")
        return

    # Create backup
    console.print(f"[yellow]Creating backup:[/yellow] {backup_path}")
    with open(library_path, encoding="utf-8") as f:
        backup_data = f.read()
    with open(backup_path, "w", encoding="utf-8") as f:
        f.write(backup_data)

    # Migrate
    try:
        new_library = migrate_library(library_path)

        # Write migrated library
        console.print(f"[green]Writing migrated library:[/green] {library_path}")
        with open(library_path, "w", encoding="utf-8") as f:
            json.dump(new_library, f, indent=2, ensure_ascii=False)

        console.print("\n[green]✓ Migration completed successfully![/green]")
        console.print(f"[dim]Backup saved to: {backup_path}[/dim]")
        console.print("\n[yellow]Next steps:[/yellow]")
        console.print("1. Review the migrated file and fill in placeholder values")
        console.print(
            "2. Test role generation with: uv run python scripts/roles/create_role.py --list-templates"
        )
        console.print("3. Generate a sample role to verify the new format")

    except Exception as e:
        console.print(f"[red]Migration failed:[/red] {e}")
        console.print("[yellow]Restoring backup...[/yellow]")
        with open(backup_path, encoding="utf-8") as f:
            backup_data = f.read()
        with open(library_path, "w", encoding="utf-8") as f:
            f.write(backup_data)
        console.print("[green]Backup restored[/green]")


if __name__ == "__main__":
    main()
