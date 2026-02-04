# Design Audit Skill

## Purpose

Invoke a systematic design review using the 15-point audit protocol and Jobs filter. This skill triggers the design-reviewer agent to evaluate UI implementations against FRONTEND_GUIDELINES.md and produce a phased improvement plan.

## Usage

```
/design-audit [target]
```

Where `[target]` is:
- A playground name (e.g., `learning-playground`)
- A specific component or file path
- Omitted to audit the current context

## Examples

```
/design-audit learning-playground
/design-audit playgrounds/workflow-hub.html
/design-audit  # Audit whatever is currently being discussed
```

## What Happens

1. **Load Required Context**
   - Read FRONTEND_GUIDELINES.md for design tokens and standards
   - Read APP_FLOW_STANDARD.md for journey expectations
   - Read PLAYGROUND_AUDIT_PROTOCOL.md for checklist
   - Read the target's APP_FLOW (if exists)

2. **Run 15-Point Audit**
   Systematically evaluate:
   - Visual hierarchy, spacing, typography, color, alignment
   - Component consistency, iconography, motion
   - Empty, loading, and error states
   - Dark mode, density, responsiveness, accessibility

3. **Apply Jobs Filter**
   For every element, ask:
   - Would a user need to be told this exists?
   - Can this be removed without losing meaning?
   - Does this feel inevitable?
   - Is every detail as refined as details users never see?

4. **Produce Phased Plan**
   - Phase 1 — Critical: Issues that actively hurt the experience
   - Phase 2 — Refinement: Adjustments that elevate
   - Phase 3 — Polish: Micro-details that make it premium

## Output Format

```markdown
## Design Review: [Target Name]

### Overall Assessment
[1-2 sentences on current state]

### Audit Results
| # | Dimension | Score | Notes |
|---|-----------|-------|-------|
| 1 | Visual Hierarchy | ✅/⚠️/❌ | ... |
...

### Phase 1 — Critical
- [Component]: [What's wrong] → [What it should be] → [Why]

### Phase 2 — Refinement
...

### Phase 3 — Polish
...

### FRONTEND_GUIDELINES Updates Required
- [Any new tokens needed]

### Implementation Notes
- [Exact file, property, old value → new value]

### What's Good
- [Preserve these]

### Verdict
- [ ] Approved
- [ ] Approved with polish suggestions
- [ ] Changes requested
```

## Agent Delegation

This skill delegates to the **design-reviewer** agent:

```
design: audit [target] against FRONTEND_GUIDELINES.md
```

The design-reviewer has read-only access (Read, Grep, Glob) and produces recommendations without making code changes.

## Related

- [FRONTEND_GUIDELINES.md](../../docs/reference/FRONTEND_GUIDELINES.md) - Design system
- [APP_FLOW_STANDARD.md](../../docs/standards/APP_FLOW_STANDARD.md) - Journey template
- [PLAYGROUND_AUDIT_PROTOCOL.md](../../docs/standards/PLAYGROUND_AUDIT_PROTOCOL.md) - Checklist
- [design-reviewer.md](../agents/design-reviewer.md) - Agent definition
