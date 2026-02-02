import { test, expect } from '@playwright/test';

test.describe('Workflow Hub v0.9 Widget Verification', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5050/playgrounds/workflow-hub.html');
    await page.waitForLoadState('networkidle');
    // Wait for widgets to load
    await page.waitForTimeout(3000);
  });

  test('PM Overview widget should connect to Backlog.md', async ({ page }) => {
    const pmOverview = page.locator('#pm-overview-container');
    await expect(pmOverview).toBeVisible();
    
    // Should NOT show error message
    const errorText = await pmOverview.textContent();
    expect(errorText).not.toContain('Could not connect to Backlog.md');
    
    // Should show task status grid
    const statusGrid = pmOverview.locator('.pm-status-grid');
    await expect(statusGrid).toBeVisible();
  });

  test('PM Sessions widget should show active sessions', async ({ page }) => {
    const pmSessions = page.locator('#pm-sessions-card');
    await expect(pmSessions).toBeVisible();
    
    // Check title
    await expect(pmSessions.locator('.card-title')).toContainText('PM Sessions');
    
    // Should show session count
    const sessionCount = pmSessions.locator('#pm-session-count');
    await expect(sessionCount).toBeVisible();
    
    // Should show sessions container
    const sessionsContainer = page.locator('#pm-sessions-container');
    await expect(sessionsContainer).toBeVisible();
    
    // Should NOT show "Loading sessions..." after data loads
    await page.waitForTimeout(2000);
    const content = await sessionsContainer.textContent();
    expect(content).not.toContain('Loading sessions...');
  });

  test('PM Overview should display task statistics', async ({ page }) => {
    const pmOverview = page.locator('#pm-overview-container');
    
    // Wait for task data to load
    await page.waitForTimeout(2000);
    
    // Should show status boxes
    const statusBoxes = pmOverview.locator('.pm-status-box');
    const count = await statusBoxes.count();
    expect(count).toBeGreaterThan(0);
  });
});
