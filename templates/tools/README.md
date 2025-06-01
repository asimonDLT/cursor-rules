# Tools Templates

This directory contains templates for tool registry configurations and tool-related structures.

## Purpose

Templates in this directory help create and manage:
- Tool registry configurations
- Tool category definitions
- Tool integration patterns
- Tool metadata structures

## Coming Soon

This directory is currently empty but reserved for future tool configuration templates such as:

- **`tool_registry_template.json`** - Template for creating new tool registries
- **`tool_category_template.json`** - Template for defining new tool categories
- **`integration_template.json`** - Template for tool integration configurations
- **`tool_metadata_template.json`** - Template for tool metadata structures

## Usage

When tool templates are added, they will follow the same pattern as domain and role templates:

```bash
# Example future usage
uv run python scripts/create_tool_config.py --type registry --name your_config
```

## Related

- **Tool Registry**: `.cursor/rules/tools/tool_registry.json`
- **Domain Templates**: `../domains/`
- **Role Templates**: `../roles/`
