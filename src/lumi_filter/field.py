"""
Filter field classes for handling query parameters and data validation.

This module provides various field types that can parse and validate
input values for different data types, supporting multiple lookup expressions
for flexible filtering operations.
"""

import datetime
import decimal
from typing import Any, Optional, Set, Tuple


class FilterField:
    """
    Base filter field for handling query parameters.

    This is the base class for all filter fields. It provides the basic
    interface for parsing values and defining supported lookup expressions.

    Attributes:
        SUPPORTED_LOOKUP_EXPR: Set of supported lookup expressions for this field
        request_arg_name: Name of the parameter in HTTP requests
        source: Source field or attribute name for data extraction
        name: Field name, usually set by metaclass
    """

    SUPPORTED_LOOKUP_EXPR: Set[str] = {"", "!", "gt", "lt", "gte", "lte", "in", "nin"}

    def __init__(
        self, request_arg_name: Optional[str] = None, source: Any = None
    ) -> None:
        """
        Initialize the filter field.

        Args:
            request_arg_name: Name used in HTTP request parameters
            source: Source field or attribute for data extraction
        """
        self.request_arg_name = request_arg_name
        self.source = source
        self.name: Optional[str] = None  # Set by metaclass

    def parse_value(self, value: Any) -> Tuple[Any, bool]:
        """
        Parse and validate the input value.

        Args:
            value: Raw input value to parse

        Returns:
            Tuple of (parsed_value, is_valid)
            - parsed_value: The converted value
            - is_valid: Boolean indicating if parsing was successful
        """
        return value, True


class IntField(FilterField):
    """
    Integer field with numeric comparison support.

    Supports all numeric comparison operations but excludes string-based
    operations like 'in' and 'nin'.
    """

    SUPPORTED_LOOKUP_EXPR = {"", "!", "gt", "lt", "gte", "lte"}

    def parse_value(self, value: Any) -> Tuple[Optional[int], bool]:
        """
        Parse value as integer.

        Args:
            value: Value to convert to integer

        Returns:
            Tuple of (integer_value, success_flag)
        """
        try:
            return int(value), True
        except (ValueError, TypeError):
            return None, False


class StrField(FilterField):
    """
    String field with full lookup expression support.

    Supports all comparison and substring operations including
    case-sensitive and case-insensitive searches.
    """

    SUPPORTED_LOOKUP_EXPR = {"", "!", "gt", "lt", "gte", "lte", "in", "nin"}


class DecimalField(FilterField):
    """
    Decimal field for precise numeric operations.

    Uses Python's decimal.Decimal for high-precision arithmetic,
    avoiding floating-point precision issues.
    """

    SUPPORTED_LOOKUP_EXPR = {"", "!", "gt", "lt", "gte", "lte"}

    def parse_value(self, value: Any) -> Tuple[Optional[decimal.Decimal], bool]:
        """
        Parse value as Decimal.

        Args:
            value: Value to convert to Decimal

        Returns:
            Tuple of (decimal_value, success_flag)
        """
        try:
            return decimal.Decimal(str(value)), True
        except (ValueError, TypeError, decimal.InvalidOperation):
            return None, False


class BooleanField(FilterField):
    """
    Boolean field with string-to-bool conversion.

    Handles various string representations of boolean values:
    - True: 'true', '1', 'yes', 'on' (case-insensitive)
    - False: 'false', '0', 'no', 'off' (case-insensitive)
    """

    SUPPORTED_LOOKUP_EXPR = {"", "!"}

    def parse_value(self, value: Any) -> Tuple[Optional[bool], bool]:
        """
        Parse value as boolean.

        Args:
            value: Value to convert to boolean

        Returns:
            Tuple of (boolean_value, success_flag)
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
    """
    Date field with ISO format parsing.

    Parses date strings in ISO format (YYYY-MM-DD) and supports
    all comparison operations for date ranges.
    """

    SUPPORTED_LOOKUP_EXPR = {"", "!", "gt", "lt", "gte", "lte"}

    def parse_value(self, value: Any) -> Tuple[Optional[datetime.date], bool]:
        """
        Parse value as date.

        Args:
            value: Value to convert to date (datetime.date or string)

        Returns:
            Tuple of (date_value, success_flag)
        """
        if isinstance(value, datetime.date):
            return value, True

        try:
            return datetime.datetime.strptime(str(value), "%Y-%m-%d").date(), True
        except (ValueError, TypeError):
            return None, False


class DateTimeField(FilterField):
    """
    DateTime field with ISO format parsing.

    Supports multiple datetime formats:
    - ISO format with fromisoformat()
    - Standard format: YYYY-MM-DDTHH:MM:SS
    """

    SUPPORTED_LOOKUP_EXPR = {"", "!", "gt", "lt", "gte", "lte"}

    def parse_value(self, value: Any) -> Tuple[Optional[datetime.datetime], bool]:
        """
        Parse value as datetime.

        Args:
            value: Value to convert to datetime

        Returns:
            Tuple of (datetime_value, success_flag)
        """
        if isinstance(value, datetime.datetime):
            return value, True

        try:
            # Try ISO format first
            return datetime.datetime.fromisoformat(str(value)), True
        except (ValueError, TypeError):
            try:
                # Fallback to common format
                return datetime.datetime.strptime(str(value), "%Y-%m-%dT%H:%M:%S"), True
            except (ValueError, TypeError):
                return None, False
