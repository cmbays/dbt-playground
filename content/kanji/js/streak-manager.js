/**
 * Streak Manager Module (streak-manager.js)
 *
 * Handles streak tracking, freeze management, and streak-related calculations.
 * Part of Phase 2: Engagement Layer.
 *
 * Version: v0.4.0
 * Updated: 2026-01-25
 *
 * TDD Reference: TDD-003 §4
 * PRD Reference: PRD-003
 * Task: T2.4 (#49)
 */

const StreakManager = (function() {
  'use strict';

  // ============================================
  // Constants
  // ============================================

  const MAX_FREEZES = 2;
  const FREEZE_EARN_INTERVAL = 7; // Earn 1 freeze every 7 days
  const AT_RISK_HOUR = 18; // 6 PM

  // Milestone definitions
  const MILESTONES = {
    7: { title: 'One Week!', message: "You've studied for a full week!", emoji: '🔥' },
    14: { title: 'Two Weeks!', message: 'Consistency is building!', emoji: '🔥🔥' },
    30: { title: 'One Month!', message: "That's serious dedication!", emoji: '🏆' },
    60: { title: 'Two Months!', message: "You're unstoppable!", emoji: '💪' },
    90: { title: 'Three Months!', message: 'A habit is born!', emoji: '⭐' },
    180: { title: 'Six Months!', message: 'Half a year of dedication!', emoji: '🌟' },
    365: { title: 'One Year!', message: "You're a legend!", emoji: '👑' }
  };

  // ============================================
  // Date Utilities
  // ============================================

  /**
   * Get date string for a given timestamp in local time
   *
   * @param {Date} date - Date object (defaults to now)
   * @returns {string} YYYY-MM-DD format in local time
   */
  function getLocalDateString(date = new Date()) {
    return date.toLocaleDateString('en-CA'); // Returns YYYY-MM-DD
  }

  /**
   * Check if two date strings represent the same day
   *
   * @param {string} dateStr1 - First date (YYYY-MM-DD)
   * @param {string} dateStr2 - Second date (YYYY-MM-DD)
   * @returns {boolean} True if same day
   */
  function isSameDay(dateStr1, dateStr2) {
    return dateStr1 === dateStr2;
  }

  /**
   * Check if dateStr2 is exactly one day after dateStr1
   *
   * @param {string} dateStr1 - First date (YYYY-MM-DD)
   * @param {string} dateStr2 - Second date (YYYY-MM-DD)
   * @returns {boolean} True if dateStr2 is next day
   */
  function isNextDay(dateStr1, dateStr2) {
    if (!dateStr1 || !dateStr2) return false;

    const date1 = new Date(dateStr1 + 'T00:00:00');
    const date2 = new Date(dateStr2 + 'T00:00:00');
    const diffMs = date2 - date1;
    const diffDays = Math.round(diffMs / (24 * 60 * 60 * 1000));

    return diffDays === 1;
  }

  /**
   * Get number of days between two date strings
   *
   * @param {string} dateStr1 - Start date (YYYY-MM-DD)
   * @param {string} dateStr2 - End date (YYYY-MM-DD)
   * @returns {number} Number of days between (positive if dateStr2 > dateStr1)
   */
  function daysBetween(dateStr1, dateStr2) {
    if (!dateStr1 || !dateStr2) return 0;

    const date1 = new Date(dateStr1 + 'T00:00:00');
    const date2 = new Date(dateStr2 + 'T00:00:00');
    const diffMs = date2 - date1;

    return Math.floor(diffMs / (24 * 60 * 60 * 1000));
  }

  // ============================================
  // Streak Management
  // ============================================

  /**
   * Update streak state based on current date
   * Call this at the start of each session
   *
   * @param {Object} schema - Full schema object (will be mutated)
   * @returns {Object} { schema, streakBroken, freezeUsed, streakIncreased, newStreak, milestone }
   */
  function updateStreak(schema) {
    if (!schema || !schema.stats || !schema.stats.streak) {
      console.error('StreakManager: Invalid schema structure');
      return {
        schema,
        streakBroken: false,
        freezeUsed: false,
        streakIncreased: false,
        newStreak: 0,
        milestone: null
      };
    }

    const today = getLocalDateString();
    const lastStudy = schema.stats.streak.last_study_date;

    let streakBroken = false;
    let freezeUsed = false;
    let streakIncreased = false;
    let milestone = null;

    if (!lastStudy) {
      // First ever study session
      schema.stats.streak.current = 1;
      schema.stats.streak.longest = Math.max(1, schema.stats.streak.longest || 0);
      schema.stats.streak.last_study_date = today;
      streakIncreased = true;

    } else if (isSameDay(lastStudy, today)) {
      // Already studied today - no change
      // (streak was already incremented on first study of the day)

    } else if (isNextDay(lastStudy, today)) {
      // Consecutive day - increment streak
      schema.stats.streak.current += 1;
      schema.stats.streak.last_study_date = today;
      streakIncreased = true;

      // Update longest streak if needed
      if (schema.stats.streak.current > schema.stats.streak.longest) {
        schema.stats.streak.longest = schema.stats.streak.current;
      }

      // Check for freeze earning (every 7 days, max 2)
      checkFreezeEarning(schema);

      // Check for milestone
      milestone = getStreakMilestone(schema.stats.streak.current);

    } else {
      // Gap detected - check how many days
      const daysMissed = daysBetween(lastStudy, today) - 1;

      if (daysMissed === 1 && schema.stats.streak.freezes_available > 0) {
        // Use freeze for single missed day
        schema.stats.streak.freezes_available -= 1;
        schema.stats.streak.freeze_used_date = today;
        schema.stats.streak.current += 1; // Continue streak (counts the freeze day + today)
        schema.stats.streak.last_study_date = today;
        freezeUsed = true;
        streakIncreased = true;

        // Update longest streak if needed
        if (schema.stats.streak.current > schema.stats.streak.longest) {
          schema.stats.streak.longest = schema.stats.streak.current;
        }

        // Check for milestone
        milestone = getStreakMilestone(schema.stats.streak.current);

      } else {
        // Streak broken - reset to 1
        schema.stats.streak.current = 1;
        schema.stats.streak.last_study_date = today;
        streakBroken = true;
        streakIncreased = true; // New streak of 1

        // Note: Don't reset freezes_available when streak breaks
        // User keeps their freezes for the new streak
      }
    }

    return {
      schema,
      streakBroken,
      freezeUsed,
      streakIncreased,
      newStreak: schema.stats.streak.current,
      milestone
    };
  }

  /**
   * Check if user should earn a new freeze
   * Called after streak increment
   *
   * @param {Object} schema - Schema object (will be mutated)
   * @returns {boolean} True if freeze was earned
   */
  function checkFreezeEarning(schema) {
    const streak = schema.stats.streak;

    // Check if at a freeze earning interval
    if (streak.current % FREEZE_EARN_INTERVAL === 0 &&
        streak.freezes_available < MAX_FREEZES &&
        streak.current > streak.freezes_earned_at) {
      streak.freezes_available += 1;
      streak.freezes_earned_at = streak.current;
      return true;
    }

    return false;
  }

  /**
   * Manually use a freeze (for UI if needed)
   *
   * @param {Object} schema - Full schema object
   * @returns {Object} { schema, success, message }
   */
  function useFreeze(schema) {
    if (!schema || !schema.stats || !schema.stats.streak) {
      return { schema, success: false, message: 'Invalid schema' };
    }

    if (schema.stats.streak.freezes_available <= 0) {
      return { schema, success: false, message: 'No freezes available' };
    }

    schema.stats.streak.freezes_available -= 1;
    schema.stats.streak.freeze_used_date = getLocalDateString();

    return { schema, success: true, message: 'Freeze used successfully' };
  }

  // ============================================
  // Streak Status
  // ============================================

  /**
   * Check if streak is at risk (no study today, after 6 PM)
   *
   * @param {Object} schema - Full schema object
   * @returns {boolean} True if streak is at risk
   */
  function isStreakAtRisk(schema) {
    if (!schema || !schema.stats || !schema.stats.streak) {
      return false;
    }

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
           currentHour >= AT_RISK_HOUR;
  }

  /**
   * Get time remaining until streak breaks (midnight)
   *
   * @returns {Object} { hours, minutes, formatted }
   */
  function getTimeUntilStreakBreak() {
    const now = new Date();
    const midnight = new Date(now);
    midnight.setDate(midnight.getDate() + 1);
    midnight.setHours(0, 0, 0, 0);

    const diffMs = midnight - now;
    const hours = Math.floor(diffMs / (1000 * 60 * 60));
    const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));

    let formatted;
    if (hours > 0) {
      formatted = `${hours}h ${minutes}m`;
    } else {
      formatted = `${minutes}m`;
    }

    return { hours, minutes, formatted };
  }

  /**
   * Check if current streak is at a milestone
   *
   * @param {number} streakDays - Current streak
   * @returns {Object|null} Milestone info or null
   */
  function getStreakMilestone(streakDays) {
    return MILESTONES[streakDays] || null;
  }

  /**
   * Get all milestones achieved by current streak
   *
   * @param {number} streakDays - Current streak
   * @returns {Array} Array of achieved milestone objects
   */
  function getAchievedMilestones(streakDays) {
    const achieved = [];
    for (const [days, milestone] of Object.entries(MILESTONES)) {
      if (streakDays >= parseInt(days)) {
        achieved.push({ days: parseInt(days), ...milestone });
      }
    }
    return achieved;
  }

  /**
   * Get next milestone to reach
   *
   * @param {number} streakDays - Current streak
   * @returns {Object|null} Next milestone info with days remaining
   */
  function getNextMilestone(streakDays) {
    const milestoneDays = Object.keys(MILESTONES).map(Number).sort((a, b) => a - b);

    for (const days of milestoneDays) {
      if (days > streakDays) {
        return {
          days,
          daysRemaining: days - streakDays,
          ...MILESTONES[days]
        };
      }
    }

    return null; // All milestones achieved
  }

  // ============================================
  // Streak Display Helpers
  // ============================================

  /**
   * Get streak status for display
   *
   * @param {Object} schema - Full schema object
   * @returns {Object} Status info for UI
   */
  function getStreakStatus(schema) {
    if (!schema || !schema.stats || !schema.stats.streak) {
      return {
        current: 0,
        longest: 0,
        freezesAvailable: 0,
        freezeUsedRecently: false,
        atRisk: false,
        studiedToday: false,
        nextMilestone: null
      };
    }

    const streak = schema.stats.streak;
    const today = getLocalDateString();
    const studiedToday = streak.last_study_date === today;

    // Check if freeze was used in last 2 days
    let freezeUsedRecently = false;
    if (streak.freeze_used_date) {
      const daysSinceFreeze = daysBetween(streak.freeze_used_date, today);
      freezeUsedRecently = daysSinceFreeze <= 2;
    }

    return {
      current: streak.current || 0,
      longest: streak.longest || 0,
      freezesAvailable: streak.freezes_available || 0,
      freezeUsedRecently,
      atRisk: isStreakAtRisk(schema),
      studiedToday,
      nextMilestone: getNextMilestone(streak.current || 0),
      timeRemaining: studiedToday ? null : getTimeUntilStreakBreak()
    };
  }

  /**
   * Format streak days for display
   *
   * @param {number} days - Number of days
   * @returns {string} Formatted string (e.g., "7 days", "1 day")
   */
  function formatStreakDays(days) {
    if (days === 1) return '1 day';
    return `${days} days`;
  }

  /**
   * Get motivational message based on streak
   *
   * @param {number} streakDays - Current streak
   * @returns {string} Motivational message
   */
  function getMotivationalMessage(streakDays) {
    if (streakDays === 0) {
      return 'Start your streak today!';
    } else if (streakDays === 1) {
      return 'Great start! Keep it going!';
    } else if (streakDays < 7) {
      return `${7 - streakDays} days until your first freeze!`;
    } else if (streakDays < 14) {
      return 'Keep building that habit!';
    } else if (streakDays < 30) {
      return "You're doing amazing!";
    } else if (streakDays < 100) {
      return 'Incredible dedication!';
    } else {
      return "You're a true master!";
    }
  }

  // ============================================
  // Legacy Data Migration Helper
  // ============================================

  /**
   * Migrate legacy streak fields to new structure
   * Used by storage.js migration
   *
   * @param {Object} stats - Stats object with legacy fields
   * @returns {Object} New streak object
   */
  function migrateFromLegacy(stats) {
    return {
      current: stats.streak_days || 0,
      longest: stats.streak_days || 0,
      last_study_date: stats.last_study_date || null,
      freezes_available: 0,
      freeze_used_date: null,
      freezes_earned_at: 0
    };
  }

  // ============================================
  // Public API
  // ============================================

  return {
    // Constants (exposed for testing/display)
    MAX_FREEZES,
    FREEZE_EARN_INTERVAL,
    AT_RISK_HOUR,
    MILESTONES,

    // Date Utilities
    getLocalDateString,
    isSameDay,
    isNextDay,
    daysBetween,

    // Streak Management
    updateStreak,
    checkFreezeEarning,
    useFreeze,

    // Streak Status
    isStreakAtRisk,
    getTimeUntilStreakBreak,
    getStreakMilestone,
    getAchievedMilestones,
    getNextMilestone,

    // Display Helpers
    getStreakStatus,
    formatStreakDays,
    getMotivationalMessage,

    // Migration
    migrateFromLegacy
  };
})();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = StreakManager;
}
