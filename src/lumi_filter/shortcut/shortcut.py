import logging
from typing import Iterable

import peewee

from lumi_filter.field import FilterField
from lumi_filter.map import pd_filter_mapping, pw_filter_mapping
from lumi_filter.model import Model

logger = logging.getLogger("lumi_filter.shortcut")


class AutoQueryModel:
    def __new__(cls, data, request_args):
        cls.data = data
        cls.request_args = request_args
        attrs = {}
        if isinstance(cls.data, peewee.ModelSelect):
            for node in cls.data.selected_columns:
                if isinstance(node, peewee.Field):
                    attrs[node.name] = pw_filter_mapping.get(
                        node.__class__, FilterField
                    )(source=node)
                elif isinstance(node, peewee.Alias) and isinstance(
                    node.node, peewee.Field
                ):
                    pw_field = node.node
                    attrs[node.name] = pw_filter_mapping.get(
                        pw_field.__class__, FilterField
                    )(source=pw_field)
                else:
                    logger.warning(
                        "Unsupported field type in AutoQuery: %s. Using default FilterField.",
                        type(node),
                    )
        elif isinstance(cls.data, Iterable):
            cls.data = list(cls.data)
            if not cls.data:
                raise ValueError("Data cannot be empty for AutoQuery.")
            stack = [(cls.data[0], "")]
            while stack:
                current_dict, key_prefix = stack.pop()
                for key, value in current_dict.items():
                    new_key = f"{key_prefix}.{key}" if key_prefix else key
                    if isinstance(value, dict):
                        stack.append((value, new_key))
                    else:
                        attrs[new_key.replace(".", "_")] = pd_filter_mapping.get(
                            type(value), FilterField
                        )(request_arg_name=new_key, source=new_key)
        else:
            logger.error("Unsupported data type for AutoQuery: %s", type(cls.data))
            raise TypeError("Unsupported data type for AutoQuery")
        return type("dynamic_filter_model", (Model,), attrs)(
            data=data, request_args=request_args
        )


def compatible_request_args(request_args):
    ret = {}
    map = {
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
        key, lookup_expr = key.split("(", 1)
        lookup_expr = lookup_expr[:-1]
        if lookup_expr in map:
            request_args[key] = map[lookup_expr]
        else:
            raise ValueError(f"Unsupported lookup expression: {lookup_expr}")
        if lookup_expr == "!":
            ret[f"{key}!"] = value
        elif lookup_expr == "":
            ret[key] = value
        elif lookup_expr in ["in", "iin"]:
            ret[f"{key}__{map[lookup_expr]}"] = value[1:-1] if len(value) > 2 else value
        else:
            ret[f"{key}__{map[lookup_expr]}"] = value
    return ret
