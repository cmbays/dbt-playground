"""Contract Validator for API Contract Validation.

Implements validation rules from PLANNER_REPORT.md (WAVE3-011):
- Breaking change detection
- Expedited path gating
- Observability event emission

Part of Wave 3 P2: Integration Completion (WAVE3-024)
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional

from scripts.lib.api_validation.contracts import (
    ApiContract,
    ContractType,
    ContractVersion,
    DatabaseColumn,
    DatabaseContract,
    InternalApiContract,
    MessageContract,
)
from scripts.lib.api_validation.exceptions import (
    BreakingChangeError,
    ContractViolationError,
    SchemaValidationError,
)


class ValidationSeverity(Enum):
    """Severity levels for validation findings."""

    INFO = 'info'  # Informational, no action needed
    WARNING = 'warning'  # Should be addressed, not blocking
    ERROR = 'error'  # Must be addressed, blocks expedited path
    CRITICAL = 'critical'  # Breaking change, requires immediate attention


class ChangeType(Enum):
    """Types of contract changes."""

    # Breaking changes (require major version bump)
    ENDPOINT_REMOVED = 'endpoint_removed'
    ENDPOINT_RENAMED = 'endpoint_renamed'
    FIELD_REMOVED = 'field_removed'
    FIELD_TYPE_CHANGED = 'field_type_changed'
    FIELD_MADE_REQUIRED = 'field_made_required'
    AUTH_REQUIREMENT_ADDED = 'auth_requirement_added'
    RATE_LIMIT_DECREASED = 'rate_limit_decreased'
    COLUMN_REMOVED = 'column_removed'
    COLUMN_TYPE_CHANGED = 'column_type_changed'
    NULLABLE_TO_NOT_NULL = 'nullable_to_not_null'

    # Non-breaking changes (minor version bump)
    ENDPOINT_ADDED = 'endpoint_added'
    OPTIONAL_FIELD_ADDED = 'optional_field_added'
    RATE_LIMIT_INCREASED = 'rate_limit_increased'
    COLUMN_ADDED = 'column_added'
    INDEX_ADDED = 'index_added'

    # Patch-level changes
    DOCUMENTATION_UPDATED = 'documentation_updated'
    INTERNAL_OPTIMIZATION = 'internal_optimization'


# Breaking changes that block expedited path
BREAKING_CHANGES = {
    ChangeType.ENDPOINT_REMOVED,
    ChangeType.ENDPOINT_RENAMED,
    ChangeType.FIELD_REMOVED,
    ChangeType.FIELD_TYPE_CHANGED,
    ChangeType.FIELD_MADE_REQUIRED,
    ChangeType.AUTH_REQUIREMENT_ADDED,
    ChangeType.RATE_LIMIT_DECREASED,
    ChangeType.COLUMN_REMOVED,
    ChangeType.COLUMN_TYPE_CHANGED,
    ChangeType.NULLABLE_TO_NOT_NULL,
}


@dataclass
class ValidationFinding:
    """A single validation finding."""

    severity: ValidationSeverity
    change_type: ChangeType
    message: str
    location: str  # e.g., "endpoint:/api/users:POST" or "column:users.email"
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def is_breaking(self) -> bool:
        """Check if this finding represents a breaking change."""
        return self.change_type in BREAKING_CHANGES

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            'severity': self.severity.value,
            'change_type': self.change_type.value,
            'message': self.message,
            'location': self.location,
            'details': self.details,
            'is_breaking': self.is_breaking,
            'timestamp': self.timestamp.isoformat(),
        }


@dataclass
class ValidationResult:
    """Result of contract validation."""

    contract_name: str
    contract_type: ContractType
    passed: bool
    findings: list[ValidationFinding] = field(default_factory=list)
    expedited_path_allowed: bool = True
    version_bump_required: Optional[str] = None  # 'major', 'minor', 'patch', or None
    validated_at: datetime = field(default_factory=datetime.now)

    @property
    def breaking_changes(self) -> list[ValidationFinding]:
        """Get all breaking change findings."""
        return [f for f in self.findings if f.is_breaking]

    @property
    def has_breaking_changes(self) -> bool:
        """Check if there are any breaking changes."""
        return len(self.breaking_changes) > 0

    @property
    def error_count(self) -> int:
        """Count of error-level findings."""
        return sum(1 for f in self.findings if f.severity == ValidationSeverity.ERROR)

    @property
    def warning_count(self) -> int:
        """Count of warning-level findings."""
        return sum(1 for f in self.findings if f.severity == ValidationSeverity.WARNING)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            'contract_name': self.contract_name,
            'contract_type': self.contract_type.value,
            'passed': self.passed,
            'findings': [f.to_dict() for f in self.findings],
            'expedited_path_allowed': self.expedited_path_allowed,
            'version_bump_required': self.version_bump_required,
            'breaking_changes_count': len(self.breaking_changes),
            'error_count': self.error_count,
            'warning_count': self.warning_count,
            'validated_at': self.validated_at.isoformat(),
        }


class ContractValidator:
    """Validates API contracts for breaking changes and compliance.

    Integrates with observability hooks for event emission.
    """

    def __init__(
        self,
        on_violation: Optional[Callable[[ValidationFinding], None]] = None,
        on_breaking_change: Optional[Callable[[ValidationFinding], None]] = None,
    ):
        """Initialize validator.

        Args:
            on_violation: Callback for any validation violation
            on_breaking_change: Callback specifically for breaking changes
        """
        self._on_violation = on_violation
        self._on_breaking_change = on_breaking_change

    def validate_change(
        self,
        old_contract: ApiContract,
        new_contract: ApiContract,
    ) -> ValidationResult:
        """Validate changes between two contract versions.

        Args:
            old_contract: The existing contract
            new_contract: The proposed new contract

        Returns:
            ValidationResult with all findings
        """
        findings: list[ValidationFinding] = []

        # Dispatch to type-specific validator
        if old_contract.contract_type == ContractType.INTERNAL_API:
            findings.extend(
                self._validate_api_changes(
                    old_contract,  # type: ignore
                    new_contract,  # type: ignore
                )
            )
        elif old_contract.contract_type == ContractType.DATABASE:
            findings.extend(
                self._validate_database_changes(
                    old_contract,  # type: ignore
                    new_contract,  # type: ignore
                )
            )
        elif old_contract.contract_type == ContractType.MESSAGE:
            findings.extend(
                self._validate_message_changes(
                    old_contract,  # type: ignore
                    new_contract,  # type: ignore
                )
            )

        # Determine version bump requirement
        version_bump = self._determine_version_bump(findings)

        # Check if expedited path is allowed
        expedited_allowed = not any(f.is_breaking for f in findings)

        # Emit events for findings
        for finding in findings:
            if self._on_violation:
                self._on_violation(finding)
            if finding.is_breaking and self._on_breaking_change:
                self._on_breaking_change(finding)

        # Build result
        passed = not any(f.severity in {ValidationSeverity.ERROR, ValidationSeverity.CRITICAL} for f in findings)

        return ValidationResult(
            contract_name=new_contract.name,
            contract_type=new_contract.contract_type,
            passed=passed,
            findings=findings,
            expedited_path_allowed=expedited_allowed,
            version_bump_required=version_bump,
        )

    def _validate_api_changes(
        self,
        old: InternalApiContract,
        new: InternalApiContract,
    ) -> list[ValidationFinding]:
        """Validate changes to an internal API contract."""
        findings: list[ValidationFinding] = []

        old_endpoints = {(e.path, e.method): e for e in old.endpoints}
        new_endpoints = {(e.path, e.method): e for e in new.endpoints}

        # Check for removed endpoints
        for key, endpoint in old_endpoints.items():
            if key not in new_endpoints:
                findings.append(
                    ValidationFinding(
                        severity=ValidationSeverity.CRITICAL,
                        change_type=ChangeType.ENDPOINT_REMOVED,
                        message=f"Endpoint {endpoint.method} {endpoint.path} was removed",
                        location=f"endpoint:{endpoint.path}:{endpoint.method}",
                        details={'path': endpoint.path, 'method': endpoint.method},
                    )
                )

        # Check for new endpoints (non-breaking but notable)
        for key, endpoint in new_endpoints.items():
            if key not in old_endpoints:
                findings.append(
                    ValidationFinding(
                        severity=ValidationSeverity.INFO,
                        change_type=ChangeType.ENDPOINT_ADDED,
                        message=f"New endpoint {endpoint.method} {endpoint.path} added",
                        location=f"endpoint:{endpoint.path}:{endpoint.method}",
                        details={'path': endpoint.path, 'method': endpoint.method},
                    )
                )

        # Check for changed endpoints
        for key, old_endpoint in old_endpoints.items():
            if key in new_endpoints:
                new_endpoint = new_endpoints[key]
                findings.extend(
                    self._compare_endpoint_schemas(old_endpoint, new_endpoint)
                )

        # Check rate limit changes
        if old.timeout_ms != new.timeout_ms:
            if new.timeout_ms < old.timeout_ms:
                findings.append(
                    ValidationFinding(
                        severity=ValidationSeverity.WARNING,
                        change_type=ChangeType.RATE_LIMIT_DECREASED,
                        message=f"Timeout decreased from {old.timeout_ms}ms to {new.timeout_ms}ms",
                        location=f"api:{new.name}:timeout",
                        details={'old': old.timeout_ms, 'new': new.timeout_ms},
                    )
                )

        # Check authentication changes
        if old.authentication != new.authentication:
            if new.authentication != 'none' and old.authentication == 'none':
                findings.append(
                    ValidationFinding(
                        severity=ValidationSeverity.CRITICAL,
                        change_type=ChangeType.AUTH_REQUIREMENT_ADDED,
                        message=f"Authentication requirement added: {new.authentication}",
                        location=f"api:{new.name}:authentication",
                        details={'old': old.authentication, 'new': new.authentication},
                    )
                )

        return findings

    def _compare_endpoint_schemas(
        self,
        old_endpoint,
        new_endpoint,
    ) -> list[ValidationFinding]:
        """Compare schemas between endpoint versions."""
        findings: list[ValidationFinding] = []
        location = f"endpoint:{old_endpoint.path}:{old_endpoint.method}"

        # Compare request schemas
        if old_endpoint.request_schema and new_endpoint.request_schema:
            findings.extend(
                self._compare_schemas(
                    old_endpoint.request_schema,
                    new_endpoint.request_schema,
                    f"{location}:request",
                )
            )

        # Compare response schemas
        if old_endpoint.response_schema and new_endpoint.response_schema:
            findings.extend(
                self._compare_schemas(
                    old_endpoint.response_schema,
                    new_endpoint.response_schema,
                    f"{location}:response",
                )
            )

        return findings

    def _compare_schemas(
        self,
        old_schema: dict[str, Any],
        new_schema: dict[str, Any],
        location: str,
    ) -> list[ValidationFinding]:
        """Compare JSON schemas for breaking changes."""
        findings: list[ValidationFinding] = []

        old_props = old_schema.get('properties', {})
        new_props = new_schema.get('properties', {})
        old_required = set(old_schema.get('required', []))
        new_required = set(new_schema.get('required', []))

        # Check for removed fields
        for field_name in old_props:
            if field_name not in new_props:
                findings.append(
                    ValidationFinding(
                        severity=ValidationSeverity.CRITICAL,
                        change_type=ChangeType.FIELD_REMOVED,
                        message=f"Field '{field_name}' was removed",
                        location=f"{location}:{field_name}",
                        details={'field': field_name},
                    )
                )

        # Check for new required fields
        new_required_fields = new_required - old_required
        for field_name in new_required_fields:
            if field_name in old_props:
                # Existing field made required
                findings.append(
                    ValidationFinding(
                        severity=ValidationSeverity.CRITICAL,
                        change_type=ChangeType.FIELD_MADE_REQUIRED,
                        message=f"Field '{field_name}' changed from optional to required",
                        location=f"{location}:{field_name}",
                        details={'field': field_name},
                    )
                )

        # Check for type changes
        for field_name, old_def in old_props.items():
            if field_name in new_props:
                new_def = new_props[field_name]
                old_type = old_def.get('type')
                new_type = new_def.get('type')
                if old_type and new_type and old_type != new_type:
                    findings.append(
                        ValidationFinding(
                            severity=ValidationSeverity.CRITICAL,
                            change_type=ChangeType.FIELD_TYPE_CHANGED,
                            message=f"Field '{field_name}' type changed from {old_type} to {new_type}",
                            location=f"{location}:{field_name}",
                            details={'field': field_name, 'old_type': old_type, 'new_type': new_type},
                        )
                    )

        # Check for new optional fields (non-breaking)
        for field_name in new_props:
            if field_name not in old_props and field_name not in new_required:
                findings.append(
                    ValidationFinding(
                        severity=ValidationSeverity.INFO,
                        change_type=ChangeType.OPTIONAL_FIELD_ADDED,
                        message=f"New optional field '{field_name}' added",
                        location=f"{location}:{field_name}",
                        details={'field': field_name},
                    )
                )

        return findings

    def _validate_database_changes(
        self,
        old: DatabaseContract,
        new: DatabaseContract,
    ) -> list[ValidationFinding]:
        """Validate changes to a database contract."""
        findings: list[ValidationFinding] = []

        old_columns = {c.name: c for c in old.columns}
        new_columns = {c.name: c for c in new.columns}

        # Check for removed columns
        for name, column in old_columns.items():
            if name not in new_columns:
                findings.append(
                    ValidationFinding(
                        severity=ValidationSeverity.CRITICAL,
                        change_type=ChangeType.COLUMN_REMOVED,
                        message=f"Column '{name}' was removed from {old.table_name}",
                        location=f"column:{old.table_name}.{name}",
                        details={'column': name, 'table': old.table_name},
                    )
                )

        # Check for added columns
        for name, column in new_columns.items():
            if name not in old_columns:
                findings.append(
                    ValidationFinding(
                        severity=ValidationSeverity.INFO,
                        change_type=ChangeType.COLUMN_ADDED,
                        message=f"Column '{name}' added to {new.table_name}",
                        location=f"column:{new.table_name}.{name}",
                        details={'column': name, 'table': new.table_name, 'type': column.data_type},
                    )
                )

        # Check for column changes
        for name, old_col in old_columns.items():
            if name in new_columns:
                new_col = new_columns[name]
                findings.extend(
                    self._compare_columns(old_col, new_col, new.table_name)
                )

        # Check for new indexes (non-breaking)
        new_indexes = set(new.indexes) - set(old.indexes)
        for index in new_indexes:
            findings.append(
                ValidationFinding(
                    severity=ValidationSeverity.INFO,
                    change_type=ChangeType.INDEX_ADDED,
                    message=f"Index '{index}' added to {new.table_name}",
                    location=f"index:{new.table_name}.{index}",
                    details={'index': index, 'table': new.table_name},
                )
            )

        return findings

    def _compare_columns(
        self,
        old_col: DatabaseColumn,
        new_col: DatabaseColumn,
        table_name: str,
    ) -> list[ValidationFinding]:
        """Compare database columns for breaking changes."""
        findings: list[ValidationFinding] = []
        location = f"column:{table_name}.{old_col.name}"

        # Type changes
        if old_col.data_type != new_col.data_type:
            findings.append(
                ValidationFinding(
                    severity=ValidationSeverity.CRITICAL,
                    change_type=ChangeType.COLUMN_TYPE_CHANGED,
                    message=f"Column '{old_col.name}' type changed from {old_col.data_type} to {new_col.data_type}",
                    location=location,
                    details={
                        'column': old_col.name,
                        'old_type': old_col.data_type,
                        'new_type': new_col.data_type,
                    },
                )
            )

        # Nullable changes
        if old_col.nullable and not new_col.nullable:
            findings.append(
                ValidationFinding(
                    severity=ValidationSeverity.CRITICAL,
                    change_type=ChangeType.NULLABLE_TO_NOT_NULL,
                    message=f"Column '{old_col.name}' changed from nullable to not null",
                    location=location,
                    details={'column': old_col.name},
                )
            )

        return findings

    def _validate_message_changes(
        self,
        old: MessageContract,
        new: MessageContract,
    ) -> list[ValidationFinding]:
        """Validate changes to a message contract."""
        findings: list[ValidationFinding] = []

        # Compare message schemas
        if old.message_schema and new.message_schema:
            findings.extend(
                self._compare_schemas(
                    old.message_schema,
                    new.message_schema,
                    f"message:{new.topic}:schema",
                )
            )

        # Topic changes (always breaking)
        if old.topic != new.topic:
            findings.append(
                ValidationFinding(
                    severity=ValidationSeverity.CRITICAL,
                    change_type=ChangeType.ENDPOINT_RENAMED,  # Reuse for topic rename
                    message=f"Topic changed from '{old.topic}' to '{new.topic}'",
                    location=f"message:{old.topic}",
                    details={'old_topic': old.topic, 'new_topic': new.topic},
                )
            )

        return findings

    def _determine_version_bump(self, findings: list[ValidationFinding]) -> Optional[str]:
        """Determine what version bump is required based on findings."""
        if any(f.is_breaking for f in findings):
            return 'major'
        elif any(
            f.change_type
            in {
                ChangeType.ENDPOINT_ADDED,
                ChangeType.OPTIONAL_FIELD_ADDED,
                ChangeType.COLUMN_ADDED,
                ChangeType.INDEX_ADDED,
            }
            for f in findings
        ):
            return 'minor'
        elif any(f.change_type == ChangeType.DOCUMENTATION_UPDATED for f in findings):
            return 'patch'
        return None

    def check_expedited_path(self, result: ValidationResult) -> tuple[bool, list[str]]:
        """Check if expedited path is allowed based on validation result.

        Args:
            result: The validation result to check

        Returns:
            Tuple of (allowed, list of disqualifying reasons)
        """
        disqualifiers: list[str] = []

        if result.has_breaking_changes:
            for finding in result.breaking_changes:
                disqualifiers.append(
                    f"{finding.change_type.value}: {finding.message}"
                )

        return (len(disqualifiers) == 0, disqualifiers)

    def validate_against_current(
        self,
        proposed_contract: ApiContract,
        current_contracts: dict[str, ApiContract],
    ) -> ValidationResult:
        """Validate a proposed contract against current contracts.

        Args:
            proposed_contract: The new contract version
            current_contracts: Dictionary of current contracts by name

        Returns:
            ValidationResult
        """
        if proposed_contract.name not in current_contracts:
            # New contract - no validation needed
            return ValidationResult(
                contract_name=proposed_contract.name,
                contract_type=proposed_contract.contract_type,
                passed=True,
                findings=[
                    ValidationFinding(
                        severity=ValidationSeverity.INFO,
                        change_type=ChangeType.ENDPOINT_ADDED,
                        message=f"New contract '{proposed_contract.name}' created",
                        location=f"contract:{proposed_contract.name}",
                    )
                ],
                expedited_path_allowed=True,
            )

        current = current_contracts[proposed_contract.name]
        return self.validate_change(current, proposed_contract)
