import operator

from lumi_filter.operator import (
    generic_ilike_operator,
    generic_is_null_operator,
    generic_like_operator,
)


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


class IterableBackend:
    LOOKUP_EXPR_OPERATOR_MAP = {
        "": operator.eq,
        "!=": operator.ne,
        ">=": operator.ge,
        "<=": operator.le,
        ">": operator.gt,
        "<": operator.lt,
        "LIKE": generic_like_operator,
        "ILIKE": generic_ilike_operator,
        "is_null": generic_is_null_operator,
    }

    @classmethod
    def filter(cls, data, key, value, lookup_expr):
        return filter(
            lambda x: cls.LOOKUP_EXPR_OPERATOR_MAP[lookup_expr](x[key], value),
            data,
        )
