#!/usr/bin/env node

/**
 * OS Notification Hook for Claude Code
 * Displays native desktop notifications when Claude sends notifications
 *
 * Receives notification data via stdin in JSON format
 * Works natively on macOS using osascript (AppleScript)
 */

const { execSync } = require('child_process');

// Read notification data from stdin
let notificationData = '';
process.stdin.on('data', (chunk) => {
  notificationData += chunk;
});

process.stdin.on('end', () => {
  try {
    // Parse the notification data
    const data = JSON.parse(notificationData);

    // Extract notification details
    const title = data.title || 'Claude Code';
    const message = data.message || 'Notification from Claude';
    const type = data.type || 'info'; // info, warning, error, success

    // Choose sound based on notification type
    const soundMap = {
      'info': 'default',
      'warning': 'Basso',
      'error': 'Sosumi',
      'success': 'Glass',
      'needsInput': 'Ping'
    };
    const sound = soundMap[type] || 'default';

    // Send macOS notification using osascript
    const script = `display notification "${escapeForAppleScript(message)}" with title "${escapeForAppleScript(title)}" sound name "${sound}"`;

    execSync(`osascript -e '${script}'`, { stdio: 'ignore' });

  } catch (error) {
    // Silent fail - don't disrupt Claude Code if notification fails
    console.error('Notification hook error:', error.message);
  }
});

/**
 * Escape special characters for AppleScript
 */
function escapeForAppleScript(str) {
  return str
    .replace(/\\/g, '\\\\')
    .replace(/"/g, '\\"')
    .replace(/\n/g, '\\n');
}
