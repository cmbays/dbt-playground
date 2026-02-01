# PRD: Hackathon System

**Document ID**: PRD-HACKATHON-SYSTEM
**Feature Set**: 8
**Version**: 1.0
**Status**: Draft (Deferred to v1.1+)
**Author**: Product Manager
**Date**: 2026-02-01

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Goals and Non-Goals](#2-goals-and-non-goals)
3. [User Stories](#3-user-stories)
4. [Use Cases](#4-use-cases)
5. [Functional Requirements](#5-functional-requirements)
6. [Non-Functional Requirements](#6-non-functional-requirements)
7. [Acceptance Criteria](#7-acceptance-criteria)
8. [Out of Scope](#8-out-of-scope)
9. [Dependencies](#9-dependencies)
10. [Success Metrics](#10-success-metrics)
11. [Open Questions](#11-open-questions)
12. [Appendix](#appendix)

---

## 1. Problem Statement

### 1.1 Current State

The dbt-playground project has robust infrastructure for:

- Sequential agent workflows via `/orchestrate`
- Parallel development via git worktrees
- Code review via single reviewer agents
- Learning extraction via Sage

However, when facing open-ended problems where the "best" solution is unclear, the current workflow has limitations:

| Limitation | Impact |
|------------|--------|
| Single solution path | May miss innovative approaches |
| No competitive exploration | Solutions tend toward safe, incremental |
| Limited perspectives on review | One reviewer bias |
| No structured comparison | Hard to evaluate alternatives |

### 1.2 Problem Definition

**Problem**: When exploring novel approaches or validating assumptions, there is no mechanism for parallel competitive exploration that would surface diverse solutions and enable objective comparison.

**Who is affected**:

- Chris (project owner) seeking innovative solutions
- Agent teams that could learn from alternative approaches
- The project's long-term innovation capacity

**Impact of not solving**:

- Suboptimal solutions go unchallenged
- Innovation stagnates in incremental improvements
- No mechanism to test "what would Team B have done differently"

### 1.3 Opportunity

Hackathon-style competitive exploration unlocks:

- Discovery of non-obvious solutions
- Best-of-breed selection from multiple attempts
- Cross-team learning and pattern sharing
- Rapid prototyping with lower risk tolerance

---

## 2. Goals and Non-Goals

### 2.1 Goals

| Goal | Priority | Success Indicator |
|------|----------|-------------------|
| Enable parallel competitive teams | P0 | 3+ teams work simultaneously |
| Provide objective evaluation | P0 | Council scoring with clear rubric |
| Capture diverse approaches | P1 | Multiple distinct solutions submitted |
| Extract learnings | P1 | Patterns documented from all teams |
| Determine clear winner | P2 | Consensus algorithm produces ranking |

### 2.2 Non-Goals

| Non-Goal | Rationale |
|----------|-----------|
| Replace standard workflow | Hackathons are for exploration, not routine work |
| Merge all submissions | Only winning approach merges |
| Real-time collaboration between teams | Teams work in isolation |
| Human council members | All reviewers are agents |
| Production-critical features | Hackathon work requires additional review |

---

## 3. User Stories

### 3.1 Primary User Stories

**US-1: Launch Hackathon**
> As Chris, I want to launch a hackathon with a specific theme so that multiple agent teams compete to solve the same problem.

**Acceptance Criteria**:

- [ ] Can specify theme/challenge in plain text
- [ ] Can specify number of teams (2-5)
- [ ] Can specify duration (1-4 hours)
- [ ] Each team gets isolated worktree
- [ ] Each team understands the challenge

**US-2: Team Development**
> As a hackathon team, I want to go through a full development cycle so that I can produce a quality submission.

**Acceptance Criteria**:

- [ ] IDEATION phase for brainstorming
- [ ] SPIKE phase for rapid prototyping
- [ ] Full UNDERSTAND/PLAN/DEVELOP/TEST cycle
- [ ] REVIEW/REFACTOR iterations (up to 5)
- [ ] APPROVE/DOCS/CLEANUP for submission

**US-3: Council Review**
> As Chris, I want multiple reviewers to score each submission so that the evaluation is objective and thorough.

**Acceptance Criteria**:

- [ ] 7 council reviewers score each submission
- [ ] Scoring uses standardized rubric
- [ ] Each reviewer provides detailed feedback
- [ ] Scores aggregated for ranking

**US-4: Results Documentation**
> As Chris, I want hackathon results documented so that learnings are preserved and the winning approach is clear.

**Acceptance Criteria**:

- [ ] Results saved to `docs/hackathons/`
- [ ] Per-team feedback included
- [ ] Winner announced with rationale
- [ ] Overall learnings captured

### 3.2 Secondary User Stories

**US-5: Prototype Validation**
> As Chris, I want to run a simplified hackathon so that I can validate the system before full implementation.

**Acceptance Criteria**:

- [ ] 2-team minimum
- [ ] 3-reviewer council option
- [ ] 2-hour duration option
- [ ] Simplified theme support

**US-6: Mid-Hackathon Status**
> As Chris, I want to check hackathon progress so that I know how teams are doing.

**Acceptance Criteria**:

- [ ] Central state file shows all team phases
- [ ] Time remaining visible
- [ ] Refactor cycle count per team
- [ ] Blockers highlighted

---

## 4. Use Cases

### 4.1 UC-1: New Feature Exploration

**Scenario**: Chris wants to explore different approaches to building a patient cohort analytics feature.

**Actors**: Chris, 3 Agent Teams, 7 Council Reviewers

**Preconditions**:

- v1.0 multi-agent coordination operational
- Clear theme formulated
- 4-hour block available

**Flow**:

```
1. Chris invokes: /hackathon "Build patient cohort analytics" --teams 3 --duration 4h

2. SETUP Phase:
   - System creates worktrees: dbt-playground--team-alpha, --team-beta, --team-gamma
   - System creates branches: hackathon/2026-02-01/team-alpha, etc.
   - System initializes HACKATHON_STATE.md

3. BRIEFING Phase:
   - Each team receives theme and constraints
   - Teams acknowledge and begin IDEATION

4. DEVELOPMENT Phase (parallel):
   - Team Alpha: Explores dimension-first approach
   - Team Beta: Explores fact-first approach
   - Team Gamma: Explores hybrid approach
   - Each team progresses through IDEATION -> SPIKE -> full cycle
   - State file updates with progress

5. SUBMISSION Phase:
   - Teams create hackathon_submission.md
   - Teams mark ready for review
   - Worktrees preserved for council access

6. COUNCIL Phase:
   - 7 reviewers invoked sequentially
   - Each reviewer scores all 3 submissions
   - Reviews written to temp/AGENT_REPORTS/hackathon-2026-02-01/council/

7. RESULTS Phase:
   - Scores aggregated
   - Merge recommendation calculated
   - HACKATHON_RESULTS.md generated
   - Winner announced

8. CLEANUP Phase:
   - Worktrees for losing teams removed
   - Winning team's branch ready for merge review
   - State file archived
```

**Postconditions**:

- Results documented in `docs/hackathons/2026_02_01_cohort_analytics/`
- Winning approach ready for merge consideration
- Learnings extracted from all teams

### 4.2 UC-2: Architecture Decision Exploration

**Scenario**: The team is unsure whether to use incremental or full-refresh models for a new data source.

**Flow**:

1. Theme: "Implement stripe_payments model - compete: incremental vs full-refresh"
2. Team Alpha: Implements incremental
3. Team Beta: Implements full-refresh
4. Council reviews for: performance, maintainability, correctness
5. Winner demonstrates superior approach for this use case

**Value**: Eliminates guesswork, provides evidence-based decision.

### 4.3 UC-3: Rapid Prototyping Competition

**Scenario**: Explore creative solutions for a complex data transformation.

**Flow**:

1. Theme: "Transform nested JSON claims data into flat dimensional model"
2. 3 teams have 2 hours to prototype solutions
3. Council evaluates innovation and feasibility
4. Best ideas inform actual implementation (may not merge directly)

**Value**: SPIKE-style exploration with structured comparison.

---

## 5. Functional Requirements

### 5.1 `/hackathon` Command

**FR-1**: Command Invocation

| Requirement | Description |
|-------------|-------------|
| FR-1.1 | Accept theme as required argument (string) |
| FR-1.2 | Accept `--teams N` parameter (default: 3, range: 2-5) |
| FR-1.3 | Accept `--duration Xh` parameter (default: 4h, range: 1-8h) |
| FR-1.4 | Validate parameters before proceeding |
| FR-1.5 | Display confirmation with parameters |

**Example**:

```
/hackathon "Build patient cohort analytics" --teams 3 --duration 4h
```

**FR-2**: SETUP Phase

| Requirement | Description |
|-------------|-------------|
| FR-2.1 | Create worktree per team: `dbt-playground--team-{name}` |
| FR-2.2 | Create branch per team: `hackathon/YYYY-MM-DD/team-{name}` |
| FR-2.3 | Initialize `temp/HACKATHON_STATE.md` |
| FR-2.4 | Create `temp/AGENT_REPORTS/hackathon-YYYY-MM-DD/` folders |
| FR-2.5 | Report setup completion |

**FR-3**: Team Development Cycle

| Requirement | Description |
|-------------|-------------|
| FR-3.1 | IDEATION: Generate 3+ approaches in `ideas.md` |
| FR-3.2 | SPIKE: Create prototype in `spike/` folder |
| FR-3.3 | UNDERSTAND/PLAN/DEVELOP/TEST: Standard workflow |
| FR-3.4 | REVIEW/REFACTOR: Up to 5 iterations |
| FR-3.5 | APPROVE: Team lead validates submission |
| FR-3.6 | DOCS: Create `hackathon_submission.md` |
| FR-3.7 | CLEANUP: Remove spike code |

**FR-4**: Council Review

| Requirement | Description |
|-------------|-------------|
| FR-4.1 | Invoke 7 council reviewers sequentially |
| FR-4.2 | Each reviewer scores all submissions |
| FR-4.3 | Write reviews to `council/reviewer-{N}/` |
| FR-4.4 | Use standardized `HACKATHON_RUBRIC.md` |
| FR-4.5 | Include Y/N merge recommendation |

**FR-5**: Results Documentation

| Requirement | Description |
|-------------|-------------|
| FR-5.1 | Aggregate scores using weighted algorithm |
| FR-5.2 | Apply merge rules (>=3.0 avg, 4/7 votes, no category=1) |
| FR-5.3 | Generate `HACKATHON_RESULTS.md` |
| FR-5.4 | Archive to `docs/hackathons/YYYY_MM_DD_{topic}/` |
| FR-5.5 | Announce winner with rationale |

### 5.2 State Management

**FR-6**: HACKATHON_STATE.md

| Requirement | Description |
|-------------|-------------|
| FR-6.1 | YAML frontmatter with hackathon metadata |
| FR-6.2 | Per-team section with: worktree, branch, phase, refactor_cycle |
| FR-6.3 | Council review status (N/7 complete) |
| FR-6.4 | Timeline log of key events |
| FR-6.5 | Update on every phase transition |

**FR-7**: Timeout Handling

| Requirement | Description |
|-------------|-------------|
| FR-7.1 | Track elapsed time against duration |
| FR-7.2 | Warning at 30 min, 10 min remaining |
| FR-7.3 | Grace period (15 min) after duration |
| FR-7.4 | Force submission after grace period |

---

## 6. Non-Functional Requirements

### 6.1 Resource Consumption

| Requirement | Target | Rationale |
|-------------|--------|-----------|
| NFR-1 | Token budget <250k per hackathon | Cost management |
| NFR-2 | Use cheaper models for routine phases | Token optimization |
| NFR-3 | Limit refactor cycles to 3 (prototype) | Time management |
| NFR-4 | Max 4-hour duration (standard) | Human attention span |

**Model Allocation**:

| Phase | Model | Tokens (est.) |
|-------|-------|---------------|
| IDEATION, DOCS, CLEANUP | Haiku | 1,000 |
| UNDERSTAND, SPIKE | Sonnet | 3,000 |
| PLAN, DEVELOP, TEST | Sonnet | 5,000 |
| REVIEW, REFACTOR | Opus | 5,000 |
| Council Review | Opus | 3,000 |

### 6.2 Coordination

| Requirement | Target | Rationale |
|-------------|--------|-----------|
| NFR-5 | Teams work in isolation | Prevent conflicts |
| NFR-6 | No cross-team communication | Fair competition |
| NFR-7 | Central state updates <1 min lag | Real-time visibility |
| NFR-8 | Council invoked sequentially | Avoid race conditions |

### 6.3 Reliability

| Requirement | Target | Rationale |
|-------------|--------|-----------|
| NFR-9 | Graceful abort preserves progress | Recover from failures |
| NFR-10 | Partial submission allowed | Better than nothing |
| NFR-11 | Worktree cleanup on failure | Prevent clutter |
| NFR-12 | State persistence across sessions | Support interrupts |

### 6.4 Observability

| Requirement | Target | Rationale |
|-------------|--------|-----------|
| NFR-13 | Real-time phase visibility | Chris monitoring |
| NFR-14 | Token consumption tracking | Budget awareness |
| NFR-15 | Council progress indicator | Patience management |
| NFR-16 | Final results accessible | Documentation value |

---

## 7. Acceptance Criteria

### 7.1 Minimum Viable Product (Prototype)

| ID | Criterion | Verification |
|----|-----------|--------------|
| AC-MVP-1 | 2 teams complete parallel development | Both submit |
| AC-MVP-2 | Submissions follow template | Template fields populated |
| AC-MVP-3 | 3 reviewers score using rubric | All scores recorded |
| AC-MVP-4 | Winner determined by algorithm | Clear ranking |
| AC-MVP-5 | Results documented | File in docs/hackathons/ |

### 7.2 Full System

| ID | Criterion | Verification |
|----|-----------|--------------|
| AC-FS-1 | `/hackathon` command accepts parameters | Command parses correctly |
| AC-FS-2 | 3+ teams work in parallel | No merge conflicts |
| AC-FS-3 | Teams complete full development cycle | All phases logged |
| AC-FS-4 | 7 council reviewers score submissions | 21 reviews generated |
| AC-FS-5 | Scores aggregated correctly | Math verified |
| AC-FS-6 | Merge rules applied correctly | Decisions documented |
| AC-FS-7 | Winning submission merges cleanly | No conflicts on merge |
| AC-FS-8 | Results archived correctly | Folder structure correct |
| AC-FS-9 | Learnings extracted | Sage invoked |
| AC-FS-10 | Worktrees cleaned up | No orphaned worktrees |

### 7.3 Edge Cases

| ID | Criterion | Verification |
|----|-----------|--------------|
| AC-EC-1 | Timeout triggers graceful submission | Partial work preserved |
| AC-EC-2 | Team dropout handled | Remaining teams continue |
| AC-EC-3 | Council tie resolved | Tiebreaker applied |
| AC-EC-4 | All submissions fail merge criteria | Archive-only documented |
| AC-EC-5 | Abort mid-hackathon | State preserved for resume |

---

## 8. Out of Scope

### 8.1 Initial Version Exclusions

| Exclusion | Rationale | Future Consideration |
|-----------|-----------|---------------------|
| Real-time team chat | Breaks isolation fairness | v1.2+ if needed |
| Human council members | Adds coordination complexity | v1.2+ optional |
| Public leaderboards | Privacy/complexity | v1.2+ if useful |
| Cross-hackathon statistics | Requires history tracking | v1.3+ |
| Custom rubric per hackathon | Standardization first | v1.2+ |
| Automated theme generation | Manual themes sufficient | v1.3+ |

### 8.2 Explicit Non-Features

| Non-Feature | Rationale |
|-------------|-----------|
| Production deployment | Hackathon code needs additional review |
| Automatic merge of winner | Manual review required |
| Team preference for personas | Random/balanced assignment |
| Multiple winners | Single winner for clarity |
| Prize/reward system | Not needed for agent teams |

---

## 9. Dependencies

### 9.1 Hard Dependencies (Blocking)

| Dependency | Feature Set | Required For |
|------------|-------------|--------------|
| Multi-Agent Coordination | FS6 | Parallel team orchestration |
| Git Worktrees | Existing | Team isolation |
| Supervisor Agent | Existing | Hackathon orchestration |

### 9.2 Soft Dependencies (Enhance)

| Dependency | Feature Set | Enhancement |
|------------|-------------|-------------|
| Metrics Dashboard | FS5 | Scoring visualization |
| Agent Memory | FS1 | Learning persistence |
| Kanban Workflow | FS2 | Team workflow discipline |
| QA Enforcement | FS3 | Submission quality |

### 9.3 Infrastructure Dependencies

| Component | Status | Notes |
|-----------|--------|-------|
| Git worktree support | Ready | Fully operational |
| Inter-agent reports | Ready | Templates exist |
| Code reviewer persona | Ready | Base for council |
| `/orchestrate` command | Ready | Pattern for `/hackathon` |

---

## 10. Success Metrics

### 10.1 Launch Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| First hackathon completion | 100% | All phases complete |
| No blocking failures | Yes | No unrecoverable errors |
| Results documented | Yes | File created |
| Positive user feedback | >4/5 | Post-hackathon survey |

### 10.2 Operational Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Hackathons per quarter | 2+ | Count |
| Average team count | 3 | Average N |
| Council agreement rate | >80% | Score variance <1.0 |
| Merge success rate | >90% | Clean merges / winners |
| Token budget adherence | <250k | Actual vs budget |

### 10.3 Value Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Innovative solutions discovered | 1+ per hackathon | Novel approaches |
| Patterns extracted | 3+ per hackathon | LEARNINGS.md entries |
| Cross-team learning | Evidence of adoption | Pattern reuse |
| Decision quality improvement | Subjective | Chris assessment |

---

## 11. Open Questions

### 11.1 Design Questions

| Question | Options | Impact | Resolution |
|----------|---------|--------|------------|
| Fixed or variable council size? | 3/5/7 | Review quality vs cost | Default 7, --reviewers flag |
| Team names assignment? | Random, sequential, user-defined | UX | Greek letters (Alpha, Beta, Gamma) |
| Theme constraints format? | Free text, template, checklist | Clarity | Free text with optional constraints |

### 11.2 Technical Questions

| Question | Considerations | Resolution |
|----------|----------------|------------|
| Sequential vs parallel council? | Parallel faster but complex | Sequential (simpler) |
| State persistence mechanism? | YAML file vs SQLite | YAML file (consistency) |
| Error recovery strategy? | Retry vs abort vs skip | Graceful degradation |

### 11.3 Operational Questions

| Question | Considerations | Resolution |
|----------|----------------|------------|
| When to run hackathons? | Exploration needs, time availability | User-triggered |
| How to select themes? | Roadmap items, experiments, challenges | User-defined |
| Feedback loop to teams? | During vs after competition | After only (fairness) |

---

## Appendix

### A. Glossary

| Term | Definition |
|------|------------|
| Hackathon | Competitive parallel team event |
| Council | Group of 7 reviewer agents |
| Team | Single agent workflow in isolated worktree |
| Theme | Challenge/problem statement for hackathon |
| Submission | Team's completed work + documentation |
| Rubric | Standardized scoring criteria |

### B. Related Documents

| Document | Relationship |
|----------|--------------|
| `hackathon_system_report.md` | Research report |
| `hackathon_system_plan.md` | Implementation plan |
| `hackathon_system_TDD.md` | Technical design |
| `UPDATED_IDEAS.md` | Feature prioritization |
| `GIT-WORKTREE-WORKFLOW.md` | Worktree patterns |
| `AGENTS.md` | Agent orchestration |

### C. Template References

| Template | Purpose |
|----------|---------|
| `HACKATHON_RUBRIC.md` | Scoring criteria |
| `HACKATHON_SUBMISSION.md` | Team submission |
| `COUNCIL_REVIEW.md` | Reviewer output |
| `HACKATHON_RESULTS.md` | Final documentation |

### D. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-01 | PM | Initial draft |

---

*For Architect: Read this PRD, then create TDD for Hackathon System.*
