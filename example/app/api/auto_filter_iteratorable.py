"""Automatic Iterable field introspection demo.

GET /auto/iterable/products

Uses AutoQueryModel for filtering iterable data structures like lists of dictionaries.
"""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from lumi_filter.shortcut import AutoQueryModel

bp = Blueprint("auto_iterable", __name__, url_prefix="/auto/iterable/")

# Sample data - in real application this might come from CSV, JSON API, etc.
sample_products = [
    {
        "id": 1,
        "name": "Laptop",
        "price": 999.99,
        "is_active": True,
        "category": {"id": 1, "name": "Electronics"},
        "created_at": "2023-01-15T10:30:00",
        "tags": ["computer", "portable"],
    },
    {
        "id": 2,
        "name": "Mouse",
        "price": 25.50,
        "is_active": True,
        "category": {"id": 1, "name": "Electronics"},
        "created_at": "2023-02-10T14:20:00",
        "tags": ["computer", "accessory"],
    },
    {
        "id": 3,
        "name": "Desk Chair",
        "price": 150.00,
        "is_active": False,
        "category": {"id": 2, "name": "Furniture"},
        "created_at": "2023-03-05T09:15:00",
        "tags": ["furniture", "office"],
    },
    {
        "id": 4,
        "name": "Coffee Mug",
        "price": 12.99,
        "is_active": True,
        "category": {"id": 3, "name": "Kitchen"},
        "created_at": "2023-04-01T11:45:00",
        "tags": ["kitchen", "ceramic"],
    },
]


@bp.get("")
def list_products_auto():
    query_model = AutoQueryModel(sample_products, request.args)
    filtered_data = query_model.filter().order().result()
    filtered_data = list(filtered_data)

    return jsonify({"count": len(filtered_data), "results": filtered_data})
