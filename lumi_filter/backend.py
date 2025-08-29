"""Backend implementations for filtering and ordering data.

This module provides backend classes for different data sources:
- PeeweeBackend: For Peewee ORM queries
- IterableBackend: For Python iterable data structures

Both backends support various lookup expressions and maintain consistent
interfaces for filtering and ordering operations.
"""

import logging
import operator
from functools import partial

import peewee

from lumi_filter.operator import generic_ilike_operator, generic_in_operator, generic_like_operator

logger = logging.getLogger("lumi_filter.backend")


class PeeweeBackend:
    """Backend for filtering and ordering Peewee queries.

    This backend provides functionality to apply filters and ordering
    to Peewee ORM queries in a consistent manner. It supports various
    lookup expressions including equality, comparison operators, and
    text search operations.

    The backend handles database-specific optimizations, such as using
    FTS (Full Text Search) syntax for SQLite databases when performing
    contains operations.

    Attributes:
        LOOKUP_EXPR_OPERATOR_MAP (dict): Mapping of lookup expressions
            to corresponding Peewee operators.
    """

    LOOKUP_EXPR_OPERATOR_MAP = {
        "": operator.eq,
        "!": operator.ne,
        "gte": operator.ge,
        "lte": operator.le,
        "gt": operator.gt,
        "lt": operator.lt,
        "contains": operator.mod,
        "icontains": operator.pow,
        "in": operator.lshift,
    }

    def __init__(self):
        """Initialize the PeeweeBackend.

        The backend is stateless and doesn't require any configuration.
        All methods are class methods that operate on provided queries.
        """
        pass

    @classmethod
    def filter(cls, query, peewee_field, value, lookup_expr):
        """Apply filter to the query.

        Applies a filter condition to the Peewee query based on the provided
        field, value, and lookup expression. Handles special cases for text
        search operations, adjusting the value format for different database
        backends (SQLite uses FTS syntax with asterisks, others use SQL LIKE
        with percent signs).

        Args:
            query (peewee.Query): The Peewee query to filter.
            peewee_field (peewee.Field): The Peewee field to filter on.
            value: The value to filter by.
            lookup_expr (str): The lookup expression for filtering (e.g., '', '!',
                'gte', 'lte', 'gt', 'lt', 'contains', 'icontains', 'in').

        Returns:
            peewee.Query: Filtered query with the condition applied.

        Raises:
            TypeError: If peewee_field is not a Peewee Field instance.
        """
        if lookup_expr == "contains":
            if isinstance(query.model._meta.database, peewee.SqliteDatabase) or (
                isinstance(query.model._meta.database, peewee.Proxy)
                and isinstance(query.model._meta.database.obj, peewee.SqliteDatabase)
            ):
                value = f"*{value}*"
            else:
                value = f"%{value}%"
        elif lookup_expr == "icontains":
            value = f"%{value}%"

        if not isinstance(peewee_field, peewee.Field):
            raise TypeError(f"Expected peewee.Field, got {type(peewee_field)}")

        operator_func = cls.LOOKUP_EXPR_OPERATOR_MAP[lookup_expr]
        return query.where(operator_func(peewee_field, value))

    @classmethod
    def order(cls, query, ordering):
        """Apply ordering to the query.

        Args:
            query: The Peewee query to order.
            ordering: List of tuples containing (field, is_negative) pairs
                where field is the Peewee field to order by and
                is_negative is a boolean indicating descending order.

        Returns:
            peewee.Query: Ordered query.
        """
        order_fields = []
        for field, is_negative in ordering:
            order_fields.append(field.desc() if is_negative else field.asc())
        return query.order_by(*order_fields)


class IterableBackend:
    """Backend for filtering and ordering iterable data.

    This backend provides functionality to apply filters and ordering
    to iterable data structures like lists, tuples, sets, and dictionaries.
    It supports nested field access using dot notation and various lookup
    expressions for flexible data filtering.

    The backend is designed to be permissive, returning True on errors
    during filtering to avoid breaking the filter chain when dealing
    with inconsistent data structures.

    Attributes:
        LOOKUP_EXPR_OPERATOR_MAP (dict): Mapping of lookup expressions
            to corresponding operator functions.
    """

    LOOKUP_EXPR_OPERATOR_MAP = {
        "": operator.eq,
        "!": operator.ne,
        "gte": operator.ge,
        "lte": operator.le,
        "gt": operator.gt,
        "lt": operator.lt,
        "contains": generic_like_operator,
        "icontains": generic_ilike_operator,
        "in": generic_in_operator,
    }

    @classmethod
    def _get_nested_value(cls, item, key):
        """Get nested value from item using dot notation.

        Extracts a value from a nested data structure using dot notation
        for the key path. For example, 'user.profile.name' would access
        item['user']['profile']['name'].

        Args:
            item: The item to extract value from (dict-like object).
            key (str): The key path using dot notation (e.g., 'user.name').

        Returns:
            The nested value.

        Raises:
            KeyError: If any part of the key path doesn't exist.
        """
        for k in key.split("."):
            item = item[k]
        return item

    @classmethod
    def _match_item(cls, item, key, value, lookup_expr):
        """Check if item matches the filter criteria.

        Evaluates whether an item satisfies the specified filter condition.
        Uses the appropriate operator based on the lookup expression and
        handles nested field access. Returns True on errors (KeyError, TypeError)
        to maintain a permissive filtering approach.

        Args:
            item: The item to check (dict-like object).
            key (str): The key to filter on (supports dot notation).
            value: The value to match against.
            lookup_expr (str): The lookup expression for matching (e.g., '', '!',
                'gte', 'lte', 'gt', 'lt', 'contains', 'icontains', 'in').

        Returns:
            bool: True if item matches the criteria, True on error (permissive).
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

        Filters an iterable data structure based on the specified criteria.
        Preserves the original data type of the input (list, tuple, set) while
        filtering the elements. For other iterable types, returns a filter object.

        Args:
            data (iterable): The iterable data to filter.
            key (str): The key to filter on (supports dot notation for nested access).
            value: The value to filter by.
            lookup_expr (str): The lookup expression for filtering (e.g., '', '!',
                'gte', 'lte', 'gt', 'lt', 'contains', 'icontains', 'in').

        Returns:
            The filtered iterable of the same type as input (or a filter object).
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
    def order(cls, data, ordering):
        """Sort the data by multiple keys.

        Args:
            data (iterable): The iterable data to sort.
            ordering (list): List of tuples containing (key, is_reverse) pairs
                where key is the field name to sort by (supports dot notation)
                and is_reverse is a boolean indicating reverse order.

        Returns:
            The sorted data of the same type as input.
        """
        try:
            for key, is_reverse in ordering[::-1]:
                data = sorted(data, key=lambda x: cls._get_nested_value(x, key), reverse=is_reverse)
        except (KeyError, TypeError):
            logger.warning("Failed to sort by ordering: %s", ordering)
        finally:
            return data
