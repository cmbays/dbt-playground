"""LESSONS.md Analyzer - main analyzer class.

Orchestrates pattern extraction from debug sessions.
"""

from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Optional

import duckdb

from scripts.lib.lessons_analyzer.clustering import cluster_root_causes
from scripts.lib.lessons_analyzer.exceptions import (
    DatabaseNotFoundError,
    InsufficientDataError,
    NoSessionsFoundError,
    PatternNotFoundError,
)
from scripts.lib.lessons_analyzer.generator import generate_lessons_entry
from scripts.lib.lessons_analyzer.models import DebugSessionData, Pattern


def get_db_path() -> Path:
    """Get debug sessions database path."""
    for parent in [Path.cwd(), *Path.cwd().parents]:
        if (parent / 'CLAUDE.md').exists():
            return parent / 'database' / 'debug_sessions' / 'debug_sessions.duckdb'

    # Fallback
    return Path('database') / 'debug_sessions' / 'debug_sessions.duckdb'


class LessonsAnalyzer:
    """Main analyzer class for pattern extraction."""

    def __init__(self, conn: Optional[duckdb.DuckDBPyConnection] = None):
        """Initialize analyzer with optional connection.

        Args:
            conn: DuckDB connection (connects to debug_sessions if not provided)
        """
        self._conn = conn
        self._owns_connection = conn is None

    @property
    def conn(self) -> duckdb.DuckDBPyConnection:
        """Get or create database connection."""
        if self._conn is None:
            db_path = get_db_path()
            if not db_path.exists():
                raise DatabaseNotFoundError(
                    f"Debug session database not found at {db_path}. "
                    f"Run 'debug-tracker.py start' to create your first session."
                )
            self._conn = duckdb.connect(str(db_path), read_only=True)
        return self._conn

    def close(self) -> None:
        """Close connection if we own it."""
        if self._owns_connection and self._conn is not None:
            self._conn.close()
            self._conn = None

    def load_sessions(
        self,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        category: Optional[str] = None,
    ) -> list[DebugSessionData]:
        """Load debug sessions from database.

        Args:
            since: Start date for analysis
            until: End date for analysis
            category: Optional pattern category filter

        Returns:
            List of debug sessions
        """
        query = """
        SELECT
            session_id,
            bug_description,
            root_cause,
            tags,
            start_time,
            end_time,
            duration_minutes,
            outcome,
            step_count
        FROM debug_sessions
        WHERE outcome = 'resolved'
          AND root_cause IS NOT NULL
        """
        params = []

        if since:
            query += ' AND start_time >= ?'
            params.append(since)

        if until:
            query += ' AND start_time <= ?'
            params.append(until)

        if category:
            query += ' AND root_cause ILIKE ?'
            params.append(f'%{category}%')

        query += ' ORDER BY start_time DESC'

        results = self.conn.execute(query, params).fetchall()

        def ensure_utc(dt):
            if dt is None:
                return None
            if dt.tzinfo is None:
                return dt.replace(tzinfo=UTC)
            return dt

        return [
            DebugSessionData(
                session_id=row[0],
                bug_description=row[1],
                root_cause=row[2],
                tags=row[3] or [],
                start_time=ensure_utc(row[4]),
                end_time=ensure_utc(row[5]),
                duration_minutes=row[6] or 0,
                outcome=row[7],
                step_count=row[8] or 0,
            )
            for row in results
        ]

    def extract(
        self,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        min_frequency: int = 2,
        min_score: float = 0.5,
        category: Optional[str] = None,
        limit: int = 10,
    ) -> list[Pattern]:
        """Extract patterns from debug sessions.

        Args:
            since: Start date (default: 30 days ago)
            until: End date (default: today)
            min_frequency: Minimum occurrence count
            min_score: Minimum confidence score
            category: Optional pattern category filter
            limit: Maximum patterns to return

        Returns:
            List of extracted patterns

        Raises:
            NoSessionsFoundError: If no sessions match criteria
        """
        # Default date range
        if since is None:
            since = datetime.now(UTC) - timedelta(days=30)
        if until is None:
            until = datetime.now(UTC)

        sessions = self.load_sessions(since=since, until=until, category=category)

        if not sessions:
            raise NoSessionsFoundError(
                f'No resolved sessions found between {since.date()} and {until.date()}'
            )

        if len(sessions) < 2:
            raise InsufficientDataError(
                f'Only {len(sessions)} session(s) found. Need at least 2 for pattern detection.'
            )

        # Cluster sessions into patterns
        patterns = cluster_root_causes(sessions, min_cluster_size=min_frequency)

        # Filter by score
        patterns = [p for p in patterns if p.confidence_score >= min_score]

        # Sort by score and limit
        patterns.sort(key=lambda p: p.confidence_score, reverse=True)
        return patterns[:limit]

    def review(self, pattern_name: str) -> Pattern:
        """Get detailed review of a specific pattern.

        Args:
            pattern_name: Name of pattern to review

        Returns:
            Pattern with full details

        Raises:
            PatternNotFoundError: If pattern not found
        """
        # Extract all patterns
        patterns = self.extract(min_frequency=1, min_score=0.0, limit=100)

        # Find matching pattern (case-insensitive partial match)
        pattern_lower = pattern_name.lower()
        for p in patterns:
            if pattern_lower in p.pattern_name.lower():
                return p

        raise PatternNotFoundError(pattern_name)

    def find_similar_patterns(self, pattern_name: str, limit: int = 5) -> list[str]:
        """Find patterns similar to the given name.

        Args:
            pattern_name: Pattern name to search for
            limit: Maximum suggestions

        Returns:
            List of similar pattern names
        """
        try:
            patterns = self.extract(min_frequency=1, min_score=0.0, limit=50)
        except (NoSessionsFoundError, InsufficientDataError):
            return []

        pattern_lower = pattern_name.lower()
        similar = []

        for p in patterns:
            name_lower = p.pattern_name.lower()
            # Check for any word overlap
            words1 = set(pattern_lower.split())
            words2 = set(name_lower.split())
            if words1 & words2:
                similar.append(p.pattern_name)

        return similar[:limit]

    def generate_entry(self, pattern: Pattern, include_sessions: int = 3) -> str:
        """Generate LESSONS.md entry for a pattern.

        Args:
            pattern: Pattern to generate entry for
            include_sessions: Number of example sessions

        Returns:
            Formatted markdown entry
        """
        return generate_lessons_entry(pattern, include_sessions)

    def get_stats(self, since: Optional[datetime] = None) -> dict:
        """Get aggregate statistics.

        Args:
            since: Start date for analysis

        Returns:
            Dictionary with statistics
        """
        if since is None:
            since = datetime.now(UTC) - timedelta(days=30)

        # Get all sessions
        all_sessions_query = """
        SELECT
            outcome,
            duration_minutes,
            tags
        FROM debug_sessions
        WHERE start_time >= ?
        """
        results = self.conn.execute(all_sessions_query, [since]).fetchall()

        if not results:
            return {
                'total_sessions': 0,
                'by_outcome': {},
                'by_category': {},
                'top_tags': [],
                'patterns_detected': 0,
            }

        # Aggregate stats
        total = len(results)
        by_outcome: dict[str, int] = {}
        total_duration = 0
        duration_count = 0
        all_tags: list[str] = []

        for outcome, duration, tags in results:
            by_outcome[outcome] = by_outcome.get(outcome, 0) + 1
            if duration:
                total_duration += duration
                duration_count += 1
            if tags:
                all_tags.extend(tags)

        # Category breakdown via v_session_summary view
        try:
            category_results = self.conn.execute("""
            SELECT
                pattern_category,
                COUNT(*) as count,
                AVG(duration_minutes) as avg_duration
            FROM v_session_summary
            WHERE session_date >= ?
            GROUP BY pattern_category
            ORDER BY count DESC
            """, [since.date()]).fetchall()

            by_category = {
                row[0]: {'count': row[1], 'avg_duration': int(row[2] or 0)}
                for row in category_results
            }
        except Exception:
            by_category = {}

        # Top tags
        from collections import Counter
        tag_counts = Counter(all_tags)
        top_tags = [{'tag': t, 'count': c} for t, c in tag_counts.most_common(10)]

        # Pattern count
        try:
            patterns = self.extract(since=since, min_frequency=2, min_score=0.5, limit=100)
            pattern_count = len(patterns)
            promoted = sum(1 for p in patterns if p.status == 'PROMOTE')
            candidates = sum(1 for p in patterns if p.status == 'CANDIDATE')
        except (NoSessionsFoundError, InsufficientDataError):
            pattern_count = 0
            promoted = 0
            candidates = 0

        return {
            'total_sessions': total,
            'by_outcome': by_outcome,
            'by_category': by_category,
            'top_tags': top_tags,
            'avg_duration_minutes': int(total_duration / duration_count) if duration_count > 0 else 0,
            'patterns_detected': pattern_count,
            'patterns_promoted': promoted,
            'patterns_candidates': candidates,
            'analysis_period': {
                'start': since.strftime('%Y-%m-%d'),
                'end': datetime.now(UTC).strftime('%Y-%m-%d'),
            },
        }
