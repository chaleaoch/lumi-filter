import datetime
import decimal


class FilterField:
    """Base class for filter fields with common functionality.

    This class provides the foundation for all filter field types,
    handling basic parsing and validation operations.

    :param request_arg_name: Name of the request argument
    :type request_arg_name: str or None
    :param source: Source field or attribute name
    :type source: str or None
    """

    SUPPORTED_LOOKUP_EXPR = frozenset({"", "!", "gt", "lt", "gte", "lte", "in", "nin"})

    def __init__(self, request_arg_name=None, source=None):
        self.request_arg_name = request_arg_name
        self.source = source

    def parse_value(self, value):
        """Parse and validate the input value.

        :param value: The input value to parse
        :return: Tuple of (parsed_value, is_valid)
        :rtype: tuple
        """
        return value, True


class IntField(FilterField):
    """Integer field filter.

    Handles parsing and validation of integer values for filtering operations.
    Supports comparison operations like equality, greater than, less than, etc.
    """

    SUPPORTED_LOOKUP_EXPR = frozenset({"", "!", "gt", "lt", "gte", "lte"})

    def parse_value(self, value):
        try:
            return int(value), True
        except (ValueError, TypeError):
            return None, False


class StrField(FilterField):
    """String field filter.

    Handles parsing and validation of string values for filtering operations.
    Supports text matching operations including contains, equality, and comparisons.
    """

    SUPPORTED_LOOKUP_EXPR = frozenset({"", "!", "gt", "lt", "gte", "lte", "in", "nin"})


class DecimalField(FilterField):
    """Decimal field filter.

    Handles parsing and validation of decimal values for filtering operations.
    Provides precise decimal arithmetic for financial and scientific calculations.
    """

    SUPPORTED_LOOKUP_EXPR = frozenset({"", "!", "gt", "lt", "gte", "lte"})

    def parse_value(self, value):
        try:
            return decimal.Decimal(value), True
        except (ValueError, TypeError, decimal.InvalidOperation):
            return None, False


class BooleanField(FilterField):
    """Boolean field filter.

    Handles parsing and validation of boolean values for filtering operations.
    Accepts various string representations of boolean values including
    'true', 'false', '1', '0', 'yes', 'no', 'on', 'off'.
    """

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
    """Date field filter.

    Handles parsing and validation of date values for filtering operations.
    Accepts datetime.date objects or ISO format date strings (YYYY-MM-DD).
    """

    SUPPORTED_LOOKUP_EXPR = frozenset({"", "!", "gt", "lt", "gte", "lte"})

    def parse_value(self, value):
        if isinstance(value, datetime.date):
            return value, True
        try:
            return datetime.datetime.strptime(value, "%Y-%m-%d").date(), True
        except (ValueError, TypeError):
            return None, False


class DateTimeField(FilterField):
    """DateTime field filter.

    Handles parsing and validation of datetime values for filtering operations.
    Accepts datetime.datetime objects or ISO format datetime strings (YYYY-MM-DDTHH:MM:SS).
    """

    SUPPORTED_LOOKUP_EXPR = frozenset({"", "!", "gt", "lt", "gte", "lte"})

    def parse_value(self, value):
        if isinstance(value, datetime.datetime):
            return value, True
        try:
            return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S"), True
        except (ValueError, TypeError):
            return None, False
