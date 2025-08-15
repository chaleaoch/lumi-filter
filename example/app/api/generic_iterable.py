"""Generic iterable (list[dict]) filtering demo.

GET /generic/users

Demonstrates filtering a plain Python list (no ORM) with nested keys.
Lookups: equality, !, gt, lt, gte, lte, in (substring), iin (case-insensitive substring).

Fields: username, age, profile.country, profile.bio (request args: profile_country, profile_bio)
"""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from lumi_filter.model import Model
from lumi_filter.field import IntField, StrField

bp = Blueprint("generic_iterable", __name__, url_prefix="/generic/users")

USERS = [
    {"username": "alice", "age": 25, "profile": {"country": "US", "bio": "Python engineer"}},
    {"username": "bob", "age": 30, "profile": {"country": "CA", "bio": "Data scientist"}},
    {"username": "charlie", "age": 19, "profile": {"country": "US", "bio": "Rust + Python"}},
]


class FilterUser(Model):
    username = StrField(source="username")
    age = IntField(source="age")
    profile_country = StrField(source="profile.country")
    profile_bio = StrField(source="profile.bio")

    class Meta:
        ordering_extra_field = set()


@bp.get("")
def list_users():
    request_args = {k: v for k, v in request.args.items() if v not in (None, "")}
    data = FilterUser.cls_filter(USERS, request_args)
    data = FilterUser.cls_order(data, request_args)
    data_list = list(data)
    return jsonify({"count": len(data_list), "results": data_list})
