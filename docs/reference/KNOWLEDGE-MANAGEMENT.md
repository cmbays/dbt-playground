---
audience: [sage, multi-agent]
priority: medium
size: medium
last_updated: 2026-01-28
status: active
tags: [learning, knowledge, patterns, sage]
---

# Knowledge Management

**Purpose**: Cross-agent reference for how knowledge is captured, organized, and maintained in this project.

**Owner**: Sage persona

---

## Knowledge Hierarchy

Knowledge flows from session-specific to permanent, with increasing quality gates:

```
Session Work → LEARNINGS.md → Learned Skills → FOR_CHRIS docs
(temporary)    (proven ≥2x)   (executable)    (educational)
```

### Tier 1: Technical Patterns (`docs/reference/LEARNINGS.md`)

**Purpose**: Quick reference for proven patterns and decision frameworks

**Quality Bar**: Pattern must be proven in ≥2 real implementations

**Format**: Concise, actionable, with code examples

**When to Add**:

- Pattern used successfully in multiple features
- Decision framework that guides future choices
- Common pitfall with prevention strategy

### Tier 2: Learned Skills (`.claude/skills/learned-pattern-*.md`)

**Purpose**: Executable workflows extracted from proven patterns

**Quality Bar**: Workflow must be repeatable and self-contained

**Format**: Step-by-step instructions with clear inputs/outputs

**When to Add**:

- Workflow used ≥2 times with consistent success
- Process that other agents should follow
- Automation opportunity identified

### Tier 3: Educational Narratives (`docs/for_chris/*.md`)

**Purpose**: Deep-dive explanations for learning and future reference

**Quality Bar**: Must meet decision rubric (≥2 criteria)

**Format**: Engaging narrative with analogies and context

**When to Add** (Decision Rubric - need ≥2):

1. Significant architectural decision with trade-offs
2. Novel pattern not in existing resources
3. Workflow change affecting future development
4. Multiple approaches evaluated with clear winner
5. High educational value

---

## Single Source of Truth

Each type of knowledge has ONE authoritative location:

| Knowledge Type | Location | Owner |
|----------------|----------|-------|
| Technical Patterns | `docs/reference/LEARNINGS.md` | Sage |
| Executable Workflows | `.claude/skills/learned-pattern-*.md` | Sage |
| Educational Narratives | `docs/for_chris/*.md` | Sage |
| Bug Patterns | `docs/standards/TESTING.md#bug-learnings` | Tester/Sage |
| FOR_CHRIS Index | `docs/for_chris/README.md` | Sage |

---

## Cross-Reference Guidelines

**DO**:

- Link to authoritative source
- Reference specific sections/anchors
- Keep links up to date

**DON'T**:

- Duplicate content across documents
- Create parallel versions of same information
- Let documents drift out of sync

---

## Sage Workflows

### 1. Session Learning Curation

**Trigger**: End of significant session or milestone

**Process**:

1. Review session context and changes
2. Identify patterns worth capturing
3. Check if pattern already documented
4. Add to LEARNINGS.md if proven ≥2x
5. Create learned skill if workflow is repeatable
6. Create FOR_CHRIS doc if rubric met

### 2. Pattern Extraction

**Trigger**: Same approach used successfully ≥2 times

**Process**:

1. Document pattern in LEARNINGS.md
2. Extract executable workflow to learned skill
3. Cross-reference in both locations

### 3. Educational Documentation

**Trigger**: Decision rubric met (≥2 criteria)

**Process**:

1. Use FOR_CHRIS template
2. Write engaging narrative
3. Cross-reference technical docs
4. Update docs/for_chris/README.md index

---

## Related Documentation

- `.claude/agents/sage.md` - Sage persona definition
- `docs/reference/LEARNINGS.md` - Technical patterns
- `docs/for_chris/README.md` - Educational docs index
- `.claude/skills/learning-curation.md` - Curation workflow
- `.claude/templates/for-chris-doc-template.md` - FOR_CHRIS template
