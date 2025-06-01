# Domain Creation Guide

This guide provides templates and instructions for creating new cursor rule domains.

## Quick Start

1. **Use the comprehensive template**: `domain_creation_template.json` - Contains all available parameters with explanations
2. **Create a custom override**: Copy and modify `example_domain_override.json` for your specific domain
3. **Generate the domain**: Use the creation script with your override file

## Files in this Directory

### Templates
- **`domain_creation_template.json`** - Complete reference with all parameters and options
- **`enhanced_domain_rule.mdc.template`** - Advanced MDC template with all recommended sections
- **`example_domain_override.json`** - Working example showing how to fill in the template
- **`domain_rule.mdc.template`** - Basic template used by the creation script

### Creation Process

#### Step 1: Plan Your Domain
- Define clear boundaries (what's in scope vs out of scope)
- Identify owner team and primary consumers
- List required tools and categories

#### Step 2: Update Tool Registry (if needed)
```bash
# Edit .cursor/rules/tools/tool_registry.json
# Add new tool categories, domain mappings, and metadata
```

#### Step 3: Create Basic Domain File
```bash
uv run python scripts/create_domain_rule.py \
  --name your_domain_name \
  --category backend \
  --description "Your domain description"
```

#### Step 4: Enhance with Template Content
- Use `enhanced_domain_rule.mdc.template` as a guide
- Fill in specific standards, patterns, and guidelines
- Keep under 150 lines for validation compliance

#### Step 5: Validate
```bash
# Validate the domain rule
uv run python scripts/lint_mdc.py .cursor/rules/domains/category/your_domain.mdc

# Validate tool registry
uv run python scripts/lint_tool_registry.py .cursor/rules/tools/tool_registry.json
```

## Domain Structure Best Practices

### Required Sections
- **Core Principles** - Fundamental beliefs and approaches
- **Standards & Guidelines** - Specific implementation guidance

### Recommended Sections
- **Identity & Scope** - Clear boundaries and ownership
- **Quality Targets & SLOs** - Measurable objectives
- **Common Patterns** - Recommended approaches
- **Anti-Patterns** - What to avoid
- **Tools & Resources** - Supporting tools and documentation

### Content Guidelines
- Make principles actionable and measurable
- Include decision frameworks for common choices
- Provide specific examples and code samples
- Use clear, scannable formatting
- Reference tools teams actually use

## Available Categories
- `frontend` - Frontend development and UI standards
- `backend` - Server-side development and APIs
- `cloud` - Cloud infrastructure and platform services
- `data` - Data engineering and analytics
- `security` - Security standards and practices
- `docs` - Documentation and technical writing
- `martech` - Marketing technology and analytics

## Tool Registry Parameters

### Tool Categories
```json
"your_tool_category": {
  "description": "What this category contains",
  "tools": ["Tool 1", "Tool 2", "Framework X"]
}
```

### Domain Mappings
```json
"your_domain": ["category1", "category2", "category3"]
```

### Domain Metadata
```json
"your_domain": {
  "description": "Clear description",
  "owner": "@my-org/team-name",
  "status": "active",
  "last_reviewed": "2025-05-27",
  "template_type": "your_template_type",
  "required_sections": ["## Section 1", "## Section 2"],
  "compliance_requirements": ["Requirement 1", "Requirement 2"]
}
```

## Common Template Types
- `layered_architecture` - Multi-tier applications
- `cloud_native` - Cloud infrastructure patterns
- `universal_standards` - Cross-cutting concerns
- `data_platform` - Data engineering patterns
- `component_driven` - UI/UX component systems
- `security_first` - Security-focused domains
- `language_specific` - Programming language standards
- `role_specific` - Role-based guidance

## Usage Examples

### Creating a Mobile Domain
```bash
# 1. Add mobile tools to tool_registry.json
# 2. Create the domain
uv run python scripts/create_domain_rule.py \
  --name mobile \
  --category frontend \
  --description "Mobile app development for iOS and Android"

# 3. Enhance with mobile-specific content
# 4. Validate and test
```

### Creating a DevOps Domain
```bash
# 1. Add DevOps tools to tool_registry.json
# 2. Create the domain
uv run python scripts/create_domain_rule.py \
  --name devops \
  --category cloud \
  --description "DevOps practices and infrastructure automation"
```

## Testing Your Domain

After creation, test the domain invocation:
```bash
# In your development environment
@your_domain_name
```

The domain should be recognized and provide relevant guidance for your specific area.

## Maintenance

- Review domains quarterly and update `last_reviewed` dates
- Keep tool lists current as technologies evolve
- Update compliance requirements as regulations change
- Refactor overly large domains (>150 lines) into focused sub-domains
