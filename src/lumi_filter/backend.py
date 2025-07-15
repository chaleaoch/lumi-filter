import logging
import operator

import peewee

from lumi_filter.operator import (
    generic_ilike_operator,
    generic_is_null_operator,
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
        "nin": operator.pow,
    }

    @classmethod
    def filter(cls, query, peewee_field, value, lookup_expr):
        return query.where(
            cls.LOOKUP_EXPR_OPERATOR_MAP[lookup_expr](peewee_field, value)
        )

    @classmethod
    def get_node_name(cls, node):
        if isinstance(node, peewee.Alias):
            return node.alias_name
        elif isinstance(node, peewee.Field):
            return node.column_name
        else:
            logger.warning(
                "Unsupported field type in order_by: %s. Using default ordering.",
                type(node),
            )
            return ""

    @classmethod
    def order(cls, query, peewee_field_name, is_negative=False):
        for node in query.selected_columns:
            if peewee_field_name == cls.get_node_name(node):
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
        "nin": generic_ilike_operator,
        "is_null": generic_is_null_operator,
    }

    @classmethod
    def filter(cls, data, key, value, lookup_expr):
        return filter(
            lambda x: cls.LOOKUP_EXPR_OPERATOR_MAP[lookup_expr](x[key], value),
            data,
        )

    @classmethod
    def order(cls, data, key, is_reverse=False):
        return sorted(data, key=lambda x: x[key], reverse=is_reverse)
