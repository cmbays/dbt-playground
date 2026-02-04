import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright configuration for Worktree Monitor E2E tests.
 *
 * Run tests with:
 *   npx playwright test tests/e2e/worktree-monitor.spec.ts
 *
 * Run with UI:
 *   npx playwright test tests/e2e/ --ui
 */
export default defineConfig({
  testDir: './',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['list'],
    ['html', { outputFolder: './playwright-report', open: 'never' }]
  ],
  use: {
    // Base URL for tests
    baseURL: 'http://127.0.0.1:5173',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 10000,
    navigationTimeout: 30000,
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  timeout: 60000,

  // Web server to serve the project root (run from project root, not tests/e2e)
  webServer: {
    command: 'npx serve . -l 5173',
    url: 'http://127.0.0.1:5173',
    timeout: 60000,
    reuseExistingServer: !process.env.CI,
    cwd: '../..',  // Go up from tests/e2e to project root
  },
});
