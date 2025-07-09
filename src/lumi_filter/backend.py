import operator


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
    def filter(cls, query, peewee_field, req_value, lookup_expr):
        return query.where(
            cls.LOOKUP_EXPR_OPERATOR_MAP[lookup_expr](peewee_field, req_value)
        )
