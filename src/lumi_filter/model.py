import datetime
import decimal
from typing import Iterable

import peewee
import pydantic

from lumi_filter.backend import IterableBackend, PeeweeBackend
from lumi_filter.field import (
    BooleanField,
    DateField,
    DateTimeField,
    DecimalField,
    FilterField,
    IntField,
    StrField,
)
from lumi_filter.util import ClassHierarchyMapping


class MetaModel:
    PW_FILTER_MAP = {
        peewee.CharField: StrField,
        peewee.TextField: StrField,
        peewee.IntegerField: IntField,
        peewee.DecimalField: DecimalField,
        peewee.BooleanField: BooleanField,
        peewee.DateField: DateField,
        peewee.DateTimeField: DateTimeField,
    }
    PD_FILTER_MAP = {
        str: StrField,
        int: IntField,
        decimal.Decimal: DecimalField,
        bool: BooleanField,
        datetime.date: DateField,
        datetime.datetime: DateTimeField,
    }

    def __init__(self, schema=None):
        self.schema = schema

    def get_filter_fields(self):
        ret = {}
        pw_filter_mapping = ClassHierarchyMapping(self.PW_FILTER_MAP)
        pd_filter_mapping = ClassHierarchyMapping(self.PD_FILTER_MAP)
        if self.schema is not None:
            if issubclass(self.schema, peewee.Model):
                for attr_name, pw_field in self.schema._meta.fields.items():
                    filter_field_class = pw_filter_mapping.get(
                        pw_field.__class__, FilterField
                    )
                    ret[attr_name] = filter_field_class(source=pw_field)
            elif issubclass(self.schema, pydantic.BaseModel):
                for attr_name, pydantic_field in self.schema.model_fields.items():
                    filter_field_class = pd_filter_mapping.get(
                        pydantic_field.annotation, FilterField
                    )
                    ret[attr_name] = filter_field_class()
        return ret


class ModelMeta(type):
    def __new__(cls, name, bases, attrs):
        supported_query_key_field_dict = {}
        meta_options = {}
        meta = attrs.pop("Meta", None)
        if meta:
            for k, v in meta.__dict__.items():
                if not k.startswith("_"):
                    meta_options[k] = v
        meta_model = MetaModel(**meta_options)
        # attrs have higher priority
        attrs = meta_model.get_filter_fields() | attrs
        for field_name, field in attrs.items():
            if isinstance(field, FilterField):
                field.name = field_name
                if field.request_arg_name is None:
                    field.request_arg_name = field_name
                if field.source is None:
                    field.source = field_name
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


class Model(metaclass=ModelMeta):
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
