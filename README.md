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
- **Domain-Specific Guidance**: Rules automatically attach based on file patterns and project context
- **Scalable Structure**: Easy to add new domains or technologies as projects grow
- **Clean Separation**: Related rules grouped together for better maintainability

## Rule Categories

### 🌍 Core Rules (`core/`)
Universal development standards that apply across all projects and technologies:
- Communication style and engineering principles
- Security mandates and best practices
- Git workflow and code quality standards

### 🔧 Backend Rules (`backend/`)
Server-side development and infrastructure:
- Python development patterns and tooling
- Database design and SQL standards
- Container deployment and orchestration
- MCP server development guidelines

### ☁️ Cloud Rules (`cloud/`)
Cloud platform and infrastructure standards:
- AWS services and CloudFormation templates
- Infrastructure as code patterns
- Cloud security and compliance

### 🎨 Frontend Rules (`frontend/`)
Client-side development standards:
- TypeScript/JavaScript patterns
- Web development tooling (Vite, React, etc.)
- Frontend testing and performance

### 📝 Documentation Rules (`docs/`)
Documentation and specification standards:
- Markdown formatting and structure
- Project requirements document (PRD) templates
- Technical design specification guidelines

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
- Focus on one domain/technology per rule
- Include specific examples and patterns
- Reference related files using `@filename` (not `@folder`)
- Keep rules under 500 lines for maintainability

## Context Loading

Developers automatically receive relevant rules based on their work:

- **Any file**: Core rules for universal standards
- **Python files**: Backend rules + core rules
- **TypeScript files**: Frontend rules + core rules  
- **CloudFormation**: Cloud rules + core rules
- **Markdown files**: Documentation rules + core rules
- **Database files**: Backend database rules + core rules

## Version Control
All `.cursor/rules/` directories are version-controlled to ensure team consistency.

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