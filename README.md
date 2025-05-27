# Cursor Rules Organization

A comprehensive framework for organizing Cursor AI rules in large projects with **hybrid modular tool system** and automated role factory. This repository provides a scalable structure for domain-specific rules, role-based personas, and development tooling with enterprise-grade automation and intelligent tool synchronization.

## 🎯 Recent Achievements (v2.5)

**✅ Scripts Architecture Reorganization** - Restructured scripts folder to mirror production architecture with dedicated folders for domains, roles, tools, validation, and backup operations

**✅ Templates Organization** - Reorganized templates into architecture-aligned subfolders (domains/, roles/, tools/) with descriptive documentation files

**✅ Salesforce Architecture Integration** - Added comprehensive sf_dev domain for Salesforce backend development with Sales Cloud, Service Cloud, and Marketing Cloud standards

**✅ Domain Metadata Enhancement** - Enhanced schema with status tracking, template types, required sections, and automated governance

**✅ Metadata-Driven Architecture** - Tool registry now serves as single source of truth for domain descriptions, templates, and validation rules

**✅ Advanced Governance Tooling** - Automated validation of domain metadata schema, required sections checking, and comprehensive error reporting

**✅ Enterprise Governance Ready** - GitHub team ownership, review date tracking, and automated governance workflows foundation

**✅ Data Analyst Role Delivered** - Complete MarTech integration with GA4, privacy compliance, and business intelligence capabilities

## Structure

```
cursor_rules/
├── .cursor/
│   └── rules/
│       ├── domains/                 # 🎯 Domain-Specific Rules
│       │   ├── backend/             # 🔧 Backend & Infrastructure Rules
│       │   │   ├── containers.mdc   # Deployment & containerization standards
│       │   │   ├── database.mdc     # Database/SQL standards
│       │   │   ├── mcp.mdc          # MCP server development
│       │   │   ├── python.mdc       # Python development standards
│       │   │   └── sf_dev.mdc       # Salesforce backend development ✨ NEW
│       │   ├── cloud/               # ☁️ Cloud Platform Rules
│       │   │   └── aws.mdc          # AWS infrastructure standards
│       │   ├── core/                # 🌍 Universal Rules
│       │   │   └── core.mdc         # Core development standards & communication
│       │   ├── data/                # 📊 Data Engineering Rules
│       │   │   └── data.mdc         # Data engineering & analytics standards
│       │   ├── docs/                # 📝 Documentation Rules
│       │   │   ├── design_spec.mdc  # Technical specification standards
│       │   │   ├── markdown.mdc     # Markdown documentation standards
│       │   │   └── prd.mdc          # Project requirements standards
│       │   ├── frontend/            # 🎨 Frontend Rules
│       │   │   └── typescript.mdc   # TypeScript/web development standards
│       │   ├── martech/             # 📈 Marketing Technology Rules
│       │   │   └── marketing_analytics.mdc # GA4, GTM, privacy compliance
│       │   └── security/            # 🔒 Security Rules
│       │       └── security.mdc     # Security standards and practices
│       ├── roles/                   # 👥 Executive & Specialist Personas
│       │   ├── executive/           # 👔 C-Level Executives
│       │   │   ├── cmo.mdc          # Chief Marketing Officer
│       │   │   ├── cto.mdc          # Chief Technology Officer
│       │   │   ├── cfo.mdc          # Chief Financial Officer
│       │   │   ├── cso.mdc          # Chief Security Officer
│       │   │   ├── cpo.mdc          # Chief Product Officer
│       │   │   └── vp_sales.mdc     # VP of Sales
│       │   └── specialist/          # 🛠️ Technical Specialists
│       │       ├── data_analyst.mdc     # Data Analyst (Business Intelligence)
│       │       ├── data_engineer.mdc    # Data Engineer (Platform Expertise)
│       │       ├── salesforce_architect.mdc # Salesforce Architect ✨ NEW
│       │       ├── qa_lead.mdc          # QA Lead (Testing & Quality)
│       │       └── security.mdc         # Security Specialist
│       └── tools/                   # 🧰 Tool Registry & Metadata
│           ├── tool_registry.json   # Enhanced tool registry (100+ tools across 20 categories) ✨ ENHANCED
│           └── role_library.json    # Role templates and definitions
├── scripts/                         # 🔧 Development & Automation Tools ✨ REORGANIZED
│   ├── SCRIPTS_OVERVIEW.md         # Main scripts documentation
│   ├── domains/                     # Domain management scripts
│   │   ├── DOMAIN_SCRIPTS_GUIDE.md # Domain scripts documentation
│   │   ├── create_domain_rule.py   # Metadata-driven domain scaffolding
│   │   └── validate_domains.py     # Domain consistency & schema validation
│   ├── roles/                       # Role management scripts
│   │   ├── ROLE_SCRIPTS_GUIDE.md   # Role scripts documentation
│   │   ├── create_role.py          # Role factory with tool registry integration
│   │   ├── lint_role_library.py    # Role library validation and linting
│   │   └── migrate_roles.py        # Role library migration utilities
│   ├── tools/                       # Tool registry management
│   │   ├── TOOL_REGISTRY_GUIDE.md  # Tool registry documentation
│   │   └── lint_tool_registry.py   # Tool registry structure validation
│   ├── validation/                  # Cross-cutting validation
│   │   ├── VALIDATION_GUIDE.md     # Validation documentation
│   │   └── lint_mdc.py             # MDC file format validation
│   └── backup/                      # Backup and migration data
│       ├── BACKUP_MANAGEMENT.md    # Backup documentation
│       └── role_library.json.backup # Role library backup
├── templates/                       # 📄 Template System ✨ REORGANIZED
│   ├── domains/                     # Domain creation templates
│   │   ├── DOMAIN_CREATION_GUIDE.md # Complete domain creation guide
│   │   ├── domain_creation_template.json # Comprehensive template reference
│   │   ├── domain_rule.mdc.template # Basic domain template
│   │   ├── enhanced_domain_rule.mdc.template # Advanced domain template
│   │   └── example_domain_override.json # Working example
│   ├── roles/                       # Role creation templates
│   │   ├── executive_role.mdc.template # Executive role template
│   │   └── specialist_role.mdc.template # Specialist role template
│   └── tools/                       # Tool configuration templates (future)
│       └── README.md               # Tool templates documentation
└── tests/                          # 🧪 Test Suite
    ├── test_create_domain_rule.py  # Domain creation tests
    ├── test_create_role.py         # Role creation tests
    ├── test_lint_*.py              # Validation tests
    └── test_validate_domains.py    # Domain validation tests
```

## How It Works

- **Architecture-Aligned Organization**: Scripts and templates mirror production structure for consistency
- **Metadata-Driven Architecture**: Enhanced tool registry serves as single source of truth for domain descriptions, templates, and governance
- **Automated Governance**: Schema validation, required sections checking, and ownership tracking with GitHub team integration
- **Template System Refactored**: Data-driven template selection using metadata template_type field (12 template types available)
- **Enterprise-Ready Governance**: Status tracking, review dates, and foundation for automated governance workflows
- **Hybrid Modular Architecture**: Dual-layer system combining build-time tool composition with runtime behavioral synthesis
- **Centralized Tool Registry**: Single source of truth for tool standards across all domains and roles (100+ tools, 20 categories)
- **Agent-Based Composition**: Domain experts (@aws, @python, @database, @sf_dev) provide dynamic cross-referencing
- **Automated Synchronization**: Tool updates propagate automatically to all relevant roles
- **Domain-Specific Guidance**: Targeted rules load based on file types and project context
- **Scalable Structure**: Easy to add new domains or technologies as projects grow

### Enhanced Tool Registry System ✨ EXPANDED

The tool registry now manages **100+ tools across 20 categories** with comprehensive Salesforce integration:

**Core Technology Stacks:**
- **AWS** (12 tools) - Core infrastructure, security, compute services
- **Python** (18 tools) - Development, data manipulation, testing frameworks  
- **Database** (7 tools) - Engines, migration tools, optimization
- **Salesforce** (32 tools) - Platform tools, governance, development environments

**Specialized Domains:**
- **MarTech** (18 tools) - Analytics, advertising, SEO platforms
- **Data Engineering** (5 tools) - Pipeline and quality tools
- **Development** (9 tools) - IDEs, collaboration, integration tools
- **Testing** (2 tools) - Quality assurance frameworks

**Domain Mappings:**
- **14 domain mappings** connecting logical domains to tool categories
- **Technical domains**: aws, python, database (tool-specific)
- **Organizational domains**: backend, frontend, cloud, data, security, docs, martech
- **Role-specific domains**: data_engineer, data_analyst, sf_dev

### Salesforce Architecture Integration ✨ NEW

Comprehensive Salesforce backend development standards:

**sf_dev Domain Features:**
- **Multi-Cloud Coverage**: Sales Cloud, Service Cloud, Marketing Cloud
- **Apex Development Standards**: Code organization, governor limits, testing
- **Integration Patterns**: REST APIs, Platform Events, Change Data Capture
- **Security & Performance**: FLS, sharing rules, query optimization
- **Anti-Patterns Guide**: Common mistakes to avoid
- **Tool Integration**: 23 Salesforce-specific tools from tool registry

**Salesforce Architect Role:**
- **Principal-level guidance** for enterprise Salesforce implementations
- **Business-first approach** with technical excellence guardrails
- **5 quality gates**: Architecture Review Board, Business Value Assessment, Security Impact Assessment
- **Comprehensive toolchain**: Well-Architected Framework, Optimizer, DevOps Center

### Organizational Architecture ✨ ENHANCED

**Scripts Organization** (Architecture-Aligned):
```
scripts/
├── domains/     # Domain management (create, validate)
├── roles/       # Role management (create, lint, migrate)  
├── tools/       # Tool registry management
├── validation/  # Cross-cutting validation
└── backup/      # Backup and migration artifacts
```

**Templates Organization** (Architecture-Aligned):
```
templates/
├── domains/     # Domain creation templates and guides
├── roles/       # Role creation templates
└── tools/       # Tool configuration templates (future)
```

**Benefits:**
- **Clear Responsibilities**: Each directory has focused purpose
- **Scalable Structure**: Easy to add new scripts in appropriate locations
- **Better Discoverability**: Clear where to find specific functionality
- **Professional Documentation**: Descriptive file names replace generic READMEs

## Quick Start

### Creating a New Domain
```bash
# Create domain
uv run python scripts/domains/create_domain_rule.py \
  --name your_domain \
  --category backend \
  --description "Your domain description"

# Validate domain
uv run python scripts/domains/validate_domains.py
```

### Creating a New Role
```bash
# Create specialist role
uv run python scripts/roles/create_role.py \
  --name your_role \
  --type specialist \
  --tool-domains martech,backend

# Validate role library
uv run python scripts/roles/lint_role_library.py .cursor/rules/tools/role_library.json
```

### Using Templates
```bash
# Review domain creation guide
cat templates/domains/DOMAIN_CREATION_GUIDE.md

# Use comprehensive template
cp templates/domains/domain_creation_template.json my_domain_config.json
# Edit my_domain_config.json with your domain details
```

### Validation & Quality
```bash
# Validate all .mdc files
uv run python scripts/validation/lint_mdc.py .cursor/rules/**/*.mdc

# Validate tool registry
uv run python scripts/tools/lint_tool_registry.py .cursor/rules/tools/tool_registry.json
```

## Usage Examples

### Invoke Domain Experts
```bash
@aws              # AWS infrastructure guidance
@python           # Python development standards  
@database         # Database design and optimization
@sf_dev           # Salesforce backend development ✨ NEW
@martech          # Marketing technology standards
```

### Invoke Role-Based Agents
```bash
@cto              # Chief Technology Officer perspective
@salesforce_architect  # Salesforce architecture guidance ✨ NEW
@data_analyst     # Business intelligence and analytics
@security         # Security specialist guidance
```

## Architecture Principles

1. **Architecture Alignment**: All organizational structures mirror production layout
2. **Single Source of Truth**: Tool registry manages all tool definitions and domain mappings
3. **Metadata-Driven**: Domain templates and validation rules derived from metadata
4. **Comprehensive Coverage**: 100+ tools across 20 categories support all major technology stacks
5. **Enterprise Governance**: Built-in support for team ownership, review tracking, and compliance
6. **Scalable Design**: Easy to extend with new domains, roles, and tool categories
7. **Quality Assurance**: Automated validation at multiple levels (structure, content, consistency)
8. **Documentation-First**: Every component includes comprehensive guides and examples

## Contributing

1. **Review Documentation**: Start with `scripts/SCRIPTS_OVERVIEW.md` and `templates/domains/DOMAIN_CREATION_GUIDE.md`
2. **Follow Patterns**: Use existing domains and roles as templates
3. **Validate Changes**: Run appropriate linting scripts before committing
4. **Update Tool Registry**: Add new tools to appropriate categories in `tool_registry.json`
5. **Maintain Architecture**: Keep scripts and templates organized by purpose

## License

MIT License - see LICENSE file for details.