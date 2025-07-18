import logging
import operator
from functools import partial

import peewee

from lumi_filter.operator import (
    generic_ilike_operator,
    generic_like_operator,
)

logger = logging.getLogger("lumi_filter.backend")


class PeeweeBackend:
    LOOKUP_EXPR_OPERATOR_MAP = {
        "": operator.eq,
        "!": operator.ne,
        "gte": operator.ge,
        "lte": operator.le,
        "gt": operator.gt,
        "lt": operator.lt,
        "in": operator.mod,
        "iin": operator.pow,
    }

    def __init__(self, query, ordering_extra_fields):
        self.field_names = set()
        for node in query.selected_columns:
            if isinstance(node, peewee.Alias):
                self.field_names.add(node.alias_name)
            elif isinstance(node, peewee.Field):
                self.field_names.add(node.column_name)
            else:
                logger.warning(
                    f"Unsupported field type in order_by: {type(node)}. Using default ordering.",
                )
        self.field_names = self.field_names | ordering_extra_fields

    @classmethod
    def filter(self, query, peewee_field, value, lookup_expr):
        if lookup_expr in ["in", "iin"]:
            value = f"%{value}%"
        if isinstance(peewee_field, type) and not issubclass(
            peewee_field, peewee.Field
        ):
            raise TypeError(f"Expected a peewee.Field, got {type(peewee_field)}.")
        return query.where(
            self.LOOKUP_EXPR_OPERATOR_MAP[lookup_expr](peewee_field, value)
        )

    def order(self, query, peewee_field_name, is_negative=False):
        if peewee_field_name in self.field_names:
            if is_negative:
                query = query.order_by(peewee.SQL(peewee_field_name + " DESC"))
            else:
                query = query.order_by(peewee.SQL(peewee_field_name + " ASC"))
        return query


class IterableBackend:
    LOOKUP_EXPR_OPERATOR_MAP = {
        "": operator.eq,
        "!": operator.ne,
        "gte": operator.ge,
        "lte": operator.le,
        "gt": operator.gt,
        "lt": operator.lt,
        "in": generic_like_operator,
        "iin": generic_ilike_operator,
        # "is_null": generic_is_null_operator,
    }

    @classmethod
    def match_nested_value(cls, item_dict, key, value, lookup_expr):
        for k in key.split("."):
            item_dict = item_dict[k]
        return cls.LOOKUP_EXPR_OPERATOR_MAP[lookup_expr](item_dict, value)

    @classmethod
    def filter(cls, data, key, value, lookup_expr):
        return filter(
            partial(
                cls.match_nested_value, key=key, value=value, lookup_expr=lookup_expr
            ),
            data,
        )

    @classmethod
    def order(cls, data, key, is_reverse=False):
        return sorted(data, key=lambda x: x[key], reverse=is_reverse)
