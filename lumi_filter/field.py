import datetime
import decimal


class FilterField:
    """Base class for filter fields with common functionality.

    This class provides the foundation for all filter field types,
    handling basic parsing and validation operations. It defines the
    interface for field-specific value parsing and validation.

    Attributes:
        SUPPORTED_LOOKUP_EXPR (frozenset): Set of supported lookup expressions
            for filtering operations. Includes equality, negation, comparisons,
            containment checks, and list membership.
        request_arg_name (str or None): Name of the request argument to bind to.
            If None, uses the field name from the filter class.
        source (str or None): Source field or attribute name in the data model.
            If None, uses the field name from the filter class.

    Args:
        request_arg_name (str, optional): Name of the request argument.
            Defaults to None.
        source (str, optional): Source field or attribute name.
            Defaults to None.
    """

    SUPPORTED_LOOKUP_EXPR = frozenset({"", "!", "gt", "lt", "gte", "lte", "in", "contains", "icontains"})

    def __init__(self, request_arg_name=None, source=None):
        self.request_arg_name = request_arg_name
        self.source = source

    def parse_value(self, value):
        """Parse and validate the input value.

        This is the base implementation that accepts any value as valid.
        Subclasses should override this method to provide type-specific
        parsing and validation logic.

        Args:
            value: The input value to parse and validate.

        Returns:
            tuple: A tuple containing (parsed_value, is_valid) where:
                - parsed_value: The parsed and potentially converted value
                - is_valid (bool): True if the value is valid, False otherwise
        """
        return value, True


class IntField(FilterField):
    """Integer field filter for numeric filtering operations.

    Handles parsing and validation of integer values for filtering operations.
    Supports numerical comparison operations like equality, greater than,
    less than, and list membership. String representations of integers
    are automatically converted to int type.

    Attributes:
        SUPPORTED_LOOKUP_EXPR (frozenset): Supported lookup expressions:
            - "" (empty): Exact equality
            - "!": Not equal
            - "gt": Greater than
            - "lt": Less than
            - "gte": Greater than or equal
            - "lte": Less than or equal
            - "in": List membership
    """

    SUPPORTED_LOOKUP_EXPR = frozenset({"", "!", "gt", "lt", "gte", "lte", "in"})

    def parse_value(self, value):
        """Parse string or numeric input to integer.

        Attempts to convert the input value to an integer type.

        Args:
            value: Input value to convert to integer. Can be string, int,
                or other numeric types.

        Returns:
            tuple: A tuple containing (parsed_value, is_valid) where:
                - parsed_value (int or None): The integer value if conversion
                  succeeds, None if it fails
                - is_valid (bool): True if conversion succeeds, False otherwise

        Examples:
            >>> field = IntField()
            >>> field.parse_value("123")
            (123, True)
            >>> field.parse_value("invalid")
            (None, False)
        """
        try:
            return int(value), True
        except (ValueError, TypeError):
            return None, False


class StrField(FilterField):
    """String field filter for text-based filtering operations.

    Handles parsing and validation of string values for filtering operations.
    Supports comprehensive text matching operations including exact matches,
    case-sensitive and case-insensitive containment checks, comparisons,
    and list membership.

    Attributes:
        SUPPORTED_LOOKUP_EXPR (frozenset): Supported lookup expressions:
            - "" (empty): Exact equality (case-sensitive)
            - "!": Not equal
            - "gt": Greater than (lexicographical)
            - "lt": Less than (lexicographical)
            - "gte": Greater than or equal (lexicographical)
            - "lte": Less than or equal (lexicographical)
            - "in": List membership
            - "contains": Case-sensitive substring match
            - "icontains": Case-insensitive substring match
    """

    SUPPORTED_LOOKUP_EXPR = frozenset({"", "!", "gt", "lt", "gte", "lte", "in", "contains", "icontains"})


class DecimalField(FilterField):
    """Decimal field filter for precise numeric filtering operations.

    Handles parsing and validation of decimal values for filtering operations.
    Provides precise decimal arithmetic suitable for financial calculations,
    scientific measurements, and other scenarios requiring exact decimal
    representation without floating-point precision issues.

    Attributes:
        SUPPORTED_LOOKUP_EXPR (frozenset): Supported lookup expressions:
            - "" (empty): Exact equality
            - "!": Not equal
            - "gt": Greater than
            - "lt": Less than
            - "gte": Greater than or equal
            - "lte": Less than or equal
            - "in": List membership
    """

    SUPPORTED_LOOKUP_EXPR = frozenset({"", "!", "gt", "lt", "gte", "lte", "in"})

    def parse_value(self, value):
        """Parse string or numeric input to Decimal.

        Converts the input value to a decimal.Decimal object for precise
        arithmetic operations.

        Args:
            value: Input value to convert to Decimal. Can be string, int,
                float, or other numeric types.

        Returns:
            tuple: A tuple containing (parsed_value, is_valid) where:
                - parsed_value (Decimal or None): The Decimal value if conversion
                  succeeds, None if it fails
                - is_valid (bool): True if conversion succeeds, False otherwise

        Examples:
            >>> field = DecimalField()
            >>> field.parse_value("123.45")
            (Decimal('123.45'), True)
            >>> field.parse_value("invalid")
            (None, False)
        """
        try:
            return decimal.Decimal(value), True
        except (ValueError, TypeError, decimal.InvalidOperation):
            return None, False


class BooleanField(FilterField):
    """Boolean field filter for true/false filtering operations.

    Handles parsing and validation of boolean values for filtering operations.
    Accepts various string representations of boolean values and converts them
    to proper Python boolean types. Supports flexible input formats commonly
    used in web applications and configuration files.

    Attributes:
        SUPPORTED_LOOKUP_EXPR (frozenset): Supported lookup expressions:
            - "" (empty): Exact equality (only supports exact boolean matching)
    """

    SUPPORTED_LOOKUP_EXPR = frozenset({""})

    def parse_value(self, value):
        """Parse various representations to boolean.

        Converts string and boolean inputs to Python boolean values.
        Accepts multiple common representations of true/false values.

        Args:
            value: Input value to convert to boolean. Can be bool, string,
                or other types.

        Returns:
            tuple: A tuple containing (parsed_value, is_valid) where:
                - parsed_value (bool or None): The boolean value if conversion
                  succeeds, None if it fails
                - is_valid (bool): True if conversion succeeds, False otherwise

        Note:
            Accepted true values: 'true', '1', 'yes', 'on' (case-insensitive)
            Accepted false values: 'false', '0', 'no', 'off' (case-insensitive)

        Examples:
            >>> field = BooleanField()
            >>> field.parse_value("true")
            (True, True)
            >>> field.parse_value("0")
            (False, True)
            >>> field.parse_value("invalid")
            (None, False)
        """
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
    """Date field filter for date-only filtering operations.

    Handles parsing and validation of date values for filtering operations.
    Accepts both datetime.date objects and ISO format date strings. Provides
    date-based comparisons without time components.

    Attributes:
        SUPPORTED_LOOKUP_EXPR (frozenset): Supported lookup expressions:
            - "" (empty): Exact date equality
            - "!": Not equal
            - "gt": After date (greater than)
            - "lt": Before date (less than)
            - "gte": On or after date (greater than or equal)
            - "lte": On or before date (less than or equal)
            - "in": Date list membership
    """

    SUPPORTED_LOOKUP_EXPR = frozenset({"", "!", "gt", "lt", "gte", "lte", "in"})

    def parse_value(self, value):
        """Parse datetime.date objects or ISO date strings.

        Converts input to datetime.date objects. Accepts existing date objects
        or parses ISO format date strings (YYYY-MM-DD).

        Args:
            value: Input value to convert to date. Can be datetime.date object
                or string in ISO format (YYYY-MM-DD).

        Returns:
            tuple: A tuple containing (parsed_value, is_valid) where:
                - parsed_value (datetime.date or None): The date value if conversion
                  succeeds, None if it fails
                - is_valid (bool): True if conversion succeeds, False otherwise

        Examples:
            >>> field = DateField()
            >>> field.parse_value("2023-12-25")
            (datetime.date(2023, 12, 25), True)
            >>> field.parse_value("invalid-date")
            (None, False)
        """
        if isinstance(value, datetime.date):
            return value, True
        try:
            return datetime.datetime.strptime(value, "%Y-%m-%d").date(), True
        except (ValueError, TypeError):
            return None, False


class DateTimeField(FilterField):
    """DateTime field filter for date and time filtering operations.

    Handles parsing and validation of datetime values for filtering operations.
    Accepts both datetime.datetime objects and ISO format datetime strings.
    Provides timestamp-based comparisons including both date and time components.

    Attributes:
        SUPPORTED_LOOKUP_EXPR (frozenset): Supported lookup expressions:
            - "" (empty): Exact datetime equality
            - "!": Not equal
            - "gt": After datetime (greater than)
            - "lt": Before datetime (less than)
            - "gte": On or after datetime (greater than or equal)
            - "lte": On or before datetime (less than or equal)
            - "in": DateTime list membership
    """

    SUPPORTED_LOOKUP_EXPR = frozenset({"", "!", "gt", "lt", "gte", "lte", "in"})

    def parse_value(self, value):
        """Parse datetime.datetime objects or ISO datetime strings.

        Converts input to datetime.datetime objects. Accepts existing datetime objects
        or parses ISO format datetime strings (YYYY-MM-DDTHH:MM:SS).

        Args:
            value: Input value to convert to datetime. Can be datetime.datetime object
                or string in ISO format (YYYY-MM-DDTHH:MM:SS).

        Returns:
            tuple: A tuple containing (parsed_value, is_valid) where:
                - parsed_value (datetime.datetime or None): The datetime value if
                  conversion succeeds, None if it fails
                - is_valid (bool): True if conversion succeeds, False otherwise

        Examples:
            >>> field = DateTimeField()
            >>> field.parse_value("2023-12-25T14:30:00")
            (datetime.datetime(2023, 12, 25, 14, 30), True)
            >>> field.parse_value("invalid-datetime")
            (None, False)
        """
        if isinstance(value, datetime.datetime):
            return value, True
        try:
            return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S"), True
        except (ValueError, TypeError):
            return None, False
