# Role Scripts

Scripts for managing cursor rule roles and role-based AI agents.

## Scripts

### `create_role.py`
Creates new role-based agent files with industry standards and validation.

**Usage:**
```bash
# Create specialist role
uv run python scripts/roles/create_role.py \
  --name your_role_name \
  --type specialist \
  --tool-domains martech,backend

# Create executive role  
uv run python scripts/roles/create_role.py \
  --name your_role_name \
  --type executive \
  --scope "Global" \
  --seniority "C-level"
```

**Options:**
- `--name` - Role name (required)
- `--type` - Role type: executive, specialist (required)
- `--tool-domains` - Comma-separated tool domains
- `--json-override` - Path to JSON override file
- `--trusted-tools` - Comma-separated list of tools
- `--scope` - Role scope/region
- `--seniority` - Role seniority level
- `--list-templates` - Show available role templates

**Features:**
- Uses templates from `templates/roles/`
- Resolves tools from tool registry
- Supports JSON override files for complex roles
- Validates role structure after creation
- Supports both executive (5-bucket) and specialist (2+ bucket) roles

### `lint_role_library.py`
Validates role library structure and integrity.

**Usage:**
```bash
uv run python scripts/roles/lint_role_library.py .cursor/rules/tools/role_library.json
```

**Features:**
- Validates JSON structure
- Checks required fields for each role type
- Validates framework references
- Ensures bucket completeness
- Reports validation errors and warnings

### `migrate_roles.py`
Migrates role library to new schema versions.

**Usage:**
```bash
uv run python scripts/roles/migrate_roles.py
```

**Features:**
- Upgrades role library to five-bucket standard
- Creates backups before migration
- Adds placeholders for missing fields
- Validates migrated data
- Provides migration reports

## Role Types

### Executive Roles
C-level and executive roles with five required buckets:
- **Identity** - Scope, seniority, span of control
- **Objectives** - Top objectives, KPIs
- **Influence** - Decision rights, stakeholders
- **Behaviors** - Communication, tools, risk posture
- **Motivations** - Drivers, pain points

### Specialist Roles
Technical specialist roles with 2+ buckets:
- **Identity** - Scope, seniority, span of control
- **Objectives** - Top objectives, KPIs
- **Standards/Behaviors** - Technical standards or behavioral guidelines
- **Gates** - Quality gates and checkpoints (optional)

## Related Files

- **Templates**: `templates/roles/` - Role creation templates
- **Production**: `.cursor/rules/roles/` - Generated role files
- **Library**: `.cursor/rules/tools/role_library.json` - Role definitions
- **Backup**: `scripts/backup/role_library.json.backup` - Library backup