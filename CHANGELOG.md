# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned

- Incremental refresh patterns for large fact tables (v0.9)
- Advanced analytics models (clustering, cohort analysis) (v0.9)
- Real-time monitoring and alerting (v0.9)

---

## [0.9.0] - 2026-02-01

### Added

- **PM Orchestration (Hybrid Lite)** - Multi-session coordination system (#118, #131)
  - **Session Management**:
    - `PM_SESSIONS.json` - Session tracking with heartbeat and stale detection
    - `scripts/pm_sessions.js` - CLI helpers (625 lines) for session lifecycle management
    - Commands: `register`, `heartbeat`, `claim`, `release`, `active`, `check-stale`
    - 5-minute stale session threshold with automatic detection
    - File locking with DRY abstraction and schema validation
    - 40/40 unit tests passing for core session operations

  - **Backlog.md Integration**:
    - v1.35.4 installed and configured with custom 5-stage workflow columns
    - Workflow stages: UNDERSTAND → PLAN → BUILD → VERIFY → DEPLOY (+ BLOCKED)
    - REST API integration (`/api/tasks`, `/api/config`) for cross-session task visibility
    - Remote operations support for multi-worktree coordination
    - Active branch checking to prevent conflicts
    - MCP integration for agent-driven task management

  - **Workflow Hub Widgets** (Phase 2):
    - **PM Overview Widget** - Session health metrics and status summary
    - **Active Sessions Widget** - Real-time session tracking with heartbeat indicators
    - **Kanban Board Widget** (#110, #130) - 7-column drag-and-drop task board
      - Columns: Backlog, UNDERSTAND, PLAN, BUILD, VERIFY, DEPLOY, Done
      - Card details: type icons, priority, labels, issue numbers
      - Click-to-expand modal with "Start Session", "Move to", GitHub link actions
      - Done lane archiving with show more/less (20 cards default)
      - GitHub sync via `/api/github-issues` endpoint
      - Responsive design for tablet/mobile with swipe indicator
      - Keyboard shortcuts: D (Kanban), K (All), S (sync), Esc (close)
      - Toast notifications for user actions
      - Accessibility: ARIA attributes, keyboard navigation, focus management
      - LocalStorage for column assignments and collapsed state
      - ~600 lines of elegant functional code (70% reduction from initial design)

  - **Supervisor Integration** (Phase 3):
    - Session registration workflow on startup
    - Backlog.md API integration for task queries
    - Automatic heartbeat maintenance
    - Task claiming with conflict detection
    - 8/8 E2E tests passing for Supervisor integration (TASK-10, TASK-11)

  - **Multi-Worktree Visibility** (Phase 3):
    - Cross-worktree task visibility via Backlog.md API
    - Shared state architecture (PM_SESSIONS.json + Backlog.md)
    - Single active session per worktree enforcement
    - 10/10 E2E tests passing for multi-worktree coordination (TASK-12)

  - **Testing**:
    - **Unit Tests**: 40/40 passing (`scripts/__tests__/pm_sessions.test.js`)
    - **E2E Tests**: 29/29 passing (3.3s execution time)
      - 11 widget tests (PM Overview, PM Sessions, health checks)
      - 8 supervisor integration tests (registration, API, heartbeat)
      - 10 multi-worktree visibility tests (config, task tracking, workflow)
    - Performance verified: 10 concurrent operations in <2s

  - **Configuration**:
    - `backlog/config.yml` - Custom workflow stages and settings
    - `scripts/pm_config.js` - Shared configuration module (33 lines)
    - Test infrastructure: `scripts/update_tests_async.js` for async test updates

- **Architecture Documentation**:
  - `PRD-022-PM-ORCHESTRATION.md` - Product requirements (updated to Hybrid Lite scope)
  - `TDD-022-PM-ORCHESTRATION-HYBRID-LITE.md` - Technical design specification
  - `PRD-023-KANBAN-BOARD.md` - Kanban board product requirements
  - `TDD-023-KANBAN-BOARD.md` - Kanban board technical design
  - `ARCH_DECISION_HYBRID_LITE.md` - Architecture decision rationale
  - `ADR-001-backlog-md-adoption.md` - Decision record (Approved)
  - `ADR-002-sqlite-state-layer.md` - Decision record (Superseded by Hybrid Lite)
  - `ADR-003-dbt-pm-analytics.md` - Decision record (Superseded by Hybrid Lite)

- **Workflow Hub Enhancements**:
  - PM sessions endpoint (`/api/pm-sessions`) in playground server
  - Backlog.md CORS proxy endpoints (`/api/backlog/tasks`, `/api/backlog/config`)
  - Improved error handling and cleanup in server endpoints
  - Body scroll locking when modal is open for better UX

- **Planning for v0.10**:
  - Agent Orchestration planning documents for 7 feature sets (#143-149)
  - Epic issues for FS1-FS8: Memory & Learning, Kanban Workflow, QA Enforcement, Metrics, Multi-Agent Coordination, GitHub Integration, Hackathon System
  - Implementation issues #150-170 for v0.10 milestone tasks
  - Target: Apr 30, 2026

### Changed

- **Supervisor Agent** - Enhanced with PM orchestration capabilities
  - Session registration on startup
  - Backlog.md API integration for task management
  - Heartbeat workflow for session health tracking
  - Updated documentation (383 line addition to `.claude/agents/supervisor.md`)

- **Workflow Hub** - Major UI/UX improvements
  - Integrated Kanban board as primary view (587 lines added)
  - Enhanced PM overview and sessions widgets
  - Improved keyboard shortcuts and accessibility
  - Better responsive design for mobile/tablet

- **Project Status** - Updated CLAUDE.md and ROADMAP.md
  - v0.8.0 marked complete (31 models, 425 tests, 0 errors)
  - v0.9 marked implementation complete, ready for deployment
  - Added v0.10 milestone planning with 7 epic feature sets

### Fixed

- **Playground Server**:
  - PM sessions endpoint error handling
  - Backlog.md CORS proxy endpoints for cross-origin requests
  - Test assertions to match actual API responses (`session_id` vs `id`)
  - Proper cleanup in E2E tests to prevent state leakage

- **Kanban Board**:
  - LocalStorage cleanup for closed issues during sync
  - Clipboard error handling with `prompt()` fallback
  - Focus management for modal accessibility
  - Schema validation for localStorage data integrity
  - External link security with `rel="noopener noreferrer"`

- **CI/CD**:
  - Removed data loading step from dbt-test workflow (#c78183c)
  - Removed GitHub comment step from dbt-test workflow (#f992553)

### Deprecated

- **SQLite State Database** - Deferred to future enhancements (#140)
  - Only implement if Hybrid Lite shows race conditions or needs SQL analytics
  - Current JSON + Backlog.md approach provides 90% of requirements

- **dbt PM Analytics** - Deferred to future enhancements (#141)
  - Task velocity, bottleneck detection, agent productivity metrics
  - Only implement if business value is proven

- **Advanced Alerting** - Deferred to future enhancements (#142)
  - Conflict detection, orphaned tasks, branch drift, PR feedback tracking
  - Current simple stale detection sufficient for v0.9

### Technical Highlights

- **Architecture Decision**: Hybrid Lite over SQLite + bi-directional sync
  - Rationale: Backlog.md provides REST API, MCP, browser UI, CLI out of the box
  - Implementation time: 4 hours vs 2-3 weeks for full SQLite solution
  - Maintenance: 1 system + 1 JSON file vs 3 systems (MD + SQLite + dbt)
  - Zero sync complexity (single source of truth)

- **Kanban Board Rewrite**: Functional module pattern
  - 70% code reduction (~500 lines vs ~1,600 lines in initial implementation)
  - Uses existing `issues` array as data source (no duplication)
  - Only stores column assignments in localStorage (minimal state)
  - Elegant IIFE module pattern for better maintainability

- **Multi-Worktree Coordination**: Shared state architecture
  - PM_SESSIONS.json provides session-level tracking across worktrees
  - Backlog.md API provides task-level visibility across worktrees
  - One active session per worktree enforcement prevents conflicts
  - Remote operations config enables cross-worktree task queries

- **Testing Strategy**: Comprehensive coverage at multiple levels
  - Unit tests for core session operations (40 tests)
  - E2E tests for UI widgets, API integration, multi-worktree scenarios (29 tests)
  - Manual CLI verification for all commands
  - Performance testing for concurrent operations

### Performance

- **E2E Test Suite**: 29 tests execute in 3.3 seconds
- **Concurrent Operations**: 10 simultaneous PM session operations complete in <2s
- **Kanban Board**: Smooth drag-and-drop performance with minimal DOM manipulation
- **LocalStorage**: Efficient schema with only column assignments stored (not full card data)

### Accessibility

- **ARIA Attributes**: Proper roles, labels, and states for screen readers
- **Keyboard Navigation**: Tab navigation, Enter/Space activation, Escape to close
- **Focus Management**: Auto-focus on modal open, focus trapping, visible focus indicators
- **Mobile Support**: Responsive design with swipe indicator, touch-friendly targets

### Related Issues & PRs

- Closes #118 - PM Orchestration System (Hybrid Lite)
- Closes #110 - Kanban Board Widget
- Implemented via PR #131 - Phase 1 Backlog.md Core Integration
- Implemented via PR #130 - Kanban Board Implementation (v0.7.2)
- Related to #113 - Multi-session coordination requirements
- Deferred #140 - SQLite state database
- Deferred #141 - dbt PM analytics integration
- Deferred #142 - Advanced alerting system

### Migration Notes

No breaking changes. PM Orchestration is purely additive:

- Existing workflows continue to work unchanged
- New PM features are opt-in via Supervisor integration
- Workflow Hub widgets can be used independently

### Future Enhancements

**Deferred from v0.9 to future releases**:

- SQLite state database (only if race conditions emerge)
- dbt PM analytics (task velocity, bottleneck detection)
- Advanced alerting (conflict detection, orphaned tasks)
- Bi-directional sync engine (eliminated - single source of truth via Backlog.md)

**Planned for v0.10** (Apr 2026):

- Agent Memory & Learning System (FS1)
- Kanban Workflow Engine automation (FS2)
- QA & Testing Enforcement (FS3)
- Metrics & Dashboard System (FS5)
- GitHub Integration enhancements (FS7)

---

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
