"""
Operator functions for filtering operations.

This module provides operator functions used by different backends
to perform filtering and comparison operations on various data types.
"""

from typing import Any, Callable

import peewee


def generic_like_operator(left: Any, right: Any) -> bool:
    """
    Case-sensitive substring search operator.

    Checks if the right operand (needle) is contained within
    the left operand (haystack).

    Args:
        left: The value to search within (haystack)
        right: The value to search for (needle)

    Returns:
        True if right is found in left (case-sensitive)

    Example:
        >>> generic_like_operator("Hello World", "World")
        True
        >>> generic_like_operator("Hello World", "world")
        False
    """
    return str(right) in str(left)


def generic_ilike_operator(left: Any, right: Any) -> bool:
    """
    Case-insensitive substring search operator.

    Checks if the right operand (needle) is contained within
    the left operand (haystack), ignoring case differences.

    Args:
        left: The value to search within (haystack)
        right: The value to search for (needle)

    Returns:
        True if right is found in left (case-insensitive)

    Example:
        >>> generic_ilike_operator("Hello World", "world")
        True
        >>> generic_ilike_operator("Hello World", "WORLD")
        True
    """
    return str(right).lower() in str(left).lower()


def operator_curry(operator_name: str) -> Callable[[peewee.Field, Any], Any]:
    """
    Create a curried operator function for Peewee fields.

    This function creates a wrapper that calls the specified operator
    method on a Peewee field with the given value.

    Args:
        operator_name: Name of the operator method to call on the field

    Returns:
        A function that takes (field, value) and returns the operation result

    Example:
        >>> eq_op = operator_curry('__eq__')
        >>> # Later use: eq_op(field, value) calls field.__eq__(value)
    """

    def inner(field: peewee.Field, value: Any) -> Any:
        """
        Apply the operator to the field with the given value.

        Args:
            field: Peewee field to operate on
            value: Value to use in the operation

        Returns:
            Result of calling the operator method on the field
        """
        return getattr(field, operator_name)(value)

    return inner


def is_null_operator(field: peewee.Field, value: Any) -> Any:
    """
    Check if a Peewee field is null based on string value.

    Converts the value to a string and checks if it equals "true"
    to determine whether to check for null or not-null.

    Args:
        field: Peewee field to check
        value: String value ("true" for IS NULL, others for IS NOT NULL)

    Returns:
        Peewee expression for null check

    Example:
        >>> is_null_operator(User.name, "true")   # User.name IS NULL
        >>> is_null_operator(User.name, "false")  # User.name IS NOT NULL
    """
    return field.is_null(str(value).lower() == "true")


def generic_is_null_operator(left: Any, right: Any) -> bool:
    """
    Generic null check for non-ORM data.

    Performs null checking on arbitrary Python values,
    useful for filtering plain Python data structures.

    Args:
        left: The value to check for null/None
        right: Control value ("true" for None check, others for not-None check)

    Returns:
        True if the null condition matches, False otherwise

    Example:
        >>> generic_is_null_operator(None, "true")    # True
        >>> generic_is_null_operator("value", "true") # False
        >>> generic_is_null_operator(None, "false")   # False
        >>> generic_is_null_operator("value", "false") # True
    """
    if str(right).lower() == "true":
        return left is None
    else:
        return left is not None
