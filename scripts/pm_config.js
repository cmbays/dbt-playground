/**
 * PM Orchestration Configuration
 * Shared configuration between pm_sessions.js and workflow-hub widgets
 * @module pm_config
 */

const path = require('path');

module.exports = {
  // Session management
  STALE_THRESHOLD_MS: 5 * 60 * 1000,        // 5 minutes
  HEARTBEAT_INTERVAL_MS: 60 * 1000,         // 60 seconds
  WARNING_THRESHOLD_MS: 2 * 60 * 1000,      // 2 minutes (for UI)

  // Cleanup settings
  CLEANUP_RETENTION_DAYS: 30,                // Keep sessions for 30 days

  // File paths
  SESSIONS_FILE: path.join(__dirname, '../temp/PM_SESSIONS.json'),

  // API endpoints (for widgets)
  BACKLOG_API_BASE: 'http://localhost:6420/api',

  // Polling intervals (for widgets)
  WIDGET_POLL_INTERVAL_MS: 15 * 1000,       // 15 seconds
  MAX_RETRY_DELAY_MS: 60 * 1000,            // Max 60 seconds backoff

  // Session schema version
  SCHEMA_VERSION: '1.0.0',

  // Valid session statuses
  SESSION_STATUSES: ['active', 'stale', 'ended']
};
