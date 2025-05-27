# Cursor Role Factory (v2.0)

Automated framework for creating standardized executive personas at scale.

---

## Quick Start

```bash
# Generate a new role
uv run python scripts/create_role.py --name cmo --type executive

# Generate with CLI overrides (highest precedence)
uv run python scripts/create_role.py --name cto --type executive \
  --trusted-tools "New Relic, PagerDuty" \
  --comms "Slack daily stand-up, Monthly arch review" \
  --kpis "MTTR, Deployment Frequency, Lead Time"

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

---

## A. Role Creation Rules

1. **Naming:** `{role}.mdc` in `.cursor/rules/roles/` (e.g., `cmo.mdc`, `qa_lead.mdc`)
2. **Size Limit:** 150 lines max (enforced by `lint_mdc.py`)
3. **Versioning:** Semantic versioning in file header
4. **Five-Bucket Standard:** Executive personas **must** populate ≥ 1 attribute in each of the five buckets (Identity, Objectives, Influence, Behaviors, Motivations). Specialists must cover Identity, Objectives and either Standards *or* Behaviors.
5. **Output:** Standardized decision template required

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
- {{FINDING_1}}
- {{FINDING_2}}

**Decision:** <GO / NO-GO / REVISE>
**Next steps:**
- {{ACTION_1}}
- {{ACTION_2}}
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
- {{TECHNICAL_FINDING}}
- {{RECOMMENDATION}}

**Status:** <APPROVED / BLOCKED / NEEDS_REVISION>
**Next steps:**
- {{ACTION}}
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

## D. Automation Scripts

### Role Generator (`scripts/create_role.py`)
- **Three-tier override system:** CLI flags > JSON override > role_library.json
- **CLI overrides:** `--trusted-tools`, `--comms`, `--kpis`, `--drivers`, `--pain-points`, `--top-objectives`, `--decision-rights`, `--stakeholders`
- **JSON override:** `--json-override path/to/file.json` for power users
- **Strict validation:** `--strict` fails if required five-bucket data is missing
- **Auto-populates** templates with industry frameworks from `role_library.json`
- **Generates** proper `.mdc` files with YAML front-matter
- **Sanitizes** input to prevent template injection

### Validator (`scripts/lint_mdc.py`)
- Enforces 150-line limit (includes front-matter and comments)
- Validates YAML structure
- Checks for required five-bucket sections (Identity, Objectives, Influence/Standards, Behaviors, Motivations)
- Warns if `{{placeholders}}` remain after generation

### Role Library (`scripts/role_library.json`)
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
    "security": {
      "identity": {"scope": "Cross-functional", "seniority": "Senior specialist"},
      "objectives": {"top_objectives": ["Zero vulnerabilities"], "kpis": ["Vulnerability count"]},
      "standards": ["nist-framework", "zero-trust", "soc2"],
      "gates": ["Threat Model", "Pen Test", "Compliance Check"]
    }
  }
}
```

---

## E. Maintenance & Security

- **Auto-validation:** Pre-commit hook runs `lint_mdc.py`
- **Quarterly review:** GitHub Action opens `role-review` issue every 90 days
- **Deprecation:** Move to `archived/` with sunset date
- **Input sanitization:** `create_role.py` only accepts values from `role_library.json`
- **Template validation:** Lint check ensures no `{{placeholders}}` remain

---

## F. Pre-commit Integration

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

## G. Testing Requirements

Add to `tests/test_role_factory.py`:
- Smoke test: Generate role → validate structure
- Lint test: Ensure generated files pass `lint_mdc.py`
- Security test: Verify input sanitization prevents injection