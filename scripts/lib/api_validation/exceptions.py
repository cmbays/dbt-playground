"""Exceptions for API Contract Validation.

Part of Wave 3 P2: Integration Completion (WAVE3-024)
"""


class ApiValidationError(Exception):
    """Base exception for API validation errors."""

    pass


class ContractNotFoundError(ApiValidationError):
    """Contract definition not found."""

    def __init__(self, contract_name: str, service: str):
        self.contract_name = contract_name
        self.service = service
        super().__init__(f"Contract '{contract_name}' not found for service '{service}'")


class ContractViolationError(ApiValidationError):
    """Contract violation detected."""

    def __init__(
        self,
        contract_name: str,
        violation_type: str,
        details: str,
        severity: str = 'high',
    ):
        self.contract_name = contract_name
        self.violation_type = violation_type
        self.details = details
        self.severity = severity
        super().__init__(f"Contract violation [{severity}]: {violation_type} - {details}")


class BreakingChangeError(ApiValidationError):
    """Breaking change detected that requires major version bump."""

    def __init__(
        self,
        change_type: str,
        old_value: str,
        new_value: str,
        affected_consumers: int = 0,
    ):
        self.change_type = change_type
        self.old_value = old_value
        self.new_value = new_value
        self.affected_consumers = affected_consumers
        super().__init__(
            f"Breaking change: {change_type} changed from '{old_value}' to '{new_value}'"
        )


class SchemaValidationError(ApiValidationError):
    """Schema validation failed."""

    def __init__(self, schema_path: str, errors: list[str]):
        self.schema_path = schema_path
        self.errors = errors
        error_list = '\n  - '.join(errors)
        super().__init__(f"Schema validation failed at {schema_path}:\n  - {error_list}")
