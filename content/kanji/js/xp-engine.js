/**
 * XP Engine Module (xp-engine.js)
 *
 * Handles XP calculation, level progression, and level-up detection.
 * Part of Phase 2: Engagement Layer.
 *
 * Version: v0.4.0
 * Updated: 2026-01-25
 *
 * TDD Reference: TDD-003 §3
 * PRD Reference: PRD-003
 * Task: T2.2 (#47)
 */

const XPEngine = (function() {
  'use strict';

  // ============================================
  // Constants
  // ============================================

  const BASE_XP = 10;
  const MAX_LEVEL = 60;

  // Quality bonuses (quality values: 0=Again, 2=Hard, 4=Good, 5=Easy)
  const QUALITY_BONUS = {
    0: 0,   // Again - no bonus
    2: 0,   // Hard - no bonus
    4: 5,   // Good - +5 XP
    5: 10   // Easy - +10 XP
  };

  // Streak bonus tiers (10% per 7-day tier, max 50%)
  const MAX_STREAK_TIER = 5;
  const STREAK_TIER_DAYS = 7;
  const STREAK_BONUS_PER_TIER = 0.10;

  // Special bonuses
  const DAILY_GOAL_BONUS = 50;
  const PERFECT_SESSION_BONUS = 25;
  const PERFECT_SESSION_MIN_CARDS = 5;

  // Milestone levels for special celebrations
  const MILESTONE_LEVELS = [10, 20, 30, 40, 50, 60];

  // ============================================
  // XP Calculation
  // ============================================

  /**
   * Calculate XP earned for a single review
   *
   * Formula: (BASE_XP + QUALITY_BONUS) * STREAK_MULTIPLIER
   *
   * @param {number} quality - Review quality (0, 2, 4, or 5)
   * @param {number} streakDays - Current streak days (0+)
   * @returns {number} XP earned for this review
   */
  function calculateXP(quality, streakDays = 0) {
    // Validate inputs
    if (![0, 2, 4, 5].includes(quality)) {
      console.warn('XPEngine: Invalid quality value, defaulting to 0');
      quality = 0;
    }
    streakDays = Math.max(0, Math.floor(streakDays || 0));

    // Base XP + quality bonus
    const qualityBonus = QUALITY_BONUS[quality] || 0;
    const baseTotal = BASE_XP + qualityBonus;

    // Streak multiplier (10% per 7-day tier, max 50%)
    const streakTier = Math.min(Math.floor(streakDays / STREAK_TIER_DAYS), MAX_STREAK_TIER);
    const streakMultiplier = 1 + (streakTier * STREAK_BONUS_PER_TIER);

    return Math.round(baseTotal * streakMultiplier);
  }

  /**
   * Calculate perfect session bonus
   *
   * @param {number} totalCards - Total cards in session
   * @param {number} correctCount - Number of Good (4) or Easy (5) responses
   * @returns {number} Bonus XP (25 if perfect, 0 otherwise)
   */
  function calculatePerfectSessionBonus(totalCards, correctCount) {
    if (totalCards >= PERFECT_SESSION_MIN_CARDS && correctCount === totalCards) {
      return PERFECT_SESSION_BONUS;
    }
    return 0;
  }

  /**
   * Get the daily goal completion bonus
   *
   * @returns {number} Daily goal bonus XP
   */
  function getDailyGoalBonus() {
    return DAILY_GOAL_BONUS;
  }

  // ============================================
  // Level System
  // ============================================

  /**
   * Calculate XP required to advance from level N to level N+1
   *
   * Formula: 50 * level * (1 + 0.1 * floor(level/10))
   * This creates a gentle exponential curve with tier jumps every 10 levels.
   *
   * @param {number} level - Current level (1-59)
   * @returns {number} XP required to advance to next level
   */
  function getXPRequiredForLevel(level) {
    if (level < 1 || level >= MAX_LEVEL) return 0;

    const tierMultiplier = 1 + 0.1 * Math.floor(level / 10);
    return Math.round(50 * level * tierMultiplier);
  }

  /**
   * Calculate total XP needed to reach a specific level from level 1
   *
   * @param {number} targetLevel - Target level (1-60)
   * @returns {number} Total XP required to reach this level
   */
  function getXPForLevel(targetLevel) {
    if (targetLevel <= 1) return 0;
    if (targetLevel > MAX_LEVEL) targetLevel = MAX_LEVEL;

    let totalXP = 0;
    for (let level = 1; level < targetLevel; level++) {
      totalXP += getXPRequiredForLevel(level);
    }
    return totalXP;
  }

  /**
   * Determine level and progress from total XP
   *
   * @param {number} totalXP - Total lifetime XP
   * @returns {Object} { level, xp_this_level, xp_to_next_level }
   */
  function getLevelFromXP(totalXP) {
    totalXP = Math.max(0, Math.floor(totalXP || 0));

    let level = 1;
    let cumulativeXP = 0;

    while (level < MAX_LEVEL) {
      const xpForNextLevel = getXPRequiredForLevel(level);
      if (cumulativeXP + xpForNextLevel > totalXP) {
        break;
      }
      cumulativeXP += xpForNextLevel;
      level++;
    }

    const xpThisLevel = totalXP - cumulativeXP;
    const xpToNextLevel = level < MAX_LEVEL ? getXPRequiredForLevel(level) : 0;

    return {
      level,
      xp_this_level: xpThisLevel,
      xp_to_next_level: xpToNextLevel
    };
  }

  /**
   * Check if a level is a milestone level (for special celebrations)
   *
   * @param {number} level - Level to check
   * @returns {boolean} True if milestone level
   */
  function isMilestoneLevel(level) {
    return MILESTONE_LEVELS.includes(level);
  }

  // ============================================
  // XP Award System
  // ============================================

  /**
   * Award XP to schema and check for level up
   *
   * @param {Object} schema - Full schema object (will be mutated)
   * @param {number} xpAmount - XP to award
   * @returns {Object} { schema, leveledUp, newLevel, previousLevel, celebration }
   */
  function awardXP(schema, xpAmount) {
    if (!schema || !schema.stats || !schema.stats.xp) {
      console.error('XPEngine: Invalid schema structure');
      return { schema, leveledUp: false, newLevel: null, previousLevel: null, celebration: null };
    }

    xpAmount = Math.max(0, Math.floor(xpAmount || 0));
    if (xpAmount === 0) {
      return { schema, leveledUp: false, newLevel: schema.stats.xp.current_level, previousLevel: schema.stats.xp.current_level, celebration: null };
    }

    const previousLevel = schema.stats.xp.current_level;

    // Add XP to totals
    schema.stats.xp.total += xpAmount;

    // Update today's XP if today object exists
    if (schema.stats.today) {
      schema.stats.today.xp_earned = (schema.stats.today.xp_earned || 0) + xpAmount;
    }

    // Recalculate level
    const levelInfo = getLevelFromXP(schema.stats.xp.total);
    schema.stats.xp.current_level = levelInfo.level;
    schema.stats.xp.xp_this_level = levelInfo.xp_this_level;
    schema.stats.xp.xp_to_next_level = levelInfo.xp_to_next_level;

    const leveledUp = levelInfo.level > previousLevel;

    // Record level-up timestamp
    if (leveledUp) {
      schema.stats.xp.last_level_up = new Date().toISOString();
    }

    // Determine celebration type
    let celebration = null;
    if (leveledUp) {
      if (isMilestoneLevel(levelInfo.level)) {
        celebration = 'milestone'; // Special celebration for levels 10, 20, 30, 40, 50, 60
      } else {
        celebration = 'level_up'; // Standard celebration
      }
    }

    return {
      schema,
      leveledUp,
      newLevel: levelInfo.level,
      previousLevel,
      celebration
    };
  }

  // ============================================
  // XP Progress Helpers
  // ============================================

  /**
   * Get progress percentage toward next level
   *
   * @param {Object} xpStats - schema.stats.xp object
   * @returns {number} Percentage (0-100)
   */
  function getLevelProgress(xpStats) {
    if (!xpStats || xpStats.current_level >= MAX_LEVEL) return 100;
    if (xpStats.xp_to_next_level === 0) return 100;

    return Math.min(100, Math.round((xpStats.xp_this_level / xpStats.xp_to_next_level) * 100));
  }

  /**
   * Get human-readable level title
   *
   * @param {number} level - Current level
   * @returns {string} Level title
   */
  function getLevelTitle(level) {
    if (level >= 60) return 'Master';
    if (level >= 50) return 'Expert';
    if (level >= 40) return 'Advanced';
    if (level >= 30) return 'Intermediate';
    if (level >= 20) return 'Apprentice III';
    if (level >= 10) return 'Apprentice II';
    if (level >= 5) return 'Apprentice I';
    return 'Novice';
  }

  /**
   * Get streak bonus multiplier for display
   *
   * @param {number} streakDays - Current streak days
   * @returns {Object} { tier, multiplier, percentage }
   */
  function getStreakBonus(streakDays) {
    const tier = Math.min(Math.floor(streakDays / STREAK_TIER_DAYS), MAX_STREAK_TIER);
    const multiplier = 1 + (tier * STREAK_BONUS_PER_TIER);
    const percentage = tier * 10;

    return { tier, multiplier, percentage };
  }

  /**
   * Generate XP table for debugging/display
   *
   * @param {number} maxLevel - Maximum level to show (default 60)
   * @returns {Array} Array of { level, xpForLevel, cumulativeXP }
   */
  function generateXPTable(maxLevel = MAX_LEVEL) {
    const table = [];
    let cumulativeXP = 0;

    for (let level = 1; level <= maxLevel; level++) {
      const xpForLevel = level === 1 ? 0 : getXPRequiredForLevel(level - 1);
      cumulativeXP += xpForLevel;

      table.push({
        level,
        xpForLevel,
        cumulativeXP,
        xpToNextLevel: getXPRequiredForLevel(level)
      });
    }

    return table;
  }

  // ============================================
  // Public API
  // ============================================

  return {
    // Constants (exposed for testing/display)
    BASE_XP,
    MAX_LEVEL,
    QUALITY_BONUS,
    DAILY_GOAL_BONUS,
    PERFECT_SESSION_BONUS,
    PERFECT_SESSION_MIN_CARDS,
    MILESTONE_LEVELS,

    // XP Calculation
    calculateXP,
    calculatePerfectSessionBonus,
    getDailyGoalBonus,

    // Level System
    getXPRequiredForLevel,
    getXPForLevel,
    getLevelFromXP,
    isMilestoneLevel,

    // XP Award
    awardXP,

    // Helpers
    getLevelProgress,
    getLevelTitle,
    getStreakBonus,
    generateXPTable
  };
})();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = XPEngine;
}
