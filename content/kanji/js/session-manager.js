/**
 * Session Manager Module - Study Queue and Session Orchestration
 *
 * Version: 1.0.0
 * Task: T1.4/T1.5 - Implement queue management and new card limiting
 * Related: PRD-001, TDD-001 §6.4
 *
 * Responsibilities:
 * - Build study queue (due cards + new cards)
 * - Enforce new card daily limits
 * - Track session statistics
 * - Coordinate review processing with storage and SRS engine
 *
 * Dependencies:
 * - storage.js (loadSchema, saveSchema, updateKanjiProgress)
 * - srs-engine.js (processReview, unlockKanji, isDue)
 * - mastery-calculator.js (calculateStageDistribution)
 */

// ============================================================================
// SESSION CONSTANTS
// ============================================================================

/**
 * Session configuration defaults
 */
const SESSION_DEFAULTS = {
  /** Default new cards per day */
  NEW_CARDS_PER_DAY: 10,

  /** Maximum new cards per day allowed */
  MAX_NEW_CARDS_PER_DAY: 50,

  /** Minimum new cards per day allowed */
  MIN_NEW_CARDS_PER_DAY: 1
};

// ============================================================================
// QUEUE BUILDING FUNCTIONS
// ============================================================================

/**
 * Get all kanji that are due for review
 *
 * Filters by optional JLPT level and topic, excludes locked and burned.
 * Sorts by due date (most overdue first).
 *
 * @param {Object} schema - Full schema from localStorage
 * @param {Object} [filters={}] - Filter options
 * @param {string} [filters.jlpt_level='All'] - JLPT level filter
 * @param {string} [filters.topic='All'] - Topic filter
 * @returns {Array} Array of due kanji progress objects, sorted by urgency
 */
function getDueCards(schema, filters = {}) {
  if (!schema || !schema.kanji) {
    return [];
  }

  const jlptFilter = filters.jlpt_level || 'All';
  const topicFilter = filters.topic || 'All';
  const now = new Date();

  // Filter kanji
  const dueCards = Object.values(schema.kanji).filter(kanji => {
    // Skip locked and burned
    if (!kanji.srs || kanji.srs.stage === 'locked' || kanji.srs.stage === 'burned') {
      return false;
    }

    // Apply JLPT filter
    if (jlptFilter !== 'All' && kanji.jlpt_level !== jlptFilter) {
      return false;
    }

    // Apply topic filter
    if (topicFilter !== 'All') {
      if (!kanji.topics || !kanji.topics.includes(topicFilter)) {
        return false;
      }
    }

    // Check if due (use SRSEngine.isDue if available, otherwise manual check)
    if (typeof window !== 'undefined' && window.SRSEngine && window.SRSEngine.isDue) {
      return window.SRSEngine.isDue(kanji, now);
    }

    // Manual due check
    if (kanji.srs.is_new || kanji.srs.next_review_date === null) {
      return true;
    }
    return new Date(kanji.srs.next_review_date) <= now;
  });

  // Sort by due date (most overdue first)
  dueCards.sort((a, b) => {
    const dateA = a.srs.next_review_date ? new Date(a.srs.next_review_date) : new Date(0);
    const dateB = b.srs.next_review_date ? new Date(b.srs.next_review_date) : new Date(0);
    return dateA - dateB;
  });

  return dueCards;
}

/**
 * Get new kanji to introduce (locked -> lesson)
 *
 * Respects daily new card limit. Returns empty if limit reached.
 *
 * @param {Object} schema - Full schema from localStorage
 * @param {number} [limit] - Max new cards to return (default from settings)
 * @param {Object} [filters={}] - Filter options
 * @param {string} [filters.jlpt_level='All'] - JLPT level filter
 * @param {string} [filters.topic='All'] - Topic filter
 * @returns {Array} Array of locked kanji to introduce
 */
function getNewCards(schema, limit, filters = {}) {
  if (!schema || !schema.kanji) {
    return [];
  }

  // Get limit from settings if not provided
  const maxNewCards = limit !== undefined ? limit : (
    schema.settings && schema.settings.new_cards_per_day
      ? schema.settings.new_cards_per_day
      : SESSION_DEFAULTS.NEW_CARDS_PER_DAY
  );

  // Check today's stats to see how many already introduced
  const today = new Date().toISOString().split('T')[0];
  const todayStats = schema.stats && schema.stats.today;

  let alreadyIntroduced = 0;
  if (todayStats && todayStats.date === today) {
    alreadyIntroduced = todayStats.new_cards_introduced || 0;
  }

  // Calculate remaining slots
  const remaining = Math.max(0, maxNewCards - alreadyIntroduced);

  if (remaining <= 0) {
    return [];
  }

  const jlptFilter = filters.jlpt_level || 'All';
  const topicFilter = filters.topic || 'All';

  // Find locked kanji matching filters
  const lockedKanji = Object.values(schema.kanji).filter(kanji => {
    // Must be locked
    if (!kanji.srs || kanji.srs.stage !== 'locked') {
      return false;
    }

    // Apply JLPT filter
    if (jlptFilter !== 'All' && kanji.jlpt_level !== jlptFilter) {
      return false;
    }

    // Apply topic filter
    if (topicFilter !== 'All') {
      if (!kanji.topics || !kanji.topics.includes(topicFilter)) {
        return false;
      }
    }

    return true;
  });

  // Sort by JLPT level (N5 first, then N4, etc.) for progression
  // Use ?? instead of || because N5's order value is 0 (falsy)
  const jlptOrder = { 'N5': 0, 'N4': 1, 'N3': 2, 'N2': 3, 'N1': 4 };
  lockedKanji.sort((a, b) => {
    const orderA = jlptOrder[a.jlpt_level] ?? 5;
    const orderB = jlptOrder[b.jlpt_level] ?? 5;
    return orderA - orderB;
  });

  // Return up to remaining slots
  return lockedKanji.slice(0, remaining);
}

/**
 * Create a study session with due cards and new cards
 *
 * Combines due reviews with new cards (up to limit).
 * Randomizes card order for better learning.
 *
 * @param {Object} schema - Full schema from localStorage
 * @param {Object} [options={}] - Session options
 * @param {string} [options.jlpt_level='All'] - JLPT level filter
 * @param {string} [options.topic='All'] - Topic filter
 * @param {boolean} [options.includeNew=true] - Include new cards
 * @param {boolean} [options.shuffle=true] - Shuffle card order
 * @returns {Object} Session object with cards and metadata
 */
function createSession(schema, options = {}) {
  const filters = {
    jlpt_level: options.jlpt_level || 'All',
    topic: options.topic || 'All'
  };
  const includeNew = options.includeNew !== false;
  const shuffle = options.shuffle !== false;

  // Get due cards
  const dueCards = getDueCards(schema, filters);

  // Get new cards if enabled
  let newCards = [];
  if (includeNew) {
    newCards = getNewCards(schema, undefined, filters);
  }

  // Combine cards
  let allCards = [...dueCards, ...newCards];

  // Shuffle if enabled
  if (shuffle && allCards.length > 0) {
    allCards = shuffleArray(allCards);
  }

  return {
    cards: allCards,
    due_count: dueCards.length,
    new_count: newCards.length,
    total_count: allCards.length,
    session_start: new Date().toISOString(),
    filters: filters,
    current_index: 0,
    completed_count: 0,
    correct_count: 0
  };
}

// ============================================================================
// SESSION PROCESSING FUNCTIONS
// ============================================================================

/**
 * Process a review response within a session
 *
 * Updates kanji progress via SRS engine and saves to storage.
 *
 * @param {Object} schema - Full schema (will be mutated)
 * @param {Object} kanji - Kanji being reviewed
 * @param {number} quality - Quality rating (0, 2, 4, 5)
 * @param {number} [responseTimeMs] - Optional response time
 * @returns {Object} Updated kanji progress
 */
function processSessionReview(schema, kanji, quality, responseTimeMs) {
  if (!schema || !kanji || !kanji.character) {
    throw new Error('Invalid schema or kanji object');
  }

  // Process review via SRS engine
  let updated;
  if (typeof window !== 'undefined' && window.SRSEngine && window.SRSEngine.processReview) {
    updated = window.SRSEngine.processReview(kanji, quality, responseTimeMs);
  } else {
    throw new Error('SRSEngine not available');
  }

  // Update schema
  schema.kanji[kanji.character] = updated;

  // Update today's stats
  updateTodayStats(schema, quality);

  // Update stage distribution
  updateStageDistribution(schema);

  // Update metadata
  if (schema.metadata) {
    schema.metadata.last_modified = new Date().toISOString();
  }

  return updated;
}

/**
 * Introduce a new card (unlock from locked -> lesson)
 *
 * @param {Object} schema - Full schema (will be mutated)
 * @param {Object} kanji - Locked kanji to introduce
 * @returns {Object} Updated kanji progress (now in lesson stage)
 */
function introduceNewCard(schema, kanji) {
  if (!schema || !kanji || !kanji.character) {
    throw new Error('Invalid schema or kanji object');
  }

  if (!kanji.srs || kanji.srs.stage !== 'locked') {
    throw new Error('Kanji is not locked');
  }

  // Unlock via SRS engine
  let unlocked;
  if (typeof window !== 'undefined' && window.SRSEngine && window.SRSEngine.unlockKanji) {
    unlocked = window.SRSEngine.unlockKanji(kanji);
  } else {
    // Manual unlock if SRSEngine not available
    unlocked = {
      ...kanji,
      srs: {
        ...kanji.srs,
        stage: 'lesson',
        interval_days: 0.167,
        next_review_date: new Date().toISOString(),
        is_new: true,
        introduced_at: new Date().toISOString()
      }
    };
  }

  // Update schema
  schema.kanji[kanji.character] = unlocked;

  // Update today's new card count
  const today = new Date().toISOString().split('T')[0];
  if (!schema.stats.today || schema.stats.today.date !== today) {
    schema.stats.today = {
      date: today,
      new_cards_introduced: 0,
      reviews_completed: 0,
      correct_count: 0,
      session_count: 0
    };
  }
  schema.stats.today.new_cards_introduced++;

  // Update total kanji seen
  schema.stats.total_kanji_seen = (schema.stats.total_kanji_seen || 0) + 1;

  // Update stage distribution
  updateStageDistribution(schema);

  // Update metadata
  if (schema.metadata) {
    schema.metadata.last_modified = new Date().toISOString();
  }

  return unlocked;
}

// ============================================================================
// STATS UPDATE FUNCTIONS
// ============================================================================

/**
 * Update today's statistics after a review
 *
 * @param {Object} schema - Schema to update
 * @param {number} quality - Quality rating from review
 */
function updateTodayStats(schema, quality) {
  const today = new Date().toISOString().split('T')[0];

  // Initialize today's stats if needed
  if (!schema.stats.today || schema.stats.today.date !== today) {
    schema.stats.today = {
      date: today,
      new_cards_introduced: 0,
      reviews_completed: 0,
      correct_count: 0,
      session_count: 0
    };
  }

  // Increment review count
  schema.stats.today.reviews_completed++;

  // Increment correct count if passing
  if (quality >= 3) {
    schema.stats.today.correct_count++;
  }

  // Increment total reviews
  schema.stats.total_reviews = (schema.stats.total_reviews || 0) + 1;

  // Update streak
  updateStreak(schema);
}

/**
 * Update streak information
 *
 * @param {Object} schema - Schema to update
 */
function updateStreak(schema) {
  const today = new Date().toISOString().split('T')[0];
  const lastStudy = schema.stats.last_study_date;

  if (!lastStudy) {
    // First study session ever
    schema.stats.streak_days = 1;
    schema.stats.streak_start_date = today;
  } else if (lastStudy === today) {
    // Already studied today, no change
    return;
  } else {
    // Check if consecutive day with error handling
    try {
      const lastDate = new Date(lastStudy);
      const todayDate = new Date(today);

      // Validate date objects
      if (isNaN(lastDate.getTime()) || isNaN(todayDate.getTime())) {
        console.error('Invalid date in streak calculation, resetting streak');
        schema.stats.streak_days = 1;
        schema.stats.streak_start_date = today;
        schema.stats.last_study_date = today;
        return;
      }

      const diffDays = Math.floor((todayDate - lastDate) / (24 * 60 * 60 * 1000));

      if (diffDays === 1) {
        // Consecutive day - extend streak
        schema.stats.streak_days++;
      } else {
        // Streak broken - reset
        schema.stats.streak_days = 1;
        schema.stats.streak_start_date = today;
      }
    } catch (error) {
      console.error('Error in streak calculation:', error);
      schema.stats.streak_days = 1;
      schema.stats.streak_start_date = today;
    }
  }

  schema.stats.last_study_date = today;
}

/**
 * Update stage distribution cache
 *
 * @param {Object} schema - Schema to update
 */
function updateStageDistribution(schema) {
  // Use MasteryCalculator if available
  if (typeof window !== 'undefined' && window.MasteryCalculator && window.MasteryCalculator.calculateStageDistribution) {
    schema.stats.stage_distribution = window.MasteryCalculator.calculateStageDistribution(schema.kanji);
    return;
  }

  // Manual calculation
  const distribution = {
    locked: 0,
    lesson: 0,
    apprentice_1: 0,
    apprentice_2: 0,
    apprentice_3: 0,
    apprentice_4: 0,
    guru_1: 0,
    guru_2: 0,
    master: 0,
    enlightened: 0,
    burned: 0
  };

  Object.values(schema.kanji).forEach(kanji => {
    const stage = kanji && kanji.srs ? kanji.srs.stage : 'locked';
    if (distribution.hasOwnProperty(stage)) {
      distribution[stage]++;
    }
  });

  schema.stats.stage_distribution = distribution;
}

/**
 * Increment session count for today
 *
 * @param {Object} schema - Schema to update
 */
function incrementSessionCount(schema) {
  const today = new Date().toISOString().split('T')[0];

  if (!schema.stats.today || schema.stats.today.date !== today) {
    schema.stats.today = {
      date: today,
      new_cards_introduced: 0,
      reviews_completed: 0,
      correct_count: 0,
      session_count: 1
    };
  } else {
    schema.stats.today.session_count++;
  }
}

// ============================================================================
// QUEUE STATUS FUNCTIONS
// ============================================================================

/**
 * Get current queue status (counts of due and new cards)
 *
 * @param {Object} schema - Full schema
 * @param {Object} [filters={}] - Filter options
 * @returns {Object} Queue status
 */
function getQueueStatus(schema, filters = {}) {
  if (!schema || !schema.kanji) {
    return {
      due_count: 0,
      new_available: 0,
      new_limit: SESSION_DEFAULTS.NEW_CARDS_PER_DAY,
      new_introduced_today: 0,
      new_remaining: SESSION_DEFAULTS.NEW_CARDS_PER_DAY,
      total_available: 0
    };
  }

  const dueCards = getDueCards(schema, filters);
  const newCards = getNewCards(schema, undefined, filters);

  const newLimit = schema.settings && schema.settings.new_cards_per_day
    ? schema.settings.new_cards_per_day
    : SESSION_DEFAULTS.NEW_CARDS_PER_DAY;

  const today = new Date().toISOString().split('T')[0];
  const newIntroducedToday = (schema.stats.today && schema.stats.today.date === today)
    ? schema.stats.today.new_cards_introduced
    : 0;

  return {
    due_count: dueCards.length,
    new_available: newCards.length,
    new_limit: newLimit,
    new_introduced_today: newIntroducedToday,
    new_remaining: Math.max(0, newLimit - newIntroducedToday),
    total_available: dueCards.length + newCards.length
  };
}

/**
 * Get upcoming reviews (reviews due in the next N hours)
 *
 * @param {Object} schema - Full schema
 * @param {number} [hours=24] - Hours to look ahead
 * @returns {Array} Kanji due within the specified time
 */
function getUpcomingReviews(schema, hours = 24) {
  if (!schema || !schema.kanji) {
    return [];
  }

  const now = new Date();
  const cutoff = new Date(now.getTime() + hours * 60 * 60 * 1000);

  return Object.values(schema.kanji).filter(kanji => {
    if (!kanji.srs || kanji.srs.stage === 'locked' || kanji.srs.stage === 'burned') {
      return false;
    }

    if (!kanji.srs.next_review_date) {
      return true; // New cards are "upcoming"
    }

    const reviewDate = new Date(kanji.srs.next_review_date);
    return reviewDate > now && reviewDate <= cutoff;
  }).sort((a, b) => {
    const dateA = a.srs.next_review_date ? new Date(a.srs.next_review_date) : new Date();
    const dateB = b.srs.next_review_date ? new Date(b.srs.next_review_date) : new Date();
    return dateA - dateB;
  });
}

/**
 * Get review forecast for the next N days
 *
 * @param {Object} schema - Full schema
 * @param {number} [days=7] - Days to forecast
 * @returns {Array} Array of {date, count} objects
 */
function getReviewForecast(schema, days = 7) {
  if (!schema || !schema.kanji) {
    return [];
  }

  const forecast = [];
  const now = new Date();

  for (let i = 0; i < days; i++) {
    const dayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate() + i);
    const dayEnd = new Date(dayStart.getTime() + 24 * 60 * 60 * 1000);

    const count = Object.values(schema.kanji).filter(kanji => {
      if (!kanji.srs || kanji.srs.stage === 'locked' || kanji.srs.stage === 'burned') {
        return false;
      }

      if (!kanji.srs.next_review_date) {
        return i === 0; // New cards count for today
      }

      const reviewDate = new Date(kanji.srs.next_review_date);
      return reviewDate >= dayStart && reviewDate < dayEnd;
    }).length;

    forecast.push({
      date: dayStart.toISOString().split('T')[0],
      count
    });
  }

  return forecast;
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Shuffle an array using Fisher-Yates algorithm
 *
 * @param {Array} array - Array to shuffle
 * @returns {Array} Shuffled array (new array, original unchanged)
 */
function shuffleArray(array) {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}

/**
 * Get the next card in a session
 *
 * @param {Object} session - Session object
 * @returns {Object|null} Next kanji or null if session complete
 */
function getNextCard(session) {
  if (!session || session.current_index >= session.cards.length) {
    return null;
  }
  return session.cards[session.current_index];
}

/**
 * Advance to the next card in a session
 *
 * @param {Object} session - Session object (will be mutated)
 * @param {boolean} wasCorrect - Whether the response was correct
 * @returns {Object} Updated session
 */
function advanceSession(session, wasCorrect) {
  session.current_index++;
  session.completed_count++;
  if (wasCorrect) {
    session.correct_count++;
  }
  return session;
}

/**
 * Check if a session is complete
 *
 * @param {Object} session - Session object
 * @returns {boolean} True if all cards reviewed
 */
function isSessionComplete(session) {
  return !session || session.current_index >= session.cards.length;
}

/**
 * Get session progress
 *
 * @param {Object} session - Session object
 * @returns {Object} Progress info
 */
function getSessionProgress(session) {
  if (!session) {
    return {
      current: 0,
      total: 0,
      completed: 0,
      remaining: 0,
      correct: 0,
      accuracy: 0,
      is_complete: true
    };
  }

  const total = session.cards.length;
  const completed = session.completed_count;
  const remaining = total - completed;
  const accuracy = completed > 0 ? Math.round((session.correct_count / completed) * 100) : 0;

  return {
    current: session.current_index + 1,
    total,
    completed,
    remaining,
    correct: session.correct_count,
    accuracy,
    is_complete: session.current_index >= total
  };
}

// ============================================================================
// EXPORTS (Browser Global)
// ============================================================================

// Make functions available globally for browser use
if (typeof window !== 'undefined') {
  window.SessionManager = {
    // Queue building
    getDueCards,
    getNewCards,
    createSession,

    // Session processing
    processSessionReview,
    introduceNewCard,

    // Stats updates
    updateTodayStats,
    updateStreak,
    updateStageDistribution,
    incrementSessionCount,

    // Queue status
    getQueueStatus,
    getUpcomingReviews,
    getReviewForecast,

    // Session utilities
    getNextCard,
    advanceSession,
    isSessionComplete,
    getSessionProgress,
    shuffleArray,

    // Constants
    SESSION_DEFAULTS
  };
}
