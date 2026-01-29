/**
 * Storage Module - localStorage CRUD and Validation
 *
 * Version: 1.1.0
 * Task: T2.1 - Schema migration v1.0.0 → v1.1.0
 * Related: PRD-001, PRD-003, TDD-001 §6.1, TDD-003 §2
 *
 * Responsibilities:
 * - Load and save kanji progress schema from/to localStorage
 * - Validate schema structure and data integrity
 * - Provide CRUD operations on kanji progress objects
 * - Handle localStorage quota exceeded gracefully
 * - Support schema versioning and migrations
 *
 * Storage Key: 'jss_kanji_data' (Japanese Study Site)
 * Schema Version: 1.1.0 (semver format)
 *
 * v1.1.0 Changes:
 * - Added stats.xp (XP and level system)
 * - Added stats.streak (streak system with freezes)
 * - Added stats.daily_history (for heatmap)
 * - Added stats.at_risk_kanji (recently dropped kanji)
 * - Added stats.mastery_snapshots (for trend line)
 * - Added settings.daily_goal (daily goal system)
 * - Added stats.today.xp_earned and stats.today.goal_completed
 */

// ============================================================================
// CONSTANTS
// ============================================================================

const STORAGE_KEY = 'jss_kanji_data';
const SCHEMA_VERSION = '1.1.0';

// Mastery stages enum (matches srs-engine.js and TDD §4.1)
const STAGES = {
  LOCKED: 'locked',
  LESSON: 'lesson',
  APPRENTICE_1: 'apprentice_1',
  APPRENTICE_2: 'apprentice_2',
  APPRENTICE_3: 'apprentice_3',
  APPRENTICE_4: 'apprentice_4',
  GURU_1: 'guru_1',
  GURU_2: 'guru_2',
  MASTER: 'master',
  ENLIGHTENED: 'enlightened',
  BURNED: 'burned'
};

const VALID_STAGES = Object.freeze(Object.values(STAGES));
const VALID_JLPT_LEVELS = Object.freeze(['N5', 'N4', 'N3', 'N2', 'N1']);
const VALID_TOPICS = Object.freeze(['home-life', 'shopping', 'restaurant', 'travel']);

// Limits and constraints
const LIMITS = {
  MAX_HISTORY_ENTRIES: 50,
  MIN_EASE_FACTOR: 1.3,
  MAX_EASE_FACTOR: 5.0,
  NEW_CARDS_PER_DAY_MIN: 1,
  NEW_CARDS_PER_DAY_MAX: 50,
  NEW_CARDS_PER_DAY_DEFAULT: 10,
  // v1.1.0 additions
  DAILY_GOAL_MIN: 1,
  DAILY_GOAL_MAX: 100,
  DAILY_GOAL_DEFAULT: 10,
  MAX_STREAK_FREEZES: 2,
  MAX_LEVEL: 60,
  MAX_AT_RISK_KANJI: 50,
  MAX_MASTERY_SNAPSHOTS: 52,  // 1 year of weekly snapshots
  MAX_DAILY_HISTORY_DAYS: 400
};

// ============================================================================
// SCHEMA INITIALIZATION
// ============================================================================

/**
 * Create a default schema for a new user
 *
 * @returns {Object} Default schema object with empty kanji map
 */
function createDefaultSchema() {
  const now = new Date();
  const todayStr = now.toISOString().split('T')[0];

  return {
    version: SCHEMA_VERSION,
    kanji: {},  // Will be populated with kanji-metadata.js
    settings: {
      new_cards_per_day: LIMITS.NEW_CARDS_PER_DAY_DEFAULT,
      default_jlpt_filter: 'All',
      default_topic_filter: 'All',
      show_romaji: false,
      show_furigana: true,
      auto_play_audio: false,
      preferred_reading_type: 'meaning',
      // v1.1.0: Daily goal settings
      daily_goal: {
        enabled: true,
        target_cards: LIMITS.DAILY_GOAL_DEFAULT,
        notify_enabled: false,
        notify_time: '19:00'
      }
    },
    stats: {
      total_reviews: 0,
      total_kanji_seen: 0,
      // Legacy streak fields (deprecated, use stats.streak instead)
      streak_days: 0,
      last_study_date: null,
      streak_start_date: null,
      today: {
        date: todayStr,
        new_cards_introduced: 0,
        reviews_completed: 0,
        correct_count: 0,
        session_count: 0,
        // v1.1.0 additions
        xp_earned: 0,
        goal_completed: false
      },
      stage_distribution: {
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
      },
      jlpt_mastery_cache: {
        N5: 0,
        N4: 0,
        N3: 0,
        N2: 0,
        N1: 0,
        calculated_at: now.toISOString()
      },
      // v1.1.0: XP & Level System
      xp: {
        total: 0,
        current_level: 1,
        xp_this_level: 0,
        xp_to_next_level: 100,
        last_level_up: null
      },
      // v1.1.0: Streak System
      streak: {
        current: 0,
        longest: 0,
        last_study_date: null,
        freezes_available: 0,
        freeze_used_date: null,
        freezes_earned_at: 0
      },
      // v1.1.0: Daily History (for heatmap)
      daily_history: {},
      // v1.1.0: At-Risk Kanji (recently dropped stages)
      at_risk_kanji: [],
      // v1.1.0: Mastery Snapshots (for trend line)
      mastery_snapshots: []
    },
    metadata: {
      created: now.toISOString(),
      last_modified: now.toISOString(),
      migration_count: 0,
      last_export: null,
      client_id: generateClientId()
    }
  };
}

/**
 * Generate a unique client ID for future sync capabilities
 *
 * @returns {string} UUID v4 format string
 */
function generateClientId() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

// ============================================================================
// SCHEMA MIGRATION (v1.0.0 → v1.1.0)
// ============================================================================

/**
 * Compare two semver version strings
 *
 * @param {string} a - First version (e.g., "1.0.0")
 * @param {string} b - Second version (e.g., "1.1.0")
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

/**
 * Get current date string in YYYY-MM-DD format (local time)
 *
 * @param {Date} date - Date object (defaults to now)
 * @returns {string} Date string in YYYY-MM-DD format
 */
function getLocalDateString(date = new Date()) {
  return date.toLocaleDateString('en-CA'); // Returns YYYY-MM-DD
}

/**
 * Migrate schema from v1.0.0 to v1.1.0
 *
 * Adds engagement system fields: XP, levels, streaks, goals, daily history.
 * This migration is backward-compatible (additive only).
 *
 * @param {Object} schema - v1.0.0 schema
 * @returns {Object} v1.1.0 schema
 */
function migrateToV1_1_0(schema) {
  // Already v1.1.0+, no migration needed
  if (compareVersions(schema.version, '1.1.0') >= 0) {
    return schema;
  }

  console.log(`Migrating schema from v${schema.version} to v1.1.0...`);

  // Add daily_goal to settings
  if (!schema.settings.daily_goal) {
    schema.settings.daily_goal = {
      enabled: true,
      target_cards: LIMITS.DAILY_GOAL_DEFAULT,
      notify_enabled: false,
      notify_time: '19:00'
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
      const todayData = schema.stats.today;
      if (todayData.reviews_completed > 0) {
        schema.stats.daily_history[todayData.date] = {
          reviews: todayData.reviews_completed,
          correct: todayData.correct_count,
          xp_earned: 0  // Can't reconstruct historical XP
        };
      }
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

  console.log('Migration to v1.1.0 complete.');
  return schema;
}

/**
 * Run all necessary migrations on a schema
 *
 * @param {Object} schema - Schema at any version
 * @returns {Object} Schema migrated to current version
 */
function runMigrations(schema) {
  // Run migrations in order
  if (compareVersions(schema.version, '1.1.0') < 0) {
    schema = migrateToV1_1_0(schema);
  }

  // Future migrations would go here:
  // if (compareVersions(schema.version, '1.2.0') < 0) {
  //   schema = migrateToV1_2_0(schema);
  // }

  return schema;
}

// ============================================================================
// VALIDATION FUNCTIONS
// ============================================================================

/**
 * Validate a kanji character is a single CJK character
 *
 * @param {string} character - Character to validate
 * @returns {boolean} True if valid kanji character
 */
function isValidKanjiCharacter(character) {
  if (typeof character !== 'string' || character.length !== 1) {
    return false;
  }
  // CJK Unified Ideographs range: U+4E00 to U+9FFF
  const code = character.charCodeAt(0);
  return code >= 0x4E00 && code <= 0x9FFF;
}

/**
 * Validate a mastery stage value
 *
 * @param {string} stage - Stage to validate
 * @returns {boolean} True if valid stage
 */
function isValidStage(stage) {
  return VALID_STAGES.includes(stage);
}

/**
 * Validate a JLPT level
 *
 * @param {string} level - Level to validate
 * @returns {boolean} True if valid JLPT level
 */
function isValidJLPTLevel(level) {
  return VALID_JLPT_LEVELS.includes(level);
}

/**
 * Validate an ease factor value
 *
 * @param {number} easeFactor - Ease factor to validate
 * @returns {boolean} True if in valid range [1.3, 5.0]
 */
function isValidEaseFactor(easeFactor) {
  return typeof easeFactor === 'number' &&
         easeFactor >= LIMITS.MIN_EASE_FACTOR &&
         easeFactor <= LIMITS.MAX_EASE_FACTOR;
}

/**
 * Validate an ISO 8601 timestamp
 *
 * @param {string|null} timestamp - Timestamp to validate
 * @returns {boolean} True if null or valid ISO 8601
 */
function isValidTimestamp(timestamp) {
  if (timestamp === null) {
    return true;
  }
  if (typeof timestamp !== 'string') {
    return false;
  }
  // Basic ISO 8601 validation
  const date = new Date(timestamp);
  return !isNaN(date.getTime()) && date.toISOString() === timestamp;
}

/**
 * Validate a semver version string
 *
 * @param {string} version - Version string
 * @returns {boolean} True if valid semver format
 */
function isValidVersion(version) {
  return /^\d+\.\d+\.\d+$/.test(version);
}

/**
 * Validate an SRS state object
 *
 * @param {Object} srs - SRS state to validate
 * @returns {Object} Validation result {valid: boolean, errors: string[]}
 */
function validateSRSState(srs) {
  const errors = [];

  if (!isValidStage(srs.stage)) {
    errors.push(`Invalid stage: ${srs.stage}`);
  }
  if (typeof srs.interval_days !== 'number' || srs.interval_days < 0) {
    errors.push(`Invalid interval_days: ${srs.interval_days}`);
  }
  if (!isValidEaseFactor(srs.ease_factor)) {
    errors.push(`Invalid ease_factor: ${srs.ease_factor}`);
  }
  if (!Number.isInteger(srs.repetitions) || srs.repetitions < 0) {
    errors.push(`Invalid repetitions: ${srs.repetitions}`);
  }
  if (!isValidTimestamp(srs.last_reviewed)) {
    errors.push(`Invalid last_reviewed: ${srs.last_reviewed}`);
  }
  if (!isValidTimestamp(srs.next_review_date)) {
    errors.push(`Invalid next_review_date: ${srs.next_review_date}`);
  }
  if (!Number.isInteger(srs.total_reviews) || srs.total_reviews < 0) {
    errors.push(`Invalid total_reviews: ${srs.total_reviews}`);
  }
  if (!Number.isInteger(srs.correct_count) || srs.correct_count < 0) {
    errors.push(`Invalid correct_count: ${srs.correct_count}`);
  }
  if (typeof srs.is_new !== 'boolean') {
    errors.push(`Invalid is_new: ${srs.is_new}`);
  }
  if (!isValidTimestamp(srs.introduced_at)) {
    errors.push(`Invalid introduced_at: ${srs.introduced_at}`);
  }

  return {
    valid: errors.length === 0,
    errors
  };
}

/**
 * Validate a history entry
 *
 * @param {Object} entry - History entry to validate
 * @returns {Object} Validation result {valid: boolean, errors: string[]}
 */
function validateHistoryEntry(entry) {
  const errors = [];

  if (!isValidTimestamp(entry.timestamp)) {
    errors.push(`Invalid history timestamp`);
  }
  if (![0, 2, 4, 5].includes(entry.quality)) {
    errors.push(`Invalid history quality: ${entry.quality}`);
  }
  if (!isValidStage(entry.stage_before)) {
    errors.push(`Invalid history stage_before: ${entry.stage_before}`);
  }
  if (!isValidStage(entry.stage_after)) {
    errors.push(`Invalid history stage_after: ${entry.stage_after}`);
  }
  if (entry.response_time_ms !== undefined &&
      (typeof entry.response_time_ms !== 'number' || entry.response_time_ms < 0)) {
    errors.push(`Invalid response_time_ms: ${entry.response_time_ms}`);
  }

  return {
    valid: errors.length === 0,
    errors
  };
}

/**
 * Validate a kanji progress object
 *
 * @param {Object} progress - Progress object to validate
 * @param {string} expectedCharacter - Expected character (for key mismatch check)
 * @returns {Object} Validation result {valid: boolean, errors: string[]}
 */
function validateKanjiProgress(progress, expectedCharacter) {
  const errors = [];

  // Check character field
  if (!isValidKanjiCharacter(progress.character)) {
    errors.push(`Invalid character: ${progress.character}`);
  }

  // Check key/character match (critical for data integrity)
  if (progress.character !== expectedCharacter) {
    errors.push(`Character mismatch: key=${expectedCharacter}, character=${progress.character}`);
  }

  // Check JLPT level
  if (!isValidJLPTLevel(progress.jlpt_level)) {
    errors.push(`Invalid jlpt_level: ${progress.jlpt_level}`);
  }

  // Check topics array
  if (!Array.isArray(progress.topics) || progress.topics.length === 0) {
    errors.push(`Invalid topics: must be non-empty array`);
  } else {
    progress.topics.forEach(topic => {
      if (!VALID_TOPICS.includes(topic)) {
        errors.push(`Invalid topic: ${topic}`);
      }
    });
  }

  // Validate SRS state
  const srsValidation = validateSRSState(progress.srs);
  if (!srsValidation.valid) {
    errors.push(...srsValidation.errors);
  }

  // Validate history array
  if (!Array.isArray(progress.history)) {
    errors.push(`Invalid history: must be array`);
  } else if (progress.history.length > LIMITS.MAX_HISTORY_ENTRIES) {
    errors.push(`History overflow: ${progress.history.length} > ${LIMITS.MAX_HISTORY_ENTRIES}`);
  } else {
    progress.history.forEach((entry, index) => {
      const entryValidation = validateHistoryEntry(entry);
      if (!entryValidation.valid) {
        errors.push(`History[${index}]: ${entryValidation.errors.join(', ')}`);
      }
    });
  }

  return {
    valid: errors.length === 0,
    errors
  };
}

/**
 * Validate a date string in YYYY-MM-DD format
 *
 * @param {string|null} dateStr - Date string to validate
 * @returns {boolean} True if null or valid YYYY-MM-DD format
 */
function isValidDateString(dateStr) {
  if (dateStr === null) return true;
  if (typeof dateStr !== 'string') return false;
  return /^\d{4}-\d{2}-\d{2}$/.test(dateStr);
}

/**
 * Validate a time string in HH:MM format
 *
 * @param {string} timeStr - Time string to validate
 * @returns {boolean} True if valid HH:MM format
 */
function isValidTimeString(timeStr) {
  if (typeof timeStr !== 'string') return false;
  return /^([01]\d|2[0-3]):[0-5]\d$/.test(timeStr);
}

/**
 * Validate v1.1.0 daily_goal settings
 *
 * @param {Object} goal - daily_goal settings object
 * @returns {Object} Validation result {valid: boolean, errors: string[]}
 */
function validateDailyGoal(goal) {
  const errors = [];

  if (!goal || typeof goal !== 'object') {
    errors.push('daily_goal must be an object');
    return { valid: false, errors };
  }

  if (typeof goal.enabled !== 'boolean') {
    errors.push('daily_goal.enabled must be boolean');
  }

  if (typeof goal.target_cards !== 'number' ||
      goal.target_cards < LIMITS.DAILY_GOAL_MIN ||
      goal.target_cards > LIMITS.DAILY_GOAL_MAX) {
    errors.push(`daily_goal.target_cards must be ${LIMITS.DAILY_GOAL_MIN}-${LIMITS.DAILY_GOAL_MAX}`);
  }

  if (typeof goal.notify_enabled !== 'boolean') {
    errors.push('daily_goal.notify_enabled must be boolean');
  }

  if (!isValidTimeString(goal.notify_time)) {
    errors.push('daily_goal.notify_time must be HH:MM format');
  }

  return { valid: errors.length === 0, errors };
}

/**
 * Validate v1.1.0 XP stats
 *
 * @param {Object} xp - XP stats object
 * @returns {Object} Validation result {valid: boolean, errors: string[]}
 */
function validateXPStats(xp) {
  const errors = [];

  if (!xp || typeof xp !== 'object') {
    errors.push('stats.xp must be an object');
    return { valid: false, errors };
  }

  if (!Number.isInteger(xp.total) || xp.total < 0) {
    errors.push('stats.xp.total must be non-negative integer');
  }

  if (!Number.isInteger(xp.current_level) ||
      xp.current_level < 1 ||
      xp.current_level > LIMITS.MAX_LEVEL) {
    errors.push(`stats.xp.current_level must be 1-${LIMITS.MAX_LEVEL}`);
  }

  if (!Number.isInteger(xp.xp_this_level) || xp.xp_this_level < 0) {
    errors.push('stats.xp.xp_this_level must be non-negative integer');
  }

  if (!Number.isInteger(xp.xp_to_next_level) || xp.xp_to_next_level < 0) {
    errors.push('stats.xp.xp_to_next_level must be non-negative integer');
  }

  if (!isValidTimestamp(xp.last_level_up)) {
    errors.push('stats.xp.last_level_up must be valid timestamp or null');
  }

  return { valid: errors.length === 0, errors };
}

/**
 * Validate v1.1.0 streak stats
 *
 * @param {Object} streak - Streak stats object
 * @returns {Object} Validation result {valid: boolean, errors: string[]}
 */
function validateStreakStats(streak) {
  const errors = [];

  if (!streak || typeof streak !== 'object') {
    errors.push('stats.streak must be an object');
    return { valid: false, errors };
  }

  if (!Number.isInteger(streak.current) || streak.current < 0) {
    errors.push('stats.streak.current must be non-negative integer');
  }

  if (!Number.isInteger(streak.longest) || streak.longest < 0) {
    errors.push('stats.streak.longest must be non-negative integer');
  }

  if (!isValidDateString(streak.last_study_date)) {
    errors.push('stats.streak.last_study_date must be YYYY-MM-DD or null');
  }

  if (!Number.isInteger(streak.freezes_available) ||
      streak.freezes_available < 0 ||
      streak.freezes_available > LIMITS.MAX_STREAK_FREEZES) {
    errors.push(`stats.streak.freezes_available must be 0-${LIMITS.MAX_STREAK_FREEZES}`);
  }

  if (!isValidDateString(streak.freeze_used_date)) {
    errors.push('stats.streak.freeze_used_date must be YYYY-MM-DD or null');
  }

  if (!Number.isInteger(streak.freezes_earned_at) || streak.freezes_earned_at < 0) {
    errors.push('stats.streak.freezes_earned_at must be non-negative integer');
  }

  return { valid: errors.length === 0, errors };
}

/**
 * Validate entire schema object (comprehensive validation)
 *
 * @param {Object} schema - Schema to validate
 * @returns {Object} Validation result {valid: boolean, errors: string[]}
 */
function validateSchema(schema) {
  const errors = [];

  // Check root structure
  if (!schema || typeof schema !== 'object') {
    return { valid: false, errors: ['Schema must be an object'] };
  }

  // Check version
  if (!isValidVersion(schema.version)) {
    errors.push(`Invalid version: ${schema.version}`);
  }

  // Check kanji object
  if (typeof schema.kanji !== 'object' || schema.kanji === null) {
    errors.push(`kanji must be an object`);
  } else {
    // Validate each kanji entry
    for (const [character, progress] of Object.entries(schema.kanji)) {
      const validation = validateKanjiProgress(progress, character);
      if (!validation.valid) {
        errors.push(`Kanji[${character}]: ${validation.errors.join(', ')}`);
      }
    }
  }

  // Check settings
  if (typeof schema.settings !== 'object') {
    errors.push(`settings must be an object`);
  } else {
    const { new_cards_per_day } = schema.settings;
    if (typeof new_cards_per_day !== 'number' ||
        new_cards_per_day < LIMITS.NEW_CARDS_PER_DAY_MIN ||
        new_cards_per_day > LIMITS.NEW_CARDS_PER_DAY_MAX) {
      errors.push(`Invalid new_cards_per_day: ${new_cards_per_day}`);
    }

    // v1.1.0: Validate daily_goal if present
    if (schema.settings.daily_goal) {
      const goalValidation = validateDailyGoal(schema.settings.daily_goal);
      if (!goalValidation.valid) {
        errors.push(...goalValidation.errors);
      }
    }
  }

  // Check stats
  if (typeof schema.stats !== 'object') {
    errors.push(`stats must be an object`);
  } else {
    // v1.1.0: Validate XP stats if present
    if (schema.stats.xp) {
      const xpValidation = validateXPStats(schema.stats.xp);
      if (!xpValidation.valid) {
        errors.push(...xpValidation.errors);
      }
    }

    // v1.1.0: Validate streak stats if present
    if (schema.stats.streak) {
      const streakValidation = validateStreakStats(schema.stats.streak);
      if (!streakValidation.valid) {
        errors.push(...streakValidation.errors);
      }
    }

    // v1.1.0: Validate daily_history if present
    if (schema.stats.daily_history && typeof schema.stats.daily_history === 'object') {
      const historyKeys = Object.keys(schema.stats.daily_history);
      if (historyKeys.length > LIMITS.MAX_DAILY_HISTORY_DAYS) {
        errors.push(`daily_history exceeds ${LIMITS.MAX_DAILY_HISTORY_DAYS} entries`);
      }
      for (const dateKey of historyKeys) {
        if (!isValidDateString(dateKey)) {
          errors.push(`Invalid daily_history key: ${dateKey}`);
        }
      }
    }

    // v1.1.0: Validate at_risk_kanji if present
    if (schema.stats.at_risk_kanji) {
      if (!Array.isArray(schema.stats.at_risk_kanji)) {
        errors.push('at_risk_kanji must be an array');
      } else if (schema.stats.at_risk_kanji.length > LIMITS.MAX_AT_RISK_KANJI) {
        errors.push(`at_risk_kanji exceeds ${LIMITS.MAX_AT_RISK_KANJI} entries`);
      }
    }

    // v1.1.0: Validate mastery_snapshots if present
    if (schema.stats.mastery_snapshots) {
      if (!Array.isArray(schema.stats.mastery_snapshots)) {
        errors.push('mastery_snapshots must be an array');
      } else if (schema.stats.mastery_snapshots.length > LIMITS.MAX_MASTERY_SNAPSHOTS) {
        errors.push(`mastery_snapshots exceeds ${LIMITS.MAX_MASTERY_SNAPSHOTS} entries`);
      }
    }
  }

  // Check metadata
  if (typeof schema.metadata !== 'object') {
    errors.push(`metadata must be an object`);
  } else {
    if (!isValidTimestamp(schema.metadata.created)) {
      errors.push(`Invalid metadata.created timestamp`);
    }
    if (!isValidTimestamp(schema.metadata.last_modified)) {
      errors.push(`Invalid metadata.last_modified timestamp`);
    }
  }

  return {
    valid: errors.length === 0,
    errors
  };
}

// ============================================================================
// MAIN API FUNCTIONS
// ============================================================================

/**
 * Load kanji progress schema from localStorage
 *
 * Returns null if no schema exists (first-time user).
 * Automatically runs migrations if schema is older than current version.
 * Throws error if schema is corrupted beyond repair.
 * Logs warnings for minor validation issues but still returns data.
 *
 * @returns {Object|null} Loaded schema or null if not found
 * @throws {Error} If schema is corrupted and unrecoverable
 */
function loadSchema() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);

    // First-time user - no stored data
    if (raw === null) {
      console.log('No stored schema found. Creating default.');
      return null;
    }

    // Parse JSON
    let schema;
    try {
      schema = JSON.parse(raw);
    } catch (e) {
      throw new Error(`Corrupted localStorage data: ${e.message}`);
    }

    // Run migrations if needed (before validation)
    if (schema.version && compareVersions(schema.version, SCHEMA_VERSION) < 0) {
      console.log(`Schema version ${schema.version} is older than ${SCHEMA_VERSION}, running migrations...`);
      schema = runMigrations(schema);

      // Save migrated schema immediately
      try {
        const json = JSON.stringify(schema);
        localStorage.setItem(STORAGE_KEY, json);
        console.log('Migrated schema saved to localStorage.');
      } catch (e) {
        console.warn('Failed to save migrated schema:', e);
      }
    }

    // Validate schema (after migration)
    const validation = validateSchema(schema);
    if (!validation.valid) {
      // Log warnings but don't throw - allow graceful degradation
      console.warn('Schema validation warnings:', validation.errors);

      // If critical errors exist, throw
      const criticalErrors = validation.errors.filter(
        err => err.includes('must be') || err.includes('mismatch')
      );
      if (criticalErrors.length > 0) {
        throw new Error(`Critical schema errors: ${criticalErrors.join(', ')}`);
      }
    }

    console.log(`Schema loaded: v${schema.version}, ${Object.keys(schema.kanji).length} kanji`);
    return schema;

  } catch (error) {
    console.error('Failed to load schema:', error);
    throw error;
  }
}

/**
 * Save kanji progress schema to localStorage
 *
 * Validates schema before saving. Updates last_modified timestamp.
 * Returns false if localStorage quota exceeded. Throws on validation failure.
 *
 * @param {Object} schema - Schema to save
 * @returns {boolean} True if saved successfully, false if quota exceeded
 * @throws {Error} If schema validation fails
 */
function saveSchema(schema) {
  try {
    // Validate before saving
    const validation = validateSchema(schema);
    if (!validation.valid) {
      throw new Error(`Schema validation failed: ${validation.errors.join(', ')}`);
    }

    // Update metadata
    schema.metadata.last_modified = new Date().toISOString();

    // Try to save
    try {
      const json = JSON.stringify(schema);
      localStorage.setItem(STORAGE_KEY, json);
      console.log(`Schema saved: ${json.length} bytes`);
      return true;
    } catch (e) {
      if (e.name === 'QuotaExceededError') {
        console.error('localStorage quota exceeded');
        return false;
      }
      throw e;
    }

  } catch (error) {
    console.error('Failed to save schema:', error);
    throw error;
  }
}

/**
 * Get progress for a specific kanji
 *
 * @param {string} character - Single kanji character
 * @returns {Object|null} Progress object or null if not found
 */
function getKanjiProgress(character) {
  try {
    if (!isValidKanjiCharacter(character)) {
      console.error(`Invalid character: ${character}`);
      return null;
    }

    const schema = loadSchema();
    if (schema === null) {
      console.warn('No schema found');
      return null;
    }

    const progress = schema.kanji[character];
    if (!progress) {
      console.debug(`Kanji not in schema: ${character}`);
      return null;
    }

    return progress;

  } catch (error) {
    console.error(`Failed to get kanji progress for ${character}:`, error);
    return null;
  }
}

/**
 * Update progress for a specific kanji
 *
 * Validates progress object before saving. Updates schema last_modified.
 * Returns false if save fails (quota). Throws on validation failure.
 *
 * @param {string} character - Single kanji character
 * @param {Object} progress - New progress object
 * @returns {boolean} True if saved successfully
 * @throws {Error} If validation fails
 */
function updateKanjiProgress(character, progress) {
  try {
    if (!isValidKanjiCharacter(character)) {
      throw new Error(`Invalid character: ${character}`);
    }

    // Validate progress object
    const validation = validateKanjiProgress(progress, character);
    if (!validation.valid) {
      throw new Error(`Progress validation failed: ${validation.errors.join(', ')}`);
    }

    // Load current schema
    let schema = loadSchema();
    if (schema === null) {
      schema = createDefaultSchema();
    }

    // Update kanji progress
    schema.kanji[character] = progress;

    // Save schema
    const saved = saveSchema(schema);

    // Invalidate mastery cache
    if (saved) {
      schema.stats.jlpt_mastery_cache.calculated_at = null;
    }

    return saved;

  } catch (error) {
    console.error(`Failed to update kanji progress for ${character}:`, error);
    throw error;
  }
}

/**
 * Initialize schema with kanji metadata
 *
 * Call this once on first app load to populate schema with 169 kanji.
 * Requires kanji-metadata.js to be loaded first.
 *
 * @param {Array} kanjiArray - Array of kanji metadata objects from kanji-metadata.js
 * @returns {boolean} True if initialization successful
 */
function initializeSchemaWithKanji(kanjiArray) {
  try {
    if (!Array.isArray(kanjiArray) || kanjiArray.length === 0) {
      throw new Error('kanjiArray must be non-empty array');
    }

    let schema = loadSchema();
    if (schema === null) {
      schema = createDefaultSchema();
    }

    // Add each kanji to schema if not already present
    for (const kanjiData of kanjiArray) {
      if (!schema.kanji[kanjiData.character]) {
        schema.kanji[kanjiData.character] = {
          character: kanjiData.character,
          jlpt_level: kanjiData.jlpt,
          topics: kanjiData.topics,
          srs: {
            stage: 'locked',
            interval_days: 0,
            ease_factor: 2.5,
            repetitions: 0,
            last_reviewed: null,
            next_review_date: null,
            total_reviews: 0,
            correct_count: 0,
            is_new: true,
            introduced_at: null
          },
          history: []
        };
      }
    }

    // Update stage distribution
    for (const progress of Object.values(schema.kanji)) {
      schema.stats.stage_distribution[progress.srs.stage]++;
    }

    const saved = saveSchema(schema);
    if (saved) {
      console.log(`Initialized schema with ${kanjiArray.length} kanji`);
    }

    return saved;

  } catch (error) {
    console.error('Failed to initialize schema with kanji:', error);
    throw error;
  }
}

/**
 * Clear all user data (for testing or reset)
 * WARNING: This is destructive and cannot be undone!
 *
 * @returns {boolean} True if cleared successfully
 */
function clearAllData() {
  try {
    localStorage.removeItem(STORAGE_KEY);
    console.warn('All kanji progress data cleared!');
    return true;
  } catch (error) {
    console.error('Failed to clear data:', error);
    return false;
  }
}

/**
 * Initialize schema from kanji metadata and return the schema
 *
 * Convenience function for first-time setup that returns the schema object.
 * Uses initializeSchemaWithKanji internally.
 *
 * @param {Array} kanjiArray - Array of kanji metadata objects from kanji-metadata.js
 * @returns {Object} Initialized schema object
 */
function initializeFromMetadata(kanjiArray) {
  try {
    if (!Array.isArray(kanjiArray) || kanjiArray.length === 0) {
      throw new Error('kanjiArray must be non-empty array');
    }

    let schema = createDefaultSchema();

    // Add each kanji to schema
    for (const kanjiData of kanjiArray) {
      schema.kanji[kanjiData.character] = {
        character: kanjiData.character,
        jlpt_level: kanjiData.jlpt,
        topics: kanjiData.topics || ['home-life'],
        srs: {
          stage: 'locked',
          interval_days: 0,
          ease_factor: 2.5,
          repetitions: 0,
          last_reviewed: null,
          next_review_date: null,
          total_reviews: 0,
          correct_count: 0,
          is_new: true,
          introduced_at: null
        },
        history: []
      };
    }

    // Update stage distribution
    schema.stats.stage_distribution.locked = Object.keys(schema.kanji).length;

    // Save the schema
    saveSchema(schema);

    console.log(`Initialized schema with ${kanjiArray.length} kanji`);

    return schema;

  } catch (error) {
    console.error('Failed to initialize schema from metadata:', error);
    throw error;
  }
}

// ============================================================================
// BROWSER EXPORT
// ============================================================================

if (typeof window !== 'undefined') {
  window.KanjiStorage = {
    // Constants
    STORAGE_KEY,
    SCHEMA_VERSION,
    STAGES,
    LIMITS,

    // Schema initialization
    createDefaultSchema,
    initializeFromMetadata,
    initializeSchemaWithKanji,

    // Migration
    compareVersions,
    runMigrations,
    migrateToV1_1_0,

    // Validation
    validateSchema,
    validateKanjiProgress,
    validateDailyGoal,
    validateXPStats,
    validateStreakStats,

    // Utilities
    getLocalDateString,

    // API
    loadSchema,
    saveSchema,
    getKanjiProgress,
    updateKanjiProgress,
    clearAllData
  };
}

// ============================================================================
// NODE.JS EXPORT (for testing)
// ============================================================================

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    // Constants
    STORAGE_KEY,
    SCHEMA_VERSION,
    STAGES,
    LIMITS,

    // Schema initialization
    createDefaultSchema,
    generateClientId,

    // Migration
    compareVersions,
    runMigrations,
    migrateToV1_1_0,

    // Validation
    validateSchema,
    validateKanjiProgress,
    validateSRSState,
    validateHistoryEntry,
    validateDailyGoal,
    validateXPStats,
    validateStreakStats,
    isValidDateString,
    isValidTimeString,

    // Utilities
    getLocalDateString,

    // API
    loadSchema,
    saveSchema,
    getKanjiProgress,
    updateKanjiProgress,
    initializeSchemaWithKanji,
    clearAllData
  };
}
