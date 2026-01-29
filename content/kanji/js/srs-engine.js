/**
 * SRS Engine Module - SM-2 Algorithm Implementation
 *
 * Version: 1.0.0
 * Task: T1.2/T1.3 - Implement SM-2 algorithm and stage transitions
 * Related: PRD-001, TDD-001 §3, §4, §6.2
 *
 * Responsibilities:
 * - Process review responses using SM-2 algorithm
 * - Calculate next review intervals
 * - Manage mastery stage transitions
 * - Track review statistics and history
 *
 * Dependencies:
 * - storage.js (STAGES constant, LIMITS constant)
 *
 * The SM-2 algorithm optimizes learning by scheduling reviews based on
 * recall quality. Cards you remember well are reviewed less frequently;
 * cards you struggle with are reviewed more often.
 */

// ============================================================================
// SM-2 ALGORITHM CONSTANTS
// ============================================================================

/**
 * SM-2 algorithm constants (from TDD §3.2-3.5)
 */
const SM2_CONSTANTS = {
  /** Minimum ease factor - prevents cards from becoming too difficult */
  MIN_EASE_FACTOR: 1.3,

  /** Maximum ease factor - prevents runaway interval growth */
  MAX_EASE_FACTOR: 5.0,

  /** Quality threshold for passing (quality >= 3 is considered correct) */
  PASSING_THRESHOLD: 3,

  /** First successful review interval (1 day) */
  FIRST_INTERVAL: 1,

  /** Second successful review interval (6 days) */
  SECOND_INTERVAL: 6,

  /** Default ease factor for new cards */
  DEFAULT_EASE_FACTOR: 2.5
};

/**
 * Quality rating definitions (from TDD §3.2)
 * Maps user button responses to SM-2 quality values
 */
const QUALITY = {
  /** Complete blackout - couldn't recall at all */
  AGAIN: 0,

  /** Correct but with significant difficulty */
  HARD: 2,

  /** Correct with some hesitation */
  GOOD: 4,

  /** Perfect recall, immediate response */
  EASY: 5
};

/**
 * Stage order for progression tracking
 * Index position determines stage level (0 = lowest, 10 = highest)
 */
const STAGE_ORDER = Object.freeze([
  'locked',
  'lesson',
  'apprentice_1',
  'apprentice_2',
  'apprentice_3',
  'apprentice_4',
  'guru_1',
  'guru_2',
  'master',
  'enlightened',
  'burned'
]);

/**
 * Index of the minimum stage for regression (can't go below apprentice_1)
 */
const MIN_REGRESSION_INDEX = STAGE_ORDER.indexOf('apprentice_1');

/**
 * Stage-specific intervals (in days) for initial placement
 * Used when a card first enters a stage
 */
const STAGE_INTERVALS = {
  locked: 0,
  lesson: 0.167,        // 4 hours
  apprentice_1: 0.333,  // 8 hours
  apprentice_2: 1,      // 1 day
  apprentice_3: 2,      // 2 days
  apprentice_4: 4,      // 4 days
  guru_1: 7,            // 1 week
  guru_2: 14,           // 2 weeks
  master: 30,           // 1 month
  enlightened: 120,     // 4 months
  burned: null          // No review
};

// ============================================================================
// CORE SM-2 ALGORITHM FUNCTIONS
// ============================================================================

/**
 * Calculate the next review interval using the SM-2 algorithm
 *
 * The SM-2 formula:
 * - First success: 1 day
 * - Second success: 6 days
 * - Subsequent: previous_interval × ease_factor
 * - Failure (quality < 3): reset to 1 day
 *
 * @param {Object} srs - Current SRS state
 * @param {number} srs.interval_days - Current interval in days
 * @param {number} srs.ease_factor - Current ease factor (1.3-5.0)
 * @param {number} srs.repetitions - Consecutive successful repetitions
 * @param {number} quality - Quality rating (0, 2, 4, or 5)
 * @returns {Object} Object with new interval_days, ease_factor, and repetitions
 */
function calculateNextInterval(srs, quality) {
  // Validate quality input
  if (![0, 2, 4, 5].includes(quality)) {
    console.warn(`Invalid quality ${quality}, treating as HARD (2)`);
    quality = QUALITY.HARD;
  }

  // Calculate ease factor adjustment using SM-2 formula
  // Formula: EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
  const easeAdjustment = 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02);
  let newEaseFactor = srs.ease_factor + easeAdjustment;

  // Clamp ease factor to valid range [1.3, 5.0]
  newEaseFactor = Math.max(
    SM2_CONSTANTS.MIN_EASE_FACTOR,
    Math.min(SM2_CONSTANTS.MAX_EASE_FACTOR, newEaseFactor)
  );

  let newInterval;
  let newRepetitions;

  if (quality >= SM2_CONSTANTS.PASSING_THRESHOLD) {
    // Passing grade - increase interval based on repetition count
    if (srs.repetitions === 0) {
      // First successful review
      newInterval = SM2_CONSTANTS.FIRST_INTERVAL;
    } else if (srs.repetitions === 1) {
      // Second successful review
      newInterval = SM2_CONSTANTS.SECOND_INTERVAL;
    } else {
      // Subsequent reviews - multiply by ease factor
      newInterval = Math.round(srs.interval_days * newEaseFactor);
    }
    newRepetitions = srs.repetitions + 1;
  } else {
    // Failing grade - reset to beginning
    newInterval = SM2_CONSTANTS.FIRST_INTERVAL;
    newRepetitions = 0;
  }

  return {
    interval_days: newInterval,
    ease_factor: newEaseFactor,
    repetitions: newRepetitions
  };
}

/**
 * Calculate the new mastery stage based on review quality
 *
 * Stage transition rules (from TDD §4.2):
 * - AGAIN (0): -2 stages (min: apprentice_1)
 * - HARD (2): -1 stage (min: apprentice_1)
 * - GOOD (4): +1 stage
 * - EASY (5): +1 stage
 *
 * Special cases:
 * - Locked cards cannot be reviewed (must be unlocked first)
 * - Burned cards are retired and don't regress
 *
 * @param {string} currentStage - Current mastery stage
 * @param {number} quality - Quality rating (0, 2, 4, or 5)
 * @returns {string} New mastery stage
 */
function updateStage(currentStage, quality) {
  // Validate stage
  if (!STAGE_ORDER.includes(currentStage)) {
    console.error(`Invalid stage: ${currentStage}`);
    return currentStage;
  }

  // Locked cards cannot be reviewed
  if (currentStage === 'locked') {
    console.warn('Cannot review locked card - unlock first');
    return 'locked';
  }

  // Burned cards are retired (no regression)
  if (currentStage === 'burned') {
    return 'burned';
  }

  const currentIndex = STAGE_ORDER.indexOf(currentStage);
  let newIndex;

  switch (quality) {
    case QUALITY.AGAIN:
      // Complete failure: drop 2 stages
      newIndex = Math.max(currentIndex - 2, MIN_REGRESSION_INDEX);
      break;

    case QUALITY.HARD:
      // Struggled but correct: drop 1 stage
      newIndex = Math.max(currentIndex - 1, MIN_REGRESSION_INDEX);
      break;

    case QUALITY.GOOD:
    case QUALITY.EASY:
      // Correct response: advance 1 stage
      newIndex = Math.min(currentIndex + 1, STAGE_ORDER.length - 1);
      break;

    default:
      // Handle unexpected quality values (1, 3) - no change
      console.warn(`Unexpected quality value: ${quality}, no stage change`);
      newIndex = currentIndex;
  }

  return STAGE_ORDER[newIndex];
}

/**
 * Process a review response and update the kanji progress object
 *
 * This is the main entry point for the SRS engine. It:
 * 1. Updates SRS state (interval, ease factor, repetitions)
 * 2. Updates mastery stage
 * 3. Calculates next review date
 * 4. Adds history entry (capped at 50)
 * 5. Updates statistics
 *
 * @param {Object} kanji - Kanji progress object
 * @param {string} kanji.character - The kanji character
 * @param {Object} kanji.srs - Current SRS state
 * @param {Array} kanji.history - Review history array
 * @param {number} quality - Quality rating (0, 2, 4, or 5)
 * @param {number} [responseTimeMs=null] - Optional response time in milliseconds
 * @returns {Object} Updated kanji progress object (new object, immutable pattern)
 */
function processReview(kanji, quality, responseTimeMs = null) {
  // Validate inputs
  if (!kanji || !kanji.srs) {
    throw new Error('Invalid kanji object: missing SRS state');
  }

  if (![0, 2, 4, 5].includes(quality)) {
    throw new Error(`Invalid quality rating: ${quality}. Must be 0, 2, 4, or 5`);
  }

  const now = new Date();
  const currentSRS = kanji.srs;
  const stageBefore = currentSRS.stage;

  // Handle first-time review (new card)
  let workingSRS = { ...currentSRS };
  if (currentSRS.is_new) {
    workingSRS.is_new = false;
    workingSRS.introduced_at = now.toISOString();

    // New cards start at lesson stage
    if (workingSRS.stage === 'locked') {
      workingSRS.stage = 'lesson';
    }
  }

  // Calculate new interval using SM-2 algorithm
  const intervalResult = calculateNextInterval(workingSRS, quality);

  // Calculate new stage
  const newStage = updateStage(workingSRS.stage, quality);

  // Calculate next review date
  let nextReviewDate = null;
  if (newStage !== 'burned') {
    nextReviewDate = new Date(
      now.getTime() + intervalResult.interval_days * 24 * 60 * 60 * 1000
    ).toISOString();
  }

  // Update statistics
  const totalReviews = currentSRS.total_reviews + 1;
  const correctCount = quality >= SM2_CONSTANTS.PASSING_THRESHOLD
    ? currentSRS.correct_count + 1
    : currentSRS.correct_count;

  // Create history entry
  const historyEntry = {
    timestamp: now.toISOString(),
    quality: quality,
    stage_before: stageBefore,
    stage_after: newStage
  };

  // Add response time if provided
  if (responseTimeMs !== null && typeof responseTimeMs === 'number' && responseTimeMs >= 0) {
    historyEntry.response_time_ms = Math.round(responseTimeMs);
  }

  // Update history array (prepend new entry, cap at 50)
  const MAX_HISTORY = 50;
  const newHistory = [historyEntry, ...(kanji.history || [])].slice(0, MAX_HISTORY);

  // Build updated SRS state
  const updatedSRS = {
    stage: newStage,
    interval_days: intervalResult.interval_days,
    ease_factor: intervalResult.ease_factor,
    repetitions: intervalResult.repetitions,
    last_reviewed: now.toISOString(),
    next_review_date: nextReviewDate,
    total_reviews: totalReviews,
    correct_count: correctCount,
    is_new: false,
    introduced_at: workingSRS.introduced_at || currentSRS.introduced_at
  };

  // Return new kanji object (immutable pattern)
  return {
    ...kanji,
    srs: updatedSRS,
    history: newHistory
  };
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Unlock a locked kanji for study
 *
 * Moves a kanji from 'locked' to 'lesson' stage, preparing it
 * for its first review.
 *
 * @param {Object} kanji - Kanji progress object
 * @returns {Object} Updated kanji progress object
 * @throws {Error} If kanji is not in locked state
 */
function unlockKanji(kanji) {
  if (!kanji || !kanji.srs) {
    throw new Error('Invalid kanji object');
  }

  if (kanji.srs.stage !== 'locked') {
    throw new Error(`Cannot unlock kanji - current stage is ${kanji.srs.stage}`);
  }

  const now = new Date();

  return {
    ...kanji,
    srs: {
      ...kanji.srs,
      stage: 'lesson',
      interval_days: STAGE_INTERVALS.lesson,
      next_review_date: now.toISOString(), // Due immediately
      is_new: true,
      introduced_at: now.toISOString()
    }
  };
}

/**
 * Get the mastery score for a stage
 *
 * Used for calculating JLPT and topic mastery percentages.
 *
 * @param {string} stage - Mastery stage
 * @returns {number} Mastery score (0-100)
 */
function getStageMasteryScore(stage) {
  const scores = {
    locked: 0,
    lesson: 10,
    apprentice_1: 20,
    apprentice_2: 30,
    apprentice_3: 40,
    apprentice_4: 50,
    guru_1: 60,
    guru_2: 70,
    master: 80,
    enlightened: 90,
    burned: 100
  };

  return scores[stage] || 0;
}

/**
 * Check if a kanji is due for review
 *
 * @param {Object} kanji - Kanji progress object
 * @param {Date} [asOf=now] - Optional date to check against
 * @returns {boolean} True if kanji is due for review
 */
function isDue(kanji, asOf = new Date()) {
  if (!kanji || !kanji.srs) {
    return false;
  }

  // Locked and burned cards are never due
  if (kanji.srs.stage === 'locked' || kanji.srs.stage === 'burned') {
    return false;
  }

  // New cards (lesson stage, never reviewed) are always due
  if (kanji.srs.is_new || kanji.srs.next_review_date === null) {
    return true;
  }

  // Check if next review date has passed
  const nextReview = new Date(kanji.srs.next_review_date);
  return nextReview <= asOf;
}

/**
 * Calculate how overdue a kanji is for review
 *
 * @param {Object} kanji - Kanji progress object
 * @param {Date} [asOf=now] - Optional date to check against
 * @returns {number} Days overdue (negative if not yet due, 0 if due now)
 */
function getOverdueDays(kanji, asOf = new Date()) {
  if (!kanji || !kanji.srs || !kanji.srs.next_review_date) {
    return 0;
  }

  if (kanji.srs.stage === 'locked' || kanji.srs.stage === 'burned') {
    return -Infinity;
  }

  const nextReview = new Date(kanji.srs.next_review_date);
  const diffMs = asOf.getTime() - nextReview.getTime();
  return diffMs / (24 * 60 * 60 * 1000);
}

/**
 * Get the expected interval for a stage (not SM-2 calculated)
 *
 * This is the "default" interval when first entering a stage,
 * not the dynamically calculated SM-2 interval.
 *
 * @param {string} stage - Mastery stage
 * @returns {number|null} Interval in days, or null for burned
 */
function getStageInterval(stage) {
  return STAGE_INTERVALS[stage] !== undefined ? STAGE_INTERVALS[stage] : null;
}

/**
 * Get the index of a stage in the progression order
 *
 * @param {string} stage - Mastery stage
 * @returns {number} Index (0-10), or -1 if invalid
 */
function getStageIndex(stage) {
  return STAGE_ORDER.indexOf(stage);
}

/**
 * Get the stage at a specific index in the progression
 *
 * @param {number} index - Stage index (0-10)
 * @returns {string|null} Stage name, or null if index invalid
 */
function getStageByIndex(index) {
  if (index < 0 || index >= STAGE_ORDER.length) {
    return null;
  }
  return STAGE_ORDER[index];
}

/**
 * Check if one stage is higher than another
 *
 * @param {string} stageA - First stage
 * @param {string} stageB - Second stage
 * @returns {boolean} True if stageA is higher than stageB
 */
function isHigherStage(stageA, stageB) {
  return STAGE_ORDER.indexOf(stageA) > STAGE_ORDER.indexOf(stageB);
}

/**
 * Get a human-readable description of the quality rating
 *
 * @param {number} quality - Quality rating (0, 2, 4, 5)
 * @returns {string} Description
 */
function getQualityDescription(quality) {
  const descriptions = {
    0: 'Again - Complete blackout',
    2: 'Hard - Struggled but correct',
    4: 'Good - Correct with some hesitation',
    5: 'Easy - Perfect recall'
  };

  return descriptions[quality] || `Unknown quality: ${quality}`;
}

/**
 * Create a default SRS state for a new kanji
 *
 * @returns {Object} Default SRS state object
 */
function createDefaultSRSState() {
  return {
    stage: 'locked',
    interval_days: 0,
    ease_factor: SM2_CONSTANTS.DEFAULT_EASE_FACTOR,
    repetitions: 0,
    last_reviewed: null,
    next_review_date: null,
    total_reviews: 0,
    correct_count: 0,
    is_new: true,
    introduced_at: null
  };
}

// ============================================================================
// EXPORTS (Browser Global)
// ============================================================================

// Make functions available globally for browser use
if (typeof window !== 'undefined') {
  window.SRSEngine = {
    // Core functions
    processReview,
    calculateNextInterval,
    updateStage,

    // Helper functions
    unlockKanji,
    getStageMasteryScore,
    isDue,
    getOverdueDays,
    getStageInterval,
    getStageIndex,
    getStageByIndex,
    isHigherStage,
    getQualityDescription,
    createDefaultSRSState,

    // Constants
    SM2_CONSTANTS,
    QUALITY,
    STAGE_ORDER,
    STAGE_INTERVALS
  };
}
