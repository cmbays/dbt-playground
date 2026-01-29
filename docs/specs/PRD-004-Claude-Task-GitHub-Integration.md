# PRD-004: Claude Task GitHub Integration MVP

**Status**: Draft
**Author**: PM (Claude)
**Created**: 2026-01-25
**Updated**: 2026-01-25

**Related Issue**: TBD (Epic issue to be created)
**Milestone**: TBD
**Technical Design**: TDD-004 (to be created)

---

## Problem Statement

Multi-agent workflows in Claude Code currently lack cross-session task persistence and GitHub issue integration. When orchestrating complex features across multiple personas (PM → Architect → Developer → Reviewer), tasks created in one session disappear when the session ends, forcing manual recreation and loss of context.

Additionally, there's no formalized connection between Claude's task primitives and GitHub issues. While we maintain GitHub issues as the source of truth for project management, agents have no standardized way to:

1. Convert GitHub issues into Claude tasks for session-level work
2. Sync task completion status back to GitHub
3. Track Epic → TDD → Task dependencies with validated metadata
4. Coordinate agent handoffs with formal metadata conventions

This creates friction in workflows like Epic → TDD → Task orchestration, where multiple agents need to hand off work with dependency tracking and context preservation.

## User Benefit

### For Christopher (Project Owner)
- **Cross-session persistence**: Tasks survive session restarts, enabling multi-day agent workflows
- **GitHub integration**: GitHub issues easily converted to Claude tasks for agent work
- **Clear orchestration**: Epic → TDD → Task workflows formalized with validated metadata
- **Reduced manual work**: No need to manually recreate tasks or track agent handoffs

### For Claude Agents
- **Validated metadata**: Schema validation prevents metadata errors and enables reliable agent coordination
- **Dependency tracking**: Tasks can block/be blocked by other tasks with formal metadata
- **Context preservation**: Metadata carries Epic ID, TDD section, GitHub issue number across sessions
- **Opt-in sync**: Agents can choose to auto-sync task completion to GitHub or work offline

### For Future Maintainers
- **Documented architecture**: Clear diagrams showing integration layers and data flow
- **Reusable patterns**: Well-documented scripts for GitHub-Claude conversions
- **Minimal dependencies**: Uses standard tools (gh CLI, jq, Bash) for broad compatibility

## Target Users

- **Primary**: Christopher, orchestrating multi-agent feature development
- **Secondary**: Future project contributors who need to understand and maintain the integration
- **Tertiary**: Claude agents (PM, Architect, Developer, etc.) coordinating via task primitives

## User Stories

### Core Integration Stories
1. As Christopher, I want to convert a GitHub Epic into a Claude task so that the PM agent can start orchestration work with full context.
2. As an Architect agent, I want my TDD creation task to reference the parent Epic so that all work traces back to the GitHub issue.
3. As a Developer agent, I want to mark a task complete and have it sync to GitHub so that the project board reflects progress.
4. As Christopher, I want tasks to persist across sessions so that multi-day agent workflows don't lose progress.

### Metadata Validation Stories
5. As any agent, I want task metadata validated on creation so that I catch schema errors early.
6. As Christopher, I want clear error messages when metadata is invalid so that I can fix issues quickly.
7. As an agent, I want to know which metadata fields are required for my task type so that I create tasks correctly.

### Documentation Stories
8. As Christopher, I want architecture diagrams showing integration layers so that I understand the system design.
9. As a future maintainer, I want usage examples for all scripts so that I can use them correctly.
10. As an agent, I want metadata schema documentation so that I know what metadata to include.

## Acceptance Criteria

### Phase 0: Discovery & Validation
- [ ] AC-1: Task created in one Claude session is visible in the next session
- [ ] AC-2: Task metadata schema validated against real GitHub issues (#7, #14)
- [ ] AC-3: Prototype issue-to-task conversion works for Epic and Task types
- [ ] AC-4: Task persistence mechanism documented in `temp/phase0-discovery-notes.md`
- [ ] AC-5: Go/No-Go decision made based on validation results

### Phase 1: Foundation (MVP Part 1)
- [ ] AC-6: `validate-metadata.sh` script rejects invalid metadata schemas
- [ ] AC-7: `validate-metadata.sh` accepts all valid metadata types (epic, task, tdd, pm-work, documentation)
- [ ] AC-8: `task-helpers.sh` provides utility functions for metadata extraction
- [ ] AC-9: Architecture diagram (D2 format) shows all 4 integration layers clearly
- [ ] AC-10: `docs/CLAUDE_TASK_INTEGRATION.md` explains metadata schema with 3+ examples
- [ ] AC-11: Task persistence configured and verified working

### Phase 2: Pull Integration (MVP Part 2)
- [ ] AC-12: `issue-to-task.sh` successfully converts Epic issue to TaskCreate call
- [ ] AC-13: `issue-to-task.sh` successfully converts Task issue to TaskCreate call
- [ ] AC-14: Script runs metadata validation and catches errors before output
- [ ] AC-15: Script output can be copy-pasted directly to create Claude task
- [ ] AC-16: `.claude/scripts/README.md` documents script usage with examples
- [ ] AC-17: `docs/PROJECT_BOARD_GUIDE.md` updated with "Claude Task Integration" section

## Scope

### In Scope (Phases 0-2 - MVP)
- Task persistence mechanism discovery and configuration
- Metadata schema definition with validation rules
- Metadata validation script (`validate-metadata.sh`)
- Utility helper functions (`task-helpers.sh`)
- Architecture documentation with D2 diagrams
- Manual GitHub issue → Claude task conversion script (`issue-to-task.sh`)
- Integration guide documentation
- Testing against real GitHub issues (Epic #7, Task #14)

### Out of Scope (Explicitly Deferred to Post-MVP)

**Phase 3: Push Integration (Opt-in Sync)**
- `task-to-status.sh` script for Claude task → GitHub status updates
- Opt-in auto-sync mechanism with `sync_on_complete` metadata flag
- Wrapper functions for automatic sync on task completion

**Phase 4: Epic Workflow Orchestration**
- `epic-workflow.sh` for automated Epic → TDD → Task setup
- `update-epic-tasks.sh` for batch task updates
- Epic workflow error handling and validation

**Phase 5: Refinement & Polish**
- `task-cleanup.sh` for removing old completed tasks
- Comprehensive error handling across all scripts
- Enhanced workflow diagrams
- FAQ section with edge case documentation
- Real-world usage examples (5+ scenarios)

**Not Planned**
- Cloud sync of Claude tasks (requires backend infrastructure)
- Automatic GitHub issue creation from Claude tasks (GitHub remains source of truth)
- Real-time bidirectional sync (opt-in manual/auto sync only)
- Web UI for task management (CLI-based only)

### Future Considerations
- Automatic task cleanup after configurable retention period (Phase 5)
- Enhanced Epic → TDD → Task orchestration (Phase 4)
- Integration with GitHub Project boards (Phase 4+)
- Task dependency visualization (post-v1.0)
- Multi-repository support (post-v1.0)

## Content Requirements

**No Japanese content required for this feature.**

This is a pure infrastructure/tooling enhancement for agent orchestration. All documentation will be in English.

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **MVP Success** (Phases 0-2) | | |
| Task persistence works | 100% sessions | Manual testing across sessions |
| Metadata validation accuracy | 100% schema catches | Test valid/invalid metadata |
| Issue conversion success rate | 100% for Epic/Task | Test against GitHub issues |
| Documentation completeness | All AC-6 to AC-17 pass | Manual review |
| **Post-MVP Success** (If Phases 3-5 implemented) | | |
| Auto-sync accuracy | 100% when enabled | Test completion → GitHub |
| Epic workflow error handling | 0 crashes on invalid input | Error testing |
| Script reliability | 0 data loss incidents | Production usage |

## Dependencies

### External Tools (Required)
- **gh CLI**: GitHub command-line interface for issue operations
  - Validation: `gh --version` (must be authenticated)
  - Installation: https://cli.github.com/
- **jq**: JSON parsing and manipulation
  - Validation: `jq --version`
  - Installation: `brew install jq` (macOS) or OS-equivalent

### Claude Code Features (Required)
- **Task Primitives**: TaskCreate, TaskUpdate, TaskList, TaskGet
  - Availability: Built into Claude Code
- **Task Persistence**: `~/.claude/tasks/` storage mechanism
  - Validation: Test in Phase 0

### Optional Dependencies
- **D2**: Diagram rendering (for architecture diagrams)
  - Not required for script functionality, only documentation

## Technical Considerations

### Technology Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| GitHub operations | `gh` CLI | Native GitHub integration, widely adopted |
| JSON parsing | `jq` | Industry standard, powerful, cross-platform |
| Scripting language | Bash | Minimal dependencies, cross-platform |
| Task storage | `~/.claude/tasks/` | Claude Code built-in persistence |
| Metadata validation | JSON Schema + jq | Industry standard validation approach |

### Layered Architecture

```
┌─────────────────────────────────────────────────────┐
│ Layer 4: Workflow Orchestration (Phase 4)          │
│ (.claude/scripts/workflows/)                        │
│ - epic-workflow.sh, update-epic-tasks.sh            │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│ Layer 3: GitHub Sync Scripts (Phases 2-3)          │
│ (.claude/scripts/github-sync/)                      │
│ - issue-to-task.sh, task-to-status.sh               │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│ Layer 2: Metadata Validation (Phase 1)             │
│ (.claude/scripts/core/)                             │
│ - validate-metadata.sh, task-helpers.sh             │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│ Layer 1: Core Primitives (Built-in)                │
│ (Claude Code)                                       │
│ - TaskCreate, TaskUpdate, TaskList, TaskGet         │
└─────────────────────────────────────────────────────┘
```

**MVP delivers Layers 1-3 (Layer 3 partial: pull only, not push)**

### Metadata Schema (Reference)

All metadata must pass validation via `validate-metadata.sh`.

**Epic Task Metadata:**
```javascript
{
  github_issue: 7,                // Required for Epic
  type: "epic",                   // Required
  epic_id: "PRD-001",            // Required for Epic
  prd: "docs/specs/PRD-001.md",  // Required for Epic
  tdd: "docs/tdd/TDD-001.md",    // Added after TDD creation
  phase: 1,                       // Optional
  tasks: [13, 14, 15],           // Optional: child GitHub issues
  sync_on_complete: false         // Optional (Phase 3)
}
```

**Implementation Task Metadata:**
```javascript
{
  github_issue: 14,              // Optional but recommended
  type: "task",                  // Required
  task_id: "T1.2",               // Optional but recommended
  epic: 7,                       // Optional: parent Epic issue
  tdd_section: "§3",             // Optional: TDD section
  effort: "M",                   // Optional: S/M/L/XL
  wave: 1,                       // Optional: implementation wave
  persona: "dev",                // Optional: responsible agent
  sync_on_complete: true         // Optional (Phase 3)
}
```

**Validation Rules:**
- `type` (required): One of `"epic"`, `"task"`, `"tdd"`, `"pm-work"`, `"documentation"`
- `github_issue` (optional): Number, must be > 0 if present
- `sync_on_complete` (optional): Boolean, defaults to `false`
- Type-specific fields validated based on `type` value

### Directory Structure

```
.claude/
├── scripts/
│   ├── core/                    # Phase 1 - MVP
│   │   ├── validate-metadata.sh
│   │   └── task-helpers.sh
│   ├── github-sync/             # Phase 2-3
│   │   ├── issue-to-task.sh    # Phase 2 - MVP
│   │   └── task-to-status.sh   # Phase 3 - Post-MVP
│   └── workflows/               # Phase 4-5 - Post-MVP
│       ├── epic-workflow.sh
│       ├── update-epic-tasks.sh
│       └── task-cleanup.sh
└── scripts/README.md            # Phase 2 - MVP
```

## Open Questions

### For Phase 0 Discovery
1. Does `~/.claude/tasks/` persist across sessions automatically, or does it require environment variable configuration?
2. What is the file format in `~/.claude/tasks/` (JSON, custom format)?
3. Does `CLAUDE_CODE_TASK_LIST_ID` need to be set, or is persistence automatic?
4. How do Claude task primitives handle metadata storage (preserved exactly, or transformed)?

### For MVP Decision
5. After completing Phases 0-2, is the manual workflow sufficient, or do we need auto-sync (Phase 3)?
6. How frequently will Epic → TDD → Task orchestration be used (determines Phase 4 priority)?
7. What is the expected volume of Claude tasks (determines Phase 5 cleanup priority)?

### For Future Phases (Post-MVP)
8. Should `sync_on_complete` be opt-in (false default) or opt-out (true default)?
9. What retention period for completed tasks? (30 days? 90 days? Configurable?)
10. Should Epic workflow script create GitHub issues for sub-tasks, or only Claude tasks?

---

## MVP Checkpoint Evaluation Criteria

After completing Phases 0-2, evaluate before proceeding to Phases 3-5:

### Proceed with Phase 3-5 if:
- Manual workflow is too tedious for frequent use
- Multiple agents need automatic sync coordination
- High volume of task completions justify automation
- Christopher wants full Epic orchestration automation

### Stop at MVP if:
- Manual workflow suffices for current project scale
- Small number of tasks makes automation overhead unnecessary
- Sync complexity outweighs benefit
- Focus should shift to other features

---

## Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2026-01-25 | PM (Claude) | Initial draft for MVP (Phases 0-2) |
