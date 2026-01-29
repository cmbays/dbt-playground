# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned

- dbt project initialization
- dbt-mcp integration
- SQL database connection setup
- Sample data models

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
