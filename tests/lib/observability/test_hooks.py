"""Tests for observability hooks module.

Part of Wave 3 P2: Integration Completion (WAVE3-025)
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib.observability.config import ObservabilityConfig, ObservabilityTier
from scripts.lib.observability.hooks import (
    DebugPhase,
    HookContext,
    ObservabilityHook,
    ObservabilityHookManager,
)


class TestDebugPhase:
    """Tests for DebugPhase enum."""

    def test_phase_values(self):
        """All phases have correct values."""
        assert DebugPhase.PRE_DEBUG.value == 'pre_debug'
        assert DebugPhase.DURING_DEBUG.value == 'during_debug'
        assert DebugPhase.POST_DEBUG.value == 'post_debug'


class TestObservabilityHook:
    """Tests for ObservabilityHook dataclass."""

    def test_hook_creation(self):
        """Hook can be created with required fields."""
        hook = ObservabilityHook(
            phase=DebugPhase.PRE_DEBUG,
            name='test_hook',
            callback=lambda ctx: None,
        )

        assert hook.phase == DebugPhase.PRE_DEBUG
        assert hook.name == 'test_hook'
        assert hook.priority == 100
        assert hook.enabled

    def test_hook_sorting_by_priority(self):
        """Hooks sort by priority."""
        hooks = [
            ObservabilityHook(
                phase=DebugPhase.PRE_DEBUG, name='low', callback=lambda: None, priority=100
            ),
            ObservabilityHook(
                phase=DebugPhase.PRE_DEBUG, name='high', callback=lambda: None, priority=10
            ),
            ObservabilityHook(
                phase=DebugPhase.PRE_DEBUG, name='medium', callback=lambda: None, priority=50
            ),
        ]

        sorted_hooks = sorted(hooks)

        assert sorted_hooks[0].name == 'high'
        assert sorted_hooks[1].name == 'medium'
        assert sorted_hooks[2].name == 'low'


class TestObservabilityHookManager:
    """Tests for ObservabilityHookManager."""

    @pytest.fixture
    def manager(self, tmp_path, monkeypatch):
        """Create manager with temp paths."""
        (tmp_path / 'CLAUDE.md').write_text('# Test')
        (tmp_path / 'temp').mkdir()
        monkeypatch.chdir(tmp_path)

        config = ObservabilityConfig.for_tier(ObservabilityTier.TIER_1_LOCAL)
        return ObservabilityHookManager(config)

    def test_default_hooks_registered(self, manager):
        """Default hooks are registered on creation."""
        # Check PRE_DEBUG hooks
        pre_hooks = [h.name for h in manager._hooks[DebugPhase.PRE_DEBUG]]
        assert 'initialize_tracer' in pre_hooks
        assert 'setup_correlation' in pre_hooks

        # Check POST_DEBUG hooks
        post_hooks = [h.name for h in manager._hooks[DebugPhase.POST_DEBUG]]
        assert 'record_session_end' in post_hooks
        assert 'export_metrics' in post_hooks

    def test_register_custom_hook(self, manager):
        """Custom hooks can be registered."""
        call_log = []

        hook = ObservabilityHook(
            phase=DebugPhase.DURING_DEBUG,
            name='custom_hook',
            callback=lambda ctx, **kwargs: call_log.append('called'),
        )

        manager.register_hook(hook)

        assert any(h.name == 'custom_hook' for h in manager._hooks[DebugPhase.DURING_DEBUG])

    def test_unregister_hook(self, manager):
        """Hooks can be unregistered."""
        result = manager.unregister_hook(DebugPhase.PRE_DEBUG, 'initialize_tracer')

        assert result is True
        assert not any(h.name == 'initialize_tracer' for h in manager._hooks[DebugPhase.PRE_DEBUG])

    def test_unregister_missing_hook(self, manager):
        """Unregistering missing hook returns False."""
        result = manager.unregister_hook(DebugPhase.PRE_DEBUG, 'nonexistent')
        assert result is False

    def test_start_session(self, manager):
        """Start session creates context and executes PRE hooks."""
        ctx = manager.start_session(
            session_id='DBG-2026-02-05-001',
            bug_description='Test bug',
            severity='high',
        )

        assert ctx is not None
        assert ctx.session_id == 'DBG-2026-02-05-001'
        assert ctx.severity == 'high'
        assert ctx.trace_context is not None  # Set by init_tracer hook

    def test_start_step(self, manager):
        """Start step creates span and logs."""
        manager.start_session(
            session_id='DBG-2026-02-05-001',
            bug_description='Test bug',
        )

        step_ctx = manager.start_step(step_number=1, step_name='reproduce')

        assert step_ctx is not None
        assert manager._context.current_step == 1

    def test_end_step_records_metrics(self, manager):
        """End step records duration metrics."""
        manager.start_session(
            session_id='DBG-2026-02-05-001',
            bug_description='Test bug',
        )

        step_ctx = manager.start_step(step_number=1, step_name='reproduce')
        manager.end_step(step_ctx, findings='Bug reproduced')

        # Step context should be cleared
        assert manager._context.current_step is None

    def test_log_hypothesis(self, manager):
        """Hypothesis can be logged."""
        manager.start_session(
            session_id='DBG-2026-02-05-001',
            bug_description='Test bug',
        )

        # Should not raise
        manager.log_hypothesis('Memory leak due to unclosed connection', evidence_count=3)

    def test_end_session_exports(self, manager):
        """End session runs POST hooks and exports."""
        manager.start_session(
            session_id='DBG-2026-02-05-001',
            bug_description='Test bug',
        )

        manager.end_session(
            root_cause='Test cause',
            outcome='resolved',
            duration_minutes=45,
        )

        # Context should be cleared
        assert manager._context is None

    def test_hook_error_handling(self, manager):
        """Hook errors are caught and logged."""
        failing_hook = ObservabilityHook(
            phase=DebugPhase.PRE_DEBUG,
            name='failing_hook',
            callback=lambda ctx, **kwargs: 1 / 0,  # Division by zero
            priority=1000,  # Run last
        )

        manager.register_hook(failing_hook)

        # Should not raise
        ctx = manager.start_session(
            session_id='test',
            bug_description='test',
        )

        # Session should still work
        assert ctx is not None

    def test_disabled_hook(self, manager):
        """Disabled hooks are not executed."""
        call_log = []

        hook = ObservabilityHook(
            phase=DebugPhase.PRE_DEBUG,
            name='disabled_hook',
            callback=lambda ctx, **kwargs: call_log.append('called'),
            enabled=False,
        )

        manager.register_hook(hook)
        manager.start_session(session_id='test', bug_description='test')

        assert 'called' not in call_log

    def test_get_trace_id(self, manager):
        """Current trace ID is accessible."""
        manager.start_session(
            session_id='test',
            bug_description='test',
        )

        trace_id = manager.get_trace_id()
        assert trace_id is not None
        assert len(trace_id) == 32


class TestHookContext:
    """Tests for HookContext dataclass."""

    def test_context_defaults(self):
        """Context has sensible defaults."""
        from scripts.lib.observability.logger import StructuredLogger
        from scripts.lib.observability.metrics import DebugMetrics
        from scripts.lib.observability.tracing import DebugTracer

        config = ObservabilityConfig.for_tier(ObservabilityTier.TIER_1_LOCAL)

        ctx = HookContext(
            tracer=DebugTracer(config),
            metrics=DebugMetrics(config),
            logger=StructuredLogger(),
            config=config,
        )

        assert ctx.session_id is None
        assert ctx.severity == 'medium'
        assert ctx.expedited is False
        assert ctx.outcome == 'in_progress'
