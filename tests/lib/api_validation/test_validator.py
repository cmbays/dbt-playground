"""Tests for API contract validator.

Part of Wave 3 P2: Integration Completion (WAVE3-024)
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib.api_validation.contracts import (
    ContractType,
    ContractVersion,
    DatabaseContract,
    InternalApiContract,
    MessageContract,
)
from scripts.lib.api_validation.validator import (
    BREAKING_CHANGES,
    ChangeType,
    ContractValidator,
    ValidationResult,
    ValidationSeverity,
)


class TestChangeType:
    """Tests for ChangeType enum."""

    def test_breaking_changes_set(self):
        """Breaking changes are correctly categorized."""
        assert ChangeType.ENDPOINT_REMOVED in BREAKING_CHANGES
        assert ChangeType.FIELD_REMOVED in BREAKING_CHANGES
        assert ChangeType.COLUMN_REMOVED in BREAKING_CHANGES

        assert ChangeType.ENDPOINT_ADDED not in BREAKING_CHANGES
        assert ChangeType.OPTIONAL_FIELD_ADDED not in BREAKING_CHANGES


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_has_breaking_changes(self):
        """Breaking change detection works."""
        from scripts.lib.api_validation.validator import ValidationFinding

        result = ValidationResult(
            contract_name='test',
            contract_type=ContractType.INTERNAL_API,
            passed=False,
            findings=[
                ValidationFinding(
                    severity=ValidationSeverity.CRITICAL,
                    change_type=ChangeType.ENDPOINT_REMOVED,
                    message='Test',
                    location='test',
                )
            ],
        )

        assert result.has_breaking_changes
        assert len(result.breaking_changes) == 1

    def test_to_dict(self):
        """Result converts to dictionary."""
        result = ValidationResult(
            contract_name='test',
            contract_type=ContractType.INTERNAL_API,
            passed=True,
        )

        d = result.to_dict()

        assert d['contract_name'] == 'test'
        assert d['passed'] is True


class TestContractValidatorApiChanges:
    """Tests for API contract validation."""

    @pytest.fixture
    def validator(self):
        """Create validator."""
        return ContractValidator()

    @pytest.fixture
    def old_api(self):
        """Create original API contract."""
        contract = InternalApiContract(
            name='user-api',
            version=ContractVersion(1, 0, 0),
            contract_type=ContractType.INTERNAL_API,
            owner='test',
        )

        contract.add_endpoint(
            path='/users',
            method='GET',
            response_schema={
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {'type': 'string'},
                },
            },
        )

        contract.add_endpoint(
            path='/users',
            method='POST',
            request_schema={
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'email': {'type': 'string'},
                },
                'required': ['name'],
            },
        )

        return contract

    def test_no_changes_passes(self, validator, old_api):
        """No changes results in pass."""
        result = validator.validate_change(old_api, old_api)

        assert result.passed
        assert not result.has_breaking_changes
        assert result.expedited_path_allowed

    def test_endpoint_removed_breaking(self, validator, old_api):
        """Removed endpoint is breaking change."""
        new_api = InternalApiContract(
            name='user-api',
            version=ContractVersion(1, 0, 0),
            contract_type=ContractType.INTERNAL_API,
            owner='test',
        )

        # Only one endpoint (POST removed)
        new_api.add_endpoint(
            path='/users',
            method='GET',
            response_schema={'type': 'object'},
        )

        result = validator.validate_change(old_api, new_api)

        assert result.has_breaking_changes
        assert not result.expedited_path_allowed
        assert result.version_bump_required == 'major'

    def test_endpoint_added_non_breaking(self, validator, old_api):
        """Added endpoint is non-breaking."""
        new_api = InternalApiContract(
            name='user-api',
            version=ContractVersion(1, 0, 0),
            contract_type=ContractType.INTERNAL_API,
            owner='test',
        )

        # Copy existing endpoints
        for endpoint in old_api.endpoints:
            new_api.add_endpoint(
                path=endpoint.path,
                method=endpoint.method,
                request_schema=endpoint.request_schema,
                response_schema=endpoint.response_schema,
            )

        # Add new endpoint
        new_api.add_endpoint(path='/users/{id}', method='DELETE')

        result = validator.validate_change(old_api, new_api)

        assert result.passed
        assert not result.has_breaking_changes
        assert result.version_bump_required == 'minor'

    def test_field_removed_breaking(self, validator, old_api):
        """Removed response field is breaking."""
        new_api = InternalApiContract(
            name='user-api',
            version=ContractVersion(1, 0, 0),
            contract_type=ContractType.INTERNAL_API,
            owner='test',
        )

        new_api.add_endpoint(
            path='/users',
            method='GET',
            response_schema={
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    # 'name' field removed
                },
            },
        )

        new_api.add_endpoint(
            path='/users',
            method='POST',
            request_schema=old_api.get_endpoint('/users', 'POST').request_schema,
        )

        result = validator.validate_change(old_api, new_api)

        assert result.has_breaking_changes
        assert any(f.change_type == ChangeType.FIELD_REMOVED for f in result.findings)

    def test_field_made_required_breaking(self, validator, old_api):
        """Making optional field required is breaking."""
        new_api = InternalApiContract(
            name='user-api',
            version=ContractVersion(1, 0, 0),
            contract_type=ContractType.INTERNAL_API,
            owner='test',
        )

        new_api.add_endpoint(
            path='/users',
            method='GET',
            response_schema=old_api.get_endpoint('/users', 'GET').response_schema,
        )

        new_api.add_endpoint(
            path='/users',
            method='POST',
            request_schema={
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'email': {'type': 'string'},
                },
                'required': ['name', 'email'],  # email is now required
            },
        )

        result = validator.validate_change(old_api, new_api)

        assert result.has_breaking_changes
        assert any(f.change_type == ChangeType.FIELD_MADE_REQUIRED for f in result.findings)

    def test_optional_field_added_non_breaking(self, validator, old_api):
        """Added optional field is non-breaking."""
        new_api = InternalApiContract(
            name='user-api',
            version=ContractVersion(1, 0, 0),
            contract_type=ContractType.INTERNAL_API,
            owner='test',
        )

        new_api.add_endpoint(
            path='/users',
            method='GET',
            response_schema={
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {'type': 'string'},
                    'avatar_url': {'type': 'string'},  # New optional field
                },
            },
        )

        new_api.add_endpoint(
            path='/users',
            method='POST',
            request_schema=old_api.get_endpoint('/users', 'POST').request_schema,
        )

        result = validator.validate_change(old_api, new_api)

        assert result.passed
        assert not result.has_breaking_changes
        assert any(f.change_type == ChangeType.OPTIONAL_FIELD_ADDED for f in result.findings)


class TestContractValidatorDatabaseChanges:
    """Tests for database contract validation."""

    @pytest.fixture
    def validator(self):
        """Create validator."""
        return ContractValidator()

    @pytest.fixture
    def old_db(self):
        """Create original database contract."""
        contract = DatabaseContract(
            name='users-table',
            version=ContractVersion(1, 0, 0),
            contract_type=ContractType.DATABASE,
            owner='test',
            table_name='users',
        )

        contract.add_column('id', 'INTEGER', nullable=False, primary_key=True)
        contract.add_column('email', 'VARCHAR(255)', nullable=False)
        contract.add_column('nickname', 'VARCHAR(100)', nullable=True)

        return contract

    def test_column_removed_breaking(self, validator, old_db):
        """Removed column is breaking change."""
        new_db = DatabaseContract(
            name='users-table',
            version=ContractVersion(1, 0, 0),
            contract_type=ContractType.DATABASE,
            owner='test',
            table_name='users',
        )

        new_db.add_column('id', 'INTEGER', nullable=False, primary_key=True)
        new_db.add_column('email', 'VARCHAR(255)', nullable=False)
        # nickname removed

        result = validator.validate_change(old_db, new_db)

        assert result.has_breaking_changes
        assert any(f.change_type == ChangeType.COLUMN_REMOVED for f in result.findings)

    def test_column_type_changed_breaking(self, validator, old_db):
        """Changed column type is breaking."""
        new_db = DatabaseContract(
            name='users-table',
            version=ContractVersion(1, 0, 0),
            contract_type=ContractType.DATABASE,
            owner='test',
            table_name='users',
        )

        new_db.add_column('id', 'INTEGER', nullable=False, primary_key=True)
        new_db.add_column('email', 'TEXT', nullable=False)  # Changed from VARCHAR to TEXT
        new_db.add_column('nickname', 'VARCHAR(100)', nullable=True)

        result = validator.validate_change(old_db, new_db)

        assert result.has_breaking_changes
        assert any(f.change_type == ChangeType.COLUMN_TYPE_CHANGED for f in result.findings)

    def test_nullable_to_not_null_breaking(self, validator, old_db):
        """Changing nullable to not null is breaking."""
        new_db = DatabaseContract(
            name='users-table',
            version=ContractVersion(1, 0, 0),
            contract_type=ContractType.DATABASE,
            owner='test',
            table_name='users',
        )

        new_db.add_column('id', 'INTEGER', nullable=False, primary_key=True)
        new_db.add_column('email', 'VARCHAR(255)', nullable=False)
        new_db.add_column('nickname', 'VARCHAR(100)', nullable=False)  # Changed to NOT NULL

        result = validator.validate_change(old_db, new_db)

        assert result.has_breaking_changes
        assert any(f.change_type == ChangeType.NULLABLE_TO_NOT_NULL for f in result.findings)

    def test_column_added_non_breaking(self, validator, old_db):
        """Added column is non-breaking."""
        new_db = DatabaseContract(
            name='users-table',
            version=ContractVersion(1, 0, 0),
            contract_type=ContractType.DATABASE,
            owner='test',
            table_name='users',
        )

        new_db.add_column('id', 'INTEGER', nullable=False, primary_key=True)
        new_db.add_column('email', 'VARCHAR(255)', nullable=False)
        new_db.add_column('nickname', 'VARCHAR(100)', nullable=True)
        new_db.add_column('created_at', 'TIMESTAMP', nullable=True)  # New column

        result = validator.validate_change(old_db, new_db)

        assert result.passed
        assert not result.has_breaking_changes
        assert any(f.change_type == ChangeType.COLUMN_ADDED for f in result.findings)

    def test_index_added_non_breaking(self, validator, old_db):
        """Added index is non-breaking."""
        new_db = DatabaseContract(
            name='users-table',
            version=ContractVersion(1, 0, 0),
            contract_type=ContractType.DATABASE,
            owner='test',
            table_name='users',
            indexes=['idx_users_email'],  # New index
        )

        new_db.add_column('id', 'INTEGER', nullable=False, primary_key=True)
        new_db.add_column('email', 'VARCHAR(255)', nullable=False)
        new_db.add_column('nickname', 'VARCHAR(100)', nullable=True)

        result = validator.validate_change(old_db, new_db)

        assert result.passed
        assert any(f.change_type == ChangeType.INDEX_ADDED for f in result.findings)


class TestContractValidatorMessageChanges:
    """Tests for message contract validation."""

    @pytest.fixture
    def validator(self):
        """Create validator."""
        return ContractValidator()

    @pytest.fixture
    def old_message(self):
        """Create original message contract."""
        return MessageContract(
            name='user-events',
            version=ContractVersion(1, 0, 0),
            contract_type=ContractType.MESSAGE,
            owner='test',
            topic='user.events.v1',
            message_schema={
                'type': 'object',
                'properties': {
                    'event_type': {'type': 'string'},
                    'user_id': {'type': 'integer'},
                },
                'required': ['event_type', 'user_id'],
            },
        )

    def test_topic_changed_breaking(self, validator, old_message):
        """Changed topic is breaking."""
        new_message = MessageContract(
            name='user-events',
            version=ContractVersion(1, 0, 0),
            contract_type=ContractType.MESSAGE,
            owner='test',
            topic='user.events.v2',  # Changed topic
            message_schema=old_message.message_schema,
        )

        result = validator.validate_change(old_message, new_message)

        assert result.has_breaking_changes

    def test_schema_field_removed_breaking(self, validator, old_message):
        """Removed message field is breaking."""
        new_message = MessageContract(
            name='user-events',
            version=ContractVersion(1, 0, 0),
            contract_type=ContractType.MESSAGE,
            owner='test',
            topic='user.events.v1',
            message_schema={
                'type': 'object',
                'properties': {
                    'event_type': {'type': 'string'},
                    # user_id removed
                },
                'required': ['event_type'],
            },
        )

        result = validator.validate_change(old_message, new_message)

        assert result.has_breaking_changes


class TestExpeditedPathGating:
    """Tests for expedited path checking."""

    @pytest.fixture
    def validator(self):
        """Create validator."""
        return ContractValidator()

    def test_check_expedited_path_allowed(self, validator):
        """Expedited path allowed when no breaking changes."""
        result = ValidationResult(
            contract_name='test',
            contract_type=ContractType.INTERNAL_API,
            passed=True,
            expedited_path_allowed=True,
        )

        allowed, reasons = validator.check_expedited_path(result)

        assert allowed
        assert len(reasons) == 0

    def test_check_expedited_path_blocked(self, validator):
        """Expedited path blocked on breaking changes."""
        from scripts.lib.api_validation.validator import ValidationFinding

        result = ValidationResult(
            contract_name='test',
            contract_type=ContractType.INTERNAL_API,
            passed=False,
            findings=[
                ValidationFinding(
                    severity=ValidationSeverity.CRITICAL,
                    change_type=ChangeType.ENDPOINT_REMOVED,
                    message='Endpoint /users removed',
                    location='endpoint:/users:GET',
                )
            ],
            expedited_path_allowed=False,
        )

        allowed, reasons = validator.check_expedited_path(result)

        assert not allowed
        assert len(reasons) == 1
        assert 'endpoint_removed' in reasons[0]


class TestViolationCallbacks:
    """Tests for validation event callbacks."""

    def test_on_violation_callback(self):
        """Violation callback is invoked."""
        violations = []

        def on_violation(finding):
            violations.append(finding)

        validator = ContractValidator(on_violation=on_violation)

        old = InternalApiContract(
            name='test',
            version=ContractVersion(1, 0, 0),
            contract_type=ContractType.INTERNAL_API,
            owner='test',
        )
        old.add_endpoint('/users', 'GET')

        new = InternalApiContract(
            name='test',
            version=ContractVersion(1, 0, 0),
            contract_type=ContractType.INTERNAL_API,
            owner='test',
        )
        # No endpoints - /users removed

        validator.validate_change(old, new)

        assert len(violations) > 0

    def test_on_breaking_change_callback(self):
        """Breaking change callback is invoked."""
        breaking_changes = []

        def on_breaking(finding):
            breaking_changes.append(finding)

        validator = ContractValidator(on_breaking_change=on_breaking)

        old = InternalApiContract(
            name='test',
            version=ContractVersion(1, 0, 0),
            contract_type=ContractType.INTERNAL_API,
            owner='test',
        )
        old.add_endpoint('/users', 'GET')

        new = InternalApiContract(
            name='test',
            version=ContractVersion(1, 0, 0),
            contract_type=ContractType.INTERNAL_API,
            owner='test',
        )

        validator.validate_change(old, new)

        assert len(breaking_changes) == 1
        assert breaking_changes[0].change_type == ChangeType.ENDPOINT_REMOVED
