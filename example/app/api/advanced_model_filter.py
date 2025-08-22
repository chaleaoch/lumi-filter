"""Basic model filter demo.

GET /model/products

Demonstrates basic usage of custom filter models with explicit field definitions.
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
    """List products with advanced model filter.

    Filterable fields:
      - name (string, supports icontains via name__icontains)
      - price (decimal, supports price__gte and price__lte)
      - is_active (boolean)
      - category_id (integer)
      - category_name (string)

    Examples:
        Basic request:
        ```bash
        curl -X GET "http://localhost:5000/advanced-model/"
        ```

        Filter by product name (case-insensitive contains):
        ```bash
        curl -X GET "http://localhost:5000/advanced-model/?name__icontains=laptop"
        ```

        Filter by price range:
        ```bash
        curl -X GET "http://localhost:5000/advanced-model/?price__gte=100&price__lte=500"
        ```

        Filter by active products only:
        ```bash
        curl -X GET "http://localhost:5000/advanced-model/?is_active=true"
        ```

        Filter by category ID:
        ```bash
        curl -X GET "http://localhost:5000/advanced-model/?category_id=1"
        ```

        Filter by category name:
        ```bash
        curl -X GET "http://localhost:5000/advanced-model/?category_name=Electronics"
        ```

        Combine filters with ordering (descending price):
        ```bash
        curl -X GET "http://localhost:5000/advanced-model/?name__icontains=phone&is_active=true&ordering=-price"
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
    for iterable data structures. Supports filtering by id, name, price, active status,
    and creation date.

    Returns:
        dict: A dictionary containing:
            - count (int): Total number of filtered results
            - results (list): List of product dictionaries with fields:
                id, name, price, is_active, created_at, category_id, category_name

    Examples:
        Basic request without filters:
        ```bash
        curl -X GET "http://localhost:5000/advanced-model/iterable/"
        ```

        Filter by ID:
        ```bash
        curl -X GET "http://localhost:5000/advanced-model/iterable/?id=10"
        ```

        Filter by product name (case-insensitive contains):
        ```bash
        curl -X GET "http://localhost:5000/advanced-model/iterable/?name__icontains=laptop"
        ```

        Filter by price range:
        ```bash
        curl -X GET "http://localhost:5000/advanced-model/iterable/?price__gte=100&price__lte=500"
        ```

        Filter by active products only:
        ```bash
        curl -X GET "http://localhost:5000/advanced-model/iterable/?is_active=true"
        ```

        Filter by creation date range:
        ```bash
        curl -X GET "http://localhost:5000/advanced-model/iterable/?created_at__gte=2024-01-01T00:00:00&created_at__lte=2024-12-31T23:59:59"
        ```

        Complex filtering with multiple conditions:
        ```bash
        curl -X GET "http://localhost:5000/advanced-model/iterable/?name__icontains=phone&price__lte=800&is_active=true"
        ```

        Ordering results (ascending by price):
        ```bash
        curl -X GET "http://localhost:5000/advanced-model/iterable/?ordering=price"
        ```

        Ordering results (descending by creation date):
        ```bash
        curl -X GET "http://localhost:5000/advanced-model/iterable/?ordering=-created_at"
        ```

        Multiple ordering criteria:
        ```bash
        curl -X GET "http://localhost:5000/advanced-model/iterable/?ordering=name,price"
        ```

        Combining filters with ordering:
        ```bash
        curl -X GET "http://localhost:5000/advanced-model/iterable/?is_active=true&price__gte=100&ordering=-price"
        ```
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
