"""Prometheus metrics for Debug Protocol.

Implements metrics defined in OBSERVABILITY_INTEGRATION.md (WAVE3-013):
- debug_sessions_total
- debug_session_duration_seconds
- debug_step_duration_seconds
- debug_root_cause_total
- debug_lessons_extracted_total

Part of Wave 3 P2: Integration Completion (WAVE3-025)
"""

import json
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Optional

from scripts.lib.observability.config import ObservabilityConfig, ObservabilityTier


@dataclass
class MetricValue:
    """A single metric observation with labels."""

    value: float
    labels: dict[str, str]
    timestamp: float = field(default_factory=time.time)


class Counter:
    """Prometheus-style counter metric."""

    def __init__(self, name: str, description: str, labels: Optional[list[str]] = None):
        self.name = name
        self.description = description
        self.label_names = labels or []
        self._values: dict[tuple, float] = defaultdict(float)

    def inc(self, amount: float = 1, labels: Optional[dict[str, str]] = None) -> None:
        """Increment counter by amount."""
        label_values = self._label_key(labels)
        self._values[label_values] += amount

    def _label_key(self, labels: Optional[dict[str, str]] = None) -> tuple:
        """Create a hashable key from labels."""
        if not labels:
            return ()
        return tuple(labels.get(name, '') for name in self.label_names)

    def collect(self) -> list[MetricValue]:
        """Collect all metric values."""
        results = []
        for label_values, value in self._values.items():
            labels = dict(zip(self.label_names, label_values))
            results.append(MetricValue(value=value, labels=labels))
        return results

    def to_prometheus(self) -> str:
        """Export in Prometheus exposition format."""
        lines = [
            f'# HELP {self.name} {self.description}',
            f'# TYPE {self.name} counter',
        ]
        for label_values, value in self._values.items():
            if label_values:
                labels = dict(zip(self.label_names, label_values))
                label_str = ','.join(f'{k}="{v}"' for k, v in labels.items())
                lines.append(f'{self.name}{{{label_str}}} {value}')
            else:
                lines.append(f'{self.name} {value}')
        return '\n'.join(lines)


class Histogram:
    """Prometheus-style histogram metric."""

    def __init__(
        self,
        name: str,
        description: str,
        buckets: Optional[list[float]] = None,
        labels: Optional[list[str]] = None,
    ):
        self.name = name
        self.description = description
        self.buckets = sorted(buckets or [10, 30, 60, 120, 300, 600, 1800, 3600])
        self.label_names = labels or []
        self._observations: dict[tuple, list[float]] = defaultdict(list)

    def observe(self, value: float, labels: Optional[dict[str, str]] = None) -> None:
        """Record an observation."""
        label_values = self._label_key(labels)
        self._observations[label_values].append(value)

    def _label_key(self, labels: Optional[dict[str, str]] = None) -> tuple:
        """Create a hashable key from labels."""
        if not labels:
            return ()
        return tuple(labels.get(name, '') for name in self.label_names)

    def to_prometheus(self) -> str:
        """Export in Prometheus exposition format."""
        lines = [
            f'# HELP {self.name} {self.description}',
            f'# TYPE {self.name} histogram',
        ]

        for label_values, observations in self._observations.items():
            labels = dict(zip(self.label_names, label_values))
            label_str = ','.join(f'{k}="{v}"' for k, v in labels.items()) if labels else ''

            # Bucket counts
            for bucket in self.buckets:
                count = sum(1 for o in observations if o <= bucket)
                if label_str:
                    lines.append(f'{self.name}_bucket{{{label_str},le="{bucket}"}} {count}')
                else:
                    lines.append(f'{self.name}_bucket{{le="{bucket}"}} {count}')

            # +Inf bucket
            if label_str:
                lines.append(f'{self.name}_bucket{{{label_str},le="+Inf"}} {len(observations)}')
            else:
                lines.append(f'{self.name}_bucket{{le="+Inf"}} {len(observations)}')

            # Sum and count
            total = sum(observations)
            count = len(observations)
            if label_str:
                lines.append(f'{self.name}_sum{{{label_str}}} {total}')
                lines.append(f'{self.name}_count{{{label_str}}} {count}')
            else:
                lines.append(f'{self.name}_sum {total}')
                lines.append(f'{self.name}_count {count}')

        return '\n'.join(lines)


class DebugMetrics:
    """Metrics registry for Debug Protocol.

    Provides all metrics defined in WAVE3-013 OBSERVABILITY_INTEGRATION.md.
    """

    def __init__(self, config: Optional[ObservabilityConfig] = None):
        """Initialize metrics registry.

        Args:
            config: Observability configuration
        """
        self.config = config or ObservabilityConfig.for_tier(ObservabilityTier.TIER_1_LOCAL)

        # Core metrics from WAVE3-013
        self.sessions_total = Counter(
            name='debug_sessions_total',
            description='Total debug sessions started',
            labels=['severity', 'outcome', 'expedited'],
        )

        self.session_duration = Histogram(
            name='debug_session_duration_seconds',
            description='Debug session duration',
            buckets=[60, 300, 900, 1800, 3600, 7200],  # 1m, 5m, 15m, 30m, 1h, 2h
            labels=['severity', 'outcome'],
        )

        self.step_duration = Histogram(
            name='debug_step_duration_seconds',
            description='Time spent per protocol step',
            buckets=[10, 30, 60, 120, 300, 600, 1800],  # 10s to 30m
            labels=['step_number', 'step_name'],
        )

        self.root_cause_total = Counter(
            name='debug_root_cause_total',
            description='Root causes identified by type',
            labels=['root_cause_type', 'severity'],
        )

        self.lessons_extracted = Counter(
            name='debug_lessons_extracted_total',
            description='Lessons extracted to LESSONS.md',
            labels=['trigger_type', 'pattern_score_bucket'],
        )

        # Additional operational metrics
        self.contract_violations = Counter(
            name='debug_contract_violations_total',
            description='API contract violations detected',
            labels=['contract_type', 'severity', 'service'],
        )

        self.expedited_path_usage = Counter(
            name='debug_expedited_path_total',
            description='Expedited vs full path usage',
            labels=['path_type', 'disqualifier'],
        )

        self._all_metrics = [
            self.sessions_total,
            self.session_duration,
            self.step_duration,
            self.root_cause_total,
            self.lessons_extracted,
            self.contract_violations,
            self.expedited_path_usage,
        ]

    def record_session_start(
        self,
        severity: str = 'medium',
        expedited: bool = False,
    ) -> None:
        """Record a session start.

        Args:
            severity: Bug severity (high/medium/low)
            expedited: Whether using expedited path
        """
        if not self.config.metrics.enabled:
            return

        self.sessions_total.inc(
            labels={
                'severity': severity,
                'outcome': 'in_progress',
                'expedited': str(expedited).lower(),
            }
        )

        path_type = 'expedited' if expedited else 'full'
        self.expedited_path_usage.inc(labels={'path_type': path_type, 'disqualifier': 'none'})

    def record_session_end(
        self,
        duration_seconds: float,
        severity: str = 'medium',
        outcome: str = 'resolved',
        root_cause_type: Optional[str] = None,
    ) -> None:
        """Record session completion.

        Args:
            duration_seconds: How long the session took
            severity: Bug severity
            outcome: Session outcome (resolved/escalated/inconclusive)
            root_cause_type: Category of root cause found
        """
        if not self.config.metrics.enabled:
            return

        self.session_duration.observe(
            duration_seconds,
            labels={'severity': severity, 'outcome': outcome},
        )

        if root_cause_type:
            self.root_cause_total.inc(
                labels={'root_cause_type': root_cause_type, 'severity': severity}
            )

    def record_step_duration(
        self,
        step_number: int,
        step_name: str,
        duration_seconds: float,
    ) -> None:
        """Record time spent on a protocol step.

        Args:
            step_number: Step number (1-7)
            step_name: Human-readable step name
            duration_seconds: Time spent on the step
        """
        if not self.config.metrics.enabled:
            return

        self.step_duration.observe(
            duration_seconds,
            labels={'step_number': str(step_number), 'step_name': step_name},
        )

    def record_lesson_extracted(
        self,
        trigger_type: str,
        pattern_score: float,
    ) -> None:
        """Record a lesson extraction to LESSONS.md.

        Args:
            trigger_type: What triggered the lesson extraction
            pattern_score: The pattern's scoring (0.0-1.0)
        """
        if not self.config.metrics.enabled:
            return

        # Bucket the score
        if pattern_score >= 0.8:
            bucket = 'high'
        elif pattern_score >= 0.6:
            bucket = 'medium'
        else:
            bucket = 'low'

        self.lessons_extracted.inc(
            labels={'trigger_type': trigger_type, 'pattern_score_bucket': bucket}
        )

    def record_contract_violation(
        self,
        contract_type: str,
        severity: str,
        service: str,
    ) -> None:
        """Record an API contract violation.

        Args:
            contract_type: Type of contract violated
            severity: Violation severity
            service: Service where violation occurred
        """
        if not self.config.metrics.enabled:
            return

        self.contract_violations.inc(
            labels={
                'contract_type': contract_type,
                'severity': severity,
                'service': service,
            }
        )

    def record_expedited_disqualification(self, disqualifier: str) -> None:
        """Record when expedited path was disqualified.

        Args:
            disqualifier: Reason for disqualification
        """
        if not self.config.metrics.enabled:
            return

        self.expedited_path_usage.inc(
            labels={'path_type': 'full', 'disqualifier': disqualifier}
        )

    def to_prometheus(self) -> str:
        """Export all metrics in Prometheus exposition format."""
        return '\n\n'.join(m.to_prometheus() for m in self._all_metrics)


class MetricsExporter:
    """Export metrics to various backends."""

    def __init__(self, metrics: DebugMetrics, config: Optional[ObservabilityConfig] = None):
        """Initialize exporter.

        Args:
            metrics: The metrics registry to export
            config: Observability configuration
        """
        self.metrics = metrics
        self.config = config or ObservabilityConfig.for_tier(ObservabilityTier.TIER_1_LOCAL)
        self._export_path: Optional[Path] = None

        # Set up file export for Tier 1
        if self.config.tier == ObservabilityTier.TIER_1_LOCAL:
            self._setup_file_export()

    def _setup_file_export(self) -> None:
        """Set up file-based metrics export."""
        for parent in [Path.cwd(), *Path.cwd().parents]:
            if (parent / 'CLAUDE.md').exists():
                metrics_dir = parent / 'temp' / 'metrics'
                metrics_dir.mkdir(parents=True, exist_ok=True)
                self._export_path = metrics_dir
                break

    def export(self) -> None:
        """Export metrics to configured backend."""
        if self._export_path:
            self._export_to_file()
        elif self.config.metrics.prometheus_endpoint:
            self._push_to_gateway()

    def _export_to_file(self) -> None:
        """Export metrics to a file."""
        if self._export_path is None:
            return

        timestamp = datetime.now(UTC).strftime('%Y%m%d_%H%M%S')
        filename = f'metrics_{timestamp}.prom'

        filepath = self._export_path / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.metrics.to_prometheus())

        # Also write a 'latest' file for easy access
        latest = self._export_path / 'metrics_latest.prom'
        with open(latest, 'w', encoding='utf-8') as f:
            f.write(self.metrics.to_prometheus())

    def _push_to_gateway(self) -> None:
        """Push metrics to Prometheus Pushgateway."""
        if not self.config.metrics.prometheus_endpoint:
            return

        try:
            import urllib.request

            data = self.metrics.to_prometheus().encode('utf-8')
            req = urllib.request.Request(
                f'{self.config.metrics.prometheus_endpoint}/metrics/job/debug_protocol',
                data=data,
                method='POST',
            )
            req.add_header('Content-Type', 'text/plain')

            with urllib.request.urlopen(req, timeout=5) as response:
                response.read()

        except Exception:
            # Silently fail - observability should not break the application
            pass

    def get_metrics_json(self) -> dict:
        """Get metrics as JSON for API consumption."""
        result = {}
        for metric in self.metrics._all_metrics:
            if isinstance(metric, Counter):
                values = metric.collect()
                result[metric.name] = {
                    'type': 'counter',
                    'description': metric.description,
                    'values': [{'value': v.value, 'labels': v.labels} for v in values],
                }
            elif isinstance(metric, Histogram):
                result[metric.name] = {
                    'type': 'histogram',
                    'description': metric.description,
                    'buckets': metric.buckets,
                }
        return result
