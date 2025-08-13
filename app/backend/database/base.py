"""
Base model classes for SQLAlchemy with UUIDv7 primary keys and audit fields.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, declared_attr


class UUIDv7:
    """Custom UUIDv7 type for SQLAlchemy."""

    def __init__(self):
        pass

    def __call__(self) -> str:
        """Generate a UUIDv7 string."""
        # For now, use a simple UUID4. We'll implement proper UUIDv7 later
        # when we have the PostgreSQL function available
        return str(uuid.uuid4())


class BaseModel:
    """Base model class with common fields and functionality."""

    # Abstract base class
    __abstract__ = True

    # UUIDv7 primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=UUIDv7())

    # Audit fields
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )

    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name."""
        # Convert CamelCase to snake_case
        import re

        name = re.sub("(?!^)([A-Z][a-z]+)", r"_\1", cls.__name__)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()

    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<{self.__class__.__name__}(id={self.id})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            elif isinstance(value, uuid.UUID):
                result[column.name] = str(value)
            else:
                result[column.name] = value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseModel":
        """Create model instance from dictionary."""
        # Filter out None values and non-column attributes
        filtered_data = {}
        for key, value in data.items():
            if hasattr(cls, key) and value is not None:
                filtered_data[key] = value

        return cls(**filtered_data)


# Create the declarative base
Base = declarative_base(cls=BaseModel)


class TimestampMixin:
    """Mixin for models that need timestamp tracking."""

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )


class UUIDMixin:
    """Mixin for models that need UUIDv7 primary keys."""

    id = Column(UUID(as_uuid=True), primary_key=True, default=UUIDv7())


class SoftDeleteMixin:
    """Mixin for models that support soft deletion."""

    deleted_at = Column(DateTime(timezone=True), nullable=True)

    @property
    def is_deleted(self) -> bool:
        """Check if the record is soft deleted."""
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        """Soft delete the record."""
        self.deleted_at = datetime.now(timezone.utc)

    def restore(self) -> None:
        """Restore a soft deleted record."""
        self.deleted_at = None
