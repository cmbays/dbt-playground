# TDD-HISTORICAL: Retrospective Architecture Decisions

**Purpose**: This document contains Architecture Decision Records (ADRs) that were reconstructed from v0.3-v0.6 development. These decisions were made and implemented but not formally recorded at the time.

**Note**: These ADRs are marked as "Approved (Historical)" to distinguish them from contemporary ADRs written during TDD authoring.

**Related**: See [ADR_INDEX.md](../reference/ADR_INDEX.md) for the full registry.

---

## ADR-6: PR-Centric Development Workflow

**Status**: Approved (Historical)

**Date**: 2026-01-30 (v0.5)

**Context**: The project needed better visibility into work-in-progress and a consistent way to preserve context across agent handoffs. Direct commits to main were causing issues:

1. Work was invisible until merged
2. No clear checkpoint for reviews
3. Context lost between sessions
4. Difficult to track parallel work streams

**Decision**: Adopt PR-centric development workflow where:

1. Draft PR is created immediately when starting any feature work
2. All multi-agent reviews are posted as GitHub PR comments
3. Post-review queue (docs, sage, pm) runs before merge
4. Supervisor performs final approval gate before merge authorization

**Rationale**:

| Approach | Visibility | Context Preservation | Review Quality |
|----------|------------|---------------------|----------------|
| Direct to main | None until merge | Lost on merge | Post-hoc only |
| PR-centric | Immediate | Preserved in PR | Inline feedback |

**Consequences**:

- **Positive**: All work visible in GitHub, reviews have permanent home, context survives sessions
- **Negative**: More ceremony for small changes, requires draft PR even for quick fixes
- **Mitigation**: Allow `--skip-pr` flag for trivial changes; draft PRs are low-friction

**Approval**: Architect + PM (2026-01-30)

**Implementations**:

- 10+ PRs merged using this workflow
- Agent personas updated (git-master, supervisor, code-reviewer, sage)
- `.claude/workflows/post-review-queue.md` created

---

## ADR-7: Single-File Playground Architecture

**Status**: Approved (Historical)

**Date**: 2026-01-31 (v0.6)

**Context**: The project needed interactive visual tools (playgrounds) for workflow management, diagram creation, and worktree coordination. Options considered:

1. **React/Vue SPA**: Full framework with build step
2. **Multi-file vanilla JS**: Separate HTML, CSS, JS files
3. **Single-file HTML**: Everything in one file, no build step

**Decision**: Build all playgrounds as single-file HTML with inline CSS and JavaScript.

**Rationale**:

| Approach | Complexity | Portability | Maintenance |
|----------|------------|-------------|-------------|
| React SPA | High (build, deps) | Low (needs server) | Medium |
| Multi-file vanilla | Medium | Medium | High (sync files) |
| Single-file HTML | Low | High (just open) | Low (one file) |

Key factors:

- Learning project - simplicity preferred over sophistication
- Tools are for developers, not end users
- CDN dependencies (Mermaid.js) handle heavy lifting
- No build step = instant iteration

**Consequences**:

- **Positive**: Zero setup, works offline (except CDN), easy to share, fast development
- **Negative**: Large files, no code splitting, limited reuse across playgrounds
- **Mitigation**: Extract common patterns to shared CSS/JS if files exceed 2000 lines

**Approval**: Architect (2026-01-31)

**Implementations**:

- `playgrounds/workflow-hub.html` (~800 lines)
- `playgrounds/worktree-coordinator.html` (~600 lines)
- `playgrounds/mermaid-designer.html` (~700 lines)
- `playgrounds/workflow-chronicle.html` (~1200 lines)

---

## ADR-8: Inter-Agent Report Pattern

**Status**: Approved (Historical)

**Date**: 2026-01-31 (v0.6)

**Context**: Multi-agent workflows were experiencing context loss during handoffs. Orchestrators (like Supervisor) were summarizing content between agents, leading to:

1. Context window overflow in orchestrator
2. Signal degradation - nuances lost in summarization
3. Information bottleneck - downstream agents get filtered view
4. Repeated context loading across agent invocations

**Decision**: Use shared artifact folders for agent communication:

```
temp/AGENT_REPORTS/[feature-name]/
├── PM_REPORT.md
├── ARCH_REPORT.md
├── TEST_SPEC.md
├── DEV_REPORT.md
├── CODE_REVIEW.md
└── SECURITY_REVIEW.md
```

Orchestrators pass file paths, not content. Downstream agents read upstream reports directly.

**Rationale**:

| Approach | Context Fidelity | Orchestrator Load | Audit Trail |
|----------|------------------|-------------------|-------------|
| Content relay | Low (summarized) | High | None |
| File paths | High (full docs) | Low | Permanent |

**Consequences**:

- **Positive**: Preserves signal fidelity, reduces orchestrator context, creates audit trail
- **Negative**: Requires temp/ directory structure, agents must read upstream before starting
- **Mitigation**: Templates in `docs/templates/agent-reports/` ensure consistency

**Approval**: Architect + PM (2026-01-31)

**Implementations**:

- PRD-016: Agent Context Management
- TDD-016: Technical design with report templates
- 5+ features tracked using inter-agent reports
- Documented in `.claude/agents/AGENTS.md`

---

*Created: 2026-01-31 | Author: Architect (Historical Reconstruction)*
