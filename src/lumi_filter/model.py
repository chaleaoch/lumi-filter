from typing import Iterable

import peewee
import pydantic

from lumi_filter.backend import IterableBackend, PeeweeBackend
from lumi_filter.field import (
    FilterField,
)
from lumi_filter.map import pd_filter_mapping, pw_filter_mapping


class MetaModel:
    def __init__(self, schema=None, fields=None, extra_field=None):
        self.schema = schema
        self.fields = fields or []
        self.extra_field = extra_field or {}

    def get_filter_fields(self):
        ret = {}
        if self.schema is not None:
            if issubclass(self.schema, peewee.Model):
                for attr_name, pw_field in self.schema._meta.fields.items():
                    if self.fields and attr_name not in self.fields:
                        continue
                    filter_field_class = pw_filter_mapping.get(
                        pw_field.__class__, FilterField
                    )
                    ret[attr_name] = filter_field_class(source=pw_field)
            elif issubclass(self.schema, pydantic.BaseModel):
                stack = [(self.schema.model_fields, "")]
                while stack:
                    model_fields, key_prefix = stack.pop()
                    for key, pydantic_field in model_fields.items():
                        new_key = f"{key_prefix}.{key}" if key_prefix else key
                        if issubclass(pydantic_field.annotation, pydantic.BaseModel):
                            stack.append(
                                (
                                    pydantic_field.annotation.model_fields,
                                    new_key,
                                )
                            )
                        else:
                            if self.fields and new_key not in self.fields:
                                continue
                            filter_field_class = pd_filter_mapping.get(
                                pydantic_field.annotation, FilterField
                            )
                            ret[new_key.replace(".", "_")] = filter_field_class(
                                request_arg_name=new_key, source=new_key
                            )
        for attr_name, field in self.extra_field.items():
            ret[attr_name] = field
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
    def cls_filter(cls, data, request_args):
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
    def cls_order(cls, data, request_args):
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

    def filter(self):
        self.data = self.__class__.cls_filter(self.data, self.request_args)
        return self

    def order(self):
        self.data = self.__class__.cls_order(self.data, self.request_args)
        return self

    def result(self):
        return self.data
