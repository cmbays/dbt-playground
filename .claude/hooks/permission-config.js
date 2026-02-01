#!/usr/bin/env node
/**
 * Permission Auto-Approval Configuration
 *
 * Centralized patterns for the three-tier permission evaluation system:
 * - Tier 1: Hard blocks (dangerous operations - instant deny)
 * - Tier 2: Fast allows (safe operations - instant approve)
 * - Tier 3: Fallthrough to user prompt
 */

module.exports = {
  // ============================================
  // Tier 1: Hard Block Patterns (dangerous operations)
  // ============================================
  hardBlockPatterns: {
    bash: [
      // Destructive file operations
      /rm\s+-rf\s+\/(?!\w)/,           // rm -rf / (root)
      /rm\s+-rf\s+~\/?$/,              // rm -rf ~ (home)
      /rm\s+-rf\s+\.\.\/(?:\.\.\/)?/,  // rm -rf ../ (traversal)
      /rm\s+-rf\s+\*$/,                // rm -rf * (current dir wildcard)

      // Privilege escalation
      /sudo\s+/,                        // Any sudo command
      /su\s+-?\s*$/,                    // Switch user to root
      /chmod\s+777/,                    // World-writable permissions
      /chown\s+root/,                   // Change ownership to root

      // Dangerous git operations (without GIT_MASTER_AUTHORIZED)
      /^git\s+push\s+--force\s+(origin\s+)?(main|master)/,  // Force push to main
      /^git\s+push\s+-f\s+(origin\s+)?(main|master)/,       // Force push to main
      /^git\s+reset\s+--hard/,                               // Hard reset
      /^git\s+clean\s+-fd/,                                  // Force clean

      // Network attacks / remote code execution
      /curl.*\|\s*(ba)?sh/,            // Pipe curl to shell
      /wget.*\|\s*(ba)?sh/,            // Pipe wget to shell

      // System modification
      /shutdown\s+/,                    // System shutdown
      /reboot/,                         // System reboot
      /mkfs\./,                         // Format filesystem
      /dd\s+if=.*of=\/dev/,             // Direct disk write
    ],

    write: [
      /\.env$/,                         // Environment files
      /\.env\.(local|prod|production)$/,
      /credentials\.json$/,             // Credential files
      /secrets?\.(json|ya?ml|toml)$/,   // Secret files
      /\.git\/(?!info\/exclude)/,       // Git internals
      /\.(pem|key|crt|p12|pfx)$/,       // Certificates/keys
      /id_rsa|id_ed25519|id_dsa/,       // SSH keys
    ],

    edit: [
      /\.env$/,
      /\.env\.(local|prod|production)$/,
      /credentials\.json$/,
      /secrets?\.(json|ya?ml|toml)$/,
      /\.(pem|key|crt)$/,
      /id_rsa|id_ed25519/,
    ]
  },

  // ============================================
  // Tier 2: Fast Allow Patterns (safe operations)
  // ============================================
  fastAllowPatterns: {
    bash: [
      // File exploration (read-only)
      /^ls(\s|$)/,
      /^pwd\s*$/,
      /^cat\s+/,
      /^head\s+/,
      /^tail\s+/,
      /^find\s+/,
      /^grep\s+/,
      /^rg\s+/,
      /^tree\s*/,
      /^wc\s+/,
      /^file\s+/,

      // Git read operations
      /^git\s+status/,
      /^git\s+log/,
      /^git\s+diff/,
      /^git\s+show/,
      /^git\s+branch\s*$/,
      /^git\s+branch\s+-[lav]/,
      /^git\s+worktree\s+list/,
      /^git\s+remote\s+-v/,
      /^git\s+stash\s+list/,
      /^git\s+rev-parse/,
      /^git\s+fetch(?!\s.*--force)/,
      /^git\s+add\s+/,                  // Stage files (safe)

      // Git write operations (with GIT_MASTER_AUTHORIZED)
      /^GIT_MASTER_AUTHORIZED=true\s+git\s+/,

      // GitHub CLI read operations
      /^gh\s+pr\s+(list|view|status|checks|diff)/,
      /^gh\s+issue\s+(list|view|status)/,
      /^gh\s+repo\s+(list|view)/,
      /^gh\s+run\s+(list|view)/,
      /^gh\s+api\s+repos\//,
      /^gh\s+auth\s+status/,

      // GitHub CLI write operations (with GIT_MASTER_AUTHORIZED)
      /^GIT_MASTER_AUTHORIZED=true\s+gh\s+/,

      // dbt operations (all safe in dev context)
      /^(uv\s+run\s+)?dbt\s+(build|test|run|compile|parse)/,
      /^(uv\s+run\s+)?dbt\s+(list|ls|show|debug|deps)/,
      /^(uv\s+run\s+)?dbt\s+docs\s+(generate|serve)/,
      /^(uv\s+run\s+)?dbt\s+source\s+freshness/,
      /^(uv\s+run\s+)?dbt\s+seed/,
      /^(uv\s+run\s+)?dbt\s+snapshot/,

      // Python/uv operations
      /^uv\s+(sync|tree|pip\s+list|pip\s+show)/,
      /^uv\s+run\s+/,
      /^python\s+--version/,
      /^python3?\s+-c/,
      /^pip\s+(list|show|freeze)/,

      // Node/npm operations
      /^npm\s+(list|ls|outdated|audit)/,
      /^npm\s+run\s+(lint|test|typecheck|check)/,
      /^npm\s+test/,
      /^node\s+--version/,
      /^node\s+/,

      // Testing/linting
      /^(uv\s+run\s+)?pytest/,
      /^(uv\s+run\s+)?sqlfluff/,
      /^(uv\s+run\s+)?ruff/,

      // General utilities
      /^echo\s+/,
      /^which\s+/,
      /^type\s+/,
      /^date/,
      /^env\s*$/,
      /^printenv/,
    ],

    // All read operations are safe
    read: [/./],
    glob: [/./],
    grep: [/./],
  },

  // ============================================
  // Audit Configuration
  // ============================================
  auditConfig: {
    logFile: '.claude/hooks/audit/permission-decisions.jsonl',
    logLevel: 'info',
  },

  // ============================================
  // Block Messages
  // ============================================
  blockMessages: {
    destructiveGit: 'Destructive git operation blocked. Use git-master: git: <operation>',
    credentialWrite: 'Cannot write to credential/secret files.',
    rootDelete: 'Cannot delete root or home directories.',
    privilegeEscalation: 'Privilege escalation (sudo) not allowed.',
    remoteExec: 'Remote code execution patterns blocked.',
  }
};
