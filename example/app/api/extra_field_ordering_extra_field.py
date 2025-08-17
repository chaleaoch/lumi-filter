"""Extra field ordering and additional field demo.

GET /extra/products

Demonstrates how to add extra fields to a filter model and use custom ordering.
"""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from lumi_filter.field import BooleanField, DateTimeField, DecimalField, IntField, StrField
from lumi_filter.model import Model

from ..db_model import Category, Product

bp = Blueprint("extra_fields", __name__, url_prefix="/extra/")


class ProductFilterWithExtras(Model):
    """Extended filter model with extra fields and custom ordering."""

    # Basic product fields
    id = IntField(source=Product.id)
    name = StrField(source=Product.name)
    price = DecimalField(source=Product.price)
    is_active = BooleanField(source=Product.is_active)
    created_at = DateTimeField(source=Product.created_at)

    # Category fields (joined)
    category_id = IntField(source=Product.category)
    category_name = StrField(source=Category.name)

    # Extra computed fields
    price_range = StrField(request_arg_name="price_range")  # Custom logic field

    class Meta:
        # Custom ordering options
        ordering_fields = ["id", "name", "price", "created_at", "category_name", "price_range"]
        default_ordering = ["-created_at", "name"]


@bp.get("")
def list_products_with_extras():
    """Filter products with extra fields and custom ordering.

    Examples:
    - GET /extra/products?price_range=budget (< 50)
    - GET /extra/products?price_range=mid (50-200)
    - GET /extra/products?price_range=premium (> 200)
    - GET /extra/products?name__in=Laptop&ordering=price,-created_at
    - GET /extra/products?category_name=Electronics&ordering=name
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

    # Initialize filter with extra logic
    filter_model = ProductFilterWithExtras(query, request.args)

    # Apply custom price range logic
    price_range = request.args.get("price_range")
    if price_range == "budget":
        query = query.where(Product.price < 50)
    elif price_range == "mid":
        query = query.where((Product.price >= 50) & (Product.price <= 200))
    elif price_range == "premium":
        query = query.where(Product.price > 200)

    # Apply filters and ordering
    filtered_query = filter_model.filter().order().result()

    # Add computed fields to response
    results = []
    for item in filtered_query.dicts():
        # Add price range classification
        price = float(item["price"])
        if price < 50:
            item["price_range"] = "budget"
        elif price <= 200:
            item["price_range"] = "mid"
        else:
            item["price_range"] = "premium"

        # Add formatted price
        item["price_formatted"] = f"${price:.2f}"

        results.append(item)

    return jsonify(
        {
            "count": len(results),
            "results": results,
            "available_price_ranges": ["budget", "mid", "premium"],
            "available_ordering": ProductFilterWithExtras.Meta.ordering_fields,
        }
    )


@bp.get("/stats")
def product_stats():
    """Get product statistics with filtering.

    Examples:
    - GET /extra/products/stats?category_name=Electronics
    - GET /extra/products/stats?is_active=true
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

    filter_model = ProductFilterWithExtras(query, request.args)
    filtered_query = filter_model.filter().result()

    # Calculate statistics
    products = list(filtered_query.dicts())
    if not products:
        return jsonify({"count": 0, "stats": None})

    prices = [float(p["price"]) for p in products]
    stats = {
        "total_products": len(products),
        "active_products": sum(1 for p in products if p["is_active"]),
        "price_stats": {
            "min": min(prices),
            "max": max(prices),
            "avg": sum(prices) / len(prices),
        },
        "categories": list(set(p["category_name"] for p in products)),
    }

    return jsonify(
        {
            "count": len(products),
            "stats": stats,
            "products": products[:10],  # First 10 products as sample
        }
    )
