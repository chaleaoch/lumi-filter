"""Tests for field module."""

import datetime
import decimal

from lumi_filter.field import (
    BooleanField,
    DateField,
    DateTimeField,
    DecimalField,
    FilterField,
    IntField,
    StrField,
)


class TestFilterField:
    """Test the base FilterField class."""

    def test_init_default(self):
        """Test FilterField initialization with default values."""
        field = FilterField()
        assert field.request_arg_name is None
        assert field.source is None

    def test_init_with_params(self):
        """Test FilterField initialization with parameters."""
        field = FilterField(request_arg_name="test_arg", source="test_source")
        assert field.request_arg_name == "test_arg"
        assert field.source == "test_source"

    def test_supported_lookup_expr(self):
        """Test that base FilterField has correct supported lookup expressions."""
        expected = {"", "!", "gt", "lt", "gte", "lte", "in", "contains", "icontains"}
        assert FilterField.SUPPORTED_LOOKUP_EXPR == expected

    def test_parse_value_default(self):
        """Test default parse_value method."""
        field = FilterField()
        value, is_valid = field.parse_value("test")
        assert value == "test"
        assert is_valid is True

    def test_parse_value_none(self):
        """Test parse_value with None."""
        field = FilterField()
        value, is_valid = field.parse_value(None)
        assert value is None
        assert is_valid is True


class TestIntField:
    """Test the IntField class."""

    def test_supported_lookup_expr(self):
        """Test IntField supported lookup expressions."""
        expected = {"", "!", "gt", "lt", "gte", "lte", "in"}
        assert IntField.SUPPORTED_LOOKUP_EXPR == expected

    def test_parse_value_valid_integer(self):
        """Test parsing valid integer values."""
        field = IntField()

        # Positive integer
        value, is_valid = field.parse_value("123")
        assert value == 123
        assert is_valid is True

        # Negative integer
        value, is_valid = field.parse_value("-456")
        assert value == -456
        assert is_valid is True

        # Zero
        value, is_valid = field.parse_value("0")
        assert value == 0
        assert is_valid is True

    def test_parse_value_integer_object(self):
        """Test parsing integer objects."""
        field = IntField()
        value, is_valid = field.parse_value(789)
        assert value == 789
        assert is_valid is True

    def test_parse_value_invalid_string(self):
        """Test parsing invalid string values."""
        field = IntField()

        # Non-numeric string
        value, is_valid = field.parse_value("abc")
        assert value is None
        assert is_valid is False

        # Decimal string
        value, is_valid = field.parse_value("123.45")
        assert value is None
        assert is_valid is False

        # Empty string
        value, is_valid = field.parse_value("")
        assert value is None
        assert is_valid is False

    def test_parse_value_none(self):
        """Test parsing None value."""
        field = IntField()
        value, is_valid = field.parse_value(None)
        assert value is None
        assert is_valid is False

    def test_parse_value_float(self):
        """Test parsing float values."""
        field = IntField()
        value, is_valid = field.parse_value(123.0)
        assert value == 123
        assert is_valid is True


class TestStrField:
    """Test the StrField class."""

    def test_supported_lookup_expr(self):
        """Test StrField supported lookup expressions."""
        expected = {"", "!", "gt", "lt", "gte", "lte", "in", "contains", "icontains"}
        assert StrField.SUPPORTED_LOOKUP_EXPR == expected

    def test_parse_value_string(self):
        """Test parsing string values."""
        field = StrField()

        # Regular string
        value, is_valid = field.parse_value("hello world")
        assert value == "hello world"
        assert is_valid is True

        # Empty string
        value, is_valid = field.parse_value("")
        assert value == ""
        assert is_valid is True

        # String with special characters
        value, is_valid = field.parse_value("!@#$%^&*()")
        assert value == "!@#$%^&*()"
        assert is_valid is True

    def test_parse_value_other_types(self):
        """Test parsing non-string values."""
        field = StrField()

        # Integer
        value, is_valid = field.parse_value(123)
        assert value == 123
        assert is_valid is True

        # None
        value, is_valid = field.parse_value(None)
        assert value is None
        assert is_valid is True


class TestDecimalField:
    """Test the DecimalField class."""

    def test_supported_lookup_expr(self):
        """Test DecimalField supported lookup expressions."""
        expected = {"", "!", "gt", "lt", "gte", "lte", "in"}
        assert DecimalField.SUPPORTED_LOOKUP_EXPR == expected

    def test_parse_value_valid_decimal(self):
        """Test parsing valid decimal values."""
        field = DecimalField()

        # String decimal
        value, is_valid = field.parse_value("123.45")
        assert value == decimal.Decimal("123.45")
        assert is_valid is True

        # Integer string
        value, is_valid = field.parse_value("100")
        assert value == decimal.Decimal("100")
        assert is_valid is True

        # Negative decimal
        value, is_valid = field.parse_value("-99.99")
        assert value == decimal.Decimal("-99.99")
        assert is_valid is True

    def test_parse_value_decimal_object(self):
        """Test parsing decimal objects."""
        field = DecimalField()
        decimal_value = decimal.Decimal("456.78")
        value, is_valid = field.parse_value(decimal_value)
        assert value == decimal_value
        assert is_valid is True

    def test_parse_value_float(self):
        """Test parsing float values."""
        field = DecimalField()
        value, is_valid = field.parse_value(123.45)
        # Floating point precision may cause slight differences
        assert abs(value - decimal.Decimal("123.45")) < decimal.Decimal("0.01")
        assert is_valid is True

    def test_parse_value_integer(self):
        """Test parsing integer values."""
        field = DecimalField()
        value, is_valid = field.parse_value(100)
        assert value == decimal.Decimal("100")
        assert is_valid is True

    def test_parse_value_invalid(self):
        """Test parsing invalid values."""
        field = DecimalField()

        # Invalid string
        value, is_valid = field.parse_value("not_a_number")
        assert value is None
        assert is_valid is False

        # None
        value, is_valid = field.parse_value(None)
        assert value is None
        assert is_valid is False

        # Empty string
        value, is_valid = field.parse_value("")
        assert value is None
        assert is_valid is False


class TestBooleanField:
    """Test the BooleanField class."""

    def test_supported_lookup_expr(self):
        """Test BooleanField supported lookup expressions."""
        expected = {""}
        assert BooleanField.SUPPORTED_LOOKUP_EXPR == expected

    def test_parse_value_boolean(self):
        """Test parsing boolean values."""
        field = BooleanField()

        # True
        value, is_valid = field.parse_value(True)
        assert value is True
        assert is_valid is True

        # False
        value, is_valid = field.parse_value(False)
        assert value is False
        assert is_valid is True

    def test_parse_value_true_strings(self):
        """Test parsing strings that represent True."""
        field = BooleanField()

        true_values = ["true", "1", "yes", "on", "TRUE", "Yes", "ON"]
        for val in true_values:
            value, is_valid = field.parse_value(val)
            assert value is True
            assert is_valid is True

    def test_parse_value_false_strings(self):
        """Test parsing strings that represent False."""
        field = BooleanField()

        false_values = ["false", "0", "no", "off", "FALSE", "No", "OFF"]
        for val in false_values:
            value, is_valid = field.parse_value(val)
            assert value is False
            assert is_valid is True

    def test_parse_value_invalid(self):
        """Test parsing invalid values."""
        field = BooleanField()

        invalid_values = ["maybe", "2", "", None, 123, []]
        for val in invalid_values:
            value, is_valid = field.parse_value(val)
            assert value is None
            assert is_valid is False


class TestDateField:
    """Test the DateField class."""

    def test_supported_lookup_expr(self):
        """Test DateField supported lookup expressions."""
        expected = {"", "!", "gt", "lt", "gte", "lte", "in"}
        assert DateField.SUPPORTED_LOOKUP_EXPR == expected

    def test_parse_value_valid_date_string(self):
        """Test parsing valid date strings."""
        field = DateField()

        # ISO format
        value, is_valid = field.parse_value("2024-01-15")
        expected_date = datetime.date(2024, 1, 15)
        assert value == expected_date
        assert is_valid is True

    def test_parse_value_date_object(self):
        """Test parsing date objects."""
        field = DateField()
        date_obj = datetime.date(2024, 1, 15)
        value, is_valid = field.parse_value(date_obj)
        assert value == date_obj
        assert is_valid is True

    def test_parse_value_datetime_object(self):
        """Test parsing datetime objects."""
        field = DateField()
        datetime_obj = datetime.datetime(2024, 1, 15, 10, 30, 0)
        value, is_valid = field.parse_value(datetime_obj)
        # DateField accepts datetime objects since datetime inherits from date
        # but returns the datetime object as-is
        assert value == datetime_obj
        assert is_valid is True

    def test_parse_value_invalid(self):
        """Test parsing invalid date values."""
        field = DateField()

        invalid_values = ["not-a-date", "2024-13-01", "", None, 123]
        for val in invalid_values:
            value, is_valid = field.parse_value(val)
            assert value is None
            assert is_valid is False


class TestDateTimeField:
    """Test the DateTimeField class."""

    def test_supported_lookup_expr(self):
        """Test DateTimeField supported lookup expressions."""
        expected = {"", "!", "gt", "lt", "gte", "lte", "in"}
        assert DateTimeField.SUPPORTED_LOOKUP_EXPR == expected

    def test_parse_value_valid_datetime_string(self):
        """Test parsing valid datetime strings."""
        field = DateTimeField()

        # ISO format
        value, is_valid = field.parse_value("2024-01-15T10:30:00")
        expected_datetime = datetime.datetime(2024, 1, 15, 10, 30, 0)
        assert value == expected_datetime
        assert is_valid is True

    def test_parse_value_datetime_object(self):
        """Test parsing datetime objects."""
        field = DateTimeField()
        datetime_obj = datetime.datetime(2024, 1, 15, 10, 30, 0)
        value, is_valid = field.parse_value(datetime_obj)
        assert value == datetime_obj
        assert is_valid is True

    def test_parse_value_date_object(self):
        """Test parsing date objects."""
        field = DateTimeField()
        date_obj = datetime.date(2024, 1, 15)
        value, is_valid = field.parse_value(date_obj)
        # DateTimeField currently doesn't handle date objects
        # This test reflects the current implementation
        assert value is None
        assert is_valid is False

    def test_parse_value_invalid(self):
        """Test parsing invalid datetime values."""
        field = DateTimeField()

        invalid_values = ["not-a-datetime", "2024-13-01T25:00:00", "", None, 123]
        for val in invalid_values:
            value, is_valid = field.parse_value(val)
            assert value is None
            assert is_valid is False
