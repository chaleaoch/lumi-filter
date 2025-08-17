from flask import Blueprint, jsonify, request
from lumi_filter.field import BooleanField, DateTimeField, DecimalField, IntField, StrField
from lumi_filter.model import Model

from ..db_model import Category, Product

bp = Blueprint("peewee_filter", __name__, url_prefix="/peewee/")


class AdvancedProductFilter(Model):
    """Advanced filter for Peewee queries with aggregations."""

    id = IntField(source=Product.id)
    name = StrField(source=Product.name)
    price = DecimalField(source=Product.price)
    is_active = BooleanField(source=Product.is_active)
    created_at = DateTimeField(source=Product.created_at)
    category_id = IntField(source=Product.category)
    category_name = StrField(source=Category.name)

    class Meta:
        ordering_fields = ["id", "name", "price", "created_at", "category_name"]


@bp.get("")
def list_products_peewee():
    query = Product.select(
        Product.id,
        Product.name,
        Product.price,
        Product.is_active,
        Product.created_at,
        Category.id.alias("category_id"),
        Category.name.alias("category_name"),
    ).join(Category)

    filter_model = AdvancedProductFilter(query, request.args)
    filtered_query = filter_model.filter().order().result()

    return jsonify(
        {
            "results": list(filtered_query.dicts()),
            "sql_query": str(filtered_query),  # Show generated SQL for debugging
        }
    )


@bp.get("/cls")
def list_products_peewee_cls():
    """Use class method for direct filtering."""
    query = Product.select(
        Product.id,
        Product.name,
        Product.price,
        Product.is_active,
        Product.created_at,
        Category.id.alias("category_id"),
        Category.name.alias("category_name"),
    ).join(Category)

    # Use class method directly
    filtered_query = AdvancedProductFilter.cls_filter(query, request.args)

    return jsonify(
        {
            "results": list(filtered_query.dicts()),
            "sql_query": str(filtered_query),  # Show generated SQL for debugging
            "method": "cls_filter",
        }
    )
