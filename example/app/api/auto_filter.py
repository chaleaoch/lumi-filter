"""Automatic Iterable field introspection demo.

GET /auto/iterable/products

Uses AutoQueryModel for filtering iterable data structures like lists of dictionaries.
"""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from lumi_filter.shortcut import AutoQueryModel

from app.db_model import Category, Product

bp = Blueprint("auto_iterable", __name__, url_prefix="/auto/")


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


@bp.get("/iterable/")
def list_products_iterable_auto():
    products_data = [
        {
            "product": {
                "id": p.id,
                "name": p.name,
                "price": p.price,
                "is_active": p.is_active,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            },
            "category_id": p.category.id if p.category else None,
            "category_name": p.category.name if p.category else None,
        }
        for p in Product.select().join(Category)
    ]

    query_model = AutoQueryModel(products_data, request.args)
    filtered_data = query_model.filter().order().result()
    filtered_data = list(filtered_data)

    return jsonify({"count": len(filtered_data), "results": filtered_data})
