# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Testing
```bash
pytest                                    # Run all tests
pytest tests/test_specific_module.py      # Run specific test file
pytest -v                                # Verbose test output
pytest --cov                             # Run with coverage
```

### Linting and Validation
```bash
# Validate all .mdc files
uv run python scripts/validation/lint_mdc.py .cursor/rules/**/*.mdc

# Validate tool registry structure
uv run python scripts/tools/lint_tool_registry.py .cursor/rules/tools/tool_registry.json

# Validate role library
uv run python scripts/roles/lint_role_library.py .cursor/rules/tools/role_library.json

# Validate domain consistency
uv run python scripts/domains/validate_domains.py

# Run ruff linting (if configured)
ruff check
```

### Domain and Role Management
```bash
# Create new domain
uv run python scripts/domains/create_domain_rule.py --name domain_name --category backend --description "Description"

# Create new role  
uv run python scripts/roles/create_role.py --name role_name --type specialist --tool-domains martech,backend

# Migrate role library
uv run python scripts/roles/migrate_roles.py
```

## Architecture Overview

This is a **cursor rules organization framework** that provides a scalable structure for AI development rules across large projects. The codebase implements a hybrid modular tool system with automated role factory capabilities.

### Core Architecture Principles

**Three-Bucket Organization:**
- **Domains** (`.cursor/rules/domains/`): Technology-specific rules (aws, python, salesforce, etc.)
- **Roles** (`.cursor/rules/roles/`): Persona-based agents (executive, specialist roles)
- **Tools** (`.cursor/rules/tools/`): Centralized registry of 100+ tools across 20 categories

**Metadata-Driven System:**
- Tool registry (`tool_registry.json`) serves as single source of truth
- Domain metadata includes status tracking, template types, required sections
- Automated governance with schema validation and consistency checking

**Architecture-Aligned Organization:**
- Scripts mirror production structure (`scripts/domains/`, `scripts/roles/`, `scripts/tools/`)
- Templates organized by purpose (`templates/domains/`, `templates/roles/`)
- Clear separation of concerns with focused responsibilities

### Key Components

**Domain System:**
- Domain-specific rules load based on file types and project context
- Agent-based composition with domain experts (@aws, @python, @sf_dev)
- Comprehensive coverage: backend, frontend, cloud, data, security, docs, martech

**Role Factory:**
- Executive roles (CTO, CMO, CFO, CSO, CPO, VP Sales)
- Specialist roles (Data Analyst, Data Engineer, Salesforce Architect, QA Lead, Security)
- Tool integration through domain mappings
- Automated synchronization when tool registry updates

**Tool Registry:**
- 100+ tools across 20 categories
- Comprehensive Salesforce integration (32 tools)
- Domain mappings connecting logical domains to tool categories
- Categories include: AWS, Python, Database, MarTech, Development, Testing

### File Structure Significance

**Scripts Directory (`scripts/`):**
Each subdirectory manages specific aspects of the cursor rules architecture:
- `domains/`: Domain creation and validation
- `roles/`: Role factory and library management  
- `tools/`: Tool registry validation
- `validation/`: Cross-cutting MDC file validation
- `backup/`: Migration artifacts and backups

**Templates Directory (`templates/`):**
Production-ready templates for extending the system:
- `domains/`: Complete domain creation guides and templates
- `roles/`: Executive and specialist role templates
- `tools/`: Tool configuration templates (future expansion)

## Development Workflow

1. **Use validation scripts before committing** - All scripts include comprehensive validation
2. **Follow metadata-driven patterns** - Leverage tool registry for consistency
3. **Test with pytest** - Full test coverage for all creation and validation scripts
4. **Maintain architecture alignment** - Keep scripts and templates organized by purpose
5. **Use uv for Python execution** - All scripts use `uv run python` for consistency

## Special Considerations

- **MDC File Format**: Custom cursor rule format with specific line limit validation
- **Tool Registry Integration**: Changes to tool registry automatically propagate to roles
- **Domain Dependencies**: Some domains reference tools from specific categories
- **Salesforce Integration**: Comprehensive sf_dev domain with multi-cloud coverage
- **Enterprise Governance**: Built-in support for team ownership and review tracking