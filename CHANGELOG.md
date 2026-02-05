# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.11.0] - 2026-02-05

### Added

- **Wave 3 P1: Backend Maturation - Protocol Enhancements** (#229-#238)
  - **WAVE3-010**: BACKEND_STRUCTURE_TEMPLATE.md - Canonical template for backend architecture documentation
  - **WAVE3-011**: API Contract Validation spec (1,500+ words) - Validation rules, breaking changes, versioning strategy
  - **WAVE3-012**: LESSONS.md Trigger Patterns (2,000+ words) - 15 patterns across 8 categories for automated extraction
  - **WAVE3-013**: Observability Integration spec (2,500+ words) - Jaeger spans, Prometheus metrics, error taxonomy, debug_startup hooks
  - **WAVE3-014**: Schema versioning patterns design
  - **WAVE3-015**: DEPLOYMENT_VALIDATION_CHECKLIST.md - Tier 1→2 and Tier 2→3 promotion gates
  - **WAVE3-016**: OBSERVABILITY.md template (1,800+ words) - Monitoring stack, metrics, alerting, dashboards, Gate T2-1 checklist
  - **WAVE3-017**: INCIDENT_TEMPLATE.md - 7-section RCA structure for pattern extraction
  - **WAVE3-020**: Debug Session Tracker CLI
    - Commands: start, log, end, query, status
    - DuckDB persistence (debug_sessions, debug_steps tables, 2 views)
    - Session ID format: DBG-YYYY-MM-DD-NNN
    - FS1 integration via memory/events.jsonl
    - 110 tests, 77% coverage
  - **WAVE3-021**: LESSONS.md Analyzer CLI
    - Commands: extract, review, generate, stats
    - Multi-factor scoring: (Frequency*0.4) + (Recency*0.3) + (Consistency*0.3)
    - 4-tier classification: PROMOTE/CANDIDATE/REVIEW/IGNORE
    - Keyword clustering (0.5 threshold)
    - LESSONS.md entry generation
    - 110 tests, 77% coverage
  - **Integration Reports** (Days 5-6)
    - ARCH_INTEGRATION_REPORT.md - Observability verification, API validation design
    - PLANNER_INTEGRATION_REPORT.md - Deployment gates validation, incident workflow
    - DEV_E2E_REPORT.md - E2E test results, performance benchmarks

### Fixed

- **CodeRabbit Critical Issues** (c5ed0aa)
  - Backup recovery OSError logging (database.py:141)
  - Event emission I/O failure handling (tracker.py:365)
  - Recency scoring calculation using current time (clustering.py:217)
  - Timezone handling for aware/naive datetime comparison (models.py:59-66)
  - XSS vulnerability in Workflow Chronicle (commit metadata escaping)
  - Null guard for decision.confidence (workflow-chronicle.html:1026)
- **CodeRabbit Minor Issues** (c5ed0aa)
  - Replaced broad 'except Exception' with specific types (database.py:411)
  - Added SessionState.from_dict validation for required fields
  - Division-by-zero guard in recency_weight function
  - Space key support for template card activation (mermaid-designer.html)

### Changed

- Multi-agent orchestration pattern: Parallel execution across 3 tracks (architect, planner, developer)
- Agent reports now written to `temp/AGENT_REPORTS/[feature]/` for tracked features
- Integration testing phase added to sprint workflow (Days 5-6)

### Added

- **FS5 Metrics & Dashboard System** (#146)
  - DuckDB-based metrics database (replaces SQLite per ADR-015)
  - Direct JSONL querying via `read_json_auto()` views
  - Adherence scoring service with 0-120 scale formula
  - Anomaly detection rules engine (8 rules)
  - Dashboard widgets for Workflow Hub integration
  - **Agent Visualizer Integration** (#172)
    - New "Agents" tab in Workflow Hub
    - Mermaid-powered workflow diagram
    - State inspector for tracks and phases
    - Collapsible execution timeline
    - Keyboard shortcut (A) for quick access

### Changed

- **PRD-027 v1.1** (2026-02-03)
  - Updated to use DuckDB instead of SQLite per ADR-015
  - Changed FR-011 from sync script to JSONL views
  - Updated performance requirements for view-based queries

### Added

- **Compound Learning Loop Integration** (#163)
  - Sage session logging trigger after QA phase (Post-QA)
  - Memory bootstrap in `/plan` command reads `memory/MEMORY_INDEX.md`
  - Relevance filtering with topic keyword matching and score threshold (≥0.7)
  - Metrics instrumentation emits events to `events.jsonl` for FS5

### Planned

- Incremental refresh patterns for large fact tables (v0.9)
- Advanced analytics models (clustering, cohort analysis) (v0.9)
- Real-time monitoring and alerting (v0.9)

---

## [0.7.1] - 2026-02-02

### Added

- **Agent Visualizer Playground** - Interactive tool for visualizing agent workflows and state
  - `playgrounds/agent-visualizer.html` - Single-file HTML playground (2047 lines)
  - `/playground:agents` command for launching

- **F1.1: Workflow Diagram Generator**
  - Auto-generates Mermaid flowcharts from WORKFLOW_STATE.md
  - Visualizes phase progression (UNDERSTAND -> PLAN -> BUILD -> VERIFY -> DEPLOY)
  - Shows track status with color-coded nodes
  - Export to clipboard or download as PNG/SVG

- **F1.2: Execution Timeline**
  - Phase progress bars with visual status indicators
  - Agent execution sequence tracking
  - Duration tracking for completed phases
  - Session metrics display (releases, models, tests, worktrees)

- **F1.4: State Inspector**
  - Visual display of WORKFLOW_STATE.md content
  - Frontmatter card with last updated, active track, last release
  - Track cards with phase pills, artifacts, and progress indicators
  - Real-time health score calculation

### Technical Highlights

- Manual paste mode for WORKFLOW_STATE.md content (API endpoints optional)
- Drag-and-drop file support for quick data loading
- localStorage caching for session persistence
- Consistent UI patterns with existing playgrounds (Workflow Hub, Chronicle)
- Mermaid.js integration for diagram rendering
- Responsive design with dark mode support
- Comprehensive help modal with keyboard shortcuts

### Documentation

- Updated CLAUDE.md with Agent Visualizer in playground table
- Updated playgrounds/README.md with usage instructions
- Added `/playground:agents` command integration

---

## [0.8.0] - 2026-02-01

### Added

- **Phase 5: Data Quality Quarantine System** - Macro-based pattern for systematic DQ handling
  - 3 reusable macros in `macros/data_quality/`:
    - `add_dq_flags()` - Adds individual validation flags + `is_dq_valid` + `failed_dq_tests` array
    - `quarantine_filter()` - Generates WHERE clause to filter invalid records
    - `generate_quarantine_model()` - Creates quarantine table with one line
  - 2 quarantine tables in `models/intermediate/quarantine/`:
    - `int_dq_quarantine__encounters` - 1 quarantined encounter (0.002% of 53,346)
    - `int_dq_quarantine__medications` - 5 quarantined medications (0.012% of 42,989)
  - DQ monitoring mart: `mart_dq_summary` - Entity-level quarantine metrics
  - Applied `{{ quarantine_filter() }}` to 3 downstream models (fct_encounters, fct_clinical_events, int_encounters__enriched)

- **Documentation**:
  - `docs/decisions/ADR-004-data-quality-quarantine.md` - Architecture decision record
  - `docs/reference/DATA_QUALITY_QUARANTINE.md` - Complete usage guide with examples
  - `macros/data_quality/README.md` - Macro documentation with usage patterns

- **Validation Rules** (Encounters):
  - `valid_encounter_timestamps`: encounter_end_at >= encounter_start_at
  - `no_future_encounter_dates`: encounter_start_at <= current_timestamp
  - `end_after_1900`: encounter_end_at >= timestamp '1900-01-01'
  - `start_after_1900`: encounter_start_at >= timestamp '1900-01-01'

- **Validation Rules** (Medications):
  - `valid_medication_dates`: medication_end_at is null or >= medication_start_at
  - `no_future_medication_dates`: medication_start_at <= current_date
  - `start_after_1900`: medication_start_at >= timestamp '1900-01-01'
  - `end_after_1900_if_present`: medication_end_at is null or >= timestamp '1900-01-01'

### Changed

- Updated `stg_synthea__encounters` to include DQ validation flags
- Updated `stg_synthea__medications` to include DQ validation flags
- Modified `fct_encounters` to filter quarantined encounters
- Modified `fct_clinical_events` to filter quarantined medications and validate encounter references
- Modified `int_encounters__enriched` to filter quarantined medications

### Fixed

- **Eliminated 2 ERROR-level test failures** (100% test pass rate achieved)
  - `assert_encounter_timestamps_valid` - Now filters by is_dq_valid (PASS)
  - `assert_medication_dates_valid` - Now filters by is_dq_valid (PASS)

### Testing

- Added 20 new tests for quarantine system (all passing)
- **Test Summary**: 423 PASS, 2 WARN, 0 ERROR (was 405 PASS, 2 ERROR)
- Verified 0 quarantined records leak to downstream marts (join tests)

### Performance

- Build time increase: ~20% (2.0s → 2.4s for full build)
- Well below 30% threshold for acceptable impact
- DuckDB optimizes redundant condition evaluation in macros

### Technical Highlights

- DuckDB-specific features: `list_value()` for arrays, `filter (where ...)` for conditional aggregation
- Individual validation flags enable precise debugging (see which specific rule failed)
- `failed_dq_tests` array allows aggregation analysis (which rules fail most often)
- Macro pattern enables consistent DQ handling across all entities
- Quarantine tables preserve evidence for root cause analysis

### Architectural Decisions

- **Macro-based abstraction**: Chosen over inline SQL for code reuse and debugging features
- **Quarantine at staging**: Earliest detection point, before transformations
- **Individual flags**: Trade-off accepted for debugging value (vs. single boolean)
- **DuckDB-only**: Acceptable for single-database learning project

### Future Enhancements (Out of Scope)

- Extend quarantine to conditions, procedures, observations
- Auto-remediation macros for common violations
- Historical quarantine trend tracking (SCD Type 2)
- Alert integration (email/Slack) for quarantine rate thresholds
- Multi-database support (adapter-specific macro implementations)

---

## [0.7.0] - 2026-01-31

### Added

- **Phase 3: GitHub Project Management** - Complete (Features 1-4)
  - Issue creation CLI (`scripts/github-ops.py`) with batch YAML templates (#92)
  - Milestone tracking with CLI commands and CLAUDE.md status section (#93)
  - Enhanced PR-Issue linking with extended keyword support (#94)
    - Keywords: `Closes`, `Fixes`, `Resolves` (auto-close), `Related to`, `See also` (keep open)
    - Issue existence validation and categorized logging
    - Bidirectional GitHub linking automatic
  - GitHub Projects integration using built-in automation (#95)
    - Design decision: Use GitHub's native project automation (no custom workflow)
    - Auto-manage issues via labels and GitHub Project settings
    - Supports single project for all repo tracking

- **ADR Adoption Phase 2**: ADR-to-LEARNINGS promotion workflow
  - `docs/reference/LEARNINGS.md` - Pattern Promotion section with first promoted pattern (ADR-2)
  - `.claude/agents/sage.md` - Workflow H for ADR pattern promotion review
  - `docs/specs/TDD-HISTORICAL.md` - 3 backfilled ADRs from v0.5-v0.6
  - `docs/reference/ADR_INDEX.md` - 8 total ADRs with promotion tracking
  - `docs/templates/agent-reports/SESSION_SUMMARY.md` - ADR review section
  - Goal: Proven ADR patterns flow to LEARNINGS.md automatically

- **ADR Adoption Phase 1**: Formalized architecture decision tracking (PRD-021)
  - `docs/specs/PRD-021-ADR-ADOPTION.md` - Initiative specification
  - `docs/reference/ADR_INDEX.md` - Centralized ADR discovery (5 ADRs indexed)
  - `docs/specs/TDD-TEMPLATE.md` - ADR section with significance criteria, examples
  - `docs/reference/ROADMAP.md` - Epic E13 (Decision Management) roadmap entry
  - Goal: Find decision rationale in <2 minutes

### Documentation

- Added PR-Issue Linking syntax table to git-workflow.md
- Updated GITHUB_ENFORCEMENT.md with Phase 3 GitHub Actions documentation

---

## [0.6.0] - 2026-01-31

### Added

- **Interactive Playgrounds**: Phase 1 visual tools for development
  - `worktree-coordinator.html` - Git worktree management dashboard
    - Manual paste mode for git data input
    - Worktree cards with branch/status/PR info
    - Copy-command buttons for common operations
    - Keyboard shortcuts (R: refresh, ?: help)
  - `mermaid-designer.html` - Diagram creation with live preview
    - Live Mermaid rendering (400ms debounce)
    - 6 built-in templates (dbt layers, agent workflow, ER diagram, etc.)
    - Export to Markdown, SVG, PNG, standalone HTML
    - Save/load diagrams to browser localStorage
    - Dark mode support

- **Technical Documentation**:
  - TDD-014: Technical design for playground tools
  - Updated playgrounds/README.md with usage instructions

### Technical Highlights

- Single-file HTML approach (no build step, no server)
- Shared CSS/JS patterns across playgrounds
- Mermaid.js loaded from CDN for diagram rendering
- localStorage for diagram persistence
- Consistent keyboard shortcuts and dark mode

### Compatibility

- No breaking changes to existing features
- Playgrounds work in Chrome 90+, Firefox 88+, Safari 14+, Edge 90+

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
| 0.7.1   | 2026-02-02 | Agent Visualizer Playground - workflow diagrams, timeline, state inspector |
| 0.7.0   | 2026-01-31 | v0.7 Phase 3 GitHub Project Management + ADR Phase 2 Promotion Workflow |
| 0.6.0   | 2026-01-31 | v0.6 Playgrounds - Worktree Coordinator, Mermaid Designer |
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
