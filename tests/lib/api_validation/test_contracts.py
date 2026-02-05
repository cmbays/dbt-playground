"""Tests for API contract definitions.

Part of Wave 3 P2: Integration Completion (WAVE3-024)
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib.api_validation.contracts import (
    ApiEndpoint,
    ContractType,
    ContractVersion,
    DatabaseColumn,
    DatabaseContract,
    InternalApiContract,
    MessageContract,
)


class TestContractVersion:
    """Tests for ContractVersion dataclass."""

    def test_parse_valid_version(self):
        """Valid version strings parse correctly."""
        v = ContractVersion.parse('1.2.3')

        assert v.major == 1
        assert v.minor == 2
        assert v.patch == 3

    def test_parse_invalid_version(self):
        """Invalid version strings raise ValueError."""
        with pytest.raises(ValueError):
            ContractVersion.parse('1.2')

        with pytest.raises(ValueError):
            ContractVersion.parse('v1.2.3')

    def test_version_to_string(self):
        """Version converts to string correctly."""
        v = ContractVersion(1, 2, 3)
        assert str(v) == '1.2.3'

    def test_version_compatibility(self):
        """Version compatibility checks work."""
        v1_2_0 = ContractVersion(1, 2, 0)
        v1_3_0 = ContractVersion(1, 3, 0)
        v2_0_0 = ContractVersion(2, 0, 0)

        # Same major version is compatible
        assert v1_2_0.is_compatible_with(v1_3_0)
        assert v1_3_0.is_compatible_with(v1_2_0)

        # Different major version is incompatible
        assert not v1_2_0.is_compatible_with(v2_0_0)

    def test_requires_major_bump(self):
        """Major bump detection works."""
        v1 = ContractVersion(1, 0, 0)
        v2 = ContractVersion(2, 0, 0)

        assert v2.requires_major_bump(v1)
        assert not v1.requires_major_bump(v1)

    def test_bump_methods(self):
        """Version bump methods work correctly."""
        v = ContractVersion(1, 2, 3)

        assert str(v.bump_major()) == '2.0.0'
        assert str(v.bump_minor()) == '1.3.0'
        assert str(v.bump_patch()) == '1.2.4'


class TestInternalApiContract:
    """Tests for InternalApiContract."""

    @pytest.fixture
    def api_contract(self):
        """Create a sample API contract."""
        contract = InternalApiContract(
            name='user-api',
            version=ContractVersion(1, 0, 0),
            contract_type=ContractType.INTERNAL_API,
            owner='platform-team',
            base_url='/api/v1',
            authentication='jwt',
        )

        contract.add_endpoint(
            path='/users',
            method='GET',
            response_schema={
                'type': 'array',
                'items': {'type': 'object'},
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
                'required': ['name', 'email'],
            },
        )

        return contract

    def test_contract_type_set(self, api_contract):
        """Contract type is set correctly."""
        assert api_contract.contract_type == ContractType.INTERNAL_API

    def test_add_endpoint(self, api_contract):
        """Endpoints can be added."""
        assert len(api_contract.endpoints) == 2

    def test_get_endpoint(self, api_contract):
        """Endpoint can be retrieved by path and method."""
        endpoint = api_contract.get_endpoint('/users', 'GET')

        assert endpoint is not None
        assert endpoint.path == '/users'
        assert endpoint.method == 'GET'

    def test_get_missing_endpoint(self, api_contract):
        """Missing endpoint returns None."""
        endpoint = api_contract.get_endpoint('/missing', 'GET')
        assert endpoint is None

    def test_to_dict(self, api_contract):
        """Contract converts to dictionary."""
        d = api_contract.to_dict()

        assert d['name'] == 'user-api'
        assert d['version'] == '1.0.0'
        assert d['contract_type'] == 'internal_api'
        assert d['owner'] == 'platform-team'


class TestDatabaseContract:
    """Tests for DatabaseContract."""

    @pytest.fixture
    def db_contract(self):
        """Create a sample database contract."""
        contract = DatabaseContract(
            name='users-table',
            version=ContractVersion(1, 0, 0),
            contract_type=ContractType.DATABASE,
            owner='platform-team',
            table_name='users',
            schema_name='public',
        )

        contract.add_column(
            name='id',
            data_type='INTEGER',
            nullable=False,
            primary_key=True,
        )

        contract.add_column(
            name='email',
            data_type='VARCHAR(255)',
            nullable=False,
        )

        contract.add_column(
            name='org_id',
            data_type='INTEGER',
            nullable=True,
            foreign_key='organizations.id',
        )

        return contract

    def test_contract_type_set(self, db_contract):
        """Contract type is set correctly."""
        assert db_contract.contract_type == ContractType.DATABASE

    def test_add_column(self, db_contract):
        """Columns can be added."""
        assert len(db_contract.columns) == 3

    def test_get_column(self, db_contract):
        """Column can be retrieved by name."""
        col = db_contract.get_column('email')

        assert col is not None
        assert col.data_type == 'VARCHAR(255)'
        assert col.nullable is False

    def test_get_primary_key_columns(self, db_contract):
        """Primary key columns can be retrieved."""
        pk_cols = db_contract.get_primary_key_columns()

        assert len(pk_cols) == 1
        assert pk_cols[0].name == 'id'

    def test_get_foreign_key_columns(self, db_contract):
        """Foreign key columns can be retrieved."""
        fk_cols = db_contract.get_foreign_key_columns()

        assert len(fk_cols) == 1
        assert fk_cols[0].name == 'org_id'
        assert fk_cols[0].foreign_key == 'organizations.id'


class TestMessageContract:
    """Tests for MessageContract."""

    @pytest.fixture
    def message_contract(self):
        """Create a sample message contract."""
        return MessageContract(
            name='user-events',
            version=ContractVersion(1, 0, 0),
            contract_type=ContractType.MESSAGE,
            owner='platform-team',
            topic='user.events.v1',
            message_schema={
                'type': 'object',
                'properties': {
                    'event_type': {'type': 'string'},
                    'user_id': {'type': 'integer'},
                    'timestamp': {'type': 'string', 'format': 'date-time'},
                },
                'required': ['event_type', 'user_id', 'timestamp'],
            },
        )

    def test_contract_type_set(self, message_contract):
        """Contract type is set correctly."""
        assert message_contract.contract_type == ContractType.MESSAGE

    def test_topic_set(self, message_contract):
        """Topic is set correctly."""
        assert message_contract.topic == 'user.events.v1'

    def test_message_schema(self, message_contract):
        """Message schema is accessible."""
        schema = message_contract.message_schema

        assert schema['type'] == 'object'
        assert 'event_type' in schema['properties']


class TestApiEndpoint:
    """Tests for ApiEndpoint dataclass."""

    def test_endpoint_creation(self):
        """Endpoint can be created."""
        endpoint = ApiEndpoint(
            path='/users/{id}',
            method='GET',
            response_schema={'type': 'object'},
            required_headers=['Authorization'],
            rate_limit=100,
        )

        assert endpoint.path == '/users/{id}'
        assert endpoint.method == 'GET'
        assert endpoint.rate_limit == 100
        assert 'Authorization' in endpoint.required_headers


class TestDatabaseColumn:
    """Tests for DatabaseColumn dataclass."""

    def test_column_creation(self):
        """Column can be created."""
        col = DatabaseColumn(
            name='created_at',
            data_type='TIMESTAMP',
            nullable=False,
            default='CURRENT_TIMESTAMP',
            comment='Record creation time',
        )

        assert col.name == 'created_at'
        assert col.nullable is False
        assert col.default == 'CURRENT_TIMESTAMP'
