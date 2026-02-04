-- FS5 Live Views for JSONL Event Sources
-- Version: v0.10.0 - Created: 2026-02-03
-- Purpose: Real-time views that query JSONL files using DuckDB's read_json_auto()

-- v_memory_events - Query memory/events.jsonl
CREATE OR REPLACE VIEW v_memory_events AS
SELECT
    md5(j::VARCHAR || json_extract_string(j, '$.timestamp'))::UUID AS event_id,
    json_extract_string(j, '$.timestamp')::TIMESTAMPTZ AS event_timestamp,
    CASE json_extract_string(j, '$.event')
        WHEN 'session_logged' THEN 'memory.session_logged'
        WHEN 'week_consolidated' THEN 'memory.week_consolidated'
        ELSE 'memory.' || json_extract_string(j, '$.event')
    END AS event_type,
    'agent' AS source_type,
    'sage' AS source_identity,
    json_extract_string(j, '$.data.session_id') AS session_id,
    COALESCE(
        json_extract_string(j, '$.data.correlation_id'),
        'unknown'
    ) AS correlation_id,
    json_extract(j, '$.data') AS payload,
    j AS raw_json
FROM read_json_auto('memory/events.jsonl') AS t(j)
WHERE json_extract_string(j, '$.event') IS NOT NULL;

-- v_chronicle_events - Query temp/WORKFLOW_HISTORY/events.jsonl
CREATE OR REPLACE VIEW v_chronicle_events AS
SELECT
    COALESCE(
        json_extract_string(j, '$.event_id')::UUID,
        md5(j::VARCHAR)::UUID
    ) AS event_id,
    json_extract_string(j, '$.timestamp')::TIMESTAMPTZ AS event_timestamp,
    CASE json_extract_string(j, '$.event_type')
        WHEN 'phase.entered' THEN 'workflow.phase_entered'
        WHEN 'phase.exited' THEN 'workflow.phase_exited'
        WHEN 'agent.invoked' THEN 'agent.invoked'
        WHEN 'commit' THEN 'git.commit'
        ELSE json_extract_string(j, '$.event_type')
    END AS event_type,
    COALESCE(json_extract_string(j, '$.source'), 'chronicle') AS source_identity,
    'system' AS source_type,
    json_extract_string(j, '$.correlation_id') AS correlation_id,
    json_extract(j, '$.data') AS payload,
    j AS raw_json
FROM read_json_auto('temp/WORKFLOW_HISTORY/events.jsonl') AS t(j)
WHERE json_extract_string(j, '$.event_type') IS NOT NULL;

-- v_qa_events - Query temp/QA_METRICS_LOG.jsonl
CREATE OR REPLACE VIEW v_qa_events AS
SELECT
    md5(j::VARCHAR || json_extract_string(j, '$.timestamp'))::UUID AS event_id,
    json_extract_string(j, '$.timestamp')::TIMESTAMPTZ AS event_timestamp,
    CASE json_extract_string(j, '$.status')
        WHEN 'PASSED' THEN 'qa.gate_passed'
        WHEN 'SKIPPED' THEN 'qa.gate_skipped'
        ELSE 'qa.gate_checked'
    END AS event_type,
    'agent' AS source_type,
    COALESCE(json_extract_string(j, '$.reviewer'), 'qa-reviewer') AS source_identity,
    json_extract_string(j, '$.session_id') AS session_id,
    json_extract_string(j, '$.session_id') AS correlation_id,
    json_extract(j, '$') AS payload,
    j AS raw_json
FROM read_json_auto('temp/QA_METRICS_LOG.jsonl') AS t(j)
WHERE json_extract_string(j, '$.gate') IS NOT NULL;

-- v_unified_events - Union all event sources
CREATE OR REPLACE VIEW v_unified_events AS
SELECT
    event_id,
    event_timestamp,
    event_type,
    source_type,
    source_identity,
    session_id,
    correlation_id,
    payload,
    raw_json,
    'memory' AS source_file
FROM v_memory_events

UNION ALL

SELECT
    event_id,
    event_timestamp,
    event_type,
    source_type,
    source_identity,
    NULL AS session_id,
    correlation_id,
    payload,
    raw_json,
    'chronicle' AS source_file
FROM v_chronicle_events

UNION ALL

SELECT
    event_id,
    event_timestamp,
    event_type,
    source_type,
    source_identity,
    session_id,
    correlation_id,
    payload,
    raw_json,
    'qa' AS source_file
FROM v_qa_events;
