# Cursor Rules Organization

A comprehensive framework for organizing Cursor AI rules in large projects with **hybrid modular tool system** and automated role factory. This repository provides a scalable structure for domain-specific rules, role-based personas, and development tooling with enterprise-grade automation and intelligent tool synchronization.

## 🎯 Recent Achievements (v2.3)

**✅ Data Analyst Role Delivered** - Complete MarTech integration with GA4, privacy compliance, and business intelligence capabilities

**✅ Domain Management Enhanced** - Centralized metadata system with automated validation and consistency checking

**✅ Architecture Validated** - CTO-approved strategic enhancements avoiding overengineering while maintaining scalability

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
        ├── data/                    # 📊 Data Platform Rules
        │   └── (data engineering standards)
        ├── docs/                    # 📝 Documentation Rules
        │   ├── design_spec.mdc      # Technical specification standards
        │   ├── markdown.mdc         # Markdown documentation standards
        │   └── prd.mdc              # Project requirements standards
        ├── frontend/                # 🎨 Frontend Rules
        │   └── typescript.mdc       # TypeScript/web development standards
        ├── martech/                 # 📈 Marketing Technology Rules
        │   └── marketing_analytics.mdc # GA4, GTM, privacy compliance
        ├── security/                # 🔒 Security Rules
        │   └── (security standards)
        └── roles/                   # 👥 Executive & Specialist Personas
            ├── cmo.mdc              # Chief Marketing Officer (Executive)
            ├── cto.mdc              # Chief Technology Officer (Executive)
            ├── data_analyst.mdc     # Data Analyst (Specialist) ✨ NEW
            ├── data_engineer.mdc    # Data Engineer (Specialist)
            ├── qa_lead.mdc          # QA Lead (Specialist)
            ├── security.mdc         # Security Specialist
            └── ... (6 total roles)  # Growing specialist library
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
- **@data_analyst** → Business intelligence and analytics expertise ✨ NEW
- **@marketing_analytics** → MarTech tools and privacy compliance ✨ NEW

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

### 📊 Data Platform Rules (`data/`)
Data engineering and analytics standards:
- **Data Quality**: Validation, monitoring, and governance frameworks
- **Privacy**: GDPR, CCPA compliance and data protection standards
- **Pipeline Architecture**: ETL/ELT patterns and error handling

### 📝 Documentation Rules (`docs/`)
Documentation and specification standards:
- **Markdown**: Advanced formatting, Mermaid diagrams, structured content
- **PRD**: Project requirements with measurable objectives and risk management
- **Design Specs**: Technical specifications with implementation-ready details

### 📈 MarTech Rules (`martech/`)
Marketing technology and analytics standards:
- **Analytics**: GA4 event tracking, GTM implementation, attribution models
- **Privacy**: GDPR/CCPA compliance, consent management, data governance
- **SEO**: Technical SEO, performance optimization, accessibility standards

### 🔒 Security Rules (`security/`)
Security standards and cybersecurity best practices:
- **Framework**: NIST, zero-trust architecture, defense in depth
- **Compliance**: SOC2, security audits, vulnerability management
- **Access Control**: Principle of least privilege, IAM best practices

### 👥 Role-Based Rules (`roles/`)
Executive and specialist personas for strategic guidance:

**Executive Roles (6):**
- **CMO**: Growth marketing with AARRR metrics and jobs-to-be-done framework
- **CTO**: Enterprise data governance, 20% cloud cost reduction, 99.95% uptime with <30min MTTR
- **CFO**: SaaS metrics, financial planning, unit economics
- **CSO**: NIST framework, zero-trust security, risk management
- **CPO**: Product-led growth, design thinking, lean startup methodology
- **VP Sales**: Revenue operations, sales methodology, customer success

**Specialist Roles (6 implemented, 11 planned):**
- **Data Analyst**: Business intelligence, MarTech analytics, statistical analysis ✨ NEW
- **Data Engineer**: Data platform expertise with cross-domain synthesis
- **Security**: NIST framework, zero-trust, SOC2 compliance
- **QA Lead**: Test pyramid, shift-left testing, automation-first
- **DevOps**: CI/CD, infrastructure-as-code, observability *(planned)*
- **Frontend/Backend Architects**: Component design, API standards, scalability *(planned)*
- **ML Engineer**: MLOps, model governance, data quality *(planned)*
- **Platform Engineer**: Developer experience, self-service, golden path *(planned)*
- **Persona Creator**: User-centered design, evidence-based research, persona governance *(planned)*


## Best Practices

### Adding New Rules
1. **Universal concerns** → `core/`
2. **Backend/server concerns** → `backend/`
3. **Cloud/infrastructure** → `cloud/`
4. **Data platform concerns** → `data/`
5. **Frontend/client concerns** → `frontend/`
6. **Marketing technology** → `martech/`
7. **Security standards** → `security/`
8. **Documentation** → `docs/`
9. **Role-specific** → `roles/`

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
Working on data analytics → Core + Data + MarTech (Analytics + Privacy) ✨ NEW
Working on GA4 implementation → Core + MarTech (Analytics + Privacy) ✨ NEW
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

## Current Implementation Status

**✅ Fully Implemented Domains (8):**
- `backend/` - Python, database, containers, MCP server development
- `cloud/` - AWS infrastructure and deployment standards  
- `core/` - Universal development standards and communication
- `data/` - Data engineering and analytics platform standards
- `docs/` - Markdown, PRD, and technical specification standards
- `frontend/` - TypeScript and web development standards
- `martech/` - Marketing analytics, privacy compliance, SEO standards
- `security/` - Security frameworks and cybersecurity best practices

**🎯 Active Development:**
- **Data Analyst Role**: Fully implemented with MarTech integration
- **Domain Validation**: Automated consistency checking between filesystem and registry
- **Tool Registry**: Centralized metadata and domain mappings

## Future Expansion

The structure easily accommodates growth:

```
.cursor/rules/
├── mobile/          # Mobile app development
├── testing/         # Testing strategies and tools
├── integrations/    # Third-party service integrations
└── compliance/      # Regulatory and compliance frameworks
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

# Validate domain consistency (NEW)
uv run python scripts/validate_domains.py

# Create new domain rules with metadata integration (ENHANCED)
uv run python scripts/create_domain_rule.py --name api_design --category backend

# Validate tool registry structure (NEW)
uv run python scripts/lint_tool_registry.py scripts/tool_registry.json

# List available templates and tool domains
uv run python scripts/create_role.py --list-templates

# Generate with verbose logging for debugging
uv run python scripts/create_role.py --name analyst --type specialist --verbose
```

## Architecture & Governance

### Domain Management System ✨ NEW
- **Dual Domain Types**: Organizational domains (filesystem directories) + Technical domains (role-based tool mappings)
- **Single Source of Truth**: `tool_registry.json` contains both tool mappings and domain metadata
- **Automated Validation**: `validate_domains.py` ensures filesystem/registry consistency
- **Enhanced Creation**: `create_domain_rule.py` reads descriptions from domain metadata

### Tool Registry Architecture
- **13 Tool Categories**: From `aws_core` to `martech_seo` with 50+ tools total
- **13 Domain Mappings**: Mix organizational (`backend`, `martech`) and technical (`python`, `data_analyst`) domains
- **Comprehensive Metadata**: Owner, compliance requirements, and descriptions for all domains
- **Automated Linting**: `lint_tool_registry.py` validates structure and referential integrity

## Documentation

- **Hybrid Modular System**: Complete v2.3 architecture with enhanced domain management and validation
- **Tool Registry**: Centralized categorization with domain mappings and metadata for automatic tool resolution
- **Agent Composition**: Runtime synthesis via @aws, @python, @database, @data_analyst expert agents  
- **Five-bucket standard**: Identity, Objectives, Influence, Behaviors, Motivations for executives
- **Three-bucket standard**: Identity, Objectives, Standards/Behaviors for specialists
- **Security & validation**: Input sanitization, role library validation, domain consistency checking

## Key Features

- **🏗️ Hybrid Architecture**: Build-time tool composition + runtime behavioral synthesis
- **📋 Tool Registry**: Single source of truth with domain mappings, metadata, and category resolution
- **🤖 Agent Synthesis**: Cross-domain expertise via @aws, @python, @database, @data_analyst agents
- **🔄 Auto-Synchronization**: Tool updates propagate to all roles automatically
- **✅ Domain Validation**: Automated consistency checking between filesystem and registry ✨ NEW
- **📈 MarTech Integration**: GA4, GTM, privacy compliance, and analytics standards ✨ NEW
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