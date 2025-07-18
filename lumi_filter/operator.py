"""Generic operators for filtering operations."""


def generic_like_operator(left, right):
    """Case-sensitive contains operator."""
    return str(right) in str(left)


def generic_ilike_operator(left, right):
    """Case-insensitive contains operator."""
    return str(right).lower() in str(left).lower()


def operator_curry(operator_name):
    """Create a curried operator function for peewee fields."""

    def inner(field, value):
        return getattr(field, operator_name)(value)

    return inner


def is_null_operator(field, value):
    """Peewee null check operator."""
    return field.is_null(value == "true")


def generic_is_null_operator(left, right):
    """Generic null check operator for iterables."""
    is_null_check = right == "true"
    return (left is None) if is_null_check else (left is not None)
