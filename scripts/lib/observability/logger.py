"""Structured logging for Debug Protocol.

Implements correlation ID injection for trace/log correlation
as defined in OBSERVABILITY_INTEGRATION.md (WAVE3-013).

Part of Wave 3 P2: Integration Completion (WAVE3-025)
"""

import json
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Optional

from scripts.lib.observability.config import LoggingConfig, ObservabilityConfig, ObservabilityTier


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def __init__(
        self,
        service_name: str = 'vibe-code-debug',
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ):
        super().__init__()
        self.service_name = service_name
        self.trace_id = trace_id
        self.span_id = span_id
        self.session_id = session_id

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            'timestamp': datetime.now(UTC).isoformat(),
            'level': record.levelname,
            'service': self.service_name,
            'logger': record.name,
            'message': record.getMessage(),
        }

        # Add correlation IDs
        if self.trace_id:
            log_data['trace_id'] = self.trace_id
        if self.span_id:
            log_data['span_id'] = self.span_id
        if self.session_id:
            log_data['session_id'] = self.session_id

        # Add extra fields from record
        extra = getattr(record, 'extra', None)
        if extra and isinstance(extra, dict):
            log_data.update(extra)

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_data)


class TextFormatter(logging.Formatter):
    """Human-readable formatter with correlation IDs."""

    COLORS = {
        'DEBUG': '\033[36m',  # Cyan
        'INFO': '\033[32m',  # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',  # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m',
    }

    def __init__(
        self,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        session_id: Optional[str] = None,
        use_colors: bool = True,
    ):
        super().__init__()
        self.trace_id = trace_id
        self.span_id = span_id
        self.session_id = session_id
        self.use_colors = use_colors and sys.stdout.isatty()

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as human-readable text."""
        timestamp = datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')

        # Build correlation prefix
        correlation_parts = []
        if self.session_id:
            correlation_parts.append(f'session={self.session_id}')
        if self.trace_id:
            correlation_parts.append(f'trace={self.trace_id[:8]}')
        correlation = f'[{" ".join(correlation_parts)}] ' if correlation_parts else ''

        # Format level with optional color
        level = record.levelname
        if self.use_colors:
            color = self.COLORS.get(level, self.COLORS['RESET'])
            reset = self.COLORS['RESET']
            level = f'{color}{level}{reset}'

        # Build message
        message = record.getMessage()

        # Add extra fields
        extra = getattr(record, 'extra', None)
        if extra and isinstance(extra, dict):
            extra_str = ' | '.join(f'{k}={v}' for k, v in extra.items())
            message = f'{message} | {extra_str}'

        formatted = f'{timestamp} {level:8} {correlation}{record.name}: {message}'

        # Add exception if present
        if record.exc_info:
            formatted += f'\n{self.formatException(record.exc_info)}'

        return formatted


class StructuredLogger:
    """Logger with correlation ID support for debug sessions.

    Provides structured logging with automatic trace/span correlation.
    """

    def __init__(
        self,
        name: str = 'debug_protocol',
        config: Optional[LoggingConfig] = None,
    ):
        """Initialize structured logger.

        Args:
            name: Logger name
            config: Logging configuration
        """
        self.name = name
        self.config = config or LoggingConfig()
        self._logger = logging.getLogger(name)

        # Correlation IDs (set when session starts)
        self._trace_id: Optional[str] = None
        self._span_id: Optional[str] = None
        self._session_id: Optional[str] = None

        self._setup_handler()

    def _setup_handler(self) -> None:
        """Configure logging handler based on config."""
        # Remove existing handlers
        self._logger.handlers.clear()

        # Set level
        level = getattr(logging, self.config.level.upper(), logging.INFO)
        self._logger.setLevel(level)

        # Create handler
        if self.config.output_path:
            handler = logging.FileHandler(
                self.config.output_path,
                encoding='utf-8',
            )
        else:
            handler = logging.StreamHandler(sys.stdout)

        # Set formatter based on format type
        if self.config.format == 'json':
            formatter = StructuredFormatter(
                trace_id=self._trace_id,
                span_id=self._span_id,
                session_id=self._session_id,
            )
        else:
            formatter = TextFormatter(
                trace_id=self._trace_id,
                span_id=self._span_id,
                session_id=self._session_id,
            )

        handler.setFormatter(formatter)
        self._logger.addHandler(handler)

    def set_correlation_ids(
        self,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> None:
        """Set correlation IDs for log entries.

        Args:
            trace_id: Jaeger trace ID
            span_id: Jaeger span ID
            session_id: Debug session ID
        """
        self._trace_id = trace_id
        self._span_id = span_id
        self._session_id = session_id
        self._setup_handler()  # Recreate formatter with new IDs

    def clear_correlation_ids(self) -> None:
        """Clear correlation IDs."""
        self._trace_id = None
        self._span_id = None
        self._session_id = None
        self._setup_handler()

    def _log(
        self,
        level: int,
        msg: str,
        *args: Any,
        extra: Optional[dict[str, Any]] = None,
        exc_info: bool = False,
        **kwargs: Any,
    ) -> None:
        """Internal log method with extra field support."""
        record_extra = extra or {}

        # Create LogRecord manually to inject extra
        record = self._logger.makeRecord(
            self.name,
            level,
            '',
            0,
            msg,
            args,
            exc_info=exc_info if exc_info else None,
            extra=None,
        )
        record.extra = record_extra
        self._logger.handle(record)

    def debug(self, msg: str, *args: Any, extra: Optional[dict[str, Any]] = None) -> None:
        """Log debug message."""
        self._log(logging.DEBUG, msg, *args, extra=extra)

    def info(self, msg: str, *args: Any, extra: Optional[dict[str, Any]] = None) -> None:
        """Log info message."""
        self._log(logging.INFO, msg, *args, extra=extra)

    def warning(self, msg: str, *args: Any, extra: Optional[dict[str, Any]] = None) -> None:
        """Log warning message."""
        self._log(logging.WARNING, msg, *args, extra=extra)

    def error(
        self,
        msg: str,
        *args: Any,
        extra: Optional[dict[str, Any]] = None,
        exc_info: bool = False,
    ) -> None:
        """Log error message."""
        self._log(logging.ERROR, msg, *args, extra=extra, exc_info=exc_info)

    def critical(
        self,
        msg: str,
        *args: Any,
        extra: Optional[dict[str, Any]] = None,
        exc_info: bool = False,
    ) -> None:
        """Log critical message."""
        self._log(logging.CRITICAL, msg, *args, extra=extra, exc_info=exc_info)

    # Debug Protocol specific logging methods

    def session_started(
        self,
        session_id: str,
        bug_description: str,
        severity: str,
    ) -> None:
        """Log session start event."""
        self.info(
            'Debug session started',
            extra={
                'event': 'debug.session.started',
                'session_id': session_id,
                'bug_description': bug_description[:100],
                'severity': severity,
            },
        )

    def symptom_detected(
        self,
        session_id: str,
        symptom_type: str,
        description: str,
    ) -> None:
        """Log symptom detection."""
        self.info(
            'Symptom detected',
            extra={
                'event': 'debug.symptom.detected',
                'session_id': session_id,
                'symptom_type': symptom_type,
                'description': description[:200],
            },
        )

    def step_started(
        self,
        session_id: str,
        step_number: int,
        step_name: str,
    ) -> None:
        """Log protocol step start."""
        self.debug(
            f'Step {step_number} started: {step_name}',
            extra={
                'event': f'debug.step.{step_number}.started',
                'session_id': session_id,
                'step_number': step_number,
                'step_name': step_name,
            },
        )

    def step_completed(
        self,
        session_id: str,
        step_number: int,
        step_name: str,
        duration_seconds: float,
    ) -> None:
        """Log protocol step completion."""
        self.debug(
            f'Step {step_number} completed: {step_name}',
            extra={
                'event': f'debug.step.{step_number}.completed',
                'session_id': session_id,
                'step_number': step_number,
                'step_name': step_name,
                'duration_seconds': duration_seconds,
            },
        )

    def hypothesis_formed(
        self,
        session_id: str,
        hypothesis: str,
        evidence_count: int,
    ) -> None:
        """Log hypothesis formation."""
        self.info(
            'Hypothesis formed',
            extra={
                'event': 'debug.hypothesis.formed',
                'session_id': session_id,
                'hypothesis': hypothesis[:200],
                'evidence_count': evidence_count,
            },
        )

    def hypothesis_validated(
        self,
        session_id: str,
        hypothesis: str,
        validated: bool,
    ) -> None:
        """Log hypothesis validation result."""
        result = 'confirmed' if validated else 'rejected'
        self.info(
            f'Hypothesis {result}',
            extra={
                'event': 'debug.hypothesis.validated',
                'session_id': session_id,
                'hypothesis': hypothesis[:200],
                'validated': validated,
            },
        )

    def root_cause_identified(
        self,
        session_id: str,
        root_cause: str,
        category: str,
    ) -> None:
        """Log root cause identification."""
        self.info(
            'Root cause identified',
            extra={
                'event': 'debug.root_cause.identified',
                'session_id': session_id,
                'root_cause': root_cause[:300],
                'category': category,
            },
        )

    def session_completed(
        self,
        session_id: str,
        outcome: str,
        duration_minutes: int,
        lesson_extracted: bool,
    ) -> None:
        """Log session completion."""
        self.info(
            'Debug session completed',
            extra={
                'event': 'debug.session.completed',
                'session_id': session_id,
                'outcome': outcome,
                'duration_minutes': duration_minutes,
                'lesson_extracted': lesson_extracted,
            },
        )

    def contract_violation(
        self,
        session_id: str,
        contract_type: str,
        service: str,
        details: str,
    ) -> None:
        """Log API contract violation."""
        self.warning(
            'Contract violation detected',
            extra={
                'event': 'debug.contract.violation',
                'session_id': session_id,
                'contract_type': contract_type,
                'service': service,
                'details': details[:200],
            },
        )


# Module-level logger instance
_default_logger: Optional[StructuredLogger] = None


def get_logger(
    name: str = 'debug_protocol',
    config: Optional[ObservabilityConfig] = None,
) -> StructuredLogger:
    """Get or create a structured logger.

    Args:
        name: Logger name
        config: Optional observability configuration

    Returns:
        StructuredLogger instance
    """
    global _default_logger

    if _default_logger is None or name != 'debug_protocol':
        logging_config = config.logging if config else LoggingConfig()
        _default_logger = StructuredLogger(name, logging_config)

    return _default_logger
