"""Distributed tracing for Debug Protocol.

Implements Jaeger span emission following the span naming conventions
defined in OBSERVABILITY_INTEGRATION.md (WAVE3-013).

Part of Wave 3 P2: Integration Completion (WAVE3-025)
"""

import json
import random
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Generator, Optional

from scripts.lib.observability.config import ObservabilityConfig, ObservabilityTier


def _generate_trace_id() -> str:
    """Generate a 32-character hex trace ID."""
    return f'{random.getrandbits(128):032x}'


def _generate_span_id() -> str:
    """Generate a 16-character hex span ID."""
    return f'{random.getrandbits(64):016x}'


@dataclass
class SpanContext:
    """Context for distributed tracing.

    Contains IDs needed to correlate spans across services.
    """

    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None

    @classmethod
    def new_root(cls) -> 'SpanContext':
        """Create a new root span context."""
        return cls(
            trace_id=_generate_trace_id(),
            span_id=_generate_span_id(),
        )

    def child(self) -> 'SpanContext':
        """Create a child span context."""
        return SpanContext(
            trace_id=self.trace_id,
            span_id=_generate_span_id(),
            parent_span_id=self.span_id,
        )


@dataclass
class Span:
    """A single trace span representing a debug operation.

    Follows Jaeger span conventions with attributes defined in WAVE3-013.
    """

    name: str
    context: SpanContext
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    attributes: dict[str, Any] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)
    status: str = 'OK'  # OK, ERROR, UNSET

    def set_attribute(self, key: str, value: Any) -> None:
        """Set a span attribute."""
        self.attributes[key] = value

    def add_event(self, name: str, attributes: Optional[dict[str, Any]] = None) -> None:
        """Add an event to the span."""
        self.events.append({
            'name': name,
            'timestamp': time.time(),
            'attributes': attributes or {},
        })

    def set_error(self, error: Exception) -> None:
        """Mark span as errored."""
        self.status = 'ERROR'
        self.set_attribute('error.type', type(error).__name__)
        self.set_attribute('error.message', str(error))

    def end(self) -> None:
        """End the span."""
        self.end_time = time.time()

    @property
    def duration_ms(self) -> float:
        """Calculate span duration in milliseconds."""
        if self.end_time is None:
            return (time.time() - self.start_time) * 1000
        return (self.end_time - self.start_time) * 1000

    def to_dict(self) -> dict[str, Any]:
        """Convert span to dictionary for export."""
        return {
            'traceID': self.context.trace_id,
            'spanID': self.context.span_id,
            'parentSpanID': self.context.parent_span_id,
            'operationName': self.name,
            'startTime': int(self.start_time * 1_000_000),  # Jaeger uses microseconds
            'duration': int(self.duration_ms * 1000),  # microseconds
            'tags': [
                {'key': k, 'type': _get_tag_type(v), 'value': v}
                for k, v in self.attributes.items()
            ],
            'logs': [
                {
                    'timestamp': int(e['timestamp'] * 1_000_000),
                    'fields': [
                        {'key': 'event', 'type': 'string', 'value': e['name']},
                        *[
                            {'key': k, 'type': _get_tag_type(v), 'value': v}
                            for k, v in e['attributes'].items()
                        ],
                    ],
                }
                for e in self.events
            ],
            'processID': 'p1',
            'warnings': [] if self.status == 'OK' else ['error'],
        }


def _get_tag_type(value: Any) -> str:
    """Get Jaeger tag type for a value."""
    if isinstance(value, bool):
        return 'bool'
    elif isinstance(value, int | float):
        return 'float64'
    return 'string'


class DebugTracer:
    """Tracer for debug sessions following Jaeger conventions.

    Span naming convention: vibe-code-debug/debug_{operation}
    """

    SERVICE_NAME = 'vibe-code-debug'
    SPAN_PREFIX = 'vibe-code-debug/'

    # Standard span names from WAVE3-013
    SPAN_NAMES = {
        'session': 'debug_session',
        'step_1': 'debug_step_1_reproduce',
        'step_2': 'debug_step_2_blast_radius',
        'step_3': 'debug_step_3_hypothesis',
        'step_4': 'debug_step_4_root_cause',
        'step_5': 'debug_step_5_fix',
        'step_6': 'debug_step_6_validate',
        'step_7': 'debug_step_7_document',
        'expedited': 'expedited_debug',
    }

    def __init__(self, config: Optional[ObservabilityConfig] = None):
        """Initialize tracer with configuration.

        Args:
            config: Observability configuration (uses defaults if not provided)
        """
        self.config = config or ObservabilityConfig.for_tier(ObservabilityTier.TIER_1_LOCAL)
        self._spans: list[Span] = []
        self._active_span: Optional[Span] = None
        self._root_context: Optional[SpanContext] = None
        self._export_path: Optional[Path] = None

        # Set up file export for Tier 1
        if self.config.tier == ObservabilityTier.TIER_1_LOCAL:
            self._setup_file_export()

    def _setup_file_export(self) -> None:
        """Set up file-based trace export for local development."""
        # Find project root
        for parent in [Path.cwd(), *Path.cwd().parents]:
            if (parent / 'CLAUDE.md').exists():
                traces_dir = parent / 'temp' / 'traces'
                traces_dir.mkdir(parents=True, exist_ok=True)
                self._export_path = traces_dir
                break

    def _should_sample(self) -> bool:
        """Determine if this trace should be sampled."""
        return random.random() < self.config.tracing.sampling_rate

    def start_session_span(
        self,
        session_id: str,
        bug_id: Optional[str] = None,
        severity: str = 'medium',
        expedited: bool = False,
    ) -> SpanContext:
        """Start the root span for a debug session.

        Args:
            session_id: Unique session identifier
            bug_id: Optional bug tracker reference
            severity: Bug severity (high/medium/low)
            expedited: Whether using expedited path

        Returns:
            SpanContext for the session
        """
        if not self.config.tracing.enabled or not self._should_sample():
            # Return a valid context but don't record
            return SpanContext.new_root()

        self._root_context = SpanContext.new_root()

        span_name = self.SPAN_NAMES['expedited'] if expedited else self.SPAN_NAMES['session']
        span = Span(
            name=f'{self.SPAN_PREFIX}{span_name}',
            context=self._root_context,
        )

        # Set required attributes from WAVE3-013
        span.set_attribute('debug.session_id', session_id)
        span.set_attribute('debug.severity', severity)
        span.set_attribute('debug.expedited', expedited)
        if bug_id:
            span.set_attribute('debug.bug_id', bug_id)

        self._spans.append(span)
        self._active_span = span

        return self._root_context

    def start_step_span(
        self,
        step_number: int,
        step_name: str,
        parent_context: Optional[SpanContext] = None,
    ) -> SpanContext:
        """Start a span for a protocol step.

        Args:
            step_number: Step number (1-7)
            step_name: Human-readable step name
            parent_context: Parent span context (uses root if not provided)

        Returns:
            SpanContext for the step
        """
        if not self.config.tracing.enabled:
            return SpanContext.new_root()

        parent = parent_context or self._root_context
        if parent is None:
            parent = SpanContext.new_root()

        context = parent.child()
        span_key = f'step_{step_number}'
        operation_name = self.SPAN_NAMES.get(span_key, f'debug_step_{step_number}')

        span = Span(
            name=f'{self.SPAN_PREFIX}{operation_name}',
            context=context,
        )

        span.set_attribute('debug.step.number', step_number)
        span.set_attribute('debug.step.name', step_name)

        self._spans.append(span)
        self._active_span = span

        return context

    @contextmanager
    def span(
        self,
        name: str,
        attributes: Optional[dict[str, Any]] = None,
        parent_context: Optional[SpanContext] = None,
    ) -> Generator[Span, None, None]:
        """Context manager for creating spans.

        Args:
            name: Span name (will be prefixed with service name)
            attributes: Initial attributes for the span
            parent_context: Parent span context

        Yields:
            The created span
        """
        if not self.config.tracing.enabled:
            # Return a dummy span that does nothing
            yield Span(name=name, context=SpanContext.new_root())
            return

        parent = parent_context or self._root_context
        if parent is None:
            parent = SpanContext.new_root()
            self._root_context = parent

        context = parent.child()
        span = Span(
            name=f'{self.SPAN_PREFIX}{name}',
            context=context,
        )

        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)

        self._spans.append(span)
        previous_active = self._active_span
        self._active_span = span

        try:
            yield span
        except Exception as e:
            span.set_error(e)
            raise
        finally:
            span.end()
            self._active_span = previous_active

    def end_step_span(
        self,
        context: SpanContext,
        findings: Optional[str] = None,
        evidence: Optional[str] = None,
    ) -> None:
        """End a step span with findings.

        Args:
            context: The span context to end
            findings: What was discovered
            evidence: Optional evidence path
        """
        span = self._find_span_by_context(context)
        if span:
            if findings:
                span.set_attribute('debug.findings', findings[:500])  # Truncate
            if evidence:
                span.set_attribute('debug.evidence', evidence)
            span.end()

    def end_session_span(
        self,
        context: SpanContext,
        root_cause: Optional[str] = None,
        outcome: str = 'resolved',
        lesson_extracted: bool = False,
    ) -> None:
        """End the session span with results.

        Args:
            context: The session span context
            root_cause: Identified root cause
            outcome: Session outcome
            lesson_extracted: Whether a pattern was added to LESSONS.md
        """
        span = self._find_span_by_context(context)
        if span:
            if root_cause:
                span.set_attribute('debug.root_cause', root_cause[:500])
            span.set_attribute('debug.outcome', outcome)
            span.set_attribute('debug.lesson_extracted', lesson_extracted)
            span.end()

        # Export all spans
        self._export_spans()

    def _find_span_by_context(self, context: SpanContext) -> Optional[Span]:
        """Find a span by its context."""
        for span in self._spans:
            if span.context.span_id == context.span_id:
                return span
        return None

    def _export_spans(self) -> None:
        """Export collected spans."""
        if not self._spans:
            return

        if self._export_path:
            self._export_to_file()
        elif self.config.tracing.jaeger_endpoint:
            self._export_to_jaeger()

        # Clear exported spans
        self._spans.clear()
        self._root_context = None

    def _export_to_file(self) -> None:
        """Export spans to a JSON file."""
        if self._export_path is None:
            return

        timestamp = datetime.now(UTC).strftime('%Y%m%d_%H%M%S')
        trace_id = self._root_context.trace_id[:8] if self._root_context else 'unknown'
        filename = f'trace_{timestamp}_{trace_id}.json'

        trace_data = {
            'data': [
                {
                    'traceID': self._root_context.trace_id if self._root_context else '',
                    'spans': [s.to_dict() for s in self._spans],
                    'processes': {
                        'p1': {
                            'serviceName': self.SERVICE_NAME,
                            'tags': [],
                        }
                    },
                    'warnings': None,
                }
            ],
            'total': 1,
            'limit': 0,
            'offset': 0,
            'errors': None,
        }

        filepath = self._export_path / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(trace_data, f, indent=2)

    def _export_to_jaeger(self) -> None:
        """Export spans to Jaeger via HTTP."""
        # Only attempt if we have an endpoint
        if not self.config.tracing.jaeger_endpoint:
            return

        try:
            import urllib.request

            trace_data = {
                'data': [
                    {
                        'traceID': self._root_context.trace_id if self._root_context else '',
                        'spans': [s.to_dict() for s in self._spans],
                        'processes': {
                            'p1': {
                                'serviceName': self.SERVICE_NAME,
                                'tags': [],
                            }
                        },
                    }
                ],
            }

            req = urllib.request.Request(
                self.config.tracing.jaeger_endpoint,
                data=json.dumps(trace_data).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST',
            )

            with urllib.request.urlopen(req, timeout=5) as response:
                response.read()  # Consume response

        except Exception:
            # Silently fail - observability should not break the application
            pass

    def get_current_trace_id(self) -> Optional[str]:
        """Get the current trace ID for correlation."""
        if self._root_context:
            return self._root_context.trace_id
        return None

    def get_current_span_id(self) -> Optional[str]:
        """Get the current span ID for correlation."""
        if self._active_span:
            return self._active_span.context.span_id
        return None
