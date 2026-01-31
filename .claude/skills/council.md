---
name: council
tools: Read, Write, Glob
model: opus
description: Convene a fresh panel of decision-makers to review accumulated agent reports and produce a unified recommendation with captured dissent. Addresses tunnel vision from deep research and resolves conflicts between multiple agent findings.
agents:
  - supervisor
  - sage
triggers:
  - /council
  - "convene council"
  - "3+ conflicting agent reports"
  - "high-stakes decision"
  - "post-research validation"
---

# Council Deliberation Skill

Structured consensus decision-making through multi-perspective deliberation.

## Overview

The Council skill enables consensus-based decision making by convening a fresh panel of decision-makers to review accumulated artifacts and produce a unified recommendation. This addresses the "tunnel vision" problem where deep research or conflicting multi-agent findings require objective synthesis.

## When to Use

Invoke this skill when:

- Multiple agent reports exist with conflicting recommendations
- Deep research needs validation before becoming project learnings
- High-stakes decisions require structured deliberation
- Supervisor detects unresolved conflicts in AGENT_REPORTS
- User requests deliberation on a complex trade-off

## Prerequisites

- Agent reports exist in `temp/AGENT_REPORTS/[feature]/`
- At least one substantive document to review (PM_REPORT, ARCH_REPORT, etc.)
- Feature scope is defined (one feature per council session)

## Invocation Methods

| Method | Trigger | Use Case |
|--------|---------|----------|
| `/council [feature]` | Manual command | User-initiated deliberation |
| `sage: convene council` | Sage-initiated | Post-research validation |
| Auto-trigger (v0.8+) | Conditions met | Supervisor detects need |

## Depth Levels

### Quick (`--depth=quick`)

Single-pass synthesis for straightforward decisions.

| Aspect | Value |
|--------|-------|
| **Council Size** | 1 synthesizer |
| **Process** | Read all reports, summarize consensus and gaps |
| **Duration** | ~1 turn |
| **Output** | `COUNCIL_QUICK.md` + `COUNCIL_CONSENSUS.md` |
| **When to use** | Status check, low-stakes decisions, clear alignment |

### Standard (`--depth=standard`) [Default]

Three-perspective analysis for typical decisions.

| Aspect | Value |
|--------|-------|
| **Council Size** | 3 roles (Pragmatist, Advocate, Skeptic) |
| **Process** | Parallel analysis, then consensus building |
| **Duration** | ~3 turns |
| **Output** | `COUNCIL_CONSENSUS.md` |
| **When to use** | Feature decisions, architecture choices, prioritization |

### Deep (`--depth=deep`)

Full deliberation with structured debate for high-stakes decisions.

| Aspect | Value |
|--------|-------|
| **Council Size** | 5 roles + moderator |
| **Process** | Individual analysis, structured debate, voting |
| **Duration** | ~5+ turns |
| **Output** | `COUNCIL_DEBATE.md` + `COUNCIL_CONSENSUS.md` |
| **When to use** | Architecture decisions, security concerns, irreversible choices |

## Council Roles

### Core Roles (Standard Depth)

| Role | Focus | Key Question | Bias |
|------|-------|--------------|------|
| **Pragmatist** | Feasibility | "Can we actually do this?" | Execution reality |
| **Advocate** | Value | "What's the benefit?" | User/business value |
| **Skeptic** | Risk | "What could go wrong?" | Potential failures |

### Extended Roles (Deep Depth)

| Role | Focus | Key Question | Bias |
|------|-------|--------------|------|
| **Architect** | Technical coherence | "Does this fit our architecture?" | System integrity |
| **Operator** | Maintenance burden | "Can we sustain this?" | Long-term cost |

### Role Guidelines

Each role must:

1. **Start fresh** - No prior session context, only provided artifacts
2. **Stay in character** - Focus on their assigned question
3. **Cite evidence** - Reference specific sections of reviewed reports
4. **Acknowledge uncertainty** - Note gaps in available information
5. **Propose, don't dictate** - Contribute perspective, not final decision

## Process

### Phase 1: Convene

1. Identify feature folder: `temp/AGENT_REPORTS/[feature]/`
2. List all available artifacts (`*.md` files)
3. Determine appropriate depth (default: standard)
4. Announce council composition

### Phase 2: Review

Each role independently reviews:

- All agent reports in the feature folder
- Related documentation (PRD, TDD if referenced)
- No access to prior session context

### Phase 3: Deliberate

**Quick depth**: Single synthesizer summarizes findings

**Standard depth**:

1. Each role presents their perspective (2-3 key points)
2. Identify areas of agreement
3. Surface disagreements explicitly
4. Propose resolution or document dissent

**Deep depth**:

1. Each role presents full analysis
2. Moderator facilitates structured debate
3. Roles respond to challenges
4. Formal voting on recommendation
5. Minority views captured in full

### Phase 4: Consensus

Generate `COUNCIL_CONSENSUS.md` with:

- Clear recommendation with confidence level
- Points where all roles agreed
- Trade-offs table
- Dissenting views (never suppressed)
- Concrete next actions

## Consensus Report Structure

Output: `temp/AGENT_REPORTS/[feature]/COUNCIL_CONSENSUS.md`

```markdown
# Council Consensus: [Feature/Decision Name]

**Convened**: YYYY-MM-DD HH:MM
**Depth**: quick | standard | deep
**Participants**: [Role list]

## Recommendation

[Clear recommendation]

**Confidence**: HIGH | MEDIUM | LOW

**Rationale**: [1-2 sentences on why this confidence level]

## Points of Consensus

1. [Point all roles agreed on]
2. [Another consensus point]
3. [Third consensus point]

## Key Trade-offs

| Option | Benefit | Cost |
|--------|---------|------|
| [A] | [benefit] | [cost] |
| [B] | [benefit] | [cost] |

## Dissenting Views

### [Role Name] Dissent

[Full dissent with reasoning - never summarized away]

### [Role Name] Concerns

[Concerns that didn't rise to dissent but should be noted]

## Next Actions

1. [ ] [Specific action with owner if known]
2. [ ] [Another action]
3. [ ] [Third action]

## Evidence Reviewed

- **PM_REPORT.md**: [What was considered from this report]
- **ARCH_REPORT.md**: [What was considered from this report]
- **[Other reports]**: [Summary of consideration]

---

*Council convened via /council skill*
```

## Confidence Levels

| Level | Meaning | When to Use |
|-------|---------|-------------|
| **HIGH** | Strong consensus, proceed confidently | All roles agree, evidence is clear |
| **MEDIUM** | Reasonable consensus, proceed with monitoring | Most roles agree, some uncertainty |
| **LOW** | Weak consensus, gather more information | Significant dissent, evidence gaps |

## Handoff Protocol

### Input

Council receives:

- Feature name (required)
- Depth level (optional, default: standard)
- Path to AGENT_REPORTS folder (derived from feature name)

### Output

Council writes:

- `COUNCIL_CONSENSUS.md` (always)
- `COUNCIL_QUICK.md` (quick depth only - synthesis notes)
- `COUNCIL_DEBATE.md` (deep depth only - debate transcript)

### Next Persona

| Confidence | Next Action |
|------------|-------------|
| HIGH | Proceed to implementation via appropriate persona |
| MEDIUM | Proceed with supervisor monitoring |
| LOW | Return to Sage for additional research |

## Integration

### With Supervisor

Supervisor may:

- Auto-trigger council when detecting 3+ conflicting reports
- Route council output to appropriate next persona
- Track council recommendations for retrospective validation

### With Sage

Sage may:

- Invoke council after deep research for validation
- Provide additional context if council requests it
- Receive council output for learning capture

### With Feature Workflow

Council integrates into the standard agent report flow:

```
PM_REPORT.md
ARCH_REPORT.md     →  /council [feature]  →  COUNCIL_CONSENSUS.md
TEST_SPEC.md                                        ↓
DEV_REPORT.md                              Implementation proceeds
```

## Examples

### Quick Synthesis

```
/council customer-analytics --depth=quick

Reading temp/AGENT_REPORTS/customer-analytics/...
Found: PM_REPORT.md, ARCH_REPORT.md

[Quick Council - Single Synthesizer]

Summary: PM and Architect agree on scope. No conflicts detected.
Confidence: HIGH
Recommendation: Proceed to TDD creation.
```

### Standard Deliberation

```
/council claims-connector

Reading temp/AGENT_REPORTS/claims-connector/...
Found: PM_REPORT.md, ARCH_REPORT.md, SECURITY_REVIEW.md

[Standard Council - Pragmatist, Advocate, Skeptic]

Pragmatist: Implementation is feasible but requires 3rd party API.
Advocate: User value is clear - addresses top feature request.
Skeptic: Security review flagged authentication concerns.

Consensus: Proceed with enhanced auth review.
Confidence: MEDIUM
Dissent: Skeptic recommends deferring until auth pattern established.
```

### Deep Deliberation

```
/council data-warehouse-migration --depth=deep

Reading temp/AGENT_REPORTS/data-warehouse-migration/...
Found: PM_REPORT.md, ARCH_REPORT.md, SECURITY_REVIEW.md,
       COST_ANALYSIS.md, VENDOR_COMPARISON.md

[Deep Council - Full Panel + Moderator]

[Extended debate transcript in COUNCIL_DEBATE.md]

Final Vote:
- Pragmatist: Proceed with Vendor A
- Advocate: Proceed with Vendor A
- Skeptic: Defer 6 months
- Architect: Proceed with Vendor A
- Operator: Proceed with Vendor B (maintenance concern)

Consensus: Proceed with Vendor A
Confidence: MEDIUM
Dissent: Skeptic (timing), Operator (maintenance)
```

## Anti-Patterns

### What Council Should NOT Do

- **Rubber-stamp**: Council must genuinely deliberate, not just approve
- **Suppress dissent**: All disagreements must be captured in full
- **Rely on prior context**: Roles must be fresh, using only provided artifacts
- **Extend scope**: Council reviews, does not add new requirements
- **Vote mechanically**: Deliberation is the goal, not vote counting

### When NOT to Use Council

- Trivial decisions with no trade-offs
- Urgent fixes where speed matters more than consensus
- Single-source decisions (only one report exists)
- Already-committed decisions (council is for deciding, not justifying)

## Exit Criteria

Council complete when:

- [ ] All artifacts in feature folder reviewed
- [ ] Each role has contributed perspective
- [ ] Recommendation stated with confidence level
- [ ] Dissenting views captured in full
- [ ] Next actions are concrete and actionable
- [ ] COUNCIL_CONSENSUS.md written to feature folder

---

## Related Documentation

- [[../commands/council.md]] - Command reference
- [[../../docs/specs/PRD-018-COUNCIL-SKILL.md]] - Product requirements
- [[../agents/AGENTS.md]] - Agent orchestration
- [[../agents/sage.md]] - Sage integration
- [[../agents/supervisor.md]] - Supervisor integration
- [[../../docs/templates/agent-reports/]] - Report templates
