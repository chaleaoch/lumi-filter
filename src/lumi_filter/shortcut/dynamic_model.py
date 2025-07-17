"""
Dynamic model creation utilities.

This module provides utilities for creating filter models dynamically
at runtime, useful for scenarios where the model structure is not
known at development time.
"""

from typing import Any, Dict, Optional, Type

from lumi_filter.field import FilterField
from lumi_filter.model import Model


def create_dynamic_model(
    name: str,
    fields: Dict[str, FilterField],
    meta_attrs: Optional[Dict[str, Any]] = None,
) -> Type[Model]:
    """
    Create a dynamic filter model class at runtime.

    Args:
        name: Name for the new model class
        fields: Dictionary of field names to FilterField instances
        meta_attrs: Optional Meta class attributes

    Returns:
        New Model class with the specified fields

    Example:
        >>> from lumi_filter.field import IntField, StrField
        >>> fields = {
        ...     'name': StrField(),
        ...     'age': IntField()
        ... }
        >>> UserFilter = create_dynamic_model('UserFilter', fields)
        >>> # Now you can use UserFilter like any other Model class
    """
    attrs = fields.copy()

    if meta_attrs:
        # Create Meta class if meta attributes provided
        meta_class = type("Meta", (), meta_attrs)
        attrs["Meta"] = meta_class

    # Create and return the new model class
    return type(name, (Model,), attrs)


def model_from_dict_schema(
    name: str,
    sample_data: Dict[str, Any],
    field_mapping: Optional[Dict[Type, Type[FilterField]]] = None,
) -> Type[Model]:
    """
    Create a dynamic model from a sample dictionary.

    Automatically infers field types from the sample data structure.

    Args:
        name: Name for the new model class
        sample_data: Sample dictionary to infer structure from
        field_mapping: Optional custom mapping of Python types to FilterFields

    Returns:
        New Model class inferred from the sample data

    Example:
        >>> sample = {'name': 'John', 'age': 30, 'active': True}
        >>> UserFilter = model_from_dict_schema('UserFilter', sample)
        >>> # Creates a model with StrField, IntField, and BooleanField
    """
    from lumi_filter.map import pd_filter_mapping

    fields = {}
    mapping = field_mapping or pd_filter_mapping

    for key, value in sample_data.items():
        value_type = type(value)
        field_class = mapping.get(value_type, FilterField)
        fields[key] = field_class()

    return create_dynamic_model(name, fields)
