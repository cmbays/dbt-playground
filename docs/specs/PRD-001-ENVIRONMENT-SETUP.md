---
title: Environment Setup
prd_number: PRD-001
epic: E1-Environment-Setup
version: 0.2.0
status: draft
author: pm
created: 2026-01-28
last_updated: 2026-01-28
---

## Overview

### Problem Statement

The dbt-playground project requires a functional development environment before any data modeling work can begin. This includes database connectivity (DuckDB), dbt adapter configuration, project initialization, and MCP tooling for AI-assisted development.

### Goal

Establish a complete, verified dbt development environment that enables the agent team to create, test, and document dbt models with AI assistance.

### Success Metrics

- `dbt debug` passes with no errors
- `dbt deps` installs all required packages
- MCP server responds to tool invocations
- Project structure matches dbt best practices

---

## Requirements

### Functional Requirements

#### FR-1: dbt-duckdb Adapter Installation

**Priority**: P0 (Critical)

Install the dbt-duckdb adapter to enable DuckDB as the data warehouse.

**Acceptance Criteria**:

- [ ] `dbt-duckdb` package installed via pip
- [ ] Version >= 1.7.0 for latest features
- [ ] Installation verified with `dbt --version`

#### FR-2: dbt Profile Configuration

**Priority**: P0 (Critical)

Create the dbt profile that defines database connections.

**Acceptance Criteria**:

- [ ] `~/.dbt/profiles.yml` created
- [ ] Profile named `dbt_playground` to match project
- [ ] `dev` target configured with local DuckDB path
- [ ] `prod` target configured for separate database file
- [ ] 4 threads configured for parallel execution

**Profile Specification**:

```yaml
dbt_playground:
  outputs:
    dev:
      type: duckdb
      path: ./dbt_project/dev.duckdb
      threads: 4
    prod:
      type: duckdb
      path: ./dbt_project/prod.duckdb
      threads: 4
  target: dev
```

#### FR-3: dbt Project Initialization

**Priority**: P0 (Critical)

Initialize the dbt project with proper structure.

**Acceptance Criteria**:

- [ ] `dbt init dbt_project` executed from project root
- [ ] `dbt_project.yml` configured with correct name and profile
- [ ] Directory structure created (models/, tests/, macros/, etc.)
- [ ] Model paths configured for staging/intermediate/marts layers

**Project Configuration**:

```yaml
name: 'dbt_playground'
version: '0.1.0'
config-version: 2
profile: 'dbt_playground'

model-paths: ["models"]
analysis-paths: ["analyses"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]

models:
  dbt_playground:
    staging:
      +materialized: view
      +schema: staging
    intermediate:
      +materialized: view
      +schema: intermediate
    marts:
      +materialized: table
      +schema: marts
```

#### FR-4: Package Dependencies

**Priority**: P1 (High)

Install essential dbt packages for utilities and testing.

**Acceptance Criteria**:

- [ ] `packages.yml` created with required packages
- [ ] `dbt deps` installs all packages successfully
- [ ] Packages verified in `dbt_packages/` directory

**Required Packages**:

| Package | Version | Purpose |
|---------|---------|---------|
| dbt-labs/dbt_utils | 1.3.0 | Core utilities and macros |
| calogica/dbt_expectations | 0.10.4 | Data quality testing |
| calogica/dbt_date | 0.10.1 | Date/time utilities |
| dbt-labs/codegen | 0.12.1 | Code generation helpers |

#### FR-5: MCP Configuration

**Priority**: P1 (High)

Configure dbt-mcp for AI-assisted development.

**Acceptance Criteria**:

- [ ] `.mcp.json` updated with dbt server configuration
- [ ] `dbt-mcp` installed or available via `uvx`
- [ ] MCP server starts without errors
- [ ] Basic MCP tool invocation succeeds

**MCP Configuration**:

```json
{
  "mcpServers": {
    "dbt": {
      "command": "uvx",
      "args": ["dbt-mcp"],
      "env": {
        "DBT_PROJECT_PATH": "./dbt_project",
        "DBT_PROFILES_DIR": "~/.dbt"
      }
    }
  }
}
```

#### FR-6: Gitignore Updates

**Priority**: P1 (High)

Ensure dbt artifacts are properly gitignored.

**Acceptance Criteria**:

- [ ] `*.duckdb` files ignored
- [ ] `dbt_project/target/` ignored
- [ ] `dbt_project/dbt_packages/` ignored
- [ ] `dbt_project/logs/` ignored
- [ ] `dbt_project/data/` ignored (raw data)

---

### Non-Functional Requirements

#### NFR-1: Cross-Platform Compatibility

Configuration should work on macOS, Linux, and Windows (WSL).

#### NFR-2: Reproducibility

All setup steps should be documented and repeatable by another developer.

#### NFR-3: Isolation

dbt environment should not interfere with other dbt projects on the same machine.

---

## User Stories

### US-1: Developer Environment Setup

**As a** developer
**I want** a one-command setup process
**So that** I can start working on dbt models quickly

**Acceptance Criteria**:

- Setup script or clear instructions provided
- All dependencies installed in correct order
- Verification steps confirm successful setup

### US-2: AI-Assisted Development

**As an** agent (dbt-developer)
**I want** MCP tools available for dbt operations
**So that** I can create and test models programmatically

**Acceptance Criteria**:

- MCP tools respond to queries
- Can execute `dbt run` via MCP
- Can query model information via MCP

---

## Technical Specifications

### Directory Structure After Setup

```text
dbt-playground/
├── .mcp.json                 # MCP configuration
├── dbt_project/
│   ├── dbt_project.yml       # Project configuration
│   ├── packages.yml          # Package dependencies
│   ├── profiles.yml          # (gitignored, use ~/.dbt/)
│   ├── models/
│   │   ├── staging/
│   │   │   └── synthea/      # Synthea source models
│   │   ├── intermediate/
│   │   │   └── healthcare/   # Business logic models
│   │   └── marts/
│   │       └── core/         # Analytics models
│   ├── tests/                # Singular tests
│   ├── macros/               # Custom macros
│   ├── seeds/                # Reference data
│   ├── snapshots/            # SCD tracking
│   ├── analyses/             # Ad-hoc queries
│   ├── target/               # Compiled output (gitignored)
│   ├── dbt_packages/         # Installed packages (gitignored)
│   ├── logs/                 # Run logs (gitignored)
│   └── data/                 # Raw data (gitignored)
│       └── synthea/          # Synthea CSV files
└── scripts/
    └── setup_dbt.sh          # Setup script
```

### Verification Commands

```bash
# Step 1: Verify dbt installation
dbt --version

# Step 2: Verify profile
dbt debug

# Step 3: Install packages
dbt deps

# Step 4: Compile (should succeed with empty models)
dbt compile

# Step 5: Verify MCP
claude mcp list
```

---

## Implementation Notes

### Prerequisites

- Python 3.9+ installed
- pip or pipx available
- Git configured
- Claude Code installed (for MCP)

### Installation Order

1. Install dbt-duckdb adapter
2. Create dbt profile
3. Initialize dbt project
4. Create packages.yml
5. Run dbt deps
6. Configure MCP
7. Update gitignore
8. Verify all components

### Known Issues

- DuckDB path must be relative to dbt project, not absolute
- MCP requires correct `DBT_PROJECT_PATH` environment variable
- Some dbt packages may have version conflicts; pin versions explicitly

---

## Agent Assignment

| Task | Agent | Notes |
|------|-------|-------|
| Adapter installation | developer | Python package management |
| Profile creation | developer | System configuration |
| Project initialization | dbt-developer | dbt CLI operations |
| Package configuration | dbt-developer | dbt ecosystem knowledge |
| MCP setup | developer | MCP configuration |
| Verification | dbt-tester | Testing and validation |

---

## Dependencies

### Upstream

- None (first epic)

### Downstream

- E2: Data Acquisition (requires working dbt environment)
- E3: Staging Layer (requires packages installed)

---

## Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| dbt-duckdb version incompatibility | High | Low | Pin to stable version |
| MCP configuration issues | Medium | Medium | Document troubleshooting steps |
| Profile path issues | Medium | Medium | Use `~/.dbt/` standard location |
| Package conflicts | Low | Medium | Pin all package versions |

---

## Open Questions

1. Should we create a setup script for one-command installation?
2. Do we need both dev and prod targets, or just dev for learning?
3. Should MCP configuration be project-local or user-level?

---

## References

- [dbt-duckdb Documentation](https://github.com/duckdb/dbt-duckdb)
- [dbt Project Structure](https://docs.getdbt.com/docs/build/projects)
- [dbt-mcp Documentation](https://github.com/dbt-labs/dbt-mcp)
- [Implementation Plan](../plans/DBT-PROJECT-INITIALIZATION.md)

---

*PRD Status: Draft - Ready for Review*
