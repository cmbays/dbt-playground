---
audience: [pm, architect]
priority: low
size: large
dependencies: []
last_updated: 2026-01-25
status: active
tags: [reference, planning, roadmap]
---

# Product Roadmap

**Japanese Study Site - Learning Platform**
**Last Updated:** 2026-01-25

---

## GitHub Project Tracking

### Quick Links

- **Milestones**: [View All Milestones](https://github.com/cmbays/japanese-study-site/milestones)
- **Issues**: [View All Issues](https://github.com/cmbays/japanese-study-site/issues)
- **Project Board**: [Japanese Study Site Roadmap](https://github.com/users/cmbays/projects/2)

### Active Milestones

| Milestone | Theme | Target | Status |
| --------- | ----- | ------ | ------ |
| [v0.3 - Foundation](https://github.com/cmbays/japanese-study-site/milestone/1) | SRS + Mastery | Q1 2026 | Active |
| [v0.4 - Engagement](https://github.com/cmbays/japanese-study-site/milestone/2) | XP + Levels + Dashboard | Q2 2026 | Planned |
| [v0.5 - Deep Learning](https://github.com/cmbays/japanese-study-site/milestone/3) | Mnemonics + Radicals | Q2 2026 | Planned |
| [v0.6 - Active Recall](https://github.com/cmbays/japanese-study-site/milestone/4) | Quiz + Audio | Q3 2026 | Planned |
| [v0.7 - Vocabulary](https://github.com/cmbays/japanese-study-site/milestone/5) | Vocab Mode | Q3 2026 | Planned |
| [v0.8 - Reading](https://github.com/cmbays/japanese-study-site/milestone/6) | Grammar + PWA | Q4 2026 | Planned |
| [v1.0 - Launch](https://github.com/cmbays/japanese-study-site/milestone/7) | Polish + Achievements | Q4 2026 | Planned |

### Label System

**Phase Labels:**

- `phase:1` - v0.3 Foundation
- `phase:2` - v0.4 Engagement
- `phase:3` - v0.5 Deep Learning
- `phase:4` - v0.6 Active Recall

**Status Labels:**

- `status:draft` - PRD in draft
- `status:approved` - PRD approved, ready for TDD
- `status:tdd` - Technical design phase
- `status:in-dev` - Implementation in progress
- `status:review` - Code review phase

**Persona Labels:**

- `persona:pm` - Product Manager
- `persona:architect` / `persona:arch` - Technical Architect
- `persona:developer` / `persona:dev` - Developer
- `persona:tester` - Quality Tester
- `persona:design` - Design Reviewer
- `persona:sensei` - Japanese Content Reviewer

### Project Board

The project board is user-level but **linked to the repository**, making it discoverable from the repository's Projects tab:
- **Direct Access**: [github.com/users/cmbays/projects/2](https://github.com/users/cmbays/projects/2)
- **Via Repository**: github.com/cmbays/japanese-study-site → Projects tab → "Japanese Study Site Roadmap"
- **Status**: All issues with `type:epic` and `type:task` labels are organized on the board

---

## Vision Statement

Build a **delightful, science-backed Japanese learning platform** that combines the retention power of spaced repetition with the engagement magic of gamification—creating a product that users genuinely want to return to every day.

### Core Differentiators

1. **Research-First Design** - Every feature grounded in learning science
2. **Habit Formation Focus** - Streaks, rewards, and cue-routine-reward loops
3. **Progressive Disclosure** - Start simple, unlock complexity as users advance
4. **JLPT Alignment** - Clear progression path (N5 → N1)

---

## Current State (v0.2)

### What Exists

- Basic kanji flashcard study mode
- 169 kanji with metadata (readings, meanings, JLPT levels)
- JLPT level filtering (N5-N2)
- Topic content: Home Life, Shopping, Restaurant, Travel
- Responsive design, shared CSS/JS

### What's Missing

- No spaced repetition (random card order)
- No progress tracking (cards don't remember state)
- No habit formation features (streaks, goals)
- No gamification (XP, levels, achievements)

---

## Phase 1: Foundation (v0.3)

**Theme:** Build the Learning Engine
**Milestone:** [v0.3 - Foundation](https://github.com/cmbays/japanese-study-site/milestone/1)
**PRDs:** [#7](https://github.com/cmbays/japanese-study-site/issues/7), [#8](https://github.com/cmbays/japanese-study-site/issues/8), [#9](https://github.com/cmbays/japanese-study-site/issues/9)

### Sprint 1: Spaced Repetition Core

**Goal:** Cards remember you

| Feature | Description | Effort |
|---------|-------------|--------|
| localStorage State | Persist card progress between sessions | S |
| SM-2 Algorithm | Calculate next review date per card | M |
| Card States | New → Learning → Review → Mastered | S |
| Due Cards Queue | Show cards due today first | M |
| Session Summary | Stats at end of each study session | S |

**Success Metric:** 100% of cards track individual progress

### Sprint 2: Self-Assessment UI

**Goal:** User controls their learning pace

| Feature | Description | Effort |
| --------- | ------------- | -------- |
| Rating Buttons | Again / Hard / Good / Easy | S |
| Interval Display | "Next review in X days" | S |
| Visual Feedback | Color-coded button effects | S |
| Undo Last Rating | Correct accidental taps | M |

**Success Metric:** Self-assessment data informs SRS intervals

### Sprint 3: Mastery Tracking System

**Goal:** Track true knowledge with bidirectional progress

| Feature | Description | Effort |
| --------- | ------------- | -------- |
| Mastery Stages | 8 stages: Locked → Burned | M |
| Stage Progression | Correct = advance, wrong = regress | M |
| Kanji Mastery Score | 0-100% per kanji | S |
| Topic Mastery Calc | Aggregate kanji mastery per topic | M |
| Stage Badge Display | Visual indicator on each card | S |
| Mastery Persistence | Store in localStorage with SRS data | S |

**Mastery Stage Definitions:**

```text
Locked (0%) → Lesson (0%) → Apprentice 1-4 (10-40%)
→ Guru 1-2 (50-70%) → Master (80%) → Enlightened (90%) → Burned (100%)
```text

**Regression Rules:**

- Again = Drop 2 stages
- Hard = Drop 1 stage
- Good/Easy = Advance 1 stage

**Success Metric:** Topic mastery % visible and updating based on review performance

### Sprint 4: Streak System (MVP)

**Goal:** Daily habit formation

| Feature | Description | Effort |
|---------|-------------|--------|
| Streak Counter | Consecutive days studied | S |
| Streak Display | Prominent on dashboard | S |
| Streak Persistence | Stored in localStorage | S |
| Streak Celebration | Animation on milestones (7, 30, 100) | M |

**Success Metric:** Streak visible and updating correctly

### Phase 1 Deliverables

- [ ] SRS algorithm functional
- [ ] localStorage persists all study data
- [ ] Self-assessment buttons on card back
- [ ] Mastery stages tracking per kanji
- [ ] Topic mastery aggregation
- [ ] Streak counter working
- [ ] Session summary screen

---

## Phase 2: Engagement Layer (v0.4)

**Theme:** Make It Addictive

### Sprint 1: XP & Levels

**Goal:** Tangible progress visualization

| Feature | Description | Effort |
|---------|-------------|--------|
| XP System | Points for cards studied | S |
| XP Bonuses | Extra for streaks, perfect sessions | S |
| Level System | XP thresholds (Lvl 1-60) | M |
| Level-Up Animation | Celebration on level increase | M |
| Dashboard Widget | Current level + XP to next | S |

### Sprint 2: Progress & Mastery Dashboard

**Goal:** Comprehensive progress view with mastery visualization

| Feature | Description | Effort |
|---------|-------------|--------|
| Topic Mastery Rings | Circular progress per topic (4 topics) | M |
| JLPT Mastery Bars | % mastery for N5, N4, N3, N2 | M |
| Stage Distribution | Pie chart: cards by mastery stage | M |
| Mastery Trend Line | Gaining or losing ground over time | M |
| "At Risk" Panel | Kanji that recently dropped stages | S |
| Study Heatmap | GitHub-style calendar | L |
| Stats Summary | Total cards, reviews, avg accuracy | S |

### Sprint 3: Daily Goals

**Goal:** Clear daily targets

| Feature | Description | Effort |
|---------|-------------|--------|
| Goal Setting | "Study X cards today" (5/10/20/custom) | S |
| Goal Progress | Visual progress bar | S |
| Goal Completion | Celebration animation + bonus XP | M |
| Notification Opt-in | Browser notification reminders | M |

### Phase 2 Deliverables

- [ ] XP earned and displayed
- [ ] Level system with visual progression
- [ ] JLPT progress bars
- [ ] Study heatmap
- [ ] Daily goal system

---

## Phase 3: Deep Learning (v0.5)

**Theme:** Learn Smarter, Not Harder

### Sprint 1: Mnemonic Foundation

**Goal:** Stories that stick

| Feature | Description | Effort |
|---------|-------------|--------|
| Mnemonic Field | Add to kanji data structure | S |
| Mnemonic Display | Show on card back | S |
| N5 Mnemonics | Write for 103 N5 kanji | L |
| N4 Mnemonics | Write for 66 N4 kanji | L |

### Sprint 2: Radical System

**Goal:** Unlock kanji composition

| Feature | Description | Effort |
|---------|-------------|--------|
| Radical Data | 50+ core radicals with meanings | M |
| Radical Display | Show breakdown on card | M |
| Radical Search | Find kanji by radical | M |
| Radical Lessons | Teach radicals before kanji | L |

### Sprint 3: Quality of Life

**Goal:** Power user features

| Feature | Description | Effort |
|---------|-------------|--------|
| Keyboard Shortcuts | Space, 1-4, arrows, Esc | S |
| Dark Mode | Theme toggle | S |
| Export Data | Download progress as JSON | S |
| Import Data | Restore progress from JSON | S |
| Font Size Options | Adjustable kanji display | S |

### Phase 3 Deliverables

- [ ] Mnemonics for all 169 kanji
- [ ] Radical breakdown on cards
- [ ] Keyboard navigation
- [ ] Dark mode
- [ ] Data export/import

---

## Phase 4: Active Recall (v0.6)

**Theme:** Testing Strengthens Memory

### Sprint 1: Quiz Mode

**Goal:** Multiple choice testing

| Feature | Description | Effort |
|---------|-------------|--------|
| Quiz Engine | Random question generation | M |
| Meaning Quiz | Kanji → pick meaning (4 options) | M |
| Reading Quiz | Kanji → pick reading (4 options) | M |
| Kanji Quiz | Meaning → pick kanji (4 options) | M |
| Quiz Stats | Track quiz performance | M |

### Sprint 2: Audio Enhancement

**Goal:** Pronunciation learning

| Feature | Description | Effort |
|---------|-------------|--------|
| TTS Integration | Web Speech API for readings | S |
| Auto-Play Toggle | Play on card flip (opt-in) | S |
| Repeat Button | Re-play pronunciation | S |
| Audio Quiz | Hear reading → pick kanji | M |

### Sprint 3: Similar Kanji

**Goal:** Reduce confusion

| Feature | Description | Effort |
|---------|-------------|--------|
| Confusables Data | Tag similar kanji pairs | M |
| Comparison View | Side-by-side display | M |
| Warning Badge | "Watch out for" on card | S |
| Confusables Quiz | Drill similar pairs | M |

### Phase 4 Deliverables

- [ ] Quiz mode with 4 types
- [ ] Audio pronunciation
- [ ] Similar kanji system
- [ ] Quiz integrated into SRS

---

## Phase 5: Content Expansion (v0.7 - v0.8)

**Theme:** Beyond Kanji

### v0.7: Vocabulary Mode

| Feature | Description | Effort |
|---------|-------------|--------|
| Vocab Data Structure | Words, readings, examples | M |
| Vocab Cards | Separate study mode | M |
| Compound Words | Words using learned kanji | L |
| Vocab SRS | Same algorithm, separate queue | M |

### v0.8: Reading & Grammar

| Feature | Description | Effort |
|---------|-------------|--------|
| Reading Passages | Short texts with learned kanji | L |
| Hover Definitions | Click word for meaning | M |
| Grammar Points | Basic N5 grammar | L |
| Grammar SRS | Spaced review of patterns | L |

### Phase 5 Deliverables

- [ ] Vocabulary study mode
- [ ] Compound word library
- [ ] Reading passages
- [ ] Basic grammar integration

---

## Phase 6: Platform Maturity (v0.9 - v1.0)

**Theme:** Polish & Scale

### v0.9: PWA & Accessibility

| Feature | Description | Effort |
|---------|-------------|--------|
| Service Worker | Offline capability | M |
| PWA Manifest | Installable app | S |
| Push Notifications | Study reminders | M |
| Screen Reader | ARIA labels, focus mgmt | M |
| Mobile Polish | Touch gestures, swipe | M |

### v1.0: Achievements & Social

| Feature | Description | Effort |
|---------|-------------|--------|
| Achievement System | Badges, milestones | M |
| Achievement Gallery | View earned badges | S |
| Daily Challenges | Bonus XP objectives | M |
| Share Progress | Social sharing (optional) | S |
| Onboarding Flow | New user experience | M |

### Phase 6 Deliverables

- [ ] Offline-capable PWA
- [ ] Full accessibility support
- [ ] Achievement system
- [ ] Polished onboarding
- [ ] v1.0 launch ready

---

## Future Horizons (v1.0+)

### User Accounts & Sync

- Cloud storage for progress
- Multi-device sync
- Social features (leaderboards)

### AI Integration

- "Explain My Answer" feature
- AI-generated personalized mnemonics
- Adaptive difficulty

### Native Apps

- iOS app (React Native / Swift)
- Android app
- Apple Watch complications

### Content Library

- Additional JLPT levels (N1 complete)
- More topics (10+)
- Audio from native speakers
- Video content

---

## Release Cadence

| Version | Theme | Target | Milestone |
|---------|-------|--------|-----------|
| v0.3 | Foundation | Q1 2026 | [Milestone #1](https://github.com/cmbays/japanese-study-site/milestone/1) |
| v0.4 | Engagement | Q2 2026 | [Milestone #2](https://github.com/cmbays/japanese-study-site/milestone/2) |
| v0.5 | Deep Learning | Q2 2026 | [Milestone #3](https://github.com/cmbays/japanese-study-site/milestone/3) |
| v0.6 | Active Recall | Q3 2026 | [Milestone #4](https://github.com/cmbays/japanese-study-site/milestone/4) |
| v0.7 | Vocabulary | Q3 2026 | [Milestone #5](https://github.com/cmbays/japanese-study-site/milestone/5) |
| v0.8 | Reading/Grammar | Q4 2026 | [Milestone #6](https://github.com/cmbays/japanese-study-site/milestone/6) |
| v1.0 | Launch | Q4 2026 | [Milestone #7](https://github.com/cmbays/japanese-study-site/milestone/7) |

---

## Success Metrics

### Engagement Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Daily Active Users | Growing | Analytics |
| Avg Session Length | 10+ min | localStorage |
| Streak Retention | 7+ days avg | Streak data |
| Return Rate | 50% weekly | Visit tracking |

### Learning Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Cards at Guru+ | 50% of studied | Mastery stage data |
| Cards Burned | Growing monthly | Mastery stage data |
| Topic Mastery | All topics 50%+ | Aggregated mastery |
| Mastery Regression | <10% per week | Stage drop tracking |
| Retention Rate | 85%+ | SRS performance |
| JLPT Completion | N5 in 3 months | Mastery progress bars |
| Quiz Accuracy | 80%+ | Quiz stats |

### Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Page Load | <2 sec | Performance testing |
| Error Rate | <1% | Console monitoring |
| Accessibility | WCAG 2.1 AA | Audit tools |
| Mobile Usability | 100% functional | Cross-device testing |

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Feature creep | High | Medium | Strict phase boundaries |
| localStorage limits | Low | High | Data export before 5MB |
| Browser compatibility | Medium | Medium | Progressive enhancement |
| Content quality | Medium | High | Japanese sensei review |
| User drop-off | High | High | Focus on Phase 2 first |

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-24 | Prioritize SRS + Streaks first | Research shows these drive retention |
| 2026-01-24 | Defer user accounts to v1.0+ | Keep client-side to reduce complexity |
| 2026-01-24 | Add mnemonics before audio | WaniKani success shows story power |
| 2026-01-24 | SM-2 over MEMORIZE | Simpler implementation, proven effective |
| 2026-01-24 | Bidirectional mastery (WaniKani-style) | Regression on failure creates meaningful stakes, accurate progress |
| 2026-01-24 | 8-stage mastery system | Matches WaniKani's proven model, granular progress visibility |
| 2026-01-24 | Topic-level mastery aggregation | Gives users clear per-topic goals, supports content completion |

---

## Research References

- [Spaced Repetition - Wikipedia](https://en.wikipedia.org/wiki/Spaced_repetition)
- [PNAS - Enhancing human learning via SRS optimization](https://www.pnas.org/doi/10.1073/pnas.1815156116)
- [Duolingo Gamification Case Study](https://www.youngurbanproject.com/duolingo-case-study/)
- [Psychology of Duolingo's Streak System](https://medium.com/@patricia-smith/the-psychology-behind-duolingos-addictive-learning-streak-system-ce29c5374d36)
- [Duolingo's Gamification Secrets - 60% engagement boost](https://www.orizon.co/blog/duolingos-gamification-secrets)

---

*This roadmap is a living document. Revisit after each phase to incorporate learnings and user feedback.*
