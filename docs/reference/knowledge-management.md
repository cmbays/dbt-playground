# Knowledge Management System

**Purpose**: Define how learnings, patterns, and documentation are organized across the project to prevent duplication and ensure discoverability.

**Applies to**: All agents creating or updating documentation

---

## Single-Source-of-Truth Hierarchy

To prevent knowledge duplication, follow this hierarchy when documenting patterns:

### Tier 1: Executable Skills (`.claude/skills/learned-pattern-*.md`)

**When**: Pattern is an actionable, repeatable workflow

**Contains**:
- Step-by-step process
- When to use criteria
- Expected outputs
- Examples

**Example**: `learned-pattern-agent-handoff.md`

### Tier 2: Technical Reference (`docs/reference/LEARNINGS.md`)

**When**: Pattern is a decision framework, best practice, or technical insight

**Contains**:
- Quick technical reference
- "When to apply" guidance
- Real examples from codebase
- Cross-references to skills and FOR_CHRIS docs

**Example**: "When to Create TDDs" decision framework

### Tier 3: Educational Narratives (`archive/FOR_CHRIS_docs/*.md`)

**When**: Pattern has high educational value and meets decision rubric (≥2 criteria)

**Contains**:
- Engaging, narrative explanations
- "Why" behind decisions
- Analogies and anecdotes
- Technical deep-dives with code examples
- Transferable meta-lessons

**Example**: `agent-orchestration-comparison.md`

### Decision Flow

```
1. Is the pattern an executable workflow?
   └─→ YES: Create skill (.claude/skills/learned-pattern-*.md)
       └─→ Add quick reference entry in LEARNINGS.md linking to skill
           └─→ If meets FOR_CHRIS rubric (≥2 criteria), create narrative doc

   └─→ NO: Is it a technical insight/decision framework?
       └─→ YES: Document in LEARNINGS.md
           └─→ If meets FOR_CHRIS rubric (≥2 criteria), create narrative doc

       └─→ NO: Is it a bug pattern?
           └─→ YES: Document in docs/TESTING.md#bug-learnings
               └─→ Link from LEARNINGS.md if broadly applicable

           └─→ NO: One-off learning, note in session digest only
```

---

## Cross-Referencing Guidelines

**Always link between tiers**:

- Skills → Link to from LEARNINGS.md
- LEARNINGS.md → Link to skills and FOR_CHRIS docs
- FOR_CHRIS docs → Link to LEARNINGS.md entries and skills

**Never duplicate content** - Use cross-references instead.

**Wiki-link format**:

```markdown
[[path/to/file.md]]           # Link to entire file
[[path/to/file.md#section]]   # Link to specific section
```

---

## When to Invoke Sage

Other personas should trigger Sage in these scenarios:

### Automatic Triggers

| Trigger | From Persona | Sage Action |
|---------|--------------|-------------|
| Version milestone complete | Documenter | Extract patterns from milestone work |
| Bug fixed with root cause | Tester | Document bug pattern for prevention |
| Workflow experiment complete | Developer | Evaluate if pattern is reusable |

### Manual Triggers

| Scenario | When to Invoke |
|----------|----------------|
| End of significant session | >5 files modified OR >50 lines changed |
| Pattern discovery | Same pattern observed ≥2 times |
| Educational documentation needed | Complex decision with high learning value |

### Invocation Examples

```
sage: Review this session and extract learnings
sage: Document the bug pattern from issue #42
sage: v0.4 is complete - create milestone learning documentation
```

---

## Learning Artifact Locations

### Files Created by Sage

| Artifact | Location | Purpose |
|----------|----------|---------|
| Learned Pattern Skills | `.claude/skills/learned-pattern-*.md` | Executable workflows |
| Technical Reference | `docs/reference/LEARNINGS.md` | Quick reference for patterns |
| Bug Patterns | `docs/TESTING.md#bug-learnings` | Prevention strategies |
| Educational Docs | `archive/FOR_CHRIS_docs/*.md` | Engaging narratives |
| FOR_CHRIS Index | `archive/FOR_CHRIS_docs/README.md` | Topic index |
| Learning Digests | `temp/LEARNING_DIGEST_[DATE].md` | Session summaries |

### Files Modified by Sage

| File | Updates |
|------|---------|
| `docs/reference/LEARNINGS.md` | Adds new patterns |
| `docs/TESTING.md` | Adds bug learnings |
| `archive/FOR_CHRIS_docs/README.md` | Updates index |

---

## Pattern Quality Bar

**All patterns must be**:

- **Proven ≥2 times** in real implementations (not theoretical)
- **Generalizable** beyond specific context
- **Actionable** with clear "when to apply" guidance
- **Documented with real examples** from this codebase

---

## Sage vs. Documenter

| Aspect | Sage | Documenter |
|--------|------|------------|
| Focus | Cross-session patterns | Version-specific facts |
| Trigger | Proactive pattern extraction | Reactive version updates |
| Artifacts | LEARNINGS.md, FOR_CHRIS docs, skills | CHANGELOG.md, living docs |
| Timing | After learnings proven | During/after version completion |

**Both run in parallel** after feature completion.

---

**Last Updated**: 2026-01-25
**Related Documentation**:

- `.claude/agents/sage.md` - Sage persona definition
- `docs/reference/LEARNINGS.md` - Technical patterns reference
- `archive/FOR_CHRIS_docs/README.md` - Educational docs index
