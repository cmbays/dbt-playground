# PRD-017: Repo Research Parallel Specialist Mode

## Overview

**Author**: Product Manager
**Status**: Implemented
**Created**: 2026-01-31 (Retrospective)
**Implemented**: 2026-01-31
**PR**: [#66](https://github.com/cmbays/dbt-playground/pull/66)
**Commit**: e9031b8

> **Note**: This is a retrospective PRD documenting a feature that was implemented and merged before formal PRD creation. The PM Report and Code Review exist in `temp/AGENT_REPORTS/repo-research-enhancements/`.

### Problem Statement

The `/repo-research` skill provides comprehensive single-threaded repository analysis through the Sage persona. However, deep repository research requires multiple perspectives (architecture, security, code quality) that are difficult to cover sequentially without:

1. **Context dilution**: Deep dives into one area reduce focus on others
2. **Single perspective limitation**: Sage conducts all research alone
3. **No structured multi-agent workflow**: Reports go to `docs/research/`, not optimized for multi-agent review
4. **Missing deliberation integration**: Findings require manual synthesis

### Goal

Enable **parallel specialist research mode** where multiple specialized agents simultaneously conduct focused analyses on different aspects of a repository, with structured artifact collection that integrates with council deliberation for synthesized recommendations.

## User Stories

### US-1: Parallel Specialist Research

**As a** developer evaluating a complex external repository,
**I want** multiple specialists to simultaneously research different aspects (architecture, security, quality),
**So that** I get deep, focused insights on each dimension without trade-offs.

**Acceptance Criteria**:

- [x] `--parallel` flag triggers multi-agent research mode
- [x] Each specialist uses `--focus` parameter for their domain
- [x] Specialists run concurrently (spawned via Task tool)
- [x] All specialist reports complete before master report generation

### US-2: Artifact Collection for Council Review

**As a** Supervisor or Council facilitator,
**I want** research artifacts stored in a predictable structure,
**So that** downstream agents can read findings directly without summarization loss.

**Acceptance Criteria**:

- [x] Master report: `temp/AGENT_REPORTS/[repo-name]/RESEARCH_MASTER.md`
- [x] Specialist reports: `temp/AGENT_REPORTS/[repo-name]/[ROLE]_FOCUS.md`
- [x] Report paths passed to council, not content summaries
- [x] Structure matches existing agent report conventions

### US-3: Depth and Parallel Mode Matrix

**As a** user choosing research depth,
**I want** clear guidance on what parallel options are available at each depth level,
**So that** I can balance thoroughness against time investment.

**Acceptance Criteria**:

- [x] `--depth=quick`: Sage only (no parallel option)
- [x] `--depth=standard`: Sage + optional 1-2 specialists
- [x] `--depth=deep`: Sage + full specialist team (default parallel)
- [x] Help text documents the matrix clearly

### US-4: Council Integration Hook

**As a** team wanting synthesized recommendations,
**I want** the parallel research output to integrate with the council skill,
**So that** diverse specialist perspectives are deliberated and reconciled.

**Acceptance Criteria**:

- [x] `--council` flag triggers council deliberation after research
- [x] Council receives paths to all specialist reports
- [x] Council produces `COUNCIL_SYNTHESIS.md` in same artifact folder
- [x] Works with existing council skill

## Requirements

### Functional Requirements

1. **FR-001**: `--parallel` flag enables multi-agent research mode
2. **FR-002**: `--focus` parameter specifies specialist scope (architecture, security, quality)
3. **FR-003**: Three specialist roles: architect, security-reviewer, code-reviewer
4. **FR-004**: Artifact folder: `temp/AGENT_REPORTS/[repo-name]/`
5. **FR-005**: Master report aggregates specialist findings
6. **FR-006**: Depth + parallel matrix documented in help text
7. **FR-007**: `--council` flag for deliberation handoff
8. **FR-008**: Progress indicators for parallel execution
9. **FR-009**: Specialist report template standardization
10. **FR-010**: Timeout handling for unresponsive specialists

### Non-Functional Requirements

1. **NFR-001**: Parallel execution completes in <50% overhead vs sequential (3x serial time)
2. **NFR-002**: Artifact quality enables council operation without clarification
3. **NFR-003**: Template consistency across all specialist reports
4. **NFR-004**: Graceful degradation when specialists fail

## Depth + Parallel Mode Matrix

| Depth | Default Behavior | Parallel Option | Specialist Count |
|-------|------------------|-----------------|------------------|
| `quick` | Sage only | Not available | 0 |
| `standard` | Sage only | `--parallel` adds 1-2 specialists | 0-2 |
| `deep` | Sage + specialists | `--parallel` (default on) | 3 (full team) |

**Specialist Assignments**:

| Specialist | Focus Flag | Research Emphasis |
|------------|------------|-------------------|
| `architect` | `--focus=architecture` | Structure, patterns, data flow, scalability |
| `security-reviewer` | `--focus=security` | Dependencies, vulnerabilities, auth patterns, data handling |
| `code-reviewer` | `--focus=quality` | Testing, documentation, maintainability, code standards |

## Artifact Structure

```
temp/AGENT_REPORTS/[repo-name]/
    RESEARCH_MASTER.md          # Sage master report with synthesis
    ARCHITECT_FOCUS.md          # Architecture specialist findings
    SECURITY_FOCUS.md           # Security specialist findings
    QUALITY_FOCUS.md            # Code quality specialist findings
    COUNCIL_SYNTHESIS.md        # (Optional) Council deliberation output
```

**Naming Convention**:

- `[repo-name]` derived from GitHub URL: `owner-repo` format
- Example: `dbt-labs-dbt-core` for `https://github.com/dbt-labs/dbt-core`

## Command Interface

```bash
# Standard single-agent research (unchanged)
/repo-research https://github.com/owner/repo

# Parallel specialist mode (new)
/repo-research https://github.com/owner/repo --parallel

# Deep research with full team (parallel default-on)
/repo-research https://github.com/owner/repo --depth=deep

# Standard depth with specific specialists
/repo-research https://github.com/owner/repo --parallel --specialists=architect,security-reviewer

# Full workflow with council deliberation
/repo-research https://github.com/owner/repo --depth=deep --council

# Focus flag for specialist invocation (internal use)
/repo-research https://github.com/owner/repo --focus=architecture
```

## Scope

### In Scope

- Parallel execution via Task tool
- Three specialist personas with domain focus
- Artifact-based handoff to council
- Structured report templates
- Depth/parallel mode matrix
- Error handling and graceful degradation

### Out of Scope

- Real-time collaboration between specialists (they work independently)
- Custom persona creation for specialists (use existing personas)
- Repository modification suggestions (research is read-only)
- Private repository access (requires separate auth)
- Caching/incremental research (future enhancement)

## Implementation Summary

### Files Modified

| File | Changes | Lines |
|------|---------|-------|
| `.claude/commands/repo-research.md` | Added parallel mode documentation | +115 |
| `.claude/skills/repo-research.md` | Parallel workflow, specialist coordination | +205 |
| `.claude/templates/specialist-focus-template.md` | New specialist report template | +234 |

**Total**: 554 lines added

### Key Features Delivered

1. **Parallel Mode Flag**: `--parallel` spawns 1-3 specialists based on depth
2. **Focus Parameter**: `--focus=architecture|security|quality` for specialist scope
3. **Council Integration**: `--council` flag triggers deliberation after research
4. **Artifact Structure**: `temp/AGENT_REPORTS/[repo-name]/` for inter-agent consumption
5. **Specialist Template**: Comprehensive template with structured findings format
6. **Error Handling**: Fallback to single-agent mode if all specialists fail

## Success Metrics

| Metric | Target | Achieved |
|--------|--------|----------|
| Research depth improvement | 2x coverage per dimension | ✅ Implemented |
| Time efficiency | <50% overhead vs sequential | ⏳ To be measured |
| Artifact quality | Council can operate without clarification | ✅ Template ensures this |
| Documentation completeness | All flags documented with examples | ✅ Complete |

## Dependencies

| Dependency | Status | Impact |
|------------|--------|--------|
| Council skill (`feat/council-skill`) | ✅ Merged (PR #67) | Full council integration available |
| Task tool for parallel execution | ✅ Available | Required for spawning specialists |
| Existing repo-research skill | ✅ Complete | Foundation for enhancement |
| Agent report templates | ✅ Available | Use `docs/templates/agent-reports/` patterns |

## Key Decisions Made

| Decision | Rationale |
|----------|-----------|
| Use existing personas with `--focus` rather than new specialist agents | Reduces complexity, leverages proven Sage methodology |
| Store artifacts in `temp/AGENT_REPORTS/` not `docs/research/` | Aligns with inter-agent report convention, not permanent documentation |
| Make parallel default-off for standard, default-on for deep | Progressive enhancement, explicit user choice for standard depth |
| Limit to 3 specialists | Covers primary evaluation dimensions without diminishing returns |
| Council integration as flag, not automatic | User controls cost/time trade-off |

## Code Review Notes

**Reviewer**: Code Reviewer
**Verdict**: APPROVED
**Date**: 2026-01-31

### Highlights

- Excellent workflow diagrams clearly illustrate parallel orchestration
- Comprehensive specialist template with structured findings format
- Well-thought-out depth matrix prevents confusion
- Council integration follows established AGENT_REPORTS pattern
- Error handling includes graceful degradation

### Minor Suggestions (Non-blocking)

1. Document council skill reference as "(planned)" → Resolved (council merged)
2. Standardize focus flag naming (short vs long form) → Documented both accepted
3. Add mapping table for specialist role → output file name → Added in docs
4. Add example of partial results on specialist failure → Documented in error handling

## Related

- **PR**: [#66 - feat: enhance repo-research with parallel specialist mode](https://github.com/cmbays/dbt-playground/pull/66)
- **Commit**: e9031b8
- **PM Report**: `temp/AGENT_REPORTS/repo-research-enhancements/PM_REPORT.md`
- **Code Review**: `temp/AGENT_REPORTS/repo-research-enhancements/CODE_REVIEW.md`
- **Council Skill**: PRD-018 (dependency, now implemented)
- **Agent Reports Pattern**: PRD-016 (foundation)
- **Skill Definition**: `.claude/skills/repo-research.md`
- **Command Reference**: `.claude/commands/repo-research.md`
- **Template**: `.claude/templates/specialist-focus-template.md`

---

*PRD Status: Implemented - Retrospective documentation of merged feature*
*Implementation Date: 2026-01-31*
*Documentation Date: 2026-01-31*
