# Domain Scripts

Scripts for managing cursor rule domains and domain-related operations.

## Scripts

### `create_domain_rule.py`
Creates new domain rule files with proper structure and validation.

**Usage:**
```bash
uv run python scripts/domains/create_domain_rule.py \
  --name your_domain_name \
  --category backend \
  --description "Your domain description"
```

**Options:**
- `--name` - Domain name (required)
- `--category` - Domain category: frontend, backend, cloud, data, security, docs, martech (required)
- `--description` - Custom description (optional)
- `--output-dir` - Output directory (default: .cursor/rules/domains)
- `--verbose` - Enable verbose logging

**Features:**
- Uses templates from `templates/domains/`
- Validates input for security
- Automatically runs validation after creation
- Creates properly structured .mdc files

### `validate_domains.py`
Validates consistency between domain directories and tool registry metadata.

**Usage:**
```bash
uv run python scripts/domains/validate_domains.py
```

**Features:**
- Checks domain directories exist
- Validates tool registry metadata
- Ensures domain mappings are consistent
- Reports missing or orphaned domains

## Domain Categories

Supported domain categories:
- **frontend** - Frontend development and UI standards
- **backend** - Server-side development and APIs
- **cloud** - Cloud infrastructure and platform services
- **data** - Data engineering and analytics
- **security** - Security standards and practices
- **docs** - Documentation and technical writing
- **martech** - Marketing technology and analytics

## Related Files

- **Templates**: `templates/domains/` - Domain creation templates
- **Production**: `.cursor/rules/domains/` - Generated domain files
- **Registry**: `.cursor/rules/tools/tool_registry.json` - Domain metadata
- **Main Overview**: `../SCRIPTS_OVERVIEW.md` - Scripts directory overview
