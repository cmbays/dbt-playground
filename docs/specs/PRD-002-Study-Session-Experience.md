# PRD-002: Study Session Experience

**Status**: Draft
**Author**: PM (Claude)
**Created**: 2026-01-24
**Updated**: 2026-01-24

**Related Issue**: [#8](https://github.com/cmbays/japanese-study-site/issues/8)
**Milestone**: [v0.3 - Foundation](https://github.com/cmbays/japanese-study-site/milestone/1)
**Technical Design**: TDD-002 (to be created)
**Depends On**: PRD-001 (JLPT Mastery Engine)

---

## Problem Statement

The current flashcard experience lacks the feedback mechanisms that make studying feel rewarding. Users flip cards, but there's no way to tell the system "I knew this" versus "I had no idea." Without self-assessment, the SRS algorithm can't optimize review timing, and users can't feel the satisfaction of rating their own knowledge.

Additionally, study sessions have no clear structure. There's no sense of "I'm done for today" or "here's what I accomplished." This makes it hard to build a consistent study habit.

## User Benefit

- **Self-Paced Learning**: Rate your own knowledge (Again/Hard/Good/Easy)
- **Instant Feedback**: See how your rating affects mastery and next review
- **Session Structure**: Clear start, progress, and completion flow
- **Accomplishment Feeling**: Summary of what you learned at session end
- **Control**: Undo accidental ratings, skip cards if needed

## Target Users

- **Active Studiers**: Users in the middle of a study session
- **Busy Learners**: Users with limited time who need efficient sessions
- **Perfectionists**: Users who want to correct mistakes (undo feature)

## JLPT Level Considerations

| Level | Considerations |
|-------|----------------|
| N5 | Encourage liberal use of "Good" to build confidence |
| N4 | Standard self-assessment expectations |
| N3+ | Users should be stricter with themselves; "Easy" means instant recall |

**JLPT Context in Session:**
- Display current JLPT filter prominently during session
- Show "Studying N5 Kanji" or "Studying Shopping Topic" in header
- Progress indicator shows position in current session queue

## User Stories

### Self-Assessment Stories
1. As a learner, I want to rate how well I knew each card so that the system can schedule my reviews appropriately.
2. As a learner, I want to see what each rating button will do (interval change) so that I can make informed choices.
3. As a learner, I want to undo my last rating so that I can correct accidental taps.
4. As a learner, I want clear visual feedback when I rate a card so that I know my input registered.

### Session Flow Stories
5. As a learner, I want to see how many cards are left in my session so that I can manage my time.
6. As a learner, I want a summary at the end of my session so that I feel accomplished.
7. As a learner, I want to end a session early if needed so that I can come back later.
8. As a learner, I want to choose how many cards to study so that I can fit study time into my schedule.

### Mastery Visibility Stories
9. As a learner, I want to see each card's current mastery stage so that I know where I stand.
10. As a learner, I want to see the stage change after rating so that I understand the impact.
11. As a learner, I want color-coded stages so that I can quickly assess card difficulty.

## Acceptance Criteria

### Self-Assessment Buttons
- [ ] AC-1: Card back displays 4 rating buttons: Again, Hard, Good, Easy
- [ ] AC-2: Each button shows the resulting interval (e.g., "Easy - 4 days")
- [ ] AC-3: Buttons are large enough for comfortable mobile tapping (min 44x44px)
- [ ] AC-4: Keyboard shortcuts work: 1=Again, 2=Hard, 3=Good, 4=Easy
- [ ] AC-5: Rating a card automatically advances to next card

### Visual Feedback
- [ ] AC-6: Button press triggers visible feedback (color change, animation)
- [ ] AC-7: Mastery stage badge visible on card (color-coded)
- [ ] AC-8: Stage change shown after rating (e.g., "Apprentice 2 → Apprentice 3")
- [ ] AC-9: Confetti/celebration animation for reaching Guru, Master, Enlightened, Burned

### Session Flow
- [ ] AC-10: Session start screen shows: due cards count, new cards available, session settings
- [ ] AC-11: Progress bar shows cards completed / total in session
- [ ] AC-12: "End Session" button available at any time
- [ ] AC-13: Session summary shows: cards reviewed, accuracy, stages advanced, XP earned

### Undo Functionality
- [ ] AC-14: "Undo" button appears for 5 seconds after rating
- [ ] AC-15: Undo reverts card to previous state (stage, interval, etc.)
- [ ] AC-16: Only last rating can be undone (not multiple)

### Session Settings
- [ ] AC-17: User can set max new cards per session (5, 10, 15, 20, custom)
- [ ] AC-18: User can set max total cards per session (10, 20, 50, unlimited)
- [ ] AC-19: Settings persist in localStorage

## Scope

### In Scope
- Self-assessment rating UI (4 buttons with intervals)
- Visual feedback for ratings and stage changes
- Session progress indicator
- Session summary screen
- Undo last rating feature
- Keyboard shortcuts for rating
- Session settings (new card limit, total card limit)

### Out of Scope
- Audio feedback (consider for accessibility update)
- Swipe gestures for rating (consider for mobile polish)
- Multiple undo (only last rating)
- Session pause/resume across browser close
- Skipping cards permanently

### Future Considerations
- Swipe left/right for Hard/Easy on mobile
- Audio cues for rating feedback
- Session history log
- "Cram" mode ignoring SRS
- Custom session types (e.g., "Weak cards only")

## UI/UX Specifications

### Card Back Layout
```
┌─────────────────────────────────────┐
│  日                                  │ ← Kanji (large)
│  ひ、か / ニチ、ジツ                   │ ← Readings
│  day, sun, Japan                    │ ← Meanings
│                                     │
│  ┌─────────────────────────────┐    │
│  │  🟡 Apprentice 3             │    │ ← Current stage badge
│  └─────────────────────────────┘    │
│                                     │
│  Example: 日本 (にほん) - Japan      │ ← Example word
│                                     │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐│
│  │Again │ │ Hard │ │ Good │ │ Easy ││ ← Rating buttons
│  │<10m  │ │ 1d   │ │ 3d   │ │ 7d   ││ ← Intervals
│  └──────┘ └──────┘ └──────┘ └──────┘│
│                                     │
│  [← Undo]                           │ ← Undo (when available)
└─────────────────────────────────────┘
```

### Session Summary Layout
```
┌─────────────────────────────────────┐
│        Session Complete! 🎉         │
│                                     │
│   Cards Reviewed:    25             │
│   Correct (Good+):   20 (80%)       │
│   New Cards Learned: 5              │
│                                     │
│   Stages Advanced:   12 ⬆️          │
│   Stages Dropped:    3 ⬇️           │
│                                     │
│   JLPT Progress:                    │
│   N5: ████████░░ 78% (+2%)          │
│                                     │
│   [Study More]  [Done for Today]    │
└─────────────────────────────────────┘
```

### Stage Color Scheme
| Stage | Color | Hex |
|-------|-------|-----|
| Locked | Gray | #9CA3AF |
| Lesson | Pink | #EC4899 |
| Apprentice | Pink/Salmon | #F87171 |
| Guru | Purple | #A855F7 |
| Master | Blue | #3B82F6 |
| Enlightened | Teal | #14B8A6 |
| Burned | Gold | #F59E0B |

## Content Requirements

- **No new Japanese content needed** - operates on existing kanji
- **UI Copy**: Button labels, celebration messages, summary text
- **Micro-copy for intervals**: "<10m", "1d", "3d", "1w", "2w", "1mo", "4mo"

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Session completion rate | 85%+ | Sessions with summary viewed |
| Undo usage | <5% of ratings | Undo button clicks |
| Keyboard shortcut adoption | 20%+ of ratings | Key press vs click |
| Average session length | 10-15 cards | Cards per session |
| Accuracy rate | 75%+ Good or Easy | Rating distribution |

## Dependencies

- **PRD-001**: SRS engine must be implemented first
- **Existing card UI**: Card flip mechanism exists
- **localStorage**: For settings persistence

## Open Questions

1. Should we show streak fire animation in the session, or only on dashboard?
2. What celebration is appropriate for reaching Burned? Special animation?
3. Should the undo button be always visible, or only appear after rating?
4. Do we want sound effects for ratings? (Accessibility considerations)

---

## Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2026-01-24 | PM (Claude) | Initial draft |
