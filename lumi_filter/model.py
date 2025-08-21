"""Model classes for filtering and ordering data.

This module contains the core model classes that provide a unified interface
for filtering and ordering different types of data sources including
Peewee ORM queries, Pydantic models, and iterable data structures.
"""

from typing import Iterable

import peewee
import pydantic

from lumi_filter.backend import IterableBackend, PeeweeBackend
from lumi_filter.field import FilterField
from lumi_filter.map import pd_filter_mapping, pw_filter_mapping


class MetaModel:
    """Configuration class for model metadata.

    This class handles the configuration and processing of model metadata,
    including schema introspection and field mapping for both Peewee and
    Pydantic models.

    :param schema: The model schema (Peewee or Pydantic model class)
    :param fields: List of specific fields to include
    :type fields: list or None
    :param extra_field: Additional custom filter fields
    :type extra_field: dict or None
    :param ordering_extra_field: Extra fields allowed for ordering
    :type ordering_extra_field: set or None
    """

    def __init__(self, schema=None, fields=None, extra_field=None):
        self.schema = schema
        self.fields = fields or []
        self.extra_field = extra_field or {}

    def get_filter_fields(self):
        """Generate filter fields from schema and extra fields.

        :return: Dictionary mapping field names to filter field instances
        :rtype: dict
        """
        ret = {}

        if self.schema is not None:
            if self._is_peewee_model(self.schema):
                ret.update(self._process_peewee_fields())
            elif self._is_pydantic_model(self.schema):
                ret.update(self._process_pydantic_fields())

        # Extra fields override schema fields
        ret.update(self.extra_field)
        return ret

    def _is_peewee_model(self, schema):
        """Check if schema is a Peewee model.

        :param schema: The schema to check
        :return: True if schema is a Peewee model class
        :rtype: bool
        """
        return isinstance(schema, type) and issubclass(schema, peewee.Model)

    def _is_pydantic_model(self, schema):
        """Check if schema is a Pydantic model.

        :param schema: The schema to check
        :return: True if schema is a Pydantic model class
        :rtype: bool
        """
        return isinstance(schema, type) and issubclass(schema, pydantic.BaseModel)

    def _process_peewee_fields(self):
        """Process Peewee model fields into filter fields.

        :return: Dictionary mapping field names to filter field instances
        :rtype: dict
        """
        ret = {}
        for attr_name, pw_field in self.schema._meta.fields.items():
            if self.fields and attr_name not in self.fields:
                continue

            filter_field_class = pw_filter_mapping.get(pw_field.__class__, FilterField)
            ret[attr_name] = filter_field_class(source=pw_field)
        return ret

    def _process_pydantic_fields(self):
        """Process Pydantic model fields into filter fields with nested support.

        :return: Dictionary mapping field names to filter field instances
        :rtype: dict
        """
        ret = {}
        stack = [(self.schema.model_fields, "")]

        while stack:
            model_fields, key_prefix = stack.pop()
            for key, pydantic_field in model_fields.items():
                new_key = f"{key_prefix}.{key}" if key_prefix else key

                if self._is_nested_pydantic_model(pydantic_field):
                    stack.append(
                        (
                            pydantic_field.annotation.model_fields,
                            new_key,
                        )
                    )
                else:
                    if self.fields and new_key not in self.fields:
                        continue

                    filter_field_class = pd_filter_mapping.get(pydantic_field.annotation, FilterField)
                    field_name = new_key.replace(".", "_")
                    ret[field_name] = filter_field_class(request_arg_name=new_key, source=new_key)
        return ret

    def _is_nested_pydantic_model(self, pydantic_field):
        """Check if a Pydantic field is a nested model.

        :param pydantic_field: The Pydantic field to check
        :return: True if field represents a nested Pydantic model
        :rtype: bool
        """
        return isinstance(pydantic_field.annotation, type) and issubclass(pydantic_field.annotation, pydantic.BaseModel)


class ModelMeta(type):
    """Metaclass for creating filter models with field validation.

    This metaclass automatically processes model definitions and creates
    the necessary internal structures for filtering and validation.
    It handles schema introspection, field mapping, and validation setup.
    """

    def __new__(cls, name, bases, attrs):
        supported_query_key_field_dict = {}
        meta_options = cls._extract_meta_options(attrs)
        meta_model = MetaModel(**meta_options)

        # Merge schema fields with explicit attrs (attrs have priority)
        attrs = meta_model.get_filter_fields() | attrs

        filter_fields = []
        filter_field_map = {}
        source_types = set()

        for field_name, field in attrs.items():
            if isinstance(field, FilterField):
                cls._configure_field(field, field_name)
                cls._validate_field_name(field, field_name)
                filter_field_map[field_name] = field
                filter_fields.append(field)  # it should be useful in the future
                source_types.add(cls._get_source_type(field))
                field_lookup_mappings = cls._get_lookup_expressions(field)
                supported_query_key_field_dict.update(field_lookup_mappings)

        cls._validate_source_type_consistency(source_types, name)

        attrs["__supported_query_key_field_dict__"] = supported_query_key_field_dict
        attrs["__ordering_field_map__"] = filter_field_map

        return super().__new__(cls, name, bases, attrs)

    @staticmethod
    def _get_lookup_expressions(field):
        """Generate lookup expressions mapping for a field."""
        lookup_mappings = {}

        for lookup_expr in field.SUPPORTED_LOOKUP_EXPR:
            if lookup_expr == "":
                supported_query_key = field.request_arg_name
            elif lookup_expr == "!":
                supported_query_key = f"{field.request_arg_name}{lookup_expr}"
            else:
                supported_query_key = f"{field.request_arg_name}__{lookup_expr}"

            lookup_mappings[supported_query_key] = {
                "field": field,
                "lookup_expr": lookup_expr,
            }

        return lookup_mappings

    @staticmethod
    def _extract_meta_options(attrs):
        """Extract Meta class options."""
        meta_options = {}
        meta = attrs.pop("Meta", None)
        if meta:
            for k, v in meta.__dict__.items():
                if not k.startswith("_"):
                    meta_options[k] = v
        return meta_options

    @staticmethod
    def _configure_field(field, field_name):
        """Configure field with default values."""
        if field.request_arg_name is None:
            field.request_arg_name = field_name
        if field.source is None:
            field.source = field_name

    @staticmethod
    def _validate_field_name(field, field_name):
        """Validate field request_arg_name doesn't contain reserved syntax."""
        if "__" in field.request_arg_name:
            raise ValueError(
                f"field.request_arg_name of {field_name} cannot contain '__' "
                "because this syntax is reserved for lookups."
            )

    @staticmethod
    def _get_source_type(field):
        """Determine the source type of a field."""
        if isinstance(field.source, str):
            return "string"
        elif isinstance(field.source, peewee.Field):
            return "peewee_field"
        else:
            return "other"

    @staticmethod
    def _validate_source_type_consistency(source_types, model_name):
        """Validate that all fields have consistent source types."""
        if len(source_types) > 1:
            raise ValueError(
                f"Model {model_name} has fields with different source types: "
                f"{', '.join(source_types)}. All fields must have the same source type."
            )


class Model(metaclass=ModelMeta):
    """Base model class for filtering and ordering data.

    This class provides a unified interface for applying filters and ordering
    to different types of data sources including Peewee ORM queries,
    Pydantic models, and iterable data structures.

    :param data: The data to filter and order
    :param request_args: Dictionary of filter and ordering parameters
    :type request_args: dict
    """

    def __init__(self, data, request_args):
        self.data = data
        self.request_args = request_args

    @classmethod
    def cls_filter(cls, data, request_args):
        """Apply filters to data based on request arguments.

        :param data: The data to filter
        :param request_args: Dictionary of filter parameters
        :type request_args: dict
        :return: Filtered data
        """
        backend_class = cls._get_backend_class(data)

        for req_field_name, req_value in request_args.items():
            field_info = cls.__supported_query_key_field_dict__.get(req_field_name)
            if not field_info:
                continue

            field = field_info["field"]
            lookup_expr = field_info["lookup_expr"]

            parsed_value, is_valid = field.parse_value(req_value)
            if not is_valid:
                continue

            data = backend_class.filter(data, field.source, parsed_value, lookup_expr)

        return data

    @classmethod
    def cls_order(cls, data, request_args):
        """Apply ordering to data based on request arguments.

        :param data: The data to order
        :param request_args: Dictionary containing ordering parameters
        :type request_args: dict
        :return: Ordered data
        """
        ordering = request_args.get("ordering", "")
        if not ordering:
            return data
        backend = cls._get_backend_class(data)
        for field_name in ordering.split(","):
            is_negative = field_name.startswith("-")
            if is_negative:
                field_name = field_name[1:]
            field = cls.__ordering_field_map__.get(field_name)
            if not field:
                continue
            data = backend.order(data, field.source, is_negative)

        return data

    @classmethod
    def _get_backend_class(cls, data):
        """Get appropriate backend class for data type."""
        if isinstance(data, peewee.ModelSelect):
            return PeeweeBackend
        elif isinstance(data, Iterable):
            return IterableBackend
        else:
            raise TypeError(f"Unsupported data type: {type(data)}")

    def filter(self):
        """Apply filters and return self for chaining.

        :return: Self for method chaining
        :rtype: Model
        """
        self.data = self.__class__.cls_filter(self.data, self.request_args)
        return self

    def order(self):
        """Apply ordering and return self for chaining.

        :return: Self for method chaining
        :rtype: Model
        """
        self.data = self.__class__.cls_order(self.data, self.request_args)
        return self

    def result(self):
        """Get the final filtered and ordered data.

        :return: The processed data
        """
        return self.data
