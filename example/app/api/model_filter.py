"""Basic model filter demo.

GET /model/products

Demonstrates basic usage of custom filter models with explicit field definitions.
"""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from lumi_filter.field import BooleanField, DateTimeField, DecimalField, IntField, StrField
from lumi_filter.model import Model

from ..db_model import Category, Product
from ..filter_model import FilterProduct

bp = Blueprint("model_filter", __name__, url_prefix="/model/")


class FilterProduct(Model):
    name = StrField(source=Product.name)
    price = DecimalField(source=Product.price)
    is_active = BooleanField(source=Product.is_active)
    created_at = DateTimeField(source=Product.created_at)
    id = IntField(source=Product.id)
    category_id = IntField(source=Product.category)
    category_name = StrField(source=Category.name)


@bp.get("")
def list_products_basic():
    """Filter products using a custom filter model.

    Examples:
    - GET /model/products?name__in=Laptop
    - GET /model/products?price__gte=20&price__lte=100
    - GET /model/products?is_active=true
    - GET /model/products?category_id=1
    - GET /model/products?ordering=price,-created_at
    - GET /model/products?name__istartswith=L
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

    # Use the predefined filter model
    filter_model = FilterProduct(query, request.args)
    filtered_query = filter_model.filter().order().result()

    return jsonify({"count": filtered_query.count(), "results": list(filtered_query.dicts())})


@bp.get("/search")
def search_products():
    """Advanced search with multiple field matching.

    Examples:
    - GET /model/products/search?q=laptop
    - GET /model/products/search?q=electronics&fields=name,category_name
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

    search_term = request.args.get("q", "")
    search_fields = request.args.get("fields", "name,category_name").split(",")

    # Build search query
    search_args = {}
    if search_term:
        for field in search_fields:
            if field in ["name", "category_name"]:
                search_args[f"{field}__icontains"] = search_term

    # Combine with other filters
    combined_args = dict(request.args)
    combined_args.update(search_args)

    filter_model = FilterProduct(query, combined_args)
    filtered_query = filter_model.filter().order().result()

    return jsonify(
        {
            "search_term": search_term,
            "search_fields": search_fields,
            "count": filtered_query.count(),
            "results": list(filtered_query.dicts()),
        }
    )


@bp.get("/categories/<int:category_id>")
def list_products_by_category(category_id: int):
    """Filter products by category with additional filters.

    Examples:
    - GET /model/products/categories/1?price__lte=100
    - GET /model/products/categories/1?is_active=true&ordering=-price
    """
    query = (
        Product.select(
            Product.id,
            Product.name,
            Product.price,
            Product.is_active,
            Product.created_at,
            Category.id.alias("category_id"),
            Category.name.alias("category_name"),
        )
        .join(Category)
        .where(Category.id == category_id)
    )

    filter_model = FilterProduct(query, request.args)
    filtered_query = filter_model.filter().order().result()

    # Get category info
    try:
        category = Category.get_by_id(category_id)
        category_info = {"id": category.id, "name": category.name}
    except Category.DoesNotExist:
        category_info = None

    return jsonify(
        {
            "category": category_info,
            "count": filtered_query.count(),
            "results": list(filtered_query.dicts()),
            "available_filters": {
                "name": "string filters (icontains, istartswith, etc.)",
                "price": "number filters (gte, lte, gt, lt)",
                "is_active": "boolean filter",
                "created_at": "datetime filters",
            },
        }
    )
