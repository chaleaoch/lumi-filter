"""Automatic Peewee field introspection demo.

GET /auto/peewee/products

Uses Meta.schema = Product; all model fields auto filterable.
"""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from lumi_filter.shortcut import AutoQueryModel

from ..db_model import Category, Product

bp = Blueprint("auto_peewee", __name__, url_prefix="/auto/peewee/")


@bp.get("")
def list_products_auto():
    query = Product.select(
        Product.id,
        Product.name,
        Product.price,
        Product.is_active,
        Product.created_at,
        Category.id.alias("category_id"),
        Category.name.alias("category_name"),
    ).join(Category)
    query = AutoQueryModel(query, request.args).filter().order().result()
    return jsonify(list(query.dicts()))
