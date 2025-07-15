from typing import Iterable

import peewee

from lumi_filter.backend import IterableBackend, PeeweeBackend
from lumi_filter.field import FilterField


class Meta(type):
    def __new__(cls, name, bases, attrs):
        supported_query_key_field_dict = {}
        for field_name, field in attrs.items():
            if isinstance(field, FilterField):
                field.name = field_name
                if field.request_arg_name is None:
                    field.request_arg_name = field_name
                if "__" in field.request_arg_name:
                    raise ValueError(
                        f"field.request_arg_name of {field_name} cannot contain '__' because this syntax is reserved for lookups."
                    )
                for lookup_expr in field.SUPPORTED_LOOKUP_EXPR:
                    if lookup_expr == "":
                        supported_query_key = field.request_arg_name
                    elif lookup_expr == "!":
                        supported_query_key = f"{field.request_arg_name}{lookup_expr}"
                    else:
                        supported_query_key = f"{field.request_arg_name}__{lookup_expr}"
                    supported_query_key_field_dict[supported_query_key] = {
                        "field": field,
                        "lookup_expr": lookup_expr,
                    }

        attrs["__supported_query_key_field_dict__"] = supported_query_key_field_dict
        return super().__new__(cls, name, bases, attrs)


class Model(metaclass=Meta):
    def __init__(self, data, request_args, *args, **kwargs):
        self.data = data
        self.request_args = request_args

    @classmethod
    def filter(cls, data, request_args):
        if isinstance(data, peewee.ModelSelect):
            Backend = PeeweeBackend
        elif isinstance(data, Iterable):
            Backend = IterableBackend
        for req_field_name, req_value in request_args.items():
            if req_field_name not in cls.__supported_query_key_field_dict__:
                continue
            field = cls.__supported_query_key_field_dict__[req_field_name]["field"]
            lookup_expr = cls.__supported_query_key_field_dict__[req_field_name][
                "lookup_expr"
            ]
            req_value, ok = field.parse_value(req_value)
            if not ok:
                continue
            data = Backend.filter(data, field.source, req_value, lookup_expr)
        return data

    @classmethod
    def order(cls, data, request_args):
        if isinstance(data, peewee.ModelSelect):
            Backend = PeeweeBackend
        elif isinstance(data, Iterable):
            Backend = IterableBackend

        ordering = request_args.get("ordering", "")
        if not ordering:
            return data
        ordering_list = ordering.split(",")
        for req_field_name in ordering_list:
            is_negative = False
            if req_field_name.startswith("-"):
                is_negative = True
                req_field_name = req_field_name[1:]
            data = Backend.order(data, req_field_name, is_negative)
        return data
