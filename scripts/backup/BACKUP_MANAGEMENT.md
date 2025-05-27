# Backup Directory

This directory contains backup files and migration artifacts from cursor rules operations.

## Files

### `role_library.json.backup`
Backup of the role library created during migration operations.

**Purpose:**
- Safety backup before role library migrations
- Allows rollback if migration fails
- Preserves original data structure for reference

**Created by:**
- `scripts/roles/migrate_roles.py` - During role library schema upgrades

**Usage:**
- Automatic backup during migrations
- Manual restore if needed: `cp backup/role_library.json.backup .cursor/rules/tools/role_library.json`

## Backup Strategy

### Automatic Backups
Scripts automatically create backups before:
- **Role Library Migration** - Schema upgrades and data transformations
- **Tool Registry Changes** - Major structural modifications (future)
- **Domain Restructuring** - Large-scale domain reorganizations (future)

### Backup Naming
Backup files use consistent naming:
- `{original_name}.backup` - Simple backup
- `{original_name}.{timestamp}.backup` - Timestamped backup (future)

### Retention
- Backups are preserved until manually cleaned
- Critical for rollback scenarios
- Review and clean periodically to manage disk space

## Related Scripts

- **`scripts/roles/migrate_roles.py`** - Creates role library backups
- **Future migration scripts** - Will follow same backup patterns

## Best Practices

1. **Always backup before migrations**
2. **Verify backup integrity** before proceeding
3. **Test restore procedures** periodically
4. **Document backup contents** for team awareness
5. **Clean old backups** when no longer needed