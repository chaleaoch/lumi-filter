"""Peewee extra ordering field demo.

GET /peewee/products/extra-ordering

Adds computed column (name_len) allowing ordering by it via:
  ?ordering=-name_len or ?ordering=name_len

Also supports all normal filters.
"""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from ..db_model import Category, Product
from ..filter_model import FilterProduct

bp = Blueprint("peewee_extra_ordering", __name__, url_prefix="/peewee/products/extra-ordering")


@bp.get("")
def list_products_extra_ordering():
    query = Product.select(
        Product.id,
        Product.name,
        Product.price,
        Product.is_active,
        Product.created_at,
        FilterProduct.name_len_expression(),
        Category.id.alias("category_id"),
        Category.name.alias("category_name"),
    ).join(Category)
    request_args = {k: v for k, v in request.args.items() if v not in (None, "")}
    filtered = FilterProduct.cls_filter(query, request_args)
    ordered = FilterProduct.cls_order(filtered, request_args)
    data = [p.to_dict() | {"name_len": len(p.name)} for p in ordered]
    return jsonify({"count": len(data), "results": data})
