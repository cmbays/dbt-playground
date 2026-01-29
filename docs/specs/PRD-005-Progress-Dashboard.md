# PRD-005: Progress Dashboard

**Status**: Complete (v0.4.0)
**Author**: PM (Claude)
**Created**: 2026-01-25
**Updated**: 2026-01-25

**Related Issue**: [Epic #45](https://github.com/cmbays/japanese-study-site/issues/45) (Sprint 2 tasks: #51-#55)
**Milestone**: [v0.4 - Engagement](https://github.com/cmbays/japanese-study-site/milestone/2)
**Technical Design**: [TDD-003](../tdd/TDD-003-Habit-Formation.md)
**Depends On**: PRD-001, PRD-003
**Part Of**: Phase 2 - Engagement Layer (Sprint 2)

---

## Problem Statement

Users studying kanji need visibility into their learning progress beyond simple session statistics. Without rich visualizations, learners can't:

1. **See patterns** in their study consistency (Am I studying regularly?)
2. **Track mastery growth** over time (Am I actually improving?)
3. **Identify trouble areas** (Which kanji keep falling back?)
4. **Celebrate milestones** (How far have I come in each JLPT level?)

Currently, the dashboard shows only basic session stats. Users have no way to see their 365-day study history, mastery trends, or at-risk kanji that need extra attention. This lack of visibility reduces motivation and makes it harder to optimize study habits.

## User Benefit

- **Visual Motivation**: Heatmap shows study consistency at a glance (GitHub-style)
- **Progress Clarity**: Mastery rings and bars show exactly how far along in each JLPT level
- **Early Warning**: At-risk panel highlights kanji that need review before they're forgotten
- **Trend Awareness**: 8-week trend line shows if mastery is improving or declining
- **Topic Focus**: Per-topic mastery rings help users focus on weak areas

## Target Users

- **Consistent Studiers**: Users building daily study habits who want to see their streak visually
- **Progress Trackers**: Users motivated by seeing concrete improvement over time
- **Strategic Learners**: Users who want to identify and focus on weak areas
- **JLPT Preppers**: Users targeting specific JLPT levels who need to track level-specific progress

## JLPT Level Considerations

| Level | Considerations |
|-------|----------------|
| N5 | Primary focus for v0.4; 103 kanji to track mastery |
| N4 | Secondary focus; 66 kanji; separate mastery bar |
| N3+ | Future content; show 0% with "Coming Soon" indicator |

**Cross-Level View**: Dashboard should show all JLPT levels in a unified view, allowing users to see their total Japanese learning journey.

## User Stories

### Heatmap Stories
1. As a learner, I want to see my study activity over the past year so that I can identify patterns in my consistency.
2. As a learner, I want color-coded intensity on my heatmap so that I can see which days I studied more.
3. As a learner, I want to hover over a day to see exact review counts so that I can understand my activity.

### Mastery Visualization Stories
4. As a learner, I want to see topic mastery rings so that I know which topics need more focus.
5. As a learner, I want to see JLPT level progress bars so that I know how close I am to mastering each level.
6. As a learner, I want to see my overall mastery percentage so that I have a single "progress score."

### Trend Stories
7. As a learner, I want to see my mastery trend over 8 weeks so that I know if I'm improving.
8. As a learner, I want the trend to show ups and downs so that I can identify when I regressed.

### At-Risk Stories
9. As a learner, I want to see kanji that recently dropped stages so that I can prioritize them.
10. As a learner, I want to click an at-risk kanji to review it immediately so that I can prevent further regression.

## Acceptance Criteria

### Study Heatmap (365-Day Calendar)
- [ ] AC-1: Heatmap displays past 365 days in a GitHub-style grid (7 rows x 52+ columns)
- [ ] AC-2: Days are color-coded by review intensity (0 reviews = gray, 1-10 = light green, 11-25 = medium, 26+ = dark green)
- [ ] AC-3: Hovering a day shows tooltip with date and review count
- [ ] AC-4: Clicking a day shows session details for that day (if available)
- [ ] AC-5: Today's date is highlighted with a border
- [ ] AC-6: Month labels appear above relevant columns
- [ ] AC-7: Day-of-week labels appear on left side (M, W, F or all 7)

### Topic Mastery Rings (SVG)
- [ ] AC-8: Four circular progress rings displayed (Home Life, Shopping, Restaurant, Travel)
- [ ] AC-9: Each ring shows percentage (0-100%) with arc fill
- [ ] AC-10: Ring center shows topic name and percentage number
- [ ] AC-11: Rings animate on load (fill from 0 to current percentage)
- [ ] AC-12: Clicking a ring filters study queue to that topic
- [ ] AC-13: Rings use consistent color coding (per topic or gradient by percentage)

### JLPT Mastery Bars
- [ ] AC-14: Horizontal progress bars for N5, N4, N3, N2 (N1 out of scope)
- [ ] AC-15: Each bar shows percentage text (e.g., "N5: 62%")
- [ ] AC-16: Bars are color-coded by level (N5 = blue, N4 = green, N3 = yellow, N2 = orange)
- [ ] AC-17: N3/N2 bars show "Coming Soon" if no kanji available
- [ ] AC-18: Clicking a bar filters study queue to that JLPT level

### Mastery Trend Line
- [ ] AC-19: Line chart shows overall mastery percentage over past 8 weeks
- [ ] AC-20: X-axis shows week labels (Week 1, Week 2, ... or dates)
- [ ] AC-21: Y-axis shows percentage (0-100%)
- [ ] AC-22: Data points are clickable/hoverable to show exact percentage
- [ ] AC-23: Trend line updates weekly (snapshot taken at end of each week)
- [ ] AC-24: Chart renders with CSS/SVG (no external charting library)

### At-Risk Kanji Panel
- [ ] AC-25: Panel displays kanji that dropped stages in the past 7 days
- [ ] AC-26: Shows kanji character, reading, meaning, and stage drop info (e.g., "Guru 1 → Apprentice 4")
- [ ] AC-27: Maximum 20 at-risk kanji displayed (sorted by most recently dropped)
- [ ] AC-28: Each kanji has a "Review Now" button for immediate practice
- [ ] AC-29: Panel shows "No at-risk kanji!" message when empty
- [ ] AC-30: At-risk kanji are highlighted in review queue

### Stats Summary Panel
- [ ] AC-31: Panel shows key stats: Total Reviews, Kanji Mastered, Average Accuracy
- [ ] AC-32: Stats update in real-time after each session
- [ ] AC-33: "Kanji Mastered" counts kanji at Burned stage

### Dashboard Layout
- [ ] AC-34: Dashboard is responsive (mobile-first design)
- [ ] AC-35: Components rearrange for mobile (stack vertically) vs desktop (grid layout)
- [ ] AC-36: No horizontal scrolling on mobile
- [ ] AC-37: Dashboard loads within 500ms (no heavy libraries)

## Scope

### In Scope
- Study heatmap (365-day activity calendar)
- Topic mastery rings (4 topics, SVG circular progress)
- JLPT mastery bars (N5-N2, horizontal progress)
- Mastery trend line (8-week history, CSS/SVG)
- At-risk kanji panel (recently dropped, max 20)
- Stats summary panel (reviews, mastered, accuracy)
- Mobile-responsive layout

### Out of Scope
- Leaderboards or social features
- Export/print dashboard
- Custom date ranges (fixed to 365 days / 8 weeks)
- Comparison with other users
- Goal tracking visualization (covered in PRD-003)
- XP/Level display (covered in PRD-003)

### Future Considerations
- Custom dashboard widgets (choose which to show)
- Dark mode support
- Animated celebrations for mastery milestones
- Weekly email digest with dashboard summary
- Shareable progress cards

## UI/UX Specifications

### Dashboard Layout (Desktop)

```
┌─────────────────────────────────────────────────────────────────┐
│  PROGRESS DASHBOARD                                    [Refresh] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │               STUDY HEATMAP (365 Days)                   │   │
│  │  Jan  Feb  Mar  Apr  May  Jun  Jul  Aug  Sep  Oct  Nov   │   │
│  │  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▓▓▓▓▓▓▓▓▓▓▓  │   │
│  │  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▓▓▓▓▓▓▓▓▓▓▓▓  │   │
│  │  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▓▓▓▓▓▓▓▓▓▓▓▓  │   │
│  │  Less ░░ ▒▒ ▓▓ ██ More                                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────────┐  ┌──────────────────────────────┐    │
│  │   TOPIC MASTERY      │  │   JLPT PROGRESS              │    │
│  │                      │  │                              │    │
│  │  ┌────┐  ┌────┐     │  │   N5 ████████░░░░ 72%         │    │
│  │  │Home│  │Shop│     │  │   N4 █████░░░░░░░ 45%         │    │
│  │  │ 72%│  │ 58%│     │  │   N3 ░░░░░░░░░░░░ Coming Soon │    │
│  │  └────┘  └────┘     │  │   N2 ░░░░░░░░░░░░ Coming Soon │    │
│  │  ┌────┐  ┌────┐     │  │                              │    │
│  │  │Rest│  │Trav│     │  └──────────────────────────────┘    │
│  │  │ 45%│  │ 63%│     │                                       │
│  │  └────┘  └────┘     │  ┌──────────────────────────────┐    │
│  │                      │  │   MASTERY TREND (8 Weeks)    │    │
│  └──────────────────────┘  │        ___/\___              │    │
│                            │   ___/         \__           │    │
│  ┌──────────────────────┐  │  /                 \_        │    │
│  │   AT-RISK KANJI      │  │  W1 W2 W3 W4 W5 W6 W7 W8     │    │
│  │                      │  └──────────────────────────────┘    │
│  │  日 Guru1→App4  [⟲]  │                                      │
│  │  語 Guru2→Guru1 [⟲]  │  ┌──────────────────────────────┐    │
│  │  読 Mast→Guru2  [⟲]  │  │   STATS SUMMARY              │    │
│  │                      │  │   Total Reviews: 2,450        │    │
│  │  [See All]           │  │   Kanji Mastered: 12          │    │
│  └──────────────────────┘  │   Average Accuracy: 84%       │    │
│                            └──────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### Dashboard Layout (Mobile)

```
┌─────────────────────┐
│  PROGRESS DASHBOARD │
├─────────────────────┤
│  STATS SUMMARY      │
│  Reviews: 2,450     │
│  Mastered: 12       │
│  Accuracy: 84%      │
├─────────────────────┤
│  JLPT PROGRESS      │
│  N5 █████████░ 72%  │
│  N4 █████░░░░░ 45%  │
├─────────────────────┤
│  TOPIC MASTERY      │
│  ┌────┐ ┌────┐     │
│  │Home│ │Shop│     │
│  │ 72%│ │ 58%│     │
│  └────┘ └────┘     │
│  ┌────┐ ┌────┐     │
│  │Rest│ │Trav│     │
│  │ 45%│ │ 63%│     │
│  └────┘ └────┘     │
├─────────────────────┤
│  HEATMAP (scrollable)│
│  ← ░░░▒▒▓▓████░░ → │
├─────────────────────┤
│  TREND (8 Weeks)    │
│    /\    /\_        │
│  _/  \__/           │
├─────────────────────┤
│  AT-RISK KANJI      │
│  日 Guru1→App4 [⟲]  │
│  語 Guru2→Guru1[⟲]  │
│  [See All]          │
└─────────────────────┘
```

### Color Specifications

**Heatmap Colors**:
| Reviews | Color | Hex |
|---------|-------|-----|
| 0 | Light gray | #ebedf0 |
| 1-10 | Light green | #9be9a8 |
| 11-25 | Medium green | #40c463 |
| 26-50 | Dark green | #30a14e |
| 51+ | Darkest green | #216e39 |

**JLPT Level Colors**:
| Level | Color | Hex |
|-------|-------|-----|
| N5 | Blue | #3b82f6 |
| N4 | Green | #22c55e |
| N3 | Yellow | #eab308 |
| N2 | Orange | #f97316 |
| N1 | Red | #ef4444 |

**Topic Colors**: Use gradient based on mastery percentage (red → yellow → green).

## Content Requirements

- **No Japanese content needed**: Dashboard displays calculated statistics
- **UI Text**: Labels, tooltips, empty states (English only for v0.4)
- **Icons**: Need icons for refresh, review, expand/collapse

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Dashboard view rate | 50% of sessions | Analytics |
| Heatmap engagement | 20% hover/click | Analytics |
| At-risk review rate | 60% of flagged kanji reviewed within 3 days | At-risk tracking |
| Dashboard load time | <500ms | Performance timing |
| Mobile usability | <5% horizontal scroll attempts | Analytics |

## Data Requirements (from PRD-003)

The Progress Dashboard requires the following data from the Habit Formation System (PRD-003):

| Data | Source | Format |
|------|--------|--------|
| Daily review counts | `stats.daily_history` | `{ "YYYY-MM-DD": { reviews, correct, xp_earned } }` |
| JLPT mastery | `stats.jlpt_mastery_cache` | `{ N5: 72.5, N4: 45.0, ... }` |
| Topic mastery | Calculated from `kanji[]` | Per-topic aggregation |
| At-risk kanji | New field: `stats.at_risk_kanji` | `[{ character, dropped_from, dropped_to, date }]` |
| Weekly snapshots | New field: `stats.mastery_snapshots` | `[{ date, overall, n5, n4, n3, n2 }]` |

**Schema Requirements for PRD-005**:

```javascript
// Add to stats object (schema v1.1.0)
stats: {
  // Required by PRD-005
  daily_history: { /* 365 days of { reviews, correct, xp_earned } */ },
  at_risk_kanji: [
    { character: "日", dropped_from: "guru_1", dropped_to: "apprentice_4", date: "2026-01-24" }
  ],
  mastery_snapshots: [
    { date: "2026-01-19", overall: 45.2, n5: 62.0, n4: 28.0, n3: 0, n2: 0 }
  ]
}
```

## Dependencies

- **PRD-001**: Kanji data with JLPT levels and topics
- **PRD-003**: XP, streak, and daily_history data in localStorage
- **TDD-001**: Mastery calculation formulas
- **TDD-003**: Schema v1.1.0 with new fields

## Open Questions (Resolved)

| Question | Decision | Rationale |
|----------|----------|-----------|
| Charting library? | No external library; CSS + SVG only | Keep bundle small, avoid dependencies |
| Heatmap scroll on mobile? | Horizontal scroll within container | Standard pattern, keeps dashboard layout clean |
| Trend line granularity? | Weekly snapshots | Daily too noisy, monthly too coarse |
| At-risk threshold? | Any stage drop in past 7 days | Balances urgency with noise |

---

## Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2026-01-25 | PM (Claude) | Initial draft for Phase 2 Sprint 2 |
