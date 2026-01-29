# PRD-003: Habit Formation System

**Status**: Complete (v0.4.0)
**Author**: PM (Claude)
**Created**: 2026-01-24
**Updated**: 2026-01-25

**Related Issue**: [Epic #45](https://github.com/cmbays/japanese-study-site/issues/45) (supersedes #9)
**Milestone**: [v0.4 - Engagement](https://github.com/cmbays/japanese-study-site/milestone/2)
**Technical Design**: [TDD-003](../tdd/TDD-003-Habit-Formation.md)
**Depends On**: PRD-001, PRD-002
**Related PRDs**: [PRD-005](PRD-005-Progress-Dashboard.md) (Dashboard Visualizations)

---

## Problem Statement

Language learning requires consistent, daily practice over months or years. But without habit-forming mechanisms, users study sporadically and eventually abandon the platform. Research shows that streaks increase user commitment by 60%, and the cue-routine-reward loop is essential for building lasting habits.

Currently, users have no incentive to return daily. There's no streak, no daily goal, no celebration for consistency. This is a critical gap—the most effective learning algorithm is worthless if users don't come back to use it.

## User Benefit

- **Daily Accountability**: Streak counter creates positive pressure to study
- **Clear Daily Target**: Know exactly what "done for today" means
- **Visible Progress**: XP and levels show cumulative achievement
- **Loss Aversion Motivation**: Protecting a streak drives return visits
- **Celebration & Reward**: Milestone animations make studying feel rewarding

## Target Users

- **Habit Builders**: Users trying to establish a daily study routine
- **Streak Chasers**: Users motivated by maintaining consecutive day counts
- **Goal-Oriented Learners**: Users who want clear daily targets
- **Casual Learners**: Even 5 minutes/day users benefit from habit structure

## JLPT Level Considerations

| Level | Considerations |
|-------|----------------|
| N5 | Lower daily goals (5-10 cards) to build habit without overwhelm |
| N4 | Standard goals (10-15 cards) as user builds competence |
| N3+ | Higher goals (15-25 cards) for serious exam prep |

**JLPT Progress as Reward:**
- Level-up celebrations should highlight JLPT progress
- "You're 75% through N5!" reinforces exam-relevant progress
- Daily goals should be tuned to realistic JLPT prep timelines

## User Stories

### Streak Stories
1. As a learner, I want to see my current streak so that I feel motivated to maintain it.
2. As a learner, I want to be warned when my streak is at risk so that I don't accidentally break it.
3. As a learner, I want to celebrate streak milestones so that long-term consistency feels rewarding.
4. As a learner, I want a "streak freeze" option so that one missed day doesn't destroy weeks of progress.

### Daily Goal Stories
5. As a learner, I want to set a daily card goal so that I know when I'm done for the day.
6. As a learner, I want to see my progress toward today's goal so that I can pace myself.
7. As a learner, I want to earn bonus XP for completing my goal so that finishing feels rewarding.
8. As a learner, I want to adjust my daily goal so that it fits my changing schedule.

### XP & Leveling Stories
9. As a learner, I want to earn XP for studying so that my effort is quantified.
10. As a learner, I want to level up as I earn XP so that I have long-term progression.
11. As a learner, I want to see my current level prominently so that I feel my progress.
12. As a learner, I want bonus XP for perfect reviews and streaks so that quality matters.

### Notification Stories
13. As a learner, I want optional daily reminders so that I don't forget to study.
14. As a learner, I want to set my preferred reminder time so that it fits my schedule.
15. As a learner, I want to disable reminders easily so that I'm not annoyed.

## Acceptance Criteria

### Streak System
- [ ] AC-1: Streak counter displays consecutive days studied
- [ ] AC-2: Streak increments when user completes at least 1 review on a new day
- [ ] AC-3: Streak resets to 0 if a day is missed (no study activity)
- [ ] AC-4: Streak milestone celebrations at: 7, 14, 30, 60, 90, 180, 365 days
- [ ] AC-5: Fire/flame animation displays when streak is active
- [ ] AC-6: "Streak at risk" warning appears after 6 PM local time if no study today

### Streak Freeze
- [ ] AC-7: Users earn 1 streak freeze per 7 days of consecutive study
- [ ] AC-8: Maximum 2 streak freezes can be held at once
- [ ] AC-9: Streak freeze automatically activates on missed day (if available)
- [ ] AC-10: Dashboard shows current streak freeze count

### Daily Goals
- [ ] AC-11: Default daily goal is 10 cards (new + review)
- [ ] AC-12: User can set goal to: 5, 10, 15, 20, 25, or custom number
- [ ] AC-13: Progress bar shows cards completed / goal
- [ ] AC-14: Goal completion triggers celebration animation
- [ ] AC-15: Completing goal awards 50 bonus XP

### XP System
- [ ] AC-16: Base XP: 10 per card reviewed
- [ ] AC-17: Bonus XP: +5 for "Good" rating, +10 for "Easy" rating
- [ ] AC-18: Streak bonus: +10% XP per 7-day streak tier (max +50% at 35+ days)
- [ ] AC-19: Daily goal bonus: +50 XP for completing daily goal
- [ ] AC-20: Perfect session bonus: +25 XP if all reviews are Good or Easy

### Level System
- [ ] AC-21: Levels 1-60 (matching WaniKani-style progression)
- [ ] AC-22: XP thresholds increase per level (e.g., L1: 100, L2: 250, L3: 500...)
- [ ] AC-23: Level displayed on dashboard with progress bar to next level
- [ ] AC-24: Level-up triggers celebration animation
- [ ] AC-25: Level milestones (10, 20, 30, 40, 50, 60) trigger special celebration

### Notifications (Optional)
- [ ] AC-26: User can enable browser notifications (with permission prompt)
- [ ] AC-27: User can set preferred notification time (default: 7 PM local)
- [ ] AC-28: Notification text: "Don't break your X-day streak! 🔥"
- [ ] AC-29: Notification only sends if user hasn't studied today
- [ ] AC-30: User can disable notifications in settings

### Data Persistence
- [ ] AC-31: Streak count persists across sessions
- [ ] AC-32: XP and level persist across sessions
- [ ] AC-33: Daily goal setting persists
- [ ] AC-34: Study dates tracked for streak calculation

## Scope

### In Scope
- Streak counter with daily increment logic
- Streak milestone celebrations (7, 30, 100 days, etc.)
- Streak freeze system (earn and use)
- Daily goal setting with progress indicator
- XP system with bonuses for quality and consistency
- Level system (1-60) with progression curve
- Basic browser notification support
- Streak-at-risk warning

### Out of Scope
- Push notifications (requires service worker - v0.8 PWA)
- Social sharing of streaks
- Leaderboards
- Weekly/monthly goals (daily only for now)
- Streak repair (paying to fix broken streak)
- Widget for lock screen (native app only)

### Future Considerations
- Streak repair purchase (if monetizing)
- Weekly challenges with bonus XP
- Friend streak comparisons (with accounts)
- Customizable goal types (time-based, accuracy-based)
- Achievement badges (separate from levels)

## UI/UX Specifications

### Dashboard Layout
```
┌─────────────────────────────────────────────┐
│  Level 12 ████████░░░░ 2,450 / 3,000 XP     │
│                                             │
│  🔥 14 Day Streak          ❄️ 1 Freeze      │
│                                             │
│  Today's Goal: ████████░░ 8/10 cards        │
│                                             │
│  JLPT Progress:                             │
│  N5 ████████░░ 82%                          │
│  N4 ████░░░░░░ 35%                          │
│                                             │
│  [Start Studying]                           │
└─────────────────────────────────────────────┘
```

### Streak Celebration (30 Days)
```
┌─────────────────────────────────────────────┐
│                 🎉 🔥 🎉                     │
│                                             │
│          30 DAY STREAK!                     │
│                                             │
│    You've studied for a full month!         │
│    That's serious dedication.               │
│                                             │
│    Streak Bonus: +30% XP                    │
│    Earned: 1 Streak Freeze ❄️               │
│                                             │
│           [Keep Going!]                     │
└─────────────────────────────────────────────┘
```

### Streak at Risk Warning
```
┌─────────────────────────────────────────────┐
│  ⚠️ Your 14-day streak is at risk!          │
│                                             │
│  Study at least 1 card before midnight      │
│  to keep your streak alive.                 │
│                                             │
│  [Study Now]  [Use Streak Freeze]           │
└─────────────────────────────────────────────┘
```

## XP Table Reference

| Level | XP Required | Cumulative XP |
|-------|-------------|---------------|
| 1 | 0 | 0 |
| 2 | 100 | 100 |
| 3 | 150 | 250 |
| 4 | 200 | 450 |
| 5 | 300 | 750 |
| 10 | 600 | 3,750 |
| 20 | 1,200 | 15,000 |
| 30 | 2,000 | 35,000 |
| 40 | 3,000 | 65,000 |
| 50 | 4,500 | 110,000 |
| 60 | 6,000 | 175,000 |

*Formula approximation: `xp_for_level(n) = 50 * n * (1 + 0.1 * floor(n/10))`*

## Content Requirements

- **Celebration Messages**: Copy for streak milestones, level-ups, goal completion
- **Notification Text**: Engaging reminder messages
- **No Japanese content needed**: System operates on activity data

### Sample Celebration Messages

**Streak Milestones:**
- 7 days: "One week strong! You're building a real habit. 🔥"
- 30 days: "A full month! Your dedication is paying off. 🏆"
- 100 days: "100 DAYS! You're in the top 1% of learners. 🌟"
- 365 days: "ONE YEAR! You're a Japanese learning legend. 👑"

**Level-Ups:**
- "Level up! You're now Level X. Keep climbing! 📈"
- Level 10: "Double digits! You're getting serious. 🎯"
- Level 30: "Halfway to max level. Impressive! 💪"
- Level 60: "MAX LEVEL! You've mastered the system. 🏅"

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| 7-day streak retention | 40% of active users | Streak data |
| 30-day streak retention | 15% of active users | Streak data |
| Daily goal completion | 70% of sessions | Goal data |
| Notification opt-in | 30% of users | Notification permission |
| Return rate (next day) | 50% of users | Visit tracking |
| Average streak length | 10+ days | Streak data |

## Dependencies

- **PRD-001**: SRS engine for tracking reviews
- **PRD-002**: Session experience for triggering XP/streak updates
- **Browser Notification API**: For optional reminders
- **Date/time handling**: For streak day boundaries

## Sprint Allocation

This PRD is implemented across Phase 2 sprints:

| Sprint | Features | Effort |
|--------|----------|--------|
| **Sprint 1** | XP System, Level System, Streak System (with freezes), Dashboard widgets | 4-5 days |
| **Sprint 2** | Progress Dashboard visualizations (see [PRD-005](PRD-005-Progress-Dashboard.md)) | 5-6 days |
| **Sprint 3** | Daily Goals, Browser Notifications | 2-3 days |

**Note**: Sprint 1 bundles XP, Levels, AND Streaks together as the core engagement foundation. All three systems are interdependent (streak bonuses affect XP, XP determines level, etc.).

## Technical Considerations

### Day Boundary
- Use local midnight as day boundary for streak calculation
- Store dates in ISO format with timezone
- "Today" defined as midnight-to-midnight local time

### localStorage Schema Extension (v1.1.0)

Extends the existing Phase 1 `stats` object (see TDD-001 §2.5):

```javascript
// Added to existing stats object
stats: {
  // ... existing Phase 1 fields (total_reviews, today, stage_distribution, etc.)

  // NEW: XP & Level System
  xp: {
    total: 12500,              // Lifetime XP earned
    current_level: 12,         // Current level (1-60)
    xp_this_level: 450,        // XP earned toward next level
    xp_to_next_level: 1200,    // XP needed for next level
    last_level_up: "2026-01-20T15:30:00Z"  // ISO timestamp
  },

  // NEW: Streak System
  streak: {
    current: 14,               // Current streak days
    longest: 30,               // Personal best streak
    last_study_date: "2026-01-24",  // YYYY-MM-DD format
    freezes_available: 1,      // Streak freezes (0-2)
    freeze_used_date: null     // Date freeze was last used
  },

  // NEW: Daily History (for heatmap, trends)
  daily_history: {
    "2026-01-24": { reviews: 45, correct: 38, xp_earned: 520 },
    "2026-01-23": { reviews: 30, correct: 28, xp_earned: 340 }
    // ... last 400 days
  }
}

// Added to existing settings object
settings: {
  // ... existing Phase 1 fields

  // NEW: Daily Goal Settings
  daily_goal: {
    enabled: true,
    target_cards: 10,          // 5, 10, 15, 20, 25, or custom
    notify_enabled: false,
    notify_time: "19:00"       // HH:MM local time
  }
}
```

**Migration Note**: Schema version bumps from 1.0.0 → 1.1.0. See TDD-003 for migration strategy.

## Open Questions (Resolved)

| Question | Decision | Rationale |
|----------|----------|-----------|
| Streak reset time? | Midnight local time | Standard approach, matches user expectations |
| Streak freezes earnable or purchasable? | Earnable only (1 per 7 days, max 2) | Keeps system fair without monetization |
| XP curve? | Tiered exponential (see XP Table Reference) | Balances early progress with long-term challenge |
| Beginner protection? | No | Keep it simple; streak freezes provide safety net |

---

## Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2026-01-24 | PM (Claude) | Initial draft |
| 2026-01-25 | PM (Claude) | Updated for Phase 2: Sprint allocation, schema v1.1.0 alignment, resolved open questions, added PRD-005 reference |
