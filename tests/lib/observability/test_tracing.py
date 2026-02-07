"""Tests for observability tracing module.

Part of Wave 3 P2: Integration Completion (WAVE3-025)
"""

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib.observability.config import ObservabilityConfig, ObservabilityTier
from scripts.lib.observability.tracing import DebugTracer, Span, SpanContext


class TestSpanContext:
    """Tests for SpanContext dataclass."""

    def test_new_root_creates_valid_ids(self):
        """Root context has valid trace and span IDs."""
        ctx = SpanContext.new_root()

        assert len(ctx.trace_id) == 32
        assert len(ctx.span_id) == 16
        assert ctx.parent_span_id is None

    def test_child_preserves_trace_id(self):
        """Child context preserves trace ID."""
        parent = SpanContext.new_root()
        child = parent.child()

        assert child.trace_id == parent.trace_id
        assert child.span_id != parent.span_id
        assert child.parent_span_id == parent.span_id

    def test_unique_span_ids(self):
        """Each span gets a unique ID."""
        parent = SpanContext.new_root()
        children = [parent.child() for _ in range(10)]

        span_ids = [c.span_id for c in children]
        assert len(set(span_ids)) == 10  # All unique


class TestSpan:
    """Tests for Span dataclass."""

    def test_span_creation(self):
        """Span can be created with required fields."""
        ctx = SpanContext.new_root()
        span = Span(name='test_span', context=ctx)

        assert span.name == 'test_span'
        assert span.status == 'OK'
        assert span.end_time is None

    def test_set_attribute(self):
        """Attributes can be set on span."""
        ctx = SpanContext.new_root()
        span = Span(name='test', context=ctx)

        span.set_attribute('key1', 'value1')
        span.set_attribute('key2', 42)

        assert span.attributes['key1'] == 'value1'
        assert span.attributes['key2'] == 42

    def test_add_event(self):
        """Events can be added to span."""
        ctx = SpanContext.new_root()
        span = Span(name='test', context=ctx)

        span.add_event('event1', {'detail': 'value'})

        assert len(span.events) == 1
        assert span.events[0]['name'] == 'event1'
        assert span.events[0]['attributes']['detail'] == 'value'

    def test_set_error(self):
        """Error can be set on span."""
        ctx = SpanContext.new_root()
        span = Span(name='test', context=ctx)

        span.set_error(ValueError('test error'))

        assert span.status == 'ERROR'
        assert span.attributes['error.type'] == 'ValueError'
        assert span.attributes['error.message'] == 'test error'

    def test_duration_calculation(self):
        """Duration is calculated correctly."""
        ctx = SpanContext.new_root()
        span = Span(name='test', context=ctx, start_time=100.0)
        span.end_time = 100.5

        assert span.duration_ms == 500.0

    def test_to_dict_format(self):
        """Span converts to Jaeger-compatible dict."""
        ctx = SpanContext.new_root()
        span = Span(name='test', context=ctx, start_time=100.0)
        span.set_attribute('key', 'value')
        span.end_time = 100.1

        result = span.to_dict()

        assert result['traceID'] == ctx.trace_id
        assert result['spanID'] == ctx.span_id
        assert result['operationName'] == 'test'
        assert any(t['key'] == 'key' and t['value'] == 'value' for t in result['tags'])


class TestDebugTracer:
    """Tests for DebugTracer class."""

    @pytest.fixture
    def tracer(self, tmp_path, monkeypatch):
        """Create tracer with temp export path."""
        # Set up project root detection
        (tmp_path / 'CLAUDE.md').write_text('# Test')
        (tmp_path / 'temp').mkdir()
        monkeypatch.chdir(tmp_path)

        config = ObservabilityConfig.for_tier(ObservabilityTier.TIER_1_LOCAL)
        return DebugTracer(config)

    def test_start_session_span(self, tracer):
        """Session span can be started."""
        ctx = tracer.start_session_span(
            session_id='DBG-2026-02-05-001',
            severity='high',
            expedited=False,
        )

        assert ctx.trace_id is not None
        assert tracer.get_current_trace_id() == ctx.trace_id

    def test_start_step_span(self, tracer):
        """Step span can be started under session."""
        session_ctx = tracer.start_session_span(
            session_id='DBG-2026-02-05-001',
        )

        step_ctx = tracer.start_step_span(
            step_number=1,
            step_name='reproduce',
        )

        assert step_ctx.trace_id == session_ctx.trace_id
        assert step_ctx.parent_span_id == session_ctx.span_id

    def test_span_context_manager(self, tracer):
        """Span context manager works correctly."""
        tracer.start_session_span(session_id='test')

        with tracer.span('custom_operation', attributes={'key': 'value'}) as span:
            span.add_event('mid_operation')
            assert tracer.get_current_span_id() == span.context.span_id

        # Span should be ended
        assert span.end_time is not None

    def test_span_error_handling(self, tracer):
        """Span captures errors from context manager."""
        tracer.start_session_span(session_id='test')

        with pytest.raises(ValueError):
            with tracer.span('failing_operation') as span:
                raise ValueError('test error')

        assert span.status == 'ERROR'
        assert span.attributes['error.type'] == 'ValueError'

    def test_end_session_exports(self, tracer, tmp_path):
        """Ending session exports traces."""
        ctx = tracer.start_session_span(
            session_id='DBG-2026-02-05-001',
        )
        tracer.start_step_span(1, 'reproduce')

        tracer.end_session_span(
            context=ctx,
            root_cause='test cause',
            outcome='resolved',
        )

        # Check that trace file was created
        traces_dir = tmp_path / 'temp' / 'traces'
        trace_files = list(traces_dir.glob('trace_*.json'))
        assert len(trace_files) == 1

        # Verify content
        content = json.loads(trace_files[0].read_text())
        assert 'data' in content
        assert len(content['data'][0]['spans']) > 0

    def test_sampling_rate(self, tmp_path, monkeypatch):
        """Sampling rate affects trace collection."""
        (tmp_path / 'CLAUDE.md').write_text('# Test')
        monkeypatch.chdir(tmp_path)

        config = ObservabilityConfig.for_tier(ObservabilityTier.TIER_1_LOCAL)
        config.tracing.sampling_rate = 0.0  # Sample nothing

        tracer = DebugTracer(config)
        ctx = tracer.start_session_span(session_id='test')

        # Span should still return a context, but nothing recorded
        assert ctx is not None

    def test_span_naming_convention(self, tracer):
        """Spans follow naming convention from WAVE3-013."""
        tracer.start_session_span(session_id='test')

        # Check that span names are prefixed correctly
        for span in tracer._spans:
            assert span.name.startswith('vibe-code-debug/')


class TestTracerDisabled:
    """Tests for tracer when tracing is disabled."""

    def test_disabled_tracing_no_ops(self, tmp_path, monkeypatch):
        """Disabled tracing doesn't break functionality."""
        (tmp_path / 'CLAUDE.md').write_text('# Test')
        monkeypatch.chdir(tmp_path)

        config = ObservabilityConfig.for_tier(ObservabilityTier.TIER_1_LOCAL)
        config.tracing.enabled = False

        tracer = DebugTracer(config)

        # Should return valid contexts without recording
        ctx = tracer.start_session_span(session_id='test')
        assert ctx is not None

        with tracer.span('test') as span:
            span.set_attribute('key', 'value')

        # No spans should be recorded
        assert len(tracer._spans) == 0
