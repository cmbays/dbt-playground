# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

**Skills & Agents Enhancement (PR #70, #69, #68, #67, #66, #65)**

**Web Design Review Skill** (PR #70)
- `/web-design-review` command for visual design analysis
- Playwright MCP integration for browser automation
- Comprehensive design audit checklist:
  - Visual hierarchy and spacing
  - Color contrast and accessibility
  - Responsive design verification
  - Component consistency checking
  - Typography and readability
- Screenshot capture and analysis

**Enhanced Repository Research** (PR #69)
- Multi-repo comparison capabilities
- Quality rubric framework for code assessment
- Metrics collection for:
  - Architecture patterns and consistency
  - Code organization and modularity
  - Documentation quality
  - Test coverage and practices
  - Performance patterns

**Documenter Audit Tools** (PR #68)
- Doc-health audit script for comprehensive documentation review
- Checks for:
  - Missing or stale documentation
  - Broken links and references
  - Inconsistent formatting
  - Coverage gaps in critical areas

**Sage Context Management** (PR #67)
- Checkpoint skill for saving learned patterns and session state
- Context window optimization for long-running projects
- Automatic pattern extraction and consolidation
- Session persistence across context boundaries

**Changelog Generator Agent** (PR #66)
- Automated CHANGELOG generation from git history
- Semantic versioning support
- Release notes and migration guides
- Customizable commit message parsing

**OS Notification Hooks** (PR #65)
- Desktop notifications for task completion
- Configurable notification timing
- Task summary in notification body
- Cross-platform support (macOS, Linux, Windows)

---

## [0.5.0] - 2026-01-27

### Added

**Git-Master Agent System**
- Git-Master agent (`git:` prefix) for centralized git operations
  - 3-layer enforcement: CLAUDE.md rules, hook blocking, agent validation
  - Workflow G: Pre-merge checklist (CHANGELOG, docs sync, Sage notification)
  - Worktree contraindications and decision matrix
- Commands:
  - `/commit` - Validated commit with Conventional Commits enforcement
  - `/branch` - Validated branch creation with naming conventions
- Skills:
  - `git-operations.md` - Step-by-step git workflows with validation
  - `worktree-orchestration.md` - Parallel development with conflict prevention
- Hook enforcement (`pre-bash-check.js`)
  - BLOCKS git write operations without `GIT_MASTER_AUTHORIZED=true`
  - Emergency bypass with `--bypass-git-master` flag (logged to audit)

**Team Optimizations Initiative (PR #64)**

**Agent Enhancement System**
- YAML frontmatter added to all 11 agent files for context optimization
  - Fields: `name`, `description`, `tools`, `model`
  - Enables ~20-30 token savings per Task call (no `allowed_tools` needed)
- Red Flags sections added to priority agents:
  - `architect.md` - 10 architecture anti-patterns
  - `code-reviewer.md` - 10 code quality anti-patterns
  - `security-reviewer.md` - 10 security anti-patterns
  - `tester.md` - testing anti-patterns
- Concrete code examples added to `architect.md` and `code-reviewer.md`
  - Module export pattern
  - Default value pattern (|| vs ??)
  - Data structure naming conventions
  - Initialization error handling
  - State immutability

**Repository Research Framework**
- `/repo-research` skill for analyzing external repositories
- Research report template (`.claude/templates/repo-research-report-template.md`)
- Research reports directory (`docs/research/`)
- Completed research: `everything-claude-code` analysis with adoption recommendations

**Documentation**
- PRD-007: Team Optimizations specification
- TDD-003: Agent Enhancement technical design (544 lines)
- Test specification: `docs/testing/v0.5_TESTING-Agent-Enhancement.md`
- Knowledge Management reference (`docs/reference/knowledge-management.md`)

**Scripts**
- `scripts/validate-frontmatter.sh` - Validate agent YAML frontmatter
- `scripts/count-agent-tokens.sh` - Measure agent token metrics

### Changed
- Updated CLAUDE.md with Git-Master persona and `/commit`, `/branch`, `/repo-research` commands
- Updated AGENTS.md with horizontal service agent documentation and frontmatter documentation section (+123 lines)
- Updated git-workflow.md with Agent Git Governance section
- Updated deployment-workflow.md to use `git:` prefix
- Updated documenter.md to delegate git ops to git-master
- Consolidated `docs/guides/` directory content into `sage.md` and `knowledge-management.md`
- Renamed PRD-003-Team-Optimizations to PRD-007-Team-Optimizations (numbering fix)

### Fixed
- PRD numbering conflict: Team Optimizations PRD renumbered from PRD-003 to PRD-007
  - PRD-003 already assigned to Habit Formation System

---

## [0.4.0] - 2026-01-25

### Added

**Phase 2: Engagement Layer - Gamification & Progress Tracking**

**Sprint 1: XP, Levels & Streaks**
- XP Engine (`content/kanji/js/xp-engine.js`)
  - Base 10 XP per review with quality bonuses (+5 Good, +10 Easy)
  - Streak multipliers (1.1x at 7 days, 1.25x at 30 days, 1.5x at 100 days)
  - Level system with 60 levels and exponential thresholds
  - Milestone celebrations at levels 10, 20, 30, 40, 50, 60
- Streak Manager (`content/kanji/js/streak-manager.js`)
  - Daily streak tracking with automatic date detection
  - Streak freeze system (max 2 freezes, earned at 7+ day streaks)
  - Streak milestone celebrations (7, 30, 100, 365 days)
  - Streak recovery within grace period
- Schema Migration v1.0.0 → v1.1.0 (`content/kanji/js/storage.js`)
  - Added `stats.xp`, `stats.streak`, `stats.daily_goal` objects
  - Added `stats.daily_history` for activity tracking
  - Added `stats.weekly_snapshots` for trend data
  - Added `stats.at_risk_kanji` for regression tracking
  - Automatic migration on load with version detection

**Sprint 2: Progress Dashboard Visualizations**
- Dashboard Visualizations Module (`content/kanji/js/dashboard-visualizations.js`)
  - 365-day study heatmap (GitHub-style activity calendar)
  - Topic mastery rings (SVG circular progress indicators)
  - 8-week mastery trend line (SVG polyline chart)
  - At-risk kanji panel (tracks SRS stage regressions)
  - Stats summary panel (XP, accuracy, reviews, mastered count)
- Dashboard CSS (`content/kanji/css/dashboard.css`)
  - 1,380+ lines of visualization styles
  - Responsive layouts for all dashboard components
  - Tooltip styling for heatmap and trend interactions
  - Color-coded intensity levels and progress states

**Sprint 3: Daily Goals with Notifications**
- Goals Manager (`content/kanji/js/goals-manager.js`)
  - Daily goal setting (1-100 cards, presets: 5/10/15/20/25)
  - Goal progress tracking with percentage calculation
  - Goal completion detection with 50 XP bonus
  - Browser notification support with permission handling
  - Notification scheduling for daily reminders
- Goal UI Components
  - Goal widget with progress bar on dashboard
  - Goal setting modal with preset buttons and custom input
  - Notification settings with toggle and time picker
  - Goal completion celebration with confetti animation

**Testing Infrastructure**
- Unit test files for all new modules:
  - `test-xp-engine.html` - XP calculation and level tests
  - `test-streak-manager.html` - Streak logic and freeze tests
  - `test-goals-manager.html` - Goal tracking and notification tests
  - `test-dashboard-visualizations.html` - Visualization rendering tests
  - `test-migration.html` - Schema migration tests

**Documentation**
- PRD-005: Progress Dashboard specification
- TDD-003: Habit Formation technical design (1,249 lines)
- Updated PRD-003 with Sprint 1-3 scope clarification

### Changed
- Updated `content/kanji/index.html` with engagement layer integration (+870 lines)
  - XP/Level progress widget in header
  - Streak counter with flame icon
  - Daily goal widget with progress bar
  - Progress Dashboard section with all visualizations
  - Celebration modals (level up, streak milestone, goal complete)
- Moved `.mcp.json` to `.claude/.mcp.json` for cleaner project root

### Fixed
- Trend line rendering: Changed from `appendChild` to `innerHTML` (createTrendLine returns string)
- Notification toggle: Prevent state reset after permission grant

---

## [0.3.0] - 2026-01-25

### Added

**JLPT Mastery Engine Phase 1 Implementation**:
- Complete SM-2 spaced repetition algorithm (`content/js/srs-engine.js`)
  - Quality ratings (AGAIN=0, HARD=2, GOOD=4, EASY=5) with interval calculation
  - Ease factor management with min/max bounds (1.3-5.0)
  - Stage transitions: +1 for GOOD/EASY, -1 for HARD, -2 for AGAIN
- Mastery calculator module (`content/js/mastery-calculator.js`)
  - JLPT-level mastery aggregation (N5, N4, N3, N2)
  - Topic-based mastery calculation (home-life, shopping, restaurant, travel)
  - 8-stage mastery system: Locked → Lesson → Apprentice 1-4 → Guru 1-2 → Master → Enlightened → Burned
- Session manager module (`content/js/session-manager.js`)
  - Due card queue management based on next_review_date
  - New card introduction with configurable daily limits (default: 10/day)
  - Session creation combining due + new cards
- localStorage persistence layer (`content/js/storage.js`)
  - Schema versioning (v1.0.0) for future migrations
  - Per-kanji progress tracking with review history (max 50 entries)
  - Data validation and sanitization for XSS prevention
  - Automatic cache invalidation for mastery calculations
- Kanji study dashboard (`content/kanji/index.html`)
  - Flashcard UI with front/back flip animation
  - JLPT level filtering (N5, N4, N3, N2, All)
  - Response buttons (Again, Hard, Good, Easy) integrated with SRS
  - Session statistics display (due cards, reviews completed)
- Home page kanji mastery widget (`content/index.html`)
  - Summary widget showing JLPT mastery percentages
  - Quick link to continue studying

**Epic → TDD → Task Workflow Pattern**:
- Complete TDD-001 specification (1,606 lines) for JLPT Mastery Engine
  - §1: 4-layer architecture with data flow diagrams
  - §2: Complete localStorage schema with 1,032-line reference implementation
  - §3: SM-2 algorithm with pseudocode and edge case handling
  - §4: 8-stage mastery system (Locked → Burned) with state machine
  - §5: JLPT/topic aggregation formulas
  - §6: API contracts for all 4 modules
  - §7: 42 test cases (unit, integration, edge cases)
- PROJECT_WORKFLOW.md (571 lines) documenting Epic → TDD → Task pattern
  - Personas and responsibilities (PM, Architect, Developer, Tester)
  - Real-world example using PRD-001 → TDD-001 → Tasks
  - Best practices per persona
  - Templates for PRDs, TDDs, and Tasks
  - When to skip phases (workflow exceptions)
- Updated GitHub tasks #13-22 with TDD section references
  - Transformed vague tasks into specific implementation instructions
  - Added acceptance criteria mapping to TDD sections
  - Included function signatures, pseudocode, and test case references

**Documentation Reorganization**:
- Reorganized docs/ into categorical subdirectories:
  - `docs/guides/` - How-to workflows (PROJECT_WORKFLOW, PROJECT_BOARD_GUIDE, CLAUDE_TASK_INTEGRATION)
  - `docs/standards/` - Rules and conventions (TESTING, CONTENT_STANDARDS, DESIGN_PRINCIPLES, WORKFLOW_EXCEPTIONS)
  - `docs/reference/` - Technical documentation (ARCHITECTURE, PROJECT_STRUCTURE, ROADMAP)
- YAML frontmatter tagging system for all documentation
  - Schema: audience, priority, size, dependencies, last_updated, status, tags
  - DOC_TAGS_MANIFEST.md documenting complete tagging reference
  - Smart loading strategies for persona-based filtering
  - Token budget management (~50K target for typical tasks)
- Updated docs/README.md with:
  - Category-based navigation
  - Smart loading patterns per persona
  - Documentation guidelines and recent changes
- Updated DOCUMENTATION_INDEX.md with:
  - New docs/ subdirectory structure
  - Comprehensive wiki links for cross-referencing
  - "I Need to Understand YAML Tagging" quick reference
  - Expanded keyword and question-based lookups
  - Navigation tips for agents and Christopher

**Claude Task GitHub Integration (MVP - Phases 0-2)**:
- Cross-session task persistence for multi-agent workflows
- Metadata validation system with JSON schema enforcement
- GitHub issue to Claude task conversion tool
- Script library in `.claude/scripts/`:
  - `core/validate-metadata.sh` - Metadata validation with exit codes
  - `core/task-helpers.sh` - Utility functions for metadata extraction
  - `github-sync/issue-to-task.sh` - Convert GitHub issues to TaskCreate calls
- 5 task types with schema validation: epic, task, tdd, pm-work, documentation
- Pattern validation for Epic IDs (PRD-XXX), TDD sections (§N), effort (S/M/L/XL)
- Copy-pasteable TaskCreate output for seamless workflow
- Comprehensive integration guide: `docs/CLAUDE_TASK_INTEGRATION.md`
- Scripts documentation: `.claude/scripts/README.md`
- Updated project board guide with Claude Task integration section

**Multi-Agent Orchestration System**:
- 8 specialized personas with dedicated profiles
- Agent profiles in `.claude/agents/` directory
- PRD and TDD templates for feature planning
- Review process documentation
- Comprehensive agent orchestration guide (`.claude/agents/AGENTS.md`)
- Documentation maintenance protocols (`.claude/agents/DOC_MAINTENANCE.md`)
- Master documentation index (`DOCUMENTATION_INDEX.md`)
- 60+ wiki-links connecting documentation network
- Agent onboarding path for fresh context sessions

**Sage Persona and Learning Repository System** (PR #42):
- 10th persona "Sage" (`sage:` prefix) for learning curation and knowledge management
- Active learning repository that compounds knowledge over time
- Single-source-of-truth hierarchy: Skills → LEARNINGS.md → FOR_CHRIS docs
- Decision rubric for FOR_CHRIS docs (≥2 criteria: architectural decision, novel pattern, workflow change, multiple approaches, educational value)
- Quality bar: patterns proven ≥2 times in practice (not theoretical)
- Four Sage workflows:
  - Session Learning Curation (extract patterns from sessions)
  - Bug Learning Extraction (document root causes and prevention)
  - Pattern Discovery (create reusable skills when pattern used ≥2 times)
  - Milestone Learning Documentation (create educational narratives)
- New files:
  - `.claude/agents/sage.md` - Persona definition (includes operational examples and tips)
  - `docs/reference/knowledge-management.md` - Cross-agent knowledge management reference
  - `.claude/templates/for-chris-doc-template.md` - Template for educational docs
  - `docs/reference/LEARNINGS.md` - Technical patterns reference (10 patterns)
  - `.claude/skills/continuous-learning.md` - Pattern extraction workflow
  - `.claude/skills/learning-curation.md` - Session curation workflow
  - `archive/FOR_CHRIS_docs/README.md` - Educational docs index
- Topic-based naming for FOR_CHRIS docs:
  - Renamed `FOR_CHRIS_pm_setup.md` → `github-project-setup.md`
  - Renamed `FOR_CHRIS_agent_orchestration.md` → `agent-orchestration-comparison.md`
- 10 documented patterns with real examples:
  - Assembly Line Workflow (v0.1, v0.2)
  - Parallel Review Execution (v0.1, v0.2)
  - Explicit Agent File Operations (T1.1, v0.3)
  - Agent Context Preparation (T1.1, T1.2, v0.3)
  - Agent vs Manual Decision Framework (v0.1-v0.3)
  - Temp-First File Creation (v0.1, v0.2)
  - Living vs. Version Documentation (all versions)
  - When to Create TDDs (v0.3 Epic → TDD → Task workflow)
- Integration with existing agent system:
  - Sage runs in parallel with Documenter after feature completion
  - Documenter handles version-specific facts; Sage extracts cross-session patterns
  - Updated `.claude/agents/documenter.md` with division of responsibility
  - Updated `.claude/agents/DOC_MAINTENANCE.md` with Sage procedures
- Learning digest created: `temp/LEARNING_DIGEST_2026-01-25.md`

**Kanji Learning Features**:
- Kanji localStorage schema design (T1.1) with SM-2 algorithm

### Changed
- **Content directory restructure**: Reorganized `topics/`, `kanji/`, `css/`, `js/` into unified `content/` directory
  - `content/topics/` - All topic content (home-life, shopping, restaurant, travel)
  - `content/kanji/` - Kanji study module and data
  - `content/css/` - Shared stylesheets
  - `content/js/` - Shared JavaScript modules (including new SRS engine)
- Updated CLAUDE.md with agent orchestration section
- Updated CLAUDE.md with prominent AGENTS.md references
- Rewrote `docs/README.md` with improved navigation and YAML tagging system
- Enhanced `.claude/agents/README.md` with purpose statement
- Added "Related Documentation" sections to 10+ files across project
- Added "For New Agents" onboarding section to AGENTS.md
- Updated `docs/PROJECT_BOARD_GUIDE.md` with Claude Task integration workflows
- Moved 10 documentation files from docs/ root to categorical subdirectories
- Added YAML frontmatter tags to all documentation files
- Updated all cross-references to reflect new documentation structure
- Enhanced DOCUMENTATION_INDEX.md with comprehensive wiki links
- Removed `FOR_CHRIS.md` at root (replaced with topic-specific docs in `archive/FOR_CHRIS_docs/`)
- Moved `docs/LEARNINGS.md` → `docs/reference/LEARNINGS.md` (updated 9 references)

### Fixed
- Documented critical agent handoff protocol (agents return content for review)
- Consolidated redundant documentation across multiple files
- Established single source of truth mapping for each topic

### Security
- Addressed code review critical issues in JLPT Mastery Engine:
  - Input validation for localStorage data before use
  - XSS prevention via proper data sanitization in mastery calculator
  - Safe JSON parsing with try/catch error handling
  - Schema validation to prevent corrupted data injection

### Dependencies
- Requires `gh` CLI (GitHub command-line tool): `brew install gh`
- Requires `jq` (JSON parser): `brew install jq`

---

## [0.2.0] - 2025-01-20

### Added
- Kanji study module with flashcard interface
- JLPT level filtering (N5, N4, N3, N2)
- 169 kanji with full metadata (readings, meanings, examples)
- Flashcard flip animation and navigation
- Kanji data generation scripts

### Changed
- Separated kanji module from topics structure
- Data files stored in `kanji/data/` directory

---

## [0.1.0] - 2025-01-19

### Added
- Initial project structure
- Reorganized content into `topics/` directory
- 4 core topics: Home Life, Shopping, Restaurant, Travel
- Shared CSS and JavaScript resources
- Documentation framework (CLAUDE.md, docs/)
- Content types: phrases, dialogue, story, manga, quiz, tips

### Changed
- Established mobile-first responsive design
- Standardized file naming conventions

---

## Version History

| Version | Date | Highlights |
|---------|------|------------|
| 0.4.0 | 2026-01-25 | Phase 2 Engagement Layer: XP/Levels, Streaks, Daily Goals, Progress Dashboard visualizations |
| 0.3.0 | 2026-01-25 | JLPT Mastery Engine (SM-2 SRS), Content directory restructure, Epic → TDD → Task workflow, Multi-agent orchestration |
| 0.2.0 | 2025-01-20 | Kanji study module |
| 0.1.0 | 2025-01-19 | Initial structure, 4 topics |

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
