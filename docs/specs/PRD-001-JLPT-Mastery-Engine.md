# PRD-001: JLPT Mastery Learning Engine

**Status**: Draft
**Author**: PM (Claude)
**Created**: 2026-01-24
**Updated**: 2026-01-24

**Related Issue**: [#7](https://github.com/cmbays/japanese-study-site/issues/7)
**Milestone**: [v0.3 - Foundation](https://github.com/cmbays/japanese-study-site/milestone/1)
**Technical Design**: TDD-001 (to be created)

---

## Problem Statement

Currently, users study kanji flashcards in random order with no memory of their progress. Every session starts fresh—there's no tracking of which kanji they know well versus which ones they struggle with. This violates the core principle of spaced repetition: review items just before you forget them.

More critically, users have no visibility into their JLPT level progression. They can't answer "How close am I to knowing all N5 kanji?" or "Which topic should I focus on to improve?" Without this feedback, learning feels aimless and users lose motivation.

## User Benefit

- **Efficient Learning**: Study cards you need to review, not ones you already know
- **Clear JLPT Goals**: See exactly how much of N5, N4, N3, N2 you've mastered
- **Topic Mastery Visibility**: Know which topics (Shopping, Restaurant, etc.) need work
- **Meaningful Progress**: Mastery reflects true knowledge—it can be earned and lost
- **Retention Optimization**: Cards appear at scientifically-optimal intervals

## Target Users

- **JLPT Preppers**: Users studying for specific JLPT exam levels (N5 → N1)
- **Casual Learners**: Users building Japanese vocabulary without exam pressure
- **Returning Users**: Users who studied before and want to see what they've retained

## JLPT Level Considerations

| Level | Kanji Count | Considerations |
|-------|-------------|----------------|
| N5 | 103 kanji | Entry point for all users; first mastery milestone |
| N4 | 66 kanji | Natural progression after N5; unlocks more content |
| N3 | ~350 kanji | Significant jump; needs clear progress visualization |
| N2 | ~350 kanji | Advanced; long-term goal for serious learners |
| N1 | ~1000 kanji | Future content; out of scope for v0.3 |

**JLPT as Primary Progression Axis:**
The platform should make users feel they are "climbing" JLPT levels. Every study session should show progress toward the next level.

## User Stories

### Core SRS Stories
1. As a learner, I want cards I struggle with to appear more often so that I can improve on my weak areas.
2. As a learner, I want cards I know well to appear less often so that I don't waste time on easy material.
3. As a returning user, I want to pick up where I left off so that my previous study time isn't wasted.

### JLPT Progression Stories
4. As a JLPT prepper, I want to see my N5 mastery percentage so that I know how close I am to exam readiness.
5. As a learner, I want to filter by JLPT level so that I can focus on my target exam level.
6. As a beginner, I want to start with N5 content so that I build a solid foundation.

### Mastery Stories
7. As a learner, I want to see each kanji's mastery stage so that I know which ones need more work.
8. As a learner, I want my mastery to decrease when I get answers wrong so that the system reflects my true knowledge.
9. As a learner, I want to see topic-level mastery so that I can focus on weak topic areas.

## Acceptance Criteria

### SRS Algorithm
- [ ] AC-1: Each kanji tracks: last_reviewed, interval, ease_factor, repetitions, stage
- [ ] AC-2: "Due" cards are those where current_date >= last_reviewed + interval
- [ ] AC-3: SM-2 algorithm calculates next interval based on user response
- [ ] AC-4: New cards (never seen) are introduced at a configurable rate (default: 10/day)
- [ ] AC-5: All SRS data persists in localStorage between sessions

### Mastery Stages
- [ ] AC-6: Kanji progress through 8 stages: Locked → Lesson → Apprentice 1-4 → Guru 1-2 → Master → Enlightened → Burned
- [ ] AC-7: "Good" or "Easy" response advances kanji by 1 stage
- [ ] AC-8: "Hard" response drops kanji by 1 stage (minimum: Apprentice 1)
- [ ] AC-9: "Again" response drops kanji by 2 stages (minimum: Apprentice 1)
- [ ] AC-10: Burned kanji are retired from SRS (can be resurrected manually)

### JLPT Integration
- [ ] AC-11: JLPT mastery % calculated as: (sum of kanji mastery scores) / (total kanji × 100)
- [ ] AC-12: Dashboard displays N5, N4, N3, N2 mastery percentages prominently
- [ ] AC-13: Users can filter study session by JLPT level
- [ ] AC-14: Users can study "All Levels" or specific level (N5, N4, etc.)

### Topic Mastery
- [ ] AC-15: Topic mastery % calculated as: (sum of topic's kanji mastery scores) / (topic kanji count × 100)
- [ ] AC-16: Dashboard displays mastery for: Home Life, Shopping, Restaurant, Travel
- [ ] AC-17: Users can filter study session by topic

### Data Persistence
- [ ] AC-18: All progress survives browser refresh
- [ ] AC-19: All progress survives browser close/reopen
- [ ] AC-20: Data export as JSON available (import in future version)

## Scope

### In Scope
- SM-2 spaced repetition algorithm implementation
- 8-stage mastery system with bidirectional movement
- Per-kanji progress tracking in localStorage
- JLPT-level mastery aggregation and display
- Topic-level mastery aggregation and display
- Due cards queue and session management
- New card introduction rate limiting

### Out of Scope
- Cloud sync (requires user accounts - v1.0+)
- Mastery decay over time (complex; consider for v0.5)
- AI-adaptive intervals (requires more data)
- Vocabulary mastery (kanji only for v0.3)
- Leaderboards or social features

### Future Considerations
- "Resurrect" burned items for refresher study
- Mastery decay for long-absent users
- Adaptive new card rate based on performance
- Cross-device sync when accounts are added
- Vocabulary items using same mastery system

## Content Requirements

- **Kanji Data**: 169 kanji already prepared with JLPT levels and topics
- **Stage Definitions**: 8 stages with clear percentage mappings
- **No new content needed**: System operates on existing kanji data

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Cards at Guru+ stage | 50% within 2 weeks | localStorage data |
| JLPT level filter usage | 70%+ of sessions | Usage analytics |
| Mastery regression rate | <15% weekly drops | Stage change tracking |
| Session completion rate | 80%+ finish due cards | Session data |
| Return rate | 40%+ return next day | Visit tracking |

## Dependencies

- **Existing kanji data**: 169 kanji with JLPT levels and topics (complete)
- **Flashcard UI**: Basic card flip mechanism (exists in v0.2)
- **localStorage API**: Browser support (universal)

## Technical Considerations

### localStorage Schema
```javascript
{
  "jss_version": "0.3.0",
  "kanji_progress": {
    "日": {
      "stage": "guru_1",
      "last_reviewed": "2026-01-24T10:30:00Z",
      "interval_days": 4,
      "ease_factor": 2.5,
      "repetitions": 5,
      "total_reviews": 12,
      "correct_count": 10
    },
    // ... more kanji
  },
  "settings": {
    "new_cards_per_day": 10,
    "default_jlpt_filter": "N5"
  },
  "stats": {
    "total_reviews": 500,
    "streak_days": 7,
    "last_study_date": "2026-01-24"
  }
}
```

### SM-2 Algorithm Reference
```
if (quality >= 3):  # correct response
    if repetitions == 0:
        interval = 1
    elif repetitions == 1:
        interval = 6
    else:
        interval = round(interval * ease_factor)

    repetitions += 1
    ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    ease_factor = max(1.3, ease_factor)
else:  # incorrect response
    repetitions = 0
    interval = 1

# quality mapping: Again=0, Hard=2, Good=4, Easy=5
```

### Stage Intervals (Initial)
| Stage | Typical Interval |
|-------|------------------|
| Lesson | 4 hours |
| Apprentice 1 | 8 hours |
| Apprentice 2 | 1 day |
| Apprentice 3 | 2 days |
| Apprentice 4 | 4 days |
| Guru 1 | 1 week |
| Guru 2 | 2 weeks |
| Master | 1 month |
| Enlightened | 4 months |
| Burned | Retired |

## Open Questions

1. Should we allow studying "burned" items in a separate review mode?
2. What's the right new card limit? 10/day? User configurable from start?
3. Should mastery ever decay if user doesn't study for weeks?
4. How do we handle the sub-day intervals (4 hours, 8 hours) for Lesson/Apprentice 1?

---

## Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2026-01-24 | PM (Claude) | Initial draft |
