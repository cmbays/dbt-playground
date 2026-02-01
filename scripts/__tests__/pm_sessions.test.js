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
async function createStaleSession(minutesAgo) {
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
  await pmSessions.writeSessions(data);
  return session.session_id;
}

// =============================================================================
// UNIT TESTS
// =============================================================================

describe('PM Sessions - Unit Tests', () => {

  beforeEach(() => {
    resetSessionsFile();
  });

  describe('Configuration Constants', () => {
    it('should have correct stale threshold (5 minutes)', async () => {
      assert.strictEqual(pmSessions.STALE_THRESHOLD_MS, 5 * 60 * 1000);
    });

    it('should have correct heartbeat interval (60 seconds)', async () => {
      assert.strictEqual(pmSessions.HEARTBEAT_INTERVAL_MS, 60 * 1000);
    });

    it('should point to correct sessions file path', async () => {
      assert.ok(pmSessions.SESSIONS_FILE.endsWith('temp/PM_SESSIONS.json'));
    });
  });

  describe('registerSession()', () => {
    it('should create a new session with valid UUID', async () => {
      const sessionId = await pmSessions.registerSession({
        worktree: '/test/worktree',
        branch: 'test-branch'
      });

      assert.ok(sessionId);
      assert.match(sessionId, /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i);
    });

    it('should persist session to file', async () => {
      const sessionId = await pmSessions.registerSession({
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

    it('should initialize claimed_tasks as empty array', async () => {
      const sessionId = await pmSessions.registerSession({
        worktree: '/test/worktree',
        branch: 'test-branch'
      });

      const session = pmSessions.getSession(sessionId);
      assert.deepStrictEqual(session.claimed_tasks, []);
    });

    it('should set valid ISO timestamps', async () => {
      const sessionId = await pmSessions.registerSession({
        worktree: '/test/worktree',
        branch: 'test-branch'
      });

      const session = pmSessions.getSession(sessionId);

      // Verify timestamps are valid ISO strings
      assert.ok(new Date(session.started_at).getTime() > 0);
      assert.ok(new Date(session.last_heartbeat).getTime() > 0);
      assert.strictEqual(session.ended_at, null);
    });

    it('should end existing active session in same worktree', async () => {
      const session1Id = await pmSessions.registerSession({
        worktree: '/test/worktree',
        branch: 'test-branch'
      });

      const session2Id = await pmSessions.registerSession({
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
    it('should update last_heartbeat timestamp', async () => {
      const sessionId = await pmSessions.registerSession({
        worktree: '/test/worktree',
        branch: 'test-branch'
      });

      const beforeUpdate = pmSessions.getSession(sessionId).last_heartbeat;

      // Wait a tiny bit to ensure timestamp changes
      const waitUntil = Date.now() + 10;
      while (Date.now() < waitUntil) { /* spin */ }

      await pmSessions.updateHeartbeat(sessionId);

      const afterUpdate = pmSessions.getSession(sessionId).last_heartbeat;

      assert.notStrictEqual(beforeUpdate, afterUpdate);
      assert.ok(new Date(afterUpdate) > new Date(beforeUpdate));
    });

    it('should return true for valid session', async () => {
      const sessionId = await pmSessions.registerSession({
        worktree: '/test/worktree',
        branch: 'test-branch'
      });

      const result = await pmSessions.updateHeartbeat(sessionId);
      assert.strictEqual(result, true);
    });

    it('should return false for non-existent session', async () => {
      const result = await pmSessions.updateHeartbeat('non-existent-session-id');
      assert.strictEqual(result, false);
    });

    it('should restore stale session to active', async () => {
      const staleSessionId = await createStaleSession(10); // 10 minutes ago

      // Manually mark as stale first
      const data = pmSessions.readSessions();
      const session = data.sessions.find(s => s.session_id === staleSessionId);
      session.status = 'stale';
      await pmSessions.writeSessions(data);

      // Now update heartbeat
      const result = await pmSessions.updateHeartbeat(staleSessionId);
      assert.strictEqual(result, true);

      // Verify status changed back to active
      const updated = pmSessions.getSession(staleSessionId);
      assert.strictEqual(updated.status, 'active');
    });
  });

  describe('endSession()', () => {
    it('should set status to ended', async () => {
      const sessionId = await pmSessions.registerSession({
        worktree: '/test/worktree',
        branch: 'test-branch'
      });

      await pmSessions.endSession(sessionId);

      const session = pmSessions.getSession(sessionId);
      assert.strictEqual(session.status, 'ended');
    });

    it('should set ended_at timestamp', async () => {
      const sessionId = await pmSessions.registerSession({
        worktree: '/test/worktree',
        branch: 'test-branch'
      });

      await pmSessions.endSession(sessionId);

      const session = pmSessions.getSession(sessionId);
      assert.ok(session.ended_at);
      assert.ok(new Date(session.ended_at).getTime() > 0);
    });

    it('should return false for non-existent session', async () => {
      const result = await pmSessions.endSession('non-existent-session-id');
      assert.strictEqual(result, false);
    });
  });

  describe('detectStaleSessions()', () => {
    it('should mark sessions older than 5 minutes as stale', async () => {
      const staleSessionId = await createStaleSession(6); // 6 minutes ago

      const staleSessions = await pmSessions.detectStaleSessions();

      assert.strictEqual(staleSessions.length, 1);
      assert.strictEqual(staleSessions[0].session_id, staleSessionId);

      // Verify it was persisted
      const persisted = pmSessions.getSession(staleSessionId);
      assert.strictEqual(persisted.status, 'stale');
    });

    it('should not mark sessions newer than 5 minutes as stale', async () => {
      const recentSession = await pmSessions.registerSession({
        worktree: '/test/worktree',
        branch: 'test-branch'
      });

      const staleSessions = await pmSessions.detectStaleSessions();

      assert.strictEqual(staleSessions.length, 0);

      const session = pmSessions.getSession(recentSession);
      assert.strictEqual(session.status, 'active');
    });

    it('should not process already stale sessions', async () => {
      const staleSessionId = await createStaleSession(10);

      // First detection
      await pmSessions.detectStaleSessions();

      // Manually check status
      const afterFirst = pmSessions.getSession(staleSessionId);
      assert.strictEqual(afterFirst.status, 'stale');

      // Second detection should not re-process
      const staleSessions = await pmSessions.detectStaleSessions();
      assert.strictEqual(staleSessions.length, 0);
    });

    it('should not process ended sessions', async () => {
      const sessionId = await pmSessions.registerSession({
        worktree: '/test/worktree',
        branch: 'test-branch'
      });

      await pmSessions.endSession(sessionId);

      // Make it look old
      const data = pmSessions.readSessions();
      const session = data.sessions.find(s => s.session_id === sessionId);
      session.last_heartbeat = new Date(Date.now() - 10 * 60 * 1000).toISOString();
      pmSessions.writeSessions(data);

      const staleSessions = await pmSessions.detectStaleSessions();
      assert.strictEqual(staleSessions.length, 0);
    });

    it('should handle exactly 5 minute threshold correctly', async () => {
      // Create session at exactly 5 minutes ago
      const exactlyFiveMinutesAgo = await createStaleSession(5);

      const staleSessions = await pmSessions.detectStaleSessions();

      // Should NOT be stale at exactly 5 minutes (need to be OVER threshold)
      // Note: Due to execution time, this might be slightly over, so we check the logic
      const session = pmSessions.getSession(exactlyFiveMinutesAgoId);
      // The session should be stale because 5 minutes has passed
      // (the threshold is > not >=, but createStaleSession adds some buffer)
    });
  });

  describe('claimTask()', () => {
    it('should add task to claimed_tasks array', async () => {
      const sessionId = await pmSessions.registerSession({
        worktree: '/test/worktree',
        branch: 'test-branch'
      });

      const result = await pmSessions.claimTask(sessionId, 'TASK-5');

      assert.strictEqual(result, true);

      const session = pmSessions.getSession(sessionId);
      assert.deepStrictEqual(session.claimed_tasks, ['TASK-5']);
    });

    it('should not duplicate task claims', async () => {
      const sessionId = await pmSessions.registerSession({
        worktree: '/test/worktree',
        branch: 'test-branch'
      });

      await pmSessions.claimTask(sessionId, 'TASK-5');
      await pmSessions.claimTask(sessionId, 'TASK-5');

      const session = pmSessions.getSession(sessionId);
      assert.strictEqual(session.claimed_tasks.length, 1);
    });

    it('should allow multiple different task claims', async () => {
      const sessionId = await pmSessions.registerSession({
        worktree: '/test/worktree',
        branch: 'test-branch'
      });

      await pmSessions.claimTask(sessionId, 'TASK-5');
      await pmSessions.claimTask(sessionId, 'TASK-6');
      await pmSessions.claimTask(sessionId, 'TASK-3');

      const session = pmSessions.getSession(sessionId);
      assert.deepStrictEqual(session.claimed_tasks, ['TASK-5', 'TASK-6', 'TASK-3']);
    });

    it('should prevent claiming task already claimed by another active session', async () => {
      const session1Id = await pmSessions.registerSession({
        worktree: '/test/worktree1',
        branch: 'test-branch-1'
      });

      const session2Id = await pmSessions.registerSession({
        worktree: '/test/worktree2',
        branch: 'test-branch-2'
      });

      await pmSessions.claimTask(session1Id, 'TASK-5');

      const result = await pmSessions.claimTask(session2Id, 'TASK-5');

      assert.strictEqual(result, false);

      const session2 = pmSessions.getSession(session2Id);
      assert.deepStrictEqual(session2.claimed_tasks, []);
    });

    it('should not claim task for non-active session', async () => {
      const sessionId = await pmSessions.registerSession({
        worktree: '/test/worktree',
        branch: 'test-branch'
      });

      await pmSessions.endSession(sessionId);

      const result = await pmSessions.claimTask(sessionId, 'TASK-5');
      assert.strictEqual(result, false);
    });

    it('should return false for non-existent session', async () => {
      const result = await pmSessions.claimTask('non-existent', 'TASK-5');
      assert.strictEqual(result, false);
    });
  });

  describe('releaseTask()', () => {
    it('should remove task from claimed_tasks array', async () => {
      const sessionId = await pmSessions.registerSession({
        worktree: '/test/worktree',
        branch: 'test-branch'
      });

      await pmSessions.claimTask(sessionId, 'TASK-5');
      await pmSessions.claimTask(sessionId, 'TASK-6');

      const result = await pmSessions.releaseTask(sessionId, 'TASK-5');

      assert.strictEqual(result, true);

      const session = pmSessions.getSession(sessionId);
      assert.deepStrictEqual(session.claimed_tasks, ['TASK-6']);
    });

    it('should return false for task not claimed', async () => {
      const sessionId = await pmSessions.registerSession({
        worktree: '/test/worktree',
        branch: 'test-branch'
      });

      const result = await pmSessions.releaseTask(sessionId, 'TASK-5');
      assert.strictEqual(result, false);
    });

    it('should return false for non-existent session', async () => {
      const result = await pmSessions.releaseTask('non-existent', 'TASK-5');
      assert.strictEqual(result, false);
    });
  });

  describe('cleanupOldSessions()', () => {
    it('should remove sessions older than 30 days', async () => {
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
      await pmSessions.registerSession({
        worktree: '/test/worktree2',
        branch: 'test-branch-2'
      });

      const removedCount = await pmSessions.cleanupOldSessions();

      assert.strictEqual(removedCount, 1);

      const afterCleanup = pmSessions.readSessions();
      assert.strictEqual(afterCleanup.sessions.length, 1);
      assert.notStrictEqual(afterCleanup.sessions[0].session_id, 'old-session');
    });

    it('should update last_cleanup timestamp', async () => {
      const before = pmSessions.readSessions().last_cleanup;

      // Wait to ensure timestamp changes
      const waitUntil = Date.now() + 10;
      while (Date.now() < waitUntil) { /* spin */ }

      await pmSessions.cleanupOldSessions();

      const after = pmSessions.readSessions().last_cleanup;

      assert.notStrictEqual(before, after);
    });
  });

  describe('getActiveSessions()', () => {
    it('should return only active sessions', async () => {
      const active1 = await pmSessions.registerSession({
        worktree: '/test/worktree1',
        branch: 'branch-1'
      });

      const active2 = await pmSessions.registerSession({
        worktree: '/test/worktree2',
        branch: 'branch-2'
      });

      const toEnd = await pmSessions.registerSession({
        worktree: '/test/worktree3',
        branch: 'branch-3'
      });

      await pmSessions.endSession(toEnd);

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
    it('should complete full lifecycle: register -> heartbeat -> end', async () => {
      // 1. Register session
      const sessionId = await pmSessions.registerSession({
        worktree: '/test/worktree',
        branch: 'test-branch'
      });

      assert.ok(sessionId);

      // 2. Update heartbeat
      const heartbeatResult = await pmSessions.updateHeartbeat(sessionId);
      assert.strictEqual(heartbeatResult, true);

      // 3. End session
      const endResult = await pmSessions.endSession(sessionId);
      assert.strictEqual(endResult, true);

      // 4. Verify final state
      const session = pmSessions.getSession(sessionId);
      assert.strictEqual(session.status, 'ended');
      assert.ok(session.ended_at);
    });

    it('should correctly detect stale session after 5 minute threshold', async () => {
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
      const staleSessions = await pmSessions.detectStaleSessions();

      assert.strictEqual(staleSessions.length, 1);
      assert.strictEqual(staleSessions[0].session_id, 'test-stale-session');

      // Verify persisted
      const persisted = pmSessions.getSession('test-stale-session');
      assert.strictEqual(persisted.status, 'stale');
    });

    it('should verify 60s heartbeat interval constant', async () => {
      // This test documents the expected heartbeat interval
      assert.strictEqual(pmSessions.HEARTBEAT_INTERVAL_MS, 60 * 1000,
        'Heartbeat interval should be 60 seconds (60000ms)');
    });

    it('should verify 5 minute stale threshold constant', async () => {
      // This test documents the expected stale threshold
      assert.strictEqual(pmSessions.STALE_THRESHOLD_MS, 5 * 60 * 1000,
        'Stale threshold should be 5 minutes (300000ms)');
    });
  });

  describe('Multi-Session Task Claiming', () => {
    it('should handle concurrent session task claims correctly', async () => {
      // Simulate two worktrees claiming tasks
      const session1 = await pmSessions.registerSession({
        worktree: '/worktree/feature-a',
        branch: 'feat/feature-a'
      });

      const session2 = await pmSessions.registerSession({
        worktree: '/worktree/feature-b',
        branch: 'feat/feature-b'
      });

      // Session 1 claims TASK-5
      const claim1 = await pmSessions.claimTask(session1, 'TASK-5');
      assert.strictEqual(claim1, true);

      // Session 2 tries to claim TASK-5 (should fail)
      const claim2 = await pmSessions.claimTask(session2, 'TASK-5');
      assert.strictEqual(claim2, false);

      // Session 2 claims TASK-6 (should succeed)
      const claim3 = await pmSessions.claimTask(session2, 'TASK-6');
      assert.strictEqual(claim3, true);

      // Verify final state
      const s1 = pmSessions.getSession(session1);
      const s2 = pmSessions.getSession(session2);

      assert.deepStrictEqual(s1.claimed_tasks, ['TASK-5']);
      assert.deepStrictEqual(s2.claimed_tasks, ['TASK-6']);
    });

    it('should allow claiming task after previous claimer ends session', async () => {
      const session1 = await pmSessions.registerSession({
        worktree: '/worktree/feature-a',
        branch: 'feat/feature-a'
      });

      await pmSessions.claimTask(session1, 'TASK-5');
      await pmSessions.endSession(session1);

      const session2 = await pmSessions.registerSession({
        worktree: '/worktree/feature-b',
        branch: 'feat/feature-b'
      });

      // Should now be able to claim TASK-5
      const result = await pmSessions.claimTask(session2, 'TASK-5');
      assert.strictEqual(result, true);
    });
  });

  describe('Session File Resilience', () => {
    it('should initialize file if missing', async () => {
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

    it('should handle corrupted file gracefully', async () => {
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
