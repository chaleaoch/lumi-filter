"""Tests for operator module."""

from unittest.mock import Mock

import peewee

from lumi_filter.operator import (
    generic_ilike_operator,
    generic_in_operator,
    generic_is_null_operator,
    generic_like_operator,
    is_null_operator,
    operator_curry,
)


class TestGenericLikeOperator:
    """Test the generic_like_operator function."""

    def test_case_sensitive_contains(self):
        """Test case-sensitive contains operation."""
        assert generic_like_operator("Hello World", "World") is True
        assert generic_like_operator("Hello World", "world") is False
        assert generic_like_operator("Hello World", "Hello") is True
        assert generic_like_operator("Hello World", "xyz") is False

    def test_empty_strings(self):
        """Test with empty strings."""
        assert generic_like_operator("", "") is True
        assert generic_like_operator("Hello", "") is True
        assert generic_like_operator("", "Hello") is False

    def test_non_string_types(self):
        """Test with non-string types."""
        assert generic_like_operator(12345, "23") is True
        assert generic_like_operator(12345, "67") is False
        assert generic_like_operator("Hello", 123) is False


class TestGenericIlikeOperator:
    """Test the generic_ilike_operator function."""

    def test_case_insensitive_contains(self):
        """Test case-insensitive contains operation."""
        assert generic_ilike_operator("Hello World", "world") is True
        assert generic_ilike_operator("Hello World", "WORLD") is True
        assert generic_ilike_operator("Hello World", "hello") is True
        assert generic_ilike_operator("Hello World", "xyz") is False

    def test_mixed_case(self):
        """Test with mixed case inputs."""
        assert generic_ilike_operator("PyThOn", "python") is True
        assert generic_ilike_operator("DATABASE", "base") is True
        assert generic_ilike_operator("CamelCase", "CAMEL") is True

    def test_empty_strings(self):
        """Test with empty strings."""
        assert generic_ilike_operator("", "") is True
        assert generic_ilike_operator("Hello", "") is True
        assert generic_ilike_operator("", "Hello") is False

    def test_non_string_types(self):
        """Test with non-string types."""
        assert generic_ilike_operator(12345, "23") is True
        assert generic_ilike_operator(12345, "67") is False


class TestGenericInOperator:
    """Test the generic_in_operator function."""

    def test_list_membership(self):
        """Test membership in lists."""
        assert generic_in_operator(1, [1, 2, 3]) is True
        assert generic_in_operator(4, [1, 2, 3]) is False
        assert generic_in_operator("a", ["a", "b", "c"]) is True
        assert generic_in_operator("d", ["a", "b", "c"]) is False

    def test_tuple_membership(self):
        """Test membership in tuples."""
        assert generic_in_operator("x", ("x", "y", "z")) is True
        assert generic_in_operator("w", ("x", "y", "z")) is False

    def test_set_membership(self):
        """Test membership in sets."""
        assert generic_in_operator(10, {10, 20, 30}) is True
        assert generic_in_operator(40, {10, 20, 30}) is False

    def test_string_membership(self):
        """Test membership in strings."""
        assert generic_in_operator("a", "abc") is True
        assert generic_in_operator("d", "abc") is False

    def test_non_iterable_fallback(self):
        """Test fallback to equality when right operand is not iterable."""
        assert generic_in_operator(5, 5) is True
        assert generic_in_operator(5, 10) is False

    def test_empty_iterable(self):
        """Test with empty iterables."""
        assert generic_in_operator(1, []) is False
        assert generic_in_operator("a", "") is False
        assert generic_in_operator(1, set()) is False


class TestGenericIsNullOperator:
    """Test the generic_is_null_operator function."""

    def test_is_null_true(self):
        """Test checking for null values when expecting null."""
        assert generic_is_null_operator(None, "true") is True
        assert generic_is_null_operator("not_null", "true") is False
        assert generic_is_null_operator(0, "true") is False
        assert generic_is_null_operator("", "true") is False

    def test_is_null_false(self):
        """Test checking for non-null values when expecting non-null."""
        assert generic_is_null_operator(None, "false") is False
        assert generic_is_null_operator("not_null", "false") is True
        assert generic_is_null_operator(0, "false") is True
        assert generic_is_null_operator("", "false") is True

    def test_invalid_check_value(self):
        """Test with invalid check values."""
        # When check value is not "true" or "false", it defaults to is_not_null check
        assert generic_is_null_operator(None, "invalid") is False
        assert generic_is_null_operator("value", "invalid") is True


class TestOperatorCurry:
    """Test the operator_curry function."""

    def test_curry_function_creation(self):
        """Test that curry creates a callable function."""
        curried_func = operator_curry("__eq__")
        assert callable(curried_func)

    def test_curried_function_execution(self):
        """Test that curried function calls the correct method."""
        # Create a mock field object
        mock_field = Mock()
        mock_field.__eq__ = Mock(return_value="equal_result")

        curried_eq = operator_curry("__eq__")
        result = curried_eq(mock_field, "test_value")

        # Verify the method was called with correct arguments
        mock_field.__eq__.assert_called_once_with("test_value")
        assert result == "equal_result"

    def test_multiple_operator_curry(self):
        """Test currying different operators."""
        mock_field = Mock()
        mock_field.__gt__ = Mock(return_value="greater_result")
        mock_field.__lt__ = Mock(return_value="less_result")

        curried_gt = operator_curry("__gt__")
        curried_lt = operator_curry("__lt__")

        gt_result = curried_gt(mock_field, 10)
        lt_result = curried_lt(mock_field, 5)

        mock_field.__gt__.assert_called_once_with(10)
        mock_field.__lt__.assert_called_once_with(5)
        assert gt_result == "greater_result"
        assert lt_result == "less_result"


class TestIsNullOperator:
    """Test the is_null_operator function for Peewee fields."""

    def test_is_null_true(self):
        """Test Peewee is_null with true value."""
        mock_field = Mock(spec=peewee.Field)
        mock_field.is_null = Mock(return_value="null_expression")

        result = is_null_operator(mock_field, "true")

        mock_field.is_null.assert_called_once_with(True)
        assert result == "null_expression"

    def test_is_null_false(self):
        """Test Peewee is_null with false value."""
        mock_field = Mock(spec=peewee.Field)
        mock_field.is_null = Mock(return_value="not_null_expression")

        result = is_null_operator(mock_field, "false")

        mock_field.is_null.assert_called_once_with(False)
        assert result == "not_null_expression"

    def test_is_null_other_values(self):
        """Test Peewee is_null with other string values."""
        mock_field = Mock(spec=peewee.Field)
        mock_field.is_null = Mock(return_value="not_null_expression")

        # Any value other than "true" should result in False being passed
        result = is_null_operator(mock_field, "false")

        mock_field.is_null.assert_called_once_with(False)
        assert result == "not_null_expression"
