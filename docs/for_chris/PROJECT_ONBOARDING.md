# FOR_CHRIS: dbt-playground Onboarding Guide

Welcome to dbt-playground! This document is your one-stop orientation for understanding the project, getting set up, and knowing where everything lives.

---

## What Is This Project?

This is a **dbt (data build tool) learning project** designed to:

1. Learn dbt and data transformation best practices
2. Practice agent orchestration for data analytics development
3. Explore dbt-mcp integration for AI-assisted data modeling

The data domain is **synthetic healthcare data** from Synthea - realistic patient records without any privacy concerns.

---

## Project Setup Overview

### Technology Stack

| Component | Choice | Why |
|-----------|--------|-----|
| **Database** | DuckDB | Zero infrastructure, analytics-optimized, native CSV support |
| **Data Source** | Synthea | Free synthetic healthcare data, realistic structure |
| **Python** | uv | Fast, modern Python package manager |
| **Node.js** | npm | For markdown/YAML linting tools |
| **AI Integration** | dbt-mcp | AI-assisted dbt development via MCP servers |

### Directory Structure (Key Paths)

```
dbt-playground/
|-- CLAUDE.md                 # Project context (Claude reads this first)
|-- docs/                     # Documentation
|   |-- reference/           # Architecture, structure, learnings
|   |-- plans/               # Roadmaps, initialization plans
|   |-- standards/           # Rules and conventions
|   |-- specs/               # PRDs (when created)
|   `-- tdd/                 # Technical design docs
|
|-- dbt_project/              # The actual dbt project
|   |-- models/              # SQL models (staging/intermediate/marts)
|   |-- seeds/               # Reference data (small CSVs)
|   |-- data/                # Raw Synthea data (gitignored)
|   |-- tests/               # Custom singular tests
|   |-- macros/              # Reusable SQL/Jinja macros
|   |-- dbt_project.yml      # Project configuration
|   `-- packages.yml         # dbt package dependencies
|
|-- .claude/                  # Agent Configuration
|   |-- agents/              # 16 personas (PM, Arch, Dev, etc.)
|   |-- commands/            # 13 slash commands (/commit, /dbt-model, etc.)
|   |-- skills/              # 21 reusable workflows
|   `-- rules/               # Coding standards
|
`-- temp/                     # Working files (development scratch space)
```

### Database Connection

The dbt profile lives at `~/.dbt/profiles.yml`:

```yaml
healthcare_analytics:
  outputs:
    dev:
      type: duckdb
      path: dev.duckdb
      threads: 4
    prod:
      type: duckdb
      path: prod.duckdb
      threads: 4
  target: dev
```

DuckDB files are created automatically on first `dbt run` - no database setup required!

### Pre-Commit Hooks

The project uses Husky + lint-staged for automatic code quality:

| Linter | Files | Auto-fix? |
|--------|-------|-----------|
| markdownlint-cli2 | `*.md` | Yes |
| yamllint | `*.yml`, `*.yaml` | No (via script) |
| sqlfluff | `*.sql` | Yes (via script) |

Run manually:

```bash
npm run lint        # Run all linters
npm run lint:md:fix # Auto-fix markdown
npm run lint:sql:fix # Auto-fix SQL
```

### MCP Server Configuration

The project includes dbt-mcp for AI-assisted development (`.mcp.json`):

```json
{
  "mcpServers": {
    "dbt": {
      "command": "uvx",
      "args": ["dbt-mcp"],
      "env": {
        "DBT_PROJECT_DIR": "./dbt_project",
        "DBT_PATH": "./.venv/bin/dbt",
        "DBT_PROFILES_DIR": "~/.dbt"
      }
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest", "--caps=vision"]
    }
  }
}
```

This enables Claude Code to interact with dbt directly via MCP tools.

---

## Data Architecture

### Synthea Healthcare Data

Synthea generates realistic synthetic healthcare records. Key entities:

| Table | Type | Description |
|-------|------|-------------|
| `patients` | Dimension | Patient demographics |
| `encounters` | Fact | Healthcare visits |
| `conditions` | Fact | Diagnoses |
| `medications` | Fact | Prescriptions |
| `procedures` | Fact | Medical procedures |
| `observations` | Fact | Vital signs, lab results |
| `providers` | Dimension | Healthcare providers |
| `organizations` | Dimension | Healthcare facilities |
| `payers` | Dimension | Insurance payers |

### Model Layer Architecture

The project follows the dbt best practice of layered modeling:

```
Raw Data (CSV)
     |
     v
+-------------+
|   Staging   |   stg_synthea__patients.sql
|   (views)   |   - 1:1 with source, renamed/retyped
+-------------+   - No joins, no business logic
     |
     v
+-------------+
| Intermediate|   int_encounters__enriched.sql
|   (views)   |   - Business logic, joins
+-------------+   - Reusable building blocks
     |
     v
+-------------+
|    Marts    |   dim_patients.sql, fct_encounters.sql
|  (tables)   |   - Analytics-ready
+-------------+   - Optimized for queries
```

### Naming Conventions

| Prefix | Layer | Example |
|--------|-------|---------|
| `stg_` | Staging | `stg_synthea__patients` |
| `int_` | Intermediate | `int_encounters__enriched` |
| `dim_` | Dimension | `dim_patients` |
| `fct_` | Fact | `fct_encounters` |

Column naming:

- Primary keys: `{entity}_id` (e.g., `patient_id`)
- Dates: `{event}_date` (e.g., `birth_date`)
- Booleans: `is_{condition}` (e.g., `is_deceased`)

---

## Development Workflow

### Agent Orchestration System

Claude operates as a multi-persona agent system. Each persona specializes in different development phases:

| Persona | Prefix | Primary Focus |
|---------|--------|---------------|
| Product Manager | `pm:` | Requirements, PRDs |
| Technical Architect | `arch:` | System design, TDDs |
| Quality Tester | `test:` | Test specifications |
| Feature Developer | `dev:` | Implementation |
| Code Reviewer | `review:` | Code quality |
| Documenter | `docs:` | Documentation, changelog |
| Git-Master | `git:` | Git operations, safety |
| Sage | `sage:` | Learning extraction |

**dbt-specific agents:**

| Persona | Prefix | Focus |
|---------|--------|-------|
| Data Modeler | `dbt-model:` | Dimensional model design |
| dbt Developer | `dbt-dev:` | SQL/Jinja implementation |
| dbt Tester | `dbt-test:` | Data quality tests |
| dbt Documenter | `dbt-docs:` | Model documentation |
| Semantic Analyst | `semantic:` | Metrics, KPIs |

### Assembly Line Workflow

For feature development, personas chain together:

```
1. PM         -> Draft PRD
2. Architect  -> Create TDD
3. Developer  -> Implement (on feature branch)
4. Reviewers  -> Code + Design review
5. Deploy     -> Merge PR, create version tag
6. Documenter -> Update CHANGELOG
7. Sage       -> Extract learnings
```

For dbt models:

```
Data Modeler -> dbt Developer -> dbt Tester -> Code Reviewer -> dbt Documenter
```

### Standard Workflow Phases

Every task (unless exempted) follows:

```
UNDERSTAND  -> Read relevant docs, understand context
PLAN        -> Create temp/v[X.Y]_PLAN.md, get approval
BUILD       -> Implement in temp/ first when prototyping
VERIFY      -> Test, create temp/v[X.Y]_TESTING.md
DEPLOY      -> Finalize, create git tag
```

### Git Workflow

**Branch naming:**

- `feat/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation
- `refactor/` - Code restructuring

**Commit format:** Conventional Commits

```
feat(models): add staging model for patients
fix(tests): correct assertion in encounter test
docs: update FOR_CHRIS with workflow section
```

**Critical rule:** All git write operations go through Git-Master (`git:` prefix or `/commit`, `/branch` commands). Direct git commits are blocked by pre-bash hooks for safety.

---

## Roadmap Ahead

### Current Status: Foundation Complete (v0.1)

What's done:

- Agent orchestration scaffold (16 personas)
- Documentation framework
- dbt project structure initialized
- Pre-commit hooks configured
- dbt-mcp integration configured
- DuckDB connection ready

### Next Milestone: v0.2 - Staging Layer

Build the foundational staging models:

- [ ] Generate/download Synthea data (500 patients)
- [ ] Create source definitions (`_synthea__sources.yml`)
- [ ] Implement 9 staging models (`stg_synthea__*.sql`)
- [ ] Add basic tests (unique, not_null on PKs)

### Future Milestones

| Version | Focus | Key Deliverables |
|---------|-------|------------------|
| v0.3 | **Marts Layer** | `dim_patients`, `dim_providers`, `fct_encounters`, `fct_clinical_events` |
| v0.4 | **Visualization** | Lightdash deployment, executive dashboard |
| v0.5 | **Engagement** | Drill-downs, scheduled reports, alerts |
| v1.0 | **Production** | SSO, row-level security, performance tuning |

### Visualization Recommendation: Lightdash

We've evaluated BI tools and recommend **Lightdash** for visualization:

| Tool | Fit | Notes |
|------|-----|-------|
| **Lightdash** | Best | Native dbt integration, MIT licensed |
| Apache Superset | Good | More powerful, steeper learning curve |
| Metabase | Good | Most user-friendly, AGPL license |
| Evidence.dev | Good | For markdown-based narratives |

Lightdash reads dbt models directly and syncs metrics - single source of truth.

---

## Key Considerations and Learnings

### Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Database | DuckDB over Postgres | Zero infrastructure, perfect for learning |
| BI Tool | Lightdash over alternatives | Native dbt integration |
| Data Source | Synthea | Realistic, free, no privacy concerns |
| Git Flow | GitHub Flow | Simple, PR-based, no release branches |

### Proven Patterns (from LEARNINGS.md)

**Agent Orchestration:**

- Use assembly line for complex features
- Use manual approach for < 3 file changes
- Always be explicit about file deliverables when delegating to agents
- Provide context links (PRDs, previous work) in agent prompts

**dbt Modeling:**

- Staging = 1:1 with source, no joins, no business logic
- Intermediate = joins, business logic, reusable building blocks
- Marts = analytics-ready, denormalized where appropriate
- Use CTEs for readability: `source` -> `renamed` -> `filtered` -> `final`

**File Operations:**

- Always prototype in `temp/` first
- Never overwrite files without backup
- Ask before cleaning temp folder

### Anti-Patterns to Avoid

**SQL/dbt:**

```sql
-- DON'T: SELECT * in final output
select * from staging

-- DO: Explicit columns
select patient_id, first_name, last_name from staging

-- DON'T: Join in staging layer
from patients p join encounters e on p.id = e.patient_id

-- DO: Keep staging simple, join in intermediate/marts
```

**Agent Usage:**

```
-- DON'T: Use agents for trivial tasks
"Agent, fix this typo in the README"

-- DO: Manual for simple, agent for complex
Just fix the typo directly
```

### Workflow Exceptions

Some tasks don't need full workflow. Approved shortcuts:

| Task Type | Skip Phases | Reason |
|-----------|-------------|--------|
| Typo fix | PLAN, PROTOTYPE | Obvious, low risk |
| Documentation update | PROTOTYPE | No functionality |
| Adding code comments | PLAN, PROTOTYPE | No behavior change |

See `docs/standards/WORKFLOW_EXCEPTIONS.md` for the full list.

---

## Quick Reference Commands

### dbt Commands

```bash
cd dbt_project

dbt debug       # Check connection
dbt deps        # Install packages
dbt compile     # Compile models (no execution)
dbt run         # Run all models
dbt run --select staging  # Run only staging
dbt test        # Run tests
dbt docs generate && dbt docs serve  # Documentation
```

### Slash Commands (Claude Code)

```
/commit "feat(models): add patient staging model"
/branch feat/patient-staging
/dbt-model design a patient dimension
/dbt-test add tests to stg_synthea__patients
/dbt-run staging
/dbt-docs generate
```

### Persona Invocation

```
pm: I want to add an encounter analytics feature
arch: design the encounter fact table
dbt-model: create the staging layer for encounters
dbt-dev: implement the stg_synthea__encounters model
review: check the staging model for best practices
docs: update changelog for v0.2
```

---

## Getting Started Checklist

When you return to this project after time away:

- [ ] Read `CLAUDE.md` for current project state
- [ ] Check `CHANGELOG.md` for recent changes
- [ ] Review `docs/plans/VISUALIZATION-ROADMAP.md` for roadmap
- [ ] Check GitHub Issues for active work
- [ ] Run `dbt debug` to verify connection
- [ ] Run `npm run lint` to check code quality

---

## Related Documentation

| Document | Purpose | When to Read |
|----------|---------|--------------|
| `CLAUDE.md` | Project context | Every session |
| `docs/reference/ARCHITECTURE.md` | System design | Implementation |
| `docs/reference/LEARNINGS.md` | Proven patterns | Problem solving |
| `docs/standards/DESIGN_PRINCIPLES.md` | SQL/dbt standards | Writing models |
| `.claude/agents/AGENTS.md` | Agent orchestration | Using agents |
| `docs/plans/VISUALIZATION-ROADMAP.md` | BI tool roadmap | Visualization work |

---

## Summary

This project is a learning sandbox for:

1. **dbt** - Modern data transformation
2. **Agent orchestration** - AI-assisted development workflows
3. **Healthcare analytics** - Realistic domain with Synthea data

The foundation is complete (v0.1). Next step is building the staging layer (v0.2) to transform raw Synthea CSVs into clean, documented dbt models.

When in doubt:

- Read the existing documentation first
- Use the appropriate agent persona
- Work in `temp/` before finalizing
- Ask before making destructive changes

Happy modeling!

---

*Last Updated: 2026-01-29*
*Maintained by: Sage persona*
