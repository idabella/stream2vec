"""
Database Base — Declarative base for all SQLAlchemy ORM models.

Kept in its own module so it can be imported by both:
  - app/models/*.py  (ORM model definitions)
  - alembic/env.py   (metadata discovery without starting the engine)

without triggering engine creation or settings loading.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass
