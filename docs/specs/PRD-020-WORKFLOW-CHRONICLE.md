# PRD-020: Workflow Chronicle - Development Observability System

## Overview

**Author**: Product Manager (Retrospective)
**Status**: Implemented
**Created**: 2026-01-31 (Retrospective)
**Implemented**: 2026-01-30
**PR**: [#62](https://github.com/cmbays/dbt-playground/pull/62)
**Research**: 5-team competitive ideation process (6,815 lines)

> **Note**: This is a retrospective PRD documenting a feature that was extensively researched, implemented, and merged before formal PRD creation. Research artifacts exist in `temp/competitive-ideation-cycle-2/` and `temp/WORKFLOW_CHRONICLE_INDEX.md`.

### Problem Statement

Working across multiple Claude Code sessions creates context fragmentation:

1. **Invisible State Evolution**: No visibility into how workflow state changes over time
2. **Lost Context**: Returning after days away requires 5+ minutes to rebuild mental model
3. **No Learning Loop**: Patterns and anti-patterns emerge but aren't systematically captured
4. **Quality Blindness**: No metrics to measure whether standards are improving or degrading
5. **Agent Activity Opacity**: What have agents been doing? What decisions were made?
6. **Performance Unknowns**: Which workflow phases are bottlenecks?

### Goal

Build a **Workflow Chronicle** observability system that enables:

- **Recall**: What happened? (Immutable event log)
- **Reflect**: What patterns emerged? (Analytics and trends)
- **Resume**: How do I get back to work fast? (30-second context recovery)

**Tagline**: *"Remember everything. Learn what matters."*

## Core Philosophy: The Three Rs

| Principle | Question Answered | Implementation |
|-----------|-------------------|----------------|
| **Recall** | What happened? | Immutable JSONL event log, git-based timeline |
| **Reflect** | What patterns emerged? | Health pulse, phase duration tracking, negative space |
| **Resume** | How do I get back to work fast? | Auto-generated context bootstrap, 30-second rule |

## User Stories

### US-1: 30-Second Context Recovery

**As a** developer returning to the project after days away,
**I want** auto-generated context bootstrap with my last session summary,
**So that** I can resume productive work in <30 seconds.

**Acceptance Criteria**:

- [x] `generate-bootstrap.py` creates `temp/CONTEXT_BOOTSTRAP.md`
- [x] Includes: last action, next action, decisions made, open questions
- [x] Reads from `temp/SESSION_SUMMARY_*.md` and `temp/WORKFLOW_STATE.md`
- [x] Regenerates automatically at session boundaries

### US-2: Workflow State History Timeline

**As a** developer managing multiple features,
**I want** visual timeline of workflow state changes,
**So that** I understand what happened across sessions.

**Acceptance Criteria**:

- [x] `workflow-timeline.py` generates git-based timeline
- [x] Shows: commits, phase transitions, agent activity
- [x] Color-coded by type (feat, fix, docs, chore)
- [x] Outputs both terminal and JSON formats

### US-3: Health Pulse Visibility

**As a** project maintainer,
**I want** composite health score (0-100) based on workflow metrics,
**So that** I know when process improvements are needed.

**Acceptance Criteria**:

- [x] `compute-health-pulse.py` calculates score from multiple signals
- [x] Metrics: commit velocity, phase duration, agent collaboration, test coverage
- [x] Color-coded output: Green (>80), Yellow (60-80), Red (<60)
- [x] `workflow-glance.py` shows health in 3-second terminal check

### US-4: Visual Chronicle Playground

**As a** user exploring project history,
**I want** interactive visual timeline with filterable layers,
**So that** I can see commits, agents, decisions, and health trends.

**Acceptance Criteria**:

- [x] `workflow-chronicle.html` single-file playground
- [x] Stratified timeline with layers: Commits, Agents, Decisions, Health
- [x] Filter by date range and event type
- [x] Dark/light mode support
- [x] Click-to-expand event details

### US-5: Negative Space Documentation

**As a** team making architectural decisions,
**I want** persistent record of what we decided NOT to do,
**So that** we don't revisit rejected approaches.

**Acceptance Criteria**:

- [x] `temp/NEGATIVE_SPACE.yaml` schema for rejected decisions
- [x] `check-negative-space.py` queries and displays decisions
- [x] Includes: question, rationale, confidence, reconsider trigger
- [x] Integrated into Chronicle playground

### US-6: Quality Ratchet Enforcement

**As a** quality-conscious team,
**I want** baseline quality metrics that can only improve,
**So that** we fight entropy and prevent degradation.

**Acceptance Criteria**:

- [x] `check-ratchet.py` enforces non-degradation
- [x] Metrics: model count, test count, documentation coverage
- [x] Baseline stored in `temp/WORKFLOW_HISTORY/ratchet-history.json`
- [x] Fails CI if metrics drop below baseline

## Requirements

### Functional Requirements

1. **FR-001**: Immutable event log in JSONL format
2. **FR-002**: Git-based timeline generator (zero instrumentation)
3. **FR-003**: 3-second terminal health check
4. **FR-004**: Composite health pulse score (0-100)
5. **FR-005**: Auto-generated context bootstrap for session resume
6. **FR-006**: Visual timeline playground with stratified layers
7. **FR-007**: Negative space decision tracking
8. **FR-008**: Quality ratchet baseline enforcement
9. **FR-009**: Schema validation for events and decisions
10. **FR-010**: Context drift detection

### Non-Functional Requirements

1. **NFR-001**: Terminal tools complete in <3 seconds (workflow-glance)
2. **NFR-002**: Playground loads and renders in <2 seconds
3. **NFR-003**: Zero instrumentation - git is telemetry source
4. **NFR-004**: Human-in-the-loop learning (system proposes, human approves)
5. **NFR-005**: Graduated enforcement (Inform → Warn → Block)

## Core Metrics

| Metric | Purpose | Implementation |
|--------|---------|----------------|
| **Feature Velocity** | Throughput (features/week) | Count merged PRs with type:feat |
| **Phase Duration** | Bottleneck identification | Time in PRD/ARCH/BUILD/etc. |
| **Resume Time** | Context preservation health | Measure from session start to productive work |
| **Standards Score** | Quality baseline | Composite of model count, test count, docs |
| **Health Pulse** | Overall workflow health | 0-100 score from multiple signals |

## Implementation Summary

### 6-Week Roadmap (All Delivered)

| Week | Deliverables | Status |
|------|--------------|--------|
| **Week 1** | Zero Setup Foundation | ✅ Complete |
| | - workflow-timeline.py | ✅ |
| | - workflow-glance.py | ✅ |
| | - Event schema (event-schema.json) | ✅ |
| **Week 2** | Event Capture + Quick Resume | ✅ Complete |
| | - capture-event.py | ✅ |
| | - generate-bootstrap.py | ✅ |
| | - Ratchet baseline (ratchet-history.json) | ✅ |
| **Week 3** | Stratified Timeline Playground | ✅ Complete |
| | - generate-chronicle-data.py | ✅ |
| | - workflow-chronicle.html | ✅ |
| **Week 4** | Health Pulse + Negative Space | ✅ Complete |
| | - compute-health-pulse.py | ✅ |
| | - check-negative-space.py | ✅ |
| | - NEGATIVE_SPACE.yaml (7 decisions documented) | ✅ |
| **Week 5** | Quality Ratchet | ✅ Complete |
| | - check-ratchet.py | ✅ |
| **Week 6** | Integration | ✅ Complete |
| | - validate-schemas.py | ✅ |
| | - detect-drift.py | ✅ |

### Files Created

**Total**: 6,770 lines across 17 files

#### Playground (1 file)

| File | Lines | Purpose |
|------|-------|---------|
| `playgrounds/workflow-chronicle.html` | 951 | Visual timeline with stratified layers |

#### Scripts (10 files)

| Script | Purpose | Key Features |
|--------|---------|--------------|
| `workflow-timeline.py` | Git-based timeline | Commits, phase transitions, agent activity |
| `workflow-glance.py` | 3-second health check | Quick health score, current state |
| `capture-event.py` | Event ingestion | Schema-validated JSONL append |
| `generate-bootstrap.py` | Context bootstrap | 30-second resume generation |
| `generate-chronicle-data.py` | Playground data generator | Aggregates events for visualization |
| `compute-health-pulse.py` | Health scoring | 0-100 composite from multiple signals |
| `check-negative-space.py` | Decision tracking | Query rejected decisions |
| `check-ratchet.py` | Quality enforcement | Non-degradation baseline checks |
| `validate-schemas.py` | Schema validation | Pre-commit validation for events |
| `detect-drift.py` | Context drift detection | Alert when context diverges |

#### Data Structures

| File | Purpose |
|------|---------|
| `temp/WORKFLOW_HISTORY/events.jsonl` | Append-only event log |
| `temp/WORKFLOW_HISTORY/chronicle-data.json` | Aggregated data for playground |
| `temp/WORKFLOW_HISTORY/ratchet-history.json` | Quality baseline storage |
| `temp/NEGATIVE_SPACE.yaml` | Rejected decisions (7 documented) |
| `temp/CONTEXT_BOOTSTRAP.md` | Auto-generated quick resume |

#### Documentation Updates

| File | Changes |
|------|---------|
| `CLAUDE.md` | Updated project status to v0.6.0 |
| `playgrounds/README.md` | Added Workflow Chronicle entry |

## Design Principles

1. **Capture comprehensively, surface sparingly**: Log everything, show what matters
2. **Measure improvement, not performance**: Processes, not people
3. **Human-in-the-loop learning**: System proposes, human approves
4. **Graduated enforcement**: Inform → Warn → Block
5. **Zero instrumentation**: Git is the telemetry source (Alpha Timeline principle)
6. **Schema-validated architecture**: Beta Foundation - structured even if simple

## Key Features

### 1. Alpha Timeline (Zero Setup)

**Philosophy**: Value on day 1 with zero instrumentation

- `workflow-timeline.py`: Parse git log for instant timeline
- `workflow-glance.py`: 3-second terminal health check
- Git commits are telemetry source (no manual event capture needed)

### 2. Beta Foundation (Schema-Validated)

**Philosophy**: Simple but structured

- Event schema: `event-schema.json` validates all events
- JSONL format: Append-only, one event per line
- Ratchet baseline: Quality metrics stored in JSON

### 3. Stratified Timeline Layers

**Visualization approach**: Multiple perspectives on same timeline

| Layer | Shows | Color Coding |
|-------|-------|--------------|
| Commits | Git commits | feat=green, fix=red, docs=blue |
| Agents | Agent activity | By persona type |
| Decisions | Negative space | NO=red, NOT_YET=yellow |
| Health | Health pulse trend | Green/yellow/red bands |

### 4. Health Pulse Algorithm

**Composite Score (0-100)** from:

| Signal | Weight | Source |
|--------|--------|--------|
| Commit velocity | 25% | Git log (last 7 days) |
| Phase duration | 25% | Workflow state transitions |
| Agent collaboration | 20% | Agent handoffs in reports |
| Test coverage | 15% | dbt test pass rate |
| Documentation | 15% | Model description coverage |

**Thresholds**:

- 🟢 Excellent (80-100): Thriving workflow
- 🟡 Warning (60-79): Monitor closely
- 🔴 Critical (<60): Intervention needed

### 5. Negative Space Documentation

**Schema**: `temp/NEGATIVE_SPACE.yaml`

```yaml
decisions:
  - id: NS-001
    question: "Should we use vector embeddings for context search?"
    answer: "NOT_YET"
    rationale: "Premature optimization - file-based reports work fine"
    confidence: 85
    reconsider_trigger: "Agent reports exceed 50 per feature"
    decided_at: "2026-01-30"
```

**7 Decisions Documented** in initial implementation

### 6. Quality Ratchet

**Baseline Enforcement**: Metrics can only improve, never degrade

```json
{
  "as_of": "2026-01-30",
  "staging_model_count": 9,
  "total_test_count": 171,
  "documentation_coverage": 100
}
```

**Enforcement**: `check-ratchet.py` fails if current < baseline

## Research Process

### Competitive Ideation (5 Teams)

**Total Research**: 6,815 lines across 8 team documents

| Team | Focus Area | Key Contribution |
|------|------------|------------------|
| Alpha | Observability & Analytics | Development workflows as data pipelines |
| Beta | Learning & Improvement | Three-tier learning loops (short/medium/long) |
| Gamma | Standards & Quality | Standards Compliance Score with graduated enforcement |
| Delta | Context & Documentation | 30-Second Rule for context recovery |
| Epsilon | UX & Interaction | Time Machine Interface with progressive disclosure |

### Consensus Themes (All 5 Teams)

These themes appeared in 4-5 team proposals (considered essential):

1. Immutable history of state changes
2. Phase duration tracking
3. Pattern detection and learning
4. Decision rationale capture
5. Signal vs. noise filtering
6. Trend visualization

### Council Synthesis

**Document**: `temp/WORKFLOW_CHRONICLE_INDEX.md`
**Outcome**: Unified product concept "Workflow Chronicle"
**Tagline**: "Remember everything. Learn what matters."

## Scope

### In Scope

- Event log (JSONL format)
- Git-based timeline (zero instrumentation)
- Terminal health check (3-second glance)
- Health pulse scoring (0-100 composite)
- Context bootstrap generation (30-second resume)
- Visual timeline playground (stratified layers)
- Negative space decision tracking
- Quality ratchet enforcement
- Schema validation
- Context drift detection

### Out of Scope

- Machine learning / NLP for pattern detection (future)
- Real-time streaming events (batch processing sufficient)
- Multi-repository aggregation (single project focus)
- Cloud sync / collaboration features (local-first)
- Automated remediation (human-in-the-loop only)

## Success Metrics

| Metric | Target | Achieved |
|--------|--------|----------|
| Terminal tools performance | <3 seconds | ✅ workflow-glance completes in ~1s |
| Playground load time | <2 seconds | ✅ Loads instantly with cached data |
| Context recovery time | <30 seconds | ✅ Bootstrap provides immediate context |
| Documentation completeness | All scripts documented | ✅ Docstrings + README |
| Research → Implementation | 100% roadmap delivered | ✅ All 6 weeks complete |

## Dependencies

| Dependency | Status | Impact |
|------------|--------|--------|
| Python 3.11+ | ✅ Available | Required for PEP 723 scripts |
| uv package manager | ✅ Available | Script execution with inline deps |
| rich library | ✅ Available | Terminal UI formatting |
| Git repository | ✅ Available | Core telemetry source |
| WORKFLOW_STATE.md | ✅ Available | Primary state source |
| SESSION_SUMMARY files | ✅ Available | Context bootstrap input |

## Integration Points

### With Existing Systems

| System | Integration |
|--------|-------------|
| Workflow Hub | Chronicle data feeds into Hub visualizations |
| Workflow State | Primary data source for state transitions |
| Session Summaries | Input for context bootstrap generation |
| Git History | Core telemetry source (zero instrumentation) |
| dbt Project | Test counts and model metrics for ratchet |
| Agent Reports | Agent activity tracking in timeline |

## Key Decisions Made

| Decision | Rationale |
|----------|-----------|
| Git as telemetry source | Zero instrumentation, always available, durable |
| JSONL for event log | Append-only, line-oriented, easy to parse |
| Composite health score | Single number easier to grasp than dashboard |
| 30-second resume rule | Concrete target prevents context bloat |
| Human-in-the-loop learning | Avoid false patterns, maintain trust |
| Graduated enforcement | Inform first, block only when critical |
| Schema validation | Prevent garbage in event log |
| Negative space as first-class | Capture "why not" alongside "why" |

## Related

- **PR**: [#62 - feat(playgrounds): Workflow Chronicle + Playground Enhancements](https://github.com/cmbays/dbt-playground/pull/62)
- **Research Index**: `temp/WORKFLOW_CHRONICLE_INDEX.md`
- **Research Teams**: `temp/competitive-ideation-cycle-2/team-{1-8}/IDEAS.md`
- **Competitive Ideation Summary**: docs/for_chris/COMPETITIVE_IDEATION_CYCLES.md
- **Playground**: `playgrounds/workflow-chronicle.html`
- **Scripts**: `scripts/workflow-*.py`, `scripts/*-chronicle-*.py`, `scripts/check-*.py`
- **Foundation**: PRD-016 (Agent Context Management) - Session summaries
- **Related**: PRD-019 (Workflow Hub v0.7) - Chronicle data integration

## Future Enhancements

These were researched but deferred to future phases:

| Enhancement | Phase | Notes |
|-------------|-------|-------|
| ML-based pattern detection | v0.8+ | Requires sufficient historical data |
| Automated context compaction | v0.8+ | See PRD-019 architecture decisions |
| Multi-repository aggregation | v0.9+ | Portfolio-level analytics |
| Real-time event streaming | v0.9+ | WebSocket updates to playground |
| Predictive bottleneck detection | v1.0+ | Forecast phase duration based on history |

---

*PRD Status: Implemented - Retrospective documentation of merged feature*
*Implementation Date: 2026-01-30*
*Documentation Date: 2026-01-31*
*Research Lines: 6,815*
*Implementation Lines: 6,770*
