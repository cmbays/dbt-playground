#!/usr/bin/env node
/**
 * PM Sessions Tracker
 *
 * Manages session lifecycle for PM orchestration across multiple worktrees.
 * Provides heartbeat monitoring and stale session detection.
 *
 * @fileoverview Session management for Hybrid Lite PM Orchestration
 * @version 1.0.0
 *
 * Session Schema (TypeScript interface for reference):
 * @typedef {Object} Session
 * @property {string} session_id - UUID v4 identifier
 * @property {string} worktree - Absolute path to worktree
 * @property {string} branch - Current git branch name
 * @property {number|null} pr_number - Linked PR number
 * @property {string|null} pr_status - draft | pending | approved
 * @property {string} last_heartbeat - ISO 8601 timestamp
 * @property {string[]} claimed_tasks - Array of TASK-IDs
 * @property {'active'|'stale'|'ended'} status - Session status
 * @property {string} started_at - ISO 8601 timestamp
 * @property {string|null} ended_at - ISO 8601 timestamp
 *
 * Sessions File Schema:
 * @typedef {Object} SessionsFile
 * @property {string} version - Schema version (e.g., "1.0.0")
 * @property {string} last_cleanup - ISO 8601 timestamp of last cleanup
 * @property {Session[]} sessions - Array of session objects
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { execSync } = require('child_process');

/** Path to the PM_SESSIONS.json file */
const SESSIONS_FILE = path.join(__dirname, '../temp/PM_SESSIONS.json');

/** Stale threshold: 5 minutes in milliseconds */
const STALE_THRESHOLD_MS = 5 * 60 * 1000;

/** Heartbeat interval: 60 seconds */
const HEARTBEAT_INTERVAL_MS = 60 * 1000;

/**
 * Initialize sessions file if it doesn't exist
 * @returns {void}
 */
function initSessionsFile() {
  if (!fs.existsSync(SESSIONS_FILE)) {
    const initial = {
      version: '1.0.0',
      last_cleanup: new Date().toISOString(),
      sessions: []
    };
    // Ensure temp directory exists
    const tempDir = path.dirname(SESSIONS_FILE);
    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir, { recursive: true });
    }
    fs.writeFileSync(SESSIONS_FILE, JSON.stringify(initial, null, 2));
  }
}

/**
 * Read sessions from file
 * @returns {SessionsFile} The sessions data
 */
function readSessions() {
  initSessionsFile();
  try {
    const data = fs.readFileSync(SESSIONS_FILE, 'utf-8');
    return JSON.parse(data);
  } catch (error) {
    console.error('Error reading sessions file:', error.message);
    // Return empty structure on corruption
    return {
      version: '1.0.0',
      last_cleanup: new Date().toISOString(),
      sessions: []
    };
  }
}

/**
 * Write sessions to file
 * @param {SessionsFile} data - The sessions data to write
 * @returns {void}
 */
function writeSessions(data) {
  try {
    fs.writeFileSync(SESSIONS_FILE, JSON.stringify(data, null, 2));
  } catch (error) {
    console.error('Error writing sessions file:', error.message);
    throw error;
  }
}

/**
 * Get current git branch name
 * @returns {string} The current branch name
 */
function getCurrentBranch() {
  try {
    return execSync('git branch --show-current', { encoding: 'utf-8' }).trim();
  } catch (error) {
    return 'unknown';
  }
}

/**
 * Get PR information for current branch
 * @returns {{number: number|null, status: string|null}} PR info
 */
function getPRInfo() {
  try {
    const prInfo = JSON.parse(
      execSync('gh pr view --json number,state', { encoding: 'utf-8' })
    );
    return {
      number: prInfo.number ?? null,
      status: prInfo.state?.toLowerCase() ?? null
    };
  } catch (error) {
    // No PR linked or gh CLI not available
    return { number: null, status: null };
  }
}

/**
 * Register a new session
 * @param {Object} options - Optional overrides
 * @param {string} [options.worktree] - Override worktree path
 * @param {string} [options.branch] - Override branch name
 * @returns {string} The new session ID
 */
function registerSession(options = {}) {
  const sessionId = crypto.randomUUID();
  const worktree = options.worktree ?? process.cwd();
  const branch = options.branch ?? getCurrentBranch();
  const prInfo = getPRInfo();

  const data = readSessions();

  // Check for existing active session in same worktree
  const existingSession = data.sessions.find(
    s => s.worktree === worktree && s.status === 'active'
  );

  if (existingSession) {
    console.warn(`Warning: Active session already exists for ${worktree}`);
    console.warn(`Existing session: ${existingSession.session_id}`);
    // End the existing session
    existingSession.status = 'ended';
    existingSession.ended_at = new Date().toISOString();
  }

  const session = {
    session_id: sessionId,
    worktree,
    branch,
    pr_number: prInfo.number,
    pr_status: prInfo.status,
    last_heartbeat: new Date().toISOString(),
    claimed_tasks: [],
    status: 'active',
    started_at: new Date().toISOString(),
    ended_at: null
  };

  data.sessions.push(session);
  writeSessions(data);

  console.log(`Session registered: ${sessionId}`);
  return sessionId;
}

/**
 * Update heartbeat for a session
 * @param {string} sessionId - The session ID to update
 * @returns {boolean} True if session was found and updated
 */
function updateHeartbeat(sessionId) {
  const data = readSessions();
  const session = data.sessions.find(s => s.session_id === sessionId);

  if (session) {
    session.last_heartbeat = new Date().toISOString();
    // Restore active status if was stale
    if (session.status === 'stale') {
      session.status = 'active';
      console.log(`Session ${sessionId} restored from stale to active`);
    }
    writeSessions(data);
    return true;
  }

  console.warn(`Session not found: ${sessionId}`);
  return false;
}

/**
 * End a session
 * @param {string} sessionId - The session ID to end
 * @returns {boolean} True if session was found and ended
 */
function endSession(sessionId) {
  const data = readSessions();
  const session = data.sessions.find(s => s.session_id === sessionId);

  if (session) {
    session.status = 'ended';
    session.ended_at = new Date().toISOString();
    writeSessions(data);
    console.log(`Session ended: ${sessionId}`);
    return true;
  }

  console.warn(`Session not found: ${sessionId}`);
  return false;
}

/**
 * Detect and mark stale sessions
 * Sessions without heartbeat for more than STALE_THRESHOLD_MS are marked stale
 * @returns {Session[]} Array of sessions that were marked stale
 */
function detectStaleSessions() {
  const data = readSessions();
  const now = Date.now();
  const staleSessions = [];

  data.sessions.forEach(session => {
    if (session.status !== 'active') return;

    const lastHeartbeat = new Date(session.last_heartbeat).getTime();
    const timeSinceHeartbeat = now - lastHeartbeat;

    if (timeSinceHeartbeat > STALE_THRESHOLD_MS) {
      session.status = 'stale';
      staleSessions.push({ ...session });
    }
  });

  if (staleSessions.length > 0) {
    writeSessions(data);
  }

  return staleSessions;
}

/**
 * Claim a task for a session
 * @param {string} sessionId - The session ID
 * @param {string} taskId - The task ID to claim (e.g., "TASK-5")
 * @returns {boolean} True if task was claimed successfully
 */
function claimTask(sessionId, taskId) {
  const data = readSessions();
  const session = data.sessions.find(s => s.session_id === sessionId);

  if (!session) {
    console.warn(`Session not found: ${sessionId}`);
    return false;
  }

  if (session.status !== 'active') {
    console.warn(`Cannot claim task: session ${sessionId} is ${session.status}`);
    return false;
  }

  // Check if task is already claimed by another session
  const existingClaim = data.sessions.find(
    s => s.status === 'active' &&
         s.session_id !== sessionId &&
         s.claimed_tasks.includes(taskId)
  );

  if (existingClaim) {
    console.warn(`Task ${taskId} is already claimed by session ${existingClaim.session_id}`);
    return false;
  }

  if (!session.claimed_tasks.includes(taskId)) {
    session.claimed_tasks.push(taskId);
    writeSessions(data);
    console.log(`Task ${taskId} claimed by session ${sessionId}`);
  }

  return true;
}

/**
 * Release a task from a session
 * @param {string} sessionId - The session ID
 * @param {string} taskId - The task ID to release
 * @returns {boolean} True if task was released successfully
 */
function releaseTask(sessionId, taskId) {
  const data = readSessions();
  const session = data.sessions.find(s => s.session_id === sessionId);

  if (!session) {
    console.warn(`Session not found: ${sessionId}`);
    return false;
  }

  const initialLength = session.claimed_tasks.length;
  session.claimed_tasks = session.claimed_tasks.filter(id => id !== taskId);

  if (session.claimed_tasks.length < initialLength) {
    writeSessions(data);
    console.log(`Task ${taskId} released from session ${sessionId}`);
    return true;
  }

  console.warn(`Task ${taskId} was not claimed by session ${sessionId}`);
  return false;
}

/**
 * Cleanup old sessions (keep last 30 days)
 * @returns {number} Number of sessions removed
 */
function cleanupOldSessions() {
  const data = readSessions();
  const thirtyDaysAgo = Date.now() - (30 * 24 * 60 * 60 * 1000);
  const initialCount = data.sessions.length;

  data.sessions = data.sessions.filter(session => {
    const sessionTime = new Date(session.started_at).getTime();
    return sessionTime > thirtyDaysAgo;
  });

  const removedCount = initialCount - data.sessions.length;
  data.last_cleanup = new Date().toISOString();
  writeSessions(data);

  if (removedCount > 0) {
    console.log(`Cleaned up ${removedCount} old sessions`);
  }

  return removedCount;
}

/**
 * Get active sessions
 * @returns {Session[]} Array of active sessions
 */
function getActiveSessions() {
  const data = readSessions();
  return data.sessions.filter(s => s.status === 'active');
}

/**
 * Get session by ID
 * @param {string} sessionId - The session ID
 * @returns {Session|null} The session or null if not found
 */
function getSession(sessionId) {
  const data = readSessions();
  return data.sessions.find(s => s.session_id === sessionId) ?? null;
}

/**
 * Start a heartbeat loop for a session
 * @param {string} sessionId - The session ID
 * @param {Function} [onStale] - Callback when stale sessions detected
 * @returns {NodeJS.Timer} The interval timer (call clearInterval to stop)
 */
function startHeartbeat(sessionId, onStale = null) {
  return setInterval(() => {
    updateHeartbeat(sessionId);

    const staleSessions = detectStaleSessions();
    if (staleSessions.length > 0 && onStale) {
      onStale(staleSessions);
    }
  }, HEARTBEAT_INTERVAL_MS);
}

// Export functions for module usage
module.exports = {
  // Core functions
  registerSession,
  updateHeartbeat,
  endSession,
  detectStaleSessions,
  claimTask,
  releaseTask,
  cleanupOldSessions,

  // Helper functions
  readSessions,
  writeSessions,
  getActiveSessions,
  getSession,
  startHeartbeat,

  // Constants (for testing)
  SESSIONS_FILE,
  STALE_THRESHOLD_MS,
  HEARTBEAT_INTERVAL_MS
};

// CLI usage
if (require.main === module) {
  const command = process.argv[2];
  const arg1 = process.argv[3];
  const arg2 = process.argv[4];

  switch (command) {
    case 'register':
      registerSession();
      break;

    case 'heartbeat':
      if (!arg1) {
        console.error('Usage: pm_sessions.js heartbeat <sessionId>');
        process.exit(1);
      }
      updateHeartbeat(arg1);
      break;

    case 'end':
      if (!arg1) {
        console.error('Usage: pm_sessions.js end <sessionId>');
        process.exit(1);
      }
      endSession(arg1);
      break;

    case 'check-stale':
      const stale = detectStaleSessions();
      console.log(`Stale sessions: ${stale.length}`);
      stale.forEach(s => console.log(`  - ${s.session_id} (${s.branch})`));
      break;

    case 'claim':
      if (!arg1 || !arg2) {
        console.error('Usage: pm_sessions.js claim <sessionId> <taskId>');
        process.exit(1);
      }
      claimTask(arg1, arg2);
      break;

    case 'release':
      if (!arg1 || !arg2) {
        console.error('Usage: pm_sessions.js release <sessionId> <taskId>');
        process.exit(1);
      }
      releaseTask(arg1, arg2);
      break;

    case 'cleanup':
      cleanupOldSessions();
      console.log('Cleanup complete');
      break;

    case 'list':
      const data = readSessions();
      console.log(JSON.stringify(data, null, 2));
      break;

    case 'active':
      const active = getActiveSessions();
      console.log(`Active sessions: ${active.length}`);
      active.forEach(s => {
        console.log(`  - ${s.session_id}`);
        console.log(`    Branch: ${s.branch}`);
        console.log(`    Worktree: ${s.worktree}`);
        console.log(`    Tasks: ${s.claimed_tasks.join(', ') || 'none'}`);
      });
      break;

    default:
      console.log(`PM Sessions Manager v1.0.0

Usage: pm_sessions.js <command> [args]

Commands:
  register              Register a new session for current worktree
  heartbeat <id>        Update heartbeat for session
  end <id>              End a session
  check-stale           Detect and mark stale sessions
  claim <id> <task>     Claim a task for a session
  release <id> <task>   Release a task from a session
  cleanup               Remove sessions older than 30 days
  list                  List all sessions (JSON)
  active                List active sessions (formatted)

Configuration:
  Stale threshold: ${STALE_THRESHOLD_MS / 1000 / 60} minutes
  Heartbeat interval: ${HEARTBEAT_INTERVAL_MS / 1000} seconds
  Sessions file: ${SESSIONS_FILE}
`);
  }
}
