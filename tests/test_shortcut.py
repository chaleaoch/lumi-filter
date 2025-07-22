"""
Test shortcut module functionality

This file tests:
- AutoQueryModel creation and functionality
- compatible_request_args function
- Error handling in shortcut functions
"""

import datetime
import decimal

import pytest

from lumi_filter.shortcut import AutoQueryModel, compatible_request_args


class TestCompatibleRequestArgs:
    """Test compatible_request_args function"""

    def test_basic_equality_operator(self):
        """Test basic equality operator conversion"""
        request_args = {"name(==)": "john"}
        result = compatible_request_args(request_args)
        expected = {"name": "john"}
        assert result == expected

    def test_not_equal_operator(self):
        """Test not equal operator conversion"""
        request_args = {"status(!=)": "inactive"}
        result = compatible_request_args(request_args)
        expected = {"status!": "inactive"}
        assert result == expected

    def test_greater_than_equal_operator(self):
        """Test greater than or equal operator conversion"""
        request_args = {"age(>=)": "25"}
        result = compatible_request_args(request_args)
        expected = {"age__gte": "25"}
        assert result == expected

    def test_less_than_equal_operator(self):
        """Test less than or equal operator conversion"""
        request_args = {"salary(<=)": "50000"}
        result = compatible_request_args(request_args)
        expected = {"salary__lte": "50000"}
        assert result == expected

    def test_greater_than_operator(self):
        """Test greater than operator conversion"""
        request_args = {"score(>)": "80"}
        result = compatible_request_args(request_args)
        expected = {"score__gt": "80"}
        assert result == expected

    def test_less_than_operator(self):
        """Test less than operator conversion"""
        request_args = {"price(<)": "100"}
        result = compatible_request_args(request_args)
        expected = {"price__lt": "100"}
        assert result == expected

    def test_like_operator(self):
        """Test LIKE operator conversion"""
        request_args = {"description(LIKE)": "%python%"}
        result = compatible_request_args(request_args)
        expected = {"description__in": "python"}  # Should strip % characters
        assert result == expected

    def test_ilike_operator(self):
        """Test ILIKE operator conversion"""
        request_args = {"title(ILIKE)": "%manager%"}
        result = compatible_request_args(request_args)
        expected = {"title__iin": "manager"}  # Should strip % characters
        assert result == expected

    def test_multiple_operators(self):
        """Test multiple operators in single request"""
        request_args = {
            "name(==)": "john",
            "age(>=)": "25",
            "salary(<=)": "100000",
            "status(!=)": "inactive",
        }
        result = compatible_request_args(request_args)
        expected = {
            "name": "john",
            "age__gte": "25",
            "salary__lte": "100000",
            "status!": "inactive",
        }
        assert result == expected

    def test_unsupported_operator_raises_error(self):
        """Test that unsupported operators raise ValueError"""
        request_args = {"field(INVALID)": "value"}
        with pytest.raises(ValueError, match="Unsupported lookup expression: INVALID"):
            compatible_request_args(request_args)

    def test_like_with_short_value(self):
        """Test LIKE operator with short value (<=2 chars)"""
        request_args = {"code(LIKE)": "%A%"}
        result = compatible_request_args(request_args)
        expected = {"code__in": "A"}  # Should not strip if result would be too short
        assert result == expected

    def test_empty_request_args(self):
        """Test empty request args"""
        request_args = {}
        result = compatible_request_args(request_args)
        assert result == {}


class TestAutoQueryModelWithDictData:
    """Test AutoQueryModel with dictionary data"""

    @property
    def sample_data(self):
        """Sample dictionary data for testing"""
        return [
            {
                "id": 1,
                "name": "Alice",
                "age": 28,
                "salary": decimal.Decimal("75000"),
                "is_active": True,
                "join_date": datetime.date(2020, 1, 15),
                "profile": {
                    "department": "Engineering",
                    "position": "Senior Developer",
                },
            },
            {
                "id": 2,
                "name": "Bob",
                "age": 32,
                "salary": decimal.Decimal("85000"),
                "is_active": True,
                "join_date": datetime.date(2019, 6, 10),
                "profile": {"department": "Marketing", "position": "Manager"},
            },
        ]

    def test_autoquery_with_flat_fields(self):
        """Test AutoQueryModel with flat dictionary fields"""
        request_args = {"name": "Alice", "ordering": "age"}
        model = AutoQueryModel(self.sample_data, request_args)

        # Test that model was created successfully
        assert hasattr(model, "name")
        assert hasattr(model, "age")
        assert hasattr(model, "salary")
        assert hasattr(model, "is_active")

        # Test filtering
        results = list(model.filter().result())
        assert len(results) == 1
        assert results[0]["name"] == "Alice"

    def test_autoquery_with_nested_fields(self):
        """Test AutoQueryModel with nested dictionary fields"""
        request_args = {"profile.department": "Engineering", "ordering": "name"}
        model = AutoQueryModel(self.sample_data, request_args)

        # Test that nested fields are flattened with underscore
        assert hasattr(model, "profile_department")
        assert hasattr(model, "profile_position")

        # Test filtering
        results = list(model.filter().result())
        assert len(results) == 1
        assert results[0]["profile"]["department"] == "Engineering"

    def test_autoquery_with_boolean_field(self):
        """Test AutoQueryModel boolean field filtering"""
        request_args = {"is_active": "true", "ordering": "name"}
        model = AutoQueryModel(self.sample_data, request_args)

        results = list(model.filter().order().result())
        assert len(results) == 2  # Both users are active
        assert all(user["is_active"] for user in results)

    def test_autoquery_with_decimal_field(self):
        """Test AutoQueryModel decimal field filtering"""
        request_args = {"salary__gte": "80000", "ordering": "salary"}
        model = AutoQueryModel(self.sample_data, request_args)

        results = list(model.filter().order().result())
        assert len(results) == 1
        assert results[0]["name"] == "Bob"
        assert results[0]["salary"] >= decimal.Decimal("80000")

    def test_autoquery_with_date_field(self):
        """Test AutoQueryModel date field filtering"""
        request_args = {"join_date__gte": "2020-01-01", "ordering": "join_date"}
        model = AutoQueryModel(self.sample_data, request_args)

        results = list(model.filter().order().result())
        assert len(results) == 1
        assert results[0]["name"] == "Alice"
        assert results[0]["join_date"] >= datetime.date(2020, 1, 1)

    def test_autoquery_empty_data_raises_error(self):
        """Test that empty data raises ValueError"""
        empty_data = []
        request_args = {"name": "test"}

        with pytest.raises(ValueError, match="Data cannot be empty for AutoQuery"):
            AutoQueryModel(empty_data, request_args)

    def test_autoquery_unsupported_data_type(self):
        """Test that unsupported data types raise TypeError"""
        invalid_data = "not a list or ModelSelect"
        request_args = {"test": "value"}

        with pytest.raises(TypeError, match="Unsupported data type for AutoQuery"):
            AutoQueryModel(invalid_data, request_args)

    def test_autoquery_ordering_multiple_fields(self):
        """Test AutoQueryModel with multiple field ordering"""
        request_args = {"ordering": "is_active,-salary"}
        model = AutoQueryModel(self.sample_data, request_args)

        results = list(model.order().result())
        assert len(results) == 2
        # Both users have is_active=True, so should be ordered by salary descending
        assert results[0]["name"] == "Bob"  # Higher salary
        assert results[1]["name"] == "Alice"  # Lower salary

    def test_autoquery_with_complex_nested_structure(self):
        """Test AutoQueryModel with complex nested structures"""
        complex_data = [
            {
                "id": 1,
                "user": {
                    "personal": {"name": "John", "age": 30},
                    "work": {"department": "IT", "salary": decimal.Decimal("90000")},
                },
            }
        ]

        request_args = {"user_personal_name": "John", "ordering": "id"}
        model = AutoQueryModel(complex_data, request_args)

        # Test that deeply nested fields are flattened
        assert hasattr(model, "user_personal_name")
        assert hasattr(model, "user_personal_age")
        assert hasattr(model, "user_work_department")
        assert hasattr(model, "user_work_salary")

        results = list(model.filter().result())
        assert len(results) == 1
        assert results[0]["user"]["personal"]["name"] == "John"


class TestAutoQueryModelEdgeCases:
    """Test edge cases and error conditions"""

    def test_autoquery_with_none_values(self):
        """Test AutoQueryModel handling None values in data"""
        data_with_none = [
            {"id": 1, "name": "Alice", "description": None, "score": 85},
            {"id": 2, "name": "Bob", "description": "Good employee", "score": None},
        ]

        request_args = {"name": "Alice", "ordering": "id"}
        model = AutoQueryModel(data_with_none, request_args)

        results = list(model.filter().result())
        assert len(results) == 1
        assert results[0]["name"] == "Alice"
        assert results[0]["description"] is None

    def test_autoquery_field_type_detection(self):
        """Test that field types are correctly detected from data"""
        data = [
            {
                "string_field": "text",
                "int_field": 42,
                "decimal_field": decimal.Decimal("123.45"),
                "bool_field": True,
                "date_field": datetime.date(2023, 1, 1),
                "datetime_field": datetime.datetime(2023, 1, 1, 12, 0, 0),
            }
        ]

        request_args = {}
        model = AutoQueryModel(data, request_args)

        # Check that correct field types were assigned by using getattr
        from lumi_filter.field import (
            BooleanField,
            DateField,
            DateTimeField,
            DecimalField,
            IntField,
            StrField,
        )

        assert isinstance(getattr(model.__class__, "string_field"), StrField)
        assert isinstance(getattr(model.__class__, "int_field"), IntField)
        assert isinstance(getattr(model.__class__, "decimal_field"), DecimalField)
        assert isinstance(getattr(model.__class__, "bool_field"), BooleanField)
        assert isinstance(getattr(model.__class__, "date_field"), DateField)
        assert isinstance(getattr(model.__class__, "datetime_field"), DateTimeField)
