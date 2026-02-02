#!/usr/bin/env node
/**
 * Pre-Bash Hook: Quality gates for Bash commands
 *
 * Checks:
 * - BLOCKS destructive git operations (requires explicit approval)
 * - BLOCKS git write operations without git-master authorization
 * - Warns about long-running commands without timeout
 * - Reminds about dev servers requiring background mode
 *
 * Authorization:
 * - Git write operations require GIT_MASTER_AUTHORIZED=true env var
 * - Use --bypass-git-master flag for emergencies (logged to audit)
 */

const input = process.argv[2];

try {
  const toolInput = JSON.parse(input || '{}');
  const command = toolInput.command || '';

  // Check for bypass flag (emergency use only)
  const hasBypass = command.includes('--bypass-git-master');
  const isAuthorized = process.env.GIT_MASTER_AUTHORIZED === 'true';

  // Log bypass attempts to audit trail
  if (hasBypass) {
    const timestamp = new Date().toISOString();
    console.error(`[AUDIT] Bypass flag used at ${timestamp}: ${command}`);
    // Allow but log the bypass
  }

  // Block destructive git operations without explicit approval
  const destructivePatterns = [
    /git\s+reset\s+--hard/,
    /git\s+push\s+--force/,
    /git\s+push\s+-f/,
    /git\s+clean\s+-f/,
    /git\s+branch\s+-D/,
    /git\s+checkout\s+\.\s*$/,
    /git\s+restore\s+\.\s*$/,
    /rm\s+-rf\s+\//,
    /rm\s+-rf\s+\*/
  ];

  for (const pattern of destructivePatterns) {
    if (pattern.test(command) && !hasBypass) {
      console.error(`[HOOK BLOCKED] Destructive command blocked: ${command}`);
      console.error('This command may cause data loss and requires explicit user approval.');
      console.error('Use git-master for safety validation: git: <describe operation>');
      console.error('Emergency bypass: Add --bypass-git-master flag (logged to audit)');
      process.exit(1);
    }
  }

  // Block git write operations without authorization (Layer 2 enforcement)
  const gitWritePatterns = [
    /git\s+commit/,
    /git\s+push(?!\s+--force)/,  // Non-force push (force handled above)
    /git\s+merge/,
    /git\s+tag\s+-a/,
    /git\s+tag\s+v/,             // Version tags
    /git\s+branch\s+[^-dDlv]/,   // Branch creation (not list/delete)
    /git\s+checkout\s+-b/,       // New branch checkout
    /git\s+switch\s+-c/,         // New branch switch
    /gh\s+pr\s+merge/,
    /gh\s+pr\s+create/
  ];

  for (const pattern of gitWritePatterns) {
    if (pattern.test(command) && !isAuthorized && !hasBypass) {
      console.error(`[HOOK BLOCKED] Git write operation requires git-master authorization.`);
      console.error(`Command: ${command}`);
      console.error('');
      console.error('Git write operations must go through git-master for:');
      console.error('  - Commit message validation (Conventional Commits)');
      console.error('  - Branch naming enforcement');
      console.error('  - Safety checks and audit trail');
      console.error('');
      console.error('Use: git: <your operation request>');
      console.error('Example: git: commit my changes with message "feat(kanji): add filter"');
      console.error('');
      console.error('Emergency bypass: Add --bypass-git-master flag (logged to audit)');
      process.exit(1);
    }
  }

  // Warn about dev servers that should run in background
  const devServerPatterns = [
    /python\s+-m\s+http\.server/,
    /npm\s+run\s+(dev|start|serve)/,
    /npx\s+(vite|serve)/,
    /live-server/
  ];

  for (const pattern of devServerPatterns) {
    if (pattern.test(command) && !toolInput.run_in_background) {
      console.error('[HOOK REMINDER] Dev server detected. Consider using run_in_background: true');
    }
  }

  // Warn about commands that might take a long time
  const longRunningPatterns = [
    /npm\s+install(?!\s+\w)/,  // npm install without specific package
    /npm\s+ci/,
    /pip\s+install\s+-r/
  ];

  for (const pattern of longRunningPatterns) {
    if (pattern.test(command) && !toolInput.timeout) {
      console.error('[HOOK REMINDER] Long-running command detected. Consider setting a timeout.');
    }
  }

  process.exit(0);
} catch (error) {
  // Don't block on hook errors
  console.error(`[HOOK ERROR] ${error.message}`);
  process.exit(0);
}
