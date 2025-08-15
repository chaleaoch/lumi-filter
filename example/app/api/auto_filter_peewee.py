"""Automatic Peewee field introspection demo.

GET /auto/peewee/products

Uses Meta.schema = Product; all model fields auto filterable.
"""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from lumi_filter.model import Model
from ..db_model import Product

bp = Blueprint("auto_peewee", __name__, url_prefix="/auto/peewee/products")


class AutoFilterProduct(Model):
    class Meta:
        schema = Product
        ordering_extra_field = set()


@bp.get("")
def list_products_auto():
    query = Product.select(
        Product.id,
        Product.name,
        Product.price,
        Product.is_active,
        Product.created_at,
    )
    request_args = {k: v for k, v in request.args.items() if v not in (None, "")}
    filtered = AutoFilterProduct.cls_filter(query, request_args)
    ordered = AutoFilterProduct.cls_order(filtered, request_args)
    data = [p.to_dict() for p in ordered]
    return jsonify({"count": len(data), "results": data})
