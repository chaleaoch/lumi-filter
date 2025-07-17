"""
Core model classes for the lumi_filter system.

This module provides the main Model class and supporting components for
building flexible filtering and ordering systems that work with both
ORM queries and plain Python data structures.
"""

import inspect
from typing import Any, Dict, Iterable, List, Optional, Union

import peewee
import pydantic

from lumi_filter.backend import IterableBackend, PeeweeBackend
from lumi_filter.field import FilterField
from lumi_filter.map import pd_filter_mapping, pw_filter_mapping


class MetaModel:
    """
    Configuration class for defining filter model schemas and fields.

    This class handles the automatic generation of FilterField instances
    from ORM models (Peewee) or data models (Pydantic), supporting both
    flat and nested field structures.
    """

    def __init__(
        self,
        schema: Optional[Union[type, peewee.Model, pydantic.BaseModel]] = None,
        fields: Optional[List[str]] = None,
        extra_field: Optional[Dict[str, FilterField]] = None,
    ) -> None:
        """
        Initialize MetaModel configuration.

        Args:
            schema: The model class to extract fields from (Peewee or Pydantic)
            fields: List of field names to include (if None, includes all fields)
            extra_field: Additional custom FilterField instances to include
        """
        self.schema = schema
        self.fields = fields or []
        self.extra_field = extra_field or {}

    def _is_field_allowed(self, field_name: str) -> bool:
        """
        Check if field should be included based on self.fields filter.

        Args:
            field_name: Name of the field to check

        Returns:
            True if field should be included
        """
        return not self.fields or field_name in self.fields

    def _get_peewee_fields(self) -> Dict[str, FilterField]:
        """
        Extract filter fields from Peewee model.

        Returns:
            Dictionary mapping field names to FilterField instances
        """
        ret = {}
        for attr_name, pw_field in self.schema._meta.fields.items():
            if not self._is_field_allowed(attr_name):
                continue
            filter_field_class = pw_filter_mapping.get(pw_field.__class__, FilterField)
            ret[attr_name] = filter_field_class(source=pw_field)
        return ret

    def _get_pydantic_fields(self) -> Dict[str, FilterField]:
        """
        Extract filter fields from Pydantic model.

        Supports nested models using dot notation for field names.

        Returns:
            Dictionary mapping field names to FilterField instances
        """
        ret = {}
        stack = [(self.schema.model_fields, "")]

        while stack:
            model_fields, key_prefix = stack.pop()
            for key, pydantic_field in model_fields.items():
                new_key = f"{key_prefix}.{key}" if key_prefix else key

                # Check if field annotation is a nested BaseModel
                annotation = pydantic_field.annotation
                try:
                    if inspect.isclass(annotation) and issubclass(
                        annotation, pydantic.BaseModel
                    ):
                        stack.append((annotation.model_fields, new_key))
                        continue
                except TypeError:
                    # annotation is not a class, skip nested check
                    pass

                if not self._is_field_allowed(new_key):
                    continue

                filter_field_class = pd_filter_mapping.get(annotation, FilterField)
                field_key = new_key.replace(".", "_")
                ret[field_key] = filter_field_class(
                    request_arg_name=new_key, source=new_key
                )
        return ret

    def get_filter_fields(self) -> Dict[str, FilterField]:
        """
        Generate FilterField instances based on the configured schema.

        Returns:
            Dictionary mapping field names to FilterField instances

        Example:
            >>> meta = MetaModel(schema=User, fields=['name', 'age'])
            >>> fields = meta.get_filter_fields()
            >>> # Returns {'name': StrField(...), 'age': IntField(...)}
        """
        ret = {}
        if self.schema is None:
            ret.update(self.extra_field)
            return ret

        try:
            if issubclass(self.schema, peewee.Model):
                ret.update(self._get_peewee_fields())
            elif issubclass(self.schema, pydantic.BaseModel):
                ret.update(self._get_pydantic_fields())
        except TypeError:
            # self.schema is not a class
            pass

        ret.update(self.extra_field)
        return ret


class ModelMeta(type):
    """
    Metaclass for Model that automatically configures FilterFields.

    This metaclass processes Meta class configurations and FilterField
    definitions to build the query support infrastructure.
    """

    def __new__(cls, name: str, bases: tuple, attrs: Dict[str, Any]) -> type:
        """
        Create a new Model class with FilterField processing.

        Args:
            name: Name of the class being created
            bases: Base classes
            attrs: Class attributes dictionary

        Returns:
            The new Model class with filtering capabilities
        """
        supported_query_key_field_dict = {}
        meta_options = {}

        # Extract Meta class configuration
        meta = attrs.pop("Meta", None)
        if meta:
            for k, v in meta.__dict__.items():
                if not k.startswith("_"):
                    meta_options[k] = v

        # Generate fields from schema and merge with explicit fields
        meta_model = MetaModel(**meta_options)
        schema_fields = meta_model.get_filter_fields()
        attrs = schema_fields | attrs  # attrs have higher priority

        # Process FilterField instances
        for field_name, field in attrs.items():
            if isinstance(field, FilterField):
                # Set field metadata
                field.name = field_name
                if field.request_arg_name is None:
                    field.request_arg_name = field_name
                if field.source is None:
                    field.source = field_name

                # Validate field configuration
                if "__" in field.request_arg_name:
                    raise ValueError(
                        f"field.request_arg_name of {field_name} cannot contain '__' "
                        "because this syntax is reserved for lookups."
                    )

                # Build lookup expression mappings
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
    """
    Base model class for filtering and ordering operations.

    This class provides a unified interface for filtering and ordering
    data from different sources (ORM queries, Python iterables) using
    a consistent API.

    Example:
        >>> class UserFilter(Model):
        ...     class Meta:
        ...         schema = User
        ...     age = IntField()
        ...
        >>> users = User.select()
        >>> filtered_users = UserFilter(users, {'age__gte': 18}).filter().result()
    """

    def __init__(
        self,
        data: Union[peewee.ModelSelect, Iterable],
        request_args: Dict[str, Any],
        *args,
        **kwargs,
    ) -> None:
        """
        Initialize the Model with data and filter parameters.

        Args:
            data: The data source to filter (ORM query or iterable)
            request_args: Dictionary of filter parameters
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        self.data = data
        self.request_args = request_args

    @classmethod
    def _get_backend(
        cls, data: Union[peewee.ModelSelect, Iterable]
    ) -> Union[PeeweeBackend, IterableBackend]:
        """
        Get appropriate backend based on data type.

        Args:
            data: The data source

        Returns:
            Backend class for handling the data type

        Raises:
            ValueError: If data type is not supported
        """
        if isinstance(data, peewee.ModelSelect):
            return PeeweeBackend
        elif isinstance(data, Iterable):
            return IterableBackend
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")

    @classmethod
    def cls_filter(
        cls, data: Union[peewee.ModelSelect, Iterable], request_args: Dict[str, Any]
    ) -> Union[peewee.ModelSelect, filter]:
        """
        Apply filters to data using class-level method.

        Args:
            data: Data source to filter
            request_args: Filter parameters

        Returns:
            Filtered data

        Example:
            >>> users = User.select()
            >>> filtered = UserFilter.cls_filter(users, {'age__gte': 18})
        """
        Backend = cls._get_backend(data)

        for req_field_name, req_value in request_args.items():
            if req_field_name not in cls.__supported_query_key_field_dict__:
                continue

            field_info = cls.__supported_query_key_field_dict__[req_field_name]
            field = field_info["field"]
            lookup_expr = field_info["lookup_expr"]

            req_value, ok = field.parse_value(req_value)
            if not ok:
                continue

            data = Backend.filter(data, field.source, req_value, lookup_expr)
        return data

    @classmethod
    def cls_order(
        cls, data: Union[peewee.ModelSelect, Iterable], request_args: Dict[str, Any]
    ) -> Union[peewee.ModelSelect, List]:
        """
        Apply ordering to data using class-level method.

        Args:
            data: Data source to order
            request_args: Parameters including 'ordering'

        Returns:
            Ordered data

        Example:
            >>> users = User.select()
            >>> ordered = UserFilter.cls_order(users, {'ordering': '-age,name'})
        """
        Backend = cls._get_backend(data)

        ordering = request_args.get("ordering", "")
        if not ordering:
            return data

        ordering_list = ordering.split(",")
        for req_field_name in ordering_list:
            is_negative = req_field_name.startswith("-")
            if is_negative:
                req_field_name = req_field_name[1:]
            data = Backend.order(data, req_field_name, is_negative)
        return data

    def filter(self) -> "Model":
        """
        Apply filters to the data.

        Returns:
            Self for method chaining

        Example:
            >>> filter_model = UserFilter(users, {'age__gte': 18})
            >>> filtered = filter_model.filter().result()
        """
        self.data = self.__class__.cls_filter(self.data, self.request_args)
        return self

    def order(self) -> "Model":
        """
        Apply ordering to the data.

        Returns:
            Self for method chaining

        Example:
            >>> filter_model = UserFilter(users, {'ordering': '-age'})
            >>> ordered = filter_model.order().result()
        """
        self.data = self.__class__.cls_order(self.data, self.request_args)
        return self

    def result(self) -> Union[peewee.ModelSelect, List, filter]:
        """
        Get the final filtered/ordered data.

        Returns:
            The processed data

        Example:
            >>> users = UserFilter(data, params).filter().order().result()
        """
        return self.data
