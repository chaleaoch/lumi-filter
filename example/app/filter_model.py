from __future__ import annotations

from lumi_filter.field import BooleanField, DateTimeField, DecimalField, IntField, StrField
from lumi_filter.model import Model

from .db_model import Category, Product


class FilterProduct(Model):
    name = StrField(source=Product.name)
    price = DecimalField(source=Product.price)
    is_active = BooleanField(source=Product.is_active)
    created_at = DateTimeField(source=Product.created_at)
    id = IntField(source=Product.id)
    category_id = IntField(source=Product.category)
    category_name = StrField(source=Category.name)
