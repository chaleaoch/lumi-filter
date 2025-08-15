"""Peewee basic filtering & ordering demo.

GET /peewee/products

Supports lookups (depending on field type):
  name, name__!, price__gt, price__gte, price__lt, price__lte,
  is_active, created_at__gte, created_at__lte, price__in (substring like),
  ordering=-price,name

Examples:
  /peewee/products?price__gte=1&price__lte=3&ordering=-price
  /peewee/products?name__in=app (LIKE match, substring)
  /peewee/products?is_active=true&ordering=name
"""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from ..db_model import Category, Product
from ..filter_model import FilterProduct

bp = Blueprint("peewee_basic", __name__, url_prefix="/peewee/products")


@bp.get("")
def list_products():
    query = Product.select(
        Product.id,
        Product.name,
        Product.price,
        Product.is_active,
        Product.created_at,
        Category.id.alias("category_id"),
        Category.name.alias("category_name"),
    ).join(Category)
    request_args = {k: v for k, v in request.args.items() if v not in (None, "")}
    filtered = FilterProduct.cls_filter(query, request_args)
    ordered = FilterProduct.cls_order(filtered, request_args)
    data = [p.to_dict() for p in ordered]
    return jsonify({"count": len(data), "results": data})
