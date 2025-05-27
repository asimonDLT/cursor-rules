# Scripts Directory

This directory contains organized scripts for managing cursor rules, domains, roles, and tools.

## Structure

```
scripts/
├── domains/          # Domain-related operations
├── roles/           # Role-related operations  
├── tools/           # Tool registry operations
├── validation/      # Cross-cutting validation
├── backup/          # Backup and migration data
└── SCRIPTS_OVERVIEW.md        # This file
```

## Quick Reference

### Domain Operations
```bash
# Create new domain
uv run python scripts/domains/create_domain_rule.py --name your_domain --category backend

# Validate domain consistency
uv run python scripts/domains/validate_domains.py
```

### Role Operations
```bash
# Create new role
uv run python scripts/roles/create_role.py --name your_role --type specialist

# Validate role library
uv run python scripts/roles/lint_role_library.py .cursor/rules/tools/role_library.json

# Migrate role data
uv run python scripts/roles/migrate_roles.py
```

### Tool Operations
```bash
# Validate tool registry
uv run python scripts/tools/lint_tool_registry.py .cursor/rules/tools/tool_registry.json
```

### Validation
```bash
# Validate .mdc files
uv run python scripts/validation/lint_mdc.py path/to/file.mdc
```

## Architecture Alignment

This structure mirrors the production cursor rules architecture:

- **scripts/domains/** → manages `.cursor/rules/domains/`
- **scripts/roles/** → manages `.cursor/rules/roles/`  
- **scripts/tools/** → manages `.cursor/rules/tools/`
- **scripts/validation/** → validates all `.mdc` files

## Adding New Scripts

When adding new scripts:

1. **Choose the right subdirectory** based on what the script manages
2. **Follow naming conventions**: `{action}_{target}.py` (e.g., `create_domain_rule.py`)
3. **Include proper documentation** - docstrings and usage examples
4. **Add validation** where appropriate
5. **Update this README** when adding new categories

## Script Categories

### Creation Scripts
Scripts that generate new files or structures:
- `domains/create_domain_rule.py` - Create domain rule files
- `roles/create_role.py` - Create role agent files

### Validation Scripts  
Scripts that check correctness and consistency:
- `validation/lint_mdc.py` - Validate .mdc file format and line limits
- `roles/lint_role_library.py` - Validate role library structure
- `tools/lint_tool_registry.py` - Validate tool registry integrity
- `domains/validate_domains.py` - Check domain consistency

### Migration Scripts
Scripts that update or transform existing data:
- `roles/migrate_roles.py` - Upgrade role library format

### Backup
Backup files and migration artifacts:
- `backup/role_library.json.backup` - Role library backup

## Dependencies

Most scripts use:
- **Rich** - Console output and formatting
- **Standard Library** - JSON, logging, argparse, pathlib
- **Cross-references** - Some scripts call validation scripts after creation