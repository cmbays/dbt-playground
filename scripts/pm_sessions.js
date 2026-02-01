#!/usr/bin/env node
/**
 * PM Sessions Tracker - Refactored v2.0.0
 *
 * Manages session lifecycle for PM orchestration across multiple worktrees.
 * Provides heartbeat monitoring and stale session detection.
 *
 * Improvements in v2.0.0:
 * - Atomic writes with file locking (prevents corruption)
 * - Async git/gh operations (non-blocking)
 * - Schema validation (data integrity)
 * - DRY abstraction (updateSession pattern)
 * - Commander CLI (better arg parsing)
 * - Shared config (eliminates magic numbers)
 *
 * @fileoverview Session management for Hybrid Lite PM Orchestration
 * @version 2.0.0
 */

const fs = require('fs');
const { exec } = require('child_process');
const util = require('util');
const crypto = require('crypto');
const lockfile = require('proper-lockfile');
const { program } = require('commander');
const Ajv = require('ajv');
const addFormats = require('ajv-formats');

const config = require('./pm_config');

// Promisify exec for async git/gh operations
const execAsync = util.promisify(exec);

// Schema validator
const ajv = new Ajv({ allErrors: true });
addFormats(ajv);

const sessionSchema = {
  type: 'object',
  properties: {
    version: { type: 'string' },
    last_cleanup: { type: 'string', format: 'date-time' },
    sessions: {
      type: 'array',
      items: {
        type: 'object',
        required: ['session_id', 'worktree', 'branch', 'status', 'started_at'],
        properties: {
          session_id: { type: 'string' },
          worktree: { type: 'string' },
          branch: { type: 'string' },
          pr_number: { type: ['number', 'null'] },
          pr_status: { type: ['string', 'null'] },
          last_heartbeat: { type: 'string', format: 'date-time' },
          claimed_tasks: { type: 'array', items: { type: 'string' } },
          status: { enum: config.SESSION_STATUSES },
          started_at: { type: 'string', format: 'date-time' },
          ended_at: { type: ['string', 'null'], format: 'date-time' }
        }
      }
    }
  },
  required: ['version', 'sessions']
};

const validate = ajv.compile(sessionSchema);

/**
 * Get default sessions file structure
 * @returns {Object} Default sessions data
 */
function getDefaultSessionsFile() {
  return {
    version: config.SCHEMA_VERSION,
    last_cleanup: new Date().toISOString(),
    sessions: []
  };
}

/**
 * Initialize sessions file if it doesn't exist
 * @returns {void}
 */
function initSessionsFile() {
  if (!fs.existsSync(config.SESSIONS_FILE)) {
    const tempDir = require('path').dirname(config.SESSIONS_FILE);
    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir, { recursive: true });
    }
    writeSessionsSync(getDefaultSessionsFile());
  }
}

/**
 * Read sessions from file with validation
 * @returns {Object} The sessions data
 */
function readSessions() {
  initSessionsFile();

  try {
    const data = fs.readFileSync(config.SESSIONS_FILE, 'utf-8');
    const parsed = JSON.parse(data);

    if (!validate(parsed)) {
      console.error('Invalid sessions file schema:', validate.errors);
      console.warn('Resetting to default sessions file');
      return getDefaultSessionsFile();
    }

    return parsed;
  } catch (error) {
    console.error('Error reading sessions file:', error.message);
    return getDefaultSessionsFile();
  }
}

/**
 * Write sessions to file with atomic write (prevents corruption)
 * Uses temporary file + rename for atomicity
 * @param {Object} data - The sessions data to write
 * @returns {void}
 */
function writeSessionsSync(data) {
  const tmpFile = config.SESSIONS_FILE + '.tmp';

  try {
    // Write to temp file first
    fs.writeFileSync(tmpFile, JSON.stringify(data, null, 2));

    // Atomic rename (POSIX guarantees atomicity)
    fs.renameSync(tmpFile, config.SESSIONS_FILE);
  } catch (error) {
    console.error('Error writing sessions file:', error.message);
    // Clean up temp file if exists
    if (fs.existsSync(tmpFile)) {
      fs.unlinkSync(tmpFile);
    }
    throw error;
  }
}

/**
 * Async wrapper for writeSessionsSync
 * @param {Object} data - The sessions data to write
 * @returns {Promise<void>}
 */
async function writeSessions(data) {
  return writeSessionsSync(data);
}

/**
 * Execute function with file lock to prevent concurrent modifications
 * @param {Function} fn - Function to execute with lock
 * @returns {Promise<any>} Result of fn
 */
async function withLock(fn) {
  initSessionsFile();

  let release;
  try {
    // Acquire lock with 10s timeout
    release = await lockfile.lock(config.SESSIONS_FILE, {
      retries: {
        retries: 5,
        minTimeout: 100,
        maxTimeout: 1000
      }
    });

    return await fn();
  } finally {
    if (release) {
      await release();
    }
  }
}

/**
 * Generic session update function (DRY abstraction)
 * @param {string} sessionId - The session ID to update
 * @param {Function} updateFn - Function to apply updates (session, data) => boolean
 * @returns {Promise<boolean>} True if update succeeded
 */
async function updateSession(sessionId, updateFn) {
  return withLock(async () => {
    const data = readSessions();
    const session = data.sessions.find(s => s.session_id === sessionId);

    if (!session) {
      console.warn(`Session not found: ${sessionId}`);
      return false;
    }

    const result = await updateFn(session, data);

    if (result) {
      writeSessionsSync(data);
    }

    return result;
  });
}

/**
 * Get current git branch name (async)
 * @returns {Promise<string>} The current branch name
 */
async function getCurrentBranch() {
  try {
    const { stdout } = await execAsync('git branch --show-current', { timeout: 5000 });
    return stdout.trim();
  } catch (error) {
    return 'unknown';
  }
}

/**
 * Get PR information for current branch (async)
 * @returns {Promise<{number: number|null, status: string|null}>} PR info
 */
async function getPRInfo() {
  try {
    const { stdout } = await execAsync('gh pr view --json number,state', { timeout: 5000 });
    const prInfo = JSON.parse(stdout);
    return {
      number: prInfo.number ?? null,
      status: prInfo.state?.toLowerCase() ?? null
    };
  } catch (error) {
    return { number: null, status: null };
  }
}

/**
 * Register a new session
 * @param {Object} options - Optional overrides
 * @param {string} [options.worktree] - Override worktree path
 * @param {string} [options.branch] - Override branch name
 * @returns {Promise<string>} The new session ID
 */
async function registerSession(options = {}) {
  return withLock(async () => {
    const sessionId = crypto.randomUUID();
    const worktree = options.worktree ?? process.cwd();
    const branch = options.branch ?? await getCurrentBranch();
    const prInfo = await getPRInfo();

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
    writeSessionsSync(data);

    console.log(`Session registered: ${sessionId}`);
    return sessionId;
  });
}

/**
 * Update heartbeat for a session
 * @param {string} sessionId - The session ID to update
 * @returns {Promise<boolean>} True if session was found and updated
 */
async function updateHeartbeat(sessionId) {
  return updateSession(sessionId, async (session) => {
    session.last_heartbeat = new Date().toISOString();

    // Restore active status if was stale
    if (session.status === 'stale') {
      session.status = 'active';
      console.log(`Session ${sessionId} restored from stale to active`);
    }

    return true;
  });
}

/**
 * End a session
 * @param {string} sessionId - The session ID to end
 * @returns {Promise<boolean>} True if session was found and ended
 */
async function endSession(sessionId) {
  return updateSession(sessionId, async (session) => {
    session.status = 'ended';
    session.ended_at = new Date().toISOString();
    console.log(`Session ended: ${sessionId}`);
    return true;
  });
}

/**
 * Detect and mark stale sessions
 * @returns {Promise<Array>} Array of sessions that were marked stale
 */
async function detectStaleSessions() {
  return withLock(async () => {
    const data = readSessions();
    const now = Date.now();
    const staleSessions = [];

    data.sessions.forEach(session => {
      if (session.status !== 'active') return;

      const lastHeartbeat = new Date(session.last_heartbeat).getTime();
      const timeSinceHeartbeat = now - lastHeartbeat;

      if (timeSinceHeartbeat > config.STALE_THRESHOLD_MS) {
        session.status = 'stale';
        staleSessions.push({ ...session });
      }
    });

    if (staleSessions.length > 0) {
      writeSessionsSync(data);
    }

    return staleSessions;
  });
}

/**
 * Claim a task for a session
 * @param {string} sessionId - The session ID
 * @param {string} taskId - The task ID to claim
 * @returns {Promise<boolean>} True if task was claimed successfully
 */
async function claimTask(sessionId, taskId) {
  return updateSession(sessionId, async (session, data) => {
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
      console.log(`Task ${taskId} claimed by session ${sessionId}`);
    }

    return true;
  });
}

/**
 * Release a task from a session
 * @param {string} sessionId - The session ID
 * @param {string} taskId - The task ID to release
 * @returns {Promise<boolean>} True if task was released successfully
 */
async function releaseTask(sessionId, taskId) {
  return updateSession(sessionId, async (session) => {
    const initialLength = session.claimed_tasks.length;
    session.claimed_tasks = session.claimed_tasks.filter(id => id !== taskId);

    if (session.claimed_tasks.length < initialLength) {
      console.log(`Task ${taskId} released from session ${sessionId}`);
      return true;
    }

    console.warn(`Task ${taskId} was not claimed by session ${sessionId}`);
    return false;
  });
}

/**
 * Cleanup old sessions (keep last N days from config)
 * @returns {Promise<number>} Number of sessions removed
 */
async function cleanupOldSessions() {
  return withLock(async () => {
    const data = readSessions();
    const retentionMs = config.CLEANUP_RETENTION_DAYS * 24 * 60 * 60 * 1000;
    const cutoffTime = Date.now() - retentionMs;
    const initialCount = data.sessions.length;

    data.sessions = data.sessions.filter(session => {
      const sessionTime = new Date(session.started_at).getTime();
      return sessionTime > cutoffTime;
    });

    const removedCount = initialCount - data.sessions.length;
    data.last_cleanup = new Date().toISOString();
    writeSessionsSync(data);

    if (removedCount > 0) {
      console.log(`Cleaned up ${removedCount} old sessions`);
    }

    return removedCount;
  });
}

/**
 * Get active sessions
 * @returns {Array} Array of active sessions
 */
function getActiveSessions() {
  const data = readSessions();
  return data.sessions.filter(s => s.status === 'active');
}

/**
 * Get session by ID
 * @param {string} sessionId - The session ID
 * @returns {Object|null} The session or null if not found
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
  return setInterval(async () => {
    await updateHeartbeat(sessionId);

    const staleSessions = await detectStaleSessions();
    if (staleSessions.length > 0 && onStale) {
      onStale(staleSessions);
    }
  }, config.HEARTBEAT_INTERVAL_MS);
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

  // Config (for testing)
  config,

  // For backwards compatibility
  SESSIONS_FILE: config.SESSIONS_FILE,
  STALE_THRESHOLD_MS: config.STALE_THRESHOLD_MS,
  HEARTBEAT_INTERVAL_MS: config.HEARTBEAT_INTERVAL_MS
};

// CLI using Commander
if (require.main === module) {
  program
    .name('pm_sessions')
    .description('PM Sessions Manager - Session lifecycle management for PM Orchestration')
    .version('2.0.0');

  program
    .command('register')
    .description('Register a new session for current worktree')
    .action(async () => {
      try {
        await registerSession();
      } catch (error) {
        console.error('Error:', error.message);
        process.exit(1);
      }
    });

  program
    .command('heartbeat <sessionId>')
    .description('Update heartbeat for session')
    .action(async (sessionId) => {
      try {
        const success = await updateHeartbeat(sessionId);
        if (!success) process.exit(1);
      } catch (error) {
        console.error('Error:', error.message);
        process.exit(1);
      }
    });

  program
    .command('end <sessionId>')
    .description('End a session')
    .action(async (sessionId) => {
      try {
        const success = await endSession(sessionId);
        if (!success) process.exit(1);
      } catch (error) {
        console.error('Error:', error.message);
        process.exit(1);
      }
    });

  program
    .command('check-stale')
    .description('Detect and mark stale sessions')
    .action(async () => {
      try {
        const stale = await detectStaleSessions();
        console.log(`Stale sessions: ${stale.length}`);
        stale.forEach(s => console.log(`  - ${s.session_id} (${s.branch})`));
      } catch (error) {
        console.error('Error:', error.message);
        process.exit(1);
      }
    });

  program
    .command('claim <sessionId> <taskId>')
    .description('Claim a task for a session')
    .action(async (sessionId, taskId) => {
      try {
        const success = await claimTask(sessionId, taskId);
        if (!success) process.exit(1);
      } catch (error) {
        console.error('Error:', error.message);
        process.exit(1);
      }
    });

  program
    .command('release <sessionId> <taskId>')
    .description('Release a task from a session')
    .action(async (sessionId, taskId) => {
      try {
        const success = await releaseTask(sessionId, taskId);
        if (!success) process.exit(1);
      } catch (error) {
        console.error('Error:', error.message);
        process.exit(1);
      }
    });

  program
    .command('cleanup')
    .description(`Remove sessions older than ${config.CLEANUP_RETENTION_DAYS} days`)
    .action(async () => {
      try {
        await cleanupOldSessions();
        console.log('Cleanup complete');
      } catch (error) {
        console.error('Error:', error.message);
        process.exit(1);
      }
    });

  program
    .command('list')
    .description('List all sessions (JSON)')
    .action(() => {
      try {
        const data = readSessions();
        console.log(JSON.stringify(data, null, 2));
      } catch (error) {
        console.error('Error:', error.message);
        process.exit(1);
      }
    });

  program
    .command('active')
    .description('List active sessions (formatted)')
    .action(() => {
      try {
        const active = getActiveSessions();
        console.log(`Active sessions: ${active.length}`);
        active.forEach(s => {
          console.log(`  - ${s.session_id}`);
          console.log(`    Branch: ${s.branch}`);
          console.log(`    Worktree: ${s.worktree}`);
          console.log(`    Tasks: ${s.claimed_tasks.join(', ') || 'none'}`);
        });
      } catch (error) {
        console.error('Error:', error.message);
        process.exit(1);
      }
    });

  program.parse();
}
