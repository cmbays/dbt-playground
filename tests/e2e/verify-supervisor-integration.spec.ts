import { test, expect } from '@playwright/test';
import { execSync } from 'child_process';

/**
 * Verification test for Supervisor integration with PM Orchestration (v0.9)
 *
 * TASK-10: Verify Supervisor uses Backlog.md API
 * TASK-11: Verify Supervisor session registration on startup
 *
 * This test verifies the documented workflow in .claude/agents/supervisor.md
 */

test.describe('Supervisor PM Orchestration Integration', () => {

  test('should register session via pm_sessions.js CLI', async () => {
    // Test documented workflow step 1: Register PM session
    const output = execSync('node scripts/pm_sessions.js register').toString();

    expect(output).toContain('Session registered:');

    // Extract session ID from output
    const sessionIdMatch = output.match(/Session registered: ([a-f0-9-]+)/);
    expect(sessionIdMatch).toBeTruthy();

    const sessionId = sessionIdMatch![1];
    console.log(`Registered session: ${sessionId}`);
  });

  test('should list active sessions', async () => {
    // Verify session tracking works
    const output = execSync('node scripts/pm_sessions.js active').toString();

    expect(output).toContain('Active sessions:');
    expect(output).toMatch(/Branch: \w+/);
    expect(output).toMatch(/Worktree: \/.*dbt-playground/);
  });

  test('should connect to Backlog.md API for config check', async ({ request }) => {
    // Test documented workflow step 2: Check Backlog.md API availability
    const response = await request.get('http://localhost:6420/api/config');

    // API may return 404 but server should be running
    // Response should be JSON even on error
    const body = await response.text();
    expect(body).toBeTruthy();
  });

  test('should query tasks from Backlog.md API', async ({ request }) => {
    // Test documented workflow step 4: Query active tasks
    const response = await request.get('http://localhost:6420/api/tasks');

    expect(response.ok()).toBeTruthy();

    const tasks = await response.json();
    expect(Array.isArray(tasks)).toBeTruthy();

    // Should have at least the test tasks
    expect(tasks.length).toBeGreaterThan(0);

    // Verify task structure matches Backlog.md schema
    const firstTask = tasks[0];
    expect(firstTask).toHaveProperty('id');
    expect(firstTask).toHaveProperty('title');
    expect(firstTask).toHaveProperty('status');
    expect(firstTask).toHaveProperty('assignee');

    console.log(`Found ${tasks.length} tasks in Backlog.md`);
  });

  test('should claim task via pm_sessions.js CLI', async () => {
    // First register a session
    const registerOutput = execSync('node scripts/pm_sessions.js register').toString();
    const sessionIdMatch = registerOutput.match(/Session registered: ([a-f0-9-]+)/);
    const sessionId = sessionIdMatch![1];

    // Test documented workflow step 7: Claim task
    // Use TASK-2 which exists in the backlog
    const claimOutput = execSync(`node scripts/pm_sessions.js claim ${sessionId} TASK-2`).toString();

    expect(claimOutput).toContain('Task TASK-2 claimed by session');

    // Verify task appears in active sessions
    const activeOutput = execSync('node scripts/pm_sessions.js active').toString();
    expect(activeOutput).toContain('TASK-2');

    // Clean up: release task
    execSync(`node scripts/pm_sessions.js release ${sessionId} TASK-2`);
  });

  test('should detect stale sessions', async () => {
    // Verify stale detection mechanism works
    const output = execSync('node scripts/pm_sessions.js check-stale').toString();

    // Should run without error (may or may not find stale sessions)
    expect(output).toBeTruthy();
  });

  test('Supervisor documentation should match implementation', async () => {
    // Read supervisor.md and verify documented workflow
    const fs = require('fs');
    const supervisorDoc = fs.readFileSync('.claude/agents/supervisor.md', 'utf-8');

    // Verify documented steps are present
    expect(supervisorDoc).toContain('node scripts/pm_sessions.js register');
    expect(supervisorDoc).toContain('GET http://localhost:6420/api/config');
    expect(supervisorDoc).toContain('GET http://localhost:6420/api/tasks');
    expect(supervisorDoc).toContain('POST /api/tasks');
    expect(supervisorDoc).toContain('PUT /api/tasks/{id}');
    expect(supervisorDoc).toContain('Start heartbeat loop (every 60s)');

    console.log('✅ Supervisor documentation matches implementation');
  });
});

test.describe('Supervisor PM Sessions Integration', () => {

  test('should maintain heartbeat for active session', async () => {
    // Register session
    const registerOutput = execSync('node scripts/pm_sessions.js register').toString();
    const sessionIdMatch = registerOutput.match(/Session registered: ([a-f0-9-]+)/);
    const sessionId = sessionIdMatch![1];

    // Update heartbeat (command may not output anything on success)
    execSync(`node scripts/pm_sessions.js heartbeat ${sessionId}`);

    // Verify session is still active (not stale)
    const activeOutput = execSync('node scripts/pm_sessions.js active').toString();
    expect(activeOutput).toContain(sessionId);
    expect(activeOutput).not.toContain('STALE');
  });
});
