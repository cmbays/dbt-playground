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

- Initial project scaffold forked from agent orchestration template
- Agent orchestration system with 10 personas:
  - Product Manager, Architect, Developer, Code Reviewer
  - Tester, Documenter, Security Reviewer, Design Reviewer
  - Git-Master, Sage, Changelog Generator
- Documentation framework:
  - `docs/guides/` - How-to workflows
  - `docs/standards/` - Rules and conventions
  - `docs/reference/` - Technical documentation
  - `docs/specs/` - PRDs
  - `docs/tdd/` - Technical design docs
- Agent configuration in `.claude/`:
  - 10+ agent persona files
  - 8 slash commands (/plan, /review, /commit, /branch, /orchestrate, /deploy, /tdd, /repo-research)
  - 14+ reusable workflow skills
  - 4 coding rules (coding-style, git-workflow, testing, security)
  - Pre/post tool hooks
  - Utility scripts
- Git governance via git-master agent with enforcement hooks

### Removed

- Japanese study site content (previous project)
- Domain-specific content directories (content/, topics/, kanji/)
- Japanese-specific agents (sensei)
- Japanese-specific skills (kanji-content-creation, topic-page-creation)
- Japanese-specific rules (japanese-content.md)
- Japanese documentation (CONTENT_STANDARDS.md, ROADMAP.md)
- Previous version archives (v0.0-v0.2)
- Japanese PRDs and TDDs

### Changed

- Rebranded from "japanese-study-site" to "dbt-playground"
- Updated all documentation for generic data project use
- Simplified project structure for dbt development

---

## Version History

| Version | Date       | Highlights                                |
| ------- | ---------- | ----------------------------------------- |
| 0.1.0   | 2026-01-28 | Initial scaffold with agent orchestration |

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
