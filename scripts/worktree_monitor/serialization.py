"""
Worktree Monitor v2.0 - Serialization Utilities

Provides automatic JSON serialization for dataclasses via SerializableMixin.
Handles enums, datetimes, nested dataclasses, and lists automatically.

Created: Phase 4 Day 3 (Refactoring)
"""

from dataclasses import fields, is_dataclass
from datetime import datetime
from enum import Enum
from typing import Any


def serialize_value(value: Any) -> Any:
    """Recursively serialize a value for JSON.

    Handles:
    - Enums: returns .value
    - datetime: returns .isoformat()
    - Objects with to_dict(): calls to_dict()
    - Lists: recursively serializes elements
    - Dicts: recursively serializes values
    - Dataclasses: recursively serializes fields
    - Other: returns as-is

    Args:
        value: Any value to serialize.

    Returns:
        JSON-serializable value.
    """
    if value is None:
        return None
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if hasattr(value, 'to_dict'):
        return value.to_dict()
    if isinstance(value, dict):
        return {k: serialize_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [serialize_value(v) for v in value]
    if is_dataclass(value) and not isinstance(value, type):
        return {f.name: serialize_value(getattr(value, f.name)) for f in fields(value)}
    return value


class SerializableMixin:
    """Mixin providing automatic to_dict() for dataclasses.

    Usage:
        @dataclass
        class MyModel(SerializableMixin):
            name: str
            status: MyEnum
            created_at: datetime

        model = MyModel(name="test", status=MyEnum.ACTIVE, created_at=now)
        data = model.to_dict()  # Automatically serializes all fields
    """

    def to_dict(self) -> dict[str, Any]:
        """Serialize all dataclass fields to a dictionary.

        Returns:
            Dictionary with all fields serialized for JSON.

        Raises:
            TypeError: If the class is not a dataclass.
        """
        if not is_dataclass(type(self)):
            raise TypeError(
                f'{type(self).__name__} is not a dataclass. '
                'SerializableMixin.to_dict() requires a dataclass.'
            )
        return {f.name: serialize_value(getattr(self, f.name)) for f in fields(self)}
