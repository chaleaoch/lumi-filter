"""Peewee ORM models for the example application.

This module defines a very small data model used to demonstrate how
``lumi_filter`` integrates with Peewee queries. The data is stored in a
SQLite database file inside the example directory (so it persists while
the app is running).

The module also seeds a few records on first import to make it easy to
test filtering & ordering straight away.
"""

from __future__ import annotations

from datetime import datetime, timezone

import peewee

from extentions import database


class BaseModel(peewee.Model):
    class Meta:
        database = database


class Category(BaseModel):
    name = peewee.CharField(max_length=50, unique=True, index=True)
    created_at = peewee.DateTimeField(default=lambda: datetime.now(timezone.utc))

    def __str__(self) -> str:  # pragma: no cover - repr helper
        return f"Category<{self.id}:{self.name}>"


class Product(BaseModel):
    name = peewee.CharField(max_length=120)
    price = peewee.DecimalField(max_digits=10, decimal_places=2, auto_round=True)
    is_active = peewee.BooleanField(default=True)
    category = peewee.ForeignKeyField(Category, backref="products", on_delete="CASCADE")
    created_at = peewee.DateTimeField(default=lambda: datetime.now(timezone.utc))
