"""Observability hook system for Debug Protocol.

Implements the hook architecture defined in OBSERVABILITY_INTEGRATION.md (WAVE3-013)
for PRE/DURING/POST debug phases.

Part of Wave 3 P2: Integration Completion (WAVE3-025)
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

from scripts.lib.observability.config import ObservabilityConfig, ObservabilityTier
from scripts.lib.observability.logger import StructuredLogger, get_logger
from scripts.lib.observability.metrics import DebugMetrics, MetricsExporter
from scripts.lib.observability.tracing import DebugTracer, SpanContext


class DebugPhase(Enum):
    """Debug session phases for hook execution.

    From OBSERVABILITY_INTEGRATION.md:
    - PRE_DEBUG: Session initialization, tracer setup
    - DURING_DEBUG: Step tracking, hypothesis logging
    - POST_DEBUG: Metrics emission, lesson extraction
    """

    PRE_DEBUG = 'pre_debug'
    DURING_DEBUG = 'during_debug'
    POST_DEBUG = 'post_debug'


@dataclass
class ObservabilityHook:
    """A hook to be executed during a debug phase.

    Attributes:
        phase: When to execute (PRE/DURING/POST)
        name: Human-readable hook name
        callback: Function to execute
        priority: Execution order (lower = earlier)
        enabled: Whether hook is active
    """

    phase: DebugPhase
    name: str
    callback: Callable[..., Any]
    priority: int = 100
    enabled: bool = True

    def __lt__(self, other: 'ObservabilityHook') -> bool:
        """Allow sorting by priority."""
        return self.priority < other.priority


@dataclass
class HookContext:
    """Context passed to hooks during execution.

    Provides access to all observability components.
    """

    tracer: DebugTracer
    metrics: DebugMetrics
    logger: StructuredLogger
    config: ObservabilityConfig

    # Session state
    session_id: Optional[str] = None
    trace_context: Optional[SpanContext] = None
    current_step: Optional[int] = None
    step_start_time: Optional[float] = None

    # Session data
    bug_description: Optional[str] = None
    severity: str = 'medium'
    expedited: bool = False

    # Results
    root_cause: Optional[str] = None
    outcome: str = 'in_progress'
    duration_minutes: Optional[int] = None


class ObservabilityHookManager:
    """Manages observability hooks for debug sessions.

    Orchestrates tracing, metrics, and logging across the debug lifecycle.
    """

    def __init__(self, config: Optional[ObservabilityConfig] = None):
        """Initialize hook manager with configuration.

        Args:
            config: Observability configuration
        """
        self.config = config or ObservabilityConfig.for_tier(ObservabilityTier.TIER_1_LOCAL)

        # Initialize observability components
        self.tracer = DebugTracer(self.config)
        self.metrics = DebugMetrics(self.config)
        self.metrics_exporter = MetricsExporter(self.metrics, self.config)
        self.logger = get_logger(config=self.config)

        # Hook registry by phase
        self._hooks: dict[DebugPhase, list[ObservabilityHook]] = {
            DebugPhase.PRE_DEBUG: [],
            DebugPhase.DURING_DEBUG: [],
            DebugPhase.POST_DEBUG: [],
        }

        # Current context
        self._context: Optional[HookContext] = None

        # Register default hooks
        self._register_default_hooks()

    def _register_default_hooks(self) -> None:
        """Register built-in observability hooks."""
        # PRE_DEBUG hooks
        self.register_hook(
            ObservabilityHook(
                phase=DebugPhase.PRE_DEBUG,
                name='initialize_tracer',
                callback=self._hook_init_tracer,
                priority=10,
            )
        )
        self.register_hook(
            ObservabilityHook(
                phase=DebugPhase.PRE_DEBUG,
                name='setup_correlation',
                callback=self._hook_setup_correlation,
                priority=20,
            )
        )
        self.register_hook(
            ObservabilityHook(
                phase=DebugPhase.PRE_DEBUG,
                name='record_session_start',
                callback=self._hook_record_session_start,
                priority=30,
            )
        )

        # POST_DEBUG hooks
        self.register_hook(
            ObservabilityHook(
                phase=DebugPhase.POST_DEBUG,
                name='record_session_end',
                callback=self._hook_record_session_end,
                priority=10,
            )
        )
        self.register_hook(
            ObservabilityHook(
                phase=DebugPhase.POST_DEBUG,
                name='export_metrics',
                callback=self._hook_export_metrics,
                priority=90,
            )
        )
        self.register_hook(
            ObservabilityHook(
                phase=DebugPhase.POST_DEBUG,
                name='clear_correlation',
                callback=self._hook_clear_correlation,
                priority=100,
            )
        )

    def register_hook(self, hook: ObservabilityHook) -> None:
        """Register a hook for a debug phase.

        Args:
            hook: The hook to register
        """
        self._hooks[hook.phase].append(hook)
        self._hooks[hook.phase].sort()  # Maintain priority order

    def unregister_hook(self, phase: DebugPhase, name: str) -> bool:
        """Unregister a hook by name.

        Args:
            phase: The phase to search in
            name: Hook name to remove

        Returns:
            True if hook was found and removed
        """
        hooks = self._hooks[phase]
        for i, hook in enumerate(hooks):
            if hook.name == name:
                hooks.pop(i)
                return True
        return False

    def execute_hooks(self, phase: DebugPhase, **kwargs: Any) -> None:
        """Execute all hooks for a phase.

        Args:
            phase: The phase to execute
            **kwargs: Additional arguments passed to hooks
        """
        for hook in self._hooks[phase]:
            if not hook.enabled:
                continue

            try:
                hook.callback(self._context, **kwargs)
            except Exception as e:
                # Log but don't fail - observability should not break the application
                if self._context:
                    self._context.logger.error(
                        f'Hook {hook.name} failed: {e}',
                        exc_info=True,
                    )

    # Session lifecycle methods

    def start_session(
        self,
        session_id: str,
        bug_description: str,
        severity: str = 'medium',
        expedited: bool = False,
        bug_id: Optional[str] = None,
    ) -> HookContext:
        """Start observability for a debug session.

        Args:
            session_id: Unique session identifier
            bug_description: Description of the bug
            severity: Bug severity (high/medium/low)
            expedited: Whether using expedited path
            bug_id: Optional bug tracker reference

        Returns:
            HookContext for the session
        """
        # Create context
        self._context = HookContext(
            tracer=self.tracer,
            metrics=self.metrics,
            logger=self.logger,
            config=self.config,
            session_id=session_id,
            bug_description=bug_description,
            severity=severity,
            expedited=expedited,
        )

        # Execute PRE_DEBUG hooks
        self.execute_hooks(DebugPhase.PRE_DEBUG, bug_id=bug_id)

        return self._context

    def start_step(
        self,
        step_number: int,
        step_name: str,
    ) -> Optional[SpanContext]:
        """Start observability for a protocol step.

        Args:
            step_number: Step number (1-7)
            step_name: Human-readable step name

        Returns:
            SpanContext for the step
        """
        if self._context is None:
            return None

        self._context.current_step = step_number
        self._context.step_start_time = time.time()

        # Start step span
        step_context = self.tracer.start_step_span(
            step_number=step_number,
            step_name=step_name,
            parent_context=self._context.trace_context,
        )

        # Log step start
        self.logger.step_started(
            session_id=self._context.session_id or 'unknown',
            step_number=step_number,
            step_name=step_name,
        )

        return step_context

    def end_step(
        self,
        step_context: SpanContext,
        findings: Optional[str] = None,
        evidence: Optional[str] = None,
    ) -> None:
        """End observability for a protocol step.

        Args:
            step_context: The step's span context
            findings: What was discovered
            evidence: Optional evidence path
        """
        if self._context is None:
            return

        # Calculate duration
        duration = 0.0
        if self._context.step_start_time:
            duration = time.time() - self._context.step_start_time

        # End step span
        self.tracer.end_step_span(
            context=step_context,
            findings=findings,
            evidence=evidence,
        )

        # Record step metrics
        step_number = self._context.current_step or 0
        step_names = {
            1: 'reproduce',
            2: 'blast_radius',
            3: 'hypothesis',
            4: 'root_cause',
            5: 'fix',
            6: 'validate',
            7: 'document',
        }
        step_name = step_names.get(step_number, f'step_{step_number}')

        self.metrics.record_step_duration(
            step_number=step_number,
            step_name=step_name,
            duration_seconds=duration,
        )

        # Log step completion
        self.logger.step_completed(
            session_id=self._context.session_id or 'unknown',
            step_number=step_number,
            step_name=step_name,
            duration_seconds=duration,
        )

        self._context.current_step = None
        self._context.step_start_time = None

    def log_hypothesis(
        self,
        hypothesis: str,
        evidence_count: int = 0,
    ) -> None:
        """Log a hypothesis during debugging.

        Args:
            hypothesis: The hypothesis formed
            evidence_count: Number of evidence pieces
        """
        if self._context is None:
            return

        self.logger.hypothesis_formed(
            session_id=self._context.session_id or 'unknown',
            hypothesis=hypothesis,
            evidence_count=evidence_count,
        )

    def log_hypothesis_result(
        self,
        hypothesis: str,
        validated: bool,
    ) -> None:
        """Log hypothesis validation result.

        Args:
            hypothesis: The hypothesis tested
            validated: Whether it was confirmed
        """
        if self._context is None:
            return

        self.logger.hypothesis_validated(
            session_id=self._context.session_id or 'unknown',
            hypothesis=hypothesis,
            validated=validated,
        )

    def end_session(
        self,
        root_cause: Optional[str] = None,
        outcome: str = 'resolved',
        duration_minutes: Optional[int] = None,
        lesson_extracted: bool = False,
        root_cause_category: Optional[str] = None,
    ) -> None:
        """End observability for a debug session.

        Args:
            root_cause: Identified root cause
            outcome: Session outcome (resolved/escalated/inconclusive)
            duration_minutes: Session duration
            lesson_extracted: Whether a pattern was added to LESSONS.md
            root_cause_category: Category of root cause
        """
        if self._context is None:
            return

        # Update context with results
        self._context.root_cause = root_cause
        self._context.outcome = outcome
        self._context.duration_minutes = duration_minutes

        # Execute POST_DEBUG hooks
        self.execute_hooks(
            DebugPhase.POST_DEBUG,
            lesson_extracted=lesson_extracted,
            root_cause_category=root_cause_category,
        )

        self._context = None

    # Default hook implementations

    def _hook_init_tracer(self, ctx: HookContext, **kwargs: Any) -> None:
        """Initialize tracing for the session."""
        bug_id = kwargs.get('bug_id')
        trace_context = ctx.tracer.start_session_span(
            session_id=ctx.session_id or 'unknown',
            bug_id=bug_id,
            severity=ctx.severity,
            expedited=ctx.expedited,
        )
        ctx.trace_context = trace_context

    def _hook_setup_correlation(self, ctx: HookContext, **kwargs: Any) -> None:
        """Set up correlation IDs for logging."""
        trace_id = ctx.tracer.get_current_trace_id()
        span_id = ctx.tracer.get_current_span_id()
        ctx.logger.set_correlation_ids(
            trace_id=trace_id,
            span_id=span_id,
            session_id=ctx.session_id,
        )

    def _hook_record_session_start(self, ctx: HookContext, **kwargs: Any) -> None:
        """Record session start metrics and logs."""
        ctx.metrics.record_session_start(
            severity=ctx.severity,
            expedited=ctx.expedited,
        )
        ctx.logger.session_started(
            session_id=ctx.session_id or 'unknown',
            bug_description=ctx.bug_description or 'No description',
            severity=ctx.severity,
        )

    def _hook_record_session_end(self, ctx: HookContext, **kwargs: Any) -> None:
        """Record session end metrics and logs."""
        lesson_extracted = kwargs.get('lesson_extracted', False)
        root_cause_category = kwargs.get('root_cause_category')

        # Record metrics
        duration_seconds = (ctx.duration_minutes or 0) * 60
        ctx.metrics.record_session_end(
            duration_seconds=duration_seconds,
            severity=ctx.severity,
            outcome=ctx.outcome,
            root_cause_type=root_cause_category,
        )

        # End trace span
        if ctx.trace_context:
            ctx.tracer.end_session_span(
                context=ctx.trace_context,
                root_cause=ctx.root_cause,
                outcome=ctx.outcome,
                lesson_extracted=lesson_extracted,
            )

        # Log completion
        ctx.logger.session_completed(
            session_id=ctx.session_id or 'unknown',
            outcome=ctx.outcome,
            duration_minutes=ctx.duration_minutes or 0,
            lesson_extracted=lesson_extracted,
        )

        if ctx.root_cause and root_cause_category:
            ctx.logger.root_cause_identified(
                session_id=ctx.session_id or 'unknown',
                root_cause=ctx.root_cause,
                category=root_cause_category,
            )

    def _hook_export_metrics(self, ctx: HookContext, **kwargs: Any) -> None:
        """Export metrics to configured backend."""
        self.metrics_exporter.export()

    def _hook_clear_correlation(self, ctx: HookContext, **kwargs: Any) -> None:
        """Clear correlation IDs after session."""
        ctx.logger.clear_correlation_ids()

    # Utility methods

    def get_context(self) -> Optional[HookContext]:
        """Get the current hook context."""
        return self._context

    def get_trace_id(self) -> Optional[str]:
        """Get current trace ID for external correlation."""
        return self.tracer.get_current_trace_id()

    def get_span_id(self) -> Optional[str]:
        """Get current span ID for external correlation."""
        return self.tracer.get_current_span_id()
