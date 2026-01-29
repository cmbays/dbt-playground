/**
 * Goals Manager Module (goals-manager.js)
 *
 * Handles daily goal tracking, progress calculation, and notifications.
 * Part of Phase 2: Engagement Layer.
 *
 * Version: v0.4.0
 * Updated: 2026-01-25
 *
 * TDD Reference: TDD-003 §5
 * PRD Reference: PRD-003
 * Task: T2.9 (#56)
 */

const GoalsManager = (function() {
  'use strict';

  // ============================================
  // Constants
  // ============================================

  const GOAL_MIN = 1;
  const GOAL_MAX = 100;
  const GOAL_DEFAULT = 10;
  const GOAL_PRESETS = [5, 10, 15, 20, 25];
  const GOAL_COMPLETION_BONUS = 50; // XP bonus for completing daily goal

  // Notification settings
  const DEFAULT_NOTIFY_TIME = '19:00';

  // ============================================
  // Goal Setting
  // ============================================

  /**
   * Set daily goal target
   *
   * @param {Object} schema - Full schema object (will be mutated)
   * @param {number} targetCards - Goal target (1-100)
   * @returns {Object} { schema, success, message }
   */
  function setDailyGoal(schema, targetCards) {
    if (!schema || !schema.settings || !schema.settings.daily_goal) {
      return { schema, success: false, message: 'Invalid schema structure' };
    }

    targetCards = Math.floor(targetCards);

    if (targetCards < GOAL_MIN || targetCards > GOAL_MAX) {
      return {
        schema,
        success: false,
        message: `Daily goal must be between ${GOAL_MIN} and ${GOAL_MAX}`
      };
    }

    schema.settings.daily_goal.target_cards = targetCards;

    return { schema, success: true, message: `Daily goal set to ${targetCards} cards` };
  }

  /**
   * Enable or disable daily goals
   *
   * @param {Object} schema - Full schema object
   * @param {boolean} enabled - Whether to enable goals
   * @returns {Object} Updated schema
   */
  function setGoalEnabled(schema, enabled) {
    if (!schema || !schema.settings || !schema.settings.daily_goal) {
      return schema;
    }

    schema.settings.daily_goal.enabled = !!enabled;
    return schema;
  }

  /**
   * Get goal settings
   *
   * @param {Object} schema - Full schema object
   * @returns {Object} Goal settings
   */
  function getGoalSettings(schema) {
    if (!schema || !schema.settings || !schema.settings.daily_goal) {
      return {
        enabled: true,
        target_cards: GOAL_DEFAULT,
        notify_enabled: false,
        notify_time: DEFAULT_NOTIFY_TIME
      };
    }

    return { ...schema.settings.daily_goal };
  }

  // ============================================
  // Goal Progress
  // ============================================

  /**
   * Get current goal progress
   *
   * @param {Object} schema - Full schema object
   * @returns {Object} { target, completed, percentage, isComplete, remaining, enabled }
   */
  function getGoalProgress(schema) {
    if (!schema || !schema.settings || !schema.stats) {
      return {
        target: GOAL_DEFAULT,
        completed: 0,
        percentage: 0,
        isComplete: false,
        remaining: GOAL_DEFAULT,
        enabled: false
      };
    }

    const settings = schema.settings.daily_goal || {};
    const today = schema.stats.today || {};

    const enabled = settings.enabled !== false;
    const target = settings.target_cards || GOAL_DEFAULT;

    // Count reviews and new cards
    const reviews = today.reviews_completed || 0;
    const newCards = today.new_cards_introduced || 0;
    const completed = reviews + newCards;

    const percentage = Math.min(100, Math.round((completed / target) * 100));
    const isComplete = completed >= target;
    const remaining = Math.max(0, target - completed);

    return {
      target,
      completed,
      percentage,
      isComplete,
      remaining,
      enabled
    };
  }

  /**
   * Check if goal was just completed and award bonus
   *
   * @param {Object} schema - Full schema object (will be mutated)
   * @returns {Object} { schema, justCompleted, bonusXP, previouslyCompleted }
   */
  function checkGoalCompletion(schema) {
    if (!schema || !schema.stats || !schema.stats.today) {
      return {
        schema,
        justCompleted: false,
        bonusXP: 0,
        previouslyCompleted: false
      };
    }

    const progress = getGoalProgress(schema);

    // Check if goal is enabled
    if (!progress.enabled) {
      return {
        schema,
        justCompleted: false,
        bonusXP: 0,
        previouslyCompleted: false
      };
    }

    const previouslyCompleted = schema.stats.today.goal_completed || false;

    // Check if goal just completed (wasn't already marked)
    if (progress.isComplete && !previouslyCompleted) {
      schema.stats.today.goal_completed = true;

      return {
        schema,
        justCompleted: true,
        bonusXP: GOAL_COMPLETION_BONUS,
        previouslyCompleted: false
      };
    }

    return {
      schema,
      justCompleted: false,
      bonusXP: 0,
      previouslyCompleted
    };
  }

  /**
   * Manually mark goal as completed (for testing/admin)
   *
   * @param {Object} schema - Full schema object
   * @returns {Object} Updated schema
   */
  function markGoalCompleted(schema) {
    if (!schema || !schema.stats || !schema.stats.today) {
      return schema;
    }

    schema.stats.today.goal_completed = true;
    return schema;
  }

  // ============================================
  // Browser Notifications
  // ============================================

  /**
   * Check if browser supports notifications
   *
   * @returns {boolean} True if notifications are supported
   */
  function isNotificationSupported() {
    return 'Notification' in window;
  }

  /**
   * Get current notification permission status
   *
   * @returns {string} 'granted', 'denied', or 'default'
   */
  function getNotificationPermission() {
    if (!isNotificationSupported()) {
      return 'denied';
    }
    return Notification.permission;
  }

  /**
   * Request notification permission
   *
   * @returns {Promise<boolean>} True if permission granted
   */
  async function requestNotificationPermission() {
    if (!isNotificationSupported()) {
      console.warn('GoalsManager: Browser does not support notifications');
      return false;
    }

    try {
      const permission = await Notification.requestPermission();
      return permission === 'granted';
    } catch (error) {
      console.error('GoalsManager: Error requesting notification permission', error);
      return false;
    }
  }

  /**
   * Set notification preferences
   *
   * @param {Object} schema - Full schema object
   * @param {boolean} enabled - Whether notifications are enabled
   * @param {string} time - HH:MM format time string
   * @returns {Object} { schema, success, message }
   */
  function setNotificationSettings(schema, enabled, time = DEFAULT_NOTIFY_TIME) {
    if (!schema || !schema.settings || !schema.settings.daily_goal) {
      return { schema, success: false, message: 'Invalid schema structure' };
    }

    // Validate time format
    if (time && !/^([01]\d|2[0-3]):[0-5]\d$/.test(time)) {
      return { schema, success: false, message: 'Invalid time format. Use HH:MM' };
    }

    schema.settings.daily_goal.notify_enabled = !!enabled;
    if (time) {
      schema.settings.daily_goal.notify_time = time;
    }

    return { schema, success: true, message: 'Notification settings updated' };
  }

  // Scheduled notification timeout ID (for cleanup)
  let scheduledNotificationTimeout = null;

  /**
   * Schedule daily reminder notification
   *
   * @param {string} time - HH:MM format
   * @param {number} streakDays - Current streak for message
   * @param {Object} progress - Goal progress object
   * @returns {boolean} True if scheduled successfully
   */
  function scheduleReminder(time, streakDays = 0, progress = null) {
    if (!isNotificationSupported() || getNotificationPermission() !== 'granted') {
      console.warn('GoalsManager: Cannot schedule - notifications not available');
      return false;
    }

    // Clear any existing scheduled notification
    if (scheduledNotificationTimeout) {
      clearTimeout(scheduledNotificationTimeout);
      scheduledNotificationTimeout = null;
    }

    // Parse target time
    const [hours, minutes] = time.split(':').map(Number);
    const now = new Date();

    let reminderTime = new Date();
    reminderTime.setHours(hours, minutes, 0, 0);

    // If time has passed today, schedule for tomorrow
    if (reminderTime <= now) {
      reminderTime.setDate(reminderTime.getDate() + 1);
    }

    const delay = reminderTime - now;

    scheduledNotificationTimeout = setTimeout(() => {
      showReminderNotification(streakDays, progress);
    }, delay);

    console.log(`GoalsManager: Reminder scheduled for ${reminderTime.toLocaleString()}`);
    return true;
  }

  /**
   * Show the reminder notification
   *
   * @param {number} streakDays - Current streak
   * @param {Object} progress - Goal progress
   */
  function showReminderNotification(streakDays = 0, progress = null) {
    if (getNotificationPermission() !== 'granted') {
      return;
    }

    let title = "Don't forget to study! 📚";
    let body = 'Your Japanese journey awaits.';

    if (streakDays > 0) {
      title = "Don't break your streak! 🔥";
      body = `You have a ${streakDays}-day streak. Study now to keep it alive!`;
    }

    if (progress && !progress.isComplete && progress.remaining > 0) {
      body = `${progress.remaining} cards left to reach your daily goal. ${body}`;
    }

    try {
      new Notification(title, {
        body,
        icon: '/content/kanji/images/icon.png',
        badge: '/content/kanji/images/badge.png',
        tag: 'daily-reminder',
        renotify: true
      });
    } catch (error) {
      console.error('GoalsManager: Error showing notification', error);
    }
  }

  /**
   * Cancel scheduled reminder
   */
  function cancelReminder() {
    if (scheduledNotificationTimeout) {
      clearTimeout(scheduledNotificationTimeout);
      scheduledNotificationTimeout = null;
      console.log('GoalsManager: Reminder cancelled');
    }
  }

  // ============================================
  // Goal Display Helpers
  // ============================================

  /**
   * Get progress bar color based on percentage
   *
   * @param {number} percentage - Progress percentage (0-100)
   * @returns {string} CSS color value
   */
  function getProgressColor(percentage) {
    if (percentage >= 100) return '#22c55e'; // Green - complete
    if (percentage >= 75) return '#84cc16';  // Lime - almost there
    if (percentage >= 50) return '#eab308';  // Yellow - halfway
    if (percentage >= 25) return '#f97316';  // Orange - getting started
    return '#ef4444';                        // Red - just started
  }

  /**
   * Get motivational message based on progress
   *
   * @param {Object} progress - Goal progress object
   * @returns {string} Motivational message
   */
  function getProgressMessage(progress) {
    if (!progress.enabled) {
      return 'Daily goals are disabled';
    }

    if (progress.isComplete) {
      return '🎉 Daily goal complete! Great job!';
    }

    const { percentage, remaining } = progress;

    if (percentage === 0) {
      return `Start your ${progress.target}-card goal!`;
    } else if (percentage < 25) {
      return `${remaining} cards to go - you've got this!`;
    } else if (percentage < 50) {
      return `Making progress! ${remaining} cards remaining.`;
    } else if (percentage < 75) {
      return `Halfway there! Only ${remaining} more cards.`;
    } else {
      return `Almost done! Just ${remaining} cards left!`;
    }
  }

  /**
   * Format goal for display
   *
   * @param {Object} progress - Goal progress object
   * @returns {string} Formatted string like "15/20"
   */
  function formatGoalProgress(progress) {
    return `${progress.completed}/${progress.target}`;
  }

  /**
   * Get goal preset options for UI
   *
   * @param {number} currentGoal - Currently selected goal
   * @returns {Array} Array of { value, label, selected } objects
   */
  function getGoalPresets(currentGoal) {
    return GOAL_PRESETS.map(value => ({
      value,
      label: `${value} cards`,
      selected: value === currentGoal
    }));
  }

  // ============================================
  // Goal Analytics
  // ============================================

  /**
   * Get goal completion stats from daily history
   *
   * @param {Object} schema - Full schema object
   * @param {number} days - Number of days to analyze (default 30)
   * @returns {Object} { totalDays, daysCompleted, completionRate, currentStreak }
   */
  function getGoalCompletionStats(schema, days = 30) {
    if (!schema || !schema.stats || !schema.stats.daily_history) {
      return {
        totalDays: 0,
        daysCompleted: 0,
        completionRate: 0,
        currentStreak: 0
      };
    }

    const history = schema.stats.daily_history;
    const target = schema.settings?.daily_goal?.target_cards || GOAL_DEFAULT;

    const today = new Date();
    let daysCompleted = 0;
    let currentStreak = 0;
    let streakBroken = false;

    for (let i = 0; i < days; i++) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      const dateStr = date.toLocaleDateString('en-CA');

      const dayData = history[dateStr];
      if (dayData) {
        const completed = (dayData.reviews || 0) + (dayData.new_cards || 0);
        if (completed >= target) {
          daysCompleted++;
          if (!streakBroken) {
            currentStreak++;
          }
        } else {
          streakBroken = true;
        }
      } else {
        streakBroken = true;
      }
    }

    const completionRate = days > 0 ? Math.round((daysCompleted / days) * 100) : 0;

    return {
      totalDays: days,
      daysCompleted,
      completionRate,
      currentStreak
    };
  }

  // ============================================
  // Public API
  // ============================================

  return {
    // Constants
    GOAL_MIN,
    GOAL_MAX,
    GOAL_DEFAULT,
    GOAL_PRESETS,
    GOAL_COMPLETION_BONUS,

    // Goal Setting
    setDailyGoal,
    setGoalEnabled,
    getGoalSettings,

    // Goal Progress
    getGoalProgress,
    checkGoalCompletion,
    markGoalCompleted,

    // Notifications
    isNotificationSupported,
    getNotificationPermission,
    requestNotificationPermission,
    setNotificationSettings,
    scheduleReminder,
    showReminderNotification,
    cancelReminder,

    // Display Helpers
    getProgressColor,
    getProgressMessage,
    formatGoalProgress,
    getGoalPresets,

    // Analytics
    getGoalCompletionStats
  };
})();

// Export for browser use
if (typeof window !== 'undefined') {
  window.GoalsManager = GoalsManager;
}

// Export for Node.js/CommonJS
if (typeof module !== 'undefined' && module.exports) {
  module.exports = GoalsManager;
}
