#!/usr/bin/env python3
"""
Setup script for cursor rules project.
Handles initial setup, migration, and validation of the cursor rules environment.
"""

import argparse
import json
import logging
import shutil
import sys
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=Console(), rich_tracebacks=True)],
)

logger = logging.getLogger("cursor_setup")
console = Console()


class SetupManager:
    """Handles cursor rules project setup and migration."""

    def __init__(self, project_root: Path | None = None):
        """Initialize setup manager.

        Args:
            project_root: Optional project root path. If None, auto-detects.
        """
        self.project_root = project_root or self._find_project_root()
        self.config_path = self.project_root / "cursor_rules_config.json"

    def _find_project_root(self) -> Path:
        """Find project root containing cursor rules markers."""
        current = Path(__file__).parent.parent

        markers = [".cursor", "cursor_rules_config.json", "pyproject.toml", ".git"]

        while current != current.parent:
            if any((current / marker).exists() for marker in markers):
                return current
            current = current.parent

        # Fallback to current directory
        return Path.cwd()

    def validate_environment(self) -> list[str]:
        """Validate the cursor rules environment.

        Returns:
            List of validation issues (empty if all good)
        """
        issues = []

        # Check for required files
        required_files = [
            "pyproject.toml",
            "cursor_rules_config.json",
            ".cursor/rules/tools/tool_registry.json",
        ]

        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                issues.append(f"Missing required file: {file_path}")

        # Check for required directories
        required_dirs = [
            ".cursor/rules",
            ".cursor/rules/tools",
            ".cursor/rules/roles",
            ".cursor/rules/domains",
            "scripts/roles",
            "scripts/domains",
            "scripts/validation",
            "templates/roles",
        ]

        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                issues.append(f"Missing required directory: {dir_path}")

        # Check role library
        role_library_path = self.project_root / ".cursor/rules/tools/role_library.json"
        if not role_library_path.exists():
            backup_path = self.project_root / "scripts/backup/role_library.json.backup"
            if backup_path.exists():
                issues.append(
                    f"Role library missing but backup available at {backup_path}"
                )
            else:
                issues.append("Role library missing and no backup found")

        return issues

    def migrate_role_library(self, force: bool = False) -> bool:
        """Migrate role library from backup if needed.

        Args:
            force: If True, overwrite existing library

        Returns:
            True if migration was performed, False otherwise
        """
        role_library_path = self.project_root / ".cursor/rules/tools/role_library.json"
        backup_path = self.project_root / "scripts/backup/role_library.json.backup"

        if role_library_path.exists() and not force:
            console.print(
                f"[yellow]Role library already exists at {role_library_path}[/yellow]"
            )
            return False

        if not backup_path.exists():
            console.print(f"[red]No backup found at {backup_path}[/red]")
            return False

        try:
            # Ensure target directory exists
            role_library_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy backup to target location
            shutil.copy2(backup_path, role_library_path)

            console.print("[green]✓ Migrated role library from backup[/green]")
            logger.info(
                f"Migrated role library from {backup_path} to {role_library_path}"
            )
            return True

        except Exception as e:
            console.print(f"[red]Failed to migrate role library: {e}[/red]")
            return False

    def create_missing_directories(self) -> None:
        """Create any missing required directories."""
        required_dirs = [
            ".cursor/rules",
            ".cursor/rules/tools",
            ".cursor/rules/roles/executive",
            ".cursor/rules/roles/specialist",
            ".cursor/rules/domains",
            "scripts/backup",
            "templates/roles",
            "templates/domains",
        ]

        created_dirs = []
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                full_path.mkdir(parents=True, exist_ok=True)
                created_dirs.append(dir_path)

        if created_dirs:
            console.print(
                f"[green]✓ Created directories: {', '.join(created_dirs)}[/green]"
            )

    def initialize_config(self, force: bool = False) -> bool:
        """Initialize configuration file if missing.

        Args:
            force: If True, overwrite existing config

        Returns:
            True if config was created, False otherwise
        """
        if self.config_path.exists() and not force:
            console.print(
                f"[yellow]Configuration already exists at {self.config_path}[/yellow]"
            )
            return False

        default_config = {
            "paths": {
                "cursor_rules": ".cursor/rules",
                "tool_registry": ".cursor/rules/tools/tool_registry.json",
                "role_library": ".cursor/rules/tools/role_library.json",
                "templates": "templates",
                "scripts": "scripts",
            },
            "validation": {
                "exclude_patterns": ["*.mdc", "*.md", "*.template"],
                "required_tools": ["uv", "ruff"],
                "mdc_linter": "scripts/validation/lint_mdc.py",
                "role_linter": "scripts/roles/lint_role_library.py",
            },
            "defaults": {
                "output_dir": ".cursor/rules/roles",
                "role_types": ["executive", "specialist"],
                "template_dir": "templates/roles",
            },
            "behavior": {
                "interactive_mode": True,
                "strict_validation": False,
                "auto_backup": True,
                "progress_indicators": True,
            },
        }

        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=2)

            console.print(
                f"[green]✓ Created configuration file at {self.config_path}[/green]"
            )
            return True

        except Exception as e:
            console.print(f"[red]Failed to create configuration: {e}[/red]")
            return False

    def run_full_setup(self, force: bool = False) -> bool:
        """Run complete setup process.

        Args:
            force: If True, overwrite existing files

        Returns:
            True if setup completed successfully
        """
        console.print(Panel("Cursor Rules Project Setup", border_style="blue"))
        console.print(f"Project root: {self.project_root}")

        success = True

        # Create missing directories
        console.print("\n[bold]Creating directories...[/bold]")
        self.create_missing_directories()

        # Initialize configuration
        console.print("\n[bold]Initializing configuration...[/bold]")
        if not self.initialize_config(force):
            success = False

        # Migrate role library if needed
        console.print("\n[bold]Setting up role library...[/bold]")
        if not self.migrate_role_library(force):
            success = False

        # Validate final state
        console.print("\n[bold]Validating environment...[/bold]")
        issues = self.validate_environment()

        if issues:
            console.print("[red]Validation issues found:[/red]")
            for issue in issues:
                console.print(f"  • {issue}")
            success = False
        else:
            console.print("[green]✓ Environment validation passed[/green]")

        return success


def main() -> None:
    """Main entry point for setup script."""
    parser = argparse.ArgumentParser(
        description="Setup and migrate cursor rules environment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full setup
  uv run python setup.py --setup

  # Just validate current environment
  uv run python setup.py --validate

  # Migrate role library from backup
  uv run python setup.py --migrate-roles --force
        """,
    )

    parser.add_argument(
        "--setup", action="store_true", help="Run full environment setup"
    )
    parser.add_argument(
        "--validate", action="store_true", help="Validate environment only"
    )
    parser.add_argument(
        "--migrate-roles", action="store_true", help="Migrate role library from backup"
    )
    parser.add_argument(
        "--create-dirs", action="store_true", help="Create missing directories only"
    )
    parser.add_argument(
        "--init-config", action="store_true", help="Initialize configuration only"
    )
    parser.add_argument(
        "--force", action="store_true", help="Force overwrite existing files"
    )
    parser.add_argument("--project-root", help="Specify project root directory")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger("cursor_setup").setLevel(logging.DEBUG)

    try:
        # Initialize setup manager
        project_root = Path(args.project_root) if args.project_root else None
        setup_manager = SetupManager(project_root)

        # Run requested operations
        if args.setup:
            success = setup_manager.run_full_setup(args.force)
            if success:
                console.print("\n[green]✓ Setup completed successfully![/green]")
            else:
                console.print("\n[red]✗ Setup completed with issues[/red]")
                sys.exit(1)

        elif args.validate:
            issues = setup_manager.validate_environment()
            if issues:
                console.print("[red]Validation issues found:[/red]")
                for issue in issues:
                    console.print(f"  • {issue}")
                sys.exit(1)
            else:
                console.print("[green]✓ Environment validation passed[/green]")

        elif args.migrate_roles:
            if setup_manager.migrate_role_library(args.force):
                console.print("[green]✓ Role library migration completed[/green]")
            else:
                console.print("[red]✗ Role library migration failed[/red]")
                sys.exit(1)

        elif args.create_dirs:
            setup_manager.create_missing_directories()
            console.print("[green]✓ Directory creation completed[/green]")

        elif args.init_config:
            if setup_manager.initialize_config(args.force):
                console.print("[green]✓ Configuration initialization completed[/green]")
            else:
                console.print("[red]✗ Configuration initialization failed[/red]")
                sys.exit(1)
        else:
            # No specific action, show help
            parser.print_help()

    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error occurred")
        console.print(f"[red]Unexpected error:[/red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
