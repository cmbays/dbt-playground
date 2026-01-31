# Council Command

Convene a council for consensus-based decision making.

## Usage

```
/council [feature] [--depth=quick|standard|deep]
```

## Description

The `/council` command convenes a fresh panel of decision-makers to review accumulated agent reports and produce a unified recommendation. This addresses tunnel vision from deep research and resolves conflicts between multiple agent findings.

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `feature` | Yes | Feature name matching folder in `temp/AGENT_REPORTS/` |

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--depth=quick` | | Single synthesizer, 1 turn, fast alignment check |
| `--depth=standard` | Yes | 3 perspectives (Pragmatist, Advocate, Skeptic), ~3 turns |
| `--depth=deep` | | 5 roles + moderator, structured debate, ~5+ turns |

## Examples

### Basic Usage

```
/council customer-analytics
```

Convenes standard council (3 perspectives) for the customer-analytics feature.

### Quick Synthesis

```
/council claims-connector --depth=quick
```

Fast single-pass synthesis when reports are already aligned.

### Deep Deliberation

```
/council data-warehouse-migration --depth=deep
```

Full panel with structured debate for high-stakes decisions.

### After Sage Research

```
sage: convene council for tuva-integration
```

Sage can invoke council to validate deep research findings.

## Workflow

```
                    ┌─────────────────────────────────┐
                    │     /council [feature]          │
                    └─────────────────────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │ Phase 1: CONVENE            │
                    │ - Find AGENT_REPORTS/[feat] │
                    │ - List available artifacts  │
                    │ - Determine depth           │
                    └─────────────┬───────────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         │                        │                        │
    ┌────┴────┐             ┌─────┴─────┐            ┌─────┴─────┐
    │  quick  │             │ standard  │            │   deep    │
    │ 1 role  │             │ 3 roles   │            │ 5 roles   │
    └────┬────┘             └─────┬─────┘            └─────┬─────┘
         │                        │                        │
         │              ┌─────────┼─────────┐              │
         │              │         │         │              │
         │         Pragmatist  Advocate  Skeptic      + Architect
         │              │         │         │         + Operator
         │              └─────────┼─────────┘         + Moderator
         │                        │                        │
         │                        │                        │
    ┌────┴────────────────────────┴────────────────────────┴────┐
    │                  Phase 2: REVIEW                          │
    │           Each role reads all artifacts fresh             │
    └───────────────────────────┬───────────────────────────────┘
                                │
    ┌───────────────────────────┴───────────────────────────────┐
    │                  Phase 3: DELIBERATE                      │
    │  - Present perspectives                                   │
    │  - Identify agreement/disagreement                        │
    │  - Build consensus or document dissent                    │
    └───────────────────────────┬───────────────────────────────┘
                                │
    ┌───────────────────────────┴───────────────────────────────┐
    │                  Phase 4: CONSENSUS                       │
    │  - Write recommendation + confidence                      │
    │  - Capture dissenting views                               │
    │  - Define next actions                                    │
    └───────────────────────────┬───────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │  COUNCIL_CONSENSUS.md │
                    │  written to feature   │
                    │  folder               │
                    └───────────────────────┘
```

## Council Roles

### Core (Standard Depth)

| Role | Focus | Key Question |
|------|-------|--------------|
| **Pragmatist** | Feasibility | "Can we actually do this?" |
| **Advocate** | Value | "What's the benefit?" |
| **Skeptic** | Risk | "What could go wrong?" |

### Extended (Deep Depth)

| Role | Focus | Key Question |
|------|-------|--------------|
| **Architect** | Technical coherence | "Does this fit our architecture?" |
| **Operator** | Maintenance burden | "Can we sustain this?" |

## Output Files

| Depth | Files Created |
|-------|---------------|
| quick | `COUNCIL_QUICK.md`, `COUNCIL_CONSENSUS.md` |
| standard | `COUNCIL_CONSENSUS.md` |
| deep | `COUNCIL_DEBATE.md`, `COUNCIL_CONSENSUS.md` |

All files written to: `temp/AGENT_REPORTS/[feature]/`

## Confidence Levels

The recommendation includes a confidence level:

| Level | Meaning | Next Action |
|-------|---------|-------------|
| **HIGH** | Strong consensus | Proceed to implementation |
| **MEDIUM** | Reasonable consensus | Proceed with monitoring |
| **LOW** | Weak consensus | Gather more information |

## Prerequisites

Before invoking `/council`:

- [ ] Feature folder exists: `temp/AGENT_REPORTS/[feature]/`
- [ ] At least one agent report exists (PM_REPORT, ARCH_REPORT, etc.)
- [ ] Reports contain substantive content for review

## Common Patterns

### Post-Research Validation

```
# After Sage completes deep research
sage: complete research, please convene council
/council [feature] --depth=standard
```

### Conflict Resolution

```
# When PM and Architect disagree
/council [feature]
# Council produces unified recommendation
```

### Pre-Architecture Decision

```
# Before committing to major change
/council data-model-v2 --depth=deep
# Full deliberation with all perspectives
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| "Feature folder not found" | No AGENT_REPORTS/[feature] | Create folder or check spelling |
| "No artifacts to review" | Empty folder | Add agent reports first |
| "Insufficient content" | Reports are stubs | Complete agent reports |

## Persona Integration

This command activates the **Council** skill with appropriate role composition based on depth.

May be invoked by:

- **User** via `/council` command
- **Sage** via `sage: convene council`
- **Supervisor** via auto-trigger (v0.8+)

## Skill Reference

See: `.claude/skills/council.md` for full skill documentation.

## Related Commands

| Command | Relationship |
|---------|--------------|
| `/plan` | Creates PRD that feeds council |
| `/tdd` | TDD may trigger council for validation |
| `/review` | Council may precede major reviews |
| `/orchestrate` | Supervisor may invoke council |

---

*Council provides structured consensus for high-stakes decisions.*
