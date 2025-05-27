# Cursor Role Factory (v2.1)

Automated framework for creating standardized executive personas at scale with enhanced security and validation.

---

## Quick Start

```bash
# Get Help
uv run python scripts/create_role.py --help

# Generate a new role
uv run python scripts/create_role.py --name cmo --type executive

# Generate with CLI overrides (highest precedence)
uv run python scripts/create_role.py --name cto --type executive \
  --trusted-tools "New Relic, PagerDuty" \
  --comms "Slack daily stand-up, Monthly arch review" \
  --kpis "MTTR, Deployment Frequency, Lead Time" \
  --scope "Regional EMEA" \
  --span-of-control "180"

# Generate with JSON override file (middle precedence)
uv run python scripts/create_role.py --name cto --type executive \
  --json-override custom_cto.json

# Generate with mixed overrides (CLI overrides JSON)
uv run python scripts/create_role.py --name cto --type executive \
  --json-override custom_cto.json \
  --comms "Weekly all-hands"  # This will override JSON comms

# Validate existing roles
uv run python scripts/lint_mdc.py .cursor/rules/roles/*.mdc

# List available role templates
uv run python scripts/create_role.py --list-templates

# Enable verbose logging for debugging
uv run python scripts/create_role.py --name cmo --type executive --verbose
```

**Requirements:** Python 3.12+ with uv package manager

### CLI Help Reference

```console
$ uv run python scripts/create_role.py --help

usage: create_role.py [-h] [--name NAME] [--type {executive,specialist}] 
                      [--frameworks FRAMEWORKS] [--no-framework-check] [--strict] 
                      [--trusted-tools TRUSTED_TOOLS] [--comms COMMS] [--kpis KPIS] 
                      [--drivers DRIVERS] [--pain-points PAIN_POINTS]
                      [--top-objectives TOP_OBJECTIVES] [--decision-rights DECISION_RIGHTS]
                      [--stakeholders STAKEHOLDERS] [--scope SCOPE] [--seniority SENIORITY]
                      [--span-of-control SPAN_OF_CONTROL] [--json-override JSON_OVERRIDE]
                      [--list-templates] [--output-dir OUTPUT_DIR] [--verbose]

Generate Cursor role files with industry standards

options:
  -h, --help            show this help message and exit
  --name NAME           Role name (e.g., cmo, qa_lead)
  --type {executive,specialist}
                        Role type
  --frameworks FRAMEWORKS
                        Comma-separated frameworks (overrides library)
  --no-framework-check  Skip framework requirement
  --strict              Fail if required five-bucket data is missing
  
  Override flags for common fields:
  --trusted-tools TRUSTED_TOOLS
                        Comma-separated list of trusted tools
  --comms COMMS         Comma-separated list of communication styles
  --kpis KPIS           Comma-separated list of key performance indicators
  --drivers DRIVERS     Comma-separated list of motivational drivers
  --pain-points PAIN_POINTS
                        Comma-separated list of pain points
  --top-objectives TOP_OBJECTIVES
                        Comma-separated list of top objectives
  --decision-rights DECISION_RIGHTS
                        Comma-separated list of decision rights
  --stakeholders STAKEHOLDERS
                        Comma-separated list of key stakeholders
  --scope SCOPE         Role scope/region (e.g., Global, Regional EMEA)
  --seniority SENIORITY Role seniority level (e.g., C-level, Senior specialist)
  --span-of-control SPAN_OF_CONTROL
                        Number of people in span of control
  
  Advanced options:
  --json-override JSON_OVERRIDE
                        Path to JSON file with full override data
  --list-templates      List available templates
  --output-dir OUTPUT_DIR
                        Output directory (default: .cursor/rules/roles)
  --verbose, -v         Enable verbose logging
```

---

## A. Role Creation Rules

1. **Naming:** `{role}.mdc` in `.cursor/rules/roles/` (e.g., `cmo.mdc`, `qa_lead.mdc`)
2. **Size Limit:** 150 lines max (enforced by `lint_mdc.py`)
3. **Versioning:** Semantic versioning in file header
4. **Five-Bucket Standard:** Executive personas **must** populate ≥ 1 attribute in each of the five buckets (Identity, Objectives, Influence, Behaviors, Motivations). Specialists must cover Identity, Objectives and either Standards *or* Behaviors.
5. **Output:** Standardized decision template required
6. **Security:** Input validation prevents injection attacks and enforces length limits
7. **Validation:** Auto-validation of role library structure on startup

---

## B. Role Templates by Type

### Executive Template (`--type executive`)
Generated as `.mdc` file with front-matter:

```
---
rule_type: Agent Requested
description: {{ROLE}} perspective for {{DOMAIN}}. Opt-in via @{{ROLE}}.
---

# {{TITLE}} (v1.0)

## Identity & Context
* Scope / region: {{SCOPE}}
* Seniority: {{SENIORITY}}
* Span of control: {{SPAN_OF_CONTROL}}

## Objectives, KPIs & Mandate
* Top objectives: {{TOP_OBJECTIVES}}
* Success metrics: {{KPIS}}

## Influence & Decision Power
* Decision rights: {{DECISION_RIGHTS}}
* Key stakeholders: {{STAKEHOLDERS}}

## Behaviors, Tools & Preferences
* Comms style: {{COMMS}}
* Trusted tools: {{TRUSTED_TOOLS}}
* Risk posture: {{RISK_POSTURE}}

## Motivations, Pain Points & Constraints
* Drivers: {{DRIVERS}}
* Pain points: {{PAIN_POINTS}}

> Project rules override this Role if they conflict.

## Output Template

**{{TITLE}} Assessment:**
- {finding_1}
- {finding_2}

**Decision:** <GO / NO-GO / REVISE>
**Next steps:**
- {action_1}
- {action_2}
```

### Specialist Template (`--type specialist`)
Generated as `.mdc` file with front-matter:

```
---
rule_type: Agent Requested
description: {{ROLE}} expertise for {{DOMAIN}}. Opt-in via @{{ROLE}}.
---

# {{TITLE}} (v1.0)

## Identity & Context
* Scope / focus: {{SCOPE}}
* Seniority: {{SENIORITY}}
* Span of control: {{SPAN_OF_CONTROL}}

## Objectives & Quality Standards
* Top objectives: {{TOP_OBJECTIVES}}
* Success metrics: {{KPIS}}
* Standards: {{STANDARDS}}

## Quality Gates & Behaviors
* Quality gates: {{GATES}}
* Trusted tools: {{TRUSTED_TOOLS}}
* Risk posture: {{RISK_POSTURE}}

> Project rules override this Role if they conflict.

## Output Template

**{{TITLE}} Review:**
- {technical_finding}
- {recommendation}

**Status:** <APPROVED / BLOCKED / NEEDS_REVISION>
**Next steps:**
- {action}
```

---

## C. Override System

### Three-Tier Precedence
The role generator supports flexible customization through a three-tier precedence system:

1. **CLI Flags (Highest)** - Override specific fields for quick customization
2. **JSON Override File (Middle)** - Power-user bulk overrides
3. **Role Library (Lowest)** - Default values from `role_library.json`

### CLI Override Flags
```bash
--trusted-tools "Tool1, Tool2, Tool3"     # behaviors.trusted_tools
--comms "Style1, Style2"                  # behaviors.comms  
--kpis "KPI1, KPI2, KPI3"                 # objectives.kpis
--drivers "Driver1, Driver2"              # motivations.drivers
--pain-points "Pain1, Pain2"              # motivations.pain_points
--top-objectives "Obj1, Obj2"             # objectives.top_objectives
--decision-rights "Right1, Right2"        # influence.decision_rights
--stakeholders "Stakeholder1, Stakeholder2" # influence.stakeholders
--scope "Global"                          # identity.scope
--seniority "C-level"                     # identity.seniority
--span-of-control "250"                   # identity.span_of_control
```

### JSON Override Example
```json
{
  "identity": {
    "scope": "Regional EMEA",
    "span_of_control": 180
  },
  "behaviors": {
    "trusted_tools": ["Kubernetes", "Terraform"],
    "risk_posture": "Innovation-focused"
  },
  "motivations": {
    "drivers": ["Technical excellence", "Team growth"],
    "pain_points": ["Legacy systems", "Skills gap"]
  }
}
```

### Precedence Example
```bash
# CLI flag overrides JSON which overrides library
uv run python scripts/create_role.py --name cto --type executive \
  --json-override custom.json \
  --comms "Daily standups"  # This overrides JSON comms
```

---

## D. Span of Control Guidelines

When defining `span_of_control` for role personas, use this methodology to ensure realistic organizational modeling:

### Calculation Method

1. **Start with direct reports** - Count people who appear on the leader's 1-to-1 calendar
2. **Add indirects if they matter** - For C-suite personas, almost always include them since culture, tooling, and risk posture cascade through organizational layers
3. **Round when unsure** - Use clean order-of-magnitude values (e.g., 25, 100, 500) to show scale without implying false accuracy

### Scale Categories

| Range | Leadership Type | Characteristics |
|-------|----------------|-----------------|
| **0-15** | Hands-on "player-coach" | Individual contributor + small team leadership |
| **15-80** | Mid-level org manager | Department head, functional lead |
| **80-500+** | Enterprise-grade leader | Strategic focus, governance, cross-functional influence |

### Examples by Role Type

**Executive Examples:**
- **CEO**: 500+ (entire organization through direct reports)
- **CTO**: 250 (all engineering + security + infrastructure teams)
- **CMO**: 150 (marketing + growth + customer success teams)
- **CFO**: 80 (finance + accounting + legal + operations teams)

**Specialist Examples:**
- **Security Lead**: 0 (individual contributor, cross-functional influence)
- **QA Lead**: 12 (dedicated QA team + embedded testers)
- **DevOps Lead**: 0 (individual contributor, platform responsibility)

### Usage in Role Generation

```bash
# Large enterprise CTO
uv run python scripts/create_role.py --name cto --type executive \
  --span-of-control 250

# Startup CTO (smaller org)
uv run python scripts/create_role.py --name cto --type executive \
  --span-of-control 25

# QA Lead with team
uv run python scripts/create_role.py --name qa_lead --type specialist \
  --span-of-control 8
```

---

## E. Automation Scripts

### Role Generator (`scripts/create_role.py`)
- **Three-tier override system:** CLI flags > JSON override > role_library.json
- **CLI overrides:** `--trusted-tools`, `--comms`, `--kpis`, `--drivers`, `--pain-points`, `--top-objectives`, `--decision-rights`, `--stakeholders`, `--scope`, `--seniority`, `--span-of-control`
- **JSON override:** `--json-override path/to/file.json` for power users
- **Strict validation:** `--strict` fails if required five-bucket data is missing
- **Auto-populates** templates with industry frameworks from `role_library.json`
- **Generates** proper `.mdc` files with YAML front-matter
- **Enhanced security:** Input validation prevents injection attacks and enforces 500-char limits
- **Role library validation:** Auto-validates structure and warns about missing buckets

### Validator (`scripts/lint_mdc.py`)
- Enforces 150-line limit (includes front-matter and comments)
- Validates YAML structure
- Checks for required five-bucket sections (Identity, Objectives, Influence/Standards, Behaviors, Motivations)
- Warns if `{placeholders}` remain after generation
- Integrated with role generation for immediate feedback

### Role Library (`scripts/role_library.json`)

**Executive Roles Available:**
- `cmo` - Chief Marketing Officer with growth focus
- `cto` - Chief Technology Officer with platform engineering
- `cfo` - Chief Financial Officer with SaaS metrics
- `cso` - Chief Security Officer with compliance focus
- `cpo` - Chief Product Officer with user-centric approach
- `vp_sales` - VP of Sales with revenue operations

**Specialist Roles Available:**
- `security` - Security specialist with NIST framework
- `accessibility` - Accessibility specialist with WCAG compliance
- `performance` - Performance specialist with Core Web Vitals
- `qa_lead` - QA Lead with test automation focus
- `devops` - DevOps specialist with infrastructure as code
- `data_engineer` - Data Engineer with quality focus
- `frontend_architect` - Frontend Architect with component systems
- `backend_architect` - Backend Architect with API design
- `ml_engineer` - ML Engineer with MLOps practices *(new)*
- `platform_engineer` - Platform Engineer with developer experience *(new)*

**Example Library Structure:**
```json
{
  "executive": {
    "cmo": {
      "identity": {"scope": "Global", "seniority": "C-level", "span_of_control": 150},
      "objectives": {"top_objectives": ["Drive 40% YoY growth"], "kpis": ["CAC", "LTV"]},
      "influence": {"decision_rights": ["Marketing budget"], "stakeholders": ["CEO"]},
      "behaviors": {"comms": ["Weekly reviews"], "trusted_tools": ["HubSpot"]},
      "motivations": {"drivers": ["Growth"], "pain_points": ["Attribution complexity"]},
      "frameworks": ["growth-marketing", "aarrr-metrics"]
    }
  },
  "specialist": {
    "ml_engineer": {
      "identity": {"scope": "ML platform", "seniority": "Senior specialist"},
      "objectives": {"top_objectives": ["Model accuracy >95%"], "kpis": ["Model accuracy"]},
      "standards": ["mlops", "model-governance", "data-quality"],
      "gates": ["Model Validation", "A/B Testing", "Performance Benchmarks"]
    }
  }
}
```

---

## F. Security & Validation Features

### Input Security
- **Injection prevention:** Blocks dangerous patterns (`{{`, `}}`, `<script`, `javascript:`, `data:`, `${`, `` ` ``)
- **Length limits:** 500-character maximum for all CLI inputs
- **Character sanitization:** Role names limited to alphanumeric, underscore, and hyphen
- **Real-time validation:** Immediate feedback on invalid input

### Role Library Validation
- **Structure validation:** Checks for required five-bucket compliance
- **Missing bucket warnings:** Alerts for incomplete role definitions
- **Type validation:** Ensures executive vs specialist role requirements
- **Startup validation:** Library validated on every script execution

### Template Security
- **Fixed placeholder escaping:** Proper `{placeholder}` format prevents rendering issues
- **Output sanitization:** Generated files are safe for immediate use
- **YAML validation:** Front-matter structure validated

---

## G. Maintenance & Operations

- **Auto-validation:** Pre-commit hook runs `lint_mdc.py`
- **Quarterly review:** GitHub Action opens `role-review` issue every 90 days
- **Deprecation:** Move to `archived/` with sunset date
- **Enhanced logging:** Rich console output with debug mode support
- **Template validation:** Lint check ensures no `{placeholders}` remain

---

## H. Pre-commit Integration

```yaml:.pre-commit-config.yaml
- repo: local
  hooks:
    - id: lint-mdc
      name: MDC Line Count Check
      entry: uv run python scripts/lint_mdc.py
      language: system
      files: '\.mdc$'
```

---

## I. Testing Requirements

Add to `tests/test_role_factory.py`:
- **Smoke test:** Generate role → validate structure
- **Lint test:** Ensure generated files pass `lint_mdc.py`
- **Security test:** Verify input sanitization prevents injection
- **CLI override test:** Verify all new CLI flags work correctly
- **Role library validation test:** Test library structure validation
- **Template rendering test:** Ensure placeholders render correctly
- **Span of control test:** Verify numeric validation for span of control

**Example Security Test:**
```python
def test_security_validation():
    """Test that dangerous input patterns are blocked."""
    dangerous_inputs = ["test{{injection}}", "<script>alert(1)</script>", "javascript:void(0)"]
    for dangerous_input in dangerous_inputs:
        with pytest.raises(SystemExit):
            validate_cli_input(dangerous_input, "test_field")
```