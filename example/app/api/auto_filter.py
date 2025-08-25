"""Automatic Iterable field introspection demo.

This module demonstrates automatic filtering capabilities for both Peewee ORM
queries and iterable data structures using AutoQueryModel. It showcases how
lumi_filter can automatically introspect data structures and generate appropriate
filter fields without manual configuration.

Available Endpoints:
    GET /auto/ - Auto filtering with Peewee ORM queries
    GET /auto/iterable/ - Auto filtering with iterable data structures

Examples:
    Test auto filtering with ORM:
    ```bash
    # Basic filtering
    curl -X GET "http://localhost:5000/auto/?name=Apple"

    # Advanced filtering with lookups
    curl -X GET "http://localhost:5000/auto/?name__icontains=apple&price__gte=1.0"

    # Filter by category
    curl -X GET "http://localhost:5000/auto/?category_name=Fruit&is_active=true"

    # Price range filtering
    curl -X GET "http://localhost:5000/auto/?price__gte=2.0&price__lte=5.0"
    ```

    Test iterable data filtering:
    ```bash
    # Filter nested product data
    curl -X GET "http://localhost:5000/auto/iterable/?product_name=Banana"

    # Filter by product ID
    curl -X GET "http://localhost:5000/auto/iterable/?product_id=1"

    # Filter by category information
    curl -X GET "http://localhost:5000/auto/iterable/?category_name=Berry"
    ```
"""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from lumi_filter.shortcut import AutoQueryModel

from app.db_model import Category, Product

bp = Blueprint("auto_iterable", __name__, url_prefix="/auto/")


@bp.get("")
def list_products_auto():
    """List products using automatic ORM query filtering.

    Demonstrates AutoQueryModel with Peewee ORM queries. The model automatically
    introspects the selected columns and generates appropriate filter fields
    based on the Peewee field types.

    Returns:
        list: List of product dictionaries with fields:
            - id (int): Product ID
            - name (str): Product name
            - price (float): Product price
            - is_active (bool): Product active status
            - created_at (str): Product creation timestamp
            - category_id (int): Associated category ID
            - category_name (str): Associated category name

    Examples:
        Basic filtering (get all products):
        ```bash
        curl -X GET "http://localhost:5000/auto/"
        ```

        Filter by name using __in lookup:
        ```bash
        curl -X GET "http://localhost:5000/auto/?name__in=Apple,Orange"
        ```

        Filter by name (case-insensitive contains):
        ```bash
        curl -X GET "http://localhost:5000/auto/?name__icontains=apple"
        ```

        Filter by price range:
        ```bash
        curl -X GET "http://localhost:5000/auto/?price__gte=2&price__lte=4"
        ```

        Filter by active status:
        ```bash
        curl -X GET "http://localhost:5000/auto/?is_active=true"
        ```

        Filter by inactive status:
        ```bash
        curl -X GET "http://localhost:5000/auto/?is_active=false"
        ```

        Filter by category name:
        ```bash
        curl -X GET "http://localhost:5000/auto/?category_name=Fruit"
        ```

        Filter for citrus fruits:
        ```bash
        curl -X GET "http://localhost:5000/auto/?category_name=Citrus"
        ```

        Complex filtering (active berry products under $3):
        ```bash
        curl -X GET "http://localhost:5000/auto/?is_active=true&price__lte=3&category_name=Berry"
        ```

        Ordering by price (ascending):
        ```bash
        curl -X GET "http://localhost:5000/auto/?ordering=price"
        ```

        Ordering by price (descending):
        ```bash
        curl -X GET "http://localhost:5000/auto/?ordering=-price"
        ```

        Complex filtering with ordering:
        ```bash
        curl -X GET "http://localhost:5000/auto/?name__icontains=berry&is_active=true&price__lt=6.0&ordering=-price"
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
    query = AutoQueryModel(query, request.args).filter().order().result()
    return jsonify(list(query.dicts()))


@bp.get("/iterable/")
def list_products_iterable_auto():
    """List products using automatic iterable data filtering.

    Demonstrates AutoQueryModel with nested dictionary data structures. The model
    automatically introspects the dictionary structure and generates filter fields
    for nested attributes using dot notation (e.g., "product.name" becomes "product_name").

    Returns:
        dict: Response containing:
            - count (int): Total number of filtered results
            - results (list): List of filtered product dictionaries with nested structure:
                - product (dict): Product information
                    - id (int): Product ID
                    - name (str): Product name
                    - price (float): Product price
                    - is_active (bool): Product active status
                    - created_at (str): ISO formatted creation timestamp
                - category_id (int): Associated category ID
                - category_name (str): Associated category name

    Examples:
        Get all products:
        ```bash
        curl -X GET "http://localhost:5000/auto/iterable/"
        ```

        Filter by nested product name:
        ```bash
        curl -X GET "http://localhost:5000/auto/iterable/?product_name=Apple"
        ```

        Filter by nested product properties (price and active status):
        ```bash
        curl -X GET "http://localhost:5000/auto/iterable/?product_price__gte=2.0&product_is_active=true"
        ```

        Filter by category information:
        ```bash
        curl -X GET "http://localhost:5000/auto/iterable/?category_name=Berry"
        ```

        Filter by product ID:
        ```bash
        curl -X GET "http://localhost:5000/auto/iterable/?product_id=1"
        ```

        Complex nested filtering:
        ```bash
        curl -X GET "http://localhost:5000/auto/iterable/?product_name__icontains=fruit&category_id=1"
        ```

        Filter by nested product price range:
        ```bash
        curl -X GET "http://localhost:5000/auto/iterable/?product_price__gte=1.0&product_price__lte=5.0"
        ```

        Complex filtering with multiple nested conditions:
        ```bash
        curl -X GET "http://localhost:5000/auto/iterable/?product_is_active=true&product_price__lt=4.0&category_name=Tropical"
        ```
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
