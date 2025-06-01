# Library Explorer - Refined Execution Plan

## Project Overview
A standalone CLI tool that makes Role Library and Tool Registry human-readable and easily explorable. Built as a modern Python package with Typer CLI framework, Pydantic data models, and Rich console output.

---

## Sprint 0: Project Bootstrap (2 business days)

### Deliverables

#### Repo Foundation
**Tasks:**
- Create `library_explorer/` package with `pyproject.toml`
- Add entry point: `library-explorer = library_explorer.cli:app`
- Pin dependencies: `typer[all]>=0.9.0`, `rich>=13.0`, `pydantic>=2.0`, `rapidfuzz>=3.0`, `pyyaml>=6.0`

**Acceptance Criteria:**
- `pip install -e .` succeeds
- `library-explorer --help` shows typer-generated help

#### Data Models
**Tasks:**
- `data/models.py`: Pydantic models for Role, Tool, Domain
- `data/loader.py`: Repository pattern with YAML/JSON support
- `data/validator.py`: Schema validation + business rules

**Acceptance Criteria:**
- Loads sample YAML without errors
- Type hints pass `mypy --strict`

#### Dev Infrastructure
**Tasks:**
- Pre-commit: black, ruff, mypy, `library-explorer validate`
- GitHub Actions: mirrors pre-commit + runs tests
- Basic error handling strategy documented

**Acceptance Criteria:**
- Pre-commit hooks install and pass
- CI badge shows green

### Sample Data Schema Required

```yaml
# roles/cmo.yaml
role_id: cmo
name: Chief Marketing Officer
seniority: c-level
scope: global
span_of_control: 150
domains: [martech, analytics, content]
primary_tools: [hubspot, mixpanel, figma]
frameworks: [growth-hacking, brand-strategy]
description: "Strategic marketing leadership..."

# tools/hubspot.yaml
tool_id: hubspot
name: HubSpot
category: martech
domains: [sales, marketing]
description: "Inbound marketing platform..."
```

---

## Sprint 1: Browse & Validate MVP (5 business days)

### Core Deliverables

#### Browse Command
**Tasks:**
- Browse roles/tools/domains with Rich tables
- Interactive prompts for role type selection
- `--no-emoji`, `--format {table|list}` flags

**Acceptance Criteria:**
- `library-explorer browse roles` shows formatted table
- Interactive prompts work smoothly
- Format options change output style

#### Validation Engine
**Tasks:**
- Auto-validation on data load
- Checks: schema compliance, orphaned tools, missing references
- Rich console error reporting with suggestions

**Acceptance Criteria:**
- Catches common data issues
- Clear error messages with fix suggestions
- Validation runs in <100ms

#### Core CLI UX
**Tasks:**
- Typer-powered help system
- Consistent error handling and user feedback
- Progress indicators for longer operations

**Acceptance Criteria:**
- `--help` is comprehensive
- Errors don't crash, show helpful messages
- Keyboard interrupt handled gracefully

### Testing & Documentation

#### Unit Tests
**Requirements:**
- Pytest with snapshot testing for Rich output
- Mocked data layer for consistent tests
- Test data with edge cases

**Acceptance Criteria:**
- Coverage >85% (not 90% - more realistic)
- Tests run in <10s
- Snapshot tests catch UI regressions

#### Documentation
**Requirements:**
- README.md with install, basic usage, examples
- Sample library files in `examples/`
- API documentation for models

**Acceptance Criteria:**
- Colleague can install and use without questions
- Examples work out of the box

### Sprint 1 Success Criteria
- ✅ `library-explorer browse roles` shows formatted table
- ✅ `library-explorer validate` catches and reports data issues
- ✅ Test suite passes with >85% coverage
- ✅ Fresh developer can install and use successfully
- ✅ Performance: browse command loads in <200ms

---

## Sprint 2: Search, Filter & Export (7 business days)
*Only proceed after Sprint 1 sign-off*

### Search & Discovery

#### Smart Search
**Implementation:**
- `search roles/tools --query "text"`
- Fuzzy matching via rapidfuzz
- Relevance scoring and ranking

**Acceptance Criteria:**
- Finds roles by partial tool names
- Typos handled gracefully
- Results ranked by relevance

#### Advanced Filtering
**Implementation:**
- `filter roles --seniority c-level --tools hubspot`
- Numeric comparisons: `--span-min 100`
- Interactive filter builder

**Acceptance Criteria:**
- Multiple criteria work together
- Interactive mode guides users
- Filter combinations make logical sense

### Export & Integration

#### Multi-format Output
**Implementation:**
- `--output {rich|markdown|json}`
- `--save filename` option
- Templatable markdown exports

**Acceptance Criteria:**
- Markdown suitable for docs
- JSON parseable by other tools
- Rich output remains default

#### Documentation Export
**Implementation:**
- Role-tool relationship diagrams
- Summary statistics and insights
- Integration with existing docs

**Acceptance Criteria:**
- Exports integrate with current workflow
- Generated docs are maintainable

---

## Technical Requirements & Standards

### Performance Targets
- **Cold start**: <200ms for browse commands
- **Memory usage**: <50MB for typical library sizes
- **File loading**: Support 100+ roles, 200+ tools without degradation

### Error Handling Strategy
- **Graceful degradation**: Partial data loads if some files malformed
- **Clear messaging**: Rich-formatted errors with suggested fixes
- **Recovery options**: Continue processing after non-critical errors

### Code Quality Gates
- **Type coverage**: 100% (strict mypy)
- **Test coverage**: >85% (pytest-cov)
- **Linting**: Black + Ruff with zero violations
- **Documentation**: All public APIs documented

---

## Risk Mitigation

### Timeline Risks
- **Sprint 0 buffer**: If bootstrap takes 3 days, Sprint 1 starts Day 4
- **Scope flexibility**: Core browse + validate is minimum viable; export can move to Sprint 3
- **Testing realism**: Focus on critical paths if 85% coverage proves challenging

### Technical Risks
- **YAML complexity**: Start with simple schemas, iterate based on real data
- **Rich output**: Keep table logic simple; fancy formatting can be enhanced later
- **Performance**: Profile early if loading times exceed targets

### Integration Risks
- **Data format changes**: Abstract loader interface to handle schema evolution
- **CLI compatibility**: Follow typer patterns for future extensibility
- **Export format stability**: Version output schemas for downstream consumers

---

## Immediate Next Steps

### For You (Day 0)
- [ ] **Confirm timeline**: Are these business days or calendar days?
- [ ] **Provide sample data**: 2-3 example role + tool YAML files matching the schema above
- [ ] **Specify standards**: Any corporate lint rules, CI requirements, or security policies?
- [ ] **Define sign-off**: Who reviews Sprint 1 deliverables? What constitutes approval?

### For Implementation (Day 1)
- [ ] Bootstrap repo with skeleton structure
- [ ] Set up development environment with pre-commit hooks
- [ ] Create initial CLI showing `library-explorer --help`
- [ ] Validate sample data loading with your provided YAML files

---

## Success Metrics

- **Sprint 1**: Colleague can explore your role library without training
- **Sprint 2**: Tool supports your documentation workflow end-to-end
- **Overall**: Reduces time to find role/tool information by 80%

---

## Project Status

| Sprint | Status | Start Date | End Date | Deliverables |
|--------|--------|------------|----------|--------------|
| Sprint 0 | ✅ Complete | Completed | Completed | Bootstrap & Foundation |
| Sprint 1 | 🟢 Ready | TBD | TBD | Browse & Validate MVP |
| Sprint 2 | ⚪ Not Started | TBD | TBD | Search, Filter & Export |

**Current Phase**: Sprint 0 Complete - Ready for Sprint 1
**Sprint 0 Achievements**:
- ✅ Package structure with entry point working
- ✅ CLI browse tools command with Rich table output
- ✅ Data validation integration
- ✅ Default path configured to authoritative source (.cursor/rules/tools/)
- ✅ No --data-path specification required for normal usage

**Next Milestone**: Sprint 1 development (browse roles, interactive prompts, enhanced validation)
