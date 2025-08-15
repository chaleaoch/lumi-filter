"""Automatic Pydantic model introspection demo.

GET /auto/pydantic/products

Meta.schema = ProductOut; data source is list[dict].
"""
from __future__ import annotations

import datetime
from flask import Blueprint, jsonify, request

from lumi_filter.model import Model
from ..schema import ProductOut

bp = Blueprint("auto_pydantic", __name__, url_prefix="/auto/pydantic/products")

NOW = datetime.datetime.utcnow()
PRODUCTS_DATA = [
    ProductOut(id=1, name="Alpha", price=1.2, is_active=True, created_at=NOW),
    ProductOut(id=2, name="Beta", price=2.5, is_active=True, created_at=NOW),
    ProductOut(id=3, name="Gamma", price=6.3, is_active=False, created_at=NOW),
]
DATASET = [p.model_dump() for p in PRODUCTS_DATA]


class AutoFilterProductOut(Model):
    class Meta:
        schema = ProductOut
        ordering_extra_field = set()


@bp.get("")
def list_products_pydantic_auto():
    request_args = {k: v for k, v in request.args.items() if v not in (None, "")}
    filtered = AutoFilterProductOut.cls_filter(DATASET, request_args)
    ordered = AutoFilterProductOut.cls_order(filtered, request_args)
    data_list = list(ordered)
    return jsonify({"count": len(data_list), "results": data_list})
