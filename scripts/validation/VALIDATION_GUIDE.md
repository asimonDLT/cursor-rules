# Validation Scripts

Cross-cutting validation scripts that work across domains, roles, and other cursor rule components.

## Scripts

### `lint_mdc.py`
Validates .mdc files for line count compliance and structure.

**Usage:**
```bash
# Validate single file
uv run python scripts/validation/lint_mdc.py path/to/file.mdc

# Validate multiple files
uv run python scripts/validation/lint_mdc.py file1.mdc file2.mdc

# Validate with custom line limit
uv run python scripts/validation/lint_mdc.py --limit 200 file.mdc
```

**Options:**
- `--limit` - Line count limit (default: 150)
- `--verbose` - Enable verbose output
- Files to validate (required)

**Features:**
- **Line Count Validation**: Ensures files don't exceed configurable limits
- **Structure Validation**: Checks for required sections (role-specific)
- **Rich Console Output**: Color-coded results and progress
- **Batch Processing**: Validate multiple files at once
- **Detailed Reporting**: Shows passing/failing files with metrics
- **Cross-Platform**: Works on all operating systems

**Validation Checks:**
- **Line Limits**: Files must be under specified line count (default 150)
- **Structure**: Role files need specific sections (Identity & Context, etc.)
- **Format**: Proper .mdc file structure
- **Readability**: Warnings for missing recommended sections

**Exit Codes:**
- `0` - All files passed validation
- `1` - One or more files failed validation

## Integration

This validation script is automatically called by:
- **Domain Creation**: `scripts/domains/create_domain_rule.py`
- **Role Creation**: `scripts/roles/create_role.py`

Both creation scripts run validation after generating files to ensure compliance.

## Output Examples

**Success:**
```
✓ file.mdc within limit: 122 lines
✓ All files passed validation!
```

**Failure:**
```
✗ file.mdc exceeds limit: 182 lines (max: 150)
⚠ Missing specialist sections: ## Identity & Context
✗ 1 of 2 files failed validation
```

## Related Files

- **Used by**: Domain and role creation scripts
- **Validates**: All .mdc files in the cursor rules system
- **Templates**: Ensures generated files meet standards