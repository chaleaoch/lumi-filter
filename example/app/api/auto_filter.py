"""Automatic field introspection demo.

This module demonstrates automatic field introspection using AutoQueryModel for both
database queries and iterable data structures like lists of dictionaries.

Example:
    GET /auto/ - Auto-filter database query results
    GET /auto/iterable/ - Auto-filter iterable data structures
"""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from lumi_filter.shortcut import AutoQueryModel

from app.db_model import Category, Product

bp = Blueprint("auto_iterable", __name__, url_prefix="/auto/")


@bp.get("")
def list_products_auto():
    """List products using automatic field introspection.

    This endpoint demonstrates automatic field detection and filtering using AutoQueryModel
    with database query results. All selected fields are automatically made filterable.

    Args:
        id (int, optional): Filter by product ID.
        name (str, optional): Filter by product name (supports __in, __nin).
        price (decimal, optional): Filter by price (supports __gte, __lte).
        is_active (bool, optional): Filter by active status.
        created_at (datetime, optional): Filter by creation date (supports __gte, __lte).
        category_id (int, optional): Filter by category ID.
        category_name (str, optional): Filter by category name.
        ordering (str, optional): Order results by field(s). Use '-' prefix for descending.

    Returns:
        list: List of product dictionaries with fields:
            id, name, price, is_active, created_at, category_id, category_name

    Examples:
        Basic request:
            GET /auto/

        Auto-detected field filtering:
            GET /auto/?name__in=Apple,Orange&price__gte=100&is_active=true

        Ordering by auto-detected fields:
            GET /auto/?ordering=-price,name
    """
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
    """List products using automatic field introspection on iterable data.

    This endpoint demonstrates automatic field detection and filtering using AutoQueryModel
    with iterable data structures. Fields are automatically detected from the data structure.

    Args:
        product.id (int, optional): Filter by product ID within nested structure.
        product.name (str, optional): Filter by product name (supports __in, __nin).
        product.price (decimal, optional): Filter by price (supports __gte, __lte).
        product.is_active (bool, optional): Filter by active status.
        product.created_at (str, optional): Filter by creation date (ISO format).
        category_id (int, optional): Filter by category ID.
        category_name (str, optional): Filter by category name.
        ordering (str, optional): Order results by field(s). Use '-' prefix for descending.

    Returns:
        dict: JSON response containing:
            - count (int): Total number of filtered results
            - results (list): List of product dictionaries with nested structure

    Examples:
        Basic request:
            GET /auto/iterable/

        Auto-detected nested field filtering:
            GET /auto/iterable/?product.name__in=Apple,Orange&product.price__lte=800

        Filter by top-level fields:
            GET /auto/iterable/?category_name=Electronics&category_id=1

        Ordering by nested fields:
            GET /auto/iterable/?ordering=-product.price,product.name
    """
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
