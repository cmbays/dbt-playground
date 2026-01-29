#!/usr/bin/env node
/**
 * Post-Edit Hook: Quality checks after file modifications
 *
 * Checks:
 * - Warns about console.log statements in production code
 * - Reminds about version stamps
 * - Checks for common issues
 */

const path = require('path');
const fs = require('fs');

const input = process.argv[2];
const output = process.argv[3];

try {
  const toolInput = JSON.parse(input || '{}');
  const filePath = toolInput.file_path || '';
  const fileName = path.basename(filePath);

  // Only check JS and HTML files
  if (!filePath.match(/\.(js|html)$/)) {
    process.exit(0);
  }

  // Skip temp and test files
  if (filePath.includes('/temp/') || filePath.includes('.test.') || filePath.includes('.spec.')) {
    process.exit(0);
  }

  // Read the file content
  if (fs.existsSync(filePath)) {
    const content = fs.readFileSync(filePath, 'utf8');

    // Check for console.log in JS files (not temp)
    if (filePath.endsWith('.js') && !filePath.includes('/temp/')) {
      const consoleLogCount = (content.match(/console\.log/g) || []).length;
      if (consoleLogCount > 3) {
        console.error(`[HOOK NOTE] Found ${consoleLogCount} console.log statements in ${fileName}`);
        console.error('Consider removing debug statements before final commit.');
      }
    }

    // Check for version comment in HTML files
    if (filePath.endsWith('.html') &&
        !filePath.includes('/temp/') &&
        filePath.includes('/topics/')) {
      if (!content.includes('<!-- Version:')) {
        console.error(`[HOOK REMINDER] ${fileName} missing version comment`);
        console.error('Add: <!-- Version: vX.Y.Z - Updated: YYYY-MM-DD -->');
      }
    }

    // Check for TODO/FIXME comments
    const todoCount = (content.match(/TODO|FIXME|HACK|XXX/g) || []).length;
    if (todoCount > 0) {
      console.error(`[HOOK NOTE] Found ${todoCount} TODO/FIXME comments in ${fileName}`);
    }
  }

  process.exit(0);
} catch (error) {
  console.error(`[HOOK ERROR] ${error.message}`);
  process.exit(0);
}
