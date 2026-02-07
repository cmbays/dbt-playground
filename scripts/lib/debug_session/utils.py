"""Utility functions for Debug Session Tracker.

Includes time parsing, formatting, and state management.
"""

import json
import re
from datetime import timedelta
from pathlib import Path
from typing import Optional

from scripts.lib.debug_session.exceptions import ValidationError
from scripts.lib.debug_session.models import SessionState


def parse_duration(duration_str: str) -> int:
    """Parse duration string to minutes.

    Args:
        duration_str: Duration string like "45m", "1h", "1h 30m", "2h 15m"

    Returns:
        Duration in minutes

    Raises:
        ValidationError: If format is invalid
    """
    if not duration_str:
        raise ValidationError('Duration cannot be empty')

    # Normalize: lowercase and remove extra spaces
    duration_str = duration_str.lower().strip()

    total_minutes = 0
    found_match = False

    # Match hours
    hours_match = re.search(r'(\d+)\s*h', duration_str)
    if hours_match:
        total_minutes += int(hours_match.group(1)) * 60
        found_match = True

    # Match minutes
    minutes_match = re.search(r'(\d+)\s*m', duration_str)
    if minutes_match:
        total_minutes += int(minutes_match.group(1))
        found_match = True

    # Also support just a number (assume minutes)
    if not found_match:
        if duration_str.isdigit():
            return int(duration_str)
        raise ValidationError(
            f"Invalid duration format: '{duration_str}'. "
            f"Use formats like '45m', '1h', '1h 30m', or just minutes as a number."
        )

    return total_minutes


def format_duration(minutes: int) -> str:
    """Format minutes as human-readable duration.

    Args:
        minutes: Duration in minutes

    Returns:
        Human-readable string like "45m" or "1h 30m"
    """
    if minutes < 60:
        return f'{minutes}m'

    hours = minutes // 60
    remaining_mins = minutes % 60

    if remaining_mins == 0:
        return f'{hours}h'

    return f'{hours}h {remaining_mins}m'


def get_state_file_path() -> Path:
    """Get the path to the state file."""
    # Find project root via CLAUDE.md
    for parent in [Path.cwd(), *Path.cwd().parents]:
        if (parent / 'CLAUDE.md').exists():
            state_dir = parent / 'temp'
            state_dir.mkdir(parents=True, exist_ok=True)
            return state_dir / '.debug_session_state.json'

    # Fallback
    return Path('temp') / '.debug_session_state.json'


def save_state(state: SessionState) -> None:
    """Save session state to file."""
    state_file = get_state_file_path()
    state_file.parent.mkdir(parents=True, exist_ok=True)

    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(state.to_dict(), f, indent=2)


def load_state() -> Optional[SessionState]:
    """Load session state from file."""
    state_file = get_state_file_path()

    if not state_file.exists():
        return None

    try:
        with open(state_file, encoding='utf-8') as f:
            data = json.load(f)
            return SessionState.from_dict(data)
    except (json.JSONDecodeError, KeyError, ValueError):
        return None


def clear_state() -> None:
    """Clear the state file."""
    state_file = get_state_file_path()
    if state_file.exists():
        state_file.unlink()


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text for display purposes."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + '...'


def format_time_ago(seconds: float) -> str:
    """Format a time difference as human-readable string."""
    if seconds < 60:
        return 'just now'

    minutes = int(seconds / 60)
    if minutes < 60:
        return f'{minutes} minute{"s" if minutes != 1 else ""} ago'

    hours = int(minutes / 60)
    if hours < 24:
        return f'{hours} hour{"s" if hours != 1 else ""} ago'

    days = int(hours / 24)
    return f'{days} day{"s" if days != 1 else ""} ago'
