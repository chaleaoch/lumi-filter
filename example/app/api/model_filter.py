"""Basic model filter demo.

This module demonstrates basic usage of custom filter models with explicit field definitions
for both database queries and iterable data structures.

Example:
    GET /model/ - Filter products using explicit field definitions
    GET /model/iterable/ - Filter iterable data using string-based source definitions
"""

from flask import Blueprint, jsonify, request
from lumi_filter.field import BooleanField, DateTimeField, DecimalField, IntField, StrField
from lumi_filter.model import Model

from ..db_model import Category, Product

bp = Blueprint("model_filter", __name__, url_prefix="/model/")


class FilterProduct(Model):
    name = StrField(source=Product.name)
    price = DecimalField(source=Product.price)
    is_active = BooleanField(source=Product.is_active)
    created_at = DateTimeField(source=Product.created_at, request_arg_name="created_at")
    id = IntField(source=Product.id)
    category_id = IntField(source=Product.category, request_arg_name="category_id")
    category_name = StrField(source=Category.name, request_arg_name="category_name")


@bp.get("")
def list_products_basic():
    """List products with filtering capabilities using explicit field definitions.

    This endpoint demonstrates basic usage of lumi_filter with explicit field definitions.
    Each field is explicitly defined with its source and filtering capabilities.

    Args:
        name (str, optional): Filter by product name (supports __in, __nin).
        price (decimal, optional): Filter by price (supports __gte, __lte).
        is_active (bool, optional): Filter by active status.
        created_at (datetime, optional): Filter by creation date (supports __gte, __lte).
        id (int, optional): Filter by product ID.
        category_id (int, optional): Filter by category ID.
        category_name (str, optional): Filter by category name.
        ordering (str, optional): Order results by field(s). Use '-' prefix for descending.

    Returns:
        dict: JSON response containing:
            - count (int): Total number of filtered results
            - results (list): List of product dictionaries with fields:
                id, name, price, is_active, created_at, category_id, category_name

    Examples:
        Basic request without filters:
            GET /model/

        Filter by product name (case-insensitive contains):
            GET /model/?name__in=Apple,Orange

        Filter by price range:
            GET /model/?price__gte=100&price__lte=500

        Filter by active products only:
            GET /model/?is_active=true

        Filter by creation date range:
            GET /model/?created_at__gte=2024-01-01T00:00:00&created_at__lte=2024-12-31T23:59:59

        Filter by category ID:
            GET /model/?category_id=1

        Filter by category name:
            GET /model/?category_name=Electronics

        Complex filtering with multiple conditions:
            GET /model/?name__in=Apple,Orange&price__lte=800&is_active=true&category_name=Electronics

        Ordering results (ascending by price):
            GET /model/?ordering=price

        Ordering results (descending by creation date):
            GET /model/?ordering=-created_at

        Multiple ordering criteria:
            GET /model/?ordering=category_name,price

        Combining filters with ordering:
            GET /model/?is_active=true&price__gte=100&ordering=-price
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

    filter_model = FilterProduct(query, request.args)
    filtered_query = filter_model.filter().order().result()

    return jsonify({"count": filtered_query.count(), "results": list(filtered_query.dicts())})


class FilterIterableProduct(Model):
    name = StrField(source="product.name")
    price = DecimalField(source="product.price")
    is_active = BooleanField(source="product.is_active")
    created_at = DateTimeField(source="product.created_at", request_arg_name="created_at")
    id = IntField(source="product.id")
    category_id = IntField(source="category_id", request_arg_name="category_id")
    category_name = StrField(source="category_name", request_arg_name="category_name")


@bp.get("/iterable/")
def list_products_iterable():
    """List products with filtering capabilities using iterable data source.

    This endpoint demonstrates usage of lumi_filter with string-based source definitions
    for iterable data structures. Each field source is defined as a string path.

    Args:
        name (str, optional): Filter by product name (supports __in, __nin).
        price (decimal, optional): Filter by price (supports __gte, __lte).
        is_active (bool, optional): Filter by active status.
        created_at (datetime, optional): Filter by creation date (supports __gte, __lte).
        id (int, optional): Filter by product ID.
        category_id (int, optional): Filter by category ID.
        category_name (str, optional): Filter by category name.
        ordering (str, optional): Order results by field(s). Use '-' prefix for descending.

    Returns:
        dict: JSON response containing:
            - count (int): Total number of filtered results
            - results (list): List of product dictionaries with nested structure

    Examples:
        Basic request without filters:
            GET /model/iterable/

        Filter by product name (case-insensitive contains):
            GET /model/iterable/?name__in=Apple,Orange

        Filter by price range:
            GET /model/iterable/?price__gte=100&price__lte=500

        Filter by active products only:
            GET /model/iterable/?is_active=true

        Filter by creation date range:
            GET /model/iterable/?created_at__gte=2024-01-01T00:00:00&created_at__lte=2024-12-31T23:59:59

        Filter by category ID:
            GET /model/iterable/?category_id=1

        Filter by category name:
            GET /model/iterable/?category_name=Electronics

        Complex filtering with multiple conditions:
            GET /model/iterable/?name__in=Apple,Orange&price__lte=800&is_active=true&category_name=Electronics

        Ordering results (ascending by price):
            GET /model/iterable/?ordering=price

        Ordering results (descending by creation date):
            GET /model/iterable/?ordering=-created_at

        Multiple ordering criteria:
            GET /model/iterable/?ordering=category_name,price

        Combining filters with ordering:
            GET /model/iterable/?is_active=true&price__gte=100&ordering=-price
    """
    # Simulate iterable data structure (could be from JSON, API, etc.)
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

    filter_model = FilterIterableProduct(products_data, request.args)
    filtered_data = filter_model.filter().order().result()

    return jsonify({"count": len(filtered_data), "results": filtered_data})
