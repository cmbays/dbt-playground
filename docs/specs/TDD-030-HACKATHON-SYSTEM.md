# TDD: Hackathon System

**Document ID**: TDD-HACKATHON-SYSTEM
**PRD Reference**: PRD-HACKATHON-SYSTEM
**Feature Set**: 8
**Version**: 1.0
**Status**: Draft (Deferred to v1.1+)
**Author**: Technical Architect
**Date**: 2026-02-01

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [/hackathon Command Design](#2-hackathon-command-design)
3. [Team Coordination Patterns](#3-team-coordination-patterns)
4. [Development Cycle Phases](#4-development-cycle-phases)
5. [Council of 7 Review Infrastructure](#5-council-of-7-review-infrastructure)
6. [Template Specifications](#6-template-specifications)
7. [Scoring and Consensus Algorithm](#7-scoring-and-consensus-algorithm)
8. [Results Documentation Format](#8-results-documentation-format)
9. [Implementation Sequence](#9-implementation-sequence)
10. [Testing Strategy](#10-testing-strategy)
11. [Appendix](#11-appendix)

---

## 1. Architecture Overview

### 1.1 System Context

```
                           ┌─────────────────────────────────────┐
                           │           Human (Chris)             │
                           │  /hackathon "theme" --teams 3       │
                           └──────────────────┬──────────────────┘
                                              │
                                              ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                          HACKATHON ORCHESTRATOR                               │
│                                                                               │
│  ┌─────────────┐   ┌─────────────────┐   ┌──────────────────────────────────┐│
│  │   SETUP     │ → │   BRIEFING      │ → │        DEVELOPMENT               ││
│  │  - Worktrees│   │  - Distribute   │   │     (Parallel Teams)             ││
│  │  - Branches │   │    challenge    │   │                                  ││
│  │  - State    │   │  - Start timer  │   │  ┌──────┐ ┌──────┐ ┌──────┐     ││
│  └─────────────┘   └─────────────────┘   │  │Team α│ │Team β│ │Team γ│     ││
│                                          │  └──────┘ └──────┘ └──────┘     ││
│                                          └──────────────────────────────────┘│
│                                                         │                     │
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────▼─────────┐          │
│  │    CLEANUP      │ ← │    RESULTS      │ ← │     COUNCIL       │          │
│  │  - Remove wt    │   │  - Aggregate    │   │  - 7 Reviewers    │          │
│  │  - Archive      │   │  - Document     │   │  - Score rubric   │          │
│  └─────────────────┘   └─────────────────┘   └───────────────────┘          │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Component Architecture

```
.claude/
├── commands/
│   └── hackathon.md           # Command definition
└── agents/
    └── council-reviewer.md    # Council reviewer persona

docs/
├── templates/
│   └── hackathons/
│       ├── HACKATHON_SUBMISSION.md
│       ├── HACKATHON_RUBRIC.md
│       ├── COUNCIL_REVIEW.md
│       └── HACKATHON_RESULTS.md
└── hackathons/
    └── YYYY_MM_DD_topic/      # Results archive
        ├── HACKATHON_RESULTS.md
        ├── team-alpha/
        │   └── hackathon_submission.md
        ├── team-beta/
        └── council/
            └── aggregated_scores.md

temp/
├── HACKATHON_STATE.md         # Active hackathon state
└── AGENT_REPORTS/
    └── hackathon-YYYY-MM-DD/
        ├── team-alpha/        # Team work artifacts
        ├── team-beta/
        ├── team-gamma/
        └── council/           # Council reviews
            ├── reviewer-1/
            ├── reviewer-2/
            └── ...
```

### 1.3 Data Flow

```
1. INVOCATION
   User → /hackathon command → Validate params → Initialize state

2. SETUP
   State → git worktree add (x N teams) → Branch creation → Folder creation

3. DEVELOPMENT (Parallel)
   Team A: IDEATION → SPIKE → PLAN → DEVELOP → TEST → REVIEW → REFACTOR → DOCS
   Team B: IDEATION → SPIKE → PLAN → DEVELOP → TEST → REVIEW → REFACTOR → DOCS
   Team C: IDEATION → SPIKE → PLAN → DEVELOP → TEST → REVIEW → REFACTOR → DOCS
                          ↓
   State file updated on each phase transition

4. COUNCIL
   Submissions → Reviewer 1 → Reviewer 2 → ... → Reviewer 7 → Aggregation

5. RESULTS
   Aggregated scores → Apply merge rules → Generate results → Archive
```

---

## 2. /hackathon Command Design

### 2.1 Command Definition File

**Location**: `.claude/commands/hackathon.md`

```markdown
# Hackathon Command

Launch competitive parallel agent teams for innovation exploration.

## Usage

```

/hackathon [theme] [options]

```

## Required Arguments

| Argument | Description |
|----------|-------------|
| theme | Challenge or problem statement (quoted string) |

## Options

| Option | Default | Range | Description |
|--------|---------|-------|-------------|
| --teams | 3 | 2-5 | Number of competing teams |
| --duration | 4h | 1-8h | Time limit for development |
| --reviewers | 7 | 3-7 | Council size (odd number) |
| --prototype | false | - | Run in prototype mode (2 teams, 3 reviewers, 2h) |

## Examples

```bash
# Full hackathon
/hackathon "Build patient cohort analytics" --teams 3 --duration 4h

# Prototype validation
/hackathon "Optimize staging models" --prototype

# Custom configuration
/hackathon "Implement incremental strategy" --teams 2 --reviewers 5 --duration 2h
```

## Workflow Phases

1. **SETUP**: Create worktrees, branches, state file
2. **BRIEFING**: Distribute challenge to teams
3. **DEVELOPMENT**: Parallel team development cycles
4. **SUBMISSION**: Teams finalize submissions
5. **COUNCIL**: 7 reviewers score submissions
6. **RESULTS**: Aggregate scores, announce winner
7. **CLEANUP**: Remove worktrees, archive results

## State Tracking

Central state maintained in `temp/HACKATHON_STATE.md`

## Artifacts

| Phase | Location |
|-------|----------|
| Team work | `temp/AGENT_REPORTS/hackathon-YYYY-MM-DD/team-{name}/` |
| Submissions | `temp/AGENT_REPORTS/hackathon-YYYY-MM-DD/team-{name}/hackathon_submission.md` |
| Council reviews | `temp/AGENT_REPORTS/hackathon-YYYY-MM-DD/council/reviewer-{N}/` |
| Final results | `docs/hackathons/YYYY_MM_DD_{topic}/HACKATHON_RESULTS.md` |

```

### 2.2 Parameter Validation

```yaml
# Parameter validation rules
theme:
  type: string
  required: true
  min_length: 10
  max_length: 500

teams:
  type: integer
  default: 3
  min: 2
  max: 5
  validation: "Must be integer in range 2-5"

duration:
  type: duration
  default: "4h"
  min: "1h"
  max: "8h"
  validation: "Format: Nh where N is 1-8"

reviewers:
  type: integer
  default: 7
  allowed: [3, 5, 7]
  validation: "Must be odd number: 3, 5, or 7"

prototype:
  type: boolean
  default: false
  effects:
    - sets teams to 2
    - sets reviewers to 3
    - sets duration to 2h
```

### 2.3 Command Execution Flow

```python
# Pseudocode for hackathon command execution

def execute_hackathon(theme, teams=3, duration="4h", reviewers=7, prototype=False):
    """Execute hackathon command."""

    # 1. VALIDATION
    validate_params(theme, teams, duration, reviewers)
    if prototype:
        teams, reviewers, duration = 2, 3, "2h"

    # 2. SETUP
    hackathon_id = generate_id()  # YYYY-MM-DD-topic-slug
    state = initialize_state(hackathon_id, theme, teams, duration, reviewers)

    for i, team_name in enumerate(TEAM_NAMES[:teams]):
        worktree = create_worktree(team_name, hackathon_id)
        branch = create_branch(team_name, hackathon_id)
        create_team_folder(team_name, hackathon_id)
        state.add_team(team_name, worktree, branch)

    # 3. BRIEFING
    for team in state.teams:
        send_briefing(team, theme)
    start_timer(duration)

    # 4. DEVELOPMENT (Supervisor monitors, teams work in parallel)
    while not all_submitted(state) and not timeout(state):
        update_state_from_teams(state)
        check_timeout_warnings(state)

    # 5. COUNCIL REVIEW
    for reviewer_id in range(1, reviewers + 1):
        for team in state.teams:
            review = invoke_council_reviewer(reviewer_id, team.submission)
            save_review(reviewer_id, team, review)
        state.council_progress = reviewer_id / reviewers

    # 6. RESULTS
    scores = aggregate_scores(state)
    ranking = apply_merge_rules(scores)
    results = generate_results(hackathon_id, ranking, state)
    archive_results(hackathon_id, results)

    # 7. CLEANUP
    for team in state.teams:
        if team != ranking.winner:
            remove_worktree(team)
    archive_state(state)

    return results
```

---

## 3. Team Coordination Patterns

### 3.1 Worktree Isolation

**Naming Convention**:

```
dbt-playground--team-{name}

Examples:
dbt-playground--team-alpha
dbt-playground--team-beta
dbt-playground--team-gamma
```

**Branch Naming**:

```
hackathon/{date}/team-{name}

Examples:
hackathon/2026-02-01/team-alpha
hackathon/2026-02-01/team-beta
hackathon/2026-02-01/team-gamma
```

**Directory Structure**:

```
~/projects/
├── dbt-playground/                      # Main repo (orchestrator)
├── dbt-playground--team-alpha/          # Team Alpha worktree
├── dbt-playground--team-beta/           # Team Beta worktree
└── dbt-playground--team-gamma/          # Team Gamma worktree
```

### 3.2 Team Isolation Rules

| Rule | Enforcement | Rationale |
|------|-------------|-----------|
| No cross-team file access | Separate worktrees | Fair competition |
| No shared communication | Isolated sessions | Independent solutions |
| No access to other submissions | Council phase only | Prevent copying |
| Independent test environments | Per-worktree `.venv` | No interference |

### 3.3 State Synchronization

**Central State** (`temp/HACKATHON_STATE.md`):

```yaml
---
hackathon_id: 2026-02-01-patient-cohorts
theme: "Build patient cohort analytics"
start_time: 2026-02-01T10:00:00Z
end_time: 2026-02-01T14:00:00Z
duration: 4h
status: IN_PROGRESS
teams_count: 3
reviewers_count: 7
---

## Configuration

- Prototype Mode: No
- Max Refactor Cycles: 5

## Teams

### Team Alpha
- Worktree: ../dbt-playground--team-alpha
- Branch: hackathon/2026-02-01/team-alpha
- Phase: DEVELOP
- Refactor Cycle: 0/5
- Submitted: No
- Last Update: 2026-02-01T11:30:00Z

### Team Beta
- Worktree: ../dbt-playground--team-beta
- Branch: hackathon/2026-02-01/team-beta
- Phase: REVIEW
- Refactor Cycle: 1/5
- Submitted: No
- Last Update: 2026-02-01T11:45:00Z

### Team Gamma
- Worktree: ../dbt-playground--team-gamma
- Branch: hackathon/2026-02-01/team-gamma
- Phase: TEST
- Refactor Cycle: 0/5
- Submitted: No
- Last Update: 2026-02-01T11:20:00Z

## Council Review

- Status: PENDING
- Reviewers Complete: 0/7
- Submissions Received: 0/3

## Timeline

| Time | Event |
|------|-------|
| 10:00 | Hackathon started |
| 10:05 | All teams briefed |
| 10:30 | Team Alpha completed IDEATION |
| 10:45 | Team Beta completed SPIKE |
| 11:00 | Team Gamma completed PLAN |
| 11:30 | Warning: 2h 30m remaining |

## Alerts

- [ ] 30 minutes remaining
- [ ] 10 minutes remaining
- [ ] Timeout reached
```

### 3.4 Parallel Execution Model

```
                    SUPERVISOR (Main Repo)
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │  Team Alpha  │ │  Team Beta   │ │  Team Gamma  │
    │  Worktree    │ │  Worktree    │ │  Worktree    │
    │              │ │              │ │              │
    │  IDEATION    │ │  IDEATION    │ │  IDEATION    │
    │      ↓       │ │      ↓       │ │      ↓       │
    │  SPIKE       │ │  SPIKE       │ │  SPIKE       │
    │      ↓       │ │      ↓       │ │      ↓       │
    │  PLAN        │ │  PLAN        │ │  PLAN        │
    │      ↓       │ │      ↓       │ │      ↓       │
    │  DEVELOP     │ │  DEVELOP     │ │  DEVELOP     │
    │      ↓       │ │      ↓       │ │      ↓       │
    │  TEST        │ │  TEST        │ │  TEST        │
    │      ↓       │ │      ↓       │ │      ↓       │
    │  REVIEW      │ │  REVIEW      │ │  REVIEW      │
    │      ↓       │ │      ↓       │ │      ↓       │
    │  REFACTOR    │ │  REFACTOR    │ │  REFACTOR    │
    │   (x1-5)     │ │   (x1-5)     │ │   (x1-5)     │
    │      ↓       │ │      ↓       │ │      ↓       │
    │  APPROVE     │ │  APPROVE     │ │  APPROVE     │
    │      ↓       │ │      ↓       │ │      ↓       │
    │  DOCS        │ │  DOCS        │ │  DOCS        │
    │      ↓       │ │      ↓       │ │      ↓       │
    │  CLEANUP     │ │  CLEANUP     │ │  CLEANUP     │
    │      ↓       │ │      ↓       │ │      ↓       │
    │  [SUBMITTED] │ │  [SUBMITTED] │ │  [SUBMITTED] │
    └──────────────┘ └──────────────┘ └──────────────┘
           │               │               │
           └───────────────┼───────────────┘
                           │
                           ▼
                    COUNCIL REVIEW
```

---

## 4. Development Cycle Phases

### 4.1 Extended Development Cycle

The hackathon development cycle extends the standard 5-stage workflow with hackathon-specific phases:

```
Standard:  UNDERSTAND → PLAN → BUILD → VERIFY → DEPLOY

Hackathon: IDEATION → SPIKE → UNDERSTAND → PLAN → DEVELOP → TEST → REVIEW → REFACTOR → APPROVE → DOCS → CLEANUP
                                                               └──────────────────┘
                                                                  (up to 5 cycles)
```

### 4.2 Phase Specifications

#### IDEATION Phase (15 min)

**Purpose**: Brainstorm multiple approaches before committing to one.

**Inputs**: Theme/challenge from briefing

**Activities**:

1. Analyze the problem space
2. Generate 3+ distinct approaches
3. Evaluate feasibility of each
4. Document in `ideas.md`

**Outputs**:

- `ideas.md` with minimum 3 approaches
- Each approach with: description, pros, cons, estimated complexity

**Gate**: At least 2 viable approaches identified

**Example ideas.md**:

```markdown
# Team Alpha - Ideation

## Challenge
Build patient cohort analytics

## Approach 1: Dimension-First
Build dim_patient_cohorts first, then fact table
- Pros: Cleaner dimensional model, reusable dimension
- Cons: May need iteration on grain
- Complexity: Medium

## Approach 2: Fact-First
Build fct_cohort_assignments first, infer dimensions
- Pros: Faster initial implementation
- Cons: May need refactoring later
- Complexity: Low-Medium

## Approach 3: Hybrid with Bridge
Use bridge table for many-to-many cohort membership
- Pros: Most flexible, handles edge cases
- Cons: More complex, more tables
- Complexity: High

## Selected: Approach 1 (Dimension-First)
Rationale: Best balance of quality and complexity
```

#### SPIKE Phase (30 min)

**Purpose**: Rapid prototype to validate selected approach.

**Inputs**: Selected approach from IDEATION

**Activities**:

1. Create minimal working prototype
2. Test core assumptions
3. Identify technical risks
4. Document learnings

**Outputs**:

- `spike/` folder with prototype code
- `spike/SPIKE_NOTES.md` with findings
- Feasibility confirmation or pivot decision

**Gate**: Prototype demonstrates feasibility

#### UNDERSTAND Phase (15 min)

**Purpose**: Deep dive into existing codebase relevant to challenge.

**Inputs**: Confirmed approach from SPIKE

**Activities**:

1. Read existing models in affected area
2. Understand current patterns
3. Identify integration points
4. Note dependencies

**Outputs**:

- Understanding of existing patterns
- List of files to modify/create
- Dependencies mapped

**Gate**: Clear understanding of integration approach

#### PLAN Phase (20 min)

**Purpose**: Create detailed implementation plan.

**Inputs**: UNDERSTAND findings

**Activities**:

1. Create model design
2. Define test strategy
3. Plan file structure
4. Estimate remaining effort

**Outputs**:

- `hackathon_plan.md` with detailed plan
- Model diagram if applicable
- Test list

**Gate**: Plan approved by team lead agent

#### DEVELOP Phase (60 min)

**Purpose**: Implement the solution.

**Inputs**: Approved plan

**Activities**:

1. Create/modify dbt models
2. Write SQL transformations
3. Add schema definitions
4. Implement tests

**Outputs**:

- Implemented models
- Schema YAML files
- Basic documentation

**Gate**: Code compiles, basic tests pass

#### TEST Phase (20 min)

**Purpose**: Validate implementation.

**Inputs**: Implemented code

**Activities**:

1. Run `dbt build`
2. Verify test coverage
3. Check data quality
4. Document test results

**Outputs**:

- Test results log
- Coverage assessment
- Quality validation

**Gate**: All tests pass, no critical issues

#### REVIEW Phase (15 min per cycle)

**Purpose**: Internal team quality review.

**Inputs**: Passing tests

**Activities**:

1. Code review against standards
2. Pattern compliance check
3. Documentation review
4. Identify improvements

**Outputs**:

- Review comments
- Improvement suggestions
- Refactor decision (Y/N)

**Gate**: Review complete, decision documented

#### REFACTOR Phase (20 min per cycle, max 5)

**Purpose**: Improve based on review feedback.

**Inputs**: Review feedback

**Activities**:

1. Address review comments
2. Improve code quality
3. Enhance documentation
4. Re-run tests

**Outputs**:

- Improved code
- Updated documentation
- Ready for next review

**Gate**: Tests pass, cycle back to REVIEW if needed

#### APPROVE Phase (10 min)

**Purpose**: Final team approval for submission.

**Inputs**: Code passing all refactor cycles

**Activities**:

1. Final quality check
2. Submission readiness assessment
3. Team lead approval

**Outputs**:

- Approval stamp
- Ready for DOCS phase

**Gate**: Team lead confirms submission-ready

#### DOCS Phase (15 min)

**Purpose**: Create submission documentation.

**Inputs**: Approved code

**Activities**:

1. Fill out HACKATHON_SUBMISSION.md template
2. Document approach and rationale
3. Capture learnings
4. Create before/after comparison

**Outputs**:

- `hackathon_submission.md` (complete)
- Design decision documentation
- Learnings captured

**Gate**: Submission template complete

#### CLEANUP Phase (10 min)

**Purpose**: Final polish and spike removal.

**Inputs**: Complete documentation

**Activities**:

1. Remove spike code (if not needed)
2. Clean up temporary files
3. Final commit
4. Mark submitted in state

**Outputs**:

- Clean branch
- Final commit
- Status: SUBMITTED

**Gate**: Branch clean, state updated

---

## 5. Council of 7 Review Infrastructure

### 5.1 Council Reviewer Persona

**Location**: `.claude/agents/council-reviewer.md`

```yaml
---
name: council-reviewer
prefix: "council:"
description: Hackathon submission reviewer for Council of 7
tools: ["Read", "Grep", "Glob", "Bash"]
model: opus
---

# Council Reviewer

You are a member of the Council of 7 reviewing hackathon submissions.

## Your Role

You are Reviewer {N} with focus area: {FOCUS_AREA}

| Reviewer | Focus Area |
|----------|------------|
| 1 | Innovation and creativity |
| 2 | Technical quality - patterns and architecture |
| 3 | Technical quality - testing and reliability |
| 4 | Completeness - requirements coverage |
| 5 | Documentation - clarity and maintainability |
| 6 | Integration feasibility - merge readiness |
| 7 | Overall recommendation - holistic assessment |

## Review Process

1. Read the team's `hackathon_submission.md`
2. Examine their code implementation
3. Run tests to verify functionality
4. Score using the HACKATHON_RUBRIC.md criteria
5. Provide detailed feedback
6. Make merge recommendation

## Scoring Guidelines

Use the HACKATHON_RUBRIC.md scoring scale:
- 1: Does not meet expectations (critical issues)
- 2: Partially meets expectations (significant gaps)
- 3: Meets expectations (acceptable quality)
- 4: Exceeds expectations (good quality)
- 5: Exceptional (exemplary work)

## Output

Write your review to:
`temp/AGENT_REPORTS/hackathon-{date}/council/reviewer-{N}/{team}-review.md`

Use the COUNCIL_REVIEW.md template.

## Objectivity Rules

- Review each submission independently
- Do not compare submissions to each other during review
- Focus on absolute quality against rubric
- Be consistent across all submissions
- Document reasoning for scores
```

### 5.2 Council Invocation Sequence

```
[All teams submitted]
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  COUNCIL COORDINATOR (Supervisor)                            │
│                                                              │
│  for reviewer_id in [1, 2, 3, 4, 5, 6, 7]:                  │
│      for team in [Alpha, Beta, Gamma]:                      │
│          invoke_council_reviewer(reviewer_id, team)         │
│          save_review()                                       │
│          update_state()                                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
    21 Reviews Total
    (7 reviewers x 3 teams)
         │
         ▼
   Score Aggregation
```

### 5.3 Review Workflow

```python
# Pseudocode for council review

def run_council_review(state):
    """Execute council review phase."""

    submissions = collect_submissions(state)

    for reviewer_id in range(1, state.reviewers_count + 1):
        focus_area = FOCUS_AREAS[reviewer_id]

        for team in state.teams:
            submission = team.submission_path

            # Invoke council reviewer
            review = invoke_agent(
                agent="council-reviewer",
                context={
                    "reviewer_id": reviewer_id,
                    "focus_area": focus_area,
                    "submission": submission,
                    "rubric": "docs/templates/hackathons/HACKATHON_RUBRIC.md"
                }
            )

            # Save review
            review_path = f"temp/AGENT_REPORTS/hackathon-{state.date}/council/reviewer-{reviewer_id}/{team.name}-review.md"
            write_review(review_path, review)

            # Update state
            state.council_reviews.append({
                "reviewer": reviewer_id,
                "team": team.name,
                "scores": review.scores,
                "recommendation": review.recommendation
            })

        # Update progress
        state.council_progress = reviewer_id / state.reviewers_count

    return state.council_reviews
```

### 5.4 Focus Area Assignments

| Reviewer | Focus Area | Primary Categories |
|----------|------------|-------------------|
| 1 | Innovation | Innovation (25%) |
| 2 | Architecture | Technical Quality - Patterns (15%) |
| 3 | Testing | Technical Quality - Tests (15%) |
| 4 | Completeness | Completeness (25%) |
| 5 | Documentation | Documentation (10%) |
| 6 | Integration | Presentation + Merge feasibility |
| 7 | Holistic | All categories, overall recommendation |

---

## 6. Template Specifications

### 6.1 HACKATHON_RUBRIC.md

**Location**: `docs/templates/hackathons/HACKATHON_RUBRIC.md`

```markdown
# Hackathon Judging Rubric

## Scoring Scale

| Score | Level | Description |
|-------|-------|-------------|
| 1 | Does not meet | Critical issues, fails requirements |
| 2 | Partially meets | Significant gaps, needs major work |
| 3 | Meets expectations | Acceptable quality, functional |
| 4 | Exceeds expectations | Good quality, well-crafted |
| 5 | Exceptional | Exemplary, best-in-class |

## Categories

### Innovation (25%)

Evaluates creativity and novelty of approach.

| Score | Criteria |
|-------|----------|
| 1 | Direct copy of existing patterns, no thought |
| 2 | Minor variation on existing approach |
| 3 | Reasonable approach, some creative elements |
| 4 | Novel approach with clear benefits |
| 5 | Highly innovative, may influence future patterns |

**Evaluation Points**:
- [ ] Novel approach to the problem
- [ ] Creative use of existing patterns
- [ ] Demonstrates learning from prior work
- [ ] Introduces reusable patterns

### Technical Quality (30%)

Evaluates code quality and engineering excellence.

**Patterns and Architecture (15%)**

| Score | Criteria |
|-------|----------|
| 1 | Violates project patterns, poor structure |
| 2 | Inconsistent patterns, some issues |
| 3 | Follows patterns, acceptable structure |
| 4 | Strong patterns, good architecture |
| 5 | Exemplary architecture, elevates codebase |

**Testing and Reliability (15%)**

| Score | Criteria |
|-------|----------|
| 1 | No tests, obvious bugs |
| 2 | Minimal tests, some bugs |
| 3 | Adequate tests, tests pass |
| 4 | Good coverage, edge cases handled |
| 5 | Comprehensive tests, bulletproof |

**Evaluation Points**:
- [ ] Code follows project patterns
- [ ] Tests written and passing
- [ ] No obvious bugs or issues
- [ ] Error handling appropriate
- [ ] Performance acceptable

### Completeness (25%)

Evaluates whether solution solves the stated problem.

| Score | Criteria |
|-------|----------|
| 1 | Does not address problem |
| 2 | Partially addresses problem |
| 3 | Addresses core problem |
| 4 | Fully addresses problem with extras |
| 5 | Complete solution exceeding requirements |

**Evaluation Points**:
- [ ] Solves stated problem
- [ ] Handles edge cases
- [ ] Production-ready quality
- [ ] All acceptance criteria met

### Documentation (10%)

Evaluates clarity of documentation and maintainability.

| Score | Criteria |
|-------|----------|
| 1 | No documentation |
| 2 | Minimal documentation |
| 3 | Adequate documentation |
| 4 | Good documentation, clear |
| 5 | Exemplary documentation, teaches |

**Evaluation Points**:
- [ ] Clear submission explanation
- [ ] Design decisions documented
- [ ] Future maintainability considered
- [ ] Learnings captured

### Presentation (10%)

Evaluates submission quality and clarity.

| Score | Criteria |
|-------|----------|
| 1 | Incomplete or confusing submission |
| 2 | Basic submission, gaps |
| 3 | Complete submission, clear |
| 4 | Well-organized, easy to follow |
| 5 | Outstanding presentation, compelling |

**Evaluation Points**:
- [ ] Submission template complete
- [ ] Clear before/after comparison
- [ ] Learnings captured
- [ ] Easy to understand approach

## Final Decision

After scoring all categories, make a merge recommendation:

- [ ] **RECOMMEND_MERGE**: This submission should be merged to main
- [ ] **ARCHIVE_ONLY**: Valuable learnings but not production-ready

**Merge Criteria**:
- Average score >= 3.0
- No category scored as 1 (critical failure)
- Code quality sufficient for production
```

### 6.2 HACKATHON_SUBMISSION.md

**Location**: `docs/templates/hackathons/HACKATHON_SUBMISSION.md`

```markdown
# Hackathon Submission: [Team Name]

---
team: [alpha|beta|gamma]
hackathon_id: YYYY-MM-DD-topic
submitted_at: YYYY-MM-DDTHH:MM:SSZ
---

## 1. Solution Overview

### 1.1 Summary

[2-3 sentence summary of what you built]

### 1.2 Before/After

**Before (Problem State)**:
- [What was the problem]
- [What was missing]

**After (Solution State)**:
- [What you built]
- [What it enables]

## 2. Technical Approach

### 2.1 Selected Approach

[From IDEATION phase, which approach did you select and why]

### 2.2 Architecture

[Describe your architecture]

```sql
-- Key model structure
[Include representative SQL snippets]
```

### 2.3 Files Changed/Created

| File | Change Type | Purpose |
|------|-------------|---------|
| models/... | Created | [purpose] |
| models/... | Modified | [purpose] |

## 3. Design Decisions

### 3.1 Key Decisions

| Decision | Alternatives Considered | Rationale |
|----------|------------------------|-----------|
| [decision 1] | [alternatives] | [why this choice] |
| [decision 2] | [alternatives] | [why this choice] |

### 3.2 Tradeoffs

| Tradeoff | Benefit | Cost |
|----------|---------|------|
| [tradeoff 1] | [benefit] | [cost] |

## 4. Testing

### 4.1 Test Coverage

| Model | Tests | Status |
|-------|-------|--------|
| [model 1] | unique, not_null, ... | Pass |
| [model 2] | relationships, ... | Pass |

### 4.2 Validation Steps

```bash
# Commands run to validate
dbt build --select +model_name
```

## 5. Learnings

### 5.1 What Worked Well

- [success 1]
- [success 2]

### 5.2 What Would Do Differently

- [improvement 1]
- [improvement 2]

### 5.3 Reusable Patterns Discovered

- [pattern 1]
- [pattern 2]

## 6. Integration Notes

### 6.1 Dependencies

- [dependency on other models]
- [external dependencies]

### 6.2 Migration Considerations

[Notes for if this is merged]

## 7. Team Notes

### 7.1 Approach Comparison

[How does this compare to what other approaches might have done]

### 7.2 Recommendations

[Recommendations regardless of whether this wins]

---

*Submitted by Team [Name]*
*Hackathon: [ID]*

```

### 6.3 COUNCIL_REVIEW.md

**Location**: `docs/templates/hackathons/COUNCIL_REVIEW.md`

```markdown
# Council Review: [Team Name]

---
reviewer_id: [1-7]
focus_area: [Innovation|Architecture|Testing|Completeness|Documentation|Integration|Holistic]
team: [alpha|beta|gamma]
hackathon_id: YYYY-MM-DD-topic
reviewed_at: YYYY-MM-DDTHH:MM:SSZ
scores:
  innovation: [1-5]
  technical_patterns: [1-5]
  technical_testing: [1-5]
  completeness: [1-5]
  documentation: [1-5]
  presentation: [1-5]
  overall: [1-5]
recommendation: [RECOMMEND_MERGE|ARCHIVE_ONLY]
---

## Reviewer Context

- **Reviewer ID**: [1-7]
- **Focus Area**: [focus area]
- **Team Reviewed**: [team name]

## Scores

### Innovation (25%)

**Score**: [1-5]

**Evaluation**:
- Novel approach: [Yes/No/Partial]
- Creative use of patterns: [Yes/No/Partial]
- Learning from prior work: [Yes/No/Partial]
- Reusable patterns: [Yes/No/Partial]

**Comments**:
[Detailed feedback on innovation]

### Technical Quality - Patterns (15%)

**Score**: [1-5]

**Evaluation**:
- Follows project patterns: [Yes/No/Partial]
- Good architecture: [Yes/No/Partial]
- No obvious issues: [Yes/No/Partial]

**Comments**:
[Detailed feedback on patterns]

### Technical Quality - Testing (15%)

**Score**: [1-5]

**Evaluation**:
- Tests written: [Yes/No/Partial]
- Tests passing: [Yes/No/Partial]
- Edge cases: [Yes/No/Partial]
- Error handling: [Yes/No/Partial]

**Comments**:
[Detailed feedback on testing]

### Completeness (25%)

**Score**: [1-5]

**Evaluation**:
- Solves problem: [Yes/No/Partial]
- Edge cases handled: [Yes/No/Partial]
- Production-ready: [Yes/No/Partial]

**Comments**:
[Detailed feedback on completeness]

### Documentation (10%)

**Score**: [1-5]

**Evaluation**:
- Submission complete: [Yes/No/Partial]
- Decisions documented: [Yes/No/Partial]
- Learnings captured: [Yes/No/Partial]

**Comments**:
[Detailed feedback on documentation]

### Presentation (10%)

**Score**: [1-5]

**Evaluation**:
- Template complete: [Yes/No/Partial]
- Clear explanation: [Yes/No/Partial]
- Easy to follow: [Yes/No/Partial]

**Comments**:
[Detailed feedback on presentation]

## Overall Assessment

**Weighted Score**: [calculated]

**Strengths**:
1. [strength 1]
2. [strength 2]

**Areas for Improvement**:
1. [improvement 1]
2. [improvement 2]

## Recommendation

**Decision**: [RECOMMEND_MERGE | ARCHIVE_ONLY]

**Rationale**:
[Why this recommendation]

**Conditions** (if RECOMMEND_MERGE):
- [ ] [any conditions before merge]

---

*Reviewed by Council Member [N]*
```

### 6.4 HACKATHON_RESULTS.md

**Location**: `docs/templates/hackathons/HACKATHON_RESULTS.md`

```markdown
# Hackathon Results: [Topic]

---
hackathon_id: YYYY-MM-DD-topic
date: YYYY-MM-DD
theme: "[theme]"
duration: [X]h
teams: [N]
reviewers: [N]
winner: [team-name]
merge_recommendation: [MERGE|ARCHIVE]
---

## Executive Summary

[2-3 sentence summary of hackathon and outcome]

## Hackathon Details

| Attribute | Value |
|-----------|-------|
| Date | [date] |
| Theme | [theme] |
| Duration | [X] hours |
| Teams | [N] |
| Council Size | [N] |

## Results

### Final Rankings

| Rank | Team | Score | Recommendation |
|------|------|-------|----------------|
| 1 | [team] | [score] | [MERGE/ARCHIVE] |
| 2 | [team] | [score] | [ARCHIVE] |
| 3 | [team] | [score] | [ARCHIVE] |

### Winner: Team [Name]

**Score**: [X.XX/5.00]

**Why They Won**:
- [reason 1]
- [reason 2]

**Council Consensus**: [N]/[N] recommended merge

### Score Breakdown by Category

| Category | Alpha | Beta | Gamma |
|----------|-------|------|-------|
| Innovation (25%) | X.X | X.X | X.X |
| Technical - Patterns (15%) | X.X | X.X | X.X |
| Technical - Testing (15%) | X.X | X.X | X.X |
| Completeness (25%) | X.X | X.X | X.X |
| Documentation (10%) | X.X | X.X | X.X |
| Presentation (10%) | X.X | X.X | X.X |
| **Weighted Total** | **X.XX** | **X.XX** | **X.XX** |

## Team Summaries

### Team Alpha

**Approach**: [brief description]

**Strengths**:
- [strength 1]
- [strength 2]

**Areas for Improvement**:
- [area 1]
- [area 2]

**Council Feedback Summary**:
[aggregated feedback]

### Team Beta

[same structure]

### Team Gamma

[same structure]

## Learnings

### Patterns Discovered

| Pattern | Source | Applicability |
|---------|--------|---------------|
| [pattern 1] | Team [X] | [where useful] |
| [pattern 2] | Team [X] | [where useful] |

### What Worked

- [success 1]
- [success 2]

### What to Improve Next Time

- [improvement 1]
- [improvement 2]

## Next Steps

### For Winner

- [ ] Additional code review before merge
- [ ] Documentation updates
- [ ] Integration testing

### For All Teams

- [ ] Learnings extracted to LEARNINGS.md
- [ ] Patterns documented for future use
- [ ] Worktrees cleaned up

## Artifacts

| Artifact | Location |
|----------|----------|
| Team Alpha Submission | [path] |
| Team Beta Submission | [path] |
| Team Gamma Submission | [path] |
| Council Reviews | [path] |
| Winner Branch | [branch name] |

---

*Hackathon completed: [date]*
*Results documented by: Supervisor*
```

---

## 7. Scoring and Consensus Algorithm

### 7.1 Score Aggregation

**Category Weights**:

| Category | Weight | Max Points |
|----------|--------|------------|
| Innovation | 25% | 1.25 |
| Technical Quality - Patterns | 15% | 0.75 |
| Technical Quality - Testing | 15% | 0.75 |
| Completeness | 25% | 1.25 |
| Documentation | 10% | 0.50 |
| Presentation | 10% | 0.50 |
| **Total** | **100%** | **5.00** |

**Calculation**:

```python
def calculate_weighted_score(scores):
    """Calculate weighted average score."""

    weights = {
        "innovation": 0.25,
        "technical_patterns": 0.15,
        "technical_testing": 0.15,
        "completeness": 0.25,
        "documentation": 0.10,
        "presentation": 0.10
    }

    weighted_sum = sum(scores[cat] * weight for cat, weight in weights.items())
    return weighted_sum

def aggregate_team_scores(team_reviews):
    """Aggregate scores from all reviewers for a team."""

    category_scores = defaultdict(list)

    for review in team_reviews:
        for category, score in review.scores.items():
            category_scores[category].append(score)

    # Average each category across reviewers
    averaged_scores = {
        cat: sum(scores) / len(scores)
        for cat, scores in category_scores.items()
    }

    # Calculate weighted total
    weighted_total = calculate_weighted_score(averaged_scores)

    return {
        "category_averages": averaged_scores,
        "weighted_total": weighted_total,
        "reviewer_count": len(team_reviews)
    }
```

### 7.2 Merge Rules

**Merge Recommendation Criteria**:

| Rule | Condition | Effect |
|------|-----------|--------|
| R1: Minimum Score | weighted_total >= 3.0 | Required for MERGE |
| R2: Majority Vote | RECOMMEND_MERGE votes >= ceil(N/2) | Required for MERGE |
| R3: No Critical Failure | No category score = 1 | Required for MERGE |
| R4: Ranking | Higher score wins | Determines winner |

**Algorithm**:

```python
def determine_merge_recommendation(team_scores, team_reviews):
    """Determine merge recommendation for a team."""

    # R1: Minimum score
    if team_scores["weighted_total"] < 3.0:
        return "ARCHIVE_ONLY", "Score below 3.0 threshold"

    # R2: Majority vote
    merge_votes = sum(1 for r in team_reviews if r.recommendation == "RECOMMEND_MERGE")
    majority = (len(team_reviews) + 1) // 2  # ceil(N/2)
    if merge_votes < majority:
        return "ARCHIVE_ONLY", f"Only {merge_votes}/{len(team_reviews)} voted merge"

    # R3: No critical failures
    for review in team_reviews:
        for category, score in review.scores.items():
            if score == 1:
                return "ARCHIVE_ONLY", f"Critical failure in {category}"

    return "RECOMMEND_MERGE", "All criteria met"

def rank_teams(all_team_scores):
    """Rank teams by weighted total score."""

    ranked = sorted(
        all_team_scores.items(),
        key=lambda x: x[1]["weighted_total"],
        reverse=True
    )

    return [
        {
            "rank": i + 1,
            "team": team,
            "score": scores["weighted_total"],
            "recommendation": determine_merge_recommendation(scores, reviews)[0]
        }
        for i, (team, scores) in enumerate(ranked)
    ]
```

### 7.3 Tie Breaking

**Tiebreaker Rules** (in order):

1. Higher Innovation score (creativity rewarded)
2. Higher Completeness score (functioning solution)
3. Higher Technical Quality total
4. First to submit (timestamp)

```python
def break_tie(team_a, team_b):
    """Break tie between two teams with equal weighted scores."""

    # Tiebreaker 1: Innovation
    if team_a.scores["innovation"] != team_b.scores["innovation"]:
        return team_a if team_a.scores["innovation"] > team_b.scores["innovation"] else team_b

    # Tiebreaker 2: Completeness
    if team_a.scores["completeness"] != team_b.scores["completeness"]:
        return team_a if team_a.scores["completeness"] > team_b.scores["completeness"] else team_b

    # Tiebreaker 3: Technical Quality (combined)
    tech_a = team_a.scores["technical_patterns"] + team_a.scores["technical_testing"]
    tech_b = team_b.scores["technical_patterns"] + team_b.scores["technical_testing"]
    if tech_a != tech_b:
        return team_a if tech_a > tech_b else team_b

    # Tiebreaker 4: Submission time
    return team_a if team_a.submitted_at < team_b.submitted_at else team_b
```

---

## 8. Results Documentation Format

### 8.1 Archive Structure

```
docs/hackathons/
└── YYYY_MM_DD_topic/
    ├── HACKATHON_RESULTS.md      # Main results document
    ├── team-alpha/
    │   └── hackathon_submission.md
    ├── team-beta/
    │   └── hackathon_submission.md
    ├── team-gamma/
    │   └── hackathon_submission.md
    ├── council/
    │   ├── reviewer-1/
    │   │   ├── team-alpha-review.md
    │   │   ├── team-beta-review.md
    │   │   └── team-gamma-review.md
    │   ├── reviewer-2/
    │   └── ...
    └── aggregated_scores.yaml
```

### 8.2 Aggregated Scores Format

**Location**: `docs/hackathons/YYYY_MM_DD_topic/aggregated_scores.yaml`

```yaml
hackathon_id: 2026-02-01-patient-cohorts
computed_at: 2026-02-01T14:30:00Z

teams:
  alpha:
    scores:
      innovation: 4.1
      technical_patterns: 3.7
      technical_testing: 4.0
      completeness: 3.9
      documentation: 4.2
      presentation: 3.8
    weighted_total: 3.94
    merge_votes: 5
    archive_votes: 2
    recommendation: RECOMMEND_MERGE
    rank: 1

  beta:
    scores:
      innovation: 3.5
      technical_patterns: 4.0
      technical_testing: 3.8
      completeness: 3.6
      documentation: 3.5
      presentation: 3.7
    weighted_total: 3.67
    merge_votes: 4
    archive_votes: 3
    recommendation: RECOMMEND_MERGE
    rank: 2

  gamma:
    scores:
      innovation: 3.0
      technical_patterns: 3.2
      technical_testing: 3.5
      completeness: 3.0
      documentation: 3.0
      presentation: 3.2
    weighted_total: 3.12
    merge_votes: 3
    archive_votes: 4
    recommendation: ARCHIVE_ONLY
    rank: 3

winner: alpha
merge_eligible: [alpha, beta]
```

---

## 9. Implementation Sequence

### 9.1 Phase 1: Templates (2-3 hours)

**Objective**: Create all hackathon templates.

**Steps**:

1. Create `docs/templates/hackathons/` directory
2. Implement HACKATHON_RUBRIC.md (scoring criteria)
3. Implement HACKATHON_SUBMISSION.md (team template)
4. Implement COUNCIL_REVIEW.md (reviewer template)
5. Implement HACKATHON_RESULTS.md (final results)
6. Test templates with sample data

**Deliverables**:

- 4 template files
- Sample filled versions for validation

**Dependencies**: None

### 9.2 Phase 2: Command Scaffold (4-6 hours)

**Objective**: Create `/hackathon` command with basic flow.

**Steps**:

1. Create `.claude/commands/hackathon.md`
2. Implement parameter validation logic
3. Create `council-reviewer.md` persona
4. Implement `temp/HACKATHON_STATE.md` schema
5. Implement SETUP phase (worktree creation)
6. Implement CLEANUP phase (worktree removal)
7. Manual test: single team dry run

**Deliverables**:

- Command definition file
- Council reviewer persona
- State file schema
- Working SETUP/CLEANUP

**Dependencies**: Phase 1

### 9.3 Phase 3: Council Review System (6-8 hours)

**Objective**: Implement multi-reviewer scoring.

**Steps**:

1. Implement council invocation sequence
2. Implement score parsing from YAML frontmatter
3. Implement `aggregate_team_scores()` function
4. Implement `determine_merge_recommendation()` logic
5. Implement `rank_teams()` with tiebreakers
6. Implement results generation
7. Test with 2 teams, 3 reviewers

**Deliverables**:

- Scoring algorithm implementation
- Results generation
- Prototype validation (2 teams, 3 reviewers)

**Dependencies**: Phase 2

### 9.4 Phase 4: Full Orchestration (8-12 hours)

**Objective**: Enable parallel team coordination.

**Steps**:

1. Implement parallel team briefing
2. Implement team progress monitoring
3. Implement timeout warnings (30 min, 10 min)
4. Implement graceful abort handling
5. Implement state persistence across sessions
6. Scale to 3 teams, 7 reviewers
7. Full end-to-end test
8. Document learnings

**Deliverables**:

- Parallel orchestration working
- Timeout handling
- Full 3-team, 7-reviewer hackathon

**Dependencies**: Phase 3

---

## 10. Testing Strategy

### 10.1 Unit Tests

| Test | Purpose | Method |
|------|---------|--------|
| Parameter validation | Verify param ranges | Unit test function |
| Score calculation | Verify weighted average | Known inputs/outputs |
| Merge rules | Verify all rule paths | Edge case coverage |
| Tiebreaker | Verify ordering | Constructed ties |

### 10.2 Integration Tests

| Test | Purpose | Method |
|------|---------|--------|
| Worktree creation | Verify isolation | Create and verify |
| State updates | Verify consistency | Simulate transitions |
| Council invocation | Verify sequencing | Mock reviewers |
| Results generation | Verify output | Compare to expected |

### 10.3 End-to-End Tests

| Test | Scenario | Success Criteria |
|------|----------|------------------|
| Prototype run | 2 teams, 3 reviewers, 1h | All phases complete |
| Full run | 3 teams, 7 reviewers, 2h | Winner determined |
| Timeout test | Force timeout at 30 min | Graceful submission |
| Abort test | Abort mid-hackathon | State preserved |

### 10.4 Test Scenarios

**Scenario 1: Happy Path**

- 3 teams complete all phases
- All submit before timeout
- Council reviews cleanly
- Clear winner emerges

**Scenario 2: Timeout**

- 1 team doesn't finish
- Timeout triggers
- Partial submission accepted
- Council reviews what's available

**Scenario 3: Tie**

- 2 teams have same score
- Tiebreakers applied
- Winner determined
- Rationale documented

**Scenario 4: No Merge Eligible**

- All teams score < 3.0
- All marked ARCHIVE_ONLY
- Results documented
- Learnings extracted

---

## 11. Appendix

### A. Team Names

Default team names (Greek letters):

| Index | Name | Short |
|-------|------|-------|
| 1 | Alpha | A |
| 2 | Beta | B |
| 3 | Gamma | G |
| 4 | Delta | D |
| 5 | Epsilon | E |

### B. State Machine

```
HACKATHON STATES:
  SETUP → BRIEFING → IN_PROGRESS → SUBMISSION → COUNCIL → RESULTS → ARCHIVED

TEAM STATES:
  BRIEFED → IDEATION → SPIKE → UNDERSTAND → PLAN → DEVELOP → TEST →
  REVIEW → REFACTOR → APPROVE → DOCS → CLEANUP → SUBMITTED

COUNCIL STATES:
  PENDING → IN_PROGRESS → COMPLETE
```

### C. Error Codes

| Code | Error | Recovery |
|------|-------|----------|
| H001 | Worktree creation failed | Retry or manual cleanup |
| H002 | State file corruption | Restore from git |
| H003 | Timeout exceeded | Force submission |
| H004 | Council reviewer failed | Skip and note |
| H005 | Score aggregation error | Manual review |

### D. Token Budget Breakdown

| Component | Per Team | 3 Teams | Notes |
|-----------|----------|---------|-------|
| IDEATION | 1,000 | 3,000 | Haiku |
| SPIKE | 3,000 | 9,000 | Sonnet |
| UNDERSTAND/PLAN | 5,000 | 15,000 | Sonnet |
| DEVELOP | 10,000 | 30,000 | Sonnet |
| TEST/REVIEW | 5,000 | 15,000 | Sonnet |
| REFACTOR (x2) | 8,000 | 24,000 | Opus |
| DOCS/CLEANUP | 2,000 | 6,000 | Haiku |
| **Team subtotal** | **34,000** | **102,000** | |
| Council (7 x 3 teams) | | 63,000 | Opus |
| Orchestration | | 20,000 | Mixed |
| **Grand Total** | | **185,000** | |

### E. Related Documentation

| Document | Relationship |
|----------|--------------|
| PRD-HACKATHON-SYSTEM | Requirements |
| hackathon_system_plan.md | Implementation plan |
| hackathon_system_report.md | Research |
| AGENTS.md | Agent orchestration |
| GIT-WORKTREE-WORKFLOW.md | Worktree patterns |
| WORKFLOW_STAGES.md | Standard workflow |

---

*Technical Design Document*
*Feature Set 8: Hackathon System*
*Target: v1.1+*
*Status: Planning complete, implementation deferred*
