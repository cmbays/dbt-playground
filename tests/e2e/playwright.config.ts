import { defineConfig, devices } from '@playwright/test';
import * as path from 'path';

// Compute absolute path to project root from this config file location
const PROJECT_ROOT = path.resolve(__dirname, '../..');

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
    // Base URL for tests - serves the playgrounds directory
    baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:5173',
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

  // Web server to serve the playgrounds
  webServer: {
    command: 'npx serve playgrounds -p 5173 --single',
    port: 5173,
    timeout: 30000,
    reuseExistingServer: !process.env.CI,
    cwd: PROJECT_ROOT,
  },
});
