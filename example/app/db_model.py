from datetime import datetime, timezone

import peewee

from extentions import database


class BaseModel(peewee.Model):
    class Meta:
        database = database


class Category(BaseModel):
    id = peewee.AutoField()
    name = peewee.CharField(max_length=50, unique=True, index=True)
    created_at = peewee.DateTimeField(default=lambda: datetime.now(timezone.utc))


class Product(BaseModel):
    id = peewee.AutoField()
    name = peewee.CharField(max_length=120)
    price = peewee.DecimalField(max_digits=10, decimal_places=2, auto_round=True)
    is_active = peewee.BooleanField(default=True)
    category = peewee.ForeignKeyField(Category, backref="products", on_delete="CASCADE")
    created_at = peewee.DateTimeField(default=lambda: datetime.now(timezone.utc))
