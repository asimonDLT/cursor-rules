# Cursor Rules Directory

This directory contains organized Cursor rules that automatically apply based on file types, project structure, and development context.

## Organization

```
.cursor/rules/
├── backend/                 # 🔧 Backend & Infrastructure Rules (4 files)
│   ├── containers.mdc       # Deployment & containerization standards
│   ├── database.mdc         # Database/SQL standards
│   ├── mcp.mdc              # MCP server development standards
│   └── python.mdc           # Python development standards
├── cloud/                   # ☁️ Cloud Platform Rules (1 file)
│   └── aws.mdc              # AWS infrastructure standards
├── core/                    # 🌍 Universal Rules (1 file)
│   └── core.mdc             # Core development standards & communication
├── docs/                    # 📝 Documentation Rules (3 files)
│   ├── design_spec.mdc      # Technical specification standards
│   ├── markdown.mdc         # Markdown documentation standards
│   └── prd.mdc              # Project requirements document standards
├── frontend/                # 🎨 Frontend Rules (1 file)
│   └── typescript.mdc       # TypeScript/web development standards
└── roles/                   # 👥 Role-Based Rules (future expansion)
```

## Rule Categories Explained

### 🌍 Core (`core/`)
**Always-active universal standards:**
- Communication style and engineering principles
- Security mandates and authentication patterns
- Git workflow and code quality requirements
- Meta-rules for rule generation and collaboration

### 🔧 Backend (`backend/`)
**Server-side development and deployment:**
- **Python**: SQLAlchemy, pytest, async patterns, packaging with uv
- **Database**: SQL formatting, migrations, query optimization, testing
- **Containers**: Multi-stage Dockerfiles, resource optimization, deployment
- **MCP**: Model Context Protocol server development and security

### ☁️ Cloud (`cloud/`)
**Cloud platform and infrastructure:**
- **AWS**: CloudFormation, CLI tools, SDK usage, security best practices
- **Serverless**: Lambda, ECS/Fargate deployment strategies
- **Monitoring**: CloudWatch integration, health check patterns

### 🎨 Frontend (`frontend/`)
**Client-side development:**
- **TypeScript**: pnpm, Biome, Vite, Prisma for type-safe development
- **Testing**: Vitest for unit tests, Playwright for E2E testing
- **Build**: Modern tooling and performance optimization

### 📝 Documentation (`docs/`)
**Documentation and specification standards:**
- **Markdown**: Advanced formatting, Mermaid diagrams, structured content
- **PRD**: Project requirements with measurable objectives and risk management
- **Design Specs**: Technical specifications with implementation-ready details

### 👥 Roles (`roles/`)
**Reserved for future role-specific guidance:**
- Architect-specific patterns and decision frameworks
- Security engineer guidelines and review checklists
- DevOps engineer deployment and monitoring standards

## How Auto-Attachment Works

Rules automatically attach based on glob patterns defined in each file:

- **Python files** (`*.py`, `pyproject.toml`) → Backend Python rules
- **TypeScript files** (`*.ts`, `*.tsx`, `package.json`) → Frontend TypeScript rules
- **SQL files** (`*.sql`, `alembic/**`) → Backend database rules
- **AWS files** (`*.cfn.yml`, `aws/**`) → Cloud AWS rules
- **Markdown files** (`*.md`, `docs/**`) → Documentation markdown rules
- **MCP files** (`*mcp*`, `mcp-config.json`) → Backend MCP rules

## Context Loading Strategy

Developers receive targeted guidance:

```
Working on Python backend → Core + Backend (Python + Database + Containers)
Working on React frontend → Core + Frontend (TypeScript)
Working on AWS CloudFormation → Core + Cloud (AWS)
Writing documentation → Core + Docs (Markdown + PRD/Design Spec)
Building MCP server → Core + Backend (Python + MCP + Database)
```

## Best Practices

- **Single Responsibility**: Each rule file focuses on one domain or technology
- **Composable Design**: Rules work together without conflicts
- **Specific Guidance**: Actionable patterns and examples, not vague principles
- **Context Awareness**: Rules provide relevant guidance for the current task
- **Version Controlled**: All rules are tracked for team consistency

## Maintenance

- Keep rules under 500 lines for readability
- Use kebab-case filenames with `.mdc` extensions
- Test rule interactions to avoid conflicts
- Update glob patterns when adding new file types
- Document rule changes in commit messages