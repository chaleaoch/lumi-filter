import logging
from typing import Iterable

import peewee

from lumi_filter.field import FilterField
from lumi_filter.map import pd_filter_mapping, pw_filter_mapping
from lumi_filter.model import Model

logger = logging.getLogger("lumi_filter.shortcut")


class AutoQuery:
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

            for key in cls.data[0].keys():
                attrs[key] = pd_filter_mapping.get(type(key), FilterField)()
        else:
            logger.error("Unsupported data type for AutoQuery: %s", type(cls.data))
            raise TypeError("Unsupported data type for AutoQuery")
        return type("dynamic_filter_model", (Model,), attrs)(
            data=data, request_args=request_args
        )
