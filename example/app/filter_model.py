"""Filter model demonstrating usage of ``lumi_filter`` with Peewee.

The FilterProduct model maps Peewee model fields to filter fields
automatically (int/str/bool/datetime/decimal). We also add an extra
ordering field `name_len` to show how to order by an expression.
"""

from __future__ import annotations

import peewee

from lumi_filter.model import Model
from lumi_filter.field import IntField, StrField, BooleanField, DateTimeField, DecimalField
from .db_model import Product


class FilterProduct(Model):
	# Explicitly declare one field just to show manual override (others auto)
	name = StrField(source=Product.name)  # override to set explicit source
	price = DecimalField(source=Product.price)
	is_active = BooleanField(source=Product.is_active)
	created_at = DateTimeField(source=Product.created_at)
	id = IntField(source=Product.id)

	class Meta:
		schema = Product  # tell MetaModel to introspect (dup ok for example clarity)
		ordering_extra_field = {"name_len"}

	# Provide backend ordering extra field implementation via property for peewee backend
	@staticmethod
	def name_len_expression():
		return peewee.fn.length(Product.name).alias("name_len")

