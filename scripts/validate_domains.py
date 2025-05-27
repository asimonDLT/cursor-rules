#!/usr/bin/env python3
"""
Domain Validation Script - Ensures consistency between file system and tool_registry.json.
Validates that domain directories and registry entries are synchronized.
"""

import json
import logging
import re
import sys
import uuid
from pathlib import Path
from typing import Dict, List, Set, Tuple

from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

# Configure structured logging with correlation IDs
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(console=Console(), rich_tracebacks=True)],
)
logger = logging.getLogger("validate_domains")

console = Console()


def load_tool_registry(registry_path: Path, correlation_id: str) -> Dict:
    """
    Load and parse the tool registry JSON file.
    
    Args:
        registry_path: Path to tool_registry.json
        correlation_id: Unique identifier for this validation run
        
    Returns:
        Parsed registry data or empty dict on error
    """
    logger.info(f"[{correlation_id}] Loading tool registry from {registry_path}")
    
    try:
        with open(registry_path, "r", encoding="utf-8") as f:
            registry = json.load(f)
        logger.info(f"[{correlation_id}] Successfully loaded tool registry")
        return registry
    except json.JSONDecodeError as e:
        logger.error(f"[{correlation_id}] Invalid JSON in tool registry: {e}")
        console.print(f"[red]✗[/red] Invalid JSON in tool registry: {e}")
        return {}
    except FileNotFoundError:
        logger.error(f"[{correlation_id}] Tool registry not found: {registry_path}")
        console.print(f"[red]✗[/red] Tool registry not found: {registry_path}")
        return {}
    except Exception as e:
        logger.error(f"[{correlation_id}] Error loading tool registry: {e}")
        console.print(f"[red]✗[/red] Error loading tool registry: {e}")
        return {}


def get_filesystem_domains(rules_dir: Path, correlation_id: str) -> Set[str]:
    """
    Get domain directories from the file system.
    
    Args:
        rules_dir: Path to .cursor/rules directory
        correlation_id: Unique identifier for this validation run
        
    Returns:
        Set of domain directory names
    """
    logger.info(f"[{correlation_id}] Scanning filesystem domains in {rules_dir}")
    
    if not rules_dir.exists():
        logger.warning(f"[{correlation_id}] Rules directory does not exist: {rules_dir}")
        return set()
    
    domains = set()
    for item in rules_dir.iterdir():
        if item.is_dir() and item.name != "roles":  # Exclude roles directory
            domains.add(item.name)
    
    logger.info(f"[{correlation_id}] Found {len(domains)} filesystem domains: {sorted(domains)}")
    return domains


def get_registry_domains(registry: Dict, correlation_id: str) -> Tuple[Set[str], Set[str]]:
    """
    Get domain names from tool registry.
    
    Args:
        registry: Parsed tool registry data
        correlation_id: Unique identifier for this validation run
        
    Returns:
        Tuple of (domain_mappings domains, domain_metadata domains)
    """
    logger.info(f"[{correlation_id}] Extracting domains from tool registry")
    
    domain_mappings = set(registry.get("domain_mappings", {}).keys())
    domain_metadata = set(registry.get("domain_metadata", {}).keys())
    
    logger.info(f"[{correlation_id}] Found {len(domain_mappings)} domain_mappings: {sorted(domain_mappings)}")
    logger.info(f"[{correlation_id}] Found {len(domain_metadata)} domain_metadata: {sorted(domain_metadata)}")
    
    return domain_mappings, domain_metadata


def validate_domain_consistency(
    filesystem_domains: Set[str],
    registry_mappings: Set[str], 
    registry_metadata: Set[str],
    correlation_id: str
) -> Tuple[bool, List[str]]:
    """
    Validate consistency between filesystem and registry domains.
    
    Args:
        filesystem_domains: Domain directories from filesystem
        registry_mappings: Domains from domain_mappings
        registry_metadata: Domains from domain_metadata
        correlation_id: Unique identifier for this validation run
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    logger.info(f"[{correlation_id}] Validating domain consistency")
    
    errors = []
    warnings = []
    
    # Define technical domains that don't need filesystem directories
    technical_domains = {"aws", "python", "database", "data_engineer", "data_analyst"}
    
    # Check for filesystem domains missing from domain_mappings
    missing_from_mappings = filesystem_domains - registry_mappings
    if missing_from_mappings:
        for domain in sorted(missing_from_mappings):
            errors.append(f"Filesystem domain '{domain}' missing from domain_mappings")
    
    # Check for filesystem domains missing from domain_metadata
    missing_from_metadata = filesystem_domains - registry_metadata
    if missing_from_metadata:
        for domain in sorted(missing_from_metadata):
            errors.append(f"Filesystem domain '{domain}' missing from domain_metadata")
    
    # Check for organizational domains (non-technical) missing filesystem directories
    missing_filesystem_mappings = (registry_mappings - filesystem_domains) - technical_domains
    if missing_filesystem_mappings:
        for domain in sorted(missing_filesystem_mappings):
            errors.append(f"Organizational domain '{domain}' in domain_mappings but has no filesystem directory")
    
    missing_filesystem_metadata = (registry_metadata - filesystem_domains) - technical_domains
    if missing_filesystem_metadata:
        for domain in sorted(missing_filesystem_metadata):
            errors.append(f"Organizational domain '{domain}' in domain_metadata but has no filesystem directory")
    
    # Check for inconsistency between domain_mappings and domain_metadata
    mappings_only = registry_mappings - registry_metadata
    metadata_only = registry_metadata - registry_mappings
    
    if mappings_only:
        for domain in sorted(mappings_only):
            errors.append(f"Domain '{domain}' in domain_mappings but not in domain_metadata")
    
    if metadata_only:
        for domain in sorted(metadata_only):
            errors.append(f"Domain '{domain}' in domain_metadata but not in domain_mappings")
    
    # Log technical domains as informational (not errors)
    technical_in_registry = (registry_mappings | registry_metadata) & technical_domains
    if technical_in_registry:
        logger.info(f"[{correlation_id}] Technical domains (role-based, no filesystem): {sorted(technical_in_registry)}")
    
    is_valid = len(errors) == 0
    
    if is_valid:
        logger.info(f"[{correlation_id}] Domain consistency validation passed")
    else:
        logger.error(f"[{correlation_id}] Domain consistency validation failed with {len(errors)} errors")
    
    return is_valid, errors


def validate_domain_metadata_schema(
    registry: Dict, correlation_id: str
) -> Tuple[bool, List[str]]:
    """
    Validate the enhanced domain metadata schema fields.
    
    Args:
        registry: Parsed tool registry data
        correlation_id: Unique identifier for this validation run
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    logger.info(f"[{correlation_id}] Validating domain metadata schema")
    
    errors = []
    domain_metadata = registry.get("domain_metadata", {})
    valid_statuses = {"active", "beta", "deprecated"}
    
    for domain_name, metadata in domain_metadata.items():
        # Validate status field
        status = metadata.get("status")
        if not status:
            errors.append(f"Domain '{domain_name}' missing required 'status' field")
        elif status not in valid_statuses:
            errors.append(f"Domain '{domain_name}' has invalid status '{status}'. Must be one of: {valid_statuses}")
        
        # Validate last_reviewed field format (YYYY-MM-DD)
        last_reviewed = metadata.get("last_reviewed")
        if last_reviewed:
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', last_reviewed):
                errors.append(f"Domain '{domain_name}' has invalid last_reviewed format '{last_reviewed}'. Must be YYYY-MM-DD")
        
        # Validate template_type field exists
        template_type = metadata.get("template_type")
        if not template_type:
            errors.append(f"Domain '{domain_name}' missing required 'template_type' field")
        
        # Validate required_sections is a list
        required_sections = metadata.get("required_sections")
        if required_sections is not None and not isinstance(required_sections, list):
            errors.append(f"Domain '{domain_name}' 'required_sections' must be a list")
    
    is_valid = len(errors) == 0
    
    if is_valid:
        logger.info(f"[{correlation_id}] Domain metadata schema validation passed")
    else:
        logger.error(f"[{correlation_id}] Domain metadata schema validation failed with {len(errors)} errors")
    
    return is_valid, errors


def validate_required_sections(
    filesystem_domains: Set[str], registry: Dict, correlation_id: str
) -> Tuple[bool, List[str]]:
    """
    Validate that domain .mdc files contain all required sections.
    
    Args:
        filesystem_domains: Domain directories from filesystem
        registry: Parsed tool registry data
        correlation_id: Unique identifier for this validation run
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    logger.info(f"[{correlation_id}] Validating required sections in domain files")
    
    errors = []
    domain_metadata = registry.get("domain_metadata", {})
    script_dir = Path(__file__).parent
    domains_dir = script_dir.parent / ".cursor" / "rules" / "domains"
    
    for domain_name in filesystem_domains:
        if domain_name not in domain_metadata:
            continue  # Skip domains not in metadata (handled by other validation)
        
        metadata = domain_metadata[domain_name]
        required_sections = metadata.get("required_sections", [])
        
        if not required_sections:
            continue  # No required sections defined
        
        # Find the domain's .mdc file
        domain_dir = domains_dir / domain_name
        mdc_files = list(domain_dir.glob("*.mdc"))
        
        if not mdc_files:
            errors.append(f"Domain '{domain_name}' has no .mdc files but has required_sections defined")
            continue
        
        # Check each .mdc file for required sections
        for mdc_file in mdc_files:
            try:
                with open(mdc_file, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Extract all H2 headers from the file
                h2_headers = re.findall(r'^## (.+)$', content, re.MULTILINE)
                found_headers = {f"## {header}" for header in h2_headers}
                
                # Check for missing required sections
                missing_sections = set(required_sections) - found_headers
                if missing_sections:
                    errors.append(
                        f"Domain '{domain_name}' file '{mdc_file.name}' missing required sections: {sorted(missing_sections)}"
                    )
                
            except (OSError, UnicodeDecodeError) as e:
                errors.append(f"Error reading domain file '{mdc_file}': {e}")
    
    is_valid = len(errors) == 0
    
    if is_valid:
        logger.info(f"[{correlation_id}] Required sections validation passed")
    else:
        logger.error(f"[{correlation_id}] Required sections validation failed with {len(errors)} errors")
    
    return is_valid, errors


def display_validation_summary(
    filesystem_domains: Set[str],
    registry_mappings: Set[str],
    registry_metadata: Set[str], 
    is_valid: bool,
    errors: List[str],
    correlation_id: str
) -> None:
    """Display a summary of the domain validation results."""
    logger.info(f"[{correlation_id}] Generating validation summary")
    
    table = Table(
        title="Domain Validation Summary",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Source", style="cyan")
    table.add_column("Count", justify="right", style="yellow")
    table.add_column("Domains", style="white")
    
    table.add_row("Filesystem", str(len(filesystem_domains)), ", ".join(sorted(filesystem_domains)))
    table.add_row("domain_mappings", str(len(registry_mappings)), ", ".join(sorted(registry_mappings)))
    table.add_row("domain_metadata", str(len(registry_metadata)), ", ".join(sorted(registry_metadata)))
    
    console.print(table)
    
    if is_valid:
        console.print("\n[green]✓ Domain validation passed - all domains are consistent[/green]")
    else:
        console.print(f"\n[red]✗ Domain validation failed with {len(errors)} errors:[/red]")
        for error in errors:
            console.print(f"  [red]•[/red] {error}")


def main():
    """Main entry point for domain validation."""
    correlation_id = str(uuid.uuid4())[:8]
    logger.info(f"[{correlation_id}] Starting domain validation")
    
    # Set up paths
    script_dir = Path(__file__).parent
    registry_path = script_dir.parent / ".cursor/rules/tools/tool_registry.json"
    rules_dir = script_dir.parent / ".cursor" / "rules" / "domains"
    
    # Load tool registry
    registry = load_tool_registry(registry_path, correlation_id)
    if not registry:
        logger.error(f"[{correlation_id}] Cannot proceed without valid tool registry")
        sys.exit(1)
    
    # Get domains from filesystem and registry
    filesystem_domains = get_filesystem_domains(rules_dir, correlation_id)
    registry_mappings, registry_metadata = get_registry_domains(registry, correlation_id)
    
    # Validate consistency
    consistency_valid, consistency_errors = validate_domain_consistency(
        filesystem_domains, registry_mappings, registry_metadata, correlation_id
    )
    
    # Validate domain metadata schema
    schema_valid, schema_errors = validate_domain_metadata_schema(registry, correlation_id)
    
    # Validate required sections in domain files
    sections_valid, sections_errors = validate_required_sections(
        filesystem_domains, registry, correlation_id
    )
    
    # Combine all validation results
    all_errors = consistency_errors + schema_errors + sections_errors
    is_valid = consistency_valid and schema_valid and sections_valid
    
    # Display results
    display_validation_summary(
        filesystem_domains, registry_mappings, registry_metadata, is_valid, all_errors, correlation_id
    )
    
    # Exit with appropriate code
    if is_valid:
        logger.info(f"[{correlation_id}] Domain validation completed successfully")
        sys.exit(0)
    else:
        logger.error(f"[{correlation_id}] Domain validation failed")
        sys.exit(1)


if __name__ == "__main__":
    main() 