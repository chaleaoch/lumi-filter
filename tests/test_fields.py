"""
Test FilterField and its subclasses basic functionality

This file tests various field types for:
- Value parsing
- Validation logic
- Supported query expressions
"""

import datetime
import decimal

import pytest

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
    """Test basic FilterField class"""

    def test_init_with_defaults(self):
        """Test default initialization"""
        field = FilterField()
        assert field.request_arg_name is None
        assert field.source is None

    def test_init_with_params(self):
        """Test initialization with parameters"""
        field = FilterField(request_arg_name="test_field", source="test_source")
        assert field.request_arg_name == "test_field"
        assert field.source == "test_source"

    def test_supported_lookup_expr(self):
        """Test supported query expressions"""
        field = FilterField()
        expected = {"", "!", "gt", "lt", "gte", "lte", "in", "nin"}
        assert field.SUPPORTED_LOOKUP_EXPR == expected

    def test_parse_value_default(self):
        """Test default value parsing"""
        field = FilterField()
        value, is_valid = field.parse_value("test_value")
        assert value == "test_value"
        assert is_valid is True


class TestIntField:
    """Test IntField class"""

    def test_supported_lookup_expr(self):
        """Test supported query expressions"""
        field = IntField()
        expected = {"", "!", "gt", "lt", "gte", "lte"}
        assert field.SUPPORTED_LOOKUP_EXPR == expected

    @pytest.mark.parametrize(
        "input_value,expected_value,expected_valid",
        [
            ("123", 123, True),
            (456, 456, True),
            ("0", 0, True),
            ("-10", -10, True),
            ("abc", None, False),
            ("", None, False),
            (None, None, False),
            ("12.34", None, False),
        ],
    )
    def test_parse_value(self, input_value, expected_value, expected_valid):
        """Test parsing various input values"""
        field = IntField()
        value, is_valid = field.parse_value(input_value)
        assert value == expected_value
        assert is_valid == expected_valid


class TestStrField:
    """Test StrField class"""

    def test_supported_lookup_expr(self):
        """Test supported query expressions"""
        field = StrField()
        expected = {"", "!", "gt", "lt", "gte", "lte", "in", "nin"}
        assert field.SUPPORTED_LOOKUP_EXPR == expected


class TestDecimalField:
    """Test DecimalField class"""

    def test_supported_lookup_expr(self):
        """Test supported query expressions"""
        field = DecimalField()
        expected = {"", "!", "gt", "lt", "gte", "lte"}
        assert field.SUPPORTED_LOOKUP_EXPR == expected

    @pytest.mark.parametrize(
        "input_value,expected_value,expected_valid",
        [
            ("123.45", decimal.Decimal("123.45"), True),
            ("0", decimal.Decimal("0"), True),
            ("10", decimal.Decimal("10"), True),
            (decimal.Decimal("99.99"), decimal.Decimal("99.99"), True),
            ("abc", None, False),
            ("", None, False),
            (None, None, False),
        ],
    )
    def test_parse_value(self, input_value, expected_value, expected_valid):
        """Test parsing various input values"""
        field = DecimalField()
        value, is_valid = field.parse_value(input_value)
        assert value == expected_value
        assert is_valid == expected_valid


class TestBooleanField:
    """Test BooleanField class"""

    def test_supported_lookup_expr(self):
        """Test supported query expressions"""
        field = BooleanField()
        expected = {""}
        assert field.SUPPORTED_LOOKUP_EXPR == expected

    @pytest.mark.parametrize(
        "input_value,expected_value,expected_valid",
        [
            (True, True, True),
            (False, False, True),
            ("true", True, True),
            ("false", False, True),
            ("True", True, True),
            ("False", False, True),
            ("1", True, True),
            ("0", False, True),
            ("yes", True, True),
            ("no", False, True),
            ("on", True, True),
            ("off", False, True),
            ("invalid", None, False),
            ("", None, False),
            (None, None, False),
        ],
    )
    def test_parse_value(self, input_value, expected_value, expected_valid):
        """Test parsing various input values"""
        field = BooleanField()
        value, is_valid = field.parse_value(input_value)
        assert value == expected_value
        assert is_valid == expected_valid


class TestDateField:
    """Test DateField class"""

    def test_supported_lookup_expr(self):
        """Test supported query expressions"""
        field = DateField()
        expected = {"", "!", "gt", "lt", "gte", "lte"}
        assert field.SUPPORTED_LOOKUP_EXPR == expected

    @pytest.mark.parametrize(
        "input_value,expected_value,expected_valid",
        [
            ("2024-01-01", datetime.date(2024, 1, 1), True),
            ("2023-12-31", datetime.date(2023, 12, 31), True),
            (datetime.date(2024, 1, 1), datetime.date(2024, 1, 1), True),
            ("invalid-date", None, False),
            ("2024-13-01", None, False),  # Invalid month
            ("", None, False),
            (None, None, False),
        ],
    )
    def test_parse_value(self, input_value, expected_value, expected_valid):
        """Test parsing various input values"""
        field = DateField()
        value, is_valid = field.parse_value(input_value)
        assert value == expected_value
        assert is_valid == expected_valid


class TestDateTimeField:
    """Test DateTimeField class"""

    def test_supported_lookup_expr(self):
        """Test supported query expressions"""
        field = DateTimeField()
        expected = {"", "!", "gt", "lt", "gte", "lte"}
        assert field.SUPPORTED_LOOKUP_EXPR == expected

    @pytest.mark.parametrize(
        "input_value,expected_value,expected_valid",
        [
            ("2024-01-01T10:30:00", datetime.datetime(2024, 1, 1, 10, 30, 0), True),
            (
                datetime.datetime(2024, 1, 1, 10, 30, 0),
                datetime.datetime(2024, 1, 1, 10, 30, 0),
                True,
            ),
            ("invalid-datetime", None, False),
            ("2024-01-01", None, False),  # Missing time part
            ("", None, False),
            (None, None, False),
        ],
    )
    def test_parse_value(self, input_value, expected_value, expected_valid):
        """Test parsing various input values"""
        field = DateTimeField()
        value, is_valid = field.parse_value(input_value)
        assert value == expected_value
        assert is_valid == expected_valid
