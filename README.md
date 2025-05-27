# Cursor Rules Organization

A comprehensive framework for organizing Cursor AI rules in large projects with automated role factory and quality assurance tools. This repository provides a scalable structure for domain-specific rules, role-based personas, and development tooling with enterprise-grade automation.

## Structure

```
cursor_rules/
└── .cursor/
    ├── README.md
    └── rules/
        ├── backend/                 # 🔧 Backend & Infrastructure Rules
        │   ├── containers.mdc       # Deployment & containerization standards
        │   ├── database.mdc         # Database/SQL standards
        │   ├── mcp.mdc              # MCP server development
        │   └── python.mdc           # Python development standards
        ├── cloud/                   # ☁️ Cloud Platform Rules
        │   └── aws.mdc              # AWS infrastructure standards
        ├── core/                    # 🌍 Universal Rules
        │   └── core.mdc             # Core development standards & communication
        ├── docs/                    # 📝 Documentation Rules
        │   ├── design_spec.mdc      # Technical specification standards
        │   ├── markdown.mdc         # Markdown documentation standards
        │   └── prd.mdc              # Project requirements standards
        ├── frontend/                # 🎨 Frontend Rules
        │   └── typescript.mdc       # TypeScript/web development standards
        └── roles/                   # 👥 Role-Based Rules
            ├── cmo.mdc              # Chief Marketing Officer perspective  
            ├── cto.mdc              # Chief Technology Officer perspective
            ├── qa_lead.mdc          # QA Lead specialist perspective
            ├── security.mdc         # Security specialist perspective
            └── ... (11 total roles) # Complete executive & specialist library
```

## How It Works

- **Centralized Organization**: All rules organized under `.cursor/rules/` with logical domain folders
- **Auto-Attachment**: Rules automatically attach based on glob patterns defined in each file
- **Domain-Specific Guidance**: Targeted rules load based on file types and project context
- **Scalable Structure**: Easy to add new domains or technologies as projects grow
- **Clean Separation**: Related rules grouped together for better maintainability

### Auto-Attachment Patterns

Rules automatically attach based on file types:

- **Python files** (`*.py`, `pyproject.toml`) → Backend Python rules
- **TypeScript files** (`*.ts`, `*.tsx`, `package.json`) → Frontend TypeScript rules  
- **SQL files** (`*.sql`, `alembic/**`) → Backend database rules
- **AWS files** (`*.cfn.yml`, `aws/**`) → Cloud AWS rules
- **Markdown files** (`*.md`, `docs/**`) → Documentation markdown rules
- **MCP files** (`*mcp*`, `mcp-config.json`) → Backend MCP rules

## Rule Categories

### 🌍 Core Rules (`core/`)
Universal development standards that apply across all projects and technologies:
- Communication style and engineering principles
- Security mandates and best practices
- Git workflow and code quality standards

### 🔧 Backend Rules (`backend/`)
Server-side development and infrastructure:
- **Python**: SQLAlchemy, pytest, async patterns, packaging with uv
- **Database**: SQL formatting, migrations, query optimization, testing
- **Containers**: Multi-stage Dockerfiles, resource optimization, deployment
- **MCP**: Model Context Protocol server development and security

### ☁️ Cloud Rules (`cloud/`)
Cloud platform and infrastructure standards:
- **AWS**: CloudFormation, CLI tools, SDK usage, security best practices
- **Serverless**: Lambda, ECS/Fargate deployment strategies
- **Monitoring**: CloudWatch integration, health check patterns

### 🎨 Frontend Rules (`frontend/`)
Client-side development standards:
- **TypeScript**: pnpm, Biome, Vite, Prisma for type-safe development
- **Testing**: Vitest for unit tests, Playwright for E2E testing
- **Build**: Modern tooling and performance optimization

### 📝 Documentation Rules (`docs/`)
Documentation and specification standards:
- **Markdown**: Advanced formatting, Mermaid diagrams, structured content
- **PRD**: Project requirements with measurable objectives and risk management
- **Design Specs**: Technical specifications with implementation-ready details

### 👥 Role-Based Rules (`roles/`)
Executive and specialist personas for strategic guidance:

**Executive Roles (6):**
- **CMO**: Growth marketing with AARRR metrics and jobs-to-be-done framework
- **CTO**: Enterprise data governance, 20% cloud cost reduction, 99.95% uptime with <30min MTTR
- **CFO**: SaaS metrics, financial planning, unit economics
- **CSO**: NIST framework, zero-trust security, risk management
- **CPO**: Product-led growth, design thinking, lean startup methodology
- **VP Sales**: Revenue operations, sales methodology, customer success

**Specialist Roles (11):**
- **Security**: NIST framework, zero-trust, SOC2 compliance
- **QA Lead**: Test pyramid, shift-left testing, automation-first
- **DevOps**: CI/CD, infrastructure-as-code, observability
- **Frontend/Backend Architects**: Component design, API standards, scalability
- **ML Engineer**: MLOps, model governance, data quality (new)
- **Platform Engineer**: Developer experience, self-service, golden path (new)
- **Persona Creator**: User-centered design, evidence-based research (new)

## Best Practices

### Adding New Rules
1. **Universal concerns** → `core/`
2. **Backend/server concerns** → `backend/`
3. **Cloud/infrastructure** → `cloud/`
4. **Frontend/client concerns** → `frontend/`
5. **Documentation** → `docs/`
6. **Role-specific** → `roles/`

### File Naming
- Use kebab-case: `my-rule.mdc`
- Single responsibility per file
- Descriptive names that indicate scope and purpose

### Rule Content
- **Single Responsibility**: Each rule file focuses on one domain or technology
- **Composable Design**: Rules work together without conflicts
- **Specific Guidance**: Actionable patterns and examples, not vague principles
- **Context Awareness**: Rules provide relevant guidance for the current task
- Keep rules under 500 lines for maintainability

## Context Loading

Developers automatically receive relevant rules based on their work:

```
Working on Python backend → Core + Backend (Python + Database + Containers)
Working on React frontend → Core + Frontend (TypeScript)
Working on AWS CloudFormation → Core + Cloud (AWS)
Writing documentation → Core + Docs (Markdown + PRD/Design Spec)
Building MCP server → Core + Backend (Python + MCP + Database)
```

## Maintenance

- Keep rules under 500 lines for readability
- Use kebab-case filenames with `.mdc` extensions
- Test rule interactions to avoid conflicts
- Update glob patterns when adding new file types
- Document rule changes in commit messages
- All `.cursor/rules/` directories are version-controlled to ensure team consistency

## Future Expansion

The structure easily accommodates growth:

```
.cursor/rules/
├── mobile/          # Mobile app development
├── data/            # Data science and analytics
├── security/        # Security-specific guidelines
├── testing/         # Testing strategies and tools
└── integrations/    # Third-party service integrations
```

## Automated Role Factory (v2.1)

Enterprise-grade role automation system for generating standardized executive and specialist personas with enhanced security and validation.

### Quick Start
```bash
# Get help
uv run python scripts/create_role.py --help

# Generate executive role
uv run python scripts/create_role.py --name cfo --type executive

# Generate with CLI overrides (highest precedence)
uv run python scripts/create_role.py --name cto --type executive \
  --trusted-tools "AWS CloudWatch, GitHub" \
  --kpis "MTTR, Data Quality Score" \
  --scope "Global" --span-of-control "250"

# Generate with JSON override file (middle precedence)  
uv run python scripts/create_role.py --name cmo --type executive \
  --json-override custom_overrides.json

# List all available templates
uv run python scripts/create_role.py --list-templates

# Validate existing roles
uv run python scripts/lint_mdc.py .cursor/rules/roles/*.mdc
```

### Key Features
- **Three-tier precedence**: CLI flags > JSON override > role library defaults
- **Enhanced CLI**: 11 override flags including scope, seniority, span-of-control
- **Security hardened**: Input validation, injection prevention, 500-char limits
- **17 role templates**: 6 executive + 11 specialist roles with industry frameworks
- **Auto-validation**: Real-time linting with five-bucket compliance checking
- **Span of control guidelines**: Realistic organizational modeling (0-500+ range)

### Available Role Templates

**Executive Roles (6):**
- `cmo` - Growth marketing with AARRR metrics
- `cto` - Data governance, cloud optimization, platform engineering
- `cfo` - SaaS metrics, financial planning, unit economics
- `cso` - NIST framework, zero-trust security
- `cpo` - Product-led growth, design thinking
- `vp_sales` - Revenue operations, sales methodology

**Specialist Roles (11):**
- `security` - NIST framework, zero-trust, SOC2
- `qa_lead` - Test pyramid, shift-left testing
- `devops` - CI/CD, infrastructure-as-code
- `accessibility` - WCAG 2.1, Section 508
- `performance` - Core Web Vitals, performance budgets
- `data_engineer` - Data quality, governance, privacy
- `frontend_architect` - Component design, performance-first
- `backend_architect` - API design, scalability
- `ml_engineer` - MLOps, model governance (new)
- `platform_engineer` - Developer experience, golden path (new)
- `persona_creator` - User research, evidence-based design (new)

### Enhanced Security & Validation
- **Input sanitization**: Blocks injection patterns, enforces character limits
- **Role library validation**: Startup checks for five-bucket compliance
- **Template security**: Fixed placeholder format prevents rendering issues
- **Real-time feedback**: Immediate validation with detailed error messages

### Development Setup
```bash
# Install dependencies with uv
uv sync

# Install pre-commit hooks  
pre-commit install

# Generate a new role with full customization
uv run python scripts/create_role.py --name data_scientist --type specialist \
  --trusted-tools "Python, Jupyter, MLflow" \
  --kpis "Model accuracy, Data quality" \
  --scope "Data platform" --seniority "Senior specialist"

# Validate all roles with detailed output
uv run python scripts/lint_mdc.py .cursor/rules/roles/*.mdc

# List available templates by category
uv run python scripts/create_role.py --list-templates

# Generate with verbose logging for debugging
uv run python scripts/create_role.py --name analyst --type specialist --verbose
```

## Documentation

- **[Role Creation Guide](docs/role_creation_guide.md)**: Complete v2.1 automation framework with CLI reference, span of control guidelines, security features, and maintenance procedures
- **Five-bucket standard**: Identity, Objectives, Influence, Behaviors, Motivations for executives
- **Three-bucket standard**: Identity, Objectives, Standards/Behaviors for specialists
- **Security & validation**: Input sanitization, role library validation, template security

## Dependencies

- **Python**: >=3.12 with uv package manager
- **Runtime**: Rich library for enhanced terminal output and colorful validation
- **Development**: pre-commit hooks, ruff linting, pytest with coverage and async support
- **Security**: Input validation, template sanitization, role library validation

## References
- [Cursor Rules Documentation](https://docs.cursor.com/customization/rules-for-ai)
- [Community Best Practices](https://community.cursor.com)