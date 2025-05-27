# Cursor Rules Organization

A comprehensive framework for organizing Cursor AI rules in large projects with **hybrid modular tool system** and automated role factory. This repository provides a scalable structure for domain-specific rules, role-based personas, and development tooling with enterprise-grade automation and intelligent tool synchronization.

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
        └── roles/                   # 👥 Executive & Specialist Personas
            ├── cmo.mdc              # Chief Marketing Officer (Executive)
            ├── cto.mdc              # Chief Technology Officer (Executive)
            ├── qa_lead.mdc          # QA Lead (Specialist)
            ├── security.mdc         # Security Specialist
            └── ... (17 total roles) # Complete executive & specialist library
```

## How It Works

- **Hybrid Modular Architecture**: Dual-layer system combining build-time tool composition with runtime behavioral synthesis
- **Centralized Tool Registry**: Single source of truth for tool standards across all domains and roles
- **Agent-Based Composition**: Domain experts (@aws, @python, @database) provide dynamic cross-referencing
- **Automated Synchronization**: Tool updates propagate automatically to all relevant roles
- **Domain-Specific Guidance**: Targeted rules load based on file types and project context
- **Scalable Structure**: Easy to add new domains or technologies as projects grow

### Agent-Based Rule System

**Domain Expert Agents** (invoke via @agent_name):
- **@aws** → AWS infrastructure standards and best practices
- **@python** → Python development standards and tooling recommendations  
- **@database** → Database query optimization and schema design
- **@data_engineer** → Data platform expertise with cross-domain synthesis

**Auto-Attachment Patterns** (for specific file types):
- **Core files** (`*.md`, `.gitignore`) → Universal development standards
- **Container files** (`Dockerfile`, `docker-compose.yml`) → Containerization rules
- **MCP files** (`*mcp*`, `mcp-config.json`) → Model Context Protocol standards

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
- **Persona Creator**: User-centered design, evidence-based research, persona governance


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
- Keep rules under 150 lines for maintainability (enforced by `lint_mdc.py`)

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

- Keep rules under 150 lines for maintainability (enforced by `lint_mdc.py`)
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

## Hybrid Modular Tool System

**Revolutionary dual-layer architecture** that solves tool synchronization through build-time data composition + runtime behavioral synthesis.

### Tool Registry System
```bash
# Create role with registry-based tool resolution
uv run python scripts/create_role.py --name data_engineer --type specialist \
  --tool-domains data_engineer  # Expands to 20+ tools automatically

# Mix domains for custom roles
uv run python scripts/create_role.py --name ml_engineer --type specialist \
  --tool-domains aws,python,data_engineering

# Override with custom tools
uv run python scripts/create_role.py --name custom_role --type specialist \
  --tool-domains python --trusted-tools "Custom Tool,Special Framework"
```

### Legacy Role Generation
```bash
# Generate executive role
uv run python scripts/create_role.py --name cfo --type executive

# Generate with CLI overrides
uv run python scripts/create_role.py --name cto --type executive \
  --trusted-tools "New Relic, PagerDuty" \
  --kpis "MTTR, Deployment Frequency, Lead Time" \
  --scope "Global" --span-of-control "250"

# List available templates (17 total: 6 executive + 11 specialist)
uv run python scripts/create_role.py --list-templates
```

**📖 Complete CLI reference and examples provided below in the Hybrid Modular Tool System section**

### System Architecture

**Build-time Data Composition:**
- `tool_registry.json` → Centralized tool categorization and domain mappings
- `--tool-domains` flag → Automatic tool resolution from registry
- Domain abstractions → Mix and match tool categories (aws + python + database)

**Runtime Behavioral Composition:**
- Domain expert agents (@aws, @python, @database) provide dynamic cross-referencing  
- Generated roles include synthesis instructions for current guidance
- No conflicts - roles invoke experts explicitly when needed

**Synthesis & Domain Integration:**
All generated roles include a synthesis section that instructs them to invoke domain experts:
- For AWS/cloud guidance: Invoke @aws for infrastructure standards and best practices
- For Python development: Invoke @python for coding standards and tooling recommendations  
- For database work: Invoke @database for query optimization and schema design

This ensures roles always access the most current domain expertise without hardcoding outdated guidance.

### Development Setup
```bash
# Install dependencies with uv
uv sync

# Install pre-commit hooks  
pre-commit install

# Generate a new role with tool registry integration
uv run python scripts/create_role.py --name data_scientist --type specialist \
  --tool-domains python,data_engineering \
  --kpis "Model accuracy, Data quality" \
  --scope "Data platform" --seniority "Senior specialist"

# Validate all roles with detailed output
uv run python scripts/lint_mdc.py .cursor/rules/roles/*.mdc

# Validate with custom line limit
MDC_LINE_LIMIT=200 uv run python scripts/lint_mdc.py .cursor/rules/roles/*.mdc

# List available templates and tool domains
uv run python scripts/create_role.py --list-templates

# Generate with verbose logging for debugging
uv run python scripts/create_role.py --name analyst --type specialist --verbose
```

## Documentation

- **Hybrid Modular System**: Complete v2.2 architecture with tool registry, domain composition, and agent synthesis (documented in this README)
- **Tool Registry**: Centralized categorization with domain mappings for automatic tool resolution
- **Agent Composition**: Runtime synthesis via @aws, @python, @database expert agents  
- **Five-bucket standard**: Identity, Objectives, Influence, Behaviors, Motivations for executives
- **Three-bucket standard**: Identity, Objectives, Standards/Behaviors for specialists
- **Security & validation**: Input sanitization, role library validation, template security

## Key Features

- **🏗️ Hybrid Architecture**: Build-time tool composition + runtime behavioral synthesis
- **📋 Tool Registry**: Single source of truth with domain mappings and category resolution
- **🤖 Agent Synthesis**: Cross-domain expertise via @aws, @python, @database agents
- **🔄 Auto-Synchronization**: Tool updates propagate to all roles automatically
- **🛡️ Enterprise Security**: Input validation, sanitization, automated testing
- **📊 Rich CLI**: Color-coded output, verbose logging, progress indicators

## Dependencies

- **Python**: >=3.12 with uv package manager
- **Runtime**: Rich library for enhanced terminal output and colorful validation
- **Development**: pre-commit hooks, ruff linting, pytest with coverage and async support
- **Security**: Input validation, template sanitization, role library validation
- **Architecture**: Dual-layer composition system with centralized tool registry

## References
- [Cursor Rules Documentation](https://docs.cursor.com/customization/rules-for-ai)
- [Community Best Practices](https://community.cursor.com)