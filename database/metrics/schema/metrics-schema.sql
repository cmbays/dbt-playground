-- FS5 Metrics Database Schema
-- Version: v0.10.0 - Created: 2026-02-03
-- Purpose: Core tables for the metrics and dashboard system

-- Sessions table (tracks active sessions)
CREATE TABLE IF NOT EXISTS sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    correlation_id VARCHAR NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    ended_at TIMESTAMPTZ,
    current_phase VARCHAR,
    phase_entered_at TIMESTAMPTZ,
    status VARCHAR DEFAULT 'active',  -- active, stuck, complete
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Adherence scores (calculated scores)
CREATE TABLE IF NOT EXISTS adherence_scores (
    score_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    correlation_id VARCHAR NOT NULL,
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    final_score INTEGER NOT NULL,
    base_points INTEGER NOT NULL,
    completion_bonus INTEGER NOT NULL DEFAULT 0,
    penalties JSON,  -- Array of penalty objects
    rating VARCHAR NOT NULL,
    UNIQUE (correlation_id, calculated_at)
);

-- Anomalies (detected issues)
CREATE TABLE IF NOT EXISTS anomalies (
    anomaly_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_id VARCHAR NOT NULL,
    severity VARCHAR NOT NULL,
    correlation_id VARCHAR NOT NULL,
    detected_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    description VARCHAR NOT NULL,
    details JSON,
    resolved_at TIMESTAMPTZ,
    resolution VARCHAR,
    acknowledged_at TIMESTAMPTZ,
    acknowledged_by VARCHAR
);

-- Transition events (from FS2 hook - optional persistence)
CREATE TABLE IF NOT EXISTS transition_events (
    event_id UUID PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    task_id VARCHAR NOT NULL,
    from_stage VARCHAR,
    to_stage VARCHAR NOT NULL,
    payload JSON,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Daily aggregates (pre-computed for dashboard)
CREATE TABLE IF NOT EXISTS daily_aggregates (
    date DATE PRIMARY KEY,
    total_sessions INTEGER DEFAULT 0,
    avg_adherence_score DECIMAL(5,2),
    anomalies_detected INTEGER DEFAULT 0,
    anomalies_resolved INTEGER DEFAULT 0,
    test_count INTEGER,
    test_pass_rate DECIMAL(5,2),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Create indexes for query performance
CREATE INDEX IF NOT EXISTS idx_sessions_correlation ON sessions(correlation_id);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);
-- Note: DuckDB does not support partial indexes (WHERE clause)
-- For active anomalies, use composite index instead
CREATE INDEX IF NOT EXISTS idx_anomalies_correlation ON anomalies(correlation_id);
CREATE INDEX IF NOT EXISTS idx_anomalies_resolved ON anomalies(resolved_at);
CREATE INDEX IF NOT EXISTS idx_anomalies_severity ON anomalies(severity);
CREATE INDEX IF NOT EXISTS idx_adherence_correlation ON adherence_scores(correlation_id);
