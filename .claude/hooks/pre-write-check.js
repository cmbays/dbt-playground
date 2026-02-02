#!/usr/bin/env node
/**
 * Pre-Write Hook: Quality gates for file writes
 *
 * Checks:
 * - Warns when overwriting key content files
 * - Reminds about temp folder workflow
 * - Validates file naming conventions
 */

const path = require('path');
const input = process.argv[2];

try {
  const toolInput = JSON.parse(input || '{}');
  const filePath = toolInput.file_path || '';
  const fileName = path.basename(filePath);
  const dirName = path.dirname(filePath);

  // Protected content files that should use temp workflow
  const protectedPaths = [
    /topics\/.*\/(phrases|dialogue|story|manga|quiz|tips)\.html$/,
    /kanji\/data\/.*\.js$/,
    /css\/shared\.css$/,
    /js\/shared\.js$/
  ];

  for (const pattern of protectedPaths) {
    if (pattern.test(filePath)) {
      console.error(`[HOOK REMINDER] Writing to protected content file: ${fileName}`);
      console.error('Per CLAUDE.md: Consider creating in temp/ first for review.');
    }
  }

  // Validate file naming conventions (lowercase with hyphens)
  if (fileName.includes('_') && !filePath.includes('node_modules')) {
    console.error(`[HOOK SUGGESTION] File name contains underscore: ${fileName}`);
    console.error('Project convention: Use lowercase-with-hyphens.ext');
  }

  // Warn about files outside expected directories
  const expectedDirs = [
    'topics', 'kanji', 'css', 'js', 'docs', 'temp', 'archive', '.claude'
  ];

  const topLevelDir = filePath.split('/').find(part =>
    part && !part.startsWith('.') && part !== 'Users' && part !== 'cmbays' &&
    part !== 'Documents' && part !== 'claude' && part !== 'japanese-study-site'
  );

  if (topLevelDir && !expectedDirs.includes(topLevelDir) && !fileName.includes('.')) {
    console.error(`[HOOK NOTE] Writing to unexpected directory: ${topLevelDir}`);
  }

  process.exit(0);
} catch (error) {
  console.error(`[HOOK ERROR] ${error.message}`);
  process.exit(0);
}
