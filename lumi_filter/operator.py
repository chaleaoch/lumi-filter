"""Generic operators for filtering operations.

This module provides generic operator functions for filtering operations
that work across different data sources and backends.
"""


def generic_like_operator(left, right):
    """Case-sensitive contains operator.

    :param left: The value to search in
    :param right: The value to search for
    :return: True if right is contained in left (case-sensitive)
    :rtype: bool
    """
    return str(right) in str(left)


def generic_ilike_operator(left, right):
    """Case-insensitive contains operator.

    :param left: The value to search in
    :param right: The value to search for
    :return: True if right is contained in left (case-insensitive)
    :rtype: bool
    """
    return str(right).lower() in str(left).lower()


def generic_in_operator(left, right):
    # Expect right to be an iterable of candidates, check if left is a member
    try:
        return left in right
    except TypeError:
        # If right isn't iterable, fall back to equality
        return left == right


def operator_curry(operator_name):
    """Create a curried operator function for peewee fields.

    :param operator_name: Name of the operator method to curry
    :type operator_name: str
    :return: Curried operator function
    :rtype: function
    """

    def inner(field, value):
        return getattr(field, operator_name)(value)

    return inner


def is_null_operator(field, value):
    """Peewee null check operator.

    :param field: The Peewee field to check
    :param value: String value ('true' or 'false') indicating null check
    :return: Peewee expression for null check
    """
    return field.is_null(value == "true")


def generic_is_null_operator(left, right):
    """Generic null check operator for iterables.

    :param left: The value to check for null
    :param right: String value ('true' or 'false') indicating null check type
    :return: True if null check condition is met
    :rtype: bool
    """
    is_null_check = right == "true"
    return (left is None) if is_null_check else (left is not None)
