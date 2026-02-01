#!/usr/bin/env node
/**
 * Audit Logger for Permission Auto-Approval System
 */

const fs = require('fs');
const path = require('path');

let config;
try {
  config = require('../permission-config');
} catch (e) {
  config = { auditConfig: { logFile: '.claude/hooks/audit/permission-decisions.jsonl' } };
}

function getSessionId() {
  return process.env.CLAUDE_SESSION_ID || process.env.TERM_SESSION_ID || `session-${Date.now()}`;
}

function ensureAuditDir(logPath) {
  const dir = path.dirname(logPath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function summarizeInput(input) {
  if (!input) return 'empty';
  if (input.command) {
    const cmd = input.command;
    return cmd.length > 100 ? cmd.substring(0, 100) + '...' : cmd;
  }
  if (input.file_path) return `file: ${input.file_path}`;
  if (input.pattern) return `pattern: ${input.pattern}`;
  return JSON.stringify(input).substring(0, 100);
}

function logDecision(context, decision, tier, reason = null, metadata = {}) {
  try {
    const logPath = path.resolve(process.cwd(), config.auditConfig.logFile);
    ensureAuditDir(logPath);

    const entry = {
      timestamp: new Date().toISOString(),
      session_id: getSessionId(),
      tool: context.tool || 'unknown',
      input_summary: summarizeInput(context.input),
      cwd: context.cwd || process.cwd(),
      decision,
      tier,
      reason,
      ...metadata
    };

    fs.appendFileSync(logPath, JSON.stringify(entry) + '\n');
    return true;
  } catch (error) {
    console.error(`[AUDIT WARNING] ${error.message}`);
    return false;
  }
}

function logBlock(context, reason) {
  return logDecision(context, 'deny', 1, reason);
}

function logAllow(context, matchedPattern = null) {
  return logDecision(context, 'allow', 2, null, { matched_pattern: matchedPattern });
}

function logFallthrough(context, reason = 'no matching pattern') {
  return logDecision(context, 'fallthrough', 0, reason);
}

module.exports = { logDecision, logBlock, logAllow, logFallthrough, summarizeInput };
