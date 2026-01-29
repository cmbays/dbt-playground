/**
 * Mastery Calculator Module - JLPT and Topic Mastery Aggregation
 *
 * Version: 1.0.0
 * Task: T1.6/T1.7 - Implement mastery percentage calculations
 * Related: PRD-001, TDD-001 §5, §6.3
 *
 * Responsibilities:
 * - Calculate JLPT level mastery percentages (N5, N4, N3, N2, N1)
 * - Calculate topic mastery percentages
 * - Calculate overall mastery across all kanji
 * - Provide stage distribution statistics
 *
 * Dependencies:
 * - srs-engine.js (getStageMasteryScore)
 *
 * Mastery Formula (TDD §5.1):
 * Mastery % = (sum of kanji mastery scores) / (total kanji × 100) × 100
 */

// ============================================================================
// CONSTANTS
// ============================================================================

/**
 * Mastery scores for each stage (from TDD §4.1)
 * Used when srs-engine.js is not loaded
 */
const STAGE_MASTERY_SCORES = {
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

/**
 * Valid JLPT levels
 */
const JLPT_LEVELS = Object.freeze(['N5', 'N4', 'N3', 'N2', 'N1']);

/**
 * Valid topics (from project)
 */
const TOPICS = Object.freeze(['home-life', 'shopping', 'restaurant', 'travel']);

// ============================================================================
// CORE MASTERY CALCULATION FUNCTIONS
// ============================================================================

/**
 * Get the mastery score for a stage
 *
 * Uses srs-engine.js if available, otherwise uses local constant.
 *
 * @param {string} stage - Mastery stage
 * @returns {number} Mastery score (0-100)
 */
function getStageMasteryScore(stage) {
  // Try to use srs-engine.js function if available
  if (typeof window !== 'undefined' && window.SRSEngine && window.SRSEngine.getStageMasteryScore) {
    return window.SRSEngine.getStageMasteryScore(stage);
  }
  return STAGE_MASTERY_SCORES[stage] || 0;
}

/**
 * Calculate JLPT level mastery percentage
 *
 * Filters kanji by JLPT level and calculates the aggregate mastery.
 *
 * Formula: Mastery % = (sum of stage scores) / (count × 100) × 100
 *
 * @param {Object.<string, KanjiProgress>} kanjiMap - All kanji progress objects keyed by character
 * @param {string} level - JLPT level (N5, N4, N3, N2, N1)
 * @returns {number} Mastery percentage (0-100), rounded to 1 decimal place
 */
function calculateJLPTMastery(kanjiMap, level) {
  if (!kanjiMap || typeof kanjiMap !== 'object') {
    return 0;
  }

  if (!JLPT_LEVELS.includes(level)) {
    console.warn(`Invalid JLPT level: ${level}`);
    return 0;
  }

  // Filter kanji by JLPT level
  const levelKanji = Object.values(kanjiMap).filter(
    kanji => kanji && kanji.jlpt_level === level
  );

  if (levelKanji.length === 0) {
    return 0;
  }

  // Sum mastery scores
  const totalScore = levelKanji.reduce((sum, kanji) => {
    const stage = kanji.srs ? kanji.srs.stage : 'locked';
    return sum + getStageMasteryScore(stage);
  }, 0);

  // Calculate percentage
  const maxScore = levelKanji.length * 100;
  const mastery = (totalScore / maxScore) * 100;

  // Round to 1 decimal place
  return Math.round(mastery * 10) / 10;
}

/**
 * Calculate topic mastery percentage
 *
 * Filters kanji that include the specified topic and calculates mastery.
 * Kanji can belong to multiple topics and will contribute to each.
 *
 * @param {Object.<string, KanjiProgress>} kanjiMap - All kanji progress objects
 * @param {string} topic - Topic name (home-life, shopping, restaurant, travel)
 * @returns {number} Mastery percentage (0-100), rounded to 1 decimal place
 */
function calculateTopicMastery(kanjiMap, topic) {
  if (!kanjiMap || typeof kanjiMap !== 'object') {
    return 0;
  }

  if (!TOPICS.includes(topic)) {
    console.warn(`Invalid topic: ${topic}`);
    return 0;
  }

  // Filter kanji that include this topic
  const topicKanji = Object.values(kanjiMap).filter(
    kanji => kanji && kanji.topics && kanji.topics.includes(topic)
  );

  if (topicKanji.length === 0) {
    return 0;
  }

  // Sum mastery scores
  const totalScore = topicKanji.reduce((sum, kanji) => {
    const stage = kanji.srs ? kanji.srs.stage : 'locked';
    return sum + getStageMasteryScore(stage);
  }, 0);

  // Calculate percentage
  const maxScore = topicKanji.length * 100;
  const mastery = (totalScore / maxScore) * 100;

  // Round to 1 decimal place
  return Math.round(mastery * 10) / 10;
}

/**
 * Calculate overall mastery across all kanji
 *
 * Aggregates all kanji regardless of level or topic.
 *
 * @param {Object.<string, KanjiProgress>} kanjiMap - All kanji progress objects
 * @returns {number} Overall mastery percentage (0-100), rounded to 1 decimal place
 */
function calculateOverallMastery(kanjiMap) {
  if (!kanjiMap || typeof kanjiMap !== 'object') {
    return 0;
  }

  const allKanji = Object.values(kanjiMap);

  if (allKanji.length === 0) {
    return 0;
  }

  // Sum mastery scores
  const totalScore = allKanji.reduce((sum, kanji) => {
    const stage = kanji && kanji.srs ? kanji.srs.stage : 'locked';
    return sum + getStageMasteryScore(stage);
  }, 0);

  // Calculate percentage
  const maxScore = allKanji.length * 100;
  const mastery = (totalScore / maxScore) * 100;

  // Round to 1 decimal place
  return Math.round(mastery * 10) / 10;
}

// ============================================================================
// AGGREGATION FUNCTIONS
// ============================================================================

/**
 * Calculate all JLPT masteries at once
 *
 * Returns an object with mastery for each JLPT level.
 *
 * @param {Object.<string, KanjiProgress>} kanjiMap - All kanji progress objects
 * @returns {Object} Object with N5, N4, N3, N2, N1 mastery percentages
 */
function calculateAllJLPTMasteries(kanjiMap) {
  return {
    N5: calculateJLPTMastery(kanjiMap, 'N5'),
    N4: calculateJLPTMastery(kanjiMap, 'N4'),
    N3: calculateJLPTMastery(kanjiMap, 'N3'),
    N2: calculateJLPTMastery(kanjiMap, 'N2'),
    N1: calculateJLPTMastery(kanjiMap, 'N1')
  };
}

/**
 * Calculate all topic masteries at once
 *
 * Returns an object with mastery for each topic.
 *
 * @param {Object.<string, KanjiProgress>} kanjiMap - All kanji progress objects
 * @returns {Object} Object with mastery for each topic
 */
function calculateAllTopicMasteries(kanjiMap) {
  const result = {};
  TOPICS.forEach(topic => {
    result[topic] = calculateTopicMastery(kanjiMap, topic);
  });
  return result;
}

/**
 * Get complete mastery summary
 *
 * Returns overall, all JLPT levels, and all topics in one call.
 *
 * @param {Object.<string, KanjiProgress>} kanjiMap - All kanji progress objects
 * @returns {Object} Complete mastery summary
 */
function getMasterySummary(kanjiMap) {
  return {
    overall: calculateOverallMastery(kanjiMap),
    jlpt: calculateAllJLPTMasteries(kanjiMap),
    topics: calculateAllTopicMasteries(kanjiMap),
    calculated_at: new Date().toISOString()
  };
}

// ============================================================================
// STATISTICS FUNCTIONS
// ============================================================================

/**
 * Calculate stage distribution
 *
 * Counts how many kanji are at each stage.
 *
 * @param {Object.<string, KanjiProgress>} kanjiMap - All kanji progress objects
 * @returns {Object} Object with count for each stage
 */
function calculateStageDistribution(kanjiMap) {
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

  if (!kanjiMap || typeof kanjiMap !== 'object') {
    return distribution;
  }

  Object.values(kanjiMap).forEach(kanji => {
    const stage = kanji && kanji.srs ? kanji.srs.stage : 'locked';
    if (distribution.hasOwnProperty(stage)) {
      distribution[stage]++;
    }
  });

  return distribution;
}

/**
 * Get JLPT level counts
 *
 * Counts how many kanji are at each JLPT level.
 *
 * @param {Object.<string, KanjiProgress>} kanjiMap - All kanji progress objects
 * @returns {Object} Object with count for each JLPT level
 */
function getJLPTLevelCounts(kanjiMap) {
  const counts = {
    N5: 0,
    N4: 0,
    N3: 0,
    N2: 0,
    N1: 0
  };

  if (!kanjiMap || typeof kanjiMap !== 'object') {
    return counts;
  }

  Object.values(kanjiMap).forEach(kanji => {
    if (kanji && kanji.jlpt_level && counts.hasOwnProperty(kanji.jlpt_level)) {
      counts[kanji.jlpt_level]++;
    }
  });

  return counts;
}

/**
 * Get topic counts
 *
 * Counts how many kanji are in each topic.
 * Note: Kanji can be in multiple topics.
 *
 * @param {Object.<string, KanjiProgress>} kanjiMap - All kanji progress objects
 * @returns {Object} Object with count for each topic
 */
function getTopicCounts(kanjiMap) {
  const counts = {};
  TOPICS.forEach(topic => counts[topic] = 0);

  if (!kanjiMap || typeof kanjiMap !== 'object') {
    return counts;
  }

  Object.values(kanjiMap).forEach(kanji => {
    if (kanji && kanji.topics && Array.isArray(kanji.topics)) {
      kanji.topics.forEach(topic => {
        if (counts.hasOwnProperty(topic)) {
          counts[topic]++;
        }
      });
    }
  });

  return counts;
}

/**
 * Get progress statistics
 *
 * Comprehensive statistics about learning progress.
 *
 * @param {Object.<string, KanjiProgress>} kanjiMap - All kanji progress objects
 * @returns {Object} Progress statistics
 */
function getProgressStats(kanjiMap) {
  if (!kanjiMap || typeof kanjiMap !== 'object') {
    return {
      total_kanji: 0,
      unlocked: 0,
      in_progress: 0,
      mastered: 0,
      burned: 0,
      locked: 0,
      unlock_percentage: 0,
      completion_percentage: 0
    };
  }

  const distribution = calculateStageDistribution(kanjiMap);
  const totalKanji = Object.values(kanjiMap).length;

  // Count categories
  const locked = distribution.locked;
  const unlocked = totalKanji - locked;
  const burned = distribution.burned;

  // In progress = unlocked but not burned
  const inProgress = unlocked - burned;

  // Mastered = guru_1 and above (including burned)
  const mastered = distribution.guru_1 +
    distribution.guru_2 +
    distribution.master +
    distribution.enlightened +
    distribution.burned;

  return {
    total_kanji: totalKanji,
    unlocked: unlocked,
    in_progress: inProgress,
    mastered: mastered,
    burned: burned,
    locked: locked,
    unlock_percentage: totalKanji > 0 ? Math.round((unlocked / totalKanji) * 1000) / 10 : 0,
    completion_percentage: totalKanji > 0 ? Math.round((burned / totalKanji) * 1000) / 10 : 0
  };
}

// ============================================================================
// FILTERING HELPERS
// ============================================================================

/**
 * Filter kanji by JLPT level
 *
 * @param {Object.<string, KanjiProgress>} kanjiMap - All kanji progress objects
 * @param {string} level - JLPT level (N5, N4, N3, N2, N1) or "All"
 * @returns {Object.<string, KanjiProgress>} Filtered kanji map
 */
function filterByJLPTLevel(kanjiMap, level) {
  if (!kanjiMap || typeof kanjiMap !== 'object') {
    return {};
  }

  if (level === 'All') {
    return kanjiMap;
  }

  const filtered = {};
  Object.entries(kanjiMap).forEach(([char, kanji]) => {
    if (kanji && kanji.jlpt_level === level) {
      filtered[char] = kanji;
    }
  });

  return filtered;
}

/**
 * Filter kanji by topic
 *
 * @param {Object.<string, KanjiProgress>} kanjiMap - All kanji progress objects
 * @param {string} topic - Topic name or "All"
 * @returns {Object.<string, KanjiProgress>} Filtered kanji map
 */
function filterByTopic(kanjiMap, topic) {
  if (!kanjiMap || typeof kanjiMap !== 'object') {
    return {};
  }

  if (topic === 'All') {
    return kanjiMap;
  }

  const filtered = {};
  Object.entries(kanjiMap).forEach(([char, kanji]) => {
    if (kanji && kanji.topics && kanji.topics.includes(topic)) {
      filtered[char] = kanji;
    }
  });

  return filtered;
}

/**
 * Filter kanji by stage
 *
 * @param {Object.<string, KanjiProgress>} kanjiMap - All kanji progress objects
 * @param {string} stage - Stage name or "All"
 * @returns {Object.<string, KanjiProgress>} Filtered kanji map
 */
function filterByStage(kanjiMap, stage) {
  if (!kanjiMap || typeof kanjiMap !== 'object') {
    return {};
  }

  if (stage === 'All') {
    return kanjiMap;
  }

  const filtered = {};
  Object.entries(kanjiMap).forEach(([char, kanji]) => {
    const kanjiStage = kanji && kanji.srs ? kanji.srs.stage : 'locked';
    if (kanjiStage === stage) {
      filtered[char] = kanji;
    }
  });

  return filtered;
}

/**
 * Apply multiple filters
 *
 * @param {Object.<string, KanjiProgress>} kanjiMap - All kanji progress objects
 * @param {Object} filters - Filter options
 * @param {string} [filters.jlpt_level] - JLPT level filter
 * @param {string} [filters.topic] - Topic filter
 * @param {string} [filters.stage] - Stage filter
 * @returns {Object.<string, KanjiProgress>} Filtered kanji map
 */
function applyFilters(kanjiMap, filters = {}) {
  let result = kanjiMap;

  if (filters.jlpt_level && filters.jlpt_level !== 'All') {
    result = filterByJLPTLevel(result, filters.jlpt_level);
  }

  if (filters.topic && filters.topic !== 'All') {
    result = filterByTopic(result, filters.topic);
  }

  if (filters.stage && filters.stage !== 'All') {
    result = filterByStage(result, filters.stage);
  }

  return result;
}

// ============================================================================
// CACHE MANAGEMENT
// ============================================================================

/**
 * Create a mastery cache object for storage in schema
 *
 * @param {Object.<string, KanjiProgress>} kanjiMap - All kanji progress objects
 * @returns {Object} Cache object with JLPT masteries and timestamp
 */
function createMasteryCache(kanjiMap) {
  return {
    N5: calculateJLPTMastery(kanjiMap, 'N5'),
    N4: calculateJLPTMastery(kanjiMap, 'N4'),
    N3: calculateJLPTMastery(kanjiMap, 'N3'),
    N2: calculateJLPTMastery(kanjiMap, 'N2'),
    N1: calculateJLPTMastery(kanjiMap, 'N1'),
    calculated_at: new Date().toISOString()
  };
}

/**
 * Check if cache is still valid
 *
 * Cache is invalid if:
 * - Older than 1 hour
 * - Schema was modified after cache creation
 *
 * @param {Object} cache - Cache object from schema.stats.jlpt_mastery_cache
 * @param {string} lastModified - ISO timestamp of last schema modification
 * @returns {boolean} True if cache is valid
 */
function isCacheValid(cache, lastModified) {
  if (!cache || !cache.calculated_at) {
    return false;
  }

  const cacheTime = new Date(cache.calculated_at).getTime();
  const modifiedTime = new Date(lastModified).getTime();

  // Cache invalid if schema modified after cache creation
  if (modifiedTime > cacheTime) {
    return false;
  }

  // Cache invalid if older than 1 hour
  const ONE_HOUR_MS = 60 * 60 * 1000;
  const now = Date.now();
  if (now - cacheTime > ONE_HOUR_MS) {
    return false;
  }

  return true;
}

/**
 * Get cached or calculate JLPT masteries
 *
 * Uses cache if valid, otherwise recalculates.
 *
 * @param {Object} schema - Full schema with stats.jlpt_mastery_cache and metadata.last_modified
 * @returns {Object} JLPT mastery cache object
 */
function getCachedOrCalculateJLPTMasteries(schema) {
  const cache = schema.stats && schema.stats.jlpt_mastery_cache;
  const lastModified = schema.metadata && schema.metadata.last_modified;

  if (isCacheValid(cache, lastModified)) {
    return cache;
  }

  // Recalculate and return fresh cache
  return createMasteryCache(schema.kanji);
}

// ============================================================================
// EXPORTS (Browser Global)
// ============================================================================

// Make functions available globally for browser use
if (typeof window !== 'undefined') {
  window.MasteryCalculator = {
    // Core calculation functions
    calculateJLPTMastery,
    calculateTopicMastery,
    calculateOverallMastery,

    // Aggregation functions
    calculateAllJLPTMasteries,
    calculateAllTopicMasteries,
    getMasterySummary,

    // Statistics functions
    calculateStageDistribution,
    getJLPTLevelCounts,
    getTopicCounts,
    getProgressStats,

    // Filtering helpers
    filterByJLPTLevel,
    filterByTopic,
    filterByStage,
    applyFilters,

    // Cache management
    createMasteryCache,
    isCacheValid,
    getCachedOrCalculateJLPTMasteries,

    // Constants
    STAGE_MASTERY_SCORES,
    JLPT_LEVELS,
    TOPICS
  };
}
