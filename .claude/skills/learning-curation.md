# Learning Curation

**Purpose**: Curate session learnings into appropriate repositories (LEARNINGS.md, FOR_CHRIS docs, skills, bug patterns).

**Owner**: Sage persona

**Invocation**: End of significant sessions, after major feature completion, or when session notes accumulate

---

## When to Use

- End of significant session with multiple learnings
- After major feature completion (version milestone)
- When `temp/SESSION-*.md` files accumulate (≥3 uncurated sessions)
- Bug fixed with valuable root cause analysis

**Do NOT use for**:

- Trivial sessions (<3 files modified)
- Sessions with no reusable learnings
- When learnings already curated in real-time

---

## Prerequisites

**Required inputs**:

- Session notes (`temp/SESSION-*.md`) OR conversation context
- Understanding of what was accomplished
- Access to codebase/documentation changes

**Required knowledge**:

- Single-source-of-truth hierarchy (Skills > LEARNINGS > FOR_CHRIS)
- FOR_CHRIS doc decision rubric (≥2 criteria)
- Quality bar for patterns (≥2 proven uses)

---

## Process

### Step 1: Read Session Notes and Conversation

**Inputs**: Session notes files, conversation history

**Actions**:

1. List all `temp/SESSION-*.md` files: `ls temp/SESSION-*.md`
2. Read each uncurated session note
3. Review conversation context if session notes incomplete
4. Identify session scope: What was accomplished? What was tried?

**Questions to guide**:

- What was the main accomplishment?
- What challenges were encountered?
- What solutions worked?
- What would we do differently?
- What patterns emerged?

**Output**: Understanding of session content and learnings

---

### Step 2: Categorize Learnings

**Apply single-source-of-truth hierarchy** to each learning:

#### Tier 1: Executable Workflows → Skills

**Criteria**:

- ✅ Repeatable process with clear steps
- ✅ Proven in ≥2 real implementations
- ✅ Actionable (not just insights)

**Destination**: `.claude/skills/learned-pattern-[name].md`

**Delegate**: Use `continuous-learning.md` skill for extraction

**Examples**:

- Workflow for agent handoffs
- Process for temp-first file creation
- Steps for parallel review execution

---

#### Tier 2: Technical Insights → LEARNINGS.md

**Criteria**:

- ✅ Technical pattern or decision framework
- ✅ Proven valuable (≥2 uses OR high-impact single use)
- ✅ Generalizable insight (not workflow steps)

**Destination**: `docs/reference/LEARNINGS.md` (appropriate section)

**Action**: Add entry directly to LEARNINGS.md

**Examples**:

- Decision framework: "When to create new files vs. edit"
- Common pitfall: "File path assumptions"
- Best practice: "Version stamps in modified files"

---

#### Tier 3: Educational Narratives → FOR_CHRIS Docs

**Criteria**: Decision rubric met (≥2 criteria)

1. Significant architectural decision made
2. Novel pattern not in existing docs
3. Workflow changed affecting future dev
4. Multiple approaches evaluated
5. High educational value for Christopher

**Destination**: `archive/FOR_CHRIS_docs/[topic].md`

**Action**: Create using template in `.claude/templates/for-chris-doc-template.md`

**Examples**:

- Agent orchestration comparison (created)
- Kanji module architecture (future)
- localStorage schema design (future)

---

#### Tier 4: Bug Patterns → TESTING.md

**Criteria**:

- ✅ Bug with identified root cause
- ✅ Preventable pattern (not one-off)

**Destination**: `docs/TESTING.md#bug-learnings`

**Action**: Add to bug learnings section

**Examples**:

- Root cause analysis
- Prevention strategy
- Detection approach

---

#### Non-Learning Content

**One-off solutions**: Document in session digest only, don't extract
**Work-in-progress**: Keep in temp until complete
**Failed experiments**: Note in digest with "what we learned", decide if pattern extractable

**Output**: Learnings categorized by tier

---

### Step 3: Extract to Appropriate Locations

**For Tier 1 (Skills)**:

1. Use `.claude/skills/continuous-learning.md` process
2. Create new skill file
3. Cross-reference in LEARNINGS.md

**For Tier 2 (LEARNINGS.md)**:

1. Open `docs/reference/LEARNINGS.md`
2. Choose appropriate section:
   - Proven Patterns
   - Decision Frameworks
   - Common Pitfalls
   - Best Practices
3. Add entry using format:

   ```markdown
   #### Pattern/Framework/Pitfall/Practice: [Name]

   **When to apply**: Context
   **Proven in**: Version/feature
   **Description**: Details
   **See also**: Links
   ```

4. Update Table of Contents if new section added
5. Update metrics at bottom

**For Tier 3 (FOR_CHRIS docs)**:

1. Verify decision rubric met (≥2 criteria)
2. Choose descriptive topic name: `[topic-description].md`
3. Copy template from `.claude/templates/for-chris-doc-template.md`
4. Fill all sections with engaging narrative
5. Include cross-references to LEARNINGS.md and skills
6. Update `archive/FOR_CHRIS_docs/README.md` index

**For Tier 4 (Bug patterns)**:

1. Open `docs/TESTING.md`
2. Navigate to `#bug-learnings` section
3. Add entry with root cause, fix, prevention

**Output**: Learnings documented in appropriate repositories

---

### Step 4: Create Learning Digest

**Purpose**: Summary of curation activity for this session

**File naming**: `temp/LEARNING_DIGEST_[YYYY-MM-DD].md`

**Template**:

```markdown
# Learning Digest - [Date]

**Session Scope**: [Brief description of what was worked on]

**Sessions Curated**: [List of SESSION-*.md files reviewed]

---

## Learnings Extracted

### Skills Created
- `.claude/skills/learned-pattern-[name].md` - [Brief description]

### LEARNINGS.md Entries
- [Pattern Name] - [Section] - [Brief description]

### FOR_CHRIS Docs Created
- `archive/FOR_CHRIS_docs/[topic].md` - [Brief description]

### Bug Patterns Documented
- [Bug description] - Added to TESTING.md#bug-learnings

---

## One-Off Learnings (Not Extracted)

[Learnings specific to this session that don't meet extraction quality bar]

- Learning 1: Description and why not extracted
- Learning 2: Description and why not extracted

---

## Failed Experiments

[Things we tried that didn't work - valuable negative knowledge]

- Experiment 1: What we tried, why it failed, what we learned

---

## Metrics

- Total sessions curated: [number]
- Skills extracted: [number]
- LEARNINGS.md entries: [number]
- FOR_CHRIS docs: [number]
- Bug patterns: [number]

---

## Next Session Candidates

[Session notes that exist but weren't curated this time - for future curation]

- `temp/SESSION-[date].md` - [Why deferred]
```

**Output**: Learning digest created in temp/

---

### Step 5: Clean Up Session Notes (with Approval)

**IMPORTANT**: Always get explicit user approval before cleaning temp files

**Ask**:

```
I've curated the following session notes:
- temp/SESSION-[date1].md
- temp/SESSION-[date2].md
- temp/SESSION-[date3].md

All learnings have been extracted to:
- [List of destinations]

May I clean up these curated session files?
```

**If approved**:

- Move curated files to `archive/sessions/` OR delete (follow project policy)
- Keep learning digest in temp/ for reference

**If not approved**:

- Leave session files in place
- Note in digest which files remain

**Output**: Session notes cleaned (with approval) or left in place

---

## Expected Outcomes

**Primary outputs**:

- `temp/LEARNING_DIGEST_[DATE].md` - Curation summary
- Updated learning repositories (skills, LEARNINGS.md, FOR_CHRIS docs, TESTING.md)
- Clean temp/ directory (with approval)

**Quality indicators**:

- ✅ All tiers considered for each learning
- ✅ Single-source-of-truth hierarchy respected
- ✅ Cross-references complete
- ✅ Decision rubric applied for FOR_CHRIS docs
- ✅ Learning digest comprehensive

**Success metrics**:

- Sessions curated ÷ sessions accumulated ≥ 0.5 (at least half curated)
- Learnings extracted > 0 (found reusable patterns)
- No duplication across repositories

---

## Examples

### Example 1: Post-Feature Curation (v0.2 Kanji Module)

**Sessions**:

- `temp/SESSION-2026-01-20.md` (kanji data structure)
- `temp/SESSION-2026-01-21.md` (flashcard UI)
- `temp/SESSION-2026-01-22.md` (JLPT filtering)

**Learnings categorized**:

- **Tier 1 (Skill)**: Data generation workflow → `learned-pattern-data-generation.md`
- **Tier 2 (LEARNINGS)**: "Separate data from presentation" → Added to Proven Patterns
- **Tier 3 (FOR_CHRIS)**: Kanji module architecture → `kanji-module-architecture.md` (rubric met: architectural decision, novel pattern, multiple approaches)
- **Tier 4 (Bug)**: None

**Digest created**: `temp/LEARNING_DIGEST_2026-01-22.md`

**Cleanup**: Session files archived with approval

---

### Example 2: Bug Fix Curation

**Session**:

- `temp/SESSION-2026-01-15.md` (navigation link bug)

**Learnings categorized**:

- **Tier 1 (Skill)**: None (bug-specific fix)
- **Tier 2 (LEARNINGS)**: "File path assumptions" pitfall → Added to Common Pitfalls
- **Tier 3 (FOR_CHRIS)**: No (doesn't meet rubric)
- **Tier 4 (Bug)**: Navigation link breakage → Added to TESTING.md#bug-learnings

**Digest created**: `temp/LEARNING_DIGEST_2026-01-15.md`

**Cleanup**: Session file kept for reference (user preference)

---

## Common Pitfalls

### Pitfall 1: Over-Extraction (Too Eager)

**Symptom**: Creating FOR_CHRIS docs or skills for minor learnings

**Why it's wrong**: Dilutes quality of learning repository

**Solution**: Apply decision rubric strictly. When in doubt, add to LEARNINGS.md instead of creating new docs.

---

### Pitfall 2: Under-Extraction (Too Conservative)

**Symptom**: Valuable patterns documented only in session digest

**Why it's wrong**: Learnings not discoverable or reusable

**Solution**: If pattern proven ≥2 times, extract it. Better to have findable learning than buried in temp.

---

### Pitfall 3: Wrong Tier Assignment

**Symptom**: Workflows in LEARNINGS.md, insights in skills

**Why it's wrong**: Violates single-source-of-truth hierarchy

**Solution**:

- If it has executable steps → Skill
- If it's a technical insight → LEARNINGS.md
- If it meets rubric → FOR_CHRIS doc

---

### Pitfall 4: Cleaning Without Approval

**Symptom**: Session notes deleted without asking user

**Why it's wrong**: User may want to reference original notes

**Solution**: ALWAYS ask for explicit approval before cleaning temp files. Include what will be removed and what was extracted.

---

## Checklist

Before completing this skill:

- [ ] All uncurated session notes reviewed
- [ ] Each learning categorized by tier
- [ ] Skills extracted using continuous-learning.md
- [ ] LEARNINGS.md updated with new entries
- [ ] FOR_CHRIS docs created (if rubric met)
- [ ] Bug patterns added to TESTING.md (if applicable)
- [ ] Learning digest created
- [ ] Cross-references complete
- [ ] User approval obtained before cleanup
- [ ] Metrics updated in relevant files

---

## See Also

- `.claude/skills/continuous-learning.md` - Skill extraction process
- `.claude/agents/sage.md` - Sage persona workflows
- `docs/reference/LEARNINGS.md` - Technical patterns repository
- `.claude/templates/for-chris-doc-template.md` - FOR_CHRIS doc template
- `docs/TESTING.md#bug-learnings` - Bug pattern repository
