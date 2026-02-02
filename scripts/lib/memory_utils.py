"""Memory directory utilities for FS1 Agent Memory System.

This module provides shared functionality for memory directory operations
used by both log-session.py and consolidate-memory.py.
"""

from pathlib import Path


def get_memory_dir() -> Path:
    """Get memory directory path, creating if needed.

    Searches current directory and parents for CLAUDE.md (project root marker),
    then returns/creates the memory/ subdirectory.

    Returns:
        Path to memory directory

    Raises:
        FileNotFoundError: If project root (CLAUDE.md) not found
    """
    for parent in [Path.cwd()] + list(Path.cwd().parents):
        if (parent / 'CLAUDE.md').exists():
            memory_dir = parent / 'memory'
            memory_dir.mkdir(exist_ok=True)
            return memory_dir
    raise FileNotFoundError(
        f'Could not find project root (CLAUDE.md). Current directory: {Path.cwd()}'
    )
