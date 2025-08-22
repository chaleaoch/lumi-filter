"""Advanced model filter demo.

This module demonstrates advanced usage of custom filter models with explicit field definitions
and schema-based field introspection capabilities.

Example:
    GET /advanced-model/ - List products with advanced filtering
    GET /advanced-model/iterable/ - List products using iterable data source
"""

from flask import Blueprint, jsonify, request
from lumi_filter.field import BooleanField, DateTimeField, DecimalField, IntField, StrField
from lumi_filter.model import Model

from app.schema import CategoryPydantic

from ..db_model import Category, Product

bp = Blueprint("advanced_model_filter", __name__, url_prefix="/advanced-model/")


class AdvancedFilterProduct(Model):
    category_id = IntField(source=Product.category, request_arg_name="category_id")
    category_name = StrField(source=Category.name, request_arg_name="category_name")

    class Meta:
        schema = Product
        fields = ["name", "price", "is_active"]


@bp.get("")
def list_products_basic():
    """List products with advanced model filter capabilities.

    This endpoint demonstrates advanced usage of lumi_filter with schema-based field
    introspection combined with explicit field definitions.

    Args:
        name (str, optional): Filter by product name (supports __in, __nin).
        price (decimal, optional): Filter by price (supports __gte, __lte).
        is_active (bool, optional): Filter by active status.
        category_id (int, optional): Filter by category ID.
        category_name (str, optional): Filter by category name.
        ordering (str, optional): Order results by field(s). Use '-' prefix for descending.

    Returns:
        dict: JSON response containing:
            - count (int): Total number of filtered results
            - results (list): List of product dictionaries with fields:
                id, name, price, is_active, created_at, category_id, category_name

    Examples:
        Basic request:
            GET /advanced-model/

        Filter by product name (case-insensitive contains):
            GET /advanced-model/?name__in=Apple,Orange

        Filter by price range:
            GET /advanced-model/?price__gte=100&price__lte=500

        Filter by active products only:
            GET /advanced-model/?is_active=true

        Filter by category ID:
            GET /advanced-model/?category_id=1

        Filter by category name:
            GET /advanced-model/?category_name=Electronics

        Combine filters with ordering (descending price):
            GET /advanced-model/?name__in=Apple,Orange&is_active=true&ordering=-price
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

    filter_model = AdvancedFilterProduct(query, request.args)
    filtered_query = filter_model.filter().order().result()

    return jsonify({"count": filtered_query.count(), "results": list(filtered_query.dicts())})


class AdvancedFilterIterableProduct(Model):
    id = IntField(source="product.id")
    product_name = StrField(source="product.name", request_arg_name="product_name")
    price = DecimalField(source="product.price")
    is_active = BooleanField(source="product.is_active")
    created_at = DateTimeField(source="product.created_at", request_arg_name="created_at")

    class Meta:
        schema = CategoryPydantic


@bp.get("/iterable/")
def list_products_iterable():
    """List products with filtering capabilities using iterable data source.

    This endpoint demonstrates usage of lumi_filter with string-based source definitions
    for iterable data structures and schema-based field introspection.

    Args:
        id (int, optional): Filter by product ID.
        product_name (str, optional): Filter by product name (supports __in, __nin).
        price (decimal, optional): Filter by price (supports __gte, __lte).
        is_active (bool, optional): Filter by active status.
        created_at (datetime, optional): Filter by creation date (supports __gte, __lte).
        category_id (int, optional): Filter by category ID.
        category_name (str, optional): Filter by category name.
        ordering (str, optional): Order results by field(s). Use '-' prefix for descending.

    Returns:
        dict: JSON response containing:
            - count (int): Total number of filtered results
            - results (list): List of product dictionaries with nested structure

    Examples:
        Basic request without filters:
            GET /advanced-model/iterable/

        Filter by ID:
            GET /advanced-model/iterable/?id=10

        Filter by product name (case-insensitive contains):
            GET /advanced-model/iterable/?name__in=Apple,Orange

        Filter by price range:
            GET /advanced-model/iterable/?price__gte=100&price__lte=500

        Filter by active products only:
            GET /advanced-model/iterable/?is_active=true

        Filter by creation date range:
            GET /advanced-model/iterable/?created_at__gte=2024-01-01T00:00:00&created_at__lte=2024-12-31T23:59:59

        Complex filtering with multiple conditions:
            GET /advanced-model/iterable/?name__in=Apple,Orange&price__lte=800&is_active=true

        Ordering results (ascending by price):
            GET /advanced-model/iterable/?ordering=price

        Ordering results (descending by creation date):
            GET /advanced-model/iterable/?ordering=-created_at

        Multiple ordering criteria:
            GET /advanced-model/iterable/?ordering=name,price

        Combining filters with ordering:
            GET /advanced-model/iterable/?is_active=true&price__gte=100&ordering=-price
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

    filter_model = AdvancedFilterIterableProduct(products_data, request.args)
    filtered_data = filter_model.filter().order().result()

    return jsonify({"count": len(filtered_data), "results": filtered_data})
