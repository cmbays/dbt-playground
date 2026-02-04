"""
FS5 Anomaly Detection Service.

Implements 8 anomaly detection rules from PRD-027:
1. stuck_session - No events for >30min in BUILD/VERIFY
2. qa_skipping - DEPLOY without VERIFY (CRITICAL)
3. phase_timeout - Duration >2x baseline
4. review_avoidance - PR merged without approvals (CRITICAL)
5. test_regression - Previously passing test now fails
6. artifact_missing - Phase complete without expected artifact
7. agent_loop - Same agent >5x without progress
8. orphan_branch - No commits for >3 days

Version: v0.10.0
Created: 2026-02-03
"""

from dataclasses import dataclass
from datetime import datetime, UTC, timedelta
from enum import Enum
from pathlib import Path
from uuid import uuid4
import fnmatch
import json
import yaml


class Severity(Enum):
    """Anomaly severity levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class Anomaly:
    """A detected anomaly."""

    anomaly_id: str
    rule_id: str
    severity: Severity
    correlation_id: str
    detected_at: datetime
    description: str
    details: dict
    resolved_at: datetime | None = None
    resolution: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "anomaly_id": self.anomaly_id,
            "rule_id": self.rule_id,
            "severity": self.severity.value,
            "correlation_id": self.correlation_id,
            "detected_at": self.detected_at.isoformat(),
            "description": self.description,
            "details": self.details,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolution": self.resolution,
        }


# Default rule configuration path
CONFIG_PATH = Path("config/anomaly-rules.yml")

# Cache for loaded config
_config_cache: dict | None = None


def load_rules_config(config_path: Path | None = None) -> dict:
    """Load anomaly rules configuration from YAML."""
    global _config_cache

    path = config_path or CONFIG_PATH

    if _config_cache is None and path.exists():
        with open(path, encoding="utf-8") as f:
            _config_cache = yaml.safe_load(f)

    return _config_cache or {"version": "1.0", "global": {"enabled": True}, "rules": {}}


def detect_anomalies(
    correlation_id: str | None = None,
    rules: list[str] | None = None,
    events: list[dict] | None = None
) -> list[Anomaly]:
    """
    Run anomaly detection rules.

    Args:
        correlation_id: Optional filter to specific feature
        rules: Optional list of rule IDs to run (runs all if None)
        events: Optional pre-fetched events

    Returns:
        List of detected anomalies (new only, not previously detected)
    """
    config = load_rules_config()

    if not config.get("global", {}).get("enabled", True):
        return []

    if events is None and correlation_id:
        events = _fetch_events(correlation_id)

    anomalies: list[Anomaly] = []
    rules_config = config.get("rules", {})
    rules_to_run = rules or list(rules_config.keys())

    for rule_id in rules_to_run:
        rule_config = rules_config.get(rule_id, {})
        if not rule_config.get("enabled", True):
            continue

        # Run the appropriate detector
        detector = _get_detector(rule_id)
        if detector and events:
            detected = detector(correlation_id or "", events, rule_config)
            anomalies.extend(detected)

    # Filter out already-detected anomalies
    return _filter_new_anomalies(anomalies, correlation_id)


def check_transition_anomalies(
    task_id: str,
    from_stage: str,
    to_stage: str
) -> list[Anomaly]:
    """
    Check for anomalies specific to a transition.

    Called immediately on transition by kanban handler.
    Checks: qa_skipping, out-of-order
    """
    anomalies = []
    config = load_rules_config()
    rules_config = config.get("rules", {})

    # Check QA skipping
    qa_config = rules_config.get("qa_skipping", {})
    if qa_config.get("enabled", True):
        if to_stage == "DEPLOY" and from_stage != "VERIFY":
            anomalies.append(Anomaly(
                anomaly_id=str(uuid4()),
                rule_id="qa_skipping",
                severity=Severity[qa_config.get("severity", "CRITICAL")],
                correlation_id=task_id,
                detected_at=datetime.now(UTC),
                description=qa_config.get("description", "DEPLOY without VERIFY"),
                details={
                    "from_stage": from_stage,
                    "to_stage": to_stage,
                    "expected_previous": "VERIFY",
                },
            ))

    return anomalies


def resolve_anomaly(anomaly_id: str, resolution: str) -> None:
    """Mark an anomaly as resolved."""
    from fs5.core.db import get_connection

    with get_connection() as conn:
        conn.execute("""
            UPDATE anomalies
            SET resolved_at = ?,
                resolution = ?
            WHERE anomaly_id = ?
        """, [datetime.now(UTC), resolution, anomaly_id])


def get_active_anomalies(
    correlation_id: str | None = None,
    severity: Severity | None = None
) -> list[Anomaly]:
    """Get currently unresolved anomalies."""
    from fs5.core.db import get_connection

    with get_connection() as conn:
        query = """
            SELECT
                anomaly_id, rule_id, severity, correlation_id,
                detected_at, description, details
            FROM anomalies
            WHERE resolved_at IS NULL
        """
        params = []

        if correlation_id:
            query += " AND correlation_id = ?"
            params.append(correlation_id)

        if severity:
            query += " AND severity = ?"
            params.append(severity.value)

        query += " ORDER BY detected_at DESC"

        results = conn.execute(query, params).fetchall()

        return [
            Anomaly(
                anomaly_id=str(r[0]),
                rule_id=r[1],
                severity=Severity(r[2]),
                correlation_id=r[3],
                detected_at=r[4],
                description=r[5],
                details=r[6] if isinstance(r[6], dict) else {},
            )
            for r in results
        ]


def persist_anomaly(anomaly: Anomaly) -> None:
    """Persist an anomaly to the database."""
    from fs5.core.db import get_connection

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO anomalies (
                anomaly_id, rule_id, severity, correlation_id,
                detected_at, description, details
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [
            anomaly.anomaly_id,
            anomaly.rule_id,
            anomaly.severity.value,
            anomaly.correlation_id,
            anomaly.detected_at,
            anomaly.description,
            json.dumps(anomaly.details),
        ])


# --- Rule Detectors ---

def _get_detector(rule_id: str):
    """Get the detector function for a rule."""
    detectors = {
        "stuck_session": _detect_stuck_session,
        "qa_skipping": _detect_qa_skipping,
        "phase_timeout": _detect_phase_timeout,
        "review_avoidance": _detect_review_avoidance,
        "test_regression": _detect_test_regression,
        "artifact_missing": _detect_artifact_missing,
        "agent_loop": _detect_agent_loop,
        "orphan_branch": _detect_orphan_branch,
    }
    return detectors.get(rule_id)


def _detect_stuck_session(
    correlation_id: str,
    events: list[dict],
    config: dict
) -> list[Anomaly]:
    """Rule 1: Detect stuck sessions (no events for threshold in active phases)."""
    threshold_minutes = config.get("threshold_minutes", 30)
    active_phases = config.get("active_phases", ["BUILD", "VERIFY"])

    if not events:
        return []

    # Find current phase from most recent phase_entered event
    current_phase = None
    last_event_time = None

    for event in reversed(events):
        event_type = event.get("event_type", "")
        timestamp = _parse_timestamp(event.get("timestamp"))

        if timestamp and (last_event_time is None or timestamp > last_event_time):
            last_event_time = timestamp

        if event_type == "workflow.phase_entered" and current_phase is None:
            payload = _parse_payload(event.get("payload", {}))
            current_phase = payload.get("phase")

    if current_phase not in active_phases:
        return []

    if last_event_time is None:
        return []

    # Check if stuck
    time_since_last = (datetime.now(UTC) - last_event_time).total_seconds() / 60

    if time_since_last > threshold_minutes:
        return [Anomaly(
            anomaly_id=str(uuid4()),
            rule_id="stuck_session",
            severity=Severity[config.get("severity", "WARNING")],
            correlation_id=correlation_id,
            detected_at=datetime.now(UTC),
            description=config.get("description", "Session appears stuck"),
            details={
                "current_phase": current_phase,
                "minutes_since_activity": round(time_since_last, 1),
                "threshold_minutes": threshold_minutes,
            },
        )]

    return []


def _detect_qa_skipping(
    correlation_id: str,
    events: list[dict],
    config: dict
) -> list[Anomaly]:
    """Rule 2: Detect QA skipping (DEPLOY without VERIFY)."""
    phases_entered = set()
    in_deploy = False

    for event in events:
        if event.get("event_type") != "workflow.phase_entered":
            continue

        payload = _parse_payload(event.get("payload", {}))
        phase = payload.get("phase")
        if phase:
            phases_entered.add(phase)
            if phase == "DEPLOY":
                in_deploy = True

    if in_deploy and "VERIFY" not in phases_entered:
        return [Anomaly(
            anomaly_id=str(uuid4()),
            rule_id="qa_skipping",
            severity=Severity[config.get("severity", "CRITICAL")],
            correlation_id=correlation_id,
            detected_at=datetime.now(UTC),
            description=config.get("description", "DEPLOY without VERIFY"),
            details={
                "phases_entered": list(phases_entered),
                "missing_phase": "VERIFY",
            },
        )]

    return []


def _detect_phase_timeout(
    correlation_id: str,
    events: list[dict],
    config: dict
) -> list[Anomaly]:
    """Rule 3: Detect phase timeouts (duration > 2x baseline)."""
    multiplier = config.get("multiplier", 2.0)
    baselines = config.get("baselines", {
        "UNDERSTAND": 30,
        "PLAN": 60,
        "BUILD": 120,
        "VERIFY": 60,
        "DEPLOY": 30,
    })

    # Extract phase durations
    phase_times: dict[str, dict] = {}

    for event in events:
        event_type = event.get("event_type", "")
        timestamp = _parse_timestamp(event.get("timestamp"))

        if not timestamp:
            continue

        payload = _parse_payload(event.get("payload", {}))
        phase = payload.get("phase")
        if not phase:
            continue

        if phase not in phase_times:
            phase_times[phase] = {"entered": None, "exited": None}

        if event_type == "workflow.phase_entered":
            if phase_times[phase]["entered"] is None:
                phase_times[phase]["entered"] = timestamp
        elif event_type == "workflow.phase_exited":
            phase_times[phase]["exited"] = timestamp

    anomalies = []

    for phase, times in phase_times.items():
        if times["entered"] and times["exited"]:
            duration_min = (times["exited"] - times["entered"]).total_seconds() / 60
            baseline = baselines.get(phase, 60)
            threshold = baseline * multiplier

            if duration_min > threshold:
                anomalies.append(Anomaly(
                    anomaly_id=str(uuid4()),
                    rule_id="phase_timeout",
                    severity=Severity[config.get("severity", "WARNING")],
                    correlation_id=correlation_id,
                    detected_at=datetime.now(UTC),
                    description=f"{phase} phase exceeded timeout",
                    details={
                        "phase": phase,
                        "duration_minutes": round(duration_min, 1),
                        "baseline_minutes": baseline,
                        "threshold_minutes": threshold,
                    },
                ))

    return anomalies


def _detect_review_avoidance(
    correlation_id: str,
    events: list[dict],
    config: dict
) -> list[Anomaly]:
    """Rule 4: Detect review avoidance (PR merged without approvals)."""
    required_approvals = config.get("required_approvals", 1)

    # Look for PR merge events without approval events
    has_merge = False
    approval_count = 0

    for event in events:
        event_type = event.get("event_type", "")

        if event_type == "git.pr_merged":
            has_merge = True
        elif event_type == "git.pr_approved":
            approval_count += 1

    if has_merge and approval_count < required_approvals:
        return [Anomaly(
            anomaly_id=str(uuid4()),
            rule_id="review_avoidance",
            severity=Severity[config.get("severity", "CRITICAL")],
            correlation_id=correlation_id,
            detected_at=datetime.now(UTC),
            description=config.get("description", "PR merged without required approvals"),
            details={
                "approvals_found": approval_count,
                "approvals_required": required_approvals,
            },
        )]

    return []


def _detect_test_regression(
    correlation_id: str,
    events: list[dict],
    config: dict
) -> list[Anomaly]:
    """Rule 5: Detect test regressions (previously passing test now fails)."""
    test_results: dict[str, list[str]] = {}  # test_name -> list of statuses

    for event in events:
        if event.get("event_type") != "test.run_completed":
            continue

        payload = _parse_payload(event.get("payload", {}))

        # Track individual test results if available
        test_details = payload.get("test_details", [])
        for test in test_details:
            name = test.get("name")
            status = test.get("status")
            if name and status:
                if name not in test_results:
                    test_results[name] = []
                test_results[name].append(status)

    anomalies = []

    for test_name, statuses in test_results.items():
        if len(statuses) >= 2:
            # Check if was passing (any previous) and now failing (last)
            previous_statuses = statuses[:-1]
            current_status = statuses[-1]

            if any(s == "PASSED" for s in previous_statuses) and current_status == "FAILED":
                anomalies.append(Anomaly(
                    anomaly_id=str(uuid4()),
                    rule_id="test_regression",
                    severity=Severity[config.get("severity", "ERROR")],
                    correlation_id=correlation_id,
                    detected_at=datetime.now(UTC),
                    description=f"Test regression: {test_name}",
                    details={
                        "test_name": test_name,
                        "previous_status": "PASSED",
                        "current_status": "FAILED",
                    },
                ))

    return anomalies


def _detect_artifact_missing(
    correlation_id: str,
    events: list[dict],
    config: dict
) -> list[Anomaly]:
    """Rule 6: Detect missing artifacts for completed phases."""
    expected = config.get("expected_artifacts", {})

    # Find completed phases and artifacts created
    completed_phases = set()
    artifacts_created: list[str] = []

    for event in events:
        event_type = event.get("event_type", "")

        if event_type == "workflow.phase_exited":
            payload = _parse_payload(event.get("payload", {}))
            phase = payload.get("phase")
            if phase:
                completed_phases.add(phase)

        elif event_type == "artifact.created":
            payload = _parse_payload(event.get("payload", {}))
            path = payload.get("path")
            if path:
                artifacts_created.append(path)

    anomalies = []

    for phase, patterns in expected.items():
        if phase not in completed_phases:
            continue

        # Check if any expected artifact pattern matches
        has_artifact = False
        for pattern in patterns:
            for artifact in artifacts_created:
                if fnmatch.fnmatch(artifact, pattern) or fnmatch.fnmatch(Path(artifact).name, pattern):
                    has_artifact = True
                    break
            if has_artifact:
                break

        if not has_artifact:
            anomalies.append(Anomaly(
                anomaly_id=str(uuid4()),
                rule_id="artifact_missing",
                severity=Severity[config.get("severity", "WARNING")],
                correlation_id=correlation_id,
                detected_at=datetime.now(UTC),
                description=f"Missing artifact for {phase} phase",
                details={
                    "phase": phase,
                    "expected_patterns": patterns,
                    "artifacts_found": artifacts_created,
                },
            ))

    return anomalies


def _detect_agent_loop(
    correlation_id: str,
    events: list[dict],
    config: dict
) -> list[Anomaly]:
    """Rule 7: Detect agent loops (same agent invoked repeatedly)."""
    max_consecutive = config.get("max_consecutive", 5)

    # Track agent invocations
    invocations: list[str] = []

    for event in events:
        if event.get("event_type") != "agent.invoked":
            continue

        payload = _parse_payload(event.get("payload", {}))
        agent_type = payload.get("agent_type")
        if agent_type:
            invocations.append(agent_type)

    # Check for consecutive same-agent invocations
    if len(invocations) < max_consecutive:
        return []

    # Check last N invocations
    last_n = invocations[-max_consecutive:]
    if len(set(last_n)) == 1:
        return [Anomaly(
            anomaly_id=str(uuid4()),
            rule_id="agent_loop",
            severity=Severity[config.get("severity", "WARNING")],
            correlation_id=correlation_id,
            detected_at=datetime.now(UTC),
            description=f"Agent loop detected: {last_n[0]}",
            details={
                "agent_type": last_n[0],
                "consecutive_count": max_consecutive,
                "threshold": max_consecutive,
            },
        )]

    return []


def _detect_orphan_branch(
    correlation_id: str,
    events: list[dict],
    config: dict
) -> list[Anomaly]:
    """Rule 8: Detect orphan branches (no commits for threshold days)."""
    threshold_days = config.get("threshold_days", 3)

    # Find last commit event
    last_commit_time = None

    for event in events:
        if event.get("event_type") in ("git.commit", "git.push"):
            timestamp = _parse_timestamp(event.get("timestamp"))
            if timestamp and (last_commit_time is None or timestamp > last_commit_time):
                last_commit_time = timestamp

    if last_commit_time is None:
        return []

    days_since_commit = (datetime.now(UTC) - last_commit_time).days

    if days_since_commit >= threshold_days:
        return [Anomaly(
            anomaly_id=str(uuid4()),
            rule_id="orphan_branch",
            severity=Severity[config.get("severity", "INFO")],
            correlation_id=correlation_id,
            detected_at=datetime.now(UTC),
            description=config.get("description", "Branch has no recent activity"),
            details={
                "days_since_commit": days_since_commit,
                "threshold_days": threshold_days,
                "last_commit": last_commit_time.isoformat(),
            },
        )]

    return []


# --- Helper Functions ---

def _fetch_events(correlation_id: str) -> list[dict]:
    """Fetch events from v_unified_events."""
    from fs5.core.db import get_connection

    with get_connection() as conn:
        result = conn.execute("""
            SELECT
                event_timestamp,
                event_type,
                payload
            FROM v_unified_events
            WHERE correlation_id = ?
            ORDER BY event_timestamp
        """, [correlation_id]).fetchall()

        return [
            {
                "timestamp": row[0],
                "event_type": row[1],
                "payload": row[2]
            }
            for row in result
        ]


def _parse_timestamp(ts) -> datetime | None:
    """Parse timestamp to datetime."""
    if ts is None:
        return None
    if isinstance(ts, datetime):
        return ts
    if isinstance(ts, str):
        try:
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


def _parse_payload(payload) -> dict:
    """Parse payload which may be string or dict."""
    if isinstance(payload, dict):
        return payload
    if isinstance(payload, str):
        try:
            return json.loads(payload)
        except (json.JSONDecodeError, TypeError):
            return {}
    return {}


def _filter_new_anomalies(anomalies: list[Anomaly], correlation_id: str | None) -> list[Anomaly]:
    """Filter out anomalies that have already been detected."""
    from fs5.core.db import get_connection

    if not anomalies:
        return []

    # Get recently detected anomalies (within cooldown period)
    config = load_rules_config()
    cooldown_minutes = config.get("global", {}).get("alert_cooldown_minutes", 5)
    cutoff = datetime.now(UTC) - timedelta(minutes=cooldown_minutes)

    existing_keys = set()

    try:
        with get_connection() as conn:
            query = """
                SELECT rule_id, correlation_id
                FROM anomalies
                WHERE detected_at > ?
            """
            params = [cutoff]

            if correlation_id:
                query += " AND correlation_id = ?"
                params.append(correlation_id)

            for row in conn.execute(query, params).fetchall():
                existing_keys.add((row[0], row[1]))
    except Exception:
        # If database doesn't exist yet, all anomalies are new
        pass

    return [a for a in anomalies if (a.rule_id, a.correlation_id) not in existing_keys]
