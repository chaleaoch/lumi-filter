def generic_like_operator(left, right):
    return right in left


def generic_ilike_operator(left, right):
    return right.lower() in left.lower()


def operator_curry(operator):
    def inner(field, value):
        return getattr(field, operator)(value)

    return inner


def is_null_operator(field, value):
    return field.is_null(value == "true")


def generic_is_null_operator(left, right):
    if right == "true":
        return left is None
    else:
        return left is not None
