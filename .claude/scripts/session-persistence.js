#!/usr/bin/env node
/**
 * Session Persistence
 *
 * Cross-platform utility to save and restore Claude session context.
 * Useful for maintaining state between Claude sessions.
 *
 * Usage:
 *   node .claude/scripts/session-persistence.js save "context description"
 *   node .claude/scripts/session-persistence.js load
 *   node .claude/scripts/session-persistence.js list
 *   node .claude/scripts/session-persistence.js clear
 *
 * Stores:
 *   - Current working files
 *   - Last task context
 *   - Open questions
 *   - Session notes
 */

const fs = require('fs');
const path = require('path');

const SESSION_DIR = path.join(process.cwd(), '.claude', 'sessions');
const CURRENT_SESSION = path.join(SESSION_DIR, 'current.json');
const MAX_SESSIONS = 10;

/**
 * Ensure sessions directory exists
 */
function ensureSessionDir() {
  if (!fs.existsSync(SESSION_DIR)) {
    fs.mkdirSync(SESSION_DIR, { recursive: true });
  }
}

/**
 * Get current git branch
 */
function getCurrentBranch() {
  try {
    const { execSync } = require('child_process');
    return execSync('git rev-parse --abbrev-ref HEAD', {
      encoding: 'utf8',
      stdio: ['pipe', 'pipe', 'ignore']
    }).trim();
  } catch {
    return 'unknown';
  }
}

/**
 * Get modified files
 */
function getModifiedFiles() {
  try {
    const { execSync } = require('child_process');
    const output = execSync('git status --porcelain', {
      encoding: 'utf8',
      stdio: ['pipe', 'pipe', 'ignore']
    });
    return output.trim().split('\n').filter(Boolean).map(line => ({
      status: line.substring(0, 2).trim(),
      file: line.substring(3)
    }));
  } catch {
    return [];
  }
}

/**
 * Get temp folder contents
 */
function getTempContents() {
  const tempDir = path.join(process.cwd(), 'temp');
  if (!fs.existsSync(tempDir)) {
    return [];
  }
  return fs.readdirSync(tempDir).filter(f => !f.startsWith('.'));
}

/**
 * Save current session
 */
function saveSession(description) {
  ensureSessionDir();

  const session = {
    id: Date.now(),
    timestamp: new Date().toISOString(),
    description: description || 'No description',
    branch: getCurrentBranch(),
    modifiedFiles: getModifiedFiles(),
    tempContents: getTempContents(),
    cwd: process.cwd()
  };

  // Archive current session if exists
  if (fs.existsSync(CURRENT_SESSION)) {
    const current = JSON.parse(fs.readFileSync(CURRENT_SESSION, 'utf8'));
    const archivePath = path.join(SESSION_DIR, `session-${current.id}.json`);
    fs.writeFileSync(archivePath, JSON.stringify(current, null, 2));

    // Cleanup old sessions
    cleanupOldSessions();
  }

  // Save new current session
  fs.writeFileSync(CURRENT_SESSION, JSON.stringify(session, null, 2));

  console.log('Session saved:');
  console.log(JSON.stringify(session, null, 2));
}

/**
 * Load current session
 */
function loadSession() {
  if (!fs.existsSync(CURRENT_SESSION)) {
    console.log('No session found.');
    return null;
  }

  const session = JSON.parse(fs.readFileSync(CURRENT_SESSION, 'utf8'));

  console.log('=== Session Context ===');
  console.log(`Saved: ${session.timestamp}`);
  console.log(`Branch: ${session.branch}`);
  console.log(`Description: ${session.description}`);
  console.log('');

  if (session.modifiedFiles.length > 0) {
    console.log('Modified files:');
    session.modifiedFiles.forEach(f => {
      console.log(`  [${f.status}] ${f.file}`);
    });
    console.log('');
  }

  if (session.tempContents.length > 0) {
    console.log('Files in temp/:');
    session.tempContents.forEach(f => {
      console.log(`  - ${f}`);
    });
    console.log('');
  }

  console.log('=== Resume Context ===');
  console.log(`To continue work, you were on branch "${session.branch}"`);
  if (session.modifiedFiles.length > 0) {
    console.log(`with ${session.modifiedFiles.length} uncommitted changes.`);
  }

  return session;
}

/**
 * List all sessions
 */
function listSessions() {
  ensureSessionDir();

  const files = fs.readdirSync(SESSION_DIR)
    .filter(f => f.endsWith('.json'))
    .sort()
    .reverse();

  if (files.length === 0) {
    console.log('No sessions found.');
    return;
  }

  console.log('Saved sessions:');
  files.forEach(f => {
    const session = JSON.parse(fs.readFileSync(path.join(SESSION_DIR, f), 'utf8'));
    const isCurrent = f === 'current.json' ? ' (current)' : '';
    console.log(`  ${session.timestamp}${isCurrent}`);
    console.log(`    Branch: ${session.branch}`);
    console.log(`    Description: ${session.description}`);
    console.log('');
  });
}

/**
 * Clear all sessions
 */
function clearSessions() {
  if (!fs.existsSync(SESSION_DIR)) {
    console.log('No sessions to clear.');
    return;
  }

  const files = fs.readdirSync(SESSION_DIR).filter(f => f.endsWith('.json'));
  files.forEach(f => {
    fs.unlinkSync(path.join(SESSION_DIR, f));
  });

  console.log(`Cleared ${files.length} session(s).`);
}

/**
 * Cleanup old sessions beyond MAX_SESSIONS
 */
function cleanupOldSessions() {
  const files = fs.readdirSync(SESSION_DIR)
    .filter(f => f.startsWith('session-') && f.endsWith('.json'))
    .sort()
    .reverse();

  if (files.length > MAX_SESSIONS) {
    const toDelete = files.slice(MAX_SESSIONS);
    toDelete.forEach(f => {
      fs.unlinkSync(path.join(SESSION_DIR, f));
    });
  }
}

/**
 * Main function
 */
function main() {
  const args = process.argv.slice(2);
  const command = args[0] || 'load';

  switch (command) {
    case 'save':
      saveSession(args.slice(1).join(' '));
      break;
    case 'load':
      loadSession();
      break;
    case 'list':
      listSessions();
      break;
    case 'clear':
      clearSessions();
      break;
    default:
      console.log('Usage:');
      console.log('  node session-persistence.js save "description"');
      console.log('  node session-persistence.js load');
      console.log('  node session-persistence.js list');
      console.log('  node session-persistence.js clear');
      process.exit(1);
  }
}

main();
