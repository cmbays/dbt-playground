#!/usr/bin/env node
/**
 * Doc Health Audit
 *
 * Zero-dependency documentation quality checker for markdown files.
 * Checks markdown lint rules, stale docs, broken links, orphan files,
 * and frontmatter completeness.
 *
 * Usage:
 *   node .claude/scripts/doc-health.js              # Full audit
 *   node .claude/scripts/doc-health.js --lint        # Lint only
 *   node .claude/scripts/doc-health.js --path docs/  # Specific directory
 *   node .claude/scripts/doc-health.js --json        # JSON output
 */

const fs = require('fs');
const path = require('path');

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const SEVERITY = { ERROR: 'error', WARNING: 'warning', INFO: 'info' };

const STALE_DAYS = 90;

const REQUIRED_FRONTMATTER = ['audience', 'priority', 'size', 'status', 'last_updated'];

const EXCLUDE_DIRS = ['node_modules', '.git', 'archive', 'temp'];

const PROJECT_ROOT = findProjectRoot();

// ---------------------------------------------------------------------------
// Results accumulator
// ---------------------------------------------------------------------------

const results = {
  files: 0,
  errors: 0,
  warnings: 0,
  infos: 0,
  issues: []
};

function addIssue(file, line, severity, message, rule) {
  results.issues.push({ file: path.relative(PROJECT_ROOT, file), line, severity, message, rule });
  if (severity === SEVERITY.ERROR) results.errors++;
  else if (severity === SEVERITY.WARNING) results.warnings++;
  else results.infos++;
}

// ---------------------------------------------------------------------------
// Utility helpers
// ---------------------------------------------------------------------------

function findProjectRoot() {
  let dir = __dirname;
  for (let i = 0; i < 10; i++) {
    if (fs.existsSync(path.join(dir, 'CLAUDE.md'))) return dir;
    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  return process.cwd();
}

function findMarkdownFiles(dir) {
  const files = [];
  if (!fs.existsSync(dir)) return files;

  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      const rel = path.relative(PROJECT_ROOT, full);
      const top = rel.split(path.sep)[0];
      if (!EXCLUDE_DIRS.includes(top) && !EXCLUDE_DIRS.includes(entry.name)) {
        files.push(...findMarkdownFiles(full));
      }
    } else if (entry.name.endsWith('.md')) {
      files.push(full);
    }
  }
  return files;
}

/**
 * Parse YAML frontmatter (simple key: value parser, no deps).
 * Returns null if no frontmatter found.
 */
function parseFrontmatter(content) {
  if (!content.startsWith('---')) return null;
  const end = content.indexOf('\n---', 3);
  if (end === -1) return null;
  const yaml = content.substring(4, end);
  const fields = {};
  for (const line of yaml.split('\n')) {
    const match = line.match(/^(\w[\w_-]*):\s*(.*)/);
    if (match) {
      fields[match[1]] = match[2].trim().replace(/^["']|["']$/g, '');
    }
  }
  return fields;
}

// ---------------------------------------------------------------------------
// Markdown lint rules
// ---------------------------------------------------------------------------

function lintMarkdown(filePath, content) {
  const lines = content.split('\n');
  const len = lines.length;

  for (let i = 0; i < len; i++) {
    const line = lines[i];
    const lineNum = i + 1;
    const prevLine = i > 0 ? lines[i - 1] : '';
    const nextLine = i < len - 1 ? lines[i + 1] : '';

    // MD022: Blank lines around headings
    if (/^#{1,6}\s/.test(line)) {
      if (i > 0 && prevLine.trim() !== '' && !prevLine.startsWith('---')) {
        addIssue(filePath, lineNum, SEVERITY.WARNING,
          'Heading should have a blank line before it', 'MD022');
      }
      if (i < len - 1 && nextLine.trim() !== '') {
        addIssue(filePath, lineNum, SEVERITY.WARNING,
          'Heading should have a blank line after it', 'MD022');
      }
    }

    // MD031: Blank lines around fenced code blocks
    if (/^```/.test(line)) {
      if (i > 0 && prevLine.trim() !== '' && !prevLine.startsWith('---')) {
        addIssue(filePath, lineNum, SEVERITY.WARNING,
          'Fenced code block should have a blank line before it', 'MD031');
      }
      // Find closing fence
      if (line.trim().length > 3 || /^```\w/.test(line.trim())) {
        // Opening fence — check line after closing fence
      } else if (line.trim() === '```') {
        // Could be opening or closing; check if blank after
        if (i < len - 1 && nextLine.trim() !== '') {
          // Only flag closing fences (heuristic: previous non-empty line is code)
          // We'll keep it simple and check both
          addIssue(filePath, lineNum, SEVERITY.WARNING,
            'Fenced code block should have a blank line after it', 'MD031');
        }
      }
    }

    // MD040: Fenced code blocks should specify a language
    if (/^```\s*$/.test(line)) {
      // Could be opening or closing. Opening if there's a later closing ```.
      // Simple heuristic: if previous line is blank or this is near start, it's opening.
      const isOpening = i === 0 || prevLine.trim() === '' || /^#{1,6}\s/.test(prevLine) || /^[-*]\s/.test(prevLine);
      if (isOpening) {
        addIssue(filePath, lineNum, SEVERITY.INFO,
          'Fenced code block should specify a language', 'MD040');
      }
    }

    // MD032: Blank lines around lists
    if (/^(\s*[-*+]|\s*\d+[.)]\s)/.test(line)) {
      // First list item — check blank line before
      if (i > 0 && !/^(\s*[-*+]|\s*\d+[.)]\s)/.test(prevLine) && prevLine.trim() !== '' && !prevLine.startsWith('---')) {
        addIssue(filePath, lineNum, SEVERITY.WARNING,
          'List should have a blank line before it', 'MD032');
      }
    }
    // Last list item — check blank line after
    if (/^(\s*[-*+]|\s*\d+[.)]\s)/.test(line)) {
      if (i < len - 1 && !/^(\s*[-*+]|\s*\d+[.)]\s)/.test(nextLine) && nextLine.trim() !== '' && !nextLine.startsWith('```')) {
        addIssue(filePath, lineNum, SEVERITY.WARNING,
          'List should have a blank line after it', 'MD032');
      }
    }

    // MD029: Ordered list prefix consistency (expects sequential)
    if (/^\s*(\d+)[.)]\s/.test(line)) {
      const num = parseInt(line.match(/^\s*(\d+)/)[1], 10);
      if (/^\s*(\d+)[.)]\s/.test(prevLine)) {
        const prevNum = parseInt(prevLine.match(/^\s*(\d+)/)[1], 10);
        if (num !== prevNum + 1) {
          addIssue(filePath, lineNum, SEVERITY.INFO,
            `Ordered list prefix should be ${prevNum + 1} (found ${num})`, 'MD029');
        }
      }
    }

    // MD009: No trailing spaces (except line break = 2 spaces)
    if (/\s+$/.test(line) && !/\s{2}$/.test(line)) {
      addIssue(filePath, lineNum, SEVERITY.INFO,
        'Trailing spaces', 'MD009');
    }

    // MD047: File should end with a single newline (check on last line)
    if (i === len - 1 && line !== '' && content.endsWith('\n') === false) {
      addIssue(filePath, lineNum, SEVERITY.INFO,
        'File should end with a newline', 'MD047');
    }
  }

  // MD060: Table formatting — check pipes are balanced
  const tableLines = [];
  for (let i = 0; i < len; i++) {
    if (/^\|.*\|$/.test(lines[i].trim())) {
      tableLines.push(i);
    }
  }
  if (tableLines.length > 0) {
    // Check that all table rows in a block have same pipe count
    let blockStart = tableLines[0];
    let expectedPipes = (lines[tableLines[0]].match(/\|/g) || []).length;
    for (let t = 1; t < tableLines.length; t++) {
      if (tableLines[t] !== tableLines[t - 1] + 1) {
        // New table block
        blockStart = tableLines[t];
        expectedPipes = (lines[tableLines[t]].match(/\|/g) || []).length;
        continue;
      }
      const pipes = (lines[tableLines[t]].match(/\|/g) || []).length;
      if (pipes !== expectedPipes) {
        addIssue(filePath, tableLines[t] + 1, SEVERITY.WARNING,
          `Table row has ${pipes} pipes, expected ${expectedPipes}`, 'MD060');
      }
    }
  }
}

// ---------------------------------------------------------------------------
// Stale doc detection
// ---------------------------------------------------------------------------

function checkStaleDocs(filePath, frontmatter) {
  if (!frontmatter || !frontmatter.last_updated) {
    addIssue(filePath, 1, SEVERITY.INFO,
      'Missing last_updated in frontmatter', 'STALE001');
    return;
  }

  const updated = new Date(frontmatter.last_updated);
  if (isNaN(updated.getTime())) {
    addIssue(filePath, 1, SEVERITY.WARNING,
      `Invalid last_updated date: ${frontmatter.last_updated}`, 'STALE002');
    return;
  }

  const daysSince = Math.floor((Date.now() - updated.getTime()) / (1000 * 60 * 60 * 24));
  if (daysSince > STALE_DAYS) {
    addIssue(filePath, 1, SEVERITY.WARNING,
      `Document is ${daysSince} days old (last updated: ${frontmatter.last_updated})`, 'STALE003');
  }
}

// ---------------------------------------------------------------------------
// Broken internal link detection
// ---------------------------------------------------------------------------

function checkLinks(filePath, content) {
  const lines = content.split('\n');
  const dir = path.dirname(filePath);

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const lineNum = i + 1;

    // Wiki-style links: [[target]]
    const wikiRe = /\[\[([^\]]+)\]\]/g;
    let match;
    while ((match = wikiRe.exec(line)) !== null) {
      const target = match[1].replace(/#.*$/, '').trim();
      if (!target) continue;
      const resolved = resolveLink(dir, target);
      if (!resolved) {
        addIssue(filePath, lineNum, SEVERITY.ERROR,
          `Broken wiki link: [[${match[1]}]]`, 'LINK001');
      }
    }

    // Markdown links: [text](path) — skip URLs
    const mdRe = /\[([^\]]*)\]\(([^)]+)\)/g;
    while ((match = mdRe.exec(line)) !== null) {
      const href = match[2].replace(/#.*$/, '').trim();
      if (!href || href.startsWith('http://') || href.startsWith('https://') || href.startsWith('mailto:')) continue;
      const resolved = resolveLink(dir, href);
      if (!resolved) {
        addIssue(filePath, lineNum, SEVERITY.ERROR,
          `Broken link: [${match[1]}](${match[2]})`, 'LINK002');
      }
    }
  }
}

function resolveLink(fromDir, target) {
  // Try relative to file dir
  const abs = path.resolve(fromDir, target);
  if (fs.existsSync(abs)) return abs;
  // Try with .md extension
  if (!path.extname(target) && fs.existsSync(abs + '.md')) return abs + '.md';
  // Try relative to project root
  const fromRoot = path.resolve(PROJECT_ROOT, target);
  if (fs.existsSync(fromRoot)) return fromRoot;
  if (!path.extname(target) && fs.existsSync(fromRoot + '.md')) return fromRoot + '.md';
  return null;
}

// ---------------------------------------------------------------------------
// Orphan doc detection
// ---------------------------------------------------------------------------

function checkOrphans(allFiles) {
  // Read index files that should reference other docs
  const indexFiles = [
    path.join(PROJECT_ROOT, 'CLAUDE.md'),
    path.join(PROJECT_ROOT, 'docs', 'README.md')
  ];

  let indexContent = '';
  for (const idx of indexFiles) {
    if (fs.existsSync(idx)) {
      indexContent += fs.readFileSync(idx, 'utf8') + '\n';
    }
  }

  // Also collect all links across all docs (broader reference check)
  let allContent = indexContent;
  for (const f of allFiles) {
    allContent += fs.readFileSync(f, 'utf8') + '\n';
  }

  for (const f of allFiles) {
    const rel = path.relative(PROJECT_ROOT, f);
    // Skip files in temp/ and archive/
    if (rel.startsWith('temp') || rel.startsWith('archive')) continue;
    // Skip index files themselves
    if (rel === 'CLAUDE.md' || rel === 'README.md' || rel === 'CHANGELOG.md') continue;

    const basename = path.basename(f);
    const relForward = rel.replace(/\\/g, '/');

    // Check if any reference to this file exists
    const referenced =
      allContent.includes(relForward) ||
      allContent.includes(basename) ||
      allContent.includes(relForward.replace(/\.md$/, ''));

    if (!referenced) {
      addIssue(f, 1, SEVERITY.INFO,
        'Document not referenced from any other doc', 'ORPHAN001');
    }
  }
}

// ---------------------------------------------------------------------------
// Frontmatter completeness
// ---------------------------------------------------------------------------

function checkFrontmatter(filePath, frontmatter) {
  // Only enforce for docs/ directory
  const rel = path.relative(PROJECT_ROOT, filePath);
  if (!rel.startsWith('docs')) return;

  if (!frontmatter) {
    addIssue(filePath, 1, SEVERITY.INFO,
      'No YAML frontmatter found', 'FM001');
    return;
  }

  const missing = REQUIRED_FRONTMATTER.filter(f => !frontmatter[f]);
  if (missing.length > 0) {
    addIssue(filePath, 1, SEVERITY.INFO,
      `Missing frontmatter fields: ${missing.join(', ')}`, 'FM002');
  }
}

// ---------------------------------------------------------------------------
// Output
// ---------------------------------------------------------------------------

function printText() {
  console.log('');
  console.log('=== Doc Health Report ===');
  console.log(`Files checked: ${results.files}`);
  console.log(`Errors: ${results.errors}  Warnings: ${results.warnings}  Info: ${results.infos}`);
  console.log('');

  if (results.issues.length === 0) {
    console.log('No issues found!');
    return;
  }

  const byFile = {};
  for (const issue of results.issues) {
    if (!byFile[issue.file]) byFile[issue.file] = [];
    byFile[issue.file].push(issue);
  }

  for (const [file, issues] of Object.entries(byFile)) {
    console.log(`${file}:`);
    for (const issue of issues) {
      const prefix = issue.severity === SEVERITY.ERROR ? '  ERROR' :
                     issue.severity === SEVERITY.WARNING ? '  WARN ' : '  INFO ';
      console.log(`${prefix} L${issue.line}: ${issue.message} (${issue.rule})`);
    }
    console.log('');
  }
}

function printJson() {
  const output = {
    summary: {
      files: results.files,
      errors: results.errors,
      warnings: results.warnings,
      infos: results.infos
    },
    issues: results.issues
  };
  console.log(JSON.stringify(output, null, 2));
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

function main() {
  const args = process.argv.slice(2);
  const jsonOutput = args.includes('--json');
  const lintOnly = args.includes('--lint');

  let searchPath = PROJECT_ROOT;
  const pathIdx = args.indexOf('--path');
  if (pathIdx !== -1 && args[pathIdx + 1]) {
    searchPath = path.resolve(args[pathIdx + 1]);
  }

  if (!jsonOutput) {
    process.stderr.write(`Scanning ${path.relative(PROJECT_ROOT, searchPath) || '.'} for markdown files...\n`);
  }

  const allFiles = findMarkdownFiles(searchPath);
  results.files = allFiles.length;

  if (!jsonOutput) {
    process.stderr.write(`Found ${allFiles.length} markdown files\n`);
  }

  for (const filePath of allFiles) {
    const content = fs.readFileSync(filePath, 'utf8');
    const frontmatter = parseFrontmatter(content);

    // Always lint
    lintMarkdown(filePath, content);

    if (!lintOnly) {
      checkStaleDocs(filePath, frontmatter);
      checkLinks(filePath, content);
      checkFrontmatter(filePath, frontmatter);
    }
  }

  if (!lintOnly) {
    checkOrphans(allFiles);
  }

  if (jsonOutput) {
    printJson();
  } else {
    printText();
  }

  process.exit(results.errors > 0 ? 1 : 0);
}

main();
