#!/usr/bin/env node

/**
 * Stop Hook Notification for Claude Code
 * Sends a desktop notification when Claude finishes responding
 *
 * Works natively on macOS using osascript (AppleScript)
 */

const { execSync } = require('child_process');

try {
  // Send macOS notification
  const script = 'display notification "Claude has finished and is waiting for your input" with title "Claude Code" sound name "Glass"';

  execSync(`osascript -e '${script}'`, { stdio: 'ignore' });

} catch (error) {
  // Silent fail - don't disrupt Claude Code if notification fails
  console.error('Stop notification error:', error.message);
}
