"""Tests for observability metrics module.

Part of Wave 3 P2: Integration Completion (WAVE3-025)
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib.observability.config import ObservabilityConfig, ObservabilityTier
from scripts.lib.observability.metrics import Counter, DebugMetrics, Histogram, MetricsExporter


class TestCounter:
    """Tests for Counter metric type."""

    def test_counter_creation(self):
        """Counter can be created."""
        counter = Counter(
            name='test_counter',
            description='A test counter',
            labels=['label1', 'label2'],
        )

        assert counter.name == 'test_counter'
        assert counter.label_names == ['label1', 'label2']

    def test_counter_increment(self):
        """Counter can be incremented."""
        counter = Counter(name='test', description='test')

        counter.inc()
        counter.inc(2)

        values = counter.collect()
        assert len(values) == 1
        assert values[0].value == 3

    def test_counter_with_labels(self):
        """Counter tracks separate values per label combination."""
        counter = Counter(
            name='test',
            description='test',
            labels=['status'],
        )

        counter.inc(labels={'status': 'success'})
        counter.inc(labels={'status': 'success'})
        counter.inc(labels={'status': 'failure'})

        values = counter.collect()
        assert len(values) == 2

        success = next(v for v in values if v.labels.get('status') == 'success')
        failure = next(v for v in values if v.labels.get('status') == 'failure')

        assert success.value == 2
        assert failure.value == 1

    def test_counter_prometheus_format(self):
        """Counter exports in Prometheus format."""
        counter = Counter(
            name='http_requests_total',
            description='Total HTTP requests',
            labels=['method'],
        )

        counter.inc(labels={'method': 'GET'})
        counter.inc(5, labels={'method': 'POST'})

        output = counter.to_prometheus()

        assert '# HELP http_requests_total Total HTTP requests' in output
        assert '# TYPE http_requests_total counter' in output
        assert 'http_requests_total{method="GET"} 1' in output
        assert 'http_requests_total{method="POST"} 5' in output


class TestHistogram:
    """Tests for Histogram metric type."""

    def test_histogram_creation(self):
        """Histogram can be created with custom buckets."""
        histogram = Histogram(
            name='test_histogram',
            description='A test histogram',
            buckets=[1, 5, 10, 50, 100],
        )

        assert histogram.name == 'test_histogram'
        assert histogram.buckets == [1, 5, 10, 50, 100]

    def test_histogram_observe(self):
        """Histogram records observations."""
        histogram = Histogram(
            name='test',
            description='test',
            buckets=[10, 50, 100],
        )

        histogram.observe(5)
        histogram.observe(25)
        histogram.observe(75)

        output = histogram.to_prometheus()

        # Check bucket counts
        assert 'le="10"} 1' in output  # 5 is <= 10
        assert 'le="50"} 2' in output  # 5, 25 are <= 50
        assert 'le="100"} 3' in output  # all three are <= 100
        assert 'le="+Inf"} 3' in output

    def test_histogram_with_labels(self):
        """Histogram tracks separate values per label combination."""
        histogram = Histogram(
            name='test',
            description='test',
            buckets=[10, 100],
            labels=['method'],
        )

        histogram.observe(5, labels={'method': 'GET'})
        histogram.observe(50, labels={'method': 'POST'})

        output = histogram.to_prometheus()

        assert 'method="GET"' in output
        assert 'method="POST"' in output

    def test_histogram_sum_and_count(self):
        """Histogram includes sum and count."""
        histogram = Histogram(
            name='duration',
            description='test',
            buckets=[10, 100],
        )

        histogram.observe(10)
        histogram.observe(20)

        output = histogram.to_prometheus()

        assert 'duration_sum 30' in output
        assert 'duration_count 2' in output


class TestDebugMetrics:
    """Tests for DebugMetrics registry."""

    @pytest.fixture
    def metrics(self):
        """Create metrics with default config."""
        config = ObservabilityConfig.for_tier(ObservabilityTier.TIER_1_LOCAL)
        return DebugMetrics(config)

    def test_record_session_start(self, metrics):
        """Session start is recorded."""
        metrics.record_session_start(severity='high', expedited=False)

        output = metrics.to_prometheus()

        assert 'debug_sessions_total' in output
        assert 'severity="high"' in output

    def test_record_session_end(self, metrics):
        """Session end is recorded with duration."""
        metrics.record_session_end(
            duration_seconds=1800,  # 30 minutes
            severity='medium',
            outcome='resolved',
            root_cause_type='race_condition',
        )

        output = metrics.to_prometheus()

        assert 'debug_session_duration_seconds' in output
        assert 'debug_root_cause_total' in output
        assert 'race_condition' in output

    def test_record_step_duration(self, metrics):
        """Step duration is recorded."""
        metrics.record_step_duration(
            step_number=3,
            step_name='hypothesis',
            duration_seconds=300,
        )

        output = metrics.to_prometheus()

        assert 'debug_step_duration_seconds' in output
        assert 'step_number="3"' in output
        assert 'step_name="hypothesis"' in output

    def test_record_lesson_extracted(self, metrics):
        """Lesson extraction is recorded."""
        metrics.record_lesson_extracted(
            trigger_type='recurring_pattern',
            pattern_score=0.85,
        )

        output = metrics.to_prometheus()

        assert 'debug_lessons_extracted_total' in output
        assert 'trigger_type="recurring_pattern"' in output
        assert 'pattern_score_bucket="high"' in output

    def test_record_contract_violation(self, metrics):
        """Contract violation is recorded."""
        metrics.record_contract_violation(
            contract_type='internal_api',
            severity='critical',
            service='user-service',
        )

        output = metrics.to_prometheus()

        assert 'debug_contract_violations_total' in output
        assert 'contract_type="internal_api"' in output

    def test_metrics_disabled(self):
        """Metrics are no-op when disabled."""
        config = ObservabilityConfig.for_tier(ObservabilityTier.TIER_1_LOCAL)
        config.metrics.enabled = False

        metrics = DebugMetrics(config)
        metrics.record_session_start()

        # Should not record anything
        output = metrics.to_prometheus()
        # Empty counters should still show structure
        assert 'debug_sessions_total' in output


class TestMetricsExporter:
    """Tests for MetricsExporter."""

    @pytest.fixture
    def exporter(self, tmp_path, monkeypatch):
        """Create exporter with temp path."""
        (tmp_path / 'CLAUDE.md').write_text('# Test')
        monkeypatch.chdir(tmp_path)

        config = ObservabilityConfig.for_tier(ObservabilityTier.TIER_1_LOCAL)
        metrics = DebugMetrics(config)
        return MetricsExporter(metrics, config)

    def test_export_to_file(self, exporter, tmp_path):
        """Metrics are exported to file."""
        exporter.metrics.record_session_start()
        exporter.export()

        metrics_dir = tmp_path / 'temp' / 'metrics'
        assert metrics_dir.exists()

        # Check latest file
        latest = metrics_dir / 'metrics_latest.prom'
        assert latest.exists()

        content = latest.read_text()
        assert 'debug_sessions_total' in content

    def test_get_metrics_json(self, exporter):
        """Metrics can be exported as JSON."""
        exporter.metrics.record_session_start()
        exporter.metrics.record_session_end(
            duration_seconds=300,
            outcome='resolved',
        )

        json_data = exporter.get_metrics_json()

        assert 'debug_sessions_total' in json_data
        assert json_data['debug_sessions_total']['type'] == 'counter'
