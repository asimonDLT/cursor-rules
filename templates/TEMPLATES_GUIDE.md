# Templates Directory

This directory contains organized templates for creating different types of cursor rules and configurations.

## Structure

```
templates/
├── domains/          # Domain rule templates and guides
├── roles/           # Role-based agent templates  
├── tools/           # Tool registry and configuration templates
└── templates_guide.md        # This file
```

## Subdirectories

### 📁 domains/
Templates and guides for creating domain-specific rules (e.g., backend, frontend, cloud)

- **`DOMAIN_CREATION_GUIDE.md`** - Complete guide for creating new domains
- **`domain_creation_template.json`** - Comprehensive reference template with all parameters
- **`domain_rule.mdc.template`** - Basic template used by creation scripts
- **`enhanced_domain_rule.mdc.template`** - Advanced template with all recommended sections
- **`example_domain_override.json`** - Working example showing proper usage

### 📁 roles/
Templates for creating role-based AI agents (e.g., specialists, executives)

- **`executive_role.mdc.template`** - Template for C-level and executive roles
- **`specialist_role.mdc.template`** - Template for technical specialist roles

### 📁 tools/
Templates for tool registry configurations and tool-related structures

- Currently empty - reserved for future tool configuration templates

## Usage

### Creating a New Domain
```bash
# Use the comprehensive guide in domains/
cd domains/
cat DOMAIN_CREATION_GUIDE.md

# Create with script
uv run python scripts/create_domain_rule.py --name your_domain --category backend
```

### Creating a New Role
```bash
# Create specialist role
uv run python scripts/create_role.py --name your_role --type specialist

# Create executive role  
uv run python scripts/create_role.py --name your_role --type executive
```

## Template Development

When adding new templates:

1. **Choose the right subdirectory** based on what you're templating
2. **Follow naming conventions**: `{type}_{purpose}.{extension}.template`
3. **Include documentation** - README files or inline comments
4. **Test templates** with the creation scripts
5. **Update this README** when adding new template types

## Architecture Alignment

This structure aligns with the overall cursor rules architecture:

- **domains/** → `.cursor/rules/domains/`
- **roles/** → `.cursor/rules/roles/`  
- **tools/** → `.cursor/rules/tools/`

Each subdirectory contains templates for creating the corresponding production artifacts.