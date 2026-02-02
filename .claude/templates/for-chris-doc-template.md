# [Topic Title]

<!--
Template for topic-specific FOR_CHRIS educational documents.
Use this template when creating new FOR_CHRIS docs in docs/for_chris/

Decision Rubric: Create FOR_CHRIS doc only if ≥2 criteria met:
1. Significant architectural decision made with trade-offs evaluated
2. Novel pattern not found in existing documentation or resources
3. Workflow changed that affects future development approach
4. Multiple approaches evaluated with clear winner and rationale
5. High educational value for Christopher's stated learning goals

File Naming: [topic-description].md (e.g., kanji-module-architecture.md)
-->

**Date Created**: YYYY-MM-DD
**Version**: vX.Y
**Decision Rubric Criteria Met**: [List which criteria from above]

---

## What We Built

[Executive summary - 2-3 sentences of what was accomplished]

**Key Outcomes:**

- Outcome 1
- Outcome 2
- Outcome 3

**Related Files:**

- `path/to/file1`
- `path/to/file2`

---

## Why We Built It This Way

[Architectural decisions, alternatives considered, trade-offs evaluated]

### Problem We Were Solving

[Context: What challenge did we face? What were the requirements?]

### Approaches Considered

**Option 1: [Approach Name]**

- **Pros**:
- **Cons**:
- **Decision**: Rejected/Chosen because...

**Option 2: [Approach Name]**

- **Pros**:
- **Cons**:
- **Decision**: Rejected/Chosen because...

### Final Decision

[Why we chose this approach. What trade-offs did we accept?]

**Decision Criteria:**

- Criterion 1 and why it mattered
- Criterion 2 and why it mattered

---

## How It Works

[Technical deep-dive with code examples]
[Engaging explanations using analogies where appropriate]

### High-Level Architecture

[Diagram or description of system structure]

```
[Visual representation or ASCII diagram if helpful]
```

### Key Components

**Component 1: [Name]**

- **Purpose**: What it does
- **Implementation**: How it works
- **Example**:

  ```javascript
  // Code example showing usage
  ```

**Component 2: [Name]**

- **Purpose**: What it does
- **Implementation**: How it works
- **Example**:

  ```javascript
  // Code example showing usage
  ```

### Data Flow

[Step-by-step walkthrough of how data/control flows through the system]

1. Step 1: What happens
2. Step 2: What happens
3. Step 3: What happens

**Analogy**: [Helpful real-world comparison to make this more intuitive]

---

## What I Learned

[Transferable lessons and meta-patterns]
[What would you do differently? What worked well?]

### Technical Lessons

1. **Lesson 1: [Title]**
   - **What we learned**: Insight gained
   - **Why it matters**: Broader applicability
   - **Apply when**: Future scenarios where this applies

2. **Lesson 2: [Title]**
   - **What we learned**: Insight gained
   - **Why it matters**: Broader applicability
   - **Apply when**: Future scenarios where this applies

### Process Lessons

- **What worked well**: Approaches that succeeded
- **What we'd do differently**: Improvements for next time
- **Time/effort observations**: Was it worth it? More/less complex than expected?

### Meta-Patterns

[Higher-level patterns that apply beyond this specific implementation]

- Pattern 1: General principle extracted
- Pattern 2: General principle extracted

---

## Gotchas & Pitfalls

[Common mistakes and how to avoid them]
[Edge cases discovered during implementation]

### Pitfall 1: [Description]

**What went wrong**: [The mistake we made or almost made]

**Why it's tricky**: [What makes this non-obvious]

**How to avoid**: [The correct approach]

**Code example**:

```javascript
// WRONG approach
// ...

// CORRECT approach
// ...
```

### Pitfall 2: [Description]

**What went wrong**: [The mistake we made or almost made]

**Why it's tricky**: [What makes this non-obvious]

**How to avoid**: [The correct approach]

### Edge Cases to Watch

- Edge case 1: Description and handling
- Edge case 2: Description and handling

---

## Further Reading

### Internal Documentation

**LEARNINGS.md entries:**

- [Pattern Name](../docs/reference/LEARNINGS.md#pattern-anchor) - Quick reference
- [Another Pattern](../docs/reference/LEARNINGS.md#another-anchor) - Quick reference

**Extracted Skills:**

- [`.claude/skills/learned-pattern-[name].md`](../.claude/skills/learned-pattern-name.md) - Executable workflow
- [`.claude/skills/learned-pattern-[name2].md`](../.claude/skills/learned-pattern-name2.md) - Executable workflow

**Related FOR_CHRIS docs:**

- [Related Topic](./related-topic.md) - Background context
- [Another Topic](./another-topic.md) - Related architecture

### External Resources

- [Resource Title](URL) - Why this is helpful
- [Resource Title](URL) - Why this is helpful

---

## Appendix: Code Snippets

[Optional: Additional code examples that are useful but too detailed for main sections]

### Snippet 1: [Purpose]

```javascript
// Complete example
```

### Snippet 2: [Purpose]

```javascript
// Complete example
```

---

## Update History

| Date | Version | Changes |
|------|---------|---------|
| YYYY-MM-DD | vX.Y | Initial creation |
| YYYY-MM-DD | vX.Z | Updates made (brief description) |

---

**Remember**:

- Cross-reference, don't duplicate (link to LEARNINGS.md and skills)
- Engaging tone, use analogies
- Explain "why", not just "what"
- Concrete examples from this codebase
- Standalone and complete
