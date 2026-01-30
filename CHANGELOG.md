# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned

- Intermediate models and business logic (v0.4)
- Marts layer with facts and dimensions (v0.5)

---

## [0.3.0] - 2026-01-29

### Added

- **Staging Models**: 9 comprehensive staging models for Synthea healthcare data
  - `stg_synthea__patients` - Patient demographics (1,171 rows)
  - `stg_synthea__encounters` - Healthcare visits (53,346 rows)
  - `stg_synthea__conditions` - Patient diagnoses (8,376 rows)
  - `stg_synthea__medications` - Prescriptions (42,989 rows)
  - `stg_synthea__procedures` - Medical procedures (34,981 rows)
  - `stg_synthea__observations` - Vitals/lab results (299,697 rows)
  - `stg_synthea__providers` - Healthcare professionals (5,855 rows)
  - `stg_synthea__organizations` - Healthcare facilities (1,119 rows)
  - `stg_synthea__payers` - Insurance payers (10 rows)

- **Data Loading**: `load_synthea_sources` macro for loading CSV data into DuckDB
  - Usage: `dbt run-operation load_synthea_sources`

- **Testing**: 80 data tests covering all staging models
  - Primary key tests (unique, not_null) on all models
  - Referential integrity tests (relationships) between models
  - Accepted values tests for categorical columns
  - Surrogate keys with row_number for deduplication

### Technical Notes

- Models use CTE pattern per coding standards
- Column names transformed from UPPERCASE to snake_case
- SSN hashed for privacy (md5)
- Observations table has ~10% null encounter_ids (valid data)
- dbt_utils.generate_surrogate_key used for composite primary keys

---

## [0.2.0] - 2026-01-29

### Added

- **uv Workflow**: Modernized Python environment with uv package manager
  - `pyproject.toml` for project metadata and dependencies
  - `uv.lock` for reproducible dependency versions
  - `.python-version` for automatic Python 3.11 selection
  - `docs/reference/UV_MIGRATION.md` comprehensive migration guide

- **Source Tables**: Added 6 new Synthea source tables to `_synthea__sources.yml`
  - `allergies` - Patient allergies and reactions
  - `immunizations` - Patient immunization records
  - `devices` - Medical devices used by patients
  - `imaging_studies` - Medical imaging studies (X-rays, MRIs, etc.)
  - `payer_transitions` - Patient insurance payer transitions over time
  - `supplies` - Medical supplies used during encounters

### Fixed

- **MCP Config**: Fixed `DBT_PROFILES_DIR` path expansion from `~/.dbt` to absolute path for proper dbt-mcp operation

### Changed

- **Documentation**: Updated all reference docs to reflect uv workflow
  - `PROJECT_STRUCTURE.md` - Added uv files and dbt_project structure
  - `ARCHITECTURE.md` - Added technology stack with uv dependencies
  - `README.md` - Added Quick Start with uv setup instructions
  - `coding-style.md` - Added Python/uv section
  - `scripts/README.md` - Documented available scripts and uv usage

---

## [0.1.0] - 2026-01-28

### Added

- **Agent System**: Complete dbt development agent orchestration with 16 personas
  - Base agents: Product Manager, Architect, Developer, Code Reviewer, Tester, Documenter, Security Reviewer, Design Reviewer, Git-Master, Sage, Changelog Generator
  - dbt agents: data-modeler, dbt-developer, dbt-tester, dbt-documenter, semantic-analyst

- **Skills**: 21 workflow skills including 6 dbt-specific
  - dbt-model-development, dbt-testing, dbt-code-review, dbt-deployment, dbt-source-onboarding, dbt-semantic-layer

- **Commands**: 13 slash commands including 5 for dbt
  - `/dbt-model`, `/dbt-test`, `/dbt-run`, `/dbt-docs`, `/dbt-query`

- **Documentation**: Comprehensive project planning
  - DBT-PROJECT-INITIALIZATION.md: 8-phase technical plan
  - ROADMAP.md: 6 epics, 4 milestones (v0.2-v0.5)
  - GITHUB-ISSUES.md: 41 actionable issues
  - 4 PRDs, 1 TDD for architecture decisions
  - Kimball dimensional modeling reference guide

- **Infrastructure**
  - GitHub project with 40 issues and 4 milestones
  - markdownlint-cli2 with pre-commit hooks
  - dbt-mcp server configuration
  - GitHub Flow workflow documentation

### Changed

- Rebranded from "japanese-study-site" to "dbt-playground"
- Updated workflow to GitHub Flow (no release branches)
- Added branch hygiene and versioning strategy documentation

### Fixed

- ~400 markdown formatting issues via linting

### Removed

- Japanese study site content and domain-specific agents
- Previous version archives (now using git tags)

---

## Version History

| Version | Date       | Highlights                                         |
| ------- | ---------- | -------------------------------------------------- |
| 0.3.0   | 2026-01-29 | v0.3 Staging Complete - 9 models, 80 tests, 440k+ rows |
| 0.2.0   | 2026-01-29 | v0.2 Environment Ready - uv workflow, 16 Synthea sources |
| 0.1.0   | 2026-01-28 | Agent orchestration + dbt project planning complete |

---

## How to Read This Changelog

### Categories

- **Added**: New features or content
- **Changed**: Changes to existing functionality
- **Deprecated**: Features to be removed in future
- **Removed**: Features removed in this release
- **Fixed**: Bug fixes
- **Security**: Security-related changes

### Version Numbers

- **MAJOR.MINOR.PATCH** (Semantic Versioning)
- MAJOR: Significant architectural changes
- MINOR: New features, content additions
- PATCH: Bug fixes, small corrections
