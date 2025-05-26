# Cursor Rules Organization

This repository follows Cursor best practices for rule organization in large projects.

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
        └── roles/                   # 👥 Role-Based Rules (future expansion)
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
Future expansion for role-specific guidance (architect, security engineer, etc.)

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

## References
- [Cursor Rules Documentation](https://docs.cursor.com/customization/rules-for-ai)
- [Community Best Practices](https://community.cursor.com)