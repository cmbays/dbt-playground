# TDD-003: Habit Formation & Engagement System

**Status**: Draft
**Author**: Architect (Claude)
**Created**: 2026-01-25
**Updated**: 2026-01-25

**Related PRDs**: [PRD-003](../specs/PRD-003-Habit-Formation-System.md), [PRD-005](../specs/PRD-005-Progress-Dashboard.md)
**Related Issue**: [Epic #45](https://github.com/cmbays/japanese-study-site/issues/45)
**Milestone**: [v0.4 - Engagement](https://github.com/cmbays/japanese-study-site/milestone/2)

---

## Table of Contents

- [§1: Architecture Overview](#1-architecture-overview)
- [§2: Schema Migration (v1.0.0 → v1.1.0)](#2-schema-migration-v100--v110)
- [§3: XP Engine Module](#3-xp-engine-module)
- [§4: Streak Manager Module](#4-streak-manager-module)
- [§5: Goals Manager Module](#5-goals-manager-module)
- [§6: Dashboard Visualizations](#6-dashboard-visualizations)
- [§7: Testing Strategy](#7-testing-strategy)

---

## §1: Architecture Overview

### 1.1 System Goals

The Habit Formation & Engagement System builds on Phase 1's SRS foundation to create addictive study habits through:

1. **XP Rewards**: Quantify effort with points for every review
2. **Level Progression**: Long-term progression through 60 levels
3. **Streak System**: Daily accountability with freeze protection
4. **Daily Goals**: Clear targets for "done for today"
5. **Progress Visualization**: Rich dashboard showing mastery and trends

### 1.2 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      UI Layer                                    │
│  - Dashboard widgets (XP, Level, Streak, Goals)                 │
│  - Progress visualizations (heatmap, rings, bars, trend)        │
│  - Celebration modals                                           │
│  - Notification permission prompts                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   Engagement Layer (NEW)                         │
│  - xp-engine.js (XP calculation, level thresholds)              │
│  - streak-manager.js (streak logic, freezes)                    │
│  - goals-manager.js (daily goals, notifications)                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   Session Layer (Phase 1)                        │
│  - session-manager.js (now triggers XP/streak updates)          │
│  - Calls engagement layer after each review                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   Algorithm Layer (Phase 1)                      │
│  - srs-engine.js (unchanged)                                    │
│  - mastery-calculator.js (extended for trends)                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   Storage Layer (Phase 1)                        │
│  - storage.js (v1.1.0 with new engagement fields)               │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 Module Responsibilities

| Module | Responsibility | Key Functions |
|--------|---------------|---------------|
| **xp-engine.js** | XP calculation, level thresholds, level-up detection | `calculateXP()`, `getLevelFromXP()`, `checkLevelUp()` |
| **streak-manager.js** | Streak tracking, freeze management | `updateStreak()`, `useFreeze()`, `isAtRisk()` |
| **goals-manager.js** | Daily goal tracking, notifications | `setGoal()`, `updateProgress()`, `checkGoalComplete()` |
| **mastery-calculator.js** | Extended with trend snapshots | `takeWeeklySnapshot()`, `getTrendData()` |
| **storage.js** | Extended with engagement schema | `migrateToV110()` |

### 1.4 Data Flow: Review with Engagement

```
User completes review (quality: 0/2/4/5)
        ↓
session-manager.processReview()
        ↓
    ┌─────────────────────────┐
    │ Phase 1 Processing:     │
    │ - SRS state update      │
    │ - Stage transition      │
    │ - History entry         │
    └─────────────────────────┘
        ↓
    ┌─────────────────────────┐
    │ Phase 2 Processing:     │
    │ xp-engine.calculateXP() │
    │ - Base XP (10)          │
    │ - Quality bonus         │
    │ - Streak bonus          │
    └─────────────────────────┘
        ↓
    ┌─────────────────────────┐
    │ Update Engagement:      │
    │ - Add XP to total       │
    │ - Check level up        │
    │ - Update daily history  │
    │ - Update goal progress  │
    │ - Check at-risk kanji   │
    └─────────────────────────┘
        ↓
storage.saveSchema()
        ↓
UI updates (XP bar, goal progress, celebrations)
```

---

## §2: Schema Migration (v1.0.0 → v1.1.0)

### 2.1 Migration Strategy

**Principle**: Additive, backward-compatible changes only.

The v1.1.0 schema adds new fields to the existing `stats` and `settings` objects without modifying existing structures. This allows:

- Existing v1.0.0 data to load without loss
- Graceful upgrade on first v1.1.0 load
- No manual data migration required

### 2.2 Schema Changes (Complete)

```javascript
// Schema v1.1.0 - Full structure with new fields highlighted
{
  version: "1.1.0",  // Bumped from 1.0.0

  kanji: { /* unchanged from v1.0.0 */ },

  settings: {
    // Existing v1.0.0 fields
    new_cards_per_day: 10,
    default_jlpt_filter: "All",
    default_topic_filter: "All",
    show_romaji: false,
    show_furigana: true,
    auto_play_audio: false,
    preferred_reading_type: "meaning",

    // NEW: Daily Goal Settings
    daily_goal: {
      enabled: true,
      target_cards: 10,       // 5, 10, 15, 20, 25, or custom (1-100)
      notify_enabled: false,
      notify_time: "19:00"    // HH:MM local time
    }
  },

  stats: {
    // Existing v1.0.0 fields
    total_reviews: 0,
    total_kanji_seen: 0,
    streak_days: 0,           // DEPRECATED: Use stats.streak.current
    last_study_date: null,    // DEPRECATED: Use stats.streak.last_study_date
    streak_start_date: null,  // DEPRECATED: Use stats.streak object

    today: {
      date: "2026-01-25",
      new_cards_introduced: 0,
      reviews_completed: 0,
      correct_count: 0,
      session_count: 0,
      // NEW
      xp_earned: 0,
      goal_completed: false
    },

    stage_distribution: { /* unchanged */ },
    jlpt_mastery_cache: { /* unchanged */ },

    // NEW: XP & Level System
    xp: {
      total: 0,                 // Lifetime XP earned
      current_level: 1,         // Current level (1-60)
      xp_this_level: 0,         // XP earned toward next level
      xp_to_next_level: 100,    // XP threshold for next level
      last_level_up: null       // ISO timestamp of last level-up
    },

    // NEW: Streak System (replaces legacy streak fields)
    streak: {
      current: 0,               // Current streak days
      longest: 0,               // Personal best streak
      last_study_date: null,    // YYYY-MM-DD format
      freezes_available: 0,     // Streak freezes (0-2)
      freeze_used_date: null,   // Date freeze was last used
      freezes_earned_at: 0      // Streak count when last freeze earned
    },

    // NEW: Daily History (for heatmap)
    daily_history: {
      // "YYYY-MM-DD": { reviews: N, correct: N, xp_earned: N }
    },

    // NEW: At-Risk Kanji (recently dropped stages)
    at_risk_kanji: [
      // { character: "日", dropped_from: "guru_1", dropped_to: "apprentice_4", date: "2026-01-24" }
    ],

    // NEW: Mastery Snapshots (for trend line)
    mastery_snapshots: [
      // { date: "2026-01-19", overall: 45.2, n5: 62.0, n4: 28.0, n3: 0, n2: 0 }
    ]
  },

  metadata: { /* unchanged */ }
}
```

### 2.3 Migration Function

```javascript
/**
 * Migrate schema from v1.0.0 to v1.1.0
 *
 * @param {Object} schema - v1.0.0 schema
 * @returns {Object} v1.1.0 schema
 */
function migrateToV1_1_0(schema) {
  // Already v1.1.0+, no migration needed
  if (compareVersions(schema.version, '1.1.0') >= 0) {
    return schema;
  }

  // Add daily_goal to settings
  if (!schema.settings.daily_goal) {
    schema.settings.daily_goal = {
      enabled: true,
      target_cards: 10,
      notify_enabled: false,
      notify_time: "19:00"
    };
  }

  // Add XP system to stats
  if (!schema.stats.xp) {
    schema.stats.xp = {
      total: 0,
      current_level: 1,
      xp_this_level: 0,
      xp_to_next_level: 100,
      last_level_up: null
    };
  }

  // Add streak system (migrate from legacy fields)
  if (!schema.stats.streak) {
    schema.stats.streak = {
      current: schema.stats.streak_days || 0,
      longest: schema.stats.streak_days || 0,
      last_study_date: schema.stats.last_study_date,
      freezes_available: 0,
      freeze_used_date: null,
      freezes_earned_at: 0
    };
  }

  // Add daily_history (empty, will populate going forward)
  if (!schema.stats.daily_history) {
    schema.stats.daily_history = {};

    // Backfill today if we have data
    if (schema.stats.today && schema.stats.today.date) {
      schema.stats.daily_history[schema.stats.today.date] = {
        reviews: schema.stats.today.reviews_completed,
        correct: schema.stats.today.correct_count,
        xp_earned: 0  // Can't reconstruct historical XP
      };
    }
  }

  // Add at_risk_kanji (empty array)
  if (!schema.stats.at_risk_kanji) {
    schema.stats.at_risk_kanji = [];
  }

  // Add mastery_snapshots (empty array)
  if (!schema.stats.mastery_snapshots) {
    schema.stats.mastery_snapshots = [];
  }

  // Add today.xp_earned and today.goal_completed
  if (schema.stats.today) {
    if (schema.stats.today.xp_earned === undefined) {
      schema.stats.today.xp_earned = 0;
    }
    if (schema.stats.today.goal_completed === undefined) {
      schema.stats.today.goal_completed = false;
    }
  }

  // Update version
  schema.version = '1.1.0';
  schema.metadata.migration_count = (schema.metadata.migration_count || 0) + 1;
  schema.metadata.last_modified = new Date().toISOString();

  return schema;
}

/**
 * Compare semver versions
 * @returns {number} -1 if a < b, 0 if equal, 1 if a > b
 */
function compareVersions(a, b) {
  const partsA = a.split('.').map(Number);
  const partsB = b.split('.').map(Number);

  for (let i = 0; i < 3; i++) {
    if (partsA[i] < partsB[i]) return -1;
    if (partsA[i] > partsB[i]) return 1;
  }
  return 0;
}
```

### 2.4 Validation Rules (New Fields)

| Field | Rule |
|-------|------|
| `settings.daily_goal.target_cards` | Integer 1-100 |
| `settings.daily_goal.notify_time` | Regex: `^([01]\d|2[0-3]):[0-5]\d$` |
| `stats.xp.total` | Non-negative integer |
| `stats.xp.current_level` | Integer 1-60 |
| `stats.streak.current` | Non-negative integer |
| `stats.streak.freezes_available` | Integer 0-2 |
| `stats.daily_history` keys | YYYY-MM-DD format |
| `stats.at_risk_kanji` | Array, max 50 entries |
| `stats.mastery_snapshots` | Array, max 52 entries (1 year of weeks) |

---

## §3: XP Engine Module

### 3.1 XP Calculation Formula

**Base Formula**:
```
XP = BASE_XP + QUALITY_BONUS + STREAK_BONUS
```

**Components**:

| Component | Value | Notes |
|-----------|-------|-------|
| BASE_XP | 10 | Awarded for every review |
| QUALITY_BONUS (Good) | +5 | Quality = 4 |
| QUALITY_BONUS (Easy) | +10 | Quality = 5 |
| QUALITY_BONUS (Hard) | 0 | Quality = 2 |
| QUALITY_BONUS (Again) | 0 | Quality = 0 |
| STREAK_BONUS | +10% per tier | Tiers: 7, 14, 21, 28, 35+ days |

**Streak Bonus Tiers**:

| Streak Days | Bonus | Max XP (Easy) |
|-------------|-------|---------------|
| 0-6 | 0% | 20 |
| 7-13 | +10% | 22 |
| 14-20 | +20% | 24 |
| 21-27 | +30% | 26 |
| 28-34 | +40% | 28 |
| 35+ | +50% | 30 |

**Special Bonuses**:

| Bonus | Value | Trigger |
|-------|-------|---------|
| Daily Goal Completion | +50 XP | Complete daily card goal |
| Perfect Session | +25 XP | All reviews Good or Easy (min 5 cards) |

### 3.2 Level System

**Level Range**: 1-60 (matching WaniKani-style progression)

**XP Thresholds** (exponential curve):

```javascript
/**
 * Calculate XP required for a specific level
 *
 * @param {number} level - Target level (1-60)
 * @returns {number} XP required to reach this level from level 1
 */
function getXPForLevel(level) {
  if (level <= 1) return 0;

  // Formula: 50 * n * (1 + 0.1 * floor(n/10))
  // This creates a gentle exponential curve
  let totalXP = 0;
  for (let n = 2; n <= level; n++) {
    const tierMultiplier = 1 + 0.1 * Math.floor(n / 10);
    totalXP += Math.round(50 * n * tierMultiplier);
  }
  return totalXP;
}
```

**XP Table (Key Levels)**:

| Level | XP to Reach | XP for Level | Cumulative XP |
|-------|-------------|--------------|---------------|
| 1 | 0 | - | 0 |
| 2 | 100 | 100 | 100 |
| 5 | 250 | 250 | 600 |
| 10 | 550 | 550 | 3,025 |
| 20 | 1,200 | 1,200 | 13,650 |
| 30 | 2,100 | 2,100 | 36,750 |
| 40 | 3,200 | 3,200 | 75,450 |
| 50 | 4,500 | 4,500 | 134,250 |
| 60 | 6,000 | 6,000 | 219,750 |

### 3.3 API Contracts

#### `calculateXP(quality, streakDays)`

```javascript
/**
 * Calculate XP earned for a single review
 *
 * @param {number} quality - Review quality (0, 2, 4, or 5)
 * @param {number} streakDays - Current streak days
 * @returns {number} XP earned for this review
 */
function calculateXP(quality, streakDays) {
  const BASE_XP = 10;

  // Quality bonus
  let qualityBonus = 0;
  if (quality === 4) qualityBonus = 5;      // Good
  else if (quality === 5) qualityBonus = 10; // Easy

  // Streak multiplier (10% per 7-day tier, max 50%)
  const streakTier = Math.min(Math.floor(streakDays / 7), 5);
  const streakMultiplier = 1 + (streakTier * 0.10);

  return Math.round((BASE_XP + qualityBonus) * streakMultiplier);
}
```

#### `getLevelFromXP(totalXP)`

```javascript
/**
 * Determine level from total XP
 *
 * @param {number} totalXP - Total lifetime XP
 * @returns {Object} { level, xp_this_level, xp_to_next_level }
 */
function getLevelFromXP(totalXP) {
  let level = 1;
  let cumulativeXP = 0;

  while (level < 60) {
    const xpForNextLevel = getXPRequiredForLevel(level + 1);
    if (cumulativeXP + xpForNextLevel > totalXP) {
      break;
    }
    cumulativeXP += xpForNextLevel;
    level++;
  }

  const xpThisLevel = totalXP - cumulativeXP;
  const xpToNextLevel = level < 60 ? getXPRequiredForLevel(level + 1) : 0;

  return {
    level,
    xp_this_level: xpThisLevel,
    xp_to_next_level: xpToNextLevel
  };
}
```

#### `awardXP(schema, xpAmount)`

```javascript
/**
 * Award XP and check for level up
 *
 * @param {Object} schema - Full schema object
 * @param {number} xpAmount - XP to award
 * @returns {Object} { schema, leveledUp, newLevel, celebration }
 */
function awardXP(schema, xpAmount) {
  const previousLevel = schema.stats.xp.current_level;

  // Add XP
  schema.stats.xp.total += xpAmount;
  schema.stats.today.xp_earned += xpAmount;

  // Recalculate level
  const levelInfo = getLevelFromXP(schema.stats.xp.total);
  schema.stats.xp.current_level = levelInfo.level;
  schema.stats.xp.xp_this_level = levelInfo.xp_this_level;
  schema.stats.xp.xp_to_next_level = levelInfo.xp_to_next_level;

  const leveledUp = levelInfo.level > previousLevel;

  if (leveledUp) {
    schema.stats.xp.last_level_up = new Date().toISOString();
  }

  // Determine celebration type
  let celebration = null;
  if (leveledUp) {
    if ([10, 20, 30, 40, 50, 60].includes(levelInfo.level)) {
      celebration = 'milestone'; // Special celebration
    } else {
      celebration = 'level_up';  // Standard celebration
    }
  }

  return { schema, leveledUp, newLevel: levelInfo.level, celebration };
}
```

---

## §4: Streak Manager Module

### 4.1 Streak Rules

**Streak Increment**:
- Streak increases by 1 when user studies on a new day
- "Day" is defined as midnight-to-midnight local time
- Minimum 1 review required to count as "studied"

**Streak Reset**:
- Streak resets to 0 if a full day passes without study
- Reset happens on first action of the day (lazy evaluation)

**Streak Freeze**:
- Prevents streak reset for 1 missed day
- Automatically consumed when day is missed
- Maximum 2 freezes can be held
- Earned: 1 freeze per 7 consecutive days (when not already at max)

### 4.2 Day Boundary Logic

```javascript
/**
 * Get date string for a given timestamp in local time
 *
 * @param {Date} date - Date object
 * @returns {string} YYYY-MM-DD format in local time
 */
function getLocalDateString(date = new Date()) {
  return date.toLocaleDateString('en-CA'); // Returns YYYY-MM-DD
}

/**
 * Check if two dates are the same day (local time)
 */
function isSameDay(dateStr1, dateStr2) {
  return dateStr1 === dateStr2;
}

/**
 * Check if dateStr2 is exactly one day after dateStr1
 */
function isNextDay(dateStr1, dateStr2) {
  const date1 = new Date(dateStr1 + 'T00:00:00');
  const date2 = new Date(dateStr2 + 'T00:00:00');
  const diffDays = (date2 - date1) / (24 * 60 * 60 * 1000);
  return diffDays === 1;
}

/**
 * Get days between two date strings
 */
function daysBetween(dateStr1, dateStr2) {
  const date1 = new Date(dateStr1 + 'T00:00:00');
  const date2 = new Date(dateStr2 + 'T00:00:00');
  return Math.floor((date2 - date1) / (24 * 60 * 60 * 1000));
}
```

### 4.3 API Contracts

#### `updateStreak(schema)`

```javascript
/**
 * Update streak state based on current date
 * Call this at start of each session
 *
 * @param {Object} schema - Full schema object
 * @returns {Object} { schema, streakBroken, freezeUsed, streakIncreased }
 */
function updateStreak(schema) {
  const today = getLocalDateString();
  const lastStudy = schema.stats.streak.last_study_date;

  let streakBroken = false;
  let freezeUsed = false;
  let streakIncreased = false;

  if (!lastStudy) {
    // First ever study session
    schema.stats.streak.current = 1;
    schema.stats.streak.longest = 1;
    schema.stats.streak.last_study_date = today;
    streakIncreased = true;
  } else if (isSameDay(lastStudy, today)) {
    // Already studied today - no change
  } else if (isNextDay(lastStudy, today)) {
    // Consecutive day - increment streak
    schema.stats.streak.current += 1;
    schema.stats.streak.last_study_date = today;
    streakIncreased = true;

    // Update longest streak
    if (schema.stats.streak.current > schema.stats.streak.longest) {
      schema.stats.streak.longest = schema.stats.streak.current;
    }

    // Check for freeze earning (every 7 days, max 2)
    if (schema.stats.streak.current % 7 === 0 &&
        schema.stats.streak.freezes_available < 2 &&
        schema.stats.streak.current > schema.stats.streak.freezes_earned_at) {
      schema.stats.streak.freezes_available += 1;
      schema.stats.streak.freezes_earned_at = schema.stats.streak.current;
    }
  } else {
    // Gap detected - check how many days
    const daysMissed = daysBetween(lastStudy, today) - 1;

    if (daysMissed === 1 && schema.stats.streak.freezes_available > 0) {
      // Use freeze for single missed day
      schema.stats.streak.freezes_available -= 1;
      schema.stats.streak.freeze_used_date = lastStudy;
      schema.stats.streak.current += 1; // Continue streak
      schema.stats.streak.last_study_date = today;
      freezeUsed = true;
      streakIncreased = true;
    } else {
      // Streak broken
      schema.stats.streak.current = 1; // Start new streak
      schema.stats.streak.last_study_date = today;
      streakBroken = true;
      streakIncreased = true; // New streak of 1
    }
  }

  return { schema, streakBroken, freezeUsed, streakIncreased };
}
```

#### `isStreakAtRisk(schema)`

```javascript
/**
 * Check if streak is at risk (no study today, after 6 PM)
 *
 * @param {Object} schema - Full schema object
 * @returns {boolean} True if streak is at risk
 */
function isStreakAtRisk(schema) {
  const now = new Date();
  const today = getLocalDateString(now);
  const lastStudy = schema.stats.streak.last_study_date;
  const currentHour = now.getHours();

  // Only at risk if:
  // 1. Has an active streak (> 0)
  // 2. Haven't studied today
  // 3. It's after 6 PM (18:00)
  return schema.stats.streak.current > 0 &&
         lastStudy !== today &&
         currentHour >= 18;
}
```

#### `getStreakMilestone(streakDays)`

```javascript
/**
 * Check if current streak is at a milestone
 *
 * @param {number} streakDays - Current streak
 * @returns {Object|null} Milestone info or null
 */
function getStreakMilestone(streakDays) {
  const milestones = {
    7: { title: 'One Week!', message: "You've studied for a full week!", emoji: '🔥' },
    14: { title: 'Two Weeks!', message: 'Consistency is building!', emoji: '🔥🔥' },
    30: { title: 'One Month!', message: "That's serious dedication!", emoji: '🏆' },
    60: { title: 'Two Months!', message: "You're unstoppable!", emoji: '💪' },
    90: { title: 'Three Months!', message: 'A habit is born!', emoji: '⭐' },
    180: { title: 'Six Months!', message: 'Half a year of dedication!', emoji: '🌟' },
    365: { title: 'One Year!', message: "You're a legend!", emoji: '👑' }
  };

  return milestones[streakDays] || null;
}
```

---

## §5: Goals Manager Module

### 5.1 Daily Goal System

**Goal Options**: 5, 10, 15, 20, 25, or custom (1-100)
**Default**: 10 cards
**Completion**: Reviews + new cards introduced count toward goal

### 5.2 API Contracts

#### `setDailyGoal(schema, targetCards)`

```javascript
/**
 * Set daily goal target
 *
 * @param {Object} schema - Full schema object
 * @param {number} targetCards - Goal target (1-100)
 * @returns {Object} Updated schema
 */
function setDailyGoal(schema, targetCards) {
  if (targetCards < 1 || targetCards > 100) {
    throw new Error('Daily goal must be between 1 and 100');
  }

  schema.settings.daily_goal.target_cards = targetCards;
  return schema;
}
```

#### `getGoalProgress(schema)`

```javascript
/**
 * Get current goal progress
 *
 * @param {Object} schema - Full schema object
 * @returns {Object} { target, completed, percentage, isComplete }
 */
function getGoalProgress(schema) {
  const target = schema.settings.daily_goal.target_cards;
  const completed = schema.stats.today.reviews_completed +
                    schema.stats.today.new_cards_introduced;
  const percentage = Math.min(100, Math.round((completed / target) * 100));
  const isComplete = completed >= target;

  return { target, completed, percentage, isComplete };
}
```

#### `checkGoalCompletion(schema)`

```javascript
/**
 * Check if goal was just completed and award bonus
 *
 * @param {Object} schema - Full schema object
 * @returns {Object} { schema, justCompleted, bonusXP }
 */
function checkGoalCompletion(schema) {
  const progress = getGoalProgress(schema);

  // Check if goal just completed (wasn't already marked)
  if (progress.isComplete && !schema.stats.today.goal_completed) {
    schema.stats.today.goal_completed = true;
    const bonusXP = 50;

    return {
      schema,
      justCompleted: true,
      bonusXP
    };
  }

  return {
    schema,
    justCompleted: false,
    bonusXP: 0
  };
}
```

### 5.3 Browser Notifications

```javascript
/**
 * Request notification permission
 *
 * @returns {Promise<boolean>} True if permission granted
 */
async function requestNotificationPermission() {
  if (!('Notification' in window)) {
    console.warn('Browser does not support notifications');
    return false;
  }

  const permission = await Notification.requestPermission();
  return permission === 'granted';
}

/**
 * Schedule daily reminder notification
 *
 * @param {string} time - HH:MM format
 * @param {number} streakDays - Current streak for message
 */
function scheduleReminder(time, streakDays) {
  const [hours, minutes] = time.split(':').map(Number);
  const now = new Date();

  let reminderTime = new Date();
  reminderTime.setHours(hours, minutes, 0, 0);

  // If time has passed today, schedule for tomorrow
  if (reminderTime <= now) {
    reminderTime.setDate(reminderTime.getDate() + 1);
  }

  const delay = reminderTime - now;

  setTimeout(() => {
    if (Notification.permission === 'granted') {
      new Notification("Don't break your streak! 🔥", {
        body: `You have a ${streakDays}-day streak. Study now to keep it alive!`,
        icon: '/content/kanji/images/icon.png'
      });
    }
  }, delay);
}
```

---

## §6: Dashboard Visualizations

### 6.1 Rendering Approach

**Philosophy**: No external charting libraries. Use CSS and SVG for all visualizations.

| Component | Technique | Notes |
|-----------|-----------|-------|
| Heatmap | CSS Grid | 7 rows x 52-53 columns |
| Mastery Rings | SVG `<circle>` with stroke-dasharray | Animated on load |
| Progress Bars | CSS width percentage | Simple, performant |
| Trend Line | SVG `<polyline>` | 8 data points |

### 6.2 Study Heatmap (365-Day Calendar)

```javascript
/**
 * Generate heatmap data for past 365 days
 *
 * @param {Object} dailyHistory - stats.daily_history object
 * @returns {Array} Array of { date, reviews, intensity } objects
 */
function generateHeatmapData(dailyHistory) {
  const data = [];
  const today = new Date();

  for (let i = 364; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    const dateStr = getLocalDateString(date);

    const dayData = dailyHistory[dateStr] || { reviews: 0 };
    const reviews = dayData.reviews;

    // Intensity levels: 0, 1, 2, 3, 4
    let intensity = 0;
    if (reviews > 0) intensity = 1;
    if (reviews > 10) intensity = 2;
    if (reviews > 25) intensity = 3;
    if (reviews > 50) intensity = 4;

    data.push({
      date: dateStr,
      reviews,
      intensity,
      dayOfWeek: date.getDay(), // 0 = Sunday
      weekIndex: Math.floor(i / 7)
    });
  }

  return data;
}
```

**CSS for Heatmap**:

```css
.heatmap-grid {
  display: grid;
  grid-template-columns: repeat(53, 12px);
  grid-template-rows: repeat(7, 12px);
  gap: 2px;
}

.heatmap-cell {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.heatmap-cell[data-intensity="0"] { background: #ebedf0; }
.heatmap-cell[data-intensity="1"] { background: #9be9a8; }
.heatmap-cell[data-intensity="2"] { background: #40c463; }
.heatmap-cell[data-intensity="3"] { background: #30a14e; }
.heatmap-cell[data-intensity="4"] { background: #216e39; }
```

### 6.3 Mastery Rings (SVG)

```javascript
/**
 * Create SVG for circular progress ring
 *
 * @param {number} percentage - 0-100
 * @param {string} label - Topic name
 * @param {string} color - Ring color
 * @returns {string} SVG markup
 */
function createMasteryRing(percentage, label, color) {
  const radius = 40;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percentage / 100) * circumference;

  return `
    <svg width="100" height="100" viewBox="0 0 100 100">
      <!-- Background circle -->
      <circle
        cx="50" cy="50" r="${radius}"
        fill="none" stroke="#e0e0e0" stroke-width="8"
      />
      <!-- Progress circle -->
      <circle
        cx="50" cy="50" r="${radius}"
        fill="none" stroke="${color}" stroke-width="8"
        stroke-dasharray="${circumference}"
        stroke-dashoffset="${offset}"
        stroke-linecap="round"
        transform="rotate(-90 50 50)"
        class="ring-progress"
      />
      <!-- Center text -->
      <text x="50" y="45" text-anchor="middle" font-size="14" font-weight="bold">
        ${Math.round(percentage)}%
      </text>
      <text x="50" y="62" text-anchor="middle" font-size="10">
        ${label}
      </text>
    </svg>
  `;
}
```

**CSS for Ring Animation**:

```css
.ring-progress {
  transition: stroke-dashoffset 1s ease-in-out;
}

/* Initial state for animation */
.ring-progress.animating {
  stroke-dashoffset: var(--circumference);
}
```

### 6.4 Trend Line (SVG Polyline)

```javascript
/**
 * Generate trend line SVG
 *
 * @param {Array} snapshots - stats.mastery_snapshots array
 * @returns {string} SVG markup
 */
function createTrendLine(snapshots) {
  const width = 300;
  const height = 100;
  const padding = 10;

  // Take last 8 weeks
  const data = snapshots.slice(-8);

  if (data.length < 2) {
    return '<p class="no-data">Not enough data for trend</p>';
  }

  // Scale points
  const xStep = (width - 2 * padding) / (data.length - 1);
  const yMax = 100;
  const yScale = (height - 2 * padding) / yMax;

  const points = data.map((snapshot, i) => {
    const x = padding + i * xStep;
    const y = height - padding - (snapshot.overall * yScale);
    return `${x},${y}`;
  }).join(' ');

  return `
    <svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">
      <!-- Grid lines -->
      <line x1="${padding}" y1="${height - padding}" x2="${width - padding}" y2="${height - padding}" stroke="#e0e0e0" />
      <line x1="${padding}" y1="${padding}" x2="${padding}" y2="${height - padding}" stroke="#e0e0e0" />

      <!-- Trend line -->
      <polyline
        points="${points}"
        fill="none"
        stroke="#3b82f6"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />

      <!-- Data points -->
      ${data.map((snapshot, i) => {
        const x = padding + i * xStep;
        const y = height - padding - (snapshot.overall * yScale);
        return `<circle cx="${x}" cy="${y}" r="4" fill="#3b82f6" />`;
      }).join('\n')}
    </svg>
  `;
}
```

### 6.5 At-Risk Kanji Tracking

```javascript
/**
 * Track stage drops for at-risk panel
 * Call this in srs-engine after stage transition
 *
 * @param {Object} schema - Full schema
 * @param {string} character - Kanji character
 * @param {string} oldStage - Stage before review
 * @param {string} newStage - Stage after review
 * @returns {Object} Updated schema
 */
function trackAtRiskKanji(schema, character, oldStage, newStage) {
  const STAGE_ORDER = [
    'locked', 'lesson', 'apprentice_1', 'apprentice_2',
    'apprentice_3', 'apprentice_4', 'guru_1', 'guru_2',
    'master', 'enlightened', 'burned'
  ];

  const oldIndex = STAGE_ORDER.indexOf(oldStage);
  const newIndex = STAGE_ORDER.indexOf(newStage);

  // Only track if stage dropped
  if (newIndex < oldIndex) {
    const today = getLocalDateString();

    // Remove existing entry for this kanji
    schema.stats.at_risk_kanji = schema.stats.at_risk_kanji.filter(
      k => k.character !== character
    );

    // Add new at-risk entry
    schema.stats.at_risk_kanji.unshift({
      character,
      dropped_from: oldStage,
      dropped_to: newStage,
      date: today
    });

    // Keep max 50 entries
    if (schema.stats.at_risk_kanji.length > 50) {
      schema.stats.at_risk_kanji = schema.stats.at_risk_kanji.slice(0, 50);
    }

    // Clean up entries older than 7 days
    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 7);
    const weekAgoStr = getLocalDateString(weekAgo);

    schema.stats.at_risk_kanji = schema.stats.at_risk_kanji.filter(
      k => k.date >= weekAgoStr
    );
  }

  return schema;
}
```

---

## §7: Testing Strategy

### 7.1 Unit Tests

**Module**: `xp-engine.js`

| Test Case | Input | Expected Output |
|-----------|-------|-----------------|
| Base XP only | quality=0, streak=0 | 10 XP |
| Good quality bonus | quality=4, streak=0 | 15 XP |
| Easy quality bonus | quality=5, streak=0 | 20 XP |
| Streak bonus tier 1 | quality=4, streak=7 | 17 XP (15 * 1.1) |
| Streak bonus tier 5 | quality=5, streak=35 | 30 XP (20 * 1.5) |
| Level from 0 XP | totalXP=0 | level=1 |
| Level from 500 XP | totalXP=500 | level=4 |
| Level from 10000 XP | totalXP=10000 | level=17 |
| Level cap at 60 | totalXP=999999 | level=60 |

**Module**: `streak-manager.js`

| Test Case | Input | Expected Output |
|-----------|-------|-----------------|
| First study ever | lastStudy=null | streak=1 |
| Same day study | lastStudy=today | streak unchanged |
| Consecutive day | lastStudy=yesterday | streak+1 |
| Gap of 1 day, has freeze | gap=1, freezes=1 | streak continues, freeze-1 |
| Gap of 1 day, no freeze | gap=1, freezes=0 | streak=1 (reset) |
| Gap of 2+ days | gap=2 | streak=1 (reset) |
| Freeze earned at day 7 | streak=7, freezes=0 | freezes=1 |
| Freeze cap at 2 | streak=14, freezes=2 | freezes=2 (no change) |
| At-risk after 6 PM | hour=18, no study today | true |
| Not at-risk before 6 PM | hour=14, no study today | false |

**Module**: `goals-manager.js`

| Test Case | Input | Expected Output |
|-----------|-------|-----------------|
| Goal progress at 50% | target=10, completed=5 | percentage=50, isComplete=false |
| Goal complete | target=10, completed=10 | percentage=100, isComplete=true |
| Goal overachieved | target=10, completed=15 | percentage=100, isComplete=true |
| Goal completion bonus | first time complete | bonusXP=50 |
| Already completed today | second completion | bonusXP=0 |

### 7.2 Integration Tests

**Test**: Full Review Flow with XP

1. Load schema (streak=10, level=5)
2. Complete review (quality=4)
3. Verify XP awarded (15 * 1.1 = 17)
4. Verify daily_history updated
5. Verify goal progress incremented

**Test**: Streak Break and Reset

1. Set last_study_date = 3 days ago
2. Start session
3. Verify streak reset to 1
4. Verify no freeze used

**Test**: Level Up Flow

1. Set XP to 1 below threshold
2. Award 10 XP
3. Verify level increased
4. Verify celebration returned

**Test**: Weekly Snapshot

1. Fast-forward 7 days
2. Trigger snapshot
3. Verify mastery_snapshots updated
4. Verify trend data available

### 7.3 Edge Cases

**XP System**:
- [ ] Max level (60) - no more XP progress
- [ ] XP overflow (very large numbers)
- [ ] Negative XP (should never happen)

**Streak System**:
- [ ] Timezone edge cases (midnight boundary)
- [ ] Daylight saving time transitions
- [ ] First day of use
- [ ] Multiple sessions same day

**Goals**:
- [ ] Goal of 1 card
- [ ] Goal of 100 cards
- [ ] Day rollover mid-session
- [ ] Goal disabled

**Visualizations**:
- [ ] Empty heatmap (new user)
- [ ] Partial heatmap (< 365 days)
- [ ] 0% mastery rings
- [ ] 100% mastery rings
- [ ] No trend data (< 2 weeks)

### 7.4 Browser Compatibility

| Feature | Chrome | Firefox | Safari | Notes |
|---------|--------|---------|--------|-------|
| localStorage v1.1.0 | ✓ | ✓ | ✓ | Size under 5 MB |
| CSS Grid (heatmap) | ✓ | ✓ | ✓ | Full support |
| SVG animations | ✓ | ✓ | ✓ | Full support |
| Notification API | ✓ | ✓ | ✓ | Requires permission |

### 7.5 Performance Targets

| Operation | Target | Notes |
|-----------|--------|-------|
| Schema migration | <50ms | One-time on upgrade |
| XP calculation | <1ms | Per review |
| Streak update | <5ms | Per session |
| Heatmap render | <100ms | 365 cells |
| Ring render | <50ms | 4 rings |
| Trend line render | <50ms | 8 data points |

---

## Appendix A: File Locations

| File | Purpose |
|------|---------|
| `content/kanji/js/storage.js` | Extended with v1.1.0 migration |
| `content/kanji/js/xp-engine.js` | NEW: XP and level calculations |
| `content/kanji/js/streak-manager.js` | NEW: Streak logic |
| `content/kanji/js/goals-manager.js` | NEW: Daily goals |
| `content/kanji/js/session-manager.js` | Extended: calls engagement layer |
| `content/kanji/js/mastery-calculator.js` | Extended: snapshots |
| `content/kanji/css/dashboard.css` | NEW: Visualization styles |
| `content/kanji/index.html` | Extended: dashboard UI |

---

## Appendix B: Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2026-01-25 | Architect (Claude) | Initial draft for Phase 2 |

---

**End of TDD-003**

**Next Steps**:
1. PM creates GitHub Epic and Task issues
2. Developer implements per §3-§6 API Contracts
3. Tester verifies against §7 Testing Strategy
