"""Basic model filter demo.

GET /model/products

Demonstrates basic usage of custom filter models with explicit field definitions.
"""

from __future__ import annotations

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
    """List products with filtering capabilities.

    This endpoint demonstrates basic usage of lumi_filter with explicit field definitions.
    Supports filtering by name, price, active status, creation date, category ID, and category name.

    Returns:
        dict: A dictionary containing:
            - count (int): Total number of filtered results
            - results (list): List of product dictionaries with fields:
                id, name, price, is_active, created_at, category_id, category_name

    Examples:
        Basic request without filters:
        ```bash
        curl -X GET "http://localhost:5000/model/"
        ```

        Filter by product name (case-insensitive contains):
        ```bash
        curl -X GET "http://localhost:5000/model/?name=laptop"
        ```

        Filter by price range:
        ```bash
        curl -X GET "http://localhost:5000/model/?price__gte=100&price__lte=500"
        ```

        Filter by active products only:
        ```bash
        curl -X GET "http://localhost:5000/model/?is_active=true"
        ```

        Filter by creation date range:
        ```bash
        curl -X GET "http://localhost:5000/model/?created_at__gte=2024-01-01T00:00:00&created_at__lte=2024-12-31T23:59:59"
        ```

        Filter by category ID:
        ```bash
        curl -X GET "http://localhost:5000/model/?category_id=1"
        ```

        Filter by category name:
        ```bash
        curl -X GET "http://localhost:5000/model/?category_name=Electronics"
        ```

        Complex filtering with multiple conditions:
        ```bash
        curl -X GET "http://localhost:5000/model/?name__icontains=phone&price__lte=800&is_active=true&category_name=Electronics"
        ```

        Ordering results (ascending by price):
        ```bash
        curl -X GET "http://localhost:5000/model/?ordering=price"
        ```

        Ordering results (descending by creation date):
        ```bash
        curl -X GET "http://localhost:5000/model/?ordering=-created_at"
        ```

        Multiple ordering criteria:
        ```bash
        curl -X GET "http://localhost:5000/model/?ordering=category_name,price"
        ```

        Combining filters with ordering:
        ```bash
        curl -X GET "http://localhost:5000/model/?is_active=true&price__gte=100&ordering=-price"
        ```
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
    name = StrField(source="products.name")
    price = DecimalField(source="products.price")
    is_active = BooleanField(source="products.is_active")
    created_at = DateTimeField(source="products.created_at", request_arg_name="created_at")
    id = IntField(source="products.id")
    category_id = IntField(source="category_id", request_arg_name="category_id")
    category_name = StrField(source="category_name", request_arg_name="category_name")


@bp.get("/iterable/")
def list_products_iterable():
    """List products with filtering capabilities using iterable data source.

    This endpoint demonstrates usage of lumi_filter with string-based source definitions
    for iterable data structures. Supports filtering by name, price, active status,
    creation date, category ID, and category name.

    Returns:
        dict: A dictionary containing:
            - count (int): Total number of filtered results
            - results (list): List of product dictionaries with fields:
                id, name, price, is_active, created_at, category_id, category_name

    Examples:
        Basic request without filters:
        ```bash
        curl -X GET "http://localhost:5000/model/iterable/"
        ```

        Filter by product name (case-insensitive contains):
        ```bash
        curl -X GET "http://localhost:5000/model/iterable/?name=laptop"
        ```

        Filter by price range:
        ```bash
        curl -X GET "http://localhost:5000/model/iterable/?price__gte=100&price__lte=500"
        ```

        Filter by active products only:
        ```bash
        curl -X GET "http://localhost:5000/model/iterable/?is_active=true"
        ```

        Filter by creation date range:
        ```bash
        curl -X GET "http://localhost:5000/model/iterable/?created_at__gte=2024-01-01T00:00:00&created_at__lte=2024-12-31T23:59:59"
        ```

        Filter by category ID:
        ```bash
        curl -X GET "http://localhost:5000/model/iterable/?category_id=1"
        ```

        Filter by category name:
        ```bash
        curl -X GET "http://localhost:5000/model/iterable/?category_name=Electronics"
        ```

        Complex filtering with multiple conditions:
        ```bash
        curl -X GET "http://localhost:5000/model/iterable/?name__icontains=phone&price__lte=800&is_active=true&category_name=Electronics"
        ```

        Ordering results (ascending by price):
        ```bash
        curl -X GET "http://localhost:5000/model/iterable/?ordering=price"
        ```

        Ordering results (descending by creation date):
        ```bash
        curl -X GET "http://localhost:5000/model/iterable/?ordering=-created_at"
        ```

        Multiple ordering criteria:
        ```bash
        curl -X GET "http://localhost:5000/model/iterable/?ordering=category_name,price"
        ```

        Combining filters with ordering:
        ```bash
        curl -X GET "http://localhost:5000/model/iterable/?is_active=true&price__gte=100&ordering=-price"
        ```
    """
    # Simulate iterable data structure (could be from JSON, API, etc.)
    products_data = [
        {
            "products": {
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
