# Phase 2: JLPT Mastery Engine - Engagement Layer (v0.4.0)

## Overview

Build the "Engagement Layer" on top of Phase 1's SRS foundation to make studying addictive through XP rewards, level progression, mastery visualization, and daily goals.

**Target Version**: v0.4.0
**Estimated Duration**: 10-13 days across 3 sprints
**PRD Reference**: PRD-003 (Habit Formation System) - already exists in Draft status
**Created**: 2026-01-25
**Updated**: 2026-01-25
**Status**: Ready for Development
**Epic Issue**: [#45](https://github.com/cmbays/japanese-study-site/issues/45)

---

## Sprint Structure

| Sprint | Focus | Effort | Dependencies |
|--------|-------|--------|--------------|
| **Sprint 1** | XP & Levels System | 3-4 days | None |
| **Sprint 2** | Progress Dashboard | 5-6 days | Sprint 1 XP foundation |
| **Sprint 3** | Daily Goals | 2-3 days | Sprint 1 XP (can parallel with Sprint 2) |

---

## Sprint 1: XP & Levels System

### Features

- XP points earned per card (quality-dependent: 0/5/10/12)
- Streak bonus XP (+2 at 7+ days, +5 at 30+ days)
- Perfect session bonus (+50 XP)
- Level system (1-60) with exponential XP thresholds
- Level-up celebration animation
- Dashboard widget: Level badge + XP progress bar

### Schema Changes (storage.js v1.1.0)

```javascript
stats.xp: {
  total: 0,
  current_level: 1,
  xp_this_level: 0,
  xp_to_next_level: 100,
  last_level_up: null
}
```

### Files to Modify/Create

- `storage.js` - Schema v1.1.0, migration function
- `session-manager.js` - Award XP after review
- `xp-engine.js` (NEW) - XP calculation, level thresholds
- `index.html` - Level/XP widget in dashboard

### Acceptance Criteria

- [ ] XP awarded after each card review (quality-dependent)
- [ ] Streak bonus applied when streak >= 7 days
- [ ] Perfect session bonus awarded at 100% accuracy
- [ ] Level advances when XP threshold reached
- [ ] Level-up triggers celebration animation
- [ ] Dashboard shows current level + XP progress bar

---

## Sprint 2: Progress & Mastery Dashboard

### Features

- Topic mastery rings (SVG circular progress x 4 topics)
- JLPT mastery bars (horizontal bars N5-N2)
- Stage distribution pie/donut chart
- Mastery trend line (8-week history)
- "At Risk" panel (kanji that dropped stages)
- Study heatmap (GitHub-style 365-day calendar)
- Stats summary panel

### Schema Changes

```javascript
stats.daily_history: { "YYYY-MM-DD": { reviews, correct, xp_earned } }
stats.mastery_snapshots: [{ date, overall, n5, n4, n3, n2 }]
stats.at_risk_kanji: [{ character, dropped_from, dropped_to, date }]
```

### Files to Modify/Create

- `storage.js` - History CRUD, snapshot management
- `mastery-calculator.js` - Trend calculations
- `session-manager.js` - Track at-risk kanji on stage drops
- `dashboard.css` (NEW) - Chart styles, heatmap grid
- `index.html` - New visualization components

### Acceptance Criteria

- [ ] Topic mastery rings display 0-100% per topic
- [ ] JLPT bars show percentage with color coding
- [ ] Heatmap shows 365-day activity history
- [ ] Trend line shows past 8 weeks of mastery
- [ ] At-risk panel lists recently dropped kanji (max 20)
- [ ] All visualizations update after each session

---

## Sprint 3: Daily Goals

### Features

- Goal setting UI (modal: 5/10/20/custom cards)
- Goal progress bar on dashboard
- Goal completion celebration + bonus XP (10% of goal)
- Browser notification opt-in with configurable time

### Schema Changes

```javascript
settings.daily_goal: {
  enabled: true,
  target_cards: 20,
  notify_enabled: false,
  notify_time: "18:00"
}
stats.today.goal_completed: false
```

### Files to Modify/Create

- `storage.js` - Goal settings validation
- `goals-manager.js` (NEW) - Progress tracking, notifications
- `index.html` - Goal setting modal, progress bar

### Acceptance Criteria

- [ ] Goal setting modal allows 5/10/20/custom choice
- [ ] Progress bar shows X/Y cards completed
- [ ] Goal completion triggers celebration + bonus XP
- [ ] Browser notification permission can be requested
- [ ] Reminder sent at configured time if not studied

---

## Implementation Order

1. **Schema migration** (storage.js v1.1.0) - enables all features
2. **XP engine** - foundation for engagement
3. **Session manager XP integration** - wire into review flow
4. **Dashboard XP widget** - verify XP works
5. **Heatmap** - most visible engagement feature
6. **Mastery rings & bars** - leverage existing data
7. **Goals system** - builds on XP
8. **Trend line & at-risk** - polish features
9. **Notifications** - last (optional enhancement)

---

## Workflow Steps

Following project standard workflow:

### Step 1: PM Review PRD-003

- PRD-003 (Habit Formation System) already exists in Draft
- Review and update for any missing requirements
- Create PRD-005 for Sprint 2 Progress Dashboard (not covered in PRD-003)

### Step 2: Architect Creates TDD-003

- Detailed API contracts for xp-engine.js, goals-manager.js
- Chart rendering approach (CSS/SVG, no libraries)
- Data flow diagrams
- Test specifications

### Step 3: PM Creates GitHub Issues

- Epic issue for Phase 2
- Task issues per feature (T2.1, T2.2, etc.)
- Link to TDD-003 sections

### Step 4: Developer Implements

- Follow TDD specifications exactly
- Create test files alongside implementation
- Feature branch per sprint

### Step 5: Tester Verifies

- Unit tests for new modules
- Integration tests for XP flow
- Manual browser testing

### Step 6: Code Review & Merge

- Review against TDD requirements
- Merge to main, tag v0.4.0

### Step 7: Post-Completion

- PM closes GitHub issues
- Documenter updates CHANGELOG
- Sage extracts learnings

---

## Critical Files

### To Modify

- `/content/kanji/js/storage.js` - Schema v1.1.0, migration
- `/content/kanji/js/session-manager.js` - XP awards, history tracking
- `/content/kanji/js/mastery-calculator.js` - Trend snapshots
- `/content/kanji/index.html` - Major UI additions

### To Create

- `/content/kanji/js/xp-engine.js` - XP and level system
- `/content/kanji/js/goals-manager.js` - Daily goals
- `/content/kanji/css/dashboard.css` - Chart/heatmap styles
- `/docs/tdd/TDD-003-Habit-Formation.md` - Technical design
- `/docs/specs/PRD-005-Progress-Dashboard.md` - Dashboard PRD

---

## Verification Plan

### Unit Tests

- `test-xp-engine.html` - XP calculation, level thresholds
- `test-goals-manager.html` - Goal progress, completion

### Integration Tests

- Complete session → XP awarded → Level advances → UI updates
- Stage drop → At-risk panel updates
- Daily goal met → Celebration + bonus XP

### Browser Testing

- New user: XP starts at 0, Level 1
- Existing user: Migration preserves data
- Heatmap colors match review counts
- Level-up animation plays correctly
- Notifications work (Chrome/Firefox)

---

## Risk Mitigations

| Risk | Mitigation |
|------|------------|
| SVG charts complex | Start with CSS-only fallbacks |
| localStorage growth | Prune history > 365 days |
| Notification rejection | Graceful degradation to in-app |
| Migration data loss | Test migration with backup |

---

## Related Documentation

- **PRD-001**: JLPT Mastery Engine (Phase 1 foundation)
- **PRD-003**: Habit Formation System (XP, Levels, Goals)
- **TDD-001**: Phase 1 Technical Design
- **ROADMAP.md**: Phase 2 requirements (v0.4 Engagement milestone)
