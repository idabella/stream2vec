"""
Stream2Vec — SQLAlchemy Declarative Base.

All ORM models must inherit from this Base class.
"""

from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    """SQLAlchemy declarative base with common configuration."""

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Auto-generate table name from class name (snake_case)."""
        import re
        name = re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()
        return name
