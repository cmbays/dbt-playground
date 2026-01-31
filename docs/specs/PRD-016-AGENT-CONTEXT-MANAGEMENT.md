# PRD-016: Agent Context Management Enhancements

## Overview

**Author**: Claude Code Agent System (PM Persona)
**Status**: Implemented (v0.6.0)
**Created**: 2026-01-30
**Updated**: 2026-01-30

### Problem Statement

Multi-agent workflows suffer from context inefficiency and signal loss:

1. **Orchestrator Bottleneck**: Supervisor relays summarized content between agents, causing signal degradation and context window overflow
2. **Session Discontinuity**: No standardized format for resuming work across sessions; agents lose context on reconnection
3. **Agent Knowledge Fragmentation**: 20+ agent files, 23 skill files, 16 command files create cognitive overhead (~51,000 tokens of potential context)
4. **Learning Accessibility**: Agent system is powerful but opaque to the human learner (Chris)

These problems were validated by external research (Claudie blog post) showing similar failures in their v1 and v2 architectures before arriving at a shared-artifact solution.

### Goal

Establish efficient context management patterns that:

- Enable direct agent-to-agent communication via shared artifacts
- Provide quick session resume capability for cross-session work
- Make agent roles accessible and understandable for learning
- Lay groundwork for future knowledge consolidation

### Reference

- Evaluation Report: `temp/CLAUDE-MEM-EVALUATION.md`
- Source: "How We Built an AI Project Manager Using Claude Code" (Claudie blog post)

## User Stories

As a **Supervisor**, I want sub-agents to write reports to a shared folder so that I can pass file locations instead of summarized content, preserving signal fidelity.

As a **downstream agent**, I want to read upstream agent reports directly so that I receive full context without orchestrator relay losses.

As a **cross-session agent**, I want a standardized session summary so that I can quickly resume work without re-reading all context.

As a **human learner (Chris)**, I want human-readable job descriptions for each agent so that I understand what each role does in plain language.

As a **knowledge curator**, I want validated patterns documented in LEARNINGS.md so that proven approaches are preserved for future use.

As a **future maintainer**, I want to understand the trade-offs in agent knowledge architecture so that I can make informed consolidation decisions.

## Requirements

### Milestone v0.6: Core Context Patterns

#### FR-1: Inter-Agent Reports Structure

Create standardized report structure at `temp/AGENT_REPORTS/[feature]/`:

| Report | Agent | Purpose |
|--------|-------|---------|
| `PM_REPORT.md` | PM | PRD summary, scope decisions, acceptance criteria |
| `ARCH_REPORT.md` | Architect | Design decisions, trade-offs, integration points |
| `TEST_SPEC.md` | Tester | Test plan, coverage targets, test commands |
| `DEV_REPORT.md` | Developer | Implementation notes, blockers resolved, files changed |
| `CODE_REVIEW.md` | Code Reviewer | Review findings, approval status |
| `SECURITY_REVIEW.md` | Security Reviewer | Security findings, risk assessment |

**Acceptance Criteria**:

- [ ] Directory structure documented in CLAUDE.md
- [ ] Each agent persona updated with report output instructions
- [ ] Supervisor updated to pass file locations, not content summaries
- [ ] Downstream agents instructed to read upstream reports directly
- [ ] Template created for each report type

#### FR-2: Session Summaries

Create timestamped session summaries at `temp/SESSION_SUMMARY_YYYY-MM-DD.md`:

```markdown
# Session Summary: YYYY-MM-DD

## Quick Resume
- **Active Track**: [feature branch name]
- **Last Action**: [what was completed]
- **Next Action**: [what should happen next]

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| [decision] | [why] |

## Open Questions
- [question 1]
- [question 2]

## Agent Reports Generated
- [list of reports created this session]

## Blockers
- [any blockers for next session]
```

**Acceptance Criteria**:

- [ ] Session summary template documented
- [ ] Supervisor creates session summary at session end (explicit trigger)
- [ ] Quick Resume section enables 30-second context recovery
- [ ] Format integrates with existing WORKFLOW_STATE.md

#### FR-3: Job Description Documentation

Create `docs/for_chris/AGENT_JOB_DESCRIPTIONS.md`:

| Agent | Human Job Title | One-Line Description |
|-------|-----------------|----------------------|
| supervisor | Project Coordinator | Makes sure nothing falls through the cracks between sessions |
| sage | Knowledge Librarian | Remembers what worked so we don't reinvent the wheel |
| git-master | Release Manager | Guards the codebase - no one commits without approval |
| pm | Product Manager | Defines what to build and why it matters |
| architect | Technical Architect | Designs how pieces fit together |
| dbt-developer | Data Engineer | Writes the SQL that transforms data |
| dbt-tester | QA Engineer | Makes sure the data is correct and complete |
| code-reviewer | Code Reviewer | Catches bugs and ensures code quality |
| security-reviewer | Security Analyst | Identifies vulnerabilities and risks |
| documenter | Technical Writer | Keeps documentation current and clear |
| data-modeler | Data Modeler | Designs the structure of dimensional models |
| explorer | Research Analyst | Investigates new tools and approaches |

**Acceptance Criteria**:

- [ ] Job descriptions written in plain language (no jargon)
- [ ] Each role has clear responsibility boundaries
- [ ] Document explains when to invoke each agent
- [ ] Includes examples of typical agent prompts

#### FR-4: LEARNINGS.md Pattern Entry

Add "Context Window Discipline for Multi-Agent Workflows" to `docs/reference/LEARNINGS.md`:

**Pattern Summary**:

- Orchestrators should pass file pointers, not content summaries
- Sub-agents write to shared temp folder; downstream agents read directly
- Prevents context overflow and preserves signal fidelity

**Validated By**:

- Claudie blog post (external validation)
- Our existing "Context Loss in Agent Handoffs" pattern (internal pattern)

**Acceptance Criteria**:

- [ ] Pattern documented with problem/solution/evidence structure
- [ ] References both external (Claudie) and internal validation
- [ ] Includes code/workflow examples
- [ ] Tagged with category (agent-orchestration)

#### FR-5: Agent Knowledge Consolidation FOR_CHRIS Doc

Create `docs/for_chris/AGENT-KNOWLEDGE-CONSOLIDATION.md`:

Content outline:

1. The Problem: Knowledge fragmentation across 51+ files
2. Case Study: Claudie's v1->v2->v3 evolution
3. Trade-offs: Fragmented vs. Consolidated knowledge
4. Our Current Architecture and why it works for now
5. Signs it's time to consolidate
6. Potential consolidation strategies

**Acceptance Criteria**:

- [ ] Explains trade-offs in accessible language
- [ ] Uses Claudie evolution as teaching example
- [ ] Provides decision criteria for when to consolidate
- [ ] Relates to our 20+ agent file architecture

### Milestone v0.7+: Handbook Consolidation Evaluation

#### FR-6: Consolidation Feasibility Study

Evaluate consolidating agent knowledge into tiered handbook structure:

**Current State**:

- 20+ agent files
- 23 skill files
- 16 command files
- ~51,000 tokens potential context

**Proposed Structure**:

```
.claude/
  handbook/
    FOUNDATION.md      # Always loaded (core workflow, rules)
    DBT_LAYER.md       # dbt-specific operations
    REVIEW_LAYER.md    # Review and quality operations
    ORCHESTRATION.md   # Supervisor and coordination
  personas/            # Minimal persona deltas only
```

**Evaluation Criteria**:

- Context window efficiency gains
- Maintenance overhead impact
- Agent specialization preservation
- Migration effort estimate

**Acceptance Criteria**:

- [ ] Evaluation document created with metrics
- [ ] Current token counts measured
- [ ] Proposed structure mapped to existing content
- [ ] Go/no-go recommendation with rationale

### Milestone v1.0+: Advanced Features

#### FR-7: Vector Search Over LEARNINGS.md

When LEARNINGS.md exceeds ~3000 lines, implement semantic search:

**Options**:

1. Simple embedding-based search over markdown
2. Standalone vector DB (not full claude-mem dependency)
3. Custom MCP server for semantic search

**Acceptance Criteria**:

- [ ] Trigger condition defined (line count threshold)
- [ ] Implementation approach selected
- [ ] Standalone solution (no external plugin dependency)
- [ ] Natural language query support

### Non-Functional Requirements

1. **NFR-1**: Inter-agent reports must be human-readable (not just machine-parseable)
2. **NFR-2**: Session summaries must enable <60 second context recovery
3. **NFR-3**: Documentation must be accessible to dbt-learning audience
4. **NFR-4**: No external plugin dependencies (build in-house)
5. **NFR-5**: Backward compatible with existing WORKFLOW_STATE.md

## Scope

### In Scope

**v0.6**:

- temp/AGENT_REPORTS/ directory structure and templates
- Session summary format and creation workflow
- Agent job descriptions document
- LEARNINGS.md pattern entry
- FOR_CHRIS consolidation document

**v0.7+**:

- Handbook consolidation evaluation
- Token counting and efficiency analysis

**v1.0+**:

- Vector search implementation (when triggered)

### Out of Scope

- Claude-mem plugin installation (conflicts with CLAUDE.md)
- Automatic session summary generation (explicit trigger only)
- Privacy tags (private repo makes unnecessary)
- External vector DB services
- Changes to core agent behavior (focus on artifacts)

## Dependencies

- Existing agent persona files (to be updated with report instructions)
- WORKFLOW_STATE.md (session summaries integrate with, not replace)
- docs/for_chris/ directory structure
- LEARNINGS.md file

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Context recovery time | <60 seconds | Time to resume work with session summary |
| Agent report adoption | 100% of features | AGENT_REPORTS directory created per feature |
| Signal preservation | Qualitative | Downstream agents receive full context |
| Learning accessibility | 3+ FOR_CHRIS docs | Documents created for human learner |

## Implementation Priority

| Priority | Feature | Effort | Impact | Version |
|----------|---------|--------|--------|---------|
| 1 | temp/AGENT_REPORTS/ structure | Low | High | v0.6 |
| 2 | Session summary format | Low | High | v0.6 |
| 3 | Job description docs | Low | Medium | v0.6 |
| 4 | LEARNINGS.md pattern entry | Low | Medium | v0.6 |
| 5 | FOR_CHRIS consolidation doc | Medium | Medium | v0.6 |
| 6 | Handbook consolidation eval | High | High | v0.7+ |
| 7 | Vector search | Medium | Medium | v1.0+ |

## Open Questions

1. Should session summaries be auto-generated at session end, or explicitly triggered by user?
   - **Recommendation**: Explicit trigger to avoid noise
2. What is the retention policy for AGENT_REPORTS? Keep forever or clean after merge?
   - **Recommendation**: Clean after merge (preserved in git history via PR)
3. Should handbook consolidation preserve all agent files or truly merge?
   - **Deferred**: Evaluate in v0.7+

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Report location | temp/AGENT_REPORTS/ | Aligns with existing temp/ usage; auto-cleaned |
| Session summary trigger | Explicit | Avoids noise; user controls when to checkpoint |
| Skip claude-mem | Build in-house | CLAUDE.md conflict; simpler to maintain |
| Skip privacy tags | Not needed | Private repo makes them unnecessary |
| Defer consolidation | v0.7+ | Not hitting pain points yet; need validation |

## Related

- **Evaluation**: `temp/CLAUDE-MEM-EVALUATION.md`
- **Workflow State**: `temp/WORKFLOW_STATE.md`
- **Agent System**: `.claude/agents/AGENTS.md`
- **For Chris Docs**: `docs/for_chris/`
- **LEARNINGS**: `docs/reference/LEARNINGS.md`
