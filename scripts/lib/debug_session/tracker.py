"""Debug Session Tracker - main tracker class.

Orchestrates session lifecycle: start, log, end, query, status.
"""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Optional

import duckdb

from scripts.lib.debug_session import database as db
from scripts.lib.debug_session.exceptions import (
    NoActiveSessionError,
    SessionAlreadyActiveError,
)
from scripts.lib.debug_session.models import (
    DebugSession,
    DebugStep,
    PROTOCOL_PHASES,
    SessionState,
    VALID_OUTCOMES,
)
from scripts.lib.debug_session.utils import (
    clear_state,
    load_state,
    parse_duration,
    save_state,
)


class DebugSessionTracker:
    """Main tracker class for debug sessions."""

    def __init__(self, conn: Optional[duckdb.DuckDBPyConnection] = None):
        """Initialize tracker with optional connection.

        Args:
            conn: DuckDB connection (creates one if not provided)
        """
        self._conn = conn
        self._owns_connection = conn is None

    @property
    def conn(self) -> duckdb.DuckDBPyConnection:
        """Get or create database connection."""
        if self._conn is None:
            self._conn = db.connect()
        return self._conn

    def close(self) -> None:
        """Close connection if we own it."""
        if self._owns_connection and self._conn is not None:
            self._conn.close()
            self._conn = None

    def start_session(
        self,
        bug_description: str,
        tags: Optional[list[str]] = None,
        severity: str = 'medium',
        context: Optional[str] = None,
        bug_id: Optional[str] = None,
        force: bool = False,
    ) -> str:
        """Start a new debug session.

        Args:
            bug_description: Description of the bug
            tags: Optional categorization tags
            severity: Bug severity (high, medium, low)
            context: Initial file:line context
            bug_id: Optional link to external tracker
            force: Force start even if session active

        Returns:
            The new session ID

        Raises:
            SessionAlreadyActiveError: If session active and not forcing
        """
        # Check for existing active session
        active = db.get_active_session(self.conn)
        if active and not force:
            raise SessionAlreadyActiveError(active.session_id)

        # End existing session if forcing
        if active and force:
            self._force_end_session(active)

        # Create new session
        session_id = db.generate_session_id(self.conn)
        session = DebugSession(
            session_id=session_id,
            bug_description=bug_description,
            start_time=datetime.now(UTC),
            severity=severity,
            tags=tags or [],
            context=context,
            bug_id=bug_id,
            outcome='in_progress',
        )

        db.insert_session(self.conn, session)

        # Save state for quick CLI access
        state = SessionState(
            session_id=session_id,
            start_time=session.start_time,
            step_count=0,
        )
        save_state(state)

        return session_id

    def log_step(
        self,
        phase: str,
        findings: str,
        evidence: Optional[str] = None,
        step_number: Optional[int] = None,
    ) -> int:
        """Log a debug step to the current session.

        Args:
            phase: Protocol phase (1-reproduce, 2-blast_radius, etc)
            findings: What was discovered
            evidence: Optional path to supporting files
            step_number: Optional specific step number

        Returns:
            The step number assigned

        Raises:
            NoActiveSessionError: If no session is active
            ValidationError: If phase is invalid
        """
        state = load_state()
        if state is None:
            active = db.get_active_session(self.conn)
            if active is None:
                raise NoActiveSessionError(
                    'No active session. Use "start" to begin a debug session.'
                )
            state = SessionState(
                session_id=active.session_id,
                start_time=active.start_time,
                step_count=active.step_count,
            )

        # Determine step number
        if step_number is None:
            step_number = db.get_next_step_number(self.conn, state.session_id)

        step = DebugStep(
            session_id=state.session_id,
            step_number=step_number,
            timestamp=datetime.now(UTC),
            protocol_phase=phase,
            findings=findings,
            evidence=evidence,
        )

        db.insert_step(self.conn, step)

        # Update session step count
        self.conn.execute(
            'UPDATE debug_sessions SET step_count = step_count + 1 WHERE session_id = ?',
            [state.session_id],
        )

        # Update state
        state.step_count = step_number
        state.last_phase = phase
        save_state(state)

        return step_number

    def end_session(
        self,
        root_cause: str,
        fix_time: str,
        resolution: Optional[str] = None,
        outcome: str = 'resolved',
    ) -> DebugSession:
        """End the current debug session.

        Args:
            root_cause: The identified root cause
            fix_time: Time spent debugging (e.g., "45m", "1h 30m")
            resolution: How it was fixed
            outcome: Session outcome (resolved, escalated, inconclusive)

        Returns:
            The completed session

        Raises:
            NoActiveSessionError: If no session is active
            ValidationError: If outcome is invalid
        """
        state = load_state()
        if state is None:
            active = db.get_active_session(self.conn)
            if active is None:
                raise NoActiveSessionError(
                    'No active session. Use "start" to begin a debug session.'
                )
            state = SessionState(
                session_id=active.session_id,
                start_time=active.start_time,
                step_count=active.step_count,
            )

        if outcome not in VALID_OUTCOMES or outcome == 'in_progress':
            valid = [o for o in VALID_OUTCOMES if o != 'in_progress']
            raise ValueError(f"Invalid outcome '{outcome}'. Valid: {valid}")

        duration_minutes = parse_duration(fix_time)

        # Get the full session
        session = db.get_session(self.conn, state.session_id)
        if session is None:
            raise NoActiveSessionError(f"Session {state.session_id} not found in database")

        # Update session
        session.end_time = datetime.now(UTC)
        session.duration_minutes = duration_minutes
        session.root_cause = root_cause
        session.resolution = resolution
        session.outcome = outcome

        db.update_session(self.conn, session)

        # Clear state
        clear_state()

        # Emit event for FS1/FS5
        self._emit_event(session)

        return session

    def get_status(self) -> dict:
        """Get current session status.

        Returns:
            Dict with session info or recent sessions if none active
        """
        state = load_state()

        if state:
            session = db.get_session(self.conn, state.session_id)
            if session and session.outcome == 'in_progress':
                steps = db.get_steps(self.conn, session.session_id)
                elapsed = (datetime.now(UTC) - session.start_time).total_seconds()

                return {
                    'active': True,
                    'session': session,
                    'steps': steps,
                    'elapsed_seconds': elapsed,
                    'last_phase': state.last_phase,
                }

        # No active session
        recent = db.get_recent_sessions(self.conn, limit=5)
        return {
            'active': False,
            'recent_sessions': recent,
        }

    def query_sessions(
        self,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        pattern: Optional[str] = None,
        tags: Optional[list[str]] = None,
        outcome: Optional[str] = None,
        limit: int = 20,
    ) -> list[DebugSession]:
        """Query sessions with filters."""
        return db.query_sessions(
            self.conn,
            since=since,
            until=until,
            pattern=pattern,
            tags=tags,
            outcome=outcome,
            limit=limit,
        )

    def get_session_details(self, session_id: str) -> Optional[dict]:
        """Get detailed information about a session.

        Returns:
            Dict with session and steps, or None if not found
        """
        session = db.get_session(self.conn, session_id)
        if session is None:
            return None

        steps = db.get_steps(self.conn, session_id)

        return {
            'session': session,
            'steps': steps,
        }

    def _force_end_session(self, session: DebugSession) -> None:
        """Force end a session (used when starting new session with --force)."""
        session.end_time = datetime.now(UTC)
        session.outcome = 'inconclusive'
        session.root_cause = 'Session forcibly ended by starting new session'

        # Calculate duration
        elapsed = session.end_time - session.start_time
        session.duration_minutes = int(elapsed.total_seconds() / 60)

        db.update_session(self.conn, session)
        clear_state()

    def _emit_event(self, session: DebugSession) -> None:
        """Emit event to events.jsonl for FS5 consumption."""
        # Find memory directory
        memory_dir = None
        for parent in [Path.cwd(), *Path.cwd().parents]:
            if (parent / 'CLAUDE.md').exists():
                memory_dir = parent / 'memory'
                memory_dir.mkdir(exist_ok=True)
                break

        if memory_dir is None:
            return  # Silently skip if not in project

        events_file = memory_dir / 'events.jsonl'

        # Determine pattern category
        pattern_category = 'other'
        if session.root_cause:
            cause_lower = session.root_cause.lower()
            if 'race' in cause_lower or 'concurrent' in cause_lower:
                pattern_category = 'race_condition'
            elif 'null' in cause_lower or 'none' in cause_lower:
                pattern_category = 'null_handling'
            elif 'timeout' in cause_lower:
                pattern_category = 'timeout'
            elif 'state' in cause_lower or 'corrupt' in cause_lower:
                pattern_category = 'state_management'

        event = {
            'timestamp': datetime.now(UTC).isoformat(),
            'event': 'debug_session_completed',
            'version': '1.0',
            'data': {
                'session_id': session.session_id,
                'duration_minutes': session.duration_minutes,
                'step_count': session.step_count,
                'outcome': session.outcome,
                'root_cause_category': pattern_category,
                'tags': session.tags,
            },
        }

        with open(events_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event) + '\n')
