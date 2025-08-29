"""Generic operators for filtering operations.

This module provides generic operator functions for filtering operations
that work across different data sources and backends.
"""


def generic_like_operator(left, right):
    """Case-sensitive contains operator.

    Args:
        left: The value to search in
        right: The value to search for

    Returns:
        bool: True if right is contained in left (case-sensitive)
    """
    return str(right) in str(left)


def generic_ilike_operator(left, right):
    """Case-insensitive contains operator.

    Args:
        left: The value to search in
        right: The value to search for

    Returns:
        bool: True if right is contained in left (case-insensitive)
    """
    return str(right).lower() in str(left).lower()


def generic_in_operator(left, right):
    """Generic membership operator.

    Checks if left value is a member of right iterable.
    Falls back to equality check if right is not iterable.

    Args:
        left: The value to check for membership
        right: The iterable to check membership in

    Returns:
        bool: True if left is in right, otherwise False
    """
    try:
        return left in right
    except TypeError:
        # If right isn't iterable, fall back to equality
        return left == right


def operator_curry(operator_name):
    """Create a curried operator function for peewee fields.

    Args:
        operator_name (str): Name of the operator method to curry

    Returns:
        function: Curried operator function
    """

    def inner(field, value):
        return getattr(field, operator_name)(value)

    return inner


def is_null_operator(field, value):
    """Peewee null check operator.

    Args:
        field: The Peewee field to check
        value: String value ('true' or 'false') indicating null check

    Returns:
        Peewee expression for null check
    """
    return field.is_null(value == "true")


def generic_is_null_operator(left, right):
    """Generic null check operator for iterables.

    Args:
        left: The value to check for null
        right: String value ('true' or 'false') indicating null check type

    Returns:
        bool: True if null check condition is met
    """
    is_null_check = right == "true"
    return (left is None) if is_null_check else (left is not None)
