#!/usr/bin/env node
/**
 * Permission Auto-Approval Hook
 *
 * Three-tier permission evaluation:
 * - Tier 1: Hard block dangerous operations
 * - Tier 2: Fast allow safe operations
 * - Tier 3: Fall through to user prompt
 *
 * Input: JSON via stdin (PermissionRequest event)
 * Output: JSON to stdout with decision
 */

const config = require('./permission-config');
const audit = require('./audit/logger');

async function readStdin() {
  return new Promise((resolve) => {
    let data = '';
    process.stdin.setEncoding('utf8');
    process.stdin.on('data', chunk => { data += chunk; });
    process.stdin.on('end', () => { resolve(data); });
    setTimeout(() => { if (!data) resolve(''); }, 5000);
  });
}

function outputDecision(behavior, message = null) {
  const output = {
    hookSpecificOutput: {
      hookEventName: 'PermissionRequest',
      decision: { behavior }
    }
  };
  if (message && behavior === 'deny') {
    output.hookSpecificOutput.decision.message = message;
  }
  console.log(JSON.stringify(output));
}

function matchesAnyPattern(input, patterns) {
  if (!patterns || !Array.isArray(patterns)) return { matches: false };
  for (const pattern of patterns) {
    if (pattern.test(input)) {
      return { matches: true, pattern: pattern.toString() };
    }
  }
  return { matches: false };
}

function normalizePath(filePath) {
  if (!filePath) return '';
  return filePath.replace(/^\.\//, '').replace(/\/+/g, '/');
}

function getBlockMessage(toolName, matchedPattern) {
  const pattern = matchedPattern.toLowerCase();
  if (pattern.includes('push') && (pattern.includes('force') || pattern.includes('-f'))) {
    return config.blockMessages.destructiveGit;
  }
  if (pattern.includes('reset') && pattern.includes('hard')) {
    return config.blockMessages.destructiveGit;
  }
  if (pattern.includes('rm') && pattern.includes('rf')) {
    return config.blockMessages.rootDelete;
  }
  if (pattern.includes('sudo')) {
    return config.blockMessages.privilegeEscalation;
  }
  if (pattern.includes('curl') && pattern.includes('sh')) {
    return config.blockMessages.remoteExec;
  }
  if (pattern.includes('env') || pattern.includes('credential') || pattern.includes('secret')) {
    return config.blockMessages.credentialWrite;
  }
  return `Operation blocked by security policy: ${toolName}`;
}

function evaluateBashPermission(command, context) {
  // Tier 1: Check hard blocks
  const hardBlock = matchesAnyPattern(command, config.hardBlockPatterns.bash);
  if (hardBlock.matches) {
    const message = getBlockMessage('Bash', hardBlock.pattern);
    audit.logBlock(context, hardBlock.pattern);
    outputDecision('deny', message);
    return true;
  }

  // Tier 2: Check fast allows
  const fastAllow = matchesAnyPattern(command, config.fastAllowPatterns.bash);
  if (fastAllow.matches) {
    audit.logAllow(context, fastAllow.pattern);
    outputDecision('allow');
    return true;
  }

  // Tier 3: Fall through
  audit.logFallthrough(context, 'no matching bash pattern');
  return false;
}

function evaluateWritePermission(filePath, toolName, context) {
  const normalizedPath = normalizePath(filePath);
  const patterns = config.hardBlockPatterns[toolName.toLowerCase()];

  // Tier 1: Check hard blocks for sensitive files
  const hardBlock = matchesAnyPattern(normalizedPath, patterns);
  if (hardBlock.matches) {
    audit.logBlock(context, hardBlock.pattern);
    outputDecision('deny', config.blockMessages.credentialWrite);
    return true;
  }

  // Fall through for writes (conservative)
  audit.logFallthrough(context, 'write operations require confirmation');
  return false;
}

function evaluateReadPermission(context) {
  // All read operations are safe
  audit.logAllow(context, 'read operations always allowed');
  outputDecision('allow');
  return true;
}

async function evaluatePermission(request) {
  const { tool_name: toolName, tool_input: toolInput, cwd } = request;
  const context = { tool: toolName, input: toolInput, cwd: cwd || process.cwd() };

  switch (toolName) {
    case 'Bash':
      return evaluateBashPermission(toolInput?.command || '', context);
    case 'Write':
    case 'Edit':
      return evaluateWritePermission(toolInput?.file_path || '', toolName, context);
    case 'Read':
    case 'Glob':
    case 'Grep':
      return evaluateReadPermission(context);
    default:
      audit.logFallthrough(context, `unknown tool: ${toolName}`);
      return false;
  }
}

async function main() {
  try {
    const input = await readStdin();
    if (!input || !input.trim()) {
      process.exit(0);
    }

    let request;
    try {
      request = JSON.parse(input);
    } catch (parseError) {
      console.error(`[PERMISSION HOOK] Parse error: ${parseError.message}`);
      process.exit(0);
    }

    await evaluatePermission(request);
    process.exit(0);
  } catch (error) {
    console.error(`[PERMISSION HOOK ERROR] ${error.message}`);
    process.exit(0);
  }
}

main();
