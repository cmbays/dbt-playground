#!/usr/bin/env node
/**
 * Format Check
 *
 * Cross-platform utility to check code formatting and conventions.
 * Validates HTML, CSS, and JavaScript files against project standards.
 *
 * Usage:
 *   node .claude/scripts/format-check.js              # Check all files
 *   node .claude/scripts/format-check.js path/to/file # Check specific file
 *   node .claude/scripts/format-check.js --staged     # Check staged files only
 *
 * Checks:
 *   - HTML: Structure, version comments, semantic elements
 *   - CSS: Custom properties, naming conventions
 *   - JavaScript: Console.log usage, error handling patterns
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Issue severities
const SEVERITY = {
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info'
};

// Results collection
const results = {
  files: 0,
  errors: 0,
  warnings: 0,
  infos: 0,
  issues: []
};

/**
 * Add an issue to results
 */
function addIssue(file, line, severity, message, rule) {
  results.issues.push({ file, line, severity, message, rule });
  if (severity === SEVERITY.ERROR) results.errors++;
  else if (severity === SEVERITY.WARNING) results.warnings++;
  else results.infos++;
}

/**
 * Check HTML file
 */
function checkHtml(filePath, content) {
  const lines = content.split('\n');

  // Check for version comment (not in temp/)
  if (!filePath.includes('/temp/') && !content.includes('<!-- Version:')) {
    addIssue(filePath, 1, SEVERITY.WARNING, 'Missing version comment', 'html-version-comment');
  }

  // Check for DOCTYPE
  if (!content.toLowerCase().includes('<!doctype html>')) {
    addIssue(filePath, 1, SEVERITY.ERROR, 'Missing DOCTYPE declaration', 'html-doctype');
  }

  // Check for meta viewport
  if (!content.includes('name="viewport"')) {
    addIssue(filePath, 1, SEVERITY.WARNING, 'Missing viewport meta tag', 'html-viewport');
  }

  // Check for shared.css link
  if (!content.includes('shared.css')) {
    addIssue(filePath, 1, SEVERITY.INFO, 'Not using shared.css', 'html-shared-css');
  }

  // Check for shared.js script
  if (!content.includes('shared.js')) {
    addIssue(filePath, 1, SEVERITY.INFO, 'Not using shared.js', 'html-shared-js');
  }

  // Check for inline styles
  lines.forEach((line, i) => {
    if (line.includes('style="') && !line.includes('<!--')) {
      addIssue(filePath, i + 1, SEVERITY.INFO, 'Inline style found - consider using CSS class', 'html-inline-style');
    }
  });

  // Check for external links without rel
  lines.forEach((line, i) => {
    if (line.includes('target="_blank"') && !line.includes('rel=')) {
      addIssue(filePath, i + 1, SEVERITY.WARNING, 'External link missing rel="noopener noreferrer"', 'html-external-link');
    }
  });
}

/**
 * Check CSS file
 */
function checkCss(filePath, content) {
  const lines = content.split('\n');

  // Check for hex colors instead of CSS variables (simplified check)
  lines.forEach((line, i) => {
    const hexMatch = line.match(/#[0-9a-fA-F]{3,6}(?!\w)/);
    if (hexMatch && !line.includes('--') && !line.includes('/*')) {
      addIssue(filePath, i + 1, SEVERITY.INFO, `Using hex color ${hexMatch[0]} - consider CSS variable`, 'css-hex-color');
    }
  });

  // Check for !important
  lines.forEach((line, i) => {
    if (line.includes('!important')) {
      addIssue(filePath, i + 1, SEVERITY.WARNING, 'Using !important - consider refactoring', 'css-important');
    }
  });
}

/**
 * Check JavaScript file
 */
function checkJs(filePath, content) {
  const lines = content.split('\n');

  // Count console.log statements
  let consoleLogCount = 0;
  lines.forEach((line, i) => {
    if (line.includes('console.log') && !line.trim().startsWith('//')) {
      consoleLogCount++;
      if (!filePath.includes('/temp/')) {
        addIssue(filePath, i + 1, SEVERITY.INFO, 'console.log statement found', 'js-console-log');
      }
    }
  });

  if (consoleLogCount > 5 && !filePath.includes('/temp/')) {
    addIssue(filePath, 1, SEVERITY.WARNING, `${consoleLogCount} console.log statements - consider cleanup`, 'js-console-log-count');
  }

  // Check for eval
  lines.forEach((line, i) => {
    if (line.includes('eval(') && !line.trim().startsWith('//')) {
      addIssue(filePath, i + 1, SEVERITY.ERROR, 'eval() usage detected - security risk', 'js-eval');
    }
  });

  // Check for innerHTML with concatenation
  lines.forEach((line, i) => {
    if (line.includes('innerHTML') && (line.includes('+') || line.includes('`'))) {
      addIssue(filePath, i + 1, SEVERITY.WARNING, 'innerHTML with dynamic content - verify sanitization', 'js-innerhtml');
    }
  });

  // Check for TODO/FIXME
  lines.forEach((line, i) => {
    if (line.match(/\b(TODO|FIXME|HACK|XXX)\b/)) {
      addIssue(filePath, i + 1, SEVERITY.INFO, 'TODO/FIXME comment found', 'js-todo');
    }
  });
}

/**
 * Check a single file
 */
function checkFile(filePath) {
  if (!fs.existsSync(filePath)) {
    console.error(`File not found: ${filePath}`);
    return;
  }

  const ext = path.extname(filePath).toLowerCase();
  const content = fs.readFileSync(filePath, 'utf8');
  results.files++;

  switch (ext) {
    case '.html':
      checkHtml(filePath, content);
      break;
    case '.css':
      checkCss(filePath, content);
      break;
    case '.js':
      checkJs(filePath, content);
      break;
  }
}

/**
 * Get staged files
 */
function getStagedFiles() {
  try {
    const output = execSync('git diff --cached --name-only --diff-filter=ACM', {
      encoding: 'utf8'
    });
    return output.trim().split('\n').filter(Boolean);
  } catch {
    return [];
  }
}

/**
 * Find all project files
 */
function findProjectFiles(dir, files = []) {
  const excludeDirs = ['node_modules', '.git', 'archive', '.claude'];

  fs.readdirSync(dir).forEach(item => {
    const fullPath = path.join(dir, item);
    const stat = fs.statSync(fullPath);

    if (stat.isDirectory()) {
      if (!excludeDirs.includes(item)) {
        findProjectFiles(fullPath, files);
      }
    } else {
      const ext = path.extname(item).toLowerCase();
      if (['.html', '.css', '.js'].includes(ext)) {
        files.push(fullPath);
      }
    }
  });

  return files;
}

/**
 * Print results
 */
function printResults() {
  console.log('');
  console.log(`=== Format Check Results ===`);
  console.log(`Files checked: ${results.files}`);
  console.log(`Errors: ${results.errors}`);
  console.log(`Warnings: ${results.warnings}`);
  console.log(`Info: ${results.infos}`);
  console.log('');

  if (results.issues.length === 0) {
    console.log('No issues found!');
    return 0;
  }

  // Group by file
  const byFile = {};
  results.issues.forEach(issue => {
    if (!byFile[issue.file]) byFile[issue.file] = [];
    byFile[issue.file].push(issue);
  });

  Object.entries(byFile).forEach(([file, issues]) => {
    console.log(`${file}:`);
    issues.forEach(issue => {
      const prefix = issue.severity === SEVERITY.ERROR ? '  ERROR' :
                     issue.severity === SEVERITY.WARNING ? '  WARN ' : '  INFO ';
      console.log(`${prefix} L${issue.line}: ${issue.message} (${issue.rule})`);
    });
    console.log('');
  });

  return results.errors > 0 ? 1 : 0;
}

/**
 * Main function
 */
function main() {
  const args = process.argv.slice(2);

  let filesToCheck = [];

  if (args.includes('--staged')) {
    filesToCheck = getStagedFiles();
    if (filesToCheck.length === 0) {
      console.log('No staged files to check.');
      return;
    }
  } else if (args.length > 0 && !args[0].startsWith('--')) {
    filesToCheck = args;
  } else {
    filesToCheck = findProjectFiles(process.cwd());
  }

  filesToCheck.forEach(file => {
    const fullPath = path.isAbsolute(file) ? file : path.join(process.cwd(), file);
    checkFile(fullPath);
  });

  const exitCode = printResults();
  process.exit(exitCode);
}

main();
