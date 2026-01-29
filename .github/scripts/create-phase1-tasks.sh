#!/bin/bash
# Create all Phase 1 implementation tasks

MILESTONE="v0.3 - Foundation"

echo "Creating Phase 1 implementation tasks..."
echo ""

# Epic 1 Tasks (T1.3 - T1.10)

echo "Creating T1.3..."
cat > /tmp/task.md << 'EOF'
**Parent Epic**: #7
**Task ID**: T1.3

## Description
Create the 8-stage mastery progression system (Locked → Apprentice 1-4 → Guru 1-2 → Master → Burned) with stage advancement and regression rules based on review quality.

## Acceptance Criteria
- [ ] 8 mastery stages defined with clear criteria
- [ ] Stage advancement logic (correct answer progresses)
- [ ] Stage regression logic (wrong answer regresses)
- [ ] Stage thresholds tied to SRS intervals
- [ ] Stage colors/visual indicators defined
- [ ] Burned stage prevents further reviews

## Technical Implementation Notes
**Files to create:**
- `kanji/js/mastery-system.js`

**Stage definitions:**
- Locked: Not yet studied
- Apprentice 1-4: intervals 1d, 3d, 7d, 14d
- Guru 1-2: intervals 30d, 90d
- Master: interval 180d
- Burned: interval ∞ (archived)

**Functions:**
```javascript
function getStageForInterval(interval)
function advanceStage(currentStage)
function regressStage(currentStage)
```

## Effort Estimate
M (1-3 days)

## Blocked By
- #14 (T1.2 - SM-2 algorithm must exist)

## Testing Plan
- Test stage transitions for all 8 stages
- Test regression doesn't go below Apprentice 1
- Test Burned stage locks kanji from queue
- Verify stage colors display correctly
EOF

gh issue create --title "[Task] T1.3 - Create 8-stage mastery progression system" \
  --body-file /tmp/task.md \
  --label "type:task,phase:1,status:blocked,persona:dev,effort:m" \
  --milestone "$MILESTONE"

echo "Creating T1.4..."
cat > /tmp/task.md << 'EOF'
**Parent Epic**: #7
**Task ID**: T1.4

## Description
Build the due cards queue logic that filters kanji by next_review_date and presents cards in the correct order (due cards first, then new cards).

## Acceptance Criteria
- [ ] Queue filters cards where next_review_date <= now
- [ ] Due cards sorted by next_review_date (oldest first)
- [ ] New cards added after due cards exhausted
- [ ] Queue respects new card limit (T1.5)
- [ ] Queue updates dynamically after each review

## Technical Implementation Notes
**Files to create:**
- `kanji/js/queue-manager.js`

**Functions:**
```javascript
function getDueCards(kanjiData, now)
function getNewCards(kanjiData, limit, studied)
function buildQueue(kanjiData, newCardLimit)
```

## Effort Estimate
M (1-3 days)

## Blocked By
- #14 (T1.2 - SM-2 algorithm must exist)

## Testing Plan
- Test with 0 due cards, 10 new cards
- Test with 5 due cards, 10 new cards
- Test with 20 due cards (should skip new cards if limit reached)
- Verify queue updates after rating
EOF

gh issue create --title "[Task] T1.4 - Build due cards queue logic" \
  --body-file /tmp/task.md \
  --label "type:task,phase:1,status:blocked,persona:dev,effort:m" \
  --milestone "$MILESTONE"

echo "Creating T1.5..."
cat > /tmp/task.md << 'EOF'
**Parent Epic**: #7
**Task ID**: T1.5

## Description
Implement new card rate limiting to prevent users from being overwhelmed by too many new cards per session (default 10/day, user-configurable).

## Acceptance Criteria
- [ ] New card limit enforced (default 10)
- [ ] Limit persists in localStorage
- [ ] Limit resets daily at midnight
- [ ] User can configure limit in settings (future)
- [ ] Queue respects limit when adding new cards

## Technical Implementation Notes
**Files to modify:**
- `kanji/js/queue-manager.js`
- `kanji/js/storage.js` (for limit persistence)

**Logic:**
- Track new_cards_today in meta object
- Check if new_cards_today < limit before adding new card
- Reset new_cards_today at midnight

## Effort Estimate
S (<1 day)

## Blocked By
- Task T1.4 must be complete

## Testing Plan
- Set limit to 5, study 10 cards (only 5 should be new)
- Test limit reset at midnight (mock date)
- Test limit persistence across page refresh
EOF

gh issue create --title "[Task] T1.5 - Implement new card rate limiting" \
  --body-file /tmp/task.md \
  --label "type:task,phase:1,status:blocked,persona:dev,effort:s" \
  --milestone "$MILESTONE"

echo "Creating T1.6..."
cat > /tmp/task.md << 'EOF'
**Parent Epic**: #7
**Task ID**: T1.6

## Description
Calculate JLPT-level mastery aggregation by grouping kanji by level (N5, N4, N3, N2) and computing percentage at Guru+ stage.

## Acceptance Criteria
- [ ] Aggregate kanji by JLPT level
- [ ] Calculate % at Guru or higher per level
- [ ] Display N5: X%, N4: Y%, N3: Z%, N2: W%
- [ ] Update in real-time after reviews

## Technical Implementation Notes
**Files to create:**
- `kanji/js/aggregation.js`

**Functions:**
```javascript
function calculateJLPTMastery(kanjiData) {
  // Returns { N5: 45, N4: 20, N3: 5, N2: 0 }
}
```

**Logic:**
- Filter kanji by level
- Count total per level
- Count Guru+ per level
- Return percentage

## Effort Estimate
M (1-3 days)

## Blocked By
- Task T1.3 (mastery stages must exist)

## Testing Plan
- Test with 10 N5 kanji, 5 at Guru+ → 50%
- Test with mixed levels
- Verify percentages update after review
EOF

gh issue create --title "[Task] T1.6 - Calculate JLPT-level mastery aggregation" \
  --body-file /tmp/task.md \
  --label "type:task,phase:1,status:blocked,persona:dev,effort:m" \
  --milestone "$MILESTONE"

echo "Creating T1.7..."
cat > /tmp/task.md << 'EOF'
**Parent Epic**: #7
**Task ID**: T1.7

## Description
Calculate topic-level mastery aggregation by grouping kanji by topic (Home Life, Shopping, Restaurant, Travel) and computing percentage at Guru+ stage.

## Acceptance Criteria
- [ ] Aggregate kanji by topic
- [ ] Calculate % at Guru or higher per topic
- [ ] Display Home Life: X%, Shopping: Y%, etc.
- [ ] Update in real-time after reviews

## Technical Implementation Notes
**Files to modify:**
- `kanji/js/aggregation.js`

**Functions:**
```javascript
function calculateTopicMastery(kanjiData) {
  // Returns { "home-life": 45, "shopping": 30, ... }
}
```

**Note:** Each kanji can belong to multiple topics

## Effort Estimate
M (1-3 days)

## Blocked By
- Task T1.3 (mastery stages must exist)

## Testing Plan
- Test with kanji in multiple topics
- Verify percentages accurate
- Test edge case: kanji in 0 topics
EOF

gh issue create --title "[Task] T1.7 - Calculate topic-level mastery aggregation" \
  --body-file /tmp/task.md \
  --label "type:task,phase:1,status:blocked,persona:dev,effort:m" \
  --milestone "$MILESTONE"

echo "Creating T1.8..."
cat > /tmp/task.md << 'EOF'
**Parent Epic**: #7
**Task ID**: T1.8

## Description
Add localStorage persistence layer to save/load all SRS data with schema versioning and validation on load.

## Acceptance Criteria
- [ ] Save entire SRS state to localStorage after each review
- [ ] Load SRS state on page load
- [ ] Handle missing/corrupted data gracefully
- [ ] Support schema versioning
- [ ] Validate data structure on load

## Technical Implementation Notes
**Files to create:**
- `kanji/js/storage.js`

**Functions:**
```javascript
function saveProgress(data)
function loadProgress()
function validateSchema(data)
function migrateSchema(oldData, newVersion)
```

## Effort Estimate
S (<1 day)

## Blocked By
- #13 (T1.1 - Schema must be defined)

## Testing Plan
- Save data, refresh page, verify data loads
- Corrupt localStorage manually, verify graceful fallback
- Test with old schema version, verify migration
EOF

gh issue create --title "[Task] T1.8 - Add localStorage persistence layer" \
  --body-file /tmp/task.md \
  --label "type:task,phase:1,status:blocked,persona:dev,effort:s" \
  --milestone "$MILESTONE"

echo "Creating T1.9..."
cat > /tmp/task.md << 'EOF'
**Parent Epic**: #7
**Task ID**: T1.9

## Description
Create full mastery dashboard page (kanji/dashboard.html) with JLPT progress charts, topic mastery breakdown, study stats, and stage distribution visualization.

## Acceptance Criteria
- [ ] Dashboard page accessible from kanji/index.html
- [ ] JLPT mastery displayed (N5-N2 percentages)
- [ ] Topic mastery displayed (all 4 topics)
- [ ] Study stats (total reviews, streak, accuracy)
- [ ] Stage distribution chart (how many kanji in each stage)
- [ ] Responsive design (mobile-friendly)

## Technical Implementation Notes
**Files to create:**
- `kanji/dashboard.html`
- `kanji/css/dashboard.css`

**Widgets:**
- JLPT progress bars
- Topic mastery cards
- Stage distribution pie chart or bar chart
- Study statistics panel

## Effort Estimate
M (1-3 days)

## Blocked By
- Task T1.6 (JLPT aggregation)
- Task T1.7 (Topic aggregation)

## Testing Plan
- Verify all stats display correctly
- Test responsiveness (320px - 1024px)
- Test with 0 progress, partial progress, full progress
EOF

gh issue create --title "[Task] T1.9 - Create full mastery dashboard page" \
  --body-file /tmp/task.md \
  --label "type:task,phase:1,status:blocked,persona:dev,effort:m" \
  --milestone "$MILESTONE"

echo "Creating T1.10..."
cat > /tmp/task.md << 'EOF'
**Parent Epic**: #7
**Task ID**: T1.10

## Description
Add condensed dashboard summary widget to kanji/index.html showing key stats at a glance: current level, streak, today's goal progress, and overall JLPT mastery percentage.

## Acceptance Criteria
- [ ] Widget displays on kanji/index.html
- [ ] Shows: Level, Streak, Today's Goal, JLPT %
- [ ] Link to full dashboard
- [ ] Updates in real-time
- [ ] Mobile-friendly layout

## Technical Implementation Notes
**Files to modify:**
- `kanji/index.html`
- `kanji/css/kanji-styles.css`

**Widget structure:**
```html
<div class="dashboard-summary">
  <div class="stat">Level 5</div>
  <div class="stat">7 day streak 🔥</div>
  <div class="stat">Goal: 8/10 cards</div>
  <div class="stat">N5: 45% mastered</div>
  <a href="dashboard.html">View Full Dashboard</a>
</div>
```

## Effort Estimate
S (<1 day)

## Blocked By
- Task T1.9 (Dashboard must exist)

## Testing Plan
- Verify stats match full dashboard
- Test link navigation
- Test responsive layout
EOF

gh issue create --title "[Task] T1.10 - Add dashboard summary widget to index" \
  --body-file /tmp/task.md \
  --label "type:task,phase:1,status:blocked,persona:dev,effort:s" \
  --milestone "$MILESTONE"

# Epic 2 Tasks (T2.1 - T2.8)

echo "Creating T2.1..."
cat > /tmp/task.md << 'EOF'
**Parent Epic**: #8
**Task ID**: T2.1

## Description
Design session flow UI wireframes for study session: start screen, flashcard layout, rating buttons, progress indicator, and summary screen.

## Acceptance Criteria
- [ ] Wireframes created for all session screens
- [ ] Button layout defined (Again/Hard/Good/Easy)
- [ ] Card flip animation sketched
- [ ] Progress bar position defined
- [ ] Summary screen layout defined

## Technical Implementation Notes
**Deliverables:**
- Wireframe sketches (can be hand-drawn or Figma)
- Color scheme for rating buttons
- Typography choices
- Spacing/layout notes

**Design considerations:**
- Mobile-first (320px min width)
- Large touch targets (44px min)
- Clear visual hierarchy

## Effort Estimate
S (<1 day)

## Blocked By
None (design work can start immediately)

## Testing Plan
- Review wireframes with design reviewer
- Get user feedback on button layout
EOF

gh issue create --title "[Task] T2.1 - Design session flow UI wireframes" \
  --body-file /tmp/task.md \
  --label "type:task,phase:1,status:ready,persona:design,effort:s" \
  --milestone "$MILESTONE"

echo "Creating T2.2..."
cat > /tmp/task.md << 'EOF'
**Parent Epic**: #8
**Task ID**: T2.2

## Description
Implement 4-button self-assessment UI (Again/Hard/Good/Easy) with interval display on card back and rating submission logic.

## Acceptance Criteria
- [ ] 4 buttons rendered on card back
- [ ] Each button shows next interval (e.g., "Again: <10m", "Good: 1d")
- [ ] Click triggers SRS calculation and updates card state
- [ ] Visual feedback on button click
- [ ] Card advances to next in queue after rating

## Technical Implementation Notes
**Files to modify:**
- `kanji/index.html`
- `kanji/css/kanji-styles.css`
- `kanji/js/session-manager.js` (new file)

**Button structure:**
```html
<div class="rating-buttons">
  <button class="rating-again" data-quality="0">
    Again<br><span class="interval">&lt;10m</span>
  </button>
  <!-- etc -->
</div>
```

## Effort Estimate
M (1-3 days)

## Blocked By
- #14 (T1.2 - SM-2 algorithm must exist)
- Task T1.3 (mastery stages must exist)

## Testing Plan
- Click all 4 buttons, verify SRS updates
- Check interval display accuracy
- Test rapid clicking (debounce)
EOF

gh issue create --title "[Task] T2.2 - Implement 4-button self-assessment UI" \
  --body-file /tmp/task.md \
  --label "type:task,phase:1,status:blocked,persona:dev,effort:m" \
  --milestone "$MILESTONE"

echo "Creating T2.3..."
cat > /tmp/task.md << 'EOF'
**Parent Epic**: #8
**Task ID**: T2.3

## Description
Add keyboard shortcuts for rating cards: 1=Again, 2=Hard, 3=Good, 4=Easy for power users.

## Acceptance Criteria
- [ ] Keyboard 1-4 triggers respective rating button
- [ ] Only active when card back is shown
- [ ] Visual indicator showing keyboard shortcuts
- [ ] Works on card flip (spacebar flips, 1-4 rates)

## Technical Implementation Notes
**Files to modify:**
- `kanji/js/session-manager.js` or `js/shared.js`

**Event listener:**
```javascript
document.addEventListener('keydown', (e) => {
  if (cardState === 'back') {
    if (e.key === '1') rateCard(0); // Again
    if (e.key === '2') rateCard(2); // Hard
    if (e.key === '3') rateCard(4); // Good
    if (e.key === '4') rateCard(5); // Easy
  }
});
```

## Effort Estimate
S (<1 day)

## Blocked By
- Task T2.2 (rating UI must exist)

## Testing Plan
- Press 1-4 while card back shown, verify rating
- Press 1-4 while card front shown, verify no action
- Test on mobile (should not interfere)
EOF

gh issue create --title "[Task] T2.3 - Add keyboard shortcuts for rating" \
  --body-file /tmp/task.md \
  --label "type:task,phase:1,status:blocked,persona:dev,effort:s" \
  --milestone "$MILESTONE"

echo "Creating T2.4..."
cat > /tmp/task.md << 'EOF'
**Parent Epic**: #8
**Task ID**: T2.4

## Description
Create mastery stage badge display on each flashcard showing current stage (Apprentice 3, Guru 1, etc.) with color-coding.

## Acceptance Criteria
- [ ] Stage badge visible on card front or back
- [ ] Color matches stage (Apprentice=yellow, Guru=purple, Master=blue, Burned=gray)
- [ ] Badge updates after rating
- [ ] Responsive sizing

## Technical Implementation Notes
**Files to modify:**
- `kanji/index.html`
- `kanji/css/kanji-styles.css`

**Badge structure:**
```html
<div class="stage-badge apprentice-3">Apprentice 3</div>
```

**CSS colors:**
- Apprentice: #FFC107 (yellow)
- Guru: #9C27B0 (purple)
- Master: #2196F3 (blue)
- Burned: #9E9E9E (gray)

## Effort Estimate
S (<1 day)

## Blocked By
- Task T1.3 (mastery stages must be defined)

## Testing Plan
- Verify badge color for all 8 stages
- Test badge updates after rating
- Check responsive sizing
EOF

gh issue create --title "[Task] T2.4 - Create mastery stage badge display" \
  --body-file /tmp/task.md \
  --label "type:task,phase:1,status:blocked,persona:dev,effort:s" \
  --milestone "$MILESTONE"

echo "Creating T2.5..."
cat > /tmp/task.md << 'EOF'
**Parent Epic**: #8
**Task ID**: T2.5

## Description
Build stage transition animations: subtle animation when stage changes after rating, celebration animation for milestone stages (Guru, Master, Burned).

## Acceptance Criteria
- [ ] Stage badge animates on stage change
- [ ] Celebration for Guru advancement (confetti/sparkle)
- [ ] Celebration for Master advancement
- [ ] Celebration for Burned (final milestone)
- [ ] Animations are smooth (60fps)
- [ ] Can be skipped/disabled

## Technical Implementation Notes
**Files to modify:**
- `kanji/css/animations.css` (new file)
- `kanji/js/session-manager.js`

**CSS animations:**
```css
@keyframes stage-advance {
  0% { transform: scale(1); }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); }
}
```

**Celebration ideas:**
- Confetti particles
- Color flash
- Sound effect (optional)

## Effort Estimate
M (1-3 days)

## Blocked By
- Task T2.4 (stage badge must exist)

## Testing Plan
- Trigger all stage transitions, verify animations
- Test performance (no jank)
- Test on mobile
EOF

gh issue create --title "[Task] T2.5 - Build stage transition animations" \
  --body-file /tmp/task.md \
  --label "type:task,phase:1,status:blocked,persona:dev,effort:m" \
  --milestone "$MILESTONE"

echo "Creating T2.6..."
cat > /tmp/task.md << 'EOF'
**Parent Epic**: #8
**Task ID**: T2.6

## Description
Implement undo last rating feature allowing users to revert the previous rating within 5 seconds, restoring card's previous SRS state.

## Acceptance Criteria
- [ ] Undo button appears after rating
- [ ] Undo available for 5 seconds
- [ ] Restores previous card state (interval, ease, stage)
- [ ] Undo disappears after 5s or next card
- [ ] Can only undo most recent rating

## Technical Implementation Notes
**Files to modify:**
- `kanji/js/session-manager.js`

**State tracking:**
```javascript
let lastRating = {
  cardId: '日',
  previousState: { interval: 1, ease: 2.5, ... },
  timestamp: Date.now()
};
```

**UI:**
```html
<button id="undo-btn" style="display:none">
  Undo ↩️
</button>
```

## Effort Estimate
M (1-3 days)

## Blocked By
- Task T2.2 (rating UI must exist)

## Testing Plan
- Rate card, click undo within 5s, verify state restored
- Wait 6s, verify undo button disappears
- Rate 2 cards, verify undo only affects last one
EOF

gh issue create --title "[Task] T2.6 - Implement undo last rating feature" \
  --body-file /tmp/task.md \
  --label "type:task,phase:1,status:blocked,persona:dev,effort:m" \
  --milestone "$MILESTONE"

echo "Creating T2.7..."
cat > /tmp/task.md << 'EOF'
**Parent Epic**: #8
**Task ID**: T2.7

## Description
Create session summary screen displayed after completing all due/new cards, showing cards reviewed, accuracy, stages advanced/dropped, and XP earned.

## Acceptance Criteria
- [ ] Summary appears after queue exhausted
- [ ] Shows: cards reviewed, accuracy %, stages advanced, XP earned
- [ ] "Continue Studying" button to add more cards
- [ ] "Finish Session" button returns to index
- [ ] Celebration animation for perfect session

## Technical Implementation Notes
**Files to create:**
- `kanji/summary.html` or in-page modal

**Stats to display:**
- Total cards reviewed
- Accuracy (% rated Good or Easy)
- Stages advanced
- Stages dropped
- Total XP earned
- Bonuses (streak, perfect session)

## Effort Estimate
M (1-3 days)

## Blocked By
- Task T2.2 (session must exist)
- Task T3.3 (XP system must exist)

## Testing Plan
- Complete session, verify stats accurate
- Test perfect session (100% Good/Easy) → celebration
- Test "Continue Studying" adds more cards
EOF

gh issue create --title "[Task] T2.7 - Create session summary screen" \
  --body-file /tmp/task.md \
  --label "type:task,phase:1,status:blocked,persona:dev,effort:m" \
  --milestone "$MILESTONE"

echo "Creating T2.8..."
cat > /tmp/task.md << 'EOF'
**Parent Epic**: #8
**Task ID**: T2.8

## Description
Build session progress indicator showing cards completed / total in current session with visual progress bar.

## Acceptance Criteria
- [ ] Progress bar visible during session
- [ ] Shows "5 / 15 cards" or similar
- [ ] Progress bar fills as cards completed
- [ ] Updates in real-time after each rating

## Technical Implementation Notes
**Files to modify:**
- `kanji/index.html`
- `kanji/css/kanji-styles.css`

**Progress bar structure:**
```html
<div class="session-progress">
  <div class="progress-text">5 / 15 cards</div>
  <div class="progress-bar">
    <div class="progress-fill" style="width: 33%"></div>
  </div>
</div>
```

## Effort Estimate
S (<1 day)

## Blocked By
- Task T2.1 (UI design must be defined)

## Testing Plan
- Start session, verify progress updates after each card
- Test with 1 card, 10 cards, 50 cards
- Verify visual accuracy
EOF

gh issue create --title "[Task] T2.8 - Build session progress indicator" \
  --body-file /tmp/task.md \
  --label "type:task,phase:1,status:blocked,persona:dev,effort:s" \
  --milestone "$MILESTONE"

# Epic 3 Tasks (T3.1 - T3.6)

echo "Creating T3.1..."
cat > /tmp/task.md << 'EOF'
**Parent Epic**: #9
**Task ID**: T3.1

## Description
Implement streak counter logic that tracks consecutive days studied, increments on new day, and resets on missed day.

## Acceptance Criteria
- [ ] Streak increments when user studies on a new calendar day
- [ ] Streak resets to 0 if a day is missed (no freeze available)
- [ ] Streak persists in localStorage
- [ ] Streak displayed on dashboard and index

## Technical Implementation Notes
**Files to create:**
- `kanji/js/habit-tracker.js`

**localStorage schema:**
```javascript
{
  streak: {
    current: 7,
    longest: 30,
    last_study_date: "2026-01-25",
    freezes_available: 1
  }
}
```

**Logic:**
- On session completion, check last_study_date
- If today !== last_study_date + 1 day, check freezes
- If no freeze, reset streak to 0
- If freeze available, use freeze, maintain streak

## Effort Estimate
M (1-3 days)

## Blocked By
- Task T2.7 (session summary must exist to trigger increment)

## Testing Plan
- Study on Day 1, verify streak=1
- Study on Day 2, verify streak=2
- Skip Day 3, study on Day 4, verify streak=1
- Test timezone edge cases (midnight boundary)
EOF

gh issue create --title "[Task] T3.1 - Implement streak counter logic" \
  --body-file /tmp/task.md \
  --label "type:task,phase:1,status:blocked,persona:dev,effort:m" \
  --milestone "$MILESTONE"

echo "Creating T3.2..."
cat > /tmp/task.md << 'EOF'
**Parent Epic**: #9
**Task ID**: T3.2

## Description
Create streak freeze system: earn 1 freeze per 7-day streak, auto-use on missed day, max 2 freezes stored.

## Acceptance Criteria
- [ ] Earn 1 freeze for every 7 consecutive days
- [ ] Auto-use freeze when day is missed
- [ ] Max 2 freezes can be stored
- [ ] Freeze usage notification shown
- [ ] Freezes displayed on dashboard

## Technical Implementation Notes
**Files to modify:**
- `kanji/js/habit-tracker.js`

**Logic:**
- On 7-day milestone, increment freezes_available (max 2)
- On missed day, check freezes_available > 0
- If yes, decrement freeze, maintain streak
- If no, reset streak

**Notification:**
- "Streak Freeze used! Your streak is safe 🛡️"

## Effort Estimate
M (1-3 days)

## Blocked By
- Task T3.1 (streak counter must exist)

## Testing Plan
- Study 7 days, verify 1 freeze earned
- Study 14 days, verify 2 freezes earned
- Miss day with freeze, verify streak maintained
- Miss day without freeze, verify streak reset
EOF

gh issue create --title "[Task] T3.2 - Create streak freeze system" \
  --body-file /tmp/task.md \
  --label "type:task,phase:1,status:blocked,persona:dev,effort:m" \
  --milestone "$MILESTONE"

echo "Creating T3.3..."
cat > /tmp/task.md << 'EOF'
**Parent Epic**: #9
**Task ID**: T3.3

## Description
Build XP calculation engine with base XP per card (10 XP) and bonuses for rating quality, streak milestones, goal completion, and perfect sessions.

## Acceptance Criteria
- [ ] Base XP: 10 per card reviewed
- [ ] Bonus XP: +5 for Good/Easy, +10 for Easy
- [ ] Streak bonus: +50 XP at 7/30/100 day milestones
- [ ] Goal completion bonus: +25 XP
- [ ] Perfect session bonus: +50 XP
- [ ] XP persists in localStorage

## Technical Implementation Notes
**Files to create:**
- `kanji/js/xp-system.js`

**XP formula:**
```javascript
function calculateXP(quality, isGoalComplete, isPerfectSession, streakMilestone) {
  let xp = 10; // base
  if (quality >= 4) xp += 5; // Good
  if (quality === 5) xp += 10; // Easy (total +15)
  if (isGoalComplete) xp += 25;
  if (isPerfectSession) xp += 50;
  if (streakMilestone) xp += 50;
  return xp;
}
```

## Effort Estimate
M (1-3 days)

## Blocked By
- Task T2.2 (rating system must exist)

## Testing Plan
- Rate card with Again, verify 10 XP
- Rate card with Easy, verify 25 XP
- Complete goal, verify +25 bonus
- Perfect session, verify +50 bonus
EOF

gh issue create --title "[Task] T3.3 - Build XP calculation engine" \
  --body-file /tmp/task.md \
  --label "type:task,phase:1,status:blocked,persona:dev,effort:m" \
  --milestone "$MILESTONE"

echo "Creating T3.4..."
cat > /tmp/task.md << 'EOF'
**Parent Epic**: #9
**Task ID**: T3.4

## Description
Implement level progression system (60 levels) with increasing XP thresholds, level-up detection, and persistence.

## Acceptance Criteria
- [ ] 60 levels defined with XP thresholds
- [ ] Level-up triggers when XP >= threshold
- [ ] Level-up notification shown
- [ ] Current level displayed on dashboard
- [ ] XP progress bar to next level

## Technical Implementation Notes
**Files to modify:**
- `kanji/js/xp-system.js`

**Level thresholds (example):**
```javascript
const LEVELS = [
  { level: 1, xp: 0 },
  { level: 2, xp: 100 },
  { level: 3, xp: 250 },
  { level: 4, xp: 450 },
  // ... up to level 60
];
```

**Formula:** threshold = level^2.2 * 50 (approximate)

## Effort Estimate
M (1-3 days)

## Blocked By
- Task T3.3 (XP system must exist)

## Testing Plan
- Earn XP, verify level-up triggers correctly
- Test XP progress bar accuracy
- Test all 60 level thresholds
EOF

gh issue create --title "[Task] T3.4 - Implement level progression system" \
  --body-file /tmp/task.md \
  --label "type:task,phase:1,status:blocked,persona:dev,effort:m" \
  --milestone "$MILESTONE"

echo "Creating T3.5..."
cat > /tmp/task.md << 'EOF'
**Parent Epic**: #9
**Task ID**: T3.5

## Description
Create daily goal setting & tracking: user-configurable goal (5-25 cards/day), progress bar, completion detection.

## Acceptance Criteria
- [ ] User can set daily goal (default 10 cards)
- [ ] Goal persists in localStorage
- [ ] Progress bar shows cards reviewed / goal
- [ ] Goal completion triggers bonus XP
- [ ] Goal resets daily at midnight

## Technical Implementation Notes
**Files to modify:**
- `kanji/js/habit-tracker.js`
- `kanji/index.html` (goal widget)

**UI:**
```html
<div class="daily-goal">
  <div>Daily Goal: 8 / 10 cards</div>
  <div class="progress-bar">
    <div class="fill" style="width: 80%"></div>
  </div>
</div>
```

## Effort Estimate
S (<1 day)

## Blocked By
- Task T2.8 (progress tracking must exist)

## Testing Plan
- Set goal to 10, study 10 cards, verify completion
- Test goal reset at midnight
- Test goal persistence across refresh
EOF

gh issue create --title "[Task] T3.5 - Create daily goal setting & tracking" \
  --body-file /tmp/task.md \
  --label "type:task,phase:1,status:blocked,persona:dev,effort:s" \
  --milestone "$MILESTONE"

echo "Creating T3.6..."
cat > /tmp/task.md << 'EOF'
**Parent Epic**: #9
**Task ID**: T3.6

## Description
Build celebration animations for streak milestones (7, 30, 100 days), level-ups (every 10 levels), and goal completion.

## Acceptance Criteria
- [ ] Celebration for 7-day streak
- [ ] Celebration for 30-day streak
- [ ] Celebration for 100-day streak
- [ ] Celebration for level milestones (10, 20, 30, etc.)
- [ ] Celebration for daily goal completion
- [ ] Animations are joyful and motivating

## Technical Implementation Notes
**Files to modify:**
- `kanji/css/animations.css`
- `kanji/js/habit-tracker.js`

**Celebration ideas:**
- Confetti animation
- Badge/trophy display
- Color flash
- Sound effect (optional)
- Congratulatory message

## Effort Estimate
M (1-3 days)

## Blocked By
- Task T3.1 (streak system)
- Task T3.4 (level system)

## Testing Plan
- Trigger all milestone celebrations
- Verify animations are smooth
- Test on mobile devices
EOF

gh issue create --title "[Task] T3.6 - Build celebration animations" \
  --body-file /tmp/task.md \
  --label "type:task,phase:1,status:blocked,persona:dev,effort:m" \
  --milestone "$MILESTONE"

echo ""
echo "✅ All 22 remaining tasks created successfully!"
echo ""
echo "Summary:"
echo "- Epic 1 (PRD-001): T1.1 - T1.10 (10 tasks)"
echo "- Epic 2 (PRD-002): T2.1 - T2.8 (8 tasks)"
echo "- Epic 3 (PRD-003): T3.1 - T3.6 (6 tasks)"
echo "- Total: 24 tasks (2 already created + 22 new)"
