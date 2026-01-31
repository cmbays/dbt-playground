# PRD-018: Council Skill for Consensus Decision Making

## Overview

**Author**: Claude Code Agent System (PM Persona)
**Status**: Draft
**Created**: 2026-01-31
**Updated**: 2026-01-31

### Problem Statement

Multi-agent workflows and deep research sessions suffer from two critical issues:

1. **Tunnel Vision**: Deep research leads to cognitive narrowing, confirmation bias, and attachment to conclusions without objective validation
2. **Conflicting Findings**: Multiple agents can produce contradictory recommendations with no arbiter to synthesize a unified direction

When the PM says "build it" but the Architect says "too complex," who decides? When Sage completes deep research, how do we validate conclusions before they become project learnings?

### Goal

Enable structured consensus decision-making by spawning fresh decision-maker panels that review accumulated artifacts and produce unified recommendations with captured dissent.

### Reference

- PM Report: `temp/AGENT_REPORTS/council-skill/PM_REPORT.md`
- Related: PRD-016 (Agent Context Management)

## User Stories

As a **Supervisor**, I want to convene a Council when multiple agents have contributed conflicting recommendations so that I can provide the human with a synthesized decision.

As a **Sage**, I want to trigger a Council review after deep research so that conclusions are validated by fresh perspectives before becoming project learnings.

As a **human (Chris)**, I want to invoke a Council manually for high-stakes decisions so that I get deliberated recommendations rather than single-agent opinions.

As a **downstream agent**, I want to read COUNCIL_CONSENSUS.md so that I can proceed with a validated direction rather than choosing between conflicting reports.

## Requirements

### Functional Requirements

#### FR-1: Council Invocation

Three invocation methods:

| Method | Trigger | Use Case |
|--------|---------|----------|
| `/council` | Manual command | User-initiated deliberation |
| `sage: convene council` | Sage-initiated | Post-research validation |
| Auto-trigger | Conditions met | Supervisor detects need |

**Auto-trigger conditions** (v0.8+):

- 3+ agent reports exist in feature folder
- High-stakes flag set (security, architecture decisions)
- Conflicting recommendations detected

#### FR-2: Council Depth Levels

| Depth | Council Size | Process | Duration |
|-------|--------------|---------|----------|
| `quick` | 1 synthesizer | Single-pass review | ~1 turn |
| `standard` | 3 perspectives | Parallel analysis, consensus | ~3 turns |
| `deep` | 5 + moderator | Structured debate, vote | ~5+ turns |

**Default**: `standard`

#### FR-3: Council Roles

**Core Roles (standard)**:

| Role | Focus | Key Question |
|------|-------|--------------|
| Pragmatist | Feasibility | "Can we actually do this?" |
| Advocate | Value | "What's the benefit?" |
| Skeptic | Risk | "What could go wrong?" |

**Extended Roles (deep)**:

| Role | Focus | Key Question |
|------|-------|--------------|
| Architect | Technical coherence | "Does this fit our architecture?" |
| Operator | Maintenance burden | "Can we sustain this?" |

#### FR-4: Consensus Report

Output: `temp/AGENT_REPORTS/[feature]/COUNCIL_CONSENSUS.md`

Structure:

- Recommendation with confidence level (HIGH/MEDIUM/LOW)
- Points of consensus
- Key trade-offs
- Dissenting views (always captured)
- Next actions

#### FR-5: Artifact Integration

- **Input**: All `*.md` files in `temp/AGENT_REPORTS/[feature]/`
- **Output**: `COUNCIL_CONSENSUS.md` to same folder
- **Additional outputs**: `COUNCIL_QUICK.md` (quick depth), `COUNCIL_DEBATE.md` (deep depth transcript)

### Non-Functional Requirements

1. **NFR-1**: Council completes within 5 minutes (standard depth)
2. **NFR-2**: Roles spawn fresh (no prior session context)
3. **NFR-3**: Dissenting views never suppressed
4. **NFR-4**: Output human-readable
5. **NFR-5**: No external dependencies

## Acceptance Criteria

- [ ] `/council` command triggers council deliberation
- [ ] Three depth levels available (quick, standard, deep)
- [ ] Council roles spawn as fresh perspectives
- [ ] COUNCIL_CONSENSUS.md written to feature folder
- [ ] Dissenting views captured explicitly
- [ ] Recommendation includes confidence level
- [ ] Next actions always specified

## Scope

### In Scope

**v0.7**:

- `/council` command implementation
- Standard depth (3 roles)
- COUNCIL_CONSENSUS.md output template
- Quick depth (1 synthesizer)

**v0.8+**:

- Deep depth (5 + moderator)
- Auto-trigger conditions
- Council history tracking

### Out of Scope

- Automated voting systems
- Council composition customization
- Cross-feature councils
- Real-time debate visualization
- External decision-tracking integration

## Dependencies

- Inter-Agent Reports structure (AGENT_REPORTS/) - Complete
- Sage persona - Complete
- Supervisor - Exists, needs enhancement
- `/council` command - New artifact
- Council skill file - New artifact

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Council adoption | >50% high-stakes decisions | COUNCIL_CONSENSUS.md count |
| Dissent capture | 100% | Audit of consensus files |
| Confidence distribution | >70% HIGH | Aggregate review |
| Retrospective validation | 3+ cases tracked | Compare recommendations to outcomes |

## Open Questions

1. Should council roles be separate agent files or parameterized prompts?
2. How to ensure fresh context (no prior session leakage)?
3. Can standard depth roles run in parallel?
4. What heuristics detect "conflicting recommendations"?
5. How does the deep-depth moderator facilitate without biasing?

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Fresh perspectives | No prior context | Ensures objectivity |
| Three depth levels | Match effort to importance | Efficient resource use |
| Dissent always captured | Never suppress | Enables retrospective learning |
| Single consensus file | One per invocation | Avoids file proliferation |

## Related

- **PM Report**: `temp/AGENT_REPORTS/council-skill/PM_REPORT.md`
- **TDD**: TBD (pending Architect)
- **Issue**: TBD
- **PRD-016**: Agent Context Management (foundational)
