# Interactive Learning Playground - Product Requirements

## Overview

Standalone product transforming markdown documentation into interactive slide-based presentations.

## Content Sources

| Source | Description |
|--------|-------------|
| FOR_CHRIS | Educational documents for user learning |
| Claude Memory | Learnings captured in `memory/` directory |

## Key Features (Prioritized)

| Priority | Feature | Description |
|----------|---------|-------------|
| **P0** | Library navigation | Browse decks - chronological or topic-based |
| **P0** | Content source toggle | Switch between FOR_CHRIS and Claude Memory |
| **P0** | Slide deck navigation | Markdown → navigable slides |
| **P0** | Visual beautification | Polished, delightful styling |
| P1 | Interactive diagrams | Tooltips, expandable, clickable |
| P1 | Embedded mock UIs | Show features inline |
| P2 | Live playgrounds | Hands-on sandboxes |
| P2 | Ask Claude integration | Query about current slide |
| P3 | Quizzes/knowledge checks | Validate understanding |

## Success Criteria

1. User prefers interactive version over raw markdown
2. Transform existing doc → presentation in <5 minutes
3. Complex concepts become clearer through interaction
4. Extensible architecture for new widget types

## Phases

| Phase | Focus | Deliverables |
|-------|-------|--------------|
| **0** | Learning Research | `LEARNING_RESEARCH.md` |
| **1 (MVP)** | Core Experience | Library, toggle, slides, styling |
| **2** | Interactivity | Diagrams, mock UIs |
| **3** | Advanced | Playgrounds, Claude, quizzes |

## Design Priorities

1. **Extensibility** - Easy to add new widget types
2. **Interactivity** - Rich interactions, not static
3. **Beautiful** - Delightful visual design
4. **Testability** - Testing framework included
