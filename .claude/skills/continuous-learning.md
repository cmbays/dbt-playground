# Continuous Learning

**Purpose**: Automatically extract reusable patterns from development sessions and save as learned skills.

**Owner**: Sage persona

**Invocation**: Triggered at end of sessions with pattern discovery, or manually via `sage:` prefix

---

## When to Use

- End of session with new patterns discovered
- After workflow experiments where multiple approaches were compared
- When same solution is applied successfully ≥2 times
- Pattern identified that could be reusable across features

**Do NOT use for**:
- One-off solutions
- Theoretical patterns (not yet proven)
- Patterns already documented elsewhere

---

## Prerequisites

**Required inputs**:
- Session notes (`temp/SESSION-*.md` files) OR conversation context
- Code examples showing pattern in practice
- Evidence of ≥2 successful uses (quality bar)

**Required knowledge**:
- Understanding of existing skills format (`.claude/skills/` directory)
- Familiarity with single-source-of-truth hierarchy
- Access to LEARNINGS.md and FOR_CHRIS doc templates

---

## Process

### Step 1: Review Session for Patterns

**Inputs**: Session notes, conversation history, code changes

**Actions**:
1. Read session notes or conversation transcript
2. Identify repeated approaches or solutions
3. Look for workflow improvements or discoveries
4. Note any "aha moments" or unexpected successes

**Questions to ask**:
- What did we do that worked well?
- Did we solve this problem before?
- Would this approach help in future scenarios?
- Is this specific to this feature or generalizable?

**Output**: List of candidate patterns

---

### Step 2: Validate Pattern Quality

**Quality bar**: Pattern must be proven in ≥2 real implementations (not theoretical)

**Validation checklist**:
- [ ] Pattern used successfully at least twice
- [ ] Pattern solved a real problem (not premature optimization)
- [ ] Pattern is generalizable (not overly specific)
- [ ] Pattern is actionable (clear steps)
- [ ] Pattern is not already documented

**Examples of invalid patterns**:
- ❌ "We should probably do X" (theoretical, not proven)
- ❌ Pattern used once (quality bar not met)
- ❌ Highly specific to one feature (not generalizable)

**Output**: Validated pattern ready for extraction OR rejection with reason

---

### Step 3: Determine Documentation Tier

**Single-source-of-truth hierarchy**:

1. **Is this an executable workflow?** (Repeatable process with clear steps)
   - **YES** → Create `.claude/skills/learned-pattern-[name].md`
   - **NO** → Continue to step 2

2. **Is this a technical insight/decision framework?**
   - **YES** → Document in `docs/reference/LEARNINGS.md` (skip skill creation)
   - **NO** → Continue to step 3

3. **Does this meet FOR_CHRIS doc rubric?** (≥2 criteria)
   - **YES** → Create `archive/FOR_CHRIS_docs/[topic].md`
   - **NO** → Document in LEARNINGS.md as best practice

**This skill focuses on tier 1 (executable workflows)**. For other tiers, use `learning-curation.md` skill.

**Output**: Decision on which tier to document in

---

### Step 4: Extract to Skill File

**Only if**: Pattern is executable workflow (tier 1)

**File naming**: `.claude/skills/learned-pattern-[descriptive-name].md`

**Examples**:
- `learned-pattern-temp-first-file-creation.md`
- `learned-pattern-parallel-review-execution.md`
- `learned-pattern-agent-handoff-protocol.md`

**Template structure**:
```markdown
# [Pattern Name]

**Purpose**: [What this pattern accomplishes]

**Owner**: Sage persona (extracted learning)

**Proven in**: [Version/feature where used]

---

## When to Use

[Triggers and contexts where this pattern applies]

**Do NOT use for**:
[Anti-patterns, when this is not appropriate]

---

## Prerequisites

[What you need before applying this pattern]

---

## Process

### Step 1: [First Step]

**Actions**:
1. Specific action
2. Specific action

**Output**: [What step produces]

### Step 2: [Second Step]

[Continue for all steps...]

---

## Expected Outcomes

[What success looks like]

---

## Examples

### Example 1: [Context]

[Concrete example from codebase showing pattern in use]

---

## Common Pitfalls

- Pitfall 1: Description and how to avoid
- Pitfall 2: Description and how to avoid

---

## See Also

- `docs/reference/LEARNINGS.md#[anchor]` - Quick reference
- `archive/FOR_CHRIS_docs/[topic].md` - Deep dive (if exists)
```

**Actions**:
1. Create new file using template above
2. Fill in all sections with specific details from pattern
3. Include concrete examples from codebase

**Output**: New skill file in `.claude/skills/`

---

### Step 5: Cross-Reference in LEARNINGS.md

**Why**: Maintain single-source-of-truth with cross-references

**Actions**:
1. Open `docs/reference/LEARNINGS.md`
2. Find appropriate section (Patterns/Frameworks/Pitfalls/Practices)
3. Add entry with link to new skill file

**Format**:
```markdown
#### Pattern: [Name]

**When to apply**: [Brief context]

**Proven in**: v0.X, v0.Y

**Description**: [1-2 sentence summary]

**See also**:
- Skill: `.claude/skills/learned-pattern-[name].md` - Full workflow
```

**Output**: Updated LEARNINGS.md with cross-reference

---

### Step 6: Update FOR_CHRIS Index (if applicable)

**Only if**: FOR_CHRIS doc was created (decision rubric met)

**Actions**:
1. Open `archive/FOR_CHRIS_docs/README.md`
2. Add entry to index table
3. Include topic, filename, date, key concepts

**Output**: Updated FOR_CHRIS index

---

## Expected Outcomes

**Primary outputs**:
- New skill file in `.claude/skills/learned-pattern-[name].md`
- Cross-reference entry in `docs/reference/LEARNINGS.md`
- Optional: FOR_CHRIS doc and index update

**Quality indicators**:
- ✅ Pattern is actionable (clear steps)
- ✅ Pattern is proven (≥2 real uses)
- ✅ Pattern is generalizable
- ✅ Examples are concrete
- ✅ Cross-references are complete

**Failure indicators**:
- ❌ Pattern is theoretical (not proven)
- ❌ Pattern is too specific (not reusable)
- ❌ Duplicates existing documentation
- ❌ Missing examples or context

---

## Examples

### Example 1: Temp-First File Creation Pattern

**Context**: Discovered during v0.1 content migration and v0.2 kanji data generation

**Validation**:
- ✅ Used successfully in both v0.1 and v0.2
- ✅ Prevented accidental overwrites
- ✅ Generalizable to any file creation

**Extraction**:
1. Created `.claude/skills/learned-pattern-temp-first-file-creation.md`
2. Documented step-by-step process
3. Included examples from both versions
4. Added cross-reference in LEARNINGS.md#file-operations

**Outcome**: Reusable workflow available for future file operations

---

### Example 2: Parallel Review Execution

**Context**: Discovered during v0.1 and v0.2 review phases

**Validation**:
- ✅ Used successfully in multiple reviews
- ✅ Reduced review time significantly
- ✅ Applicable to any multi-reviewer scenario

**Extraction**:
1. Created `.claude/skills/learned-pattern-parallel-review.md`
2. Documented conditions for parallel vs. sequential
3. Included timing benefits from real examples
4. Added cross-reference in LEARNINGS.md#agent-orchestration

**Outcome**: Reviewers know when to run in parallel vs. sequence

---

## Common Pitfalls

### Pitfall 1: Extracting Too Early

**Symptom**: Pattern documented after single use

**Why it's wrong**: Violates quality bar (≥2 proven uses)

**Solution**: Wait for second successful use before extracting. Note pattern as "candidate" in session digest.

---

### Pitfall 2: Creating Skill for Non-Workflow Pattern

**Symptom**: Skill file contains only insights, no actionable steps

**Why it's wrong**: Should be in LEARNINGS.md instead (wrong tier)

**Solution**: Check if pattern has executable steps. If not, document in LEARNINGS.md as decision framework or best practice.

---

### Pitfall 3: Duplicating Existing Documentation

**Symptom**: Content overlaps with existing skills or LEARNINGS entries

**Why it's wrong**: Violates single-source-of-truth principle

**Solution**: Before creating, search existing `.claude/skills/` and `docs/reference/LEARNINGS.md`. If similar exists, enhance that instead or add cross-reference.

---

### Pitfall 4: Missing Cross-References

**Symptom**: Skill created but not linked from LEARNINGS.md

**Why it's wrong**: Reduces discoverability, breaks hierarchy

**Solution**: Always complete Step 5 (cross-reference). Use checklist to verify.

---

## Checklist

Before completing this skill:

- [ ] Pattern proven in ≥2 real implementations
- [ ] Pattern is executable workflow (has clear steps)
- [ ] Skill file created with all sections filled
- [ ] Concrete examples from codebase included
- [ ] Cross-reference added to LEARNINGS.md
- [ ] No duplication with existing docs
- [ ] FOR_CHRIS index updated (if doc created)

---

## See Also

- `.claude/skills/learning-curation.md` - For non-skill learnings
- `docs/reference/LEARNINGS.md` - Technical patterns repository
- `.claude/templates/for-chris-doc-template.md` - Educational doc template
- `.claude/agents/sage.md` - Sage persona definition
