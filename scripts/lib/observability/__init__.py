"""Observability module for Debug Protocol integration.

Provides tracing, metrics, and structured logging for debug sessions.

Part of Wave 3 P2: Integration Completion (WAVE3-025)
"""

from scripts.lib.observability.config import ObservabilityConfig, ObservabilityTier
from scripts.lib.observability.hooks import DebugPhase, ObservabilityHook, ObservabilityHookManager
from scripts.lib.observability.logger import StructuredLogger, get_logger
from scripts.lib.observability.metrics import DebugMetrics, MetricsExporter
from scripts.lib.observability.tracing import DebugTracer, SpanContext

__all__ = [
    # Config
    'ObservabilityConfig',
    'ObservabilityTier',
    # Hooks
    'DebugPhase',
    'ObservabilityHook',
    'ObservabilityHookManager',
    # Logger
    'StructuredLogger',
    'get_logger',
    # Metrics
    'DebugMetrics',
    'MetricsExporter',
    # Tracing
    'DebugTracer',
    'SpanContext',
]
