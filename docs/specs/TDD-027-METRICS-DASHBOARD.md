# TDD: Metrics & Dashboard System (Feature Set 5)

**Document ID**: TDD-005
**Version**: 1.0
**Date**: 2026-02-01
**Author**: Technical Architect (Planning Team)
**Status**: Draft
**Related PRD**: PRD-005

---

## 1. Architecture Overview

### 1.1 System Context

```
+-------------------+     +-------------------+     +-------------------+
|   Claude Code     |     |  Metrics System   |     |    Dashboard      |
|   Session         |     |                   |     |                   |
|                   |     |  +-----------+    |     |   workflow-hub    |
|  - Supervisor     +---->+  | events    |    +---->+   .html           |
|  - Agents         |     |  | .jsonl    |    |     |                   |
|  - dbt commands   |     |  +-----------+    |     |   (Browser)       |
|                   |     |       |           |     |                   |
+-------------------+     |       v           |     +-------------------+
                          |  +-----------+    |
                          |  | metrics   |    |
                          |  | .db       |    |
                          |  | (SQLite)  |    |
                          |  +-----------+    |
                          +-------------------+
```

### 1.2 Design Principles

1. **Extend, Don't Replace**: Build on existing infrastructure (events.jsonl, compute-health-pulse.py)
2. **Dual Storage**: JSONL for events (append-only audit trail), SQLite for metrics (queryable)
3. **Zero Infrastructure**: Single-file storage, no external services
4. **Offline First**: All features work without network connectivity
5. **Progressive Enhancement**: Dashboard functional with partial data

### 1.3 Component Diagram

```
+------------------------------------------------------------------+
|                        Metrics System                             |
+------------------------------------------------------------------+
|                                                                   |
|  +------------------+     +------------------+     +-------------+|
|  | Event Capture    |     | Metrics Engine   |     | Dashboard   ||
|  |                  |     |                  |     |             ||
|  | capture-event.py +---->+ sync-metrics.py  +---->+ workflow-   ||
|  | (existing)       |     | compute-         |     | hub.html    ||
|  |                  |     | adherence.py     |     | (extended)  ||
|  +------------------+     | detect-          |     |             ||
|                           | anomalies.py     |     +-------------+|
|  +------------------+     +--------+---------+                    |
|  | Event Sources    |              |                              |
|  |                  |              v                              |
|  | - git commits    |     +------------------+                    |
|  | - phase changes  |     | Storage Layer    |                    |
|  | - agent invokes  |     |                  |                    |
|  | - dbt runs       |     | events.jsonl     |                    |
|  | - artifacts      |     | metrics.db       |                    |
|  +------------------+     +------------------+                    |
|                                                                   |
+------------------------------------------------------------------+
```

---

## 2. SQLite Schema Design

### 2.1 Database Location

```
temp/
  metrics.db              # Primary metrics database
  WORKFLOW_HISTORY/
    events.jsonl          # Append-only event log (existing)
    schema/
      event-schema.json   # Event validation (existing)
```

### 2.2 Core Tables

#### 2.2.1 sessions

Tracks workflow sessions (continuous periods of work on a feature).

```sql
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    worktree_path TEXT,
    branch_name TEXT NOT NULL,
    feature_name TEXT,  -- correlation_id from events
    started_at TEXT NOT NULL,  -- ISO 8601
    ended_at TEXT,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'ended', 'stale')),

    -- Computed scores (updated on sync)
    adherence_score INTEGER,
    health_pulse INTEGER,

    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_sessions_branch ON sessions(branch_name);
CREATE INDEX idx_sessions_status ON sessions(status);
CREATE INDEX idx_sessions_started ON sessions(started_at);
```

#### 2.2.2 phase_transitions

Tracks phase entries and exits (workflow spans).

```sql
CREATE TABLE phase_transitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES sessions(session_id),
    phase TEXT NOT NULL CHECK (phase IN ('UNDERSTAND', 'PLAN', 'BUILD', 'VERIFY', 'DEPLOY')),
    entered_at TEXT NOT NULL,  -- ISO 8601
    exited_at TEXT,
    duration_minutes INTEGER,
    outcome TEXT CHECK (outcome IN ('success', 'redo', 'skip', 'timeout', NULL)),
    is_redo INTEGER DEFAULT 0,  -- 1 if this phase was entered after being exited

    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_phase_session ON phase_transitions(session_id);
CREATE INDEX idx_phase_phase ON phase_transitions(phase);
CREATE INDEX idx_phase_entered ON phase_transitions(entered_at);
```

#### 2.2.3 test_results

Stores test results from dbt runs.

```sql
CREATE TABLE test_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT REFERENCES sessions(session_id),
    run_at TEXT NOT NULL,  -- ISO 8601
    tests_total INTEGER NOT NULL,
    tests_passed INTEGER NOT NULL,
    tests_failed INTEGER NOT NULL,
    tests_warned INTEGER DEFAULT 0,
    tests_skipped INTEGER DEFAULT 0,

    -- For regression detection
    test_names_failed TEXT,  -- JSON array of failed test names

    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_test_session ON test_results(session_id);
CREATE INDEX idx_test_run_at ON test_results(run_at);
```

#### 2.2.4 agent_invocations

Tracks agent invocations and handoffs.

```sql
CREATE TABLE agent_invocations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT REFERENCES sessions(session_id),
    agent_name TEXT NOT NULL,
    invoked_at TEXT NOT NULL,  -- ISO 8601
    task_description TEXT,
    outcome TEXT CHECK (outcome IN ('success', 'failure', 'redo', 'pending', NULL)),
    duration_minutes INTEGER,
    artifacts_created TEXT,  -- JSON array of artifact paths

    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_agent_session ON agent_invocations(session_id);
CREATE INDEX idx_agent_name ON agent_invocations(agent_name);
CREATE INDEX idx_agent_invoked ON agent_invocations(invoked_at);
```

#### 2.2.5 daily_metrics

Aggregated metrics for trending and reporting.

```sql
CREATE TABLE daily_metrics (
    date TEXT PRIMARY KEY,  -- YYYY-MM-DD

    -- Session metrics
    sessions_active INTEGER DEFAULT 0,
    sessions_completed INTEGER DEFAULT 0,

    -- Score averages
    adherence_score_avg REAL,
    adherence_score_min INTEGER,
    adherence_score_max INTEGER,
    health_pulse_avg REAL,

    -- Test metrics
    tests_run INTEGER DEFAULT 0,
    tests_passed INTEGER DEFAULT 0,
    tests_failed INTEGER DEFAULT 0,
    bugs_regressed INTEGER DEFAULT 0,  -- Tests that were passing now fail

    -- Agent metrics
    agent_invocations INTEGER DEFAULT 0,

    -- PR metrics (from GitHub)
    review_rounds_avg REAL,
    time_to_merge_hours_avg REAL,

    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);
```

#### 2.2.6 anomalies

Detected workflow anomalies.

```sql
CREATE TABLE anomalies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT REFERENCES sessions(session_id),
    anomaly_type TEXT NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('INFO', 'WARNING', 'ERROR', 'CRITICAL')),
    detected_at TEXT NOT NULL,  -- ISO 8601
    details TEXT,  -- JSON with context
    resolved_at TEXT,
    resolved_by TEXT,  -- 'auto' or user action
    acknowledged INTEGER DEFAULT 0,

    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_anomaly_session ON anomalies(session_id);
CREATE INDEX idx_anomaly_type ON anomalies(anomaly_type);
CREATE INDEX idx_anomaly_severity ON anomalies(severity);
CREATE INDEX idx_anomaly_resolved ON anomalies(resolved_at);
```

#### 2.2.7 pr_metrics

GitHub PR metrics (synced from API).

```sql
CREATE TABLE pr_metrics (
    pr_number INTEGER PRIMARY KEY,
    branch_name TEXT NOT NULL,
    session_id TEXT REFERENCES sessions(session_id),
    title TEXT,
    opened_at TEXT,
    merged_at TEXT,
    time_to_merge_hours REAL,
    review_rounds INTEGER DEFAULT 0,
    approvals INTEGER DEFAULT 0,
    changes_requested INTEGER DEFAULT 0,

    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_pr_branch ON pr_metrics(branch_name);
CREATE INDEX idx_pr_session ON pr_metrics(session_id);
```

### 2.3 Sync Tracking

```sql
CREATE TABLE sync_state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Track last processed event for incremental sync
-- INSERT INTO sync_state (key, value) VALUES ('last_event_line', '0');
```

---

## 3. Scoring Formula Specification

### 3.1 Adherence Score

#### 3.1.1 Formula

```python
def calculate_adherence_score(session_id: str, db: sqlite3.Connection) -> dict:
    """
    Calculate adherence score for a session.

    Returns:
        {
            "score": 85,
            "base_points": 100,
            "completion_bonus": 0,
            "penalties": [
                {"type": "redo", "phase": "BUILD", "points": -5}
            ],
            "breakdown": {
                "UNDERSTAND": {"completed": True, "points": 10},
                "PLAN": {"completed": True, "points": 25},
                ...
            }
        }
    """
    # Phase points
    PHASE_POINTS = {
        "UNDERSTAND": 10,
        "PLAN": 25,
        "BUILD": 30,
        "VERIFY": 20,
        "DEPLOY": 15,
    }

    # Penalty values
    PENALTIES = {
        "redo": 5,       # Per redo
        "skip": 15,      # Per skipped phase
        "out_of_order": 10,  # Per out-of-order phase
        "timeout": 5,    # Per timeout
    }

    # Completion bonus
    COMPLETION_BONUS = 20  # All phases in order

    # Query phase transitions
    phases = query_phase_transitions(db, session_id)

    # Calculate base points
    base_points = sum(
        PHASE_POINTS[p.phase] for p in phases
        if p.outcome == "success"
    )

    # Check for completion bonus
    canonical_order = ["UNDERSTAND", "PLAN", "BUILD", "VERIFY", "DEPLOY"]
    completed_order = [p.phase for p in phases if p.outcome == "success"]
    completion_bonus = COMPLETION_BONUS if completed_order == canonical_order else 0

    # Calculate penalties
    penalties = []

    # Redo penalties
    for p in phases:
        if p.is_redo:
            penalties.append({
                "type": "redo",
                "phase": p.phase,
                "points": -PENALTIES["redo"]
            })

    # Skip penalties
    completed_phases = set(p.phase for p in phases)
    for phase in canonical_order:
        if phase not in completed_phases and has_downstream_phase(phases, phase):
            penalties.append({
                "type": "skip",
                "phase": phase,
                "points": -PENALTIES["skip"]
            })

    # Out-of-order penalties
    for i, p in enumerate(phases):
        expected_index = canonical_order.index(p.phase)
        if i > 0 and phases[i-1].phase in canonical_order:
            prev_index = canonical_order.index(phases[i-1].phase)
            if expected_index < prev_index:
                penalties.append({
                    "type": "out_of_order",
                    "phase": p.phase,
                    "points": -PENALTIES["out_of_order"]
                })

    # Timeout penalties
    for p in phases:
        if p.outcome == "timeout":
            penalties.append({
                "type": "timeout",
                "phase": p.phase,
                "points": -PENALTIES["timeout"]
            })

    # Calculate final score
    total_penalties = sum(p["points"] for p in penalties)
    score = max(0, min(100, base_points + completion_bonus + total_penalties))

    return {
        "score": score,
        "base_points": base_points,
        "completion_bonus": completion_bonus,
        "penalties": penalties,
        "breakdown": {
            phase: {
                "completed": phase in completed_phases,
                "points": PHASE_POINTS[phase] if phase in completed_phases else 0
            }
            for phase in canonical_order
        }
    }
```

#### 3.1.2 Score Rating

```python
def get_adherence_rating(score: int) -> str:
    """Convert score to rating."""
    if score >= 85:
        return "EXCELLENT"
    elif score >= 70:
        return "GOOD"
    elif score >= 50:
        return "FAIR"
    else:
        return "POOR"
```

### 3.2 Health Pulse (Existing)

The existing `compute-health-pulse.py` already implements:

```python
# Components (25% weight each)
HEALTH_COMPONENTS = {
    "commit_velocity": 0.25,    # Commits per day (target: 3-5/day)
    "phase_duration": 0.25,     # Days on branch vs expected
    "test_coverage": 0.25,      # Test pass count vs baseline
    "agent_collaboration": 0.25 # % commits with Co-Authored-By
}
```

No changes needed to the formula, but results will be stored in SQLite.

---

## 4. Anomaly Detection Rules Engine

### 4.1 Rules Configuration

Rules are defined in YAML for extensibility:

```yaml
# temp/WORKFLOW_HISTORY/config/anomaly-rules.yaml
version: 1

rules:
  - id: stuck_session
    name: Stuck Session
    description: No events for extended period during active phase
    severity: WARNING
    condition:
      type: event_gap
      threshold_minutes: 30
      active_phases: [BUILD, VERIFY]
    auto_resolve: true
    resolve_on: any_event

  - id: qa_skipping
    name: QA Skipping
    description: DEPLOY phase without VERIFY phase
    severity: CRITICAL
    condition:
      type: missing_phase
      required: VERIFY
      before: DEPLOY
    auto_resolve: false

  - id: phase_timeout
    name: Phase Timeout
    description: Phase duration exceeds 2x baseline
    severity: WARNING
    condition:
      type: duration_exceeded
      multiplier: 2.0
      baseline_source: phase-baselines.json
    auto_resolve: true
    resolve_on: phase_exit

  - id: review_avoidance
    name: Review Avoidance
    description: PR merged without required approvals
    severity: CRITICAL
    condition:
      type: pr_check
      required_approvals: 1
    auto_resolve: false

  - id: test_regression
    name: Test Regression
    description: Test that was passing is now failing
    severity: ERROR
    condition:
      type: test_state_change
      from_state: PASS
      to_state: FAIL
    auto_resolve: true
    resolve_on: test_pass

  - id: artifact_missing
    name: Artifact Missing
    description: Phase completed without expected artifact
    severity: WARNING
    condition:
      type: artifact_check
      phase_artifacts:
        PLAN: [PRD, TDD]  # At least one
        BUILD: [model, test]
        VERIFY: [TESTING_doc]
    auto_resolve: true
    resolve_on: artifact_created

  - id: agent_loop
    name: Agent Loop
    description: Same agent invoked repeatedly without progress
    severity: WARNING
    condition:
      type: agent_repeat
      threshold_count: 5
      progress_indicator: commit
    auto_resolve: true
    resolve_on: progress

  - id: orphan_branch
    name: Orphan Branch
    description: Branch with no activity for extended period
    severity: INFO
    condition:
      type: branch_staleness
      threshold_days: 3
    auto_resolve: true
    resolve_on: commit
```

### 4.2 Detection Engine

```python
# scripts/detect-anomalies.py

class AnomalyDetector:
    """Detects workflow anomalies based on configured rules."""

    def __init__(self, db: sqlite3.Connection, rules_path: Path):
        self.db = db
        self.rules = self._load_rules(rules_path)

    def detect_all(self, session_id: str | None = None) -> list[Anomaly]:
        """Detect all anomalies for a session or all active sessions."""
        anomalies = []

        sessions = self._get_sessions(session_id)

        for session in sessions:
            for rule in self.rules:
                if self._check_rule(rule, session):
                    anomaly = Anomaly(
                        session_id=session.session_id,
                        anomaly_type=rule["id"],
                        severity=rule["severity"],
                        detected_at=datetime.now(timezone.utc).isoformat(),
                        details=self._get_details(rule, session)
                    )
                    anomalies.append(anomaly)

        return anomalies

    def _check_rule(self, rule: dict, session: Session) -> bool:
        """Check if a rule condition is met."""
        condition = rule["condition"]

        if condition["type"] == "event_gap":
            return self._check_event_gap(condition, session)
        elif condition["type"] == "missing_phase":
            return self._check_missing_phase(condition, session)
        elif condition["type"] == "duration_exceeded":
            return self._check_duration_exceeded(condition, session)
        # ... other condition types

        return False

    def _check_event_gap(self, condition: dict, session: Session) -> bool:
        """Check for stuck session (no events for threshold)."""
        threshold = timedelta(minutes=condition["threshold_minutes"])
        active_phases = condition.get("active_phases", [])

        # Get current phase
        current_phase = self._get_current_phase(session.session_id)
        if current_phase and current_phase not in active_phases:
            return False

        # Get last event
        last_event = self._get_last_event(session.session_id)
        if not last_event:
            return False

        # Check gap
        gap = datetime.now(timezone.utc) - last_event.timestamp
        return gap > threshold
```

---

## 5. Dashboard Extension Design

### 5.1 Architecture

The dashboard extends `workflow-hub.html` (or creates a new `metrics-dashboard.html` tab).

```
+------------------------------------------------------------------+
| WORKFLOW METRICS DASHBOARD                           [Refresh]    |
+------------------------------------------------------------------+
|                                                                   |
| +-----------------+ +-----------------+ +-----------------+       |
| | SESSION STATUS  | | ADHERENCE       | | HEALTH PULSE   |       |
| |                 | |                 | |                |       |
| | Branch: feat/x  | | Score: 85       | | Score: 73      |       |
| | Phase: BUILD    | | Rating: GOOD    | | Rating: GOOD   |       |
| | Time: 1h 23m    | | [View Details]  | | [View Details] |       |
| +-----------------+ +-----------------+ +-----------------+       |
|                                                                   |
| +---------------------------------------------------------------+|
| | PHASE TIMELINE                                                ||
| |                                                               ||
| | [UNDERSTAND] [PLAN] [BUILD*] [VERIFY] [DEPLOY]               ||
| |    (10min)   (45min) (1h23m)  (---)    (---)                 ||
| |                                                               ||
| +---------------------------------------------------------------+|
|                                                                   |
| +--------------------------+ +----------------------------------+|
| | ANOMALY ALERTS (2)       | | AGENT ACTIVITY                  ||
| |                          | |                                  ||
| | [!] CRITICAL: QA Skip    | | 14:23 PM: PRD created           ||
| | [!] WARNING: Stuck 35min | | 14:45 Architect: TDD created    ||
| |                          | | 15:10 Developer: Started build  ||
| | [Dismiss All]            | | 15:30 (current)                 ||
| +--------------------------+ +----------------------------------+|
|                                                                   |
+------------------------------------------------------------------+
```

### 5.2 Data Flow

```
+------------------+     +------------------+     +------------------+
| SQLite metrics.db|     | API Endpoint     |     | Dashboard HTML   |
|                  |     | (file:// JSON)   |     |                  |
| - sessions       +---->+ metrics.json     +---->+ JavaScript       |
| - phases         |     | (generated)      |     | fetch & render   |
| - anomalies      |     |                  |     |                  |
+------------------+     +------------------+     +------------------+
```

Since the dashboard runs from `file://`, we use a generated JSON file rather than a live API:

```bash
# Generate dashboard data
uv run scripts/generate-dashboard-data.py --output temp/WORKFLOW_HISTORY/dashboard-data.json
```

### 5.3 Dashboard Data Schema

```json
{
  "generated_at": "2026-02-01T12:00:00Z",
  "session": {
    "session_id": "abc123",
    "branch_name": "feat/customer-analytics",
    "feature_name": "Customer Analytics",
    "current_phase": "BUILD",
    "time_in_phase_minutes": 83,
    "status": "active"
  },
  "scores": {
    "adherence": {
      "score": 85,
      "rating": "GOOD",
      "breakdown": {
        "UNDERSTAND": {"completed": true, "points": 10},
        "PLAN": {"completed": true, "points": 25},
        "BUILD": {"completed": false, "points": 0},
        "VERIFY": {"completed": false, "points": 0},
        "DEPLOY": {"completed": false, "points": 0}
      },
      "penalties": []
    },
    "health_pulse": {
      "score": 73,
      "rating": "GOOD",
      "components": [
        {"name": "Commit Velocity", "score": 80, "weight": 0.25},
        {"name": "Phase Duration", "score": 70, "weight": 0.25},
        {"name": "Test Coverage", "score": 75, "weight": 0.25},
        {"name": "Agent Collaboration", "score": 67, "weight": 0.25}
      ]
    }
  },
  "phase_timeline": [
    {"phase": "UNDERSTAND", "status": "complete", "duration_minutes": 10},
    {"phase": "PLAN", "status": "complete", "duration_minutes": 45},
    {"phase": "BUILD", "status": "active", "duration_minutes": 83},
    {"phase": "VERIFY", "status": "pending", "duration_minutes": null},
    {"phase": "DEPLOY", "status": "pending", "duration_minutes": null}
  ],
  "anomalies": [
    {
      "id": 1,
      "type": "qa_skipping",
      "severity": "CRITICAL",
      "detected_at": "2026-02-01T11:30:00Z",
      "details": "DEPLOY phase entered without VERIFY"
    }
  ],
  "agent_activity": [
    {"timestamp": "2026-02-01T10:23:00Z", "agent": "PM", "action": "PRD created"},
    {"timestamp": "2026-02-01T10:45:00Z", "agent": "Architect", "action": "TDD created"},
    {"timestamp": "2026-02-01T11:10:00Z", "agent": "Developer", "action": "Started implementation"}
  ],
  "tests": {
    "total": 171,
    "passed": 171,
    "failed": 0,
    "warned": 0,
    "baseline": 171,
    "regressions": 0
  }
}
```

### 5.4 Widget Components

#### 5.4.1 Session Status Widget

```javascript
function renderSessionStatus(data) {
  const session = data.session;
  return `
    <div class="widget session-status">
      <h3>Session Status</h3>
      <div class="metric">
        <span class="label">Branch</span>
        <span class="value">${session.branch_name}</span>
      </div>
      <div class="metric">
        <span class="label">Phase</span>
        <span class="value phase-${session.current_phase.toLowerCase()}">${session.current_phase}</span>
      </div>
      <div class="metric">
        <span class="label">Time in Phase</span>
        <span class="value">${formatDuration(session.time_in_phase_minutes)}</span>
      </div>
    </div>
  `;
}
```

#### 5.4.2 Score Widget

```javascript
function renderScoreWidget(name, score, rating, breakdown) {
  const ratingClass = rating.toLowerCase();
  return `
    <div class="widget score-widget">
      <h3>${name}</h3>
      <div class="score-display">
        <span class="score ${ratingClass}">${score}</span>
        <span class="rating ${ratingClass}">${rating}</span>
      </div>
      ${breakdown ? renderBreakdown(breakdown) : ''}
    </div>
  `;
}
```

#### 5.4.3 Phase Timeline Widget

```javascript
function renderPhaseTimeline(phases) {
  return `
    <div class="widget phase-timeline">
      <h3>Phase Timeline</h3>
      <div class="timeline">
        ${phases.map(p => `
          <div class="phase ${p.status}">
            <span class="name">${p.phase}</span>
            <span class="duration">${p.duration_minutes ? formatDuration(p.duration_minutes) : '---'}</span>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}
```

#### 5.4.4 Anomaly Alert Panel

```javascript
function renderAnomalyPanel(anomalies) {
  if (anomalies.length === 0) {
    return `
      <div class="widget anomaly-panel clear">
        <h3>Anomaly Alerts</h3>
        <div class="no-anomalies">All clear - no anomalies detected</div>
      </div>
    `;
  }

  return `
    <div class="widget anomaly-panel">
      <h3>Anomaly Alerts (${anomalies.length})</h3>
      <div class="anomaly-list">
        ${anomalies.map(a => `
          <div class="anomaly ${a.severity.toLowerCase()}">
            <span class="severity">${a.severity}</span>
            <span class="type">${a.type}</span>
            <span class="details">${a.details}</span>
            <button onclick="dismissAnomaly(${a.id})">Dismiss</button>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}
```

---

## 6. Integration with Existing Systems

### 6.1 Integration with Health Pulse

```python
# Extend compute-health-pulse.py to store results

def compute_and_store_health_pulse(db: sqlite3.Connection) -> HealthPulse:
    """Compute health pulse and store in SQLite."""
    pulse = compute_health_pulse()  # Existing function

    # Store in sessions table
    db.execute("""
        UPDATE sessions
        SET health_pulse = ?, updated_at = datetime('now')
        WHERE status = 'active'
    """, (pulse.score,))

    # Store in daily_metrics
    today = date.today().isoformat()
    db.execute("""
        INSERT INTO daily_metrics (date, health_pulse_avg)
        VALUES (?, ?)
        ON CONFLICT(date) DO UPDATE SET
            health_pulse_avg = (
                COALESCE(health_pulse_avg * sessions_active, 0) + ?
            ) / (sessions_active + 1),
            updated_at = datetime('now')
    """, (today, pulse.score, pulse.score))

    return pulse
```

### 6.2 Integration with Workflow Chronicle

The existing `workflow-chronicle.html` provides timeline visualization. Metrics dashboard will:

1. Link to Chronicle for detailed commit history
2. Share styling/theming
3. Use same data generation pipeline

```javascript
// Link from dashboard to chronicle
function viewDetailedTimeline() {
  window.location.href = 'workflow-chronicle.html?session=' + currentSessionId;
}
```

### 6.3 Integration with Supervisor

```markdown
# .claude/agents/supervisor.md (additions)

## Session Wake-Up Procedure

When starting or resuming a session:

1. Check for active session in metrics.db
2. Run anomaly detection
3. Display health summary

### Health Summary Format

```

[WORKFLOW METRICS]
Session: feat/customer-analytics (1h 23m)
Adherence: 85/100 GOOD
Health:    73/100 GOOD
Anomalies: 1 WARNING (stuck session)

Phase: BUILD (45min elapsed, 30min typical)

```

### Invoke on Session Start

```bash
# Add to supervisor wake-up
uv run scripts/detect-anomalies.py --session active --format summary
```

```

### 6.4 Integration with dbt-run Command

```python
# Extend /dbt-run command to capture test results

def dbt_run_with_metrics(command: str) -> None:
    """Run dbt command and capture test results."""

    # Run dbt command
    result = subprocess.run(
        ["uv", "run", "dbt"] + command.split(),
        capture_output=True,
        text=True
    )

    # Parse test results
    test_results = parse_dbt_output(result.stdout + result.stderr)

    # Capture event
    event = {
        "schema_version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": "test.completed",
        "source": {"type": "system", "identity": "dbt"},
        "correlation_id": get_current_branch(),
        "payload": {
            "tests_total": test_results.total,
            "tests_passed": test_results.passed,
            "tests_failed": test_results.failed,
            "tests_warned": test_results.warned,
            "test_names_failed": test_results.failed_names
        }
    }

    # Append to events.jsonl
    capture_event(event)
```

---

## 7. Implementation Sequence

### 7.1 Phase 1: Foundation (Week 1)

```
Day 1-2: SQLite Schema
  - Create temp/metrics.db with all tables
  - Add indexes
  - Write schema validation tests

Day 3-4: Sync Script
  - Create scripts/sync-metrics.py
  - Implement event parsing
  - Implement incremental sync
  - Handle edge cases (empty events, malformed data)

Day 5: Event Schema Extension
  - Add test.completed event type
  - Update event-schema.json
  - Write validation tests
```

### 7.2 Phase 2: Metrics Collection (Week 2)

```
Day 1-2: Test Result Capture
  - Modify /dbt-run command
  - Parse dbt output for PASS/FAIL counts
  - Emit test.completed events

Day 3: PR Metrics
  - Create scripts/capture-pr-metrics.py
  - Implement GitHub API calls
  - Store in pr_metrics table

Day 4-5: Adherence Calculator
  - Create scripts/compute-adherence.py
  - Implement scoring formula
  - Store in sessions table
  - Add bug regression detection
```

### 7.3 Phase 3: Anomaly Detection (Week 3)

```
Day 1-2: Rules Engine
  - Create scripts/detect-anomalies.py
  - Implement rule loading from YAML
  - Implement base condition checking

Day 3-4: Rule Implementation
  - Implement all 8 rules
  - Add auto-resolve logic
  - Store in anomalies table

Day 5: Alerting
  - Implement console output
  - Add severity coloring
  - Add --quiet flag for CI
```

### 7.4 Phase 4: Dashboard (Week 4)

```
Day 1: Data Generation
  - Create scripts/generate-dashboard-data.py
  - Output to temp/WORKFLOW_HISTORY/dashboard-data.json

Day 2-3: Dashboard HTML
  - Extend workflow-hub.html (or create new)
  - Implement widget components
  - Add styling

Day 4-5: Integration
  - Wire up data fetching
  - Add auto-refresh
  - Add anomaly dismissal
```

### 7.5 Phase 5: Polish (Week 5)

```
Day 1-2: Performance
  - Profile SQLite queries
  - Add indexes if needed
  - Optimize dashboard loading

Day 3-4: Documentation
  - Update PLAYGROUND-TOOLS.md
  - Add --help to all scripts
  - Write troubleshooting guide

Day 5: Supervisor Integration
  - Add metrics check to wake-up
  - Display health summary
  - Final testing
```

---

## 8. Testing Strategy

### 8.1 Unit Tests

```python
# tests/test_adherence.py

def test_adherence_perfect_score():
    """Perfect workflow should score 100."""
    events = [
        phase_event("UNDERSTAND", "entered"),
        phase_event("UNDERSTAND", "exited", outcome="success"),
        phase_event("PLAN", "entered"),
        phase_event("PLAN", "exited", outcome="success"),
        phase_event("BUILD", "entered"),
        phase_event("BUILD", "exited", outcome="success"),
        phase_event("VERIFY", "entered"),
        phase_event("VERIFY", "exited", outcome="success"),
        phase_event("DEPLOY", "entered"),
        phase_event("DEPLOY", "exited", outcome="success"),
    ]

    score = calculate_adherence_score(events)
    assert score["score"] == 100
    assert score["completion_bonus"] == 20

def test_adherence_redo_penalty():
    """Redo should deduct 5 points."""
    events = [
        phase_event("BUILD", "entered"),
        phase_event("BUILD", "exited", outcome="success"),
        phase_event("BUILD", "entered", is_redo=True),  # Redo
        phase_event("BUILD", "exited", outcome="success"),
    ]

    score = calculate_adherence_score(events)
    assert any(p["type"] == "redo" for p in score["penalties"])
    assert score["score"] == 30 - 5  # BUILD points minus redo penalty

def test_adherence_skip_penalty():
    """Skipped phase should deduct 15 points."""
    events = [
        phase_event("PLAN", "entered"),
        phase_event("PLAN", "exited", outcome="success"),
        # VERIFY skipped
        phase_event("DEPLOY", "entered"),
        phase_event("DEPLOY", "exited", outcome="success"),
    ]

    score = calculate_adherence_score(events)
    assert any(p["type"] == "skip" and p["phase"] == "VERIFY" for p in score["penalties"])
```

### 8.2 Integration Tests

```python
# tests/test_sync.py

def test_sync_incremental():
    """Sync should process only new events."""
    # Create initial events
    write_events([event1, event2])
    sync_metrics(db)

    # Add more events
    write_events([event3, event4])

    # Sync should only process event3, event4
    sync_metrics(db)

    # Verify sync state
    last_line = get_sync_state(db, "last_event_line")
    assert last_line == 4

def test_sync_full_resync():
    """Full resync should rebuild from scratch."""
    # Create events
    write_events([event1, event2, event3])
    sync_metrics(db)

    # Modify event (simulate corruption fix)
    modify_event(1, fixed_event)

    # Full resync
    sync_metrics(db, full_resync=True)

    # Verify data matches fixed event
    session = get_session(db, "session1")
    assert session.status == fixed_event.status
```

### 8.3 End-to-End Tests

```bash
# Manual E2E test script

# 1. Create test session
git checkout -b test/metrics-e2e

# 2. Emit phase events
uv run scripts/capture-event.py --type phase.entered --phase UNDERSTAND

# 3. Sync metrics
uv run scripts/sync-metrics.py

# 4. Verify adherence score
uv run scripts/compute-adherence.py --format json | jq '.score'

# 5. Introduce anomaly (skip VERIFY)
uv run scripts/capture-event.py --type phase.entered --phase DEPLOY

# 6. Detect anomaly
uv run scripts/detect-anomalies.py --session active

# 7. Generate dashboard data
uv run scripts/generate-dashboard-data.py

# 8. Open dashboard
open playgrounds/workflow-hub.html

# 9. Verify anomaly displayed
```

---

## 9. File Summary

### 9.1 New Files

| File | Purpose |
|------|---------|
| `temp/metrics.db` | SQLite metrics database |
| `scripts/sync-metrics.py` | Sync events to SQLite |
| `scripts/compute-adherence.py` | Calculate adherence score |
| `scripts/detect-anomalies.py` | Detect workflow anomalies |
| `scripts/generate-dashboard-data.py` | Generate dashboard JSON |
| `scripts/capture-pr-metrics.py` | Fetch PR metrics from GitHub |
| `temp/WORKFLOW_HISTORY/config/anomaly-rules.yaml` | Anomaly rule definitions |
| `temp/WORKFLOW_HISTORY/dashboard-data.json` | Dashboard data (generated) |

### 9.2 Modified Files

| File | Modification |
|------|--------------|
| `temp/WORKFLOW_HISTORY/schema/event-schema.json` | Add test.completed event type |
| `playgrounds/workflow-hub.html` | Add metrics widgets |
| `.claude/agents/supervisor.md` | Add metrics wake-up procedure |
| `.claude/commands/dbt-run.md` | Add test result capture |
| `scripts/compute-health-pulse.py` | Add SQLite storage |

### 9.3 Documentation Files

| File | Content |
|------|---------|
| `docs/for_chris/METRICS-DASHBOARD-GUIDE.md` | User guide |
| `docs/reference/LEARNINGS.md` | Adherence scoring formula |
| `temp/2026_02_01_Discussion/metrics_dashboard_TDD.md` | This document |

---

## 10. Open Technical Questions

### 10.1 Resolved

| Question | Decision |
|----------|----------|
| SQLite vs DuckDB for metrics? | SQLite (simpler, sufficient) |
| Replace events.jsonl? | No (keep for audit trail) |
| Real-time dashboard? | No (polling/refresh sufficient) |

### 10.2 Open

| Question | Options | Recommendation |
|----------|---------|----------------|
| Dashboard location | Extend workflow-hub.html vs new file | Extend hub (consolidation) |
| Anomaly rule storage | YAML vs database | YAML (human-editable) |
| PR metrics frequency | On-demand vs scheduled | On-demand with caching |

---

*TDD complete. Ready for implementation.*
