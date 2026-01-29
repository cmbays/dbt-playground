# For Chris: Phase 1 Infrastructure Setup (PR #11)

Hi Chris! This document explains what just happened in PR #11 and why it matters for the project.

## The Big Picture

PR #11 completed the **GitHub Project Infrastructure** for Phase 1 development. Think of it like setting up the factory floor before mass production: we've installed the conveyor belts, organized the tools, and created a playbook so everyone knows where things go.

This isn't flashy feature work—it's the unglamorous scaffolding that lets the real development happen smoothly. It's the difference between "where do I start?" and "here's my task, here's what done looks like."

## What Changed

### 1. **Issue Templates** (The Request Forms)

Created 4 GitHub issue templates so contributors describe work consistently:

- **Epic** (`.github/ISSUE_TEMPLATE/epic.yml`) - Big features broken into tasks
- **Task** (`.github/ISSUE_TEMPLATE/task.yml`) - Implementation work with acceptance criteria
- **Bug** (`.github/ISSUE_TEMPLATE/bug.yml`) - Bug reports with severity levels
- **Question** (`.github/ISSUE_TEMPLATE/question.yml`) - Clarification requests

**Why it matters:** Instead of "hey can you do thing?", we now have structured requests that include:
- What needs to be done (acceptance criteria)
- How long it should take (effort estimate)
- Who should work on it (persona labels)
- What's blocking it (dependencies)

### 2. **Automation Scripts** (The Batch Factory)

Created 2 shell scripts that handle repetitive GitHub work:

- **`setup-project.sh`** - Sets up custom fields on the GitHub project board
- **`create-phase1-tasks.sh`** - Automatically creates all 24 Phase 1 task issues

**Why it matters:** Manually creating 24 issues with consistent labels and linking is tedious and error-prone. These scripts do it in seconds and are reusable for future phases.

### 3. **24 Task Issues Created** (#13-36)

All 24 implementation tasks for Phase 1 now exist as GitHub issues:

- **Wave 1** (T1.1-T1.3): localStorage schema, session flow wireframes
- **Wave 2** (T2.1-T2.5): SRS algorithm implementation, database design
- **Wave 3** (T3.1-T3.6): Session mode UI, spaced repetition logic
- **Wave 4** (T4.1-T4.8): Progress tracking, streak system
- **Wave 5** (T5.1-T5.7): Mastery calculations, habit features

Each task has:
- ✅ Acceptance criteria (exactly what "done" means)
- ✅ Technical notes (hints about implementation)
- ✅ Dependency mapping (what needs to happen first)
- ✅ Effort estimate (how much work it is)

### 4. **GitHub Project Board Setup**

The project board is now a **control center** with custom fields:

- **Status**: Ready → In Progress → In Review → Done
- **Effort**: XS, S, M, L, XL (effort estimates)
- **Wave**: 1-5 (which development wave)
- **Persona**: PM, Architect, Developer, etc.
- **Priority**: Critical, High, Medium, Low
- **Epic**: Links tasks to their parent epic

All 27 items (3 Epics + 24 Tasks) are visible and filterable.

### 5. **Documentation** (The Manual)

Created `docs/PROJECT_BOARD_GUIDE.md` - a complete walkthrough of:
- How to claim a task
- How to move tasks through status columns
- How to filter and sort
- How to track Wave progress
- What each custom field means

Also cleaned up markdown in CLAUDE.md and other files.

## The Learning Moment

This PR teaches three important lessons about engineering:

### 1. **Infrastructure Pays Compounding Interest**

Spending 2 hours on project setup saves 2 minutes on every future task. With 24+ tasks, that's 48+ minutes saved (and that's just the obvious stuff). Multiply by the next 5 phases... you see where this goes.

### 2. **Consistency Beats Creativity**

Templates look "boring" but they're incredibly powerful:
- Everyone describes tasks the same way
- New people can self-serve (no need to ask "how do I structure this?")
- You can automate on top of consistent structure (e.g., the scripts)
- Reporting/metrics become possible (effort trends, velocity tracking)

### 3. **Reusable Patterns Scale**

Those scripts aren't one-time use. When we do Phase 2 (v0.4), we'll use the same scripts structure. When someone new joins, they can follow the same pattern. This is how great teams work—you establish patterns early and let them compound.

## How It Unblocks Development

**Before PR #11:**
- "What am I supposed to build?" → Unclear
- "How do I know when I'm done?" → Guessing
- "What should I work on next?" → No roadmap
- "Am I blocked by anything?" → Have to ask

**After PR #11:**
- "What am I supposed to build?" → Check your assigned issue, read acceptance criteria
- "How do I know when I'm done?" → Follow the Definition of Done checklist
- "What should I work on next?" → Look at "Ready" column on project board
- "Am I blocked?" → Check the Blockers section of your issue

## Practical Example: Starting Wave 1

A developer can now:

1. Go to project board → filter Status: Ready
2. See T1.1 (localStorage schema) and T2.1 (session wireframes)
3. Click T1.1 → read acceptance criteria (exactly what schema fields are needed)
4. Click Persona label → see it needs Architect + Developer
5. See no blockers → ready to start immediately
6. Move card to "In Progress"
7. Work against the clear acceptance criteria
8. When done, move to "In Review" → trigger code review
9. Once approved → move to "Done"

The entire workflow is **self-documenting**. No Slack messages needed asking "what should I do?" or "is this good enough?"

## What This Cost Us

- ~1,540 lines of configuration/scripts (not product code)
- ~2,000 lines of documentation
- Merged 49 files changed, 4,172 additions, 859 deletions

But it's **infrastructure**, not friction. It clears the path for actual development.

## Tech Decisions Worth Understanding

### **Why Shell Scripts for GitHub Automation?**

You could use the GitHub CLI (`gh`) directly in scripts. The scripts use:
- Bash (POSIX standard—works everywhere)
- `gh` CLI (GitHub's official tool—more reliable than API calls)
- Error handling (exit codes, validation)
- Comments (so future you knows why things work this way)

### **Why Custom Fields Instead of Labels Alone?**

GitHub labels are flat (all one dimension), but we need multiple independent dimensions:
- Labels: type, status, persona (good for categorization)
- Custom fields: Effort, Wave, Priority (good for planning/filtering)

Combining both gives you powerful filtering: "Show me high-priority, small effort, Wave 1 tasks assigned to developers."

### **Why This Specific Wave Structure (1-5)?**

The 5 waves represent **dependencies**:
- Wave 1: Foundation (data structure)
- Wave 2: Logic (algorithm)
- Wave 3: UI (interface)
- Wave 4: Features (streaks, progress)
- Wave 5: Polish (animations, accessibility)

You can't start Wave 3 until Wave 1 is done, so this structure **prevents blocked work**.

## What's Next

With this infrastructure in place:

1. ✅ Wave 1 is "Ready" → developers can start claiming tasks
2. ⏭️ Build localStorage schema + session flow
3. ⏭️ Track progress on project board
4. ⏭️ When Wave 1 done → unblock Wave 2
5. ⏭️ Repeat for Waves 2-5

The **feedback loop is tight**: work → complete → move card → unblock next team → repeat.

## Lessons for Next Time

When we do PR #12, #13, etc., remember:
- Use the same issue structure (so patterns stay consistent)
- Link to PRDs in issue descriptions (single source of truth)
- Include "Definition of Done" in every task
- Update the project board as work progresses (it's not a one-time setup)

## How to Tell If This Was Worth It

In 2 weeks, if developers say:
- ✅ "I always know what to work on next"
- ✅ "The acceptance criteria are clear"
- ✅ "I can see what's blocking me"
- ✅ "No ambiguity about when I'm done"

...then this infrastructure paid for itself.

---

**PR Stats:**
- Commits: 8
- Files changed: 49
- Lines added: 4,172
- Lines removed: 859
- Time to merge: ~4 hours
- Status: ✅ Merged

**GitHub Project Board:**
https://github.com/cmbays/japanese-study-site/projects/2
