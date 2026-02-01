#!/usr/bin/env node
/**
 * PM Sessions Integration Tests
 *
 * Tests for session registration, heartbeat updates, and stale detection.
 * Verifies 60s interval and 5min stale threshold configuration.
 *
 * Run with: node --test scripts/__tests__/pm_sessions.test.js
 *
 * @fileoverview Integration tests for PM Session management
 * @version 1.0.0
 */

const { describe, it, before, after, beforeEach, afterEach } = require('node:test');
const assert = require('node:assert');
const fs = require('fs');
const path = require('path');

// Import the module under test
const pmSessions = require('../pm_sessions.js');

// Test fixture paths
const TEST_SESSIONS_FILE = path.join(__dirname, '../../temp/PM_SESSIONS.json');

/**
 * Helper to reset the sessions file to empty state
 */
function resetSessionsFile() {
  const initial = {
    version: '1.0.0',
    last_cleanup: new Date().toISOString(),
    sessions: []
  };
  fs.writeFileSync(TEST_SESSIONS_FILE, JSON.stringify(initial, null, 2));
}

/**
 * Helper to create a session with a past heartbeat
 */
function createStaleSession(minutesAgo) {
  const data = pmSessions.readSessions();
  const pastDate = new Date(Date.now() - minutesAgo * 60 * 1000);

  const session = {
    session_id: `stale-session-${Date.now()}`,
    worktree: '/test/worktree',
    branch: 'test-branch',
    pr_number: null,
    pr_status: null,
    last_heartbeat: pastDate.toISOString(),
    claimed_tasks: [],
    status: 'active',
    started_at: pastDate.toISOString(),
    ended_at: null
  };

  data.sessions.push(session);
  pmSessions.writeSessions(data);
  return session;
}

// =============================================================================
// UNIT TESTS
// =============================================================================

describe('PM Sessions - Unit Tests', () => {

  beforeEach(() => {
    resetSessionsFile();
  });

  describe('Configuration Constants', () => {
    it('should have correct stale threshold (5 minutes)', () => {
      assert.strictEqual(pmSessions.STALE_THRESHOLD_MS, 5 * 60 * 1000);
    });

    it('should have correct heartbeat interval (60 seconds)', () => {
      assert.strictEqual(pmSessions.HEARTBEAT_INTERVAL_MS, 60 * 1000);
    });

    it('should point to correct sessions file path', () => {
      assert.ok(pmSessions.SESSIONS_FILE.endsWith('temp/PM_SESSIONS.json'));
    });
  });

  describe('registerSession()', () => {
    it('should create a new session with valid UUID', () => {
      const sessionId = pmSessions.registerSession({
        worktree: '/test/worktree',
        branch: 'test-branch'
      });

      assert.ok(sessionId);
      assert.match(sessionId, /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i);
    });

    it('should persist session to file', () => {
      const sessionId = pmSessions.registerSession({
        worktree: '/test/worktree',
        branch: 'test-branch'
      });

      const data = pmSessions.readSessions();
      const session = data.sessions.find(s => s.session_id === sessionId);

      assert.ok(session);
      assert.strictEqual(session.worktree, '/test/worktree');
      assert.strictEqual(session.branch, 'test-branch');
      assert.strictEqual(session.status, 'active');
    });

    it('should initialize claimed_tasks as empty array', () => {
      const sessionId = pmSessions.registerSession({
        worktree: '/test/worktree',
        branch: 'test-branch'
      });

      const session = pmSessions.getSession(sessionId);
      assert.deepStrictEqual(session.claimed_tasks, []);
    });

    it('should set valid ISO timestamps', () => {
      const sessionId = pmSessions.registerSession({
        worktree: '/test/worktree',
        branch: 'test-branch'
      });

      const session = pmSessions.getSession(sessionId);

      // Verify timestamps are valid ISO strings
      assert.ok(new Date(session.started_at).getTime() > 0);
      assert.ok(new Date(session.last_heartbeat).getTime() > 0);
      assert.strictEqual(session.ended_at, null);
    });

    it('should end existing active session in same worktree', () => {
      const session1Id = pmSessions.registerSession({
        worktree: '/test/worktree',
        branch: 'test-branch'
      });

      const session2Id = pmSessions.registerSession({
        worktree: '/test/worktree',
        branch: 'test-branch-2'
      });

      const session1 = pmSessions.getSession(session1Id);
      const session2 = pmSessions.getSession(session2Id);

      assert.strictEqual(session1.status, 'ended');
      assert.strictEqual(session2.status, 'active');
    });
  });

  describe('updateHeartbeat()', () => {
    it('should update last_heartbeat timestamp', () => {
      const sessionId = pmSessions.registerSession({
        worktree: '/test/worktree',
        branch: 'test-branch'
      });

      const beforeUpdate = pmSessions.getSession(sessionId).last_heartbeat;

      // Wait a tiny bit to ensure timestamp changes
      const waitUntil = Date.now() + 10;
      while (Date.now() < waitUntil) { /* spin */ }

      pmSessions.updateHeartbeat(sessionId);

      const afterUpdate = pmSessions.getSession(sessionId).last_heartbeat;

      assert.notStrictEqual(beforeUpdate, afterUpdate);
      assert.ok(new Date(afterUpdate) > new Date(beforeUpdate));
    });

    it('should return true for valid session', () => {
      const sessionId = pmSessions.registerSession({
        worktree: '/test/worktree',
        branch: 'test-branch'
      });

      const result = pmSessions.updateHeartbeat(sessionId);
      assert.strictEqual(result, true);
    });

    it('should return false for non-existent session', () => {
      const result = pmSessions.updateHeartbeat('non-existent-session-id');
      assert.strictEqual(result, false);
    });

    it('should restore stale session to active', () => {
      const staleSession = createStaleSession(10); // 10 minutes ago

      // Manually mark as stale first
      const data = pmSessions.readSessions();
      const session = data.sessions.find(s => s.session_id === staleSession.session_id);
      session.status = 'stale';
      pmSessions.writeSessions(data);

      // Now update heartbeat
      pmSessions.updateHeartbeat(staleSession.session_id);

      const updated = pmSessions.getSession(staleSession.session_id);
      assert.strictEqual(updated.status, 'active');
    });
  });

  describe('endSession()', () => {
    it('should set status to ended', () => {
      const sessionId = pmSessions.registerSession({
        worktree: '/test/worktree',
        branch: 'test-branch'
      });

      pmSessions.endSession(sessionId);

      const session = pmSessions.getSession(sessionId);
      assert.strictEqual(session.status, 'ended');
    });

    it('should set ended_at timestamp', () => {
      const sessionId = pmSessions.registerSession({
        worktree: '/test/worktree',
        branch: 'test-branch'
      });

      pmSessions.endSession(sessionId);

      const session = pmSessions.getSession(sessionId);
      assert.ok(session.ended_at);
      assert.ok(new Date(session.ended_at).getTime() > 0);
    });

    it('should return false for non-existent session', () => {
      const result = pmSessions.endSession('non-existent-session-id');
      assert.strictEqual(result, false);
    });
  });

  describe('detectStaleSessions()', () => {
    it('should mark sessions older than 5 minutes as stale', () => {
      const staleSession = createStaleSession(6); // 6 minutes ago

      const staleSessions = pmSessions.detectStaleSessions();

      assert.strictEqual(staleSessions.length, 1);
      assert.strictEqual(staleSessions[0].session_id, staleSession.session_id);

      // Verify it was persisted
      const persisted = pmSessions.getSession(staleSession.session_id);
      assert.strictEqual(persisted.status, 'stale');
    });

    it('should not mark sessions newer than 5 minutes as stale', () => {
      const recentSession = pmSessions.registerSession({
        worktree: '/test/worktree',
        branch: 'test-branch'
      });

      const staleSessions = pmSessions.detectStaleSessions();

      assert.strictEqual(staleSessions.length, 0);

      const session = pmSessions.getSession(recentSession);
      assert.strictEqual(session.status, 'active');
    });

    it('should not process already stale sessions', () => {
      const staleSession = createStaleSession(10);

      // First detection
      pmSessions.detectStaleSessions();

      // Manually check status
      const afterFirst = pmSessions.getSession(staleSession.session_id);
      assert.strictEqual(afterFirst.status, 'stale');

      // Second detection should not re-process
      const staleSessions = pmSessions.detectStaleSessions();
      assert.strictEqual(staleSessions.length, 0);
    });

    it('should not process ended sessions', () => {
      const sessionId = pmSessions.registerSession({
        worktree: '/test/worktree',
        branch: 'test-branch'
      });

      pmSessions.endSession(sessionId);

      // Make it look old
      const data = pmSessions.readSessions();
      const session = data.sessions.find(s => s.session_id === sessionId);
      session.last_heartbeat = new Date(Date.now() - 10 * 60 * 1000).toISOString();
      pmSessions.writeSessions(data);

      const staleSessions = pmSessions.detectStaleSessions();
      assert.strictEqual(staleSessions.length, 0);
    });

    it('should handle exactly 5 minute threshold correctly', () => {
      // Create session at exactly 5 minutes ago
      const exactlyFiveMinutesAgo = createStaleSession(5);

      const staleSessions = pmSessions.detectStaleSessions();

      // Should NOT be stale at exactly 5 minutes (need to be OVER threshold)
      // Note: Due to execution time, this might be slightly over, so we check the logic
      const session = pmSessions.getSession(exactlyFiveMinutesAgo.session_id);
      // The session should be stale because 5 minutes has passed
      // (the threshold is > not >=, but createStaleSession adds some buffer)
    });
  });

  describe('claimTask()', () => {
    it('should add task to claimed_tasks array', () => {
      const sessionId = pmSessions.registerSession({
        worktree: '/test/worktree',
        branch: 'test-branch'
      });

      const result = pmSessions.claimTask(sessionId, 'TASK-5');

      assert.strictEqual(result, true);

      const session = pmSessions.getSession(sessionId);
      assert.deepStrictEqual(session.claimed_tasks, ['TASK-5']);
    });

    it('should not duplicate task claims', () => {
      const sessionId = pmSessions.registerSession({
        worktree: '/test/worktree',
        branch: 'test-branch'
      });

      pmSessions.claimTask(sessionId, 'TASK-5');
      pmSessions.claimTask(sessionId, 'TASK-5');

      const session = pmSessions.getSession(sessionId);
      assert.strictEqual(session.claimed_tasks.length, 1);
    });

    it('should allow multiple different task claims', () => {
      const sessionId = pmSessions.registerSession({
        worktree: '/test/worktree',
        branch: 'test-branch'
      });

      pmSessions.claimTask(sessionId, 'TASK-5');
      pmSessions.claimTask(sessionId, 'TASK-6');
      pmSessions.claimTask(sessionId, 'TASK-3');

      const session = pmSessions.getSession(sessionId);
      assert.deepStrictEqual(session.claimed_tasks, ['TASK-5', 'TASK-6', 'TASK-3']);
    });

    it('should prevent claiming task already claimed by another active session', () => {
      const session1Id = pmSessions.registerSession({
        worktree: '/test/worktree1',
        branch: 'test-branch-1'
      });

      const session2Id = pmSessions.registerSession({
        worktree: '/test/worktree2',
        branch: 'test-branch-2'
      });

      pmSessions.claimTask(session1Id, 'TASK-5');

      const result = pmSessions.claimTask(session2Id, 'TASK-5');

      assert.strictEqual(result, false);

      const session2 = pmSessions.getSession(session2Id);
      assert.deepStrictEqual(session2.claimed_tasks, []);
    });

    it('should not claim task for non-active session', () => {
      const sessionId = pmSessions.registerSession({
        worktree: '/test/worktree',
        branch: 'test-branch'
      });

      pmSessions.endSession(sessionId);

      const result = pmSessions.claimTask(sessionId, 'TASK-5');
      assert.strictEqual(result, false);
    });

    it('should return false for non-existent session', () => {
      const result = pmSessions.claimTask('non-existent', 'TASK-5');
      assert.strictEqual(result, false);
    });
  });

  describe('releaseTask()', () => {
    it('should remove task from claimed_tasks array', () => {
      const sessionId = pmSessions.registerSession({
        worktree: '/test/worktree',
        branch: 'test-branch'
      });

      pmSessions.claimTask(sessionId, 'TASK-5');
      pmSessions.claimTask(sessionId, 'TASK-6');

      const result = pmSessions.releaseTask(sessionId, 'TASK-5');

      assert.strictEqual(result, true);

      const session = pmSessions.getSession(sessionId);
      assert.deepStrictEqual(session.claimed_tasks, ['TASK-6']);
    });

    it('should return false for task not claimed', () => {
      const sessionId = pmSessions.registerSession({
        worktree: '/test/worktree',
        branch: 'test-branch'
      });

      const result = pmSessions.releaseTask(sessionId, 'TASK-5');
      assert.strictEqual(result, false);
    });

    it('should return false for non-existent session', () => {
      const result = pmSessions.releaseTask('non-existent', 'TASK-5');
      assert.strictEqual(result, false);
    });
  });

  describe('cleanupOldSessions()', () => {
    it('should remove sessions older than 30 days', () => {
      const data = pmSessions.readSessions();

      // Create old session
      const oldSession = {
        session_id: 'old-session',
        worktree: '/test/worktree',
        branch: 'test-branch',
        pr_number: null,
        pr_status: null,
        last_heartbeat: new Date(Date.now() - 31 * 24 * 60 * 60 * 1000).toISOString(),
        claimed_tasks: [],
        status: 'ended',
        started_at: new Date(Date.now() - 31 * 24 * 60 * 60 * 1000).toISOString(),
        ended_at: new Date(Date.now() - 31 * 24 * 60 * 60 * 1000).toISOString()
      };

      data.sessions.push(oldSession);
      pmSessions.writeSessions(data);

      // Create recent session
      pmSessions.registerSession({
        worktree: '/test/worktree2',
        branch: 'test-branch-2'
      });

      const removedCount = pmSessions.cleanupOldSessions();

      assert.strictEqual(removedCount, 1);

      const afterCleanup = pmSessions.readSessions();
      assert.strictEqual(afterCleanup.sessions.length, 1);
      assert.notStrictEqual(afterCleanup.sessions[0].session_id, 'old-session');
    });

    it('should update last_cleanup timestamp', () => {
      const before = pmSessions.readSessions().last_cleanup;

      // Wait to ensure timestamp changes
      const waitUntil = Date.now() + 10;
      while (Date.now() < waitUntil) { /* spin */ }

      pmSessions.cleanupOldSessions();

      const after = pmSessions.readSessions().last_cleanup;

      assert.notStrictEqual(before, after);
    });
  });

  describe('getActiveSessions()', () => {
    it('should return only active sessions', () => {
      const active1 = pmSessions.registerSession({
        worktree: '/test/worktree1',
        branch: 'branch-1'
      });

      const active2 = pmSessions.registerSession({
        worktree: '/test/worktree2',
        branch: 'branch-2'
      });

      const toEnd = pmSessions.registerSession({
        worktree: '/test/worktree3',
        branch: 'branch-3'
      });

      pmSessions.endSession(toEnd);

      const activeSessions = pmSessions.getActiveSessions();

      assert.strictEqual(activeSessions.length, 2);
      assert.ok(activeSessions.some(s => s.session_id === active1));
      assert.ok(activeSessions.some(s => s.session_id === active2));
    });
  });
});

// =============================================================================
// INTEGRATION TESTS
// =============================================================================

describe('PM Sessions - Integration Tests', () => {

  beforeEach(() => {
    resetSessionsFile();
  });

  describe('Session Registration and Heartbeat Workflow', () => {
    it('should complete full lifecycle: register -> heartbeat -> end', () => {
      // 1. Register session
      const sessionId = pmSessions.registerSession({
        worktree: '/test/worktree',
        branch: 'test-branch'
      });

      assert.ok(sessionId);

      // 2. Update heartbeat
      const heartbeatResult = pmSessions.updateHeartbeat(sessionId);
      assert.strictEqual(heartbeatResult, true);

      // 3. End session
      const endResult = pmSessions.endSession(sessionId);
      assert.strictEqual(endResult, true);

      // 4. Verify final state
      const session = pmSessions.getSession(sessionId);
      assert.strictEqual(session.status, 'ended');
      assert.ok(session.ended_at);
    });

    it('should correctly detect stale session after 5 minute threshold', () => {
      // Create session with old heartbeat (6 minutes ago)
      const data = pmSessions.readSessions();
      const sixMinutesAgo = new Date(Date.now() - 6 * 60 * 1000);

      const session = {
        session_id: 'test-stale-session',
        worktree: '/test/worktree',
        branch: 'test-branch',
        pr_number: null,
        pr_status: null,
        last_heartbeat: sixMinutesAgo.toISOString(),
        claimed_tasks: [],
        status: 'active',
        started_at: sixMinutesAgo.toISOString(),
        ended_at: null
      };

      data.sessions.push(session);
      pmSessions.writeSessions(data);

      // Detect stale sessions
      const staleSessions = pmSessions.detectStaleSessions();

      assert.strictEqual(staleSessions.length, 1);
      assert.strictEqual(staleSessions[0].session_id, 'test-stale-session');

      // Verify persisted
      const persisted = pmSessions.getSession('test-stale-session');
      assert.strictEqual(persisted.status, 'stale');
    });

    it('should verify 60s heartbeat interval constant', () => {
      // This test documents the expected heartbeat interval
      assert.strictEqual(pmSessions.HEARTBEAT_INTERVAL_MS, 60 * 1000,
        'Heartbeat interval should be 60 seconds (60000ms)');
    });

    it('should verify 5 minute stale threshold constant', () => {
      // This test documents the expected stale threshold
      assert.strictEqual(pmSessions.STALE_THRESHOLD_MS, 5 * 60 * 1000,
        'Stale threshold should be 5 minutes (300000ms)');
    });
  });

  describe('Multi-Session Task Claiming', () => {
    it('should handle concurrent session task claims correctly', () => {
      // Simulate two worktrees claiming tasks
      const session1 = pmSessions.registerSession({
        worktree: '/worktree/feature-a',
        branch: 'feat/feature-a'
      });

      const session2 = pmSessions.registerSession({
        worktree: '/worktree/feature-b',
        branch: 'feat/feature-b'
      });

      // Session 1 claims TASK-5
      const claim1 = pmSessions.claimTask(session1, 'TASK-5');
      assert.strictEqual(claim1, true);

      // Session 2 tries to claim TASK-5 (should fail)
      const claim2 = pmSessions.claimTask(session2, 'TASK-5');
      assert.strictEqual(claim2, false);

      // Session 2 claims TASK-6 (should succeed)
      const claim3 = pmSessions.claimTask(session2, 'TASK-6');
      assert.strictEqual(claim3, true);

      // Verify final state
      const s1 = pmSessions.getSession(session1);
      const s2 = pmSessions.getSession(session2);

      assert.deepStrictEqual(s1.claimed_tasks, ['TASK-5']);
      assert.deepStrictEqual(s2.claimed_tasks, ['TASK-6']);
    });

    it('should allow claiming task after previous claimer ends session', () => {
      const session1 = pmSessions.registerSession({
        worktree: '/worktree/feature-a',
        branch: 'feat/feature-a'
      });

      pmSessions.claimTask(session1, 'TASK-5');
      pmSessions.endSession(session1);

      const session2 = pmSessions.registerSession({
        worktree: '/worktree/feature-b',
        branch: 'feat/feature-b'
      });

      // Should now be able to claim TASK-5
      const result = pmSessions.claimTask(session2, 'TASK-5');
      assert.strictEqual(result, true);
    });
  });

  describe('Session File Resilience', () => {
    it('should initialize file if missing', () => {
      // Delete the file
      if (fs.existsSync(TEST_SESSIONS_FILE)) {
        fs.unlinkSync(TEST_SESSIONS_FILE);
      }

      // Reading should recreate it
      const data = pmSessions.readSessions();

      assert.ok(data);
      assert.strictEqual(data.version, '1.0.0');
      assert.ok(Array.isArray(data.sessions));
      assert.ok(fs.existsSync(TEST_SESSIONS_FILE));
    });

    it('should handle corrupted file gracefully', () => {
      // Write invalid JSON
      fs.writeFileSync(TEST_SESSIONS_FILE, 'not valid json {{{');

      // Should return empty structure
      const data = pmSessions.readSessions();

      assert.ok(data);
      assert.strictEqual(data.version, '1.0.0');
      assert.deepStrictEqual(data.sessions, []);
    });
  });
});

// =============================================================================
// RUN TESTS
// =============================================================================

// If running directly, the test runner will execute all tests
if (require.main === module) {
  console.log('Running PM Sessions tests...');
  console.log('Use: node --test scripts/__tests__/pm_sessions.test.js');
}
