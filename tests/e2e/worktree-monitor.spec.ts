import { test, expect, Page } from '@playwright/test';

/**
 * E2E Tests for Worktree Monitor v2.0
 *
 * These tests validate the UI implementation in workflow-hub.html.
 * Tests cover: Page load, heartbeat indicators, anomaly highlighting,
 * Hub integration, and archive view functionality.
 *
 * Test IDs: E2E-LOAD-*, E2E-HB-*, E2E-ANOM-*, E2E-HUB-*, E2E-ARCH-*
 */

// Fixed timestamp for deterministic tests (2026-02-04T12:00:00.000Z)
const FIXED_TIMESTAMP = '2026-02-04T12:00:00.000Z';

// Test data fixtures
const testWorktreesData = {
  timestamp: FIXED_TIMESTAMP,
  config_version: 1,
  milestone: "v0.10",
  worktree_count: 3,
  worktrees: [
    {
      path: "/test/main",
      branch: "main",
      commit_short: "abc123",
      is_main: true,
      status: "clean",
      files_changed: 0,
      files_staged: 0,
      last_commit_msg: "Initial commit",
      anomalies: []
    },
    {
      path: "/test/feat-a",
      branch: "feat/feature-a",
      commit_short: "def456",
      is_main: false,
      status: "dirty",
      files_changed: 3,
      files_staged: 1,
      last_commit_msg: "WIP: Add feature",
      pr: { url: "https://github.com/test/repo/pull/42", number: 42, state: "open" },
      anomalies: []
    },
    {
      path: "/test/feat-b",
      branch: "feat/feature-b",
      commit_short: "ghi789",
      is_main: false,
      status: "clean",
      files_changed: 0,
      files_staged: 0,
      last_commit_msg: "Implement feature B",
      anomalies: []
    }
  ],
  tracks: [],
  archived: [],
  heartbeat: null,
  anomalies: [],
  errors: []
};

// Helper to setup mock route for worktrees.json
async function mockWorktreesJson(page: Page, data: object) {
  await page.route('**/worktrees.json', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(data)
    });
  });
}

// Navigate to Workflow Hub and switch to Worktree Monitor tab
async function navigateToWorktreeMonitor(page: Page) {
  await page.goto('/playgrounds/workflow-hub.html');
  await page.click('[data-view="worktree-monitor"]');
  // Wait for the view to be visible
  await page.waitForSelector('#worktree-monitor-view.active', { state: 'visible' });
}

test.describe('E2E Page Load Tests', () => {

  test('E2E-LOAD-01: Page loads without JavaScript errors', async ({ page }) => {
    const errors: string[] = [];
    page.on('pageerror', err => errors.push(err.message));

    await mockWorktreesJson(page, testWorktreesData);
    const response = await page.goto('/playgrounds/workflow-hub.html');

    expect(response?.status()).toBe(200);
    expect(errors).toHaveLength(0);
    expect(await page.title()).toContain('Workflow Hub');
  });

  test('E2E-LOAD-02: Worktree cards render with data', async ({ page }) => {
    await mockWorktreesJson(page, testWorktreesData);
    await navigateToWorktreeMonitor(page);

    await page.waitForSelector('[data-testid="worktree-card"]');
    const cards = page.locator('[data-testid="worktree-card"]');

    await expect(cards).toHaveCount(3);

    const firstCard = cards.first();
    await expect(firstCard.locator('.branch-name')).toBeVisible();
    await expect(firstCard.locator('.branch-name')).toContainText('main');
  });

  test('E2E-LOAD-03: Phase section renders', async ({ page }) => {
    await mockWorktreesJson(page, testWorktreesData);
    await navigateToWorktreeMonitor(page);

    await page.waitForSelector('[data-testid="phase-section"]');
    const phaseSections = page.locator('[data-testid="phase-section"]');

    await expect(phaseSections).toHaveCount(1); // Default "All Worktrees" section
    await expect(phaseSections.first().locator('.phase-header')).toContainText('All Worktrees');
  });

  test('E2E-LOAD-04: Summary counts are correct', async ({ page }) => {
    await mockWorktreesJson(page, testWorktreesData);
    await navigateToWorktreeMonitor(page);

    await page.waitForSelector('[data-testid="monitor-summary"]');
    const summary = page.locator('[data-testid="monitor-summary"]');

    await expect(summary.locator('[data-testid="stat-total"] .monitor-stat-value')).toContainText('3');
    await expect(summary.locator('[data-testid="stat-dirty"] .monitor-stat-value')).toContainText('1');
  });
});

test.describe('E2E Heartbeat Indicator Tests', () => {

  test('E2E-HB-01: Fresh heartbeat shows green/active', async ({ page }) => {
    // Install clock for deterministic time
    await page.clock.install({ time: new Date('2026-02-04T12:00:00.000Z') });

    const freshData = {
      ...testWorktreesData,
      timestamp: '2026-02-04T12:00:00.000Z' // Current time per clock
    };
    await mockWorktreesJson(page, freshData);
    await navigateToWorktreeMonitor(page);

    await page.waitForSelector('[data-testid="heartbeat-indicator"]');
    const indicator = page.locator('[data-testid="heartbeat-indicator"]');

    await expect(indicator).toHaveAttribute('data-status', 'fresh');
    await expect(indicator.locator('.heartbeat-label')).toContainText(/Active/);
  });

  test('E2E-HB-02: Stale heartbeat shows warning', async ({ page }) => {
    // Install clock for deterministic time
    await page.clock.install({ time: new Date('2026-02-04T12:00:45.000Z') });

    const staleData = {
      ...testWorktreesData,
      timestamp: '2026-02-04T12:00:00.000Z' // 45 seconds before clock time
    };
    await mockWorktreesJson(page, staleData);
    await navigateToWorktreeMonitor(page);

    await page.waitForSelector('[data-testid="heartbeat-indicator"]');
    const indicator = page.locator('[data-testid="heartbeat-indicator"]');

    await expect(indicator).toHaveAttribute('data-status', 'stale');
    await expect(indicator.locator('.heartbeat-label')).toContainText(/Stale/);
  });

  test('E2E-HB-03: Inactive heartbeat shows error state', async ({ page }) => {
    // Install clock for deterministic time
    await page.clock.install({ time: new Date('2026-02-04T12:03:00.000Z') });

    const oldData = {
      ...testWorktreesData,
      timestamp: '2026-02-04T12:00:00.000Z' // 3 minutes before clock time
    };
    await mockWorktreesJson(page, oldData);
    await navigateToWorktreeMonitor(page);

    await page.waitForSelector('[data-testid="heartbeat-indicator"]');
    const indicator = page.locator('[data-testid="heartbeat-indicator"]');

    await expect(indicator).toHaveAttribute('data-status', 'inactive');
    await expect(indicator.locator('.heartbeat-label')).toContainText(/Inactive/);
  });

  test('E2E-HB-04: Refresh button triggers data reload', async ({ page }) => {
    let fetchCount = 0;
    await page.route('**/worktrees.json', route => {
      fetchCount++;
      const timestamp = fetchCount === 1
        ? new Date(Date.now() - 60000).toISOString() // First: stale
        : new Date().toISOString(); // Second: fresh

      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          ...testWorktreesData,
          timestamp
        })
      });
    });

    await navigateToWorktreeMonitor(page);
    await page.waitForSelector('[data-testid="heartbeat-indicator"]');

    // Initial should be stale
    const indicator = page.locator('[data-testid="heartbeat-indicator"]');
    await expect(indicator).toHaveAttribute('data-status', 'stale');

    // Click refresh and wait for the indicator status to change to fresh
    await page.click('[data-testid="refresh-button"]');
    await expect(indicator).toHaveAttribute('data-status', 'fresh');
    expect(fetchCount).toBe(2);
  });
});

test.describe('E2E Anomaly Highlighting Tests', () => {

  test('E2E-ANOM-01: CI failure shows danger styling', async ({ page }) => {
    const dataWithCIFailure = {
      ...testWorktreesData,
      worktrees: [
        {
          ...testWorktreesData.worktrees[0],
          branch: "feat/ci-failure",
          ci_checks: { state: "failure", passed: 2, failed: 1, pending: 0 },
          anomalies: [{ type: "ci_failed", severity: "HIGH" }]
        }
      ]
    };
    await mockWorktreesJson(page, dataWithCIFailure);
    await navigateToWorktreeMonitor(page);

    await page.waitForSelector('[data-testid="worktree-card"]');
    const card = page.locator('[data-testid="worktree-card"]').first();

    await expect(card).toHaveClass(/anomaly-ci_failed/);
  });

  test('E2E-ANOM-02: CodeRabbit changes_requested shows warning', async ({ page }) => {
    const dataWithCodeRabbit = {
      ...testWorktreesData,
      worktrees: [
        {
          ...testWorktreesData.worktrees[0],
          branch: "feat/changes-requested",
          anomalies: [{ type: "changes_requested", severity: "MEDIUM" }]
        }
      ]
    };
    await mockWorktreesJson(page, dataWithCodeRabbit);
    await navigateToWorktreeMonitor(page);

    await page.waitForSelector('[data-testid="worktree-card"]');
    const card = page.locator('[data-testid="worktree-card"]').first();

    await expect(card).toHaveClass(/anomaly-changes_requested/);
  });

  test('E2E-ANOM-03: Dirty worktree shows visual indicator', async ({ page }) => {
    const dataWithDirty = {
      ...testWorktreesData,
      worktrees: [
        {
          ...testWorktreesData.worktrees[1], // Already dirty
          anomalies: [{ type: "DIRTY_WORKTREE", severity: "LOW" }]
        }
      ]
    };
    await mockWorktreesJson(page, dataWithDirty);
    await navigateToWorktreeMonitor(page);

    await page.waitForSelector('[data-testid="worktree-card"]');
    const card = page.locator('[data-testid="worktree-card"]').first();

    await expect(card).toHaveClass(/anomaly-/);
  });

  test('E2E-ANOM-04: Multiple anomalies on same card', async ({ page }) => {
    const dataWithMultiple = {
      ...testWorktreesData,
      worktrees: [
        {
          ...testWorktreesData.worktrees[0],
          branch: "feat/multi-issue",
          status: "dirty",
          ci_checks: { state: "failure", passed: 1, failed: 2, pending: 0 },
          anomalies: [
            { type: "ci_failed", severity: "HIGH" },
            { type: "changes_requested", severity: "MEDIUM" }
          ]
        }
      ]
    };
    await mockWorktreesJson(page, dataWithMultiple);
    await navigateToWorktreeMonitor(page);

    await page.waitForSelector('[data-testid="worktree-card"]');
    const card = page.locator('[data-testid="worktree-card"]').first();

    await expect(card).toHaveClass(/anomaly-ci_failed/);
    await expect(card).toHaveClass(/anomaly-changes_requested/);
  });
});

test.describe('E2E Hub Integration Tests', () => {

  test('E2E-HUB-01: Third tab appears in Workflow Hub', async ({ page }) => {
    await mockWorktreesJson(page, testWorktreesData);
    await page.goto('/playgrounds/workflow-hub.html');

    const dashboardTab = page.locator('[data-view="dashboard"]');
    const kanbanTab = page.locator('[data-view="kanban"]');
    const monitorTab = page.locator('[data-view="worktree-monitor"]');

    await expect(dashboardTab).toBeVisible();
    await expect(kanbanTab).toBeVisible();
    await expect(monitorTab).toBeVisible();

    await expect(monitorTab).toContainText('Worktree Monitor');
  });

  test('E2E-HUB-02: Tab navigation works', async ({ page }) => {
    await mockWorktreesJson(page, testWorktreesData);
    await page.goto('/playgrounds/workflow-hub.html');

    // Start on Dashboard (default)
    await expect(page.locator('#dashboard-view')).toHaveClass(/active/);

    // Click Worktree Monitor
    await page.click('[data-view="worktree-monitor"]');
    await expect(page.locator('#worktree-monitor-view')).toHaveClass(/active/);
    await expect(page.locator('#dashboard-view')).not.toHaveClass(/active/);

    // Click Kanban
    await page.click('[data-view="kanban"]');
    await expect(page.locator('#kanban-view')).toHaveClass(/active/);
    await expect(page.locator('#worktree-monitor-view')).not.toHaveClass(/active/);

    // Click Dashboard
    await page.click('[data-view="dashboard"]');
    await expect(page.locator('#dashboard-view')).toHaveClass(/active/);
  });

  test('E2E-HUB-03: Tab content loads monitor data', async ({ page }) => {
    let fetchMade = false;
    await page.route('**/worktrees.json', route => {
      fetchMade = true;
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(testWorktreesData)
      });
    });

    await page.goto('/playgrounds/workflow-hub.html');

    // Fetch may or may not happen before tab click (depends on init timing)
    // But should definitely happen after clicking the tab
    await page.click('[data-view="worktree-monitor"]');
    await page.waitForSelector('[data-testid="worktree-card"]');

    expect(fetchMade).toBe(true);

    // Verify content rendered
    await expect(page.locator('[data-testid="worktree-card"]')).toHaveCount(3);
  });
});

test.describe('E2E Archive View Tests', () => {

  // TODO: Archive view functionality is planned for future implementation.
  // These tests are placeholders that will be enabled when archive features are added.
  test.skip('E2E-ARCH-01: Archived worktrees display correctly', async ({ page }) => {
    // Archive view is for historical data
    // The current implementation shows worktrees from worktrees.json
    // Archive support is a future feature

    const dataWithArchive = {
      ...testWorktreesData,
      archived_versions: ["v0.8", "v0.9"]
    };
    await mockWorktreesJson(page, dataWithArchive);
    await navigateToWorktreeMonitor(page);

    // For now, just verify the monitor loads successfully with archive data
    await page.waitForSelector('[data-testid="worktree-card"]');
    await expect(page.locator('[data-testid="worktree-card"]')).toHaveCount(3);
  });

  // TODO: Archive styling consistency test - will be implemented with archive feature.
  test.skip('E2E-ARCH-02: Archive cards use consistent styling (AC-8)', async ({ page }) => {
    // This test documents the AC-8 requirement:
    // "Archive cards match operator view styling"
    // When archive view is implemented, this test verifies consistency

    await mockWorktreesJson(page, testWorktreesData);
    await navigateToWorktreeMonitor(page);

    await page.waitForSelector('[data-testid="worktree-card"]');

    // Verify base card styling is consistent
    const cards = page.locator('[data-testid="worktree-card"]');
    const firstCard = cards.first();

    // Card should have standard styling elements
    await expect(firstCard.locator('.branch-name')).toBeVisible();
    await expect(firstCard.locator('.wt-status-badge')).toBeVisible();
    await expect(firstCard.locator('.commit-info')).toBeVisible();
  });
});

test.describe('E2E Filter and Refresh Tests', () => {

  test('E2E-FILTER-01: Manual refresh updates data', async ({ page }) => {
    let version = 1;
    await page.route('**/worktrees.json', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          ...testWorktreesData,
          worktrees: [
            {
              ...testWorktreesData.worktrees[0],
              branch: `feat/v${version}`
            }
          ]
        })
      });
      version++;
    });

    await navigateToWorktreeMonitor(page);
    await page.waitForSelector('[data-testid="worktree-card"]');

    // Initial data
    await expect(page.locator('.branch-name')).toContainText('feat/v1');

    // Click refresh and wait for the branch name to update to v2
    await page.click('[data-testid="refresh-button"]');
    await expect(page.locator('.branch-name')).toContainText('feat/v2');
  });

  test('E2E-FILTER-02: PR links are clickable', async ({ page }) => {
    await mockWorktreesJson(page, testWorktreesData);
    await navigateToWorktreeMonitor(page);

    await page.waitForSelector('[data-testid="worktree-card"]');

    // Find card with PR
    const prLink = page.locator('.pr-link').first();
    await expect(prLink).toBeVisible();
    await expect(prLink).toHaveAttribute('href', /github\.com.*pull\/42/);
    await expect(prLink).toContainText('PR #42');
  });
});
