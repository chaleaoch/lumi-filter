"""Tests for shortcut module."""

from unittest.mock import Mock, patch

import peewee
import pytest

from lumi_filter.field import IntField, StrField
from lumi_filter.shortcut import AutoQueryModel, compatible_request_args


class TestAutoQueryModel:
    """Test the AutoQueryModel class."""

    def test_auto_query_with_peewee_select(self, setup_test_db):
        """Test AutoQueryModel with Peewee select query."""
        from tests.conftest import Product

        query = Product.select()
        request_args = {"name": "test"}

        # Create auto model
        auto_model = AutoQueryModel(query, request_args)

        # Should have generated fields for Product model
        assert hasattr(auto_model, "__supported_query_key_field_dict__")
        assert "name" in auto_model.__supported_query_key_field_dict__
        assert "price" in auto_model.__supported_query_key_field_dict__

    def test_auto_query_with_selected_columns(self, setup_test_db):
        """Test AutoQueryModel with specific selected columns."""
        from tests.conftest import Product

        query = Product.select(Product.name, Product.price)
        request_args = {"name": "test"}

        auto_model = AutoQueryModel(query, request_args)

        # Should have fields for selected columns
        assert "name" in auto_model.__supported_query_key_field_dict__
        assert "price" in auto_model.__supported_query_key_field_dict__

    def test_auto_query_with_alias(self, setup_test_db):
        """Test AutoQueryModel with field aliases."""
        from tests.conftest import Product

        query = Product.select(Product.name.alias("product_name"))
        request_args = {"product_name": "test"}

        auto_model = AutoQueryModel(query, request_args)

        # Should have field with alias name
        assert "product_name" in auto_model.__supported_query_key_field_dict__

    @patch("lumi_filter.shortcut.logger")
    def test_auto_query_unsupported_peewee_field(self, mock_logger, setup_test_db):
        """Test AutoQueryModel with unsupported Peewee field type."""
        # Mock a query with unsupported field type
        mock_query = Mock(spec=peewee.ModelSelect)
        mock_unsupported_field = Mock()
        mock_unsupported_field.__class__ = object  # Unsupported type
        mock_query.selected_columns = [mock_unsupported_field]

        request_args = {}

        # Should log warning but not fail
        AutoQueryModel(mock_query, request_args)

        mock_logger.warning.assert_called_once()
        assert "Unsupported field type" in str(mock_logger.warning.call_args)

    def test_auto_query_with_iterable_data(self, sample_products_data):
        """Test AutoQueryModel with iterable data."""
        request_args = {"name": "test"}

        auto_model = AutoQueryModel(sample_products_data, request_args)

        # Should have generated fields for dictionary keys
        supported_keys = auto_model.__supported_query_key_field_dict__
        assert "name" in supported_keys
        assert "price" in supported_keys
        assert "is_active" in supported_keys

    def test_auto_query_with_nested_data(self):
        """Test AutoQueryModel with nested dictionary data."""
        nested_data = [{"name": "test", "user": {"profile": {"age": 30, "city": "New York"}}}]
        request_args = {"user.profile.age": "30"}

        auto_model = AutoQueryModel(nested_data, request_args)

        # Should have flattened nested fields
        supported_keys = auto_model.__supported_query_key_field_dict__
        assert "name" in supported_keys
        assert "user.profile.age" in supported_keys
        assert "user.profile.city" in supported_keys

    def test_auto_query_empty_data_error(self):
        """Test AutoQueryModel with empty iterable raises error."""
        empty_data = []
        request_args = {}

        with pytest.raises(ValueError, match="Data cannot be empty"):
            AutoQueryModel(empty_data, request_args)

    def test_auto_query_non_dict_data_error(self):
        """Test AutoQueryModel with non-dict iterable raises error."""
        non_dict_data = ["string1", "string2"]
        request_args = {}

        with pytest.raises(TypeError, match="Unsupported data type"):
            AutoQueryModel(non_dict_data, request_args)

    @patch("lumi_filter.shortcut.logger")
    def test_auto_query_unsupported_data_type(self, mock_logger):
        """Test AutoQueryModel with completely unsupported data type."""
        unsupported_data = "string_data"
        request_args = {}

        with pytest.raises(TypeError, match="Unsupported data type"):
            AutoQueryModel(unsupported_data, request_args)

    def test_auto_query_filtering_functionality(self, sample_products_data):
        """Test that AutoQueryModel actually works for filtering."""
        request_args = {"name": "Laptop"}

        auto_model = AutoQueryModel(sample_products_data, request_args)
        result = auto_model.filter().result()

        # Convert to list if needed for testing
        if not isinstance(result, list):
            result = list(result)

        # Should filter correctly
        assert len(result) == 1
        assert result[0]["name"] == "Laptop"

    def test_auto_query_ordering_functionality(self, sample_products_data):
        """Test that AutoQueryModel works for ordering."""
        request_args = {"ordering": "name"}

        auto_model = AutoQueryModel(sample_products_data, request_args)
        result = auto_model.order().result()

        # Should order correctly
        names = [item["name"] for item in result]
        assert names == sorted(names)

    def test_auto_query_field_types(self, sample_products_data):
        """Test that AutoQueryModel generates correct field types."""
        request_args = {}

        auto_model = AutoQueryModel(sample_products_data, request_args)

        # Check that fields were created with correct types based on data
        ordering_fields = auto_model.__ordering_field_map__

        # Name should be string field
        name_field = ordering_fields.get("name")
        assert isinstance(name_field, StrField)

        # ID should be int field
        id_field = ordering_fields.get("id")
        assert isinstance(id_field, IntField)


class TestCompatibleRequestArgs:
    """Test the compatible_request_args function."""

    def test_equality_operator(self):
        """Test conversion of equality operator."""
        args = {"name(==)": "test"}
        result = compatible_request_args(args)
        assert result == {"name": "test"}

    def test_not_equal_operator(self):
        """Test conversion of not equal operator."""
        args = {"name(!=)": "test"}
        result = compatible_request_args(args)
        assert result == {"name!": "test"}

    def test_greater_than_operator(self):
        """Test conversion of greater than operator."""
        args = {"age(>)": "30"}
        result = compatible_request_args(args)
        assert result == {"age__gt": "30"}

    def test_less_than_operator(self):
        """Test conversion of less than operator."""
        args = {"age(<)": "30"}
        result = compatible_request_args(args)
        assert result == {"age__lt": "30"}

    def test_greater_than_equal_operator(self):
        """Test conversion of greater than or equal operator."""
        args = {"age(>=)": "30"}
        result = compatible_request_args(args)
        assert result == {"age__gte": "30"}

    def test_less_than_equal_operator(self):
        """Test conversion of less than or equal operator."""
        args = {"age(<=)": "30"}
        result = compatible_request_args(args)
        assert result == {"age__lte": "30"}

    def test_like_operator(self):
        """Test conversion of LIKE operator."""
        args = {"name(LIKE)": "(apple,orange)"}
        result = compatible_request_args(args)
        assert result == {"name__in": "apple,orange"}

    def test_ilike_operator(self):
        """Test conversion of ILIKE operator."""
        args = {"name(ILIKE)": "(apple,orange)"}
        result = compatible_request_args(args)
        assert result == {"name__iin": "apple,orange"}

    def test_like_operator_short_value(self):
        """Test LIKE operator with short value."""
        args = {"name(LIKE)": "a"}
        result = compatible_request_args(args)
        assert result == {"name__in": "a"}

    def test_multiple_operators(self):
        """Test conversion with multiple operators."""
        args = {"name(==)": "test", "age(>)": "30", "status(!=)": "inactive"}
        result = compatible_request_args(args)
        expected = {"name": "test", "age__gt": "30", "status!": "inactive"}
        assert result == expected

    def test_unsupported_operator_error(self):
        """Test that unsupported operators raise ValueError."""
        args = {"name(UNKNOWN)": "test"}

        with pytest.raises(ValueError, match="Unsupported lookup expression: UNKNOWN"):
            compatible_request_args(args)

    def test_malformed_key_error(self):
        """Test error handling for malformed keys."""
        # Key without closing parenthesis should cause an error
        args = {"name(==": "test"}

        with pytest.raises(ValueError):
            compatible_request_args(args)

    def test_empty_args(self):
        """Test with empty request args."""
        args = {}
        result = compatible_request_args(args)
        assert result == {}

    def test_complex_field_names(self):
        """Test with complex field names."""
        args = {"user_profile_name(==)": "John", "created_at(>=)": "2024-01-01"}
        result = compatible_request_args(args)
        expected = {"user_profile_name": "John", "created_at__gte": "2024-01-01"}
        assert result == expected
