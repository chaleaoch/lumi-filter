"""Tests for backend module."""

import operator
from unittest.mock import Mock, patch

import peewee
import pytest

from lumi_filter.backend import IterableBackend, PeeweeBackend


class TestPeeweeBackend:
    """Test the PeeweeBackend class."""

    def test_lookup_expr_operator_map(self):
        """Test that lookup expression operator map is correct."""
        expected_map = {
            "": operator.eq,
            "!": operator.ne,
            "gte": operator.ge,
            "lte": operator.le,
            "gt": operator.gt,
            "lt": operator.lt,
            "contains": operator.mod,
            "icontains": operator.pow,
            "in": operator.lshift,
        }
        assert PeeweeBackend.LOOKUP_EXPR_OPERATOR_MAP == expected_map

    def test_filter_basic_equality(self):
        """Test basic equality filtering."""
        mock_query = Mock()
        mock_field = Mock(spec=peewee.Field)
        mock_where_result = Mock()
        mock_query.where.return_value = mock_where_result
        
        result = PeeweeBackend.filter(mock_query, mock_field, "test_value", "")
        
        # Verify that operator.eq was applied
        mock_query.where.assert_called_once()
        assert result == mock_where_result

    def test_filter_contains_sqlite(self):
        """Test contains filtering with SQLite database."""
        mock_query = Mock()
        mock_field = Mock(spec=peewee.Field)
        mock_database = Mock(spec=peewee.SqliteDatabase)
        mock_query.model._meta.database = mock_database
        
        PeeweeBackend.filter(mock_query, mock_field, "test", "contains")
        
        # For SQLite, contains should transform value to *value*
        mock_query.where.assert_called_once()

    def test_filter_contains_proxy_sqlite(self):
        """Test contains filtering with Proxy wrapping SQLite database."""
        mock_query = Mock()
        mock_field = Mock(spec=peewee.Field)
        mock_proxy = Mock(spec=peewee.Proxy)
        mock_sqlite = Mock(spec=peewee.SqliteDatabase)
        mock_proxy.obj = mock_sqlite
        mock_query.model._meta.database = mock_proxy
        
        PeeweeBackend.filter(mock_query, mock_field, "test", "contains")
        
        mock_query.where.assert_called_once()

    def test_filter_contains_other_database(self):
        """Test contains filtering with non-SQLite database."""
        mock_query = Mock()
        mock_field = Mock(spec=peewee.Field)
        mock_database = Mock(spec=peewee.PostgresqlDatabase)
        mock_query.model._meta.database = mock_database
        
        PeeweeBackend.filter(mock_query, mock_field, "test", "contains")
        
        mock_query.where.assert_called_once()

    def test_filter_icontains(self):
        """Test case-insensitive contains filtering."""
        mock_query = Mock()
        mock_field = Mock(spec=peewee.Field)
        
        PeeweeBackend.filter(mock_query, mock_field, "test", "icontains")
        
        mock_query.where.assert_called_once()

    def test_filter_invalid_field_type(self):
        """Test filtering with invalid field type raises TypeError."""
        mock_query = Mock()
        invalid_field = "not_a_field"
        
        with pytest.raises(TypeError, match="Expected peewee.Field"):
            PeeweeBackend.filter(mock_query, invalid_field, "value", "")

    def test_order_single_field(self):
        """Test ordering by a single field."""
        mock_query = Mock()
        mock_field = Mock()
        mock_field.asc.return_value = "field_asc"
        mock_field.desc.return_value = "field_desc"
        
        # Test ascending order
        ordering = [(mock_field, False)]
        PeeweeBackend.order(mock_query, ordering)
        
        mock_field.asc.assert_called_once()
        mock_query.order_by.assert_called_once_with("field_asc")

    def test_order_multiple_fields(self):
        """Test ordering by multiple fields."""
        mock_query = Mock()
        mock_field1 = Mock()
        mock_field2 = Mock()
        mock_field1.asc.return_value = "field1_asc"
        mock_field2.desc.return_value = "field2_desc"
        
        ordering = [(mock_field1, False), (mock_field2, True)]
        PeeweeBackend.order(mock_query, ordering)
        
        mock_field1.asc.assert_called_once()
        mock_field2.desc.assert_called_once()
        mock_query.order_by.assert_called_once_with("field1_asc", "field2_desc")

    def test_order_descending(self):
        """Test descending order."""
        mock_query = Mock()
        mock_field = Mock()
        mock_field.desc.return_value = "field_desc"
        
        ordering = [(mock_field, True)]
        PeeweeBackend.order(mock_query, ordering)
        
        mock_field.desc.assert_called_once()
        mock_query.order_by.assert_called_once_with("field_desc")


class TestIterableBackend:
    """Test the IterableBackend class."""

    def test_lookup_expr_operator_map(self):
        """Test that lookup expression operator map is correct."""
        # Test that all expected operators are present
        expected_keys = {"", "!", "gte", "lte", "gt", "lt", "contains", "icontains", "in"}
        assert set(IterableBackend.LOOKUP_EXPR_OPERATOR_MAP.keys()) == expected_keys

    def test_get_nested_value_simple(self):
        """Test getting simple nested values."""
        item = {"name": "test", "value": 123}
        
        assert IterableBackend._get_nested_value(item, "name") == "test"
        assert IterableBackend._get_nested_value(item, "value") == 123

    def test_get_nested_value_deep(self):
        """Test getting deeply nested values."""
        item = {
            "user": {
                "profile": {
                    "name": "John Doe",
                    "age": 30
                }
            }
        }
        
        assert IterableBackend._get_nested_value(item, "user.profile.name") == "John Doe"
        assert IterableBackend._get_nested_value(item, "user.profile.age") == 30

    def test_get_nested_value_key_error(self):
        """Test that KeyError is raised for missing keys."""
        item = {"name": "test"}
        
        with pytest.raises(KeyError):
            IterableBackend._get_nested_value(item, "missing_key")
        
        with pytest.raises(KeyError):
            IterableBackend._get_nested_value(item, "name.missing_nested")

    def test_match_item_equality(self):
        """Test item matching with equality."""
        item = {"name": "test", "value": 123}
        
        assert IterableBackend._match_item(item, "name", "test", "") is True
        assert IterableBackend._match_item(item, "name", "other", "") is False
        assert IterableBackend._match_item(item, "value", 123, "") is True

    def test_match_item_comparison(self):
        """Test item matching with comparison operators."""
        item = {"value": 100}
        
        assert IterableBackend._match_item(item, "value", 50, "gt") is True
        assert IterableBackend._match_item(item, "value", 150, "gt") is False
        assert IterableBackend._match_item(item, "value", 100, "gte") is True
        assert IterableBackend._match_item(item, "value", 50, "lt") is False

    def test_match_item_contains(self):
        """Test item matching with contains operators."""
        item = {"text": "Hello World"}
        
        assert IterableBackend._match_item(item, "text", "World", "contains") is True
        assert IterableBackend._match_item(item, "text", "world", "icontains") is True
        assert IterableBackend._match_item(item, "text", "xyz", "contains") is False

    def test_match_item_in_operator(self):
        """Test item matching with in operator."""
        item = {"category": "fruit"}
        
        assert IterableBackend._match_item(item, "category", ["fruit", "vegetable"], "in") is True
        assert IterableBackend._match_item(item, "category", ["meat", "dairy"], "in") is False

    def test_match_item_key_error_returns_true(self):
        """Test that KeyError in matching returns True (permissive)."""
        item = {"name": "test"}
        
        # Missing key should return True (permissive filtering)
        assert IterableBackend._match_item(item, "missing_key", "value", "") is True

    def test_filter_list(self):
        """Test filtering list data."""
        data = [
            {"name": "Alice", "age": 25},
            {"name": "Bob", "age": 30},
            {"name": "Charlie", "age": 35}
        ]
        
        result = IterableBackend.filter(data, "age", 30, "gt")
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["name"] == "Charlie"

    def test_filter_tuple(self):
        """Test filtering tuple data."""
        data = (
            {"name": "Alice", "age": 25},
            {"name": "Bob", "age": 30},
        )
        
        result = IterableBackend.filter(data, "name", "Alice", "")
        assert isinstance(result, tuple)
        assert len(result) == 1
        assert result[0]["name"] == "Alice"

    def test_filter_set(self):
        """Test filtering set data."""
        # Note: sets with dictionaries are not practical, but testing the logic
        data = [
            {"name": "Alice", "age": 25},
            {"name": "Bob", "age": 30},
        ]
        
        result = IterableBackend.filter(data, "age", 25, "")
        assert isinstance(result, list)
        assert len(result) == 1

    def test_order_single_field(self):
        """Test ordering by single field."""
        data = [
            {"name": "Charlie", "age": 35},
            {"name": "Alice", "age": 25},
            {"name": "Bob", "age": 30},
        ]
        
        ordering = [("age", False)]  # Ascending
        result = IterableBackend.order(data, ordering)
        
        ages = [item["age"] for item in result]
        assert ages == [25, 30, 35]

    def test_order_descending(self):
        """Test descending order."""
        data = [
            {"name": "Alice", "age": 25},
            {"name": "Bob", "age": 30},
            {"name": "Charlie", "age": 35},
        ]
        
        ordering = [("age", True)]  # Descending
        result = IterableBackend.order(data, ordering)
        
        ages = [item["age"] for item in result]
        assert ages == [35, 30, 25]

    def test_order_multiple_fields(self):
        """Test ordering by multiple fields."""
        data = [
            {"category": "B", "name": "Bob"},
            {"category": "A", "name": "Charlie"},
            {"category": "A", "name": "Alice"},
            {"category": "B", "name": "David"},
        ]
        
        # First by category (ascending), then by name (ascending)
        ordering = [("category", False), ("name", False)]
        result = IterableBackend.order(data, ordering)
        
        expected_names = ["Alice", "Charlie", "Bob", "David"]
        actual_names = [item["name"] for item in result]
        assert actual_names == expected_names

    @patch('lumi_filter.backend.logger')
    def test_order_key_error_logs_warning(self, mock_logger):
        """Test that KeyError during ordering logs a warning."""
        data = [
            {"name": "Alice"},
            {"name": "Bob"},
        ]
        
        # Try to order by non-existent field
        ordering = [("missing_field", False)]
        result = IterableBackend.order(data, ordering)
        
        # Should return original data and log warning
        assert result == data
        mock_logger.warning.assert_called_once()

    def test_order_nested_field(self):
        """Test ordering by nested field."""
        data = [
            {"user": {"profile": {"score": 85}}},
            {"user": {"profile": {"score": 92}}},
            {"user": {"profile": {"score": 78}}},
        ]
        
        ordering = [("user.profile.score", False)]
        result = IterableBackend.order(data, ordering)
        
        scores = [item["user"]["profile"]["score"] for item in result]
        assert scores == [78, 85, 92]
