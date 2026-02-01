#!/usr/bin/env node
/**
 * Script to convert synchronous tests to async
 */

const fs = require('fs');
const path = require('path');

const testFile = path.join(__dirname, '__tests__/pm_sessions.test.js');
let content = fs.readFileSync(testFile, 'utf-8');

// Make it() callbacks async
content = content.replace(/it\('([^']+)', \(\) => \{/g, "it('$1', async () => {");
content = content.replace(/it\("([^"]+)", \(\) => \{/g, 'it("$1", async () => {');

// Add await to all pmSessions function calls
const asyncFunctions = [
  'registerSession',
  'updateHeartbeat',
  'endSession',
  'detectStaleSessions',
  'claimTask',
  'releaseTask',
  'cleanupOldSessions'
];

asyncFunctions.forEach(fn => {
  // Pattern: pmSessions.functionName(
  content = content.replace(
    new RegExp(`(\\s+)pmSessions\\.${fn}\\(`, 'g'),
    `$1await pmSessions.${fn}(`
  );

  // Pattern: const result = pmSessions.functionName(
  content = content.replace(
    new RegExp(`const (\\w+) = pmSessions\\.${fn}\\(`, 'g'),
    `const $1 = await pmSessions.${fn}(`
  );
});

// Make helper function async
content = content.replace(
  /function createStaleSession\(/g,
  'async function createStaleSession('
);

// Write back
fs.writeFileSync(testFile, content);
console.log('✅ Tests updated to async');
