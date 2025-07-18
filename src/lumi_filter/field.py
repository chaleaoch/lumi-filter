import datetime
import decimal


class FilterField:
    """Base class for filter fields with common functionality."""

    SUPPORTED_LOOKUP_EXPR = frozenset({"", "!", "gt", "lt", "gte", "lte", "in", "nin"})

    def __init__(self, request_arg_name=None, source=None):
        self.request_arg_name = request_arg_name
        self.source = source

    def parse_value(self, value):
        """Parse and validate the input value. Returns (parsed_value, is_valid)."""
        return value, True


class IntField(FilterField):
    """Integer field filter."""

    SUPPORTED_LOOKUP_EXPR = frozenset({"", "!", "gt", "lt", "gte", "lte"})

    def parse_value(self, value):
        try:
            return int(value), True
        except (ValueError, TypeError):
            return None, False


class StrField(FilterField):
    """String field filter."""

    SUPPORTED_LOOKUP_EXPR = frozenset({"", "!", "gt", "lt", "gte", "lte", "in", "nin"})


class DecimalField(FilterField):
    """Decimal field filter."""

    SUPPORTED_LOOKUP_EXPR = frozenset({"", "!", "gt", "lt", "gte", "lte"})

    def parse_value(self, value):
        try:
            return decimal.Decimal(value), True
        except (ValueError, TypeError, decimal.InvalidOperation):
            return None, False


class BooleanField(FilterField):
    """Boolean field filter."""

    SUPPORTED_LOOKUP_EXPR = frozenset({""})

    def parse_value(self, value):
        if isinstance(value, bool):
            return value, True
        if isinstance(value, str):
            lower_value = value.lower()
            if lower_value in ("true", "1", "yes", "on"):
                return True, True
            elif lower_value in ("false", "0", "no", "off"):
                return False, True
        return None, False


class DateField(FilterField):
    """Date field filter."""

    SUPPORTED_LOOKUP_EXPR = frozenset({"", "!", "gt", "lt", "gte", "lte"})

    def parse_value(self, value):
        if isinstance(value, datetime.date):
            return value, True
        try:
            return datetime.datetime.strptime(value, "%Y-%m-%d").date(), True
        except (ValueError, TypeError):
            return None, False


class DateTimeField(FilterField):
    """DateTime field filter."""

    SUPPORTED_LOOKUP_EXPR = frozenset({"", "!", "gt", "lt", "gte", "lte"})

    def parse_value(self, value):
        if isinstance(value, datetime.datetime):
            return value, True
        try:
            return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S"), True
        except (ValueError, TypeError):
            return None, False
