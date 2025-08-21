import logging
import operator
from functools import partial

import peewee

from lumi_filter.operator import generic_ilike_operator, generic_like_operator

logger = logging.getLogger("lumi_filter.backend")


class PeeweeBackend:
    """Backend for filtering and ordering Peewee queries.

    This backend provides functionality to apply filters and ordering
    to Peewee ORM queries in a consistent manner.

    :param query: The Peewee query to apply filters and ordering to
    """

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

    def __init__(self):
        pass

    @classmethod
    def filter(cls, query, peewee_field, value, lookup_expr):
        """Apply filter to the query.

        :param query: The Peewee query to filter
        :param peewee_field: The field to filter on
        :param value: The value to filter by
        :param lookup_expr: The lookup expression for filtering
        :return: Filtered query
        :raises TypeError: If peewee_field is not a Peewee Field instance
        """
        if lookup_expr == "in":
            if isinstance(query.model._meta.database, peewee.SqliteDatabase):
                value = f"*{value}*"
            else:
                value = f"%{value}%"
        elif lookup_expr == "iin":
            value = f"%{value}%"

        if not isinstance(peewee_field, peewee.Field):
            raise TypeError(f"Expected peewee.Field, got {type(peewee_field)}")

        operator_func = cls.LOOKUP_EXPR_OPERATOR_MAP[lookup_expr]
        return query.where(operator_func(peewee_field, value))

    @classmethod
    def order(cls, query, field_name, is_negative=False):
        """Apply ordering to the query.

        :param query: The Peewee query to order
        :param field_name: Name of the field to order by
        :param is_negative: Whether to order in descending order
        :type is_negative: bool
        :return: Ordered query
        """

        direction = "DESC" if is_negative else "ASC"
        return query.order_by(peewee.SQL(f"{field_name} {direction}"))


class IterableBackend:
    """Backend for filtering and ordering iterable data.

    This backend provides functionality to apply filters and ordering
    to iterable data structures like lists and dictionaries.
    """

    LOOKUP_EXPR_OPERATOR_MAP = {
        "": operator.eq,
        "!": operator.ne,
        "gte": operator.ge,
        "lte": operator.le,
        "gt": operator.gt,
        "lt": operator.lt,
        "in": generic_like_operator,
        "iin": generic_ilike_operator,
    }

    @classmethod
    def _get_nested_value(cls, item, key):
        """Get nested value from item using dot notation.

        :param item: The item to extract value from
        :param key: The key path using dot notation (e.g., 'user.name')
        :return: The nested value
        :raises KeyError: If key path doesn't exist
        """
        for k in key.split("."):
            item = item[k]
        return item

    @classmethod
    def _match_item(cls, item, key, value, lookup_expr):
        """Check if item matches the filter criteria.

        :param item: The item to check
        :param key: The key to filter on
        :param value: The value to match against
        :param lookup_expr: The lookup expression for matching
        :return: True if item matches, True on error (permissive)
        :rtype: bool
        """
        try:
            item_value = cls._get_nested_value(item, key)
            operator_func = cls.LOOKUP_EXPR_OPERATOR_MAP[lookup_expr]
            return operator_func(item_value, value)
        except (KeyError, TypeError):
            return True

    @classmethod
    def filter(cls, data, key, value, lookup_expr):
        """Filter the data based on criteria.

        :param data: The iterable data to filter
        :param key: The key to filter on
        :param value: The value to filter by
        :param lookup_expr: The lookup expression for filtering
        :return: Filtered iterable
        """

        ret = filter(
            partial(cls._match_item, key=key, value=value, lookup_expr=lookup_expr),
            data,
        )
        if isinstance(data, list):
            return list(ret)
        if isinstance(data, tuple):
            return tuple(ret)
        if isinstance(data, set):
            return set(ret)
        return ret

    @classmethod
    def order(cls, data, key, is_reverse=False):
        """Sort the data by key.

        :param data: The iterable data to sort
        :param key: The key to sort by
        :param is_reverse: Whether to sort in reverse order
        :type is_reverse: bool
        :return: Sorted data
        """
        try:
            return sorted(data, key=lambda x: cls._get_nested_value(x, key), reverse=is_reverse)
        except (KeyError, TypeError):
            logger.warning("Failed to sort by key: %s", key)
            return data
