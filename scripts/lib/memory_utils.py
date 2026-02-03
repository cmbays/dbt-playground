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
        PermissionError: If unable to create memory directory
    """
    for parent in [Path.cwd(), *Path.cwd().parents]:
        if (parent / 'CLAUDE.md').exists():
            memory_dir = parent / 'memory'
            try:
                memory_dir.mkdir(exist_ok=True)
            except PermissionError as e:
                raise PermissionError(
                    f'Cannot create memory directory at {memory_dir}: {e}. '
                    f'Check write permissions for {parent}'
                ) from e
            except OSError as e:
                raise OSError(f'Cannot create memory directory at {memory_dir}: {e}') from e
            return memory_dir
    raise FileNotFoundError(
        f'Could not find project root (CLAUDE.md). Current directory: {Path.cwd()}'
    )
