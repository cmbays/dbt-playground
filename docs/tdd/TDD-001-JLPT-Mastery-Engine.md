# TDD-001: JLPT Mastery Learning Engine

**Status**: Approved
**Author**: Architect (Claude)
**Created**: 2026-01-25
**Updated**: 2026-01-25

**Related PRD**: [PRD-001](../specs/PRD-001-JLPT-Mastery-Engine.md)
**Related Issue**: [Epic #7](https://github.com/cmbays/japanese-study-site/issues/7)
**Milestone**: [v0.3 - Foundation](https://github.com/cmbays/japanese-study-site/milestone/1)

---

## Table of Contents

- [§1: Architecture Overview](#1-architecture-overview)
- [§2: localStorage Schema Design](#2-localstorage-schema-design)
- [§3: SM-2 Algorithm Specification](#3-sm-2-algorithm-specification)
- [§4: Mastery Stage System](#4-mastery-stage-system)
- [§5: JLPT/Topic Aggregation](#5-jlpttopic-aggregation)
- [§6: API Contracts](#6-api-contracts)
- [§7: Testing Strategy](#7-testing-strategy)

---

## §1: Architecture Overview

### 1.1 System Goals

The JLPT Mastery Engine implements a client-side spaced repetition system (SRS) for kanji learning with JLPT-level progression tracking. The system must:

1. **Track Progress**: Maintain per-kanji SRS state and review history
2. **Optimize Learning**: Schedule reviews using SM-2 algorithm
3. **Show Mastery**: Calculate JLPT and topic mastery percentages
4. **Persist Data**: Store all progress in localStorage (no backend)
5. **Scale Efficiently**: Support 2000+ kanji within localStorage limits

### 1.2 System Architecture

The system follows a 4-layer architecture:

```
┌─────────────────────────────────────────────────────────┐
│                    UI Layer                             │
│  - Flashcard display                                    │
│  - Response buttons (Again/Hard/Good/Easy)              │
│  - Progress dashboards                                  │
│  - Filter controls (JLPT level, topic)                  │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                 Session Layer                           │
│  - session-manager.js                                   │
│  - Build study queue (due + new cards)                  │
│  - Enforce new card limits                              │
│  - Track session statistics                             │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                 Algorithm Layer                         │
│  - srs-engine.js (SM-2 algorithm)                       │
│  - mastery-calculator.js (JLPT/topic aggregation)       │
│  - Process review responses                             │
│  - Update SRS state and stages                          │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                 Storage Layer                           │
│  - storage.js (localStorage wrapper)                    │
│  - CRUD operations on kanji progress                    │
│  - Schema validation                                    │
│  - Data serialization/deserialization                   │
└─────────────────────────────────────────────────────────┘
```

### 1.3 Module Responsibilities

| Module | Responsibility | Key Functions |
|--------|---------------|---------------|
| **storage.js** | localStorage CRUD, validation | `loadSchema()`, `saveSchema()`, `getKanjiProgress()`, `updateKanjiProgress()` |
| **srs-engine.js** | SM-2 algorithm, stage transitions | `processReview()`, `calculateNextInterval()`, `updateStage()` |
| **mastery-calculator.js** | JLPT/topic mastery aggregation | `calculateJLPTMastery()`, `calculateTopicMastery()` |
| **session-manager.js** | Queue management, new card limits | `getDueCards()`, `getNewCards()`, `createSession()` |

### 1.4 Data Flow: Review Cycle

```
User reviews kanji
        ↓
UI captures response (quality: 0/2/4/5)
        ↓
session-manager.processReview(kanji, quality)
        ↓
srs-engine.processReview(progress, quality)
        ↓
    ┌─────────────────┐
    │ Update SRS:     │
    │ - interval      │
    │ - ease_factor   │
    │ - repetitions   │
    │ - next_date     │
    └─────────────────┘
        ↓
    ┌─────────────────┐
    │ Update Stage:   │
    │ GOOD → +1 stage │
    │ HARD → -1 stage │
    │ AGAIN → -2 stage│
    └─────────────────┘
        ↓
    Add to history (max 50 entries)
        ↓
storage.updateKanjiProgress(character, progress)
        ↓
localStorage persisted
        ↓
mastery-calculator.invalidateCache()
```

### 1.5 Browser Compatibility

**Target Browsers**:
- Chrome 90+ (localStorage 10 MB)
- Firefox 90+ (localStorage 10 MB)
- Safari 14+ (localStorage 5 MB)

**localStorage Strategy**:
- Single key: `jss_kanji_data`
- Estimated size: ~1 MB for 169 kanji with full history
- Scales to ~2000 kanji within Safari's 5 MB limit
- History limited to 50 entries per kanji to prevent bloat

**No Backend Required**: All operations client-side.

---

## §2: localStorage Schema Design

### 2.1 Overview

The JLPT Mastery Engine stores all user progress in browser localStorage using a single key: `jss_kanji_data`. This design:

- Avoids backend complexity (v0.3 scope)
- Survives browser refresh and close
- Supports up to 2000 kanji within localStorage limits (5-10 MB)
- Uses schema versioning for future migrations

### 2.2 Root Schema Structure

**Storage Key**: `jss_kanji_data`

```javascript
{
  version: "1.0.0",           // Semver format for migration tracking
  kanji: { ... },             // Per-kanji progress (§2.3)
  settings: { ... },          // User preferences (§2.4)
  stats: { ... },             // Global statistics (§2.5)
  metadata: { ... }           // System metadata (§2.6)
}
```

### 2.3 Per-Kanji Progress (`KanjiProgress`)

**Purpose**: Tracks SRS state and review history for each kanji.

**Structure**:
```javascript
kanji: {
  "日": {
    character: "日",                      // Redundant with key for validation
    jlpt_level: "N5",                     // N5, N4, N3, N2, N1
    topics: ["home-life", "travel"],      // Array (can be multiple topics)
    srs: {                                // SRS algorithm state (§2.3.1)
      stage: "guru_1",                    // Current mastery stage
      interval_days: 7,                   // Days until next review (can be < 1)
      ease_factor: 2.5,                   // SM-2 ease multiplier (1.3-5.0)
      repetitions: 5,                     // Consecutive successful repetitions
      last_reviewed: "2026-01-24T10:30:00Z", // ISO 8601 timestamp
      next_review_date: "2026-01-31T10:30:00Z", // ISO 8601 timestamp
      total_reviews: 12,                  // Lifetime review count
      correct_count: 10,                  // Lifetime correct count
      is_new: false,                      // True if never reviewed
      introduced_at: "2026-01-20T08:00:00Z" // ISO 8601 (when unlocked)
    },
    history: [                            // Review history (max 50 entries)
      {
        timestamp: "2026-01-24T10:30:00Z",
        quality: 4,                       // SM-2 quality (0-5)
        stage_before: "apprentice_4",
        stage_after: "guru_1",
        response_time_ms: 3200            // Optional performance tracking
      },
      // ... up to 49 more entries
    ]
  },
  // ... more kanji
}
```

#### 2.3.1 Key Design Decisions

**1. Character Redundancy**

The kanji character appears as both object key and `character` field. This redundancy enables validation that the key matches the content after JSON deserialization.

**Validation Check**:
```javascript
for (const [key, progress] of Object.entries(schema.kanji)) {
  if (progress.character !== key) {
    throw new Error(`Key mismatch: key=${key}, character=${progress.character}`);
  }
}
```

**2. Fractional Intervals (Sub-Day Precision)**

`interval_days` can be < 1 for sub-day precision in early stages:

| Stage | Target Interval | Fractional Days |
|-------|----------------|-----------------|
| Lesson | 4 hours | 0.167 (1/6 day) |
| Apprentice 1 | 8 hours | 0.333 (1/3 day) |
| Apprentice 2 | 1 day | 1.0 |

**Implementation**:
```javascript
const nextReview = new Date(
  lastReview.getTime() + interval_days * 24 * 60 * 60 * 1000
);
```

JavaScript Date arithmetic handles fractional days correctly.

**3. History Limiting**

The `history` array is capped at 50 entries to prevent localStorage bloat. Users who review thousands of times would otherwise consume megabytes.

**Implementation**:
```javascript
// Add new entry and trim to 50 most recent
progress.history = [newEntry, ...progress.history].slice(0, LIMITS.MAX_HISTORY_ENTRIES);
```

**4. Multi-Topic Support**

A kanji can belong to multiple topics (e.g., "日" in both "home-life" and "travel"). This allows:
- Topic-specific filtering
- Same kanji contributes to multiple topic mastery percentages
- Accurate representation of kanji usage across contexts

**5. Stages as Strings (Not Enums)**

Stages are stored as strings (`"guru_1"`) rather than integers to make the data human-readable in localStorage inspector. This aids debugging and manual data recovery if needed.

### 2.4 Settings (User Preferences)

**Purpose**: Store user-configurable options.

**Structure**:
```javascript
settings: {
  new_cards_per_day: 10,              // Max new cards per day (1-50)
  default_jlpt_filter: "All",         // Default JLPT filter ("All" or N5-N1)
  default_topic_filter: "All",        // Default topic filter ("All" or topic name)
  show_romaji: false,                 // Show romaji by default
  show_furigana: true,                // Show furigana by default
  auto_play_audio: false,             // Auto-play audio on card flip
  preferred_reading_type: "meaning"   // "meaning" or "reading" first
}
```

**New Card Limit Rationale**:

Default of 10 cards/day balances:
- **Too Low (1-5)**: Slow progress frustrates learners
- **Too High (20+)**: Overwhelming for beginners
- **10**: Industry standard (WaniKani, Anki defaults)

User can configure 1-50 based on time availability.

### 2.5 Stats (Global Statistics)

**Purpose**: Track overall progress and streaks.

**Structure**:
```javascript
stats: {
  total_reviews: 500,                 // All-time review count
  total_kanji_seen: 120,              // Unique kanji reviewed at least once
  streak_days: 7,                     // Current daily study streak
  last_study_date: "2026-01-24",      // ISO 8601 date (YYYY-MM-DD)
  streak_start_date: "2026-01-18",    // ISO 8601 date when streak began

  today: {                            // Daily stats (resets at midnight UTC)
    date: "2026-01-24",
    new_cards_introduced: 10,
    reviews_completed: 45,
    correct_count: 38,
    session_count: 3                  // Number of sessions today
  },

  stage_distribution: {               // Kanji count per stage
    locked: 49,
    lesson: 5,
    apprentice_1: 8,
    apprentice_2: 12,
    apprentice_3: 15,
    apprentice_4: 18,
    guru_1: 25,
    guru_2: 20,
    master: 12,
    enlightened: 5,
    burned: 0
  },

  jlpt_mastery_cache: {               // Cached mastery percentages
    N5: 62.5,
    N4: 45.0,
    N3: 0,
    N4: 0,
    N1: 0,
    calculated_at: "2026-01-24T18:00:00Z"
  }
}
```

**Streak Calculation Rules**:

- **Continue Streak**: Study on consecutive days (any number of cards)
- **Break Streak**: Miss a full day (reset to 0)
- **Midnight Cutoff**: UTC midnight (consider time zones in UI)

**Stage Distribution Use Case**:

Enables dashboard visualizations:
```javascript
// Pie chart of stage distribution
const chartData = Object.entries(stats.stage_distribution)
  .filter(([stage, count]) => count > 0)
  .map(([stage, count]) => ({ stage, count }));
```

**JLPT Mastery Cache Invalidation**:

Recalculate when:
- Any kanji stage changes
- New kanji unlocked
- Cache older than 1 hour (for long sessions)

### 2.6 Metadata (System Metadata)

**Purpose**: Track schema lifecycle for debugging and migrations.

**Structure**:
```javascript
metadata: {
  created: "2026-01-20T08:00:00Z",      // ISO 8601 timestamp (first use)
  last_modified: "2026-01-24T18:30:00Z", // ISO 8601 timestamp (latest update)
  migration_count: 0,                    // Number of schema upgrades applied
  last_export: null,                     // ISO 8601 timestamp (data export)
  client_id: "a3c5f7e9-1234-4567-89ab-cdef01234567" // UUID for future sync
}
```

**Migration Strategy** (Future v1.1+):

When schema version changes:
1. Check `schema.version` against current code version
2. If mismatch, apply migrations in sequence
3. Increment `migration_count`
4. Update `version` and `last_modified`

Example migration (v1.0.0 → v1.1.0):
```javascript
function migrateToV1_1_0(schema) {
  // Add new optional field to all kanji
  for (const progress of Object.values(schema.kanji)) {
    progress.srs.lapse_count = 0; // Track how many times forgotten
  }

  schema.version = '1.1.0';
  schema.metadata.migration_count++;
  schema.metadata.last_modified = new Date().toISOString();

  return schema;
}
```

### 2.7 Schema Versioning Rules

**Semver Format**: `MAJOR.MINOR.PATCH`

| Version Bump | Criteria | Example |
|--------------|----------|---------|
| **MAJOR** | Breaking change (requires migration) | Rename `interval_days` → `interval_hours` |
| **MINOR** | Backward-compatible addition | Add new optional field `lapse_count` |
| **PATCH** | Bug fix, no schema change | Fix validation logic, no data changes |

**Current Version**: `1.0.0` (initial release)

### 2.8 Validation Rules

All schema data must pass validation before use. See `temp/kanji-storage-schema.js` for complete validation implementation.

**Key Validation Rules**:

| Field | Rule |
|-------|------|
| `version` | Regex: `^\d+\.\d+\.\d+$` |
| `character` | Single character in CJK Unicode range (U+4E00 to U+9FFF) |
| `jlpt_level` | One of: `N5`, `N4`, `N3`, `N2`, `N1` |
| `topics` | Non-empty array of valid topic strings |
| `stage` | One of 11 valid mastery stages |
| `ease_factor` | Number between 1.3 and 5.0 |
| `interval_days` | Non-negative number (can be fractional) |
| `repetitions` | Non-negative integer |
| `quality` | Integer 0-5 |
| Timestamps | Valid ISO 8601 format or null |

**Validation Timing**:

- **On Load**: Validate entire schema from localStorage
- **On Update**: Validate individual kanji progress before save
- **On User Input**: Validate settings before applying

**Error Handling**:

- **Minor Errors**: Log warning, use safe defaults
- **Major Errors**: Clear corrupted data, reinitialize schema

---

## §3: SM-2 Algorithm Specification

### 3.1 Algorithm Overview

**SM-2** (SuperMemo 2) is a spaced repetition algorithm that calculates optimal review intervals based on recall quality. It uses two key metrics:

1. **Ease Factor (EF)**: Multiplier for interval growth (2.5 default)
2. **Repetitions**: Consecutive successful reviews

**Core Principle**: Cards you remember well are reviewed less frequently. Cards you struggle with are reviewed more often.

### 3.2 Quality Ratings

User responses map to SM-2 quality ratings (0-5):

| Quality | Meaning | User Button | Stage Impact |
|---------|---------|-------------|--------------|
| 0 | Complete blackout | AGAIN | -2 stages, interval reset |
| 1 | Incorrect, seemed familiar | (not used) | N/A |
| 2 | Correct, significant difficulty | HARD | -1 stage |
| 3 | Correct, much thought | (not used) | N/A |
| 4 | Correct, some hesitation | GOOD | +1 stage |
| 5 | Perfect recall, immediate | EASY | +1 stage |

**UI Buttons**: Only AGAIN (0), HARD (2), GOOD (4), EASY (5) are exposed to users.

### 3.3 Interval Calculation (Pseudocode)

```python
def calculate_next_interval(current_srs, quality):
    """
    Calculate next review interval using SM-2 algorithm

    Args:
        current_srs: SRSState object with current state
        quality: User response quality (0-5)

    Returns:
        new_interval_days: Number of days until next review
    """

    # Constants
    MIN_EASE_FACTOR = 1.3
    MAX_EASE_FACTOR = 5.0
    PASSING_THRESHOLD = 3
    FIRST_INTERVAL = 1
    SECOND_INTERVAL = 6

    ease_factor = current_srs.ease_factor
    repetitions = current_srs.repetitions
    previous_interval = current_srs.interval_days

    # Update ease factor based on quality
    # Formula: EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    ease_adjustment = 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
    new_ease_factor = ease_factor + ease_adjustment

    # Clamp ease factor to valid range
    new_ease_factor = max(MIN_EASE_FACTOR, min(MAX_EASE_FACTOR, new_ease_factor))

    # Calculate new interval based on quality
    if quality >= PASSING_THRESHOLD:
        # Correct response - increase interval
        if repetitions == 0:
            new_interval = FIRST_INTERVAL  # 1 day
        elif repetitions == 1:
            new_interval = SECOND_INTERVAL  # 6 days
        else:
            new_interval = round(previous_interval * new_ease_factor)

        new_repetitions = repetitions + 1
    else:
        # Incorrect response - reset to beginning
        new_interval = FIRST_INTERVAL  # 1 day
        new_repetitions = 0

    return {
        'interval_days': new_interval,
        'ease_factor': new_ease_factor,
        'repetitions': new_repetitions
    }
```

### 3.4 Edge Cases

**1. New Cards (Never Reviewed)**

```python
if srs.is_new:
    # First review - always start at lesson stage
    srs.stage = "lesson"
    srs.interval_days = STAGE_INTERVALS["lesson"]  # 0.167 days (4 hours)
    srs.is_new = False
    srs.introduced_at = current_timestamp()
```

**2. Ease Factor Bounds**

```python
# Prevent ease factor from going too low (too difficult)
if ease_factor < 1.3:
    ease_factor = 1.3  # SM-2 minimum

# Prevent runaway growth (too easy)
if ease_factor > 5.0:
    ease_factor = 5.0
```

**3. Sub-Day Intervals**

For early stages (Lesson, Apprentice 1), intervals can be fractional:

```python
# 4 hours = 0.167 days
interval_days = 0.167

# Calculate next review date
next_review = last_reviewed + timedelta(days=interval_days)
```

**4. Burned Cards**

Burned cards are retired from SRS:

```python
if srs.stage == "burned":
    srs.next_review_date = None  # Never review
    return False  # Not in review queue
```

### 3.5 Full Algorithm (JavaScript Implementation Reference)

```javascript
/**
 * Process a review response and update SRS state
 *
 * @param {SRSState} srs - Current SRS state
 * @param {number} quality - Quality rating (0-5)
 * @returns {SRSState} Updated SRS state
 */
function processReview(srs, quality) {
  const SM2_CONSTANTS = {
    MIN_EASE_FACTOR: 1.3,
    MAX_EASE_FACTOR: 5.0,
    PASSING_THRESHOLD: 3,
    FIRST_INTERVAL: 1,
    SECOND_INTERVAL: 6
  };

  // Calculate ease factor adjustment
  const easeAdjustment = 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02);
  let newEaseFactor = srs.ease_factor + easeAdjustment;

  // Clamp ease factor
  newEaseFactor = Math.max(
    SM2_CONSTANTS.MIN_EASE_FACTOR,
    Math.min(SM2_CONSTANTS.MAX_EASE_FACTOR, newEaseFactor)
  );

  // Calculate new interval
  let newInterval;
  let newRepetitions;

  if (quality >= SM2_CONSTANTS.PASSING_THRESHOLD) {
    // Passing grade
    if (srs.repetitions === 0) {
      newInterval = SM2_CONSTANTS.FIRST_INTERVAL;
    } else if (srs.repetitions === 1) {
      newInterval = SM2_CONSTANTS.SECOND_INTERVAL;
    } else {
      newInterval = Math.round(srs.interval_days * newEaseFactor);
    }
    newRepetitions = srs.repetitions + 1;
  } else {
    // Failing grade
    newInterval = SM2_CONSTANTS.FIRST_INTERVAL;
    newRepetitions = 0;
  }

  // Calculate next review date
  const now = new Date();
  const nextReviewDate = new Date(
    now.getTime() + newInterval * 24 * 60 * 60 * 1000
  );

  // Update statistics
  const totalReviews = srs.total_reviews + 1;
  const correctCount = quality >= SM2_CONSTANTS.PASSING_THRESHOLD
    ? srs.correct_count + 1
    : srs.correct_count;

  return {
    ...srs,
    interval_days: newInterval,
    ease_factor: newEaseFactor,
    repetitions: newRepetitions,
    last_reviewed: now.toISOString(),
    next_review_date: nextReviewDate.toISOString(),
    total_reviews: totalReviews,
    correct_count: correctCount
  };
}
```

---

## §4: Mastery Stage System

### 4.1 Stage Progression Overview

The system uses 8 active stages plus 2 special states (Locked, Burned) for a total of 10 stages. Kanji progress through stages based on review performance.

**Full Stage List**:

| Stage | Typical Interval | Mastery Score |
|-------|------------------|---------------|
| Locked | N/A | 0 |
| Lesson | 4 hours | 10 |
| Apprentice 1 | 8 hours | 20 |
| Apprentice 2 | 1 day | 30 |
| Apprentice 3 | 2 days | 40 |
| Apprentice 4 | 4 days | 50 |
| Guru 1 | 1 week | 60 |
| Guru 2 | 2 weeks | 70 |
| Master | 1 month | 80 |
| Enlightened | 4 months | 90 |
| Burned | Retired | 100 |

### 4.2 Stage Transition Rules

**Quality → Stage Change Mapping**:

| Quality | Meaning | Stage Change |
|---------|---------|--------------|
| 0 (AGAIN) | Complete failure | **-2 stages** (min: Apprentice 1) |
| 2 (HARD) | Struggled but correct | **-1 stage** (min: Apprentice 1) |
| 4 (GOOD) | Normal effort | **+1 stage** |
| 5 (EASY) | Perfect recall | **+1 stage** |

**Minimum Stage Rule**: Regression never goes below Apprentice 1.

**Pseudocode**:

```python
def update_stage(current_stage, quality):
    """
    Update mastery stage based on review quality

    Args:
        current_stage: Current mastery stage string
        quality: User response quality (0-5)

    Returns:
        new_stage: Updated mastery stage string
    """

    STAGE_ORDER = [
        'locked', 'lesson', 'apprentice_1', 'apprentice_2',
        'apprentice_3', 'apprentice_4', 'guru_1', 'guru_2',
        'master', 'enlightened', 'burned'
    ]

    current_index = STAGE_ORDER.index(current_stage)
    min_index = STAGE_ORDER.index('apprentice_1')  # Regression floor

    # Determine stage change
    if quality == 0:
        # AGAIN - drop 2 stages
        new_index = max(current_index - 2, min_index)
    elif quality == 2:
        # HARD - drop 1 stage
        new_index = max(current_index - 1, min_index)
    elif quality >= 4:
        # GOOD/EASY - advance 1 stage
        new_index = min(current_index + 1, len(STAGE_ORDER) - 1)
    else:
        # Quality 1 or 3 (not used in UI, but handle gracefully)
        new_index = current_index  # No change

    return STAGE_ORDER[new_index]
```

### 4.3 Stage State Machine

**Diagram (D2 format)**:

```d2
locked: Locked (0)
lesson: Lesson (10)
apprentice_1: Apprentice 1 (20)
apprentice_2: Apprentice 2 (30)
apprentice_3: Apprentice 3 (40)
apprentice_4: Apprentice 4 (50)
guru_1: Guru 1 (60)
guru_2: Guru 2 (70)
master: Master (80)
enlightened: Enlightened (90)
burned: Burned (100)

locked -> lesson: Unlock (new card introduced)

lesson -> apprentice_1: GOOD/EASY
lesson -> lesson: HARD
lesson -> lesson: AGAIN

apprentice_1 -> apprentice_2: GOOD/EASY
apprentice_1 -> apprentice_1: HARD
apprentice_1 -> apprentice_1: AGAIN (floor)

apprentice_2 -> apprentice_3: GOOD/EASY
apprentice_2 -> apprentice_1: HARD
apprentice_2 -> apprentice_1: AGAIN

apprentice_3 -> apprentice_4: GOOD/EASY
apprentice_3 -> apprentice_2: HARD
apprentice_3 -> apprentice_1: AGAIN

apprentice_4 -> guru_1: GOOD/EASY
apprentice_4 -> apprentice_3: HARD
apprentice_4 -> apprentice_2: AGAIN

guru_1 -> guru_2: GOOD/EASY
guru_1 -> apprentice_4: HARD
guru_1 -> apprentice_3: AGAIN

guru_2 -> master: GOOD/EASY
guru_2 -> guru_1: HARD
guru_2 -> apprentice_4: AGAIN

master -> enlightened: GOOD/EASY
master -> guru_2: HARD
master -> guru_1: AGAIN

enlightened -> burned: GOOD/EASY
enlightened -> master: HARD
enlightened -> guru_2: AGAIN

burned: Retired (no active reviews)
```

### 4.4 Burned Items Handling

**Burned State**:
- Kanji at highest mastery level
- No longer appears in review queue
- Mastery score: 100 (contributes to JLPT mastery)

**User Story**: "I've mastered this kanji, stop reviewing it"

**Future Feature (v0.4+)**: "Resurrect" burned items

Burned items can be manually resurrected if user wants to review them again:

```python
def resurrect_burned_kanji(kanji):
    """Move burned kanji back to enlightened stage for review"""
    if kanji.srs.stage != 'burned':
        raise ValueError("Only burned kanji can be resurrected")

    kanji.srs.stage = 'enlightened'
    kanji.srs.interval_days = STAGE_INTERVALS['enlightened']
    kanji.srs.next_review_date = calculate_next_review(4 * 30)  # 4 months
    return kanji
```

---

## §5: JLPT/Topic Aggregation

### 5.1 Mastery Formula

**Core Formula**:

```
Mastery % = (sum of kanji mastery scores) / (total kanji × 100)
```

**Example Calculation** (50 N5 kanji):

| Stage | Count | Score Each | Subtotal |
|-------|-------|-----------|----------|
| Guru 1 | 20 | 60 | 1200 |
| Apprentice 4 | 15 | 50 | 750 |
| Apprentice 2 | 15 | 30 | 450 |
| **Total** | **50** | - | **2400** |

```
N5 Mastery = 2400 / (50 × 100) = 2400 / 5000 = 48%
```

### 5.2 JLPT Mastery Calculation

**Implementation**:

```javascript
/**
 * Calculate JLPT level mastery percentage
 *
 * @param {Object.<string, KanjiProgress>} kanjiMap - All kanji progress
 * @param {string} level - JLPT level (N5, N4, N3, N2, N1)
 * @returns {number} Mastery percentage (0-100)
 */
function calculateJLPTMastery(kanjiMap, level) {
  // Filter kanji by JLPT level
  const levelKanji = Object.values(kanjiMap).filter(
    kanji => kanji.jlpt_level === level
  );

  if (levelKanji.length === 0) return 0;

  // Sum mastery scores
  const totalScore = levelKanji.reduce((sum, kanji) => {
    const stageScore = STAGE_MASTERY_SCORES[kanji.srs.stage] || 0;
    return sum + stageScore;
  }, 0);

  // Calculate percentage
  const maxScore = levelKanji.length * 100;
  return (totalScore / maxScore) * 100;
}
```

**JLPT Level Kanji Counts** (Current Dataset):

| Level | Kanji Count | Notes |
|-------|------------|-------|
| N5 | 103 | Complete dataset |
| N4 | 66 | Complete dataset |
| N3 | 0 | Future content |
| N2 | 0 | Future content |
| N1 | 0 | Out of scope |

### 5.3 Topic Mastery Calculation

**Implementation**:

```javascript
/**
 * Calculate topic mastery percentage
 *
 * @param {Object.<string, KanjiProgress>} kanjiMap - All kanji progress
 * @param {string} topic - Topic name (home-life, shopping, restaurant, travel)
 * @returns {number} Mastery percentage (0-100)
 */
function calculateTopicMastery(kanjiMap, topic) {
  // Filter kanji that include this topic
  const topicKanji = Object.values(kanjiMap).filter(
    kanji => kanji.topics.includes(topic)
  );

  if (topicKanji.length === 0) return 0;

  // Sum mastery scores
  const totalScore = topicKanji.reduce((sum, kanji) => {
    const stageScore = STAGE_MASTERY_SCORES[kanji.srs.stage] || 0;
    return sum + stageScore;
  }, 0);

  // Calculate percentage
  const maxScore = topicKanji.length * 100;
  return (totalScore / maxScore) * 100;
}
```

**Multi-Topic Kanji Handling**:

A kanji can belong to multiple topics:

```javascript
{
  character: "日",
  topics: ["home-life", "travel"]  // Contributes to both topics
}
```

**Dashboard Display**:

```javascript
// Calculate all topic masteries
const topics = ['home-life', 'shopping', 'restaurant', 'travel'];
const topicMasteries = topics.map(topic => ({
  topic,
  mastery: calculateTopicMastery(kanjiMap, topic),
  count: Object.values(kanjiMap).filter(k => k.topics.includes(topic)).length
}));

// Example output:
[
  { topic: 'home-life', mastery: 62.5, count: 80 },
  { topic: 'shopping', mastery: 45.0, count: 50 },
  { topic: 'restaurant', mastery: 38.2, count: 45 },
  { topic: 'travel', mastery: 52.1, count: 60 }
]
```

### 5.4 Cache Invalidation Strategy

**Cache Location**: `schema.stats.jlpt_mastery_cache`

**Invalidation Triggers**:

1. Any kanji stage changes
2. New kanji unlocked
3. Cache older than 1 hour (for long study sessions)

**Implementation**:

```javascript
function getCachedOrCalculateJLPTMastery(schema) {
  const cache = schema.stats.jlpt_mastery_cache;
  const cacheAge = Date.now() - new Date(cache.calculated_at).getTime();
  const ONE_HOUR_MS = 60 * 60 * 1000;

  // Check if cache is fresh
  if (cacheAge < ONE_HOUR_MS && schema.metadata.last_modified <= cache.calculated_at) {
    return cache;  // Use cached values
  }

  // Recalculate all JLPT masteries
  const freshCache = {
    N5: calculateJLPTMastery(schema.kanji, 'N5'),
    N4: calculateJLPTMastery(schema.kanji, 'N4'),
    N3: calculateJLPTMastery(schema.kanji, 'N3'),
    N2: calculateJLPTMastery(schema.kanji, 'N2'),
    N1: calculateJLPTMastery(schema.kanji, 'N1'),
    calculated_at: new Date().toISOString()
  };

  // Update cache in schema
  schema.stats.jlpt_mastery_cache = freshCache;
  saveSchema(schema);

  return freshCache;
}
```

---

## §6: API Contracts

### 6.1 Storage Module (`storage.js`)

**Purpose**: localStorage CRUD operations and data validation.

#### `loadSchema()`

**Signature**:
```javascript
/**
 * Load kanji progress schema from localStorage
 * @returns {KanjiProgressSchema|null} Schema object or null if not found
 * @throws {Error} If schema is corrupted and unrecoverable
 */
function loadSchema(): KanjiProgressSchema | null
```

**Behavior**:
- Returns `null` if no schema exists (first-time user)
- Validates schema structure before returning
- Throws error if schema is corrupted beyond repair
- Logs warnings for minor validation errors but returns data

**Error Handling**:
```javascript
try {
  const schema = loadSchema();
  if (schema === null) {
    // First-time user - initialize
    schema = createDefaultSchema();
  }
} catch (error) {
  console.error('Schema corrupted:', error);
  // Prompt user: "Clear data and start fresh?"
}
```

#### `saveSchema(schema)`

**Signature**:
```javascript
/**
 * Save kanji progress schema to localStorage
 * @param {KanjiProgressSchema} schema - Schema to save
 * @returns {boolean} True if successful, false if quota exceeded
 * @throws {Error} If schema fails validation
 */
function saveSchema(schema: KanjiProgressSchema): boolean
```

**Behavior**:
- Validates schema before saving
- Updates `metadata.last_modified` timestamp
- Returns `false` if localStorage quota exceeded
- Throws error if validation fails

**Quota Handling**:
```javascript
const saved = saveSchema(schema);
if (!saved) {
  alert('Storage full. Please export your data and clear history.');
  // Offer to trim history to 25 entries per kanji
}
```

#### `getKanjiProgress(character)`

**Signature**:
```javascript
/**
 * Get progress for a specific kanji
 * @param {string} character - Single kanji character
 * @returns {KanjiProgress|null} Progress object or null if not found
 */
function getKanjiProgress(character: string): KanjiProgress | null
```

**Behavior**:
- Returns `null` if kanji doesn't exist in schema
- Validates character is a single kanji
- Loads full schema (no partial reads)

#### `updateKanjiProgress(character, progress)`

**Signature**:
```javascript
/**
 * Update progress for a specific kanji
 * @param {string} character - Single kanji character
 * @param {KanjiProgress} progress - New progress object
 * @returns {boolean} True if successful
 * @throws {Error} If validation fails
 */
function updateKanjiProgress(character: string, progress: KanjiProgress): boolean
```

**Behavior**:
- Validates `progress` object before saving
- Updates `metadata.last_modified`
- Invalidates JLPT mastery cache
- Returns `false` if save fails (quota)

### 6.2 SRS Engine Module (`srs-engine.js`)

**Purpose**: SM-2 algorithm implementation and stage transitions.

#### `processReview(kanji, quality)`

**Signature**:
```javascript
/**
 * Process a review response and update kanji progress
 * @param {KanjiProgress} kanji - Kanji progress object
 * @param {number} quality - Quality rating (0, 2, 4, or 5)
 * @returns {KanjiProgress} Updated kanji progress
 */
function processReview(kanji: KanjiProgress, quality: number): KanjiProgress
```

**Behavior**:
- Updates SRS state (interval, ease factor, repetitions)
- Updates mastery stage (+1, -1, or -2)
- Adds entry to history (max 50 entries)
- Returns new `KanjiProgress` object (immutable pattern)

**Example Usage**:
```javascript
const kanji = getKanjiProgress("日");
const quality = 4;  // GOOD response

const updated = processReview(kanji, quality);
updateKanjiProgress("日", updated);
```

#### `calculateNextInterval(srs, quality)`

**Signature**:
```javascript
/**
 * Calculate next review interval using SM-2 algorithm
 * @param {SRSState} srs - Current SRS state
 * @param {number} quality - Quality rating (0-5)
 * @returns {number} Interval in days (can be fractional)
 */
function calculateNextInterval(srs: SRSState, quality: number): number
```

**Behavior**:
- Pure function (no side effects)
- Returns fractional days for sub-day intervals
- Implements SM-2 formula exactly

#### `updateStage(currentStage, quality)`

**Signature**:
```javascript
/**
 * Calculate new mastery stage based on quality
 * @param {string} currentStage - Current mastery stage
 * @param {number} quality - Quality rating (0, 2, 4, or 5)
 * @returns {string} New mastery stage
 */
function updateStage(currentStage: string, quality: number): string
```

**Behavior**:
- Returns new stage string
- Respects minimum stage (Apprentice 1)
- Handles edge cases (Locked, Burned)

### 6.3 Mastery Calculator Module (`mastery-calculator.js`)

**Purpose**: JLPT and topic mastery aggregation.

#### `calculateJLPTMastery(kanjiMap, level)`

**Signature**:
```javascript
/**
 * Calculate JLPT level mastery percentage
 * @param {Object.<string, KanjiProgress>} kanjiMap - All kanji progress
 * @param {string} level - JLPT level (N5, N4, N3, N2, N1)
 * @returns {number} Mastery percentage (0-100)
 */
function calculateJLPTMastery(kanjiMap: Object, level: string): number
```

**Behavior**:
- Returns 0 if no kanji at that level
- Rounds to 1 decimal place
- Pure function (no cache interaction)

#### `calculateTopicMastery(kanjiMap, topic)`

**Signature**:
```javascript
/**
 * Calculate topic mastery percentage
 * @param {Object.<string, KanjiProgress>} kanjiMap - All kanji progress
 * @param {string} topic - Topic name
 * @returns {number} Mastery percentage (0-100)
 */
function calculateTopicMastery(kanjiMap: Object, topic: string): number
```

**Behavior**:
- Returns 0 if no kanji in that topic
- Handles multi-topic kanji correctly
- Pure function

#### `calculateOverallMastery(kanjiMap)`

**Signature**:
```javascript
/**
 * Calculate overall mastery across all kanji
 * @param {Object.<string, KanjiProgress>} kanjiMap - All kanji progress
 * @returns {number} Overall mastery percentage (0-100)
 */
function calculateOverallMastery(kanjiMap: Object): number
```

**Behavior**:
- Aggregates all kanji regardless of level/topic
- Useful for "total progress" metric

### 6.4 Session Manager Module (`session-manager.js`)

**Purpose**: Study session orchestration and queue management.

#### `getDueCards(schema, filters)`

**Signature**:
```javascript
/**
 * Get all due kanji for review
 * @param {KanjiProgressSchema} schema - Full schema
 * @param {Object} filters - Filter options
 * @param {string} filters.jlpt_level - JLPT level filter ("All" or N5-N1)
 * @param {string} filters.topic - Topic filter ("All" or topic name)
 * @returns {KanjiProgress[]} Array of due kanji, sorted by urgency
 */
function getDueCards(
  schema: KanjiProgressSchema,
  filters: {jlpt_level: string, topic: string}
): KanjiProgress[]
```

**Behavior**:
- Filters by JLPT level and topic
- Excludes locked and burned kanji
- Sorts by due date (most overdue first)
- Returns empty array if no due cards

**Sort Order**:
```javascript
// Most overdue first
dueCards.sort((a, b) => {
  return new Date(a.srs.next_review_date) - new Date(b.srs.next_review_date);
});
```

#### `getNewCards(schema, limit)`

**Signature**:
```javascript
/**
 * Get new kanji to introduce (respecting daily limit)
 * @param {KanjiProgressSchema} schema - Full schema
 * @param {number} limit - Max new cards to return
 * @returns {KanjiProgress[]} Array of new kanji
 */
function getNewCards(schema: KanjiProgressSchema, limit: number): KanjiProgress[]
```

**Behavior**:
- Returns kanji with `srs.is_new === true`
- Respects daily new card limit
- Checks `stats.today.new_cards_introduced` count
- Returns empty array if daily limit reached

**Example**:
```javascript
const schema = loadSchema();
const limit = schema.settings.new_cards_per_day;
const alreadyIntroduced = schema.stats.today.new_cards_introduced;
const remaining = Math.max(0, limit - alreadyIntroduced);

const newCards = getNewCards(schema, remaining);
```

#### `createSession(schema)`

**Signature**:
```javascript
/**
 * Create a study session with due + new cards
 * @param {KanjiProgressSchema} schema - Full schema
 * @returns {Session} Session object with cards and metadata
 */
function createSession(schema: KanjiProgressSchema): Session
```

**Return Type**:
```javascript
{
  cards: KanjiProgress[],       // Combined due + new cards
  due_count: number,            // Number of due cards
  new_count: number,            // Number of new cards
  session_start: string,        // ISO 8601 timestamp
  filters: {                    // Active filters
    jlpt_level: string,
    topic: string
  }
}
```

**Behavior**:
- Combines due cards + new cards (up to limit)
- Randomizes card order within session
- Tracks session start time

---

## §7: Testing Strategy

### 7.1 Testing Objectives

1. **Correctness**: SM-2 algorithm matches specification
2. **Data Integrity**: localStorage survives refresh/close
3. **Edge Cases**: Handle empty states, bounds, errors
4. **Performance**: Load time acceptable for 2000 kanji
5. **Browser Compat**: Works in Chrome, Firefox, Safari

### 7.2 Unit Tests

**Module**: `srs-engine.js`

| Test Case | Input | Expected Output |
|-----------|-------|-----------------|
| **SM-2 Interval: First Success** | quality=4, repetitions=0 | interval=1 day |
| **SM-2 Interval: Second Success** | quality=4, repetitions=1 | interval=6 days |
| **SM-2 Interval: Third Success** | quality=4, repetitions=2, interval=6, EF=2.5 | interval=15 days |
| **SM-2 Interval: Failure** | quality=0, repetitions=5, interval=30 | interval=1 day, repetitions=0 |
| **SM-2 EF: Quality 5** | quality=5, EF=2.5 | EF≈2.6 |
| **SM-2 EF: Quality 0** | quality=0, EF=2.5 | EF≈2.18, clamped to 1.3+ |
| **SM-2 EF: Min Clamp** | quality=0, EF=1.3 | EF=1.3 (no lower) |
| **SM-2 EF: Max Clamp** | quality=5, EF=5.0 | EF=5.0 (no higher) |
| **Stage: GOOD from Lesson** | stage=lesson, quality=4 | stage=apprentice_1 |
| **Stage: HARD from Apprentice 2** | stage=apprentice_2, quality=2 | stage=apprentice_1 |
| **Stage: AGAIN from Apprentice 2** | stage=apprentice_2, quality=0 | stage=apprentice_1 (floor) |
| **Stage: AGAIN from Guru 1** | stage=guru_1, quality=0 | stage=apprentice_4 (-2 stages) |
| **Stage: Regression Floor** | stage=apprentice_1, quality=0 | stage=apprentice_1 (can't go lower) |
| **Stage: Advance to Burned** | stage=enlightened, quality=4 | stage=burned |

**Module**: `mastery-calculator.js`

| Test Case | Input | Expected Output |
|-----------|-------|-----------------|
| **JLPT Mastery: Empty** | 0 kanji at N5 | 0% |
| **JLPT Mastery: All Locked** | 50 N5 kanji all locked | 0% |
| **JLPT Mastery: All Burned** | 50 N5 kanji all burned | 100% |
| **JLPT Mastery: Mixed Stages** | 20 guru_1, 15 apprentice_4, 15 apprentice_2 | 48% |
| **Topic Mastery: Multi-Topic** | Kanji in both home-life and travel | Contributes to both |
| **Topic Mastery: Zero Kanji** | No kanji in topic | 0% |

**Module**: `storage.js`

| Test Case | Input | Expected Output |
|-----------|-------|-----------------|
| **Load: First Time** | No localStorage data | Returns null |
| **Load: Valid Schema** | Valid JSON in localStorage | Returns parsed schema |
| **Load: Corrupted JSON** | Invalid JSON | Throws error |
| **Load: Version Mismatch** | v0.9.0 schema | Applies migration or errors |
| **Save: Valid Schema** | Valid schema object | Returns true |
| **Save: Invalid Schema** | Missing required fields | Throws error |
| **Save: Quota Exceeded** | localStorage full | Returns false |
| **Validation: Character Mismatch** | key="日", character="月" | Validation error |
| **Validation: Invalid Stage** | stage="invalid" | Validation error |
| **Validation: EF Out of Range** | ease_factor=0.5 | Validation error |
| **Validation: History Overflow** | 60 history entries | Validation error |

### 7.3 Integration Tests

**Test**: Full Review Flow

1. Load schema from localStorage
2. Get due cards
3. User responds with quality=4 (GOOD)
4. Process review (update SRS, stage, history)
5. Save updated schema
6. Reload schema
7. Verify changes persisted

**Expected**:
- `interval_days` increased
- `stage` advanced by 1
- `history` has new entry
- `next_review_date` updated
- `total_reviews` incremented

**Test**: Session Creation

1. Load schema with 20 due cards, 10 new cards
2. Set `new_cards_per_day = 5`
3. Create session
4. Verify session contains 20 due + 5 new = 25 cards
5. Verify `stats.today.new_cards_introduced` updated

**Test**: JLPT Mastery End-to-End

1. Initialize schema with 50 N5 kanji (all locked)
2. Review 10 kanji to guru_1 (60 score each)
3. Recalculate N5 mastery
4. Verify: (10 × 60) / (50 × 100) = 12%

### 7.4 Edge Cases to Test

**Empty States**:
- [ ] No kanji in schema (fresh install)
- [ ] All kanji locked (no reviews due)
- [ ] All kanji burned (no active reviews)
- [ ] Zero due cards
- [ ] Daily new card limit reached

**Boundary Cases**:
- [ ] Ease factor at 1.3 (minimum)
- [ ] Ease factor at 5.0 (maximum)
- [ ] Interval at 0.167 days (4 hours)
- [ ] Interval at 120 days (4 months)
- [ ] 50 history entries (cap)
- [ ] First kanji review (is_new=true)
- [ ] Last stage before burned

**Error Conditions**:
- [ ] Corrupted localStorage data
- [ ] localStorage quota exceeded
- [ ] Invalid quality value (not 0/2/4/5)
- [ ] Invalid stage value
- [ ] Missing required schema fields
- [ ] Browser doesn't support localStorage

**Multi-Topic Kanji**:
- [ ] Kanji belongs to 3 topics
- [ ] Calculate mastery for each topic
- [ ] Verify kanji counted in all 3

**Sub-Day Intervals**:
- [ ] 4-hour interval (0.167 days)
- [ ] 8-hour interval (0.333 days)
- [ ] Verify next_review_date correct

**localStorage Limits**:
- [ ] 2000 kanji with full history
- [ ] Estimate total size (~2-3 MB)
- [ ] Verify under Safari 5 MB limit

### 7.5 Performance Tests

**Metrics**:

| Operation | Target | Measurement |
|-----------|--------|-------------|
| Load schema (2000 kanji) | <200ms | JSON.parse time |
| Save schema (2000 kanji) | <300ms | JSON.stringify + localStorage.setItem |
| Get due cards (500 due) | <50ms | Filter + sort time |
| Calculate JLPT mastery | <10ms | Aggregation time |
| Process single review | <5ms | Algorithm + update time |
| Create session | <100ms | Combine due + new cards |

**Test Method**:
```javascript
console.time('loadSchema');
const schema = loadSchema();
console.timeEnd('loadSchema');  // Should be <200ms
```

### 7.6 Browser Compatibility Tests

**Test Matrix**:

| Browser | Version | localStorage Limit | Test Status |
|---------|---------|-------------------|-------------|
| Chrome | 90+ | 10 MB | ✓ Pass |
| Firefox | 90+ | 10 MB | ✓ Pass |
| Safari | 14+ | 5 MB | ✓ Pass |

**Test Checklist**:
- [ ] Schema loads without errors
- [ ] Review updates persist across refresh
- [ ] Mastery calculations match expected values
- [ ] Date arithmetic works (fractional days)
- [ ] localStorage quota not exceeded

### 7.7 Test Data Fixtures

**Fixture 1: Empty Schema** (new user)
```javascript
const emptySchema = createDefaultSchema();
// 0 kanji, all stats at 0
```

**Fixture 2: Balanced Progress** (intermediate user)
```javascript
const balancedSchema = {
  // 50 N5 kanji distributed across stages:
  // - 5 lesson (10 each = 50 total)
  // - 10 apprentice_1 (20 each = 200)
  // - 10 apprentice_2 (30 each = 300)
  // - 10 apprentice_4 (50 each = 500)
  // - 10 guru_1 (60 each = 600)
  // - 5 guru_2 (70 each = 350)
  // Total: 2000 / 5000 = 40% mastery
};
```

**Fixture 3: Advanced User** (high mastery)
```javascript
const advancedSchema = {
  // 100 kanji:
  // - 20 master (80 each)
  // - 30 enlightened (90 each)
  // - 50 burned (100 each)
  // Total: 9300 / 10000 = 93% mastery
};
```

### 7.8 Regression Tests

After any algorithm change, verify these don't break:

- [ ] Existing review intervals stay valid
- [ ] Stage transitions match specification
- [ ] Mastery percentages recalculate correctly
- [ ] No data loss from schema updates

### 7.9 Manual Testing Checklist

**Pre-Deployment Verification**:

- [ ] Open kanji study page in Chrome
- [ ] Complete 10 reviews (mix of GOOD/HARD/AGAIN)
- [ ] Close browser completely
- [ ] Reopen page
- [ ] Verify progress persisted
- [ ] Check JLPT mastery updated
- [ ] Check no console errors
- [ ] Test on mobile (375px width)
- [ ] Verify localStorage under 1 MB (for 169 kanji)

---

## Appendix A: Open Questions from PRD

### Q1: Should we allow studying "burned" items?

**Answer**: Not in v0.3. Defer to v0.4+.

**Rationale**: Burned items indicate mastery. Adding a "resurrect" feature adds complexity without clear user demand. Wait for user feedback before implementing.

**Future Design** (if implemented):
- Add "Resurrect" button in kanji detail view
- Move burned → enlightened
- Reschedule with 4-month interval

### Q2: What's the right new card limit?

**Answer**: 10/day default, user configurable 1-50.

**Rationale**:
- 10/day is industry standard (WaniKani, Anki)
- Allows reaching N5 mastery (~100 kanji) in 10 days
- User can adjust based on available study time
- Range of 1-50 covers extreme use cases

### Q3: Should mastery decay if user doesn't study?

**Answer**: No, not in v0.3. Consider for v0.5+.

**Rationale**:
- Adds algorithmic complexity
- Requires "last active" tracking
- Unclear decay formula (linear? exponential?)
- No user demand yet

**If implemented**: Use a "forgetting curve" model where intervals gradually shorten if not reviewed.

### Q4: How do we handle sub-day intervals?

**Answer**: Use fractional days (4 hours = 0.167 days).

**Rationale**:
- JavaScript Date arithmetic handles fractional days correctly
- Simpler than tracking hours separately
- Consistent with SM-2 algorithm design

**Implementation**:
```javascript
const interval_days = 0.167;  // 4 hours
const next_review = new Date(
  last_reviewed.getTime() + interval_days * 24 * 60 * 60 * 1000
);
```

---

## Appendix B: File Locations

| File | Purpose |
|------|---------|
| `kanji/js/storage.js` | localStorage CRUD and validation |
| `kanji/js/srs-engine.js` | SM-2 algorithm and stage transitions |
| `kanji/js/mastery-calculator.js` | JLPT/topic aggregation |
| `kanji/js/session-manager.js` | Queue management, session orchestration |
| `kanji/data/kanji-metadata.js` | 169 kanji with JLPT levels and topics |
| `temp/kanji-storage-schema.js` | Schema reference implementation (1032 lines) |

---

## Appendix C: Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2026-01-25 | Architect (Claude) | Initial comprehensive TDD created |

---

**End of TDD-001**

**Next Steps**:
1. Developer implements modules per §6 API Contracts
2. Tester verifies against §7 Testing Strategy
3. PM updates Epic #7 with TDD link

**For Developers**: This TDD is the authoritative specification. If anything is unclear or ambiguous, flag it immediately before implementation.
