# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned

- Incremental refresh patterns for large fact tables (v0.6)
- Advanced analytics models (clustering, cohort analysis) (v0.6)
- Real-time monitoring and alerting (v0.6)

---

## [0.5.0] - 2026-01-30

### Added

- **Analytics Models**: 7 new specialized analytics models for healthcare
  - `dim_conditions` - Master condition dimension (130 rows)
  - `fct_patient_summary` - Annual patient aggregations (21,343 rows)
  - `fct_provider_metrics` - Monthly provider metrics (33,463 rows)
  - `fct_condition_cohorts` - Patient-condition cohorts (7,165 rows)
  - `fct_cost_analysis` - Detailed cost analysis (53,346 rows)
  - `v_patient_current_conditions` - Active conditions view (3,811 rows)
  - `v_provider_active_patients` - Provider panels view (5,855 rows)

- **Comprehensive Testing**: 45+ new tests (91 total for analytics models)
  - Schema validation: 33 tests
  - Grain validation: 3 tests (unique_combination_of_columns)
  - Referential integrity: 8 tests (relationships)
  - Data quality: 38 tests (dbt_expectations)
  - Singular tests: 5 custom SQL validations
  - 100% pass rate

- **Documentation**:
  - Complete YAML documentation with example queries (3+ per model)
  - BI Integration Guide for Tableau, Looker, Power BI, Metabase, Superset
  - Test coverage and validation documentation

### Technical Highlights

- Extends v0.4's dimensional foundation with specialized analytics
- Implements 3 healthcare analytics use cases:
  - Patient outcomes tracking
  - Provider performance metrics
  - Cost analysis and financial reporting
- Maintains Kimball dimensional methodology and conformed dimensions
- Follows dbt 1.11+ best practices (new `arguments:` syntax)
- Synthea healthcare dataset with 100K+ synthetic patients/encounters

### Compatibility

- No breaking changes to v0.4 models
- Fully compatible with existing dimensions and facts
- Requires dbt 1.11.2+, DuckDB 1.10.0+

---

## [Unreleased-Tools]

### Added

- **RSS Digest Tool**: AI/Claude/Agents content aggregator with 26 curated feeds
  - `scripts/rss_digest.py` - Fetches RSS from Anthropic, OpenAI, researchers, newsletters
  - Generates interactive HTML digest with category filtering and full-text search
  - Dark mode support for comfortable reading
  - `/rss` command with subcommands: `list`, `config`, `schedule`, `add`, `remove`
  - Daily scheduling via launchd (7 AM) with `com.dbt-playground.rss-digest.plist`

- **PR-Centric Development Workflow**: Comprehensive workflow enhancement for context preservation
  - Draft PR creation at branch/worktree creation (`--with-pr` default)
  - Multi-agent review posting to GitHub PRs via `gh` CLI
  - Post-review agent queue (docs → sage → pm) before merge
  - Supervisor final approval gate with checklist
  - Auto-cleanup of worktree and branch after merge

- **Agent Updates**: 6 agents enhanced for PR-centric workflow
  - `git-master`: PR-first workflow, approval gate enforcement, auto-cleanup
  - `supervisor`: Review orchestration, post-review queue, final approval
  - `code-reviewer`: Inline PR comments and summary reviews
  - `security-reviewer`: Security findings posted to PRs
  - `documenter`: PR-commit mode for CHANGELOG updates
  - `sage`: PR learning extraction with commit support

- **Command Updates**: 2 commands enhanced
  - `/branch`: Added `--with-pr` flag (default on) for draft PR creation
  - `/review`: Added `--pr N` flag for posting reviews to GitHub

- **New Workflow**: `.claude/workflows/post-review-queue.md`
  - Defines post-review agent queue sequence
  - Documents agent invocation templates
  - Specifies skip conditions and error handling

- **Documentation**: PRD-015-WORKFLOW-ENHANCEMENT.md

---

## [0.4.0] - 2026-01-30

### Added

- **Intermediate Models**: Business logic and enrichment layer
  - `int_encounters__enriched` - Encounters with derived fields
  - `int_patients__with_conditions` - Patients joined with conditions

- **Dimension Models**: 5 core dimensions for analytics
  - `dim_patients` - Patient master with demographics and relationships
  - `dim_providers` - Healthcare providers (many-to-many with organizations)
  - `dim_organizations` - Healthcare facility/organization master
  - `dim_payers` - Insurance payer/payor information
  - `dim_date` - Date dimension for time-based aggregations (spans 100 years)

- **Fact Models**: 4 core facts for analytics
  - `fct_encounters` - Base encounter facts with all encounter types
  - `fct_clinical_events` - Events (conditions, observations, procedures) denormalized
  - `fct_encounters_monthly` - Monthly aggregate of encounters
  - `fct_encounters_yearly` - Yearly aggregate of encounters

- **Snapshots**: Slowly Changing Dimension Type 2
  - `snp_patients` - Tracks patient demographic changes over time

- **Documentation**: v0.4 design and implementation
  - Updated PRD-004-DIMENSIONAL-MODELS.md with implementation
  - TDD-004-DIMENSIONAL-MODELS.md: Technical design for dimensional models
  - v0.4_PLAN.md: Implementation plan and execution notes

### Technical Highlights

- Kimball dimensional modeling patterns
- SCD Type 2 for patient dimension
- Date spine for time series analysis
- Proper grain and fact architecture
- Comprehensive test coverage on all models

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
| 0.5.0   | 2026-01-30 | v0.5 Analytics - 7 models, 91 tests, BI integration |
| 0.4.0   | 2026-01-30 | v0.4 Dimensional Models - 12 models, Kimball patterns, SCD2 |
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
