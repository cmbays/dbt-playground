"""API Contract Validation module for Debug Protocol.

Provides contract validation, breaking change detection, and expedited path gating.

Part of Wave 3 P2: Integration Completion (WAVE3-024)
"""

from scripts.lib.api_validation.contracts import (
    ApiContract,
    ContractType,
    ContractVersion,
    DatabaseContract,
    InternalApiContract,
    MessageContract,
)
from scripts.lib.api_validation.exceptions import (
    ApiValidationError,
    BreakingChangeError,
    ContractNotFoundError,
    ContractViolationError,
    SchemaValidationError,
)
from scripts.lib.api_validation.validator import (
    ContractValidator,
    ValidationResult,
    ValidationSeverity,
)

__all__ = [
    # Contracts
    'ApiContract',
    'ContractType',
    'ContractVersion',
    'DatabaseContract',
    'InternalApiContract',
    'MessageContract',
    # Exceptions
    'ApiValidationError',
    'BreakingChangeError',
    'ContractNotFoundError',
    'ContractViolationError',
    'SchemaValidationError',
    # Validator
    'ContractValidator',
    'ValidationResult',
    'ValidationSeverity',
]
