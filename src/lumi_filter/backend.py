"""
Backend implementations for different data sources.

This module provides backend classes that handle filtering and ordering
operations for different types of data sources, including Peewee ORM
queries and Python iterables.
"""

import logging
import operator
from functools import partial
from typing import Any, Callable, Dict, List
from typing import Iterable as IterableType

import peewee

from lumi_filter.operator import (
    generic_ilike_operator,
    generic_like_operator,
)

logger = logging.getLogger("lumi_filter.backend")


class PeeweeBackend:
    """
    Backend for filtering Peewee ORM queries.

    This backend handles filtering and ordering operations on Peewee
    ModelSelect queries, converting filter expressions into appropriate
    SQL WHERE clauses and ORDER BY statements.
    """

    LOOKUP_EXPR_OPERATOR_MAP: Dict[str, Callable[[Any, Any], Any]] = {
        "": operator.eq,  # Exact match
        "!": operator.ne,  # Not equal
        "gte": operator.ge,  # Greater than or equal
        "lte": operator.le,  # Less than or equal
        "gt": operator.gt,  # Greater than
        "lt": operator.lt,  # Less than
        "in": operator.mod,  # LIKE operation (contains)
        "iin": operator.pow,  # ILIKE operation (case-insensitive contains)
    }

    @classmethod
    def filter(
        cls,
        query: peewee.ModelSelect,
        peewee_field: peewee.Field,
        value: Any,
        lookup_expr: str,
    ) -> peewee.ModelSelect:
        """
        Apply filter to Peewee query.

        Converts a filter expression into a WHERE clause and applies it
        to the given query.

        Args:
            query: The Peewee ModelSelect query to filter
            peewee_field: The field to filter on
            value: The value to filter by
            lookup_expr: The lookup expression (e.g., 'gt', 'in', 'iin')

        Returns:
            Modified query with the filter applied

        Example:
            >>> query = User.select()
            >>> filtered = PeeweeBackend.filter(query, User.age, 18, "gte")
            >>> # Equivalent to: User.select().where(User.age >= 18)
        """
        # Convert value for LIKE operations
        if lookup_expr in ["in", "iin"]:
            value = f"%{value}%"

        try:
            op = cls.LOOKUP_EXPR_OPERATOR_MAP[lookup_expr]
            return query.where(op(peewee_field, value))
        except KeyError:
            logger.warning(f"Unsupported lookup expression: {lookup_expr}")
            return query

    @classmethod
    def get_node_name(cls, node: Any) -> str:
        """
        Extract field name from Peewee node.

        Handles different types of Peewee query nodes to extract
        the appropriate column name for ordering operations.

        Args:
            node: Peewee query node (Field, Alias, etc.)

        Returns:
            The column name or alias name for the node
        """
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
    def order(
        cls, query: peewee.ModelSelect, field_name: str, is_negative: bool = False
    ) -> peewee.ModelSelect:
        """
        Apply ordering to Peewee query.

        Adds an ORDER BY clause to the query for the specified field.

        Args:
            query: The Peewee ModelSelect query to order
            field_name: Name of the field to order by
            is_negative: If True, order in descending order

        Returns:
            Query with ordering applied

        Example:
            >>> query = User.select()
            >>> ordered = PeeweeBackend.order(query, "name", False)
            >>> # Equivalent to: User.select().order_by(User.name.asc())
        """
        for node in query.selected_columns:
            if field_name == cls.get_node_name(node):
                direction = "DESC" if is_negative else "ASC"
                # Use proper SQL construction instead of string concatenation
                return query.order_by(peewee.SQL(f"{field_name} {direction}"))

        logger.warning(f"Field {field_name} not found in selected columns")
        return query


class IterableBackend:
    """
    Backend for filtering Python iterables (lists, dicts, etc.).

    This backend handles filtering and ordering operations on Python
    data structures like lists of dictionaries, supporting nested
    field access using dot notation.
    """

    LOOKUP_EXPR_OPERATOR_MAP: Dict[str, Callable[[Any, Any], bool]] = {
        "": operator.eq,  # Exact match
        "!": operator.ne,  # Not equal
        "gte": operator.ge,  # Greater than or equal
        "lte": operator.le,  # Less than or equal
        "gt": operator.gt,  # Greater than
        "lt": operator.lt,  # Less than
        "in": generic_like_operator,  # Contains (case-sensitive)
        "iin": generic_ilike_operator,  # Contains (case-insensitive)
    }

    @classmethod
    def get_nested_value(cls, item: dict, key: str) -> Any:
        """
        Get nested value from dict using dot notation.

        Supports accessing nested dictionary values using dot-separated
        keys like "user.profile.name".

        Args:
            item: Dictionary to extract value from
            key: Dot-separated key path (e.g., "user.profile.name")

        Returns:
            The nested value

        Raises:
            KeyError: If any part of the key path is not found

        Example:
            >>> data = {"user": {"profile": {"name": "John"}}}
            >>> get_nested_value(data, "user.profile.name")
            "John"
        """
        current = item
        for k in key.split("."):
            if not isinstance(current, dict) or k not in current:
                raise KeyError(f"Key '{key}' not found in item")
            current = current[k]
        return current

    @classmethod
    def match_nested_value(
        cls, item: dict, key: str, value: Any, lookup_expr: str
    ) -> bool:
        """
        Check if item matches filter criteria.

        Extracts the nested value from the item and applies the
        specified lookup operation to check if it matches the filter.

        Args:
            item: Dictionary item to check
            key: Dot-separated key path to the field
            value: Value to compare against
            lookup_expr: Lookup expression (e.g., 'gt', 'in')

        Returns:
            True if the item matches the filter criteria

        Example:
            >>> item = {"user": {"age": 25}}
            >>> match_nested_value(item, "user.age", 18, "gte")
            True
        """
        try:
            item_value = cls.get_nested_value(item, key)
            op = cls.LOOKUP_EXPR_OPERATOR_MAP.get(lookup_expr, operator.eq)
            return op(item_value, value)
        except (KeyError, TypeError):
            return False

    @classmethod
    def filter(
        cls, data: IterableType, key: str, value: Any, lookup_expr: str
    ) -> filter:
        """
        Filter iterable data based on criteria.

        Returns a filter object that yields items matching the
        specified filter criteria.

        Args:
            data: Iterable data to filter
            key: Field key to filter on (supports dot notation)
            value: Value to filter by
            lookup_expr: Lookup expression for comparison

        Returns:
            Filter object yielding matching items

        Example:
            >>> data = [{"name": "John", "age": 25}, {"name": "Jane", "age": 30}]
            >>> filtered = IterableBackend.filter(data, "age", 25, "gte")
            >>> list(filtered)
            [{"name": "John", "age": 25}, {"name": "Jane", "age": 30}]
        """
        return filter(
            partial(
                cls.match_nested_value, key=key, value=value, lookup_expr=lookup_expr
            ),
            data,
        )

    @classmethod
    def order(
        cls, data: IterableType, key: str, is_negative: bool = False
    ) -> List[dict]:
        """
        Sort iterable data by key.

        Sorts the data based on the specified key, supporting nested
        field access using dot notation.

        Args:
            data: Iterable data to sort
            key: Field key to sort by (supports dot notation)
            is_negative: If True, sort in descending order

        Returns:
            Sorted list of items

        Example:
            >>> data = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]
            >>> sorted_data = IterableBackend.order(data, "age", False)
            >>> # Returns items sorted by age in ascending order
        """
        try:
            return sorted(
                data, key=lambda x: cls.get_nested_value(x, key), reverse=is_negative
            )
        except (KeyError, TypeError) as e:
            logger.warning(f"Error sorting by key '{key}': {e}")
            return list(data)  # Return unsorted data if sorting fails
