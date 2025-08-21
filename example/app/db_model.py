from datetime import datetime

import peewee

from extentions import db


class Category(db.Model):
    id = peewee.AutoField()
    name = peewee.CharField(max_length=50, unique=True, index=True)
    created_at = peewee.DateTimeField(default=lambda: datetime.now())


class Product(db.Model):
    id = peewee.AutoField()
    name = peewee.CharField(max_length=120)
    price = peewee.DecimalField(max_digits=10, decimal_places=2, auto_round=True)
    is_active = peewee.BooleanField(default=True)
    category = peewee.ForeignKeyField(Category, backref="products", on_delete="CASCADE")
    created_at = peewee.DateTimeField(default=lambda: datetime.now())
