import { test } from '@playwright/test';

test('Screenshot Workflow Hub', async ({ page }) => {
  page.on('console', msg => console.log('[BROWSER]', msg.type(), msg.text()));
  
  await page.goto('http://localhost:5050/playgrounds/workflow-hub.html', { waitUntil: 'networkidle' });
  
  // Wait for widgets
  await page.waitForTimeout(5000);
  
  // Screenshot PM Overview widget specifically
  await page.locator('#pm-overview-card').screenshot({ path: '/tmp/pm-overview.png' });
  
  // Screenshot PM Sessions widget
  await page.locator('#pm-sessions-card').screenshot({ path: '/tmp/pm-sessions.png' });
  
  console.log('Screenshots saved to /tmp/');
});
