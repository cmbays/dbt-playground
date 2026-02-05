"""Contract definitions for API Contract Validation.

Defines contract types from PLANNER_REPORT.md (WAVE3-011):
- Internal APIs
- External services
- Message contracts
- Database schemas

Part of Wave 3 P2: Integration Completion (WAVE3-024)
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class ContractType(Enum):
    """Types of contracts that can be validated."""

    INTERNAL_API = 'internal_api'
    EXTERNAL_SERVICE = 'external_service'
    MESSAGE = 'message'
    DATABASE = 'database'


@dataclass
class ContractVersion:
    """Semantic version for contracts.

    Follows semver: MAJOR.MINOR.PATCH
    - MAJOR: Breaking changes
    - MINOR: New features, backward compatible
    - PATCH: Bug fixes, backward compatible
    """

    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, version_str: str) -> 'ContractVersion':
        """Parse version from string like '1.2.3'."""
        match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', version_str)
        if not match:
            raise ValueError(f"Invalid version format: {version_str}")
        return cls(
            major=int(match.group(1)),
            minor=int(match.group(2)),
            patch=int(match.group(3)),
        )

    def __str__(self) -> str:
        return f'{self.major}.{self.minor}.{self.patch}'

    def is_compatible_with(self, other: 'ContractVersion') -> bool:
        """Check if this version is compatible with another.

        Compatibility rules:
        - Same major version required
        - Consumer can use older minor versions
        """
        return self.major == other.major

    def requires_major_bump(self, other: 'ContractVersion') -> bool:
        """Check if upgrade from other to this requires major bump."""
        return self.major > other.major

    def bump_major(self) -> 'ContractVersion':
        """Return a new version with major bumped."""
        return ContractVersion(self.major + 1, 0, 0)

    def bump_minor(self) -> 'ContractVersion':
        """Return a new version with minor bumped."""
        return ContractVersion(self.major, self.minor + 1, 0)

    def bump_patch(self) -> 'ContractVersion':
        """Return a new version with patch bumped."""
        return ContractVersion(self.major, self.minor, self.patch + 1)


@dataclass
class ApiEndpoint:
    """Definition of an API endpoint."""

    path: str
    method: str  # GET, POST, PUT, DELETE, etc.
    request_schema: Optional[dict[str, Any]] = None
    response_schema: Optional[dict[str, Any]] = None
    required_headers: list[str] = field(default_factory=list)
    rate_limit: Optional[int] = None  # requests per minute


@dataclass
class ApiContract:
    """Base class for API contracts."""

    name: str
    version: ContractVersion
    contract_type: ContractType
    owner: str
    description: str = ''
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    deprecated: bool = False
    deprecation_date: Optional[datetime] = None
    consumers: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert contract to dictionary."""
        return {
            'name': self.name,
            'version': str(self.version),
            'contract_type': self.contract_type.value,
            'owner': self.owner,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'deprecated': self.deprecated,
            'deprecation_date': self.deprecation_date.isoformat() if self.deprecation_date else None,
            'consumers': self.consumers,
        }


@dataclass
class InternalApiContract(ApiContract):
    """Contract for internal API endpoints.

    Used for service-to-service communication within the system.
    """

    base_url: str = ''
    endpoints: list[ApiEndpoint] = field(default_factory=list)
    authentication: str = 'jwt'  # jwt, api_key, none
    timeout_ms: int = 5000

    def __post_init__(self) -> None:
        self.contract_type = ContractType.INTERNAL_API

    def add_endpoint(
        self,
        path: str,
        method: str,
        request_schema: Optional[dict[str, Any]] = None,
        response_schema: Optional[dict[str, Any]] = None,
    ) -> None:
        """Add an endpoint to the contract."""
        self.endpoints.append(
            ApiEndpoint(
                path=path,
                method=method,
                request_schema=request_schema,
                response_schema=response_schema,
            )
        )

    def get_endpoint(self, path: str, method: str) -> Optional[ApiEndpoint]:
        """Find an endpoint by path and method."""
        for endpoint in self.endpoints:
            if endpoint.path == path and endpoint.method == method:
                return endpoint
        return None


@dataclass
class MessageContract(ApiContract):
    """Contract for message queue/event schemas.

    Used for async communication via queues or event buses.
    """

    topic: str = ''
    message_schema: dict[str, Any] = field(default_factory=dict)
    key_schema: Optional[dict[str, Any]] = None
    max_size_bytes: int = 1_000_000  # 1MB default
    retention_hours: int = 168  # 7 days

    def __post_init__(self) -> None:
        self.contract_type = ContractType.MESSAGE


@dataclass
class DatabaseColumn:
    """Definition of a database column."""

    name: str
    data_type: str
    nullable: bool = True
    primary_key: bool = False
    foreign_key: Optional[str] = None  # table.column format
    default: Optional[str] = None
    comment: str = ''


@dataclass
class DatabaseContract(ApiContract):
    """Contract for database schemas.

    Used to track table/view definitions and their consumers.
    """

    table_name: str = ''
    schema_name: str = 'public'
    columns: list[DatabaseColumn] = field(default_factory=list)
    indexes: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.contract_type = ContractType.DATABASE

    def add_column(
        self,
        name: str,
        data_type: str,
        nullable: bool = True,
        primary_key: bool = False,
        foreign_key: Optional[str] = None,
        default: Optional[str] = None,
        comment: str = '',
    ) -> None:
        """Add a column to the contract."""
        self.columns.append(
            DatabaseColumn(
                name=name,
                data_type=data_type,
                nullable=nullable,
                primary_key=primary_key,
                foreign_key=foreign_key,
                default=default,
                comment=comment,
            )
        )

    def get_column(self, name: str) -> Optional[DatabaseColumn]:
        """Find a column by name."""
        for column in self.columns:
            if column.name == name:
                return column
        return None

    def get_primary_key_columns(self) -> list[DatabaseColumn]:
        """Get all primary key columns."""
        return [c for c in self.columns if c.primary_key]

    def get_foreign_key_columns(self) -> list[DatabaseColumn]:
        """Get all foreign key columns."""
        return [c for c in self.columns if c.foreign_key]
