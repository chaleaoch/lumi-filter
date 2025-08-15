"""Peewee ORM models for the example application.

This module defines a very small data model used to demonstrate how
``lumi_filter`` integrates with Peewee queries. The data is stored in a
SQLite database file inside the example directory (so it persists while
the app is running).

The module also seeds a few records on first import to make it easy to
test filtering & ordering straight away.
"""

from __future__ import annotations

import datetime
from pathlib import Path
import peewee
import decimal

DB_PATH = Path(__file__).resolve().parent.parent / "example.db"


database = peewee.SqliteDatabase(str(DB_PATH))


class BaseModel(peewee.Model):
	class Meta:
		database = database


class Product(BaseModel):
	"""Product you can list & create.

	Fields kept intentionally small to exercise the different filter
	field types (str/int/bool/decimal/datetime).
	"""

	name = peewee.CharField(max_length=120, index=True)
	price = peewee.DecimalField(max_digits=10, decimal_places=2, auto_round=True)
	is_active = peewee.BooleanField(default=True, index=True)
	created_at = peewee.DateTimeField(default=datetime.datetime.utcnow, index=True)

	def to_dict(self):  # Simple serializer for the API layer
		# self.price is already a Decimal instance when accessed on model
		# Accessing attribute produces a Decimal; ensure correct type for mypy/pyright
		price_decimal: decimal.Decimal = decimal.Decimal(str(self.price))
		return {
			"id": self.id,
			"name": self.name,
			"price": float(price_decimal),
			"is_active": self.is_active,
			"created_at": self.created_at.isoformat(),
		}


def _init_db():
	database.connect(reuse_if_open=True)
	database.create_tables([Product])

	# Seed only if empty
	if Product.select().count() == 0:
		sample = [
			{"name": "Apple", "price": 1.20, "is_active": True},
			{"name": "Orange", "price": 2.50, "is_active": True},
			{"name": "Banana", "price": 0.80, "is_active": True},
			{"name": "Watermelon", "price": 6.30, "is_active": False},
			{"name": "Grape", "price": 3.10, "is_active": True},
		]
		with database.atomic():
			for item in sample:
				Product.create(**item)


_init_db()

__all__ = ["Product", "database"]

