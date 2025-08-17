"""Pydantic schema-based filter demo.

GET /pydantic/products

Demonstrates using a Pydantic model as schema for automatic field introspection
with AutoQueryModel. The Meta.schema references a Pydantic model instead of
a Peewee model, allowing for type-safe filtering based on Pydantic field definitions.
"""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from lumi_filter.model import Model

from ..db_model import Category, Product
from ..schema import ProductListQuery, ProductOut

bp = Blueprint("pydantic_filter", __name__, url_prefix="/pydantic/")


class ProductPydanticFilter(Model):
    """Filter model using Pydantic schema for field introspection."""

    class Meta:
        schema = ProductOut  # Use Pydantic model as schema


class ProductQueryFilter(Model):
    """Filter model using Pydantic query schema for field introspection."""

    class Meta:
        schema = ProductListQuery  # Use Pydantic query model as schema


@bp.get("")
def list_products_pydantic_schema():
    """Filter products using Pydantic model schema for field definitions.

    Examples:
    - GET /pydantic/products?name__icontains=Apple
    - GET /pydantic/products?price__gte=2.0&price__lte=5.0
    - GET /pydantic/products?is_active=true
    - GET /pydantic/products?id__in=1,2,3
    - GET /pydantic/products?ordering=price,-created_at
    - GET /pydantic/products?category_name__istartswith=Fruit
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

    # Use Pydantic schema-based filter
    filter_model = ProductPydanticFilter(query, request.args)
    filtered_query = filter_model.filter().order().result()

    return jsonify(
        {
            "count": filtered_query.count(),
            "results": list(filtered_query.dicts()),
            "schema_info": {
                "model": "ProductOut",
                "fields": list(ProductOut.model_fields.keys()),
                "field_types": {
                    field_name: str(field_info.annotation) for field_name, field_info in ProductOut.model_fields.items()
                },
            },
        }
    )


@bp.get("/query")
def list_products_query_schema():
    """Filter products using Pydantic query schema.

    This endpoint uses ProductListQuery which defines specific query parameters
    with validation constraints.

    Examples:
    - GET /pydantic/products/query?name=Apple
    - GET /pydantic/products/query?price__gte=2.0&price__lte=5.0
    - GET /pydantic/products/query?is_active=true
    - GET /pydantic/products/query?ordering=price
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

    # Use Pydantic query schema-based filter
    filter_model = ProductQueryFilter(query, request.args)
    filtered_query = filter_model.filter().order().result()

    return jsonify(
        {
            "count": filtered_query.count(),
            "results": list(filtered_query.dicts()),
            "query_schema_info": {
                "model": "ProductListQuery",
                "fields": list(ProductListQuery.model_fields.keys()),
                "field_types": {
                    field_name: str(field_info.annotation)
                    for field_name, field_info in ProductListQuery.model_fields.items()
                },
            },
        }
    )


@bp.get("/validated")
def list_products_with_validation():
    """Filter products with Pydantic validation.

    This endpoint validates query parameters against the Pydantic schema
    before applying filters.

    Examples:
    - GET /pydantic/products/validated?name=Apple&price__gte=1.0
    - GET /pydantic/products/validated?is_active=true&ordering=-price
    """
    try:
        # Validate query parameters using Pydantic schema
        validated_params = ProductListQuery.model_validate(
            {k: v for k, v in request.args.items() if k in ProductListQuery.model_fields}
        )

        query = Product.select(
            Product.id,
            Product.name,
            Product.price,
            Product.is_active,
            Product.created_at,
            Category.id.alias("category_id"),
            Category.name.alias("category_name"),
        ).join(Category)

        # Use validated parameters for filtering
        filter_model = ProductQueryFilter(query, request.args)
        filtered_query = filter_model.filter().order().result()

        return jsonify(
            {
                "count": filtered_query.count(),
                "results": list(filtered_query.dicts()),
                "validated_params": validated_params.model_dump(exclude_none=True),
                "validation": "success",
            }
        )

    except Exception as e:
        return jsonify(
            {
                "error": "Validation failed",
                "details": str(e),
                "valid_fields": list(ProductListQuery.model_fields.keys()),
            }
        ), 400
