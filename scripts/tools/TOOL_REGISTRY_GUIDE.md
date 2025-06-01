# Tool Scripts

Scripts for managing tool registry and tool-related configurations.

## Scripts

### `lint_tool_registry.py`
Validates tool registry structure and referential integrity.

**Usage:**
```bash
uv run python scripts/tools/lint_tool_registry.py .cursor/rules/tools/tool_registry.json
```

**Features:**
- Validates JSON structure
- Checks required fields (tool_categories, domain_mappings)
- Validates referential integrity between domains and categories
- Reports unused tool categories
- Provides comprehensive validation summary
- Shows tool counts and metrics

**Validation Checks:**
- **Structure**: Proper JSON format and required top-level keys
- **Tool Categories**: Each category has description and tools list
- **Domain Mappings**: All referenced categories exist
- **Referential Integrity**: No broken references between domains and categories
- **Completeness**: Reports unused categories (warnings, not errors)

## Tool Registry Structure

The tool registry manages:

### Tool Categories
Logical groupings of related tools:
```json
"category_name": {
  "description": "What this category contains",
  "tools": ["Tool 1", "Tool 2", "Framework X"]
}
```

### Domain Mappings
Maps domains to tool categories:
```json
"domain_name": ["category1", "category2", "category3"]
```

### Domain Metadata
Governance information for each domain:
```json
"domain_name": {
  "description": "Domain purpose",
  "owner": "@team-name",
  "status": "active",
  "template_type": "architecture_type",
  "required_sections": ["## Section 1"],
  "compliance_requirements": ["Requirement 1"]
}
```

## Usage Examples

```bash
# Validate tool registry
uv run python scripts/tools/lint_tool_registry.py .cursor/rules/tools/tool_registry.json

# Get validation summary with metrics
uv run python scripts/tools/lint_tool_registry.py .cursor/rules/tools/tool_registry.json --verbose
```

## Library Explorer Integration

The tool registry is also accessible through the library-explorer CLI tool:

```bash
# Browse all tools in beautiful table format
uv run library-explorer browse tools

# Browse tools in list format
uv run library-explorer browse tools --format list

# Validate tool registry
uv run library-explorer validate
```

The library-explorer automatically uses the authoritative tool registry at `.cursor/rules/tools/tool_registry.json`.

## Related Files

- **Registry**: `.cursor/rules/tools/tool_registry.json` - Main tool registry (authoritative source)
- **Library Explorer**: `library_explorer/` - CLI tool for browsing and validating tool registry
- **Templates**: `templates/tools/` - Tool configuration templates (future)
- **Domains**: Used by domain creation and role creation scripts
