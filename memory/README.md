# Agent Memory System

This directory contains daily session logs for compound learning.
See `docs/specs/PRD-024-AGENT-MEMORY.md` for details.

## Files in this directory

| File | Purpose |
|------|---------|
| `YYYY-MM-DD.md` | Daily append-only session logs |
| `MEMORY_INDEX.md` | Weekly consolidation summary |
| `events.jsonl` | Machine-readable events for FS5 metrics |
| `.gitkeep` | Ensures directory is tracked by git |

## Quick Start

```bash
# Log a session
uv run scripts/log-session.py -t "What you worked on"

# Run weekly consolidation
uv run scripts/consolidate-memory.py
```

See `docs/for_chris/FS1_AGENT_MEMORY_GUIDE.md` for complete documentation.
