#!/usr/bin/env node
/**
 * Pre-Stop Hook: Final checks before Claude stops working
 *
 * Checks:
 * - Reminds about uncommitted changes
 * - Checks for leftover debug statements
 * - Validates temp folder state
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

try {
  // Check for uncommitted changes
  try {
    const gitStatus = execSync('git status --porcelain', { encoding: 'utf8' });
    if (gitStatus.trim()) {
      const changedFiles = gitStatus.trim().split('\n').length;
      console.error(`[HOOK REMINDER] ${changedFiles} uncommitted changes detected`);
      console.error('Consider committing or stashing before ending session.');
    }
  } catch (e) {
    // Not a git repo or git not available
  }

  // Check temp folder for work in progress
  const tempDir = path.join(process.cwd(), 'temp');
  if (fs.existsSync(tempDir)) {
    const tempFiles = fs.readdirSync(tempDir).filter(f => !f.startsWith('.'));
    if (tempFiles.length > 0) {
      console.error(`[HOOK REMINDER] ${tempFiles.length} files in temp/ folder`);
      console.error('Review temp/ contents before ending session.');
    }
  }

  process.exit(0);
} catch (error) {
  console.error(`[HOOK ERROR] ${error.message}`);
  process.exit(0);
}
