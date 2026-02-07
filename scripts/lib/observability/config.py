"""Observability configuration for Debug Protocol.

Defines configuration tiers and settings for different deployment environments.

Part of Wave 3 P2: Integration Completion (WAVE3-025)
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class ObservabilityTier(Enum):
    """Deployment tier affecting observability capabilities.

    Tier 1: Local development (file-based, no external services)
    Tier 2: Small production (Grafana Cloud free tier)
    Tier 3: Production scale (full observability stack)
    """

    TIER_1_LOCAL = 'local'
    TIER_2_SMALL_PROD = 'small_prod'
    TIER_3_PRODUCTION = 'production'


@dataclass
class TracingConfig:
    """Configuration for distributed tracing."""

    enabled: bool = True
    service_name: str = 'vibe-code-debug'
    jaeger_endpoint: Optional[str] = None  # None = file export
    sampling_rate: float = 1.0  # 100% for local, 10% for prod


@dataclass
class MetricsConfig:
    """Configuration for Prometheus metrics."""

    enabled: bool = True
    port: int = 8000
    prometheus_endpoint: Optional[str] = None  # None = no push gateway
    push_interval_seconds: int = 30


@dataclass
class LoggingConfig:
    """Configuration for structured logging."""

    enabled: bool = True
    level: str = 'INFO'
    format: str = 'json'  # 'json' or 'text'
    output_path: Optional[Path] = None  # None = stdout


@dataclass
class ObservabilityConfig:
    """Complete observability configuration.

    Provides sensible defaults for each tier with easy overrides.
    """

    tier: ObservabilityTier = ObservabilityTier.TIER_1_LOCAL
    tracing: TracingConfig = field(default_factory=TracingConfig)
    metrics: MetricsConfig = field(default_factory=MetricsConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    # Retention settings (for reference, enforced by external systems)
    trace_retention_days: int = 7
    metrics_retention_days: int = 30
    log_retention_days: int = 14

    @classmethod
    def for_tier(cls, tier: ObservabilityTier) -> 'ObservabilityConfig':
        """Create configuration optimized for a specific tier."""
        if tier == ObservabilityTier.TIER_1_LOCAL:
            return cls(
                tier=tier,
                tracing=TracingConfig(
                    enabled=True,
                    sampling_rate=1.0,  # 100% for debugging
                    jaeger_endpoint=None,  # File export
                ),
                metrics=MetricsConfig(
                    enabled=True,
                    prometheus_endpoint=None,  # Local scraping only
                ),
                logging=LoggingConfig(
                    enabled=True,
                    level='DEBUG',
                    format='text',  # Human readable locally
                ),
            )
        elif tier == ObservabilityTier.TIER_2_SMALL_PROD:
            return cls(
                tier=tier,
                tracing=TracingConfig(
                    enabled=True,
                    sampling_rate=0.5,  # 50% in staging
                    jaeger_endpoint='http://localhost:14268/api/traces',
                ),
                metrics=MetricsConfig(
                    enabled=True,
                ),
                logging=LoggingConfig(
                    enabled=True,
                    level='INFO',
                    format='json',
                ),
            )
        else:  # TIER_3_PRODUCTION
            return cls(
                tier=tier,
                tracing=TracingConfig(
                    enabled=True,
                    sampling_rate=0.1,  # 10% in production
                    jaeger_endpoint='http://tempo:14268/api/traces',
                ),
                metrics=MetricsConfig(
                    enabled=True,
                    push_interval_seconds=15,  # More frequent in prod
                ),
                logging=LoggingConfig(
                    enabled=True,
                    level='INFO',
                    format='json',
                ),
                trace_retention_days=7,
                metrics_retention_days=30,
                log_retention_days=14,
            )

    @classmethod
    def from_env(cls) -> 'ObservabilityConfig':
        """Create configuration from environment variables."""
        import os

        tier_str = os.environ.get('OBSERVABILITY_TIER', 'local')
        tier_map = {
            'local': ObservabilityTier.TIER_1_LOCAL,
            'small_prod': ObservabilityTier.TIER_2_SMALL_PROD,
            'production': ObservabilityTier.TIER_3_PRODUCTION,
        }
        tier = tier_map.get(tier_str, ObservabilityTier.TIER_1_LOCAL)

        config = cls.for_tier(tier)

        # Override with specific environment variables
        if jaeger := os.environ.get('JAEGER_ENDPOINT'):
            config.tracing.jaeger_endpoint = jaeger

        if sampling := os.environ.get('TRACE_SAMPLING_RATE'):
            config.tracing.sampling_rate = float(sampling)

        if port := os.environ.get('METRICS_PORT'):
            config.metrics.port = int(port)

        if level := os.environ.get('LOG_LEVEL'):
            config.logging.level = level.upper()

        return config
