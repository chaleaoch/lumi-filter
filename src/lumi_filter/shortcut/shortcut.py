"""Shortcut functions for dynamic model creation."""

import logging
from typing import Any, Dict, Iterable, Union

import peewee

from lumi_filter.field import FilterField
from lumi_filter.map import pd_filter_mapping, pw_filter_mapping
from lumi_filter.model import Model

logger = logging.getLogger("lumi_filter.shortcut")


class AutoQueryModel:
    """Automatically generate a filter model based on data structure."""

    def __new__(
        cls, data: Union[peewee.ModelSelect, Iterable], request_args: Dict[str, Any]
    ):
        cls.data = data
        cls.request_args = request_args
        attrs = {}

        try:
            if isinstance(data, peewee.ModelSelect):
                attrs.update(cls._process_peewee_data(data))
            elif isinstance(data, Iterable):
                attrs.update(cls._process_iterable_data(data))
            else:
                raise TypeError(f"Unsupported data type: {type(data)}")

        except Exception as e:
            logger.error(f"Error processing data for AutoQuery: {e}")
            raise

        # Create dynamic model class
        DynamicModel = type("DynamicFilterModel", (Model,), attrs)
        return DynamicModel(data=data, request_args=request_args)

    @classmethod
    def _process_peewee_data(cls, data: peewee.ModelSelect) -> Dict[str, FilterField]:
        """Process Peewee model select data."""
        attrs = {}
        for node in data.selected_columns:
            if isinstance(node, peewee.Field):
                field_class = pw_filter_mapping.get(node.__class__, FilterField)
                attrs[node.name] = field_class(source=node)
            elif isinstance(node, peewee.Alias) and isinstance(node.node, peewee.Field):
                pw_field = node.node
                field_class = pw_filter_mapping.get(pw_field.__class__, FilterField)
                attrs[node.alias_name] = field_class(source=pw_field)
            else:
                logger.warning(
                    f"Unsupported field type in AutoQuery: {type(node)}. Using default FilterField."
                )
                attrs[str(node)] = FilterField(source=node)
        return attrs

    @classmethod
    def _process_iterable_data(cls, data: Iterable) -> Dict[str, FilterField]:
        """Process iterable data (list of dicts)."""
        data_list = list(data)
        if not data_list:
            raise ValueError("Data cannot be empty for AutoQuery.")

        attrs = {}
        sample_item = data_list[0]

        # Use BFS to traverse nested structure
        stack = [(sample_item, "")]
        while stack:
            current_dict, key_prefix = stack.pop()

            if not isinstance(current_dict, dict):
                continue

            for key, value in current_dict.items():
                new_key = f"{key_prefix}.{key}" if key_prefix else key

                if isinstance(value, dict):
                    stack.append((value, new_key))
                else:
                    field_class = pd_filter_mapping.get(type(value), FilterField)
                    field_name = new_key.replace(".", "_")
                    attrs[field_name] = field_class(
                        request_arg_name=new_key, source=new_key
                    )

        return attrs


def compatible_request_args(request_args: Dict[str, Any]) -> Dict[str, Any]:
    """Convert request args with SQL-like operators to internal format."""
    ret = {}
    operator_map = {
        "==": "",
        "!=": "!",
        ">=": "gte",
        "<=": "lte",
        ">": "gt",
        "<": "lt",
        "LIKE": "in",
        "ILIKE": "iin",
    }

    for key, value in request_args.items():
        if "(" not in key:
            # No operator specified, use exact match
            ret[key] = value
            continue

        try:
            field_name, operator_part = key.split("(", 1)
            operator_expr = operator_part.rstrip(")")

            if operator_expr not in operator_map:
                raise ValueError(f"Unsupported lookup expression: {operator_expr}")

            internal_operator = operator_map[operator_expr]

            # Build the key based on operator
            if internal_operator == "!":
                new_key = f"{field_name}!"
            elif internal_operator == "":
                new_key = field_name
            else:
                new_key = f"{field_name}__{internal_operator}"

            # Process value for LIKE operators
            if operator_expr in ["LIKE", "ILIKE"] and isinstance(value, str):
                # Remove surrounding quotes if present
                if len(value) > 2 and value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                elif len(value) > 2 and value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]

            ret[new_key] = value

        except ValueError as e:
            logger.error(f"Error parsing request arg '{key}': {e}")
            # Skip malformed keys
            continue

    return ret
