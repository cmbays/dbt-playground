# Supervisor Command

Wake up the Supervisor agent for workflow orchestration and session management.

## Usage

```
/supervisor [action]
```

## Actions

| Action | Description |
|--------|-------------|
| (none) | Start new session, ask what we're working on |
| `resume` | Resume from WORKFLOW_STATE.md |
| `status` | Show all track status |
| `queue [feature]` | Add urgent work to queue |

## Examples

### Start New Session

```
/supervisor
```

Supervisor will ask clarifying questions and help you start a new work track.

### Resume Previous Work

```
/supervisor resume
```

Supervisor reads `temp/WORKFLOW_STATE.md` and reports:

- Active track and current phase
- Artifacts completed
- Any blockers
- Recommended next action

### Check Status

```
/supervisor status
```

Shows all active, queued, and recent completed tracks.

### Queue Urgent Work

```
/supervisor queue fix/null-handling
```

Adds work to queue without interrupting current phase.

## What Supervisor Does

The Supervisor is the **meta-orchestrator** for the agent system:

1. **Interface Layer** - Asks clarifying questions before delegating
2. **Orchestrator** - Calls `/orchestrate` with appropriate flags
3. **Quality Gate** - Verifies artifacts before phase transitions
4. **State Manager** - Maintains `temp/WORKFLOW_STATE.md`
5. **Sage Coordinator** - Triggers learning extraction on failures/deployments
6. **Multi-Track Manager** - Handles parallel work and queue

## Relationship to /orchestrate

- `/orchestrate` runs a single feature through the assembly line
- `/supervisor` wraps `/orchestrate` with state management and verification
- Supervisor determines which flags to pass to `/orchestrate`

## State File

Supervisor maintains `temp/WORKFLOW_STATE.md` with:

- Active and queued tracks
- Phase status and artifacts
- Session metrics
- Last session summary

## When to Use

| Scenario | Command |
|----------|---------|
| Starting your day | `/supervisor` |
| Continuing work | `/supervisor resume` |
| Quick status check | `/supervisor status` |
| Urgent bug came in | `/supervisor queue [description]` |
| Mid-work interruption | Supervisor will queue, not switch |

## Alternative Invocation

You can also use the prefix:

```
super: I'm starting a new session
super: Resume where we left off
super: What's the current state of all active work?
super: Queue an urgent fix: [description]
```

## Related

- [[../agents/supervisor.md]] - Full persona definition
- [[orchestrate.md]] - Assembly line workflow command
- [[../agents/sage.md]] - Learning extraction (invoked by Supervisor)
