#!/usr/bin/env node
/**
 * Detect Package Manager
 *
 * Cross-platform utility to detect which package manager is available
 * and should be used for the project.
 *
 * Usage:
 *   node .claude/scripts/detect-package-manager.js
 *   node .claude/scripts/detect-package-manager.js --install lodash
 *   node .claude/scripts/detect-package-manager.js --run dev
 *
 * Returns:
 *   - JSON with detected package manager info
 *   - Or executes command with appropriate package manager
 */

const { execSync, spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Package manager detection order (preference)
const PACKAGE_MANAGERS = [
  {
    name: 'pnpm',
    lockfile: 'pnpm-lock.yaml',
    check: 'pnpm --version',
    install: 'pnpm add',
    installDev: 'pnpm add -D',
    run: 'pnpm run',
    exec: 'pnpm exec'
  },
  {
    name: 'yarn',
    lockfile: 'yarn.lock',
    check: 'yarn --version',
    install: 'yarn add',
    installDev: 'yarn add -D',
    run: 'yarn',
    exec: 'yarn'
  },
  {
    name: 'npm',
    lockfile: 'package-lock.json',
    check: 'npm --version',
    install: 'npm install',
    installDev: 'npm install -D',
    run: 'npm run',
    exec: 'npx'
  }
];

/**
 * Check if a command is available
 */
function isCommandAvailable(command) {
  try {
    execSync(command, { stdio: 'ignore' });
    return true;
  } catch {
    return false;
  }
}

/**
 * Check if lockfile exists in current directory
 */
function hasLockfile(lockfile) {
  return fs.existsSync(path.join(process.cwd(), lockfile));
}

/**
 * Detect the best package manager to use
 */
function detectPackageManager() {
  // First, check for lockfiles (indicates project preference)
  for (const pm of PACKAGE_MANAGERS) {
    if (hasLockfile(pm.lockfile)) {
      if (isCommandAvailable(pm.check)) {
        return { ...pm, detected: 'lockfile', available: true };
      }
    }
  }

  // No lockfile found, use first available package manager
  for (const pm of PACKAGE_MANAGERS) {
    if (isCommandAvailable(pm.check)) {
      return { ...pm, detected: 'available', available: true };
    }
  }

  return { name: 'none', detected: 'none', available: false };
}

/**
 * Execute a package manager command
 */
function executeCommand(pm, action, args) {
  let command;

  switch (action) {
    case 'install':
      command = `${pm.install} ${args.join(' ')}`;
      break;
    case 'install-dev':
      command = `${pm.installDev} ${args.join(' ')}`;
      break;
    case 'run':
      command = `${pm.run} ${args.join(' ')}`;
      break;
    case 'exec':
      command = `${pm.exec} ${args.join(' ')}`;
      break;
    default:
      console.error(`Unknown action: ${action}`);
      process.exit(1);
  }

  console.log(`Running: ${command}`);

  const result = spawnSync(command, {
    stdio: 'inherit',
    shell: true,
    cwd: process.cwd()
  });

  process.exit(result.status || 0);
}

/**
 * Main function
 */
function main() {
  const args = process.argv.slice(2);
  const pm = detectPackageManager();

  // No arguments - just output detection info
  if (args.length === 0) {
    console.log(JSON.stringify({
      packageManager: pm.name,
      detected: pm.detected,
      available: pm.available,
      commands: pm.available ? {
        install: pm.install,
        installDev: pm.installDev,
        run: pm.run,
        exec: pm.exec
      } : null
    }, null, 2));
    return;
  }

  // Check if package manager is available
  if (!pm.available) {
    console.error('No package manager detected. Please install npm, yarn, or pnpm.');
    process.exit(1);
  }

  // Parse action and arguments
  const action = args[0].replace(/^--/, '');
  const actionArgs = args.slice(1);

  executeCommand(pm, action, actionArgs);
}

main();
