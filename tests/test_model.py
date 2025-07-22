"""
Test Model class core functionality

This file tests:
- Model creation and initialization
- Filtering functionality
- Sorting functionality
- Method chaining
"""

import decimal

from lumi_filter.field import BooleanField, DecimalField, IntField, StrField
from lumi_filter.model import Model


class TestBasicModel:
    """Test basic model functionality"""

    def test_model_init(self, sample_dict_data, sample_request_args):
        """Test model initialization"""
        model = Model(sample_dict_data, sample_request_args)
        assert model.data == sample_dict_data
        assert model.request_args == sample_request_args

    def test_model_result(self, sample_dict_data, empty_request_args):
        """Test getting results"""
        model = Model(sample_dict_data, empty_request_args)
        result = model.result()
        assert result == sample_dict_data


class SimpleFilterModel(Model):
    """Simple filter model for testing"""

    id = IntField()
    name = StrField()
    age = IntField()
    active = BooleanField()
    salary = DecimalField()


class TestSimpleFilterModel:
    """Test simple filter model"""

    def test_filter_by_name(self, sample_dict_data):
        """Test filtering by name"""
        request_args = {"name": "Alice"}
        model = SimpleFilterModel(sample_dict_data, request_args)
        filtered_data = list(model.filter().result())

        assert len(filtered_data) == 1
        assert filtered_data[0]["name"] == "Alice"

    def test_filter_by_age_gte(self, sample_dict_data):
        """Test filtering by age greater than or equal to"""
        request_args = {"age__gte": "30"}
        model = SimpleFilterModel(sample_dict_data, request_args)
        filtered_data = list(model.filter().result())

        assert len(filtered_data) == 2
        ages = [item["age"] for item in filtered_data]
        assert all(age >= 30 for age in ages)

    def test_filter_by_active(self, sample_dict_data):
        """Test filtering by active status"""
        request_args = {"active": "true"}
        model = SimpleFilterModel(sample_dict_data, request_args)
        filtered_data = list(model.filter().result())

        assert len(filtered_data) == 3
        assert all(item["active"] is True for item in filtered_data)

    def test_filter_by_salary_range(self, sample_dict_data):
        """Test filtering by salary range"""
        request_args = {"salary__gte": "5000", "salary__lt": "6000"}
        model = SimpleFilterModel(sample_dict_data, request_args)
        filtered_data = list(model.filter().result())

        assert len(filtered_data) == 2
        for item in filtered_data:
            salary = item["salary"]
            assert decimal.Decimal("5000") <= salary < decimal.Decimal("6000")

    def test_multiple_filters(self, sample_dict_data):
        """Test multiple filters"""
        request_args = {"active": "true", "age__gte": "30"}
        model = SimpleFilterModel(sample_dict_data, request_args)
        filtered_data = list(model.filter().result())

        assert len(filtered_data) == 2
        for item in filtered_data:
            assert item["active"] is True
            assert item["age"] >= 30

    def test_no_matching_filters(self, sample_dict_data):
        """Test filters with no matches"""
        request_args = {"name": "NonExistent"}
        model = SimpleFilterModel(sample_dict_data, request_args)
        filtered_data = list(model.filter().result())

        assert len(filtered_data) == 0

    def test_invalid_field_ignored(self, sample_dict_data):
        """Test invalid fields are ignored"""
        request_args = {"invalid_field": "value", "name": "Alice"}
        model = SimpleFilterModel(sample_dict_data, request_args)
        filtered_data = list(model.filter().result())

        # Should only apply name filter, ignore invalid_field
        assert len(filtered_data) == 1
        assert filtered_data[0]["name"] == "Alice"

    def test_invalid_value_ignored(self, sample_dict_data):
        """Test invalid values are ignored"""
        request_args = {
            "age": "invalid_age",  # Invalid integer value
            "name": "Alice",
        }
        model = SimpleFilterModel(sample_dict_data, request_args)
        filtered_data = list(model.filter().result())

        # Should only apply name filter, ignore invalid age
        assert len(filtered_data) == 1
        assert filtered_data[0]["name"] == "Alice"


class TestModelOrdering:
    """Test model ordering functionality"""

    def test_order_by_age_asc(self, sample_dict_data):
        """Test ordering by age ascending"""
        request_args = {"ordering": "age"}
        model = SimpleFilterModel(sample_dict_data, request_args)
        ordered_data = list(model.order().result())

        ages = [item["age"] for item in ordered_data]
        assert ages == sorted(ages)

    def test_order_by_age_desc(self, sample_dict_data):
        """Test ordering by age descending"""
        request_args = {"ordering": "-age"}
        model = SimpleFilterModel(sample_dict_data, request_args)
        ordered_data = list(model.order().result())

        ages = [item["age"] for item in ordered_data]
        assert ages == sorted(ages, reverse=True)

    def test_order_by_name(self, sample_dict_data):
        """Test ordering by name"""
        request_args = {"ordering": "name"}
        model = SimpleFilterModel(sample_dict_data, request_args)
        ordered_data = list(model.order().result())

        names = [item["name"] for item in ordered_data]
        assert names == sorted(names)

    def test_multiple_ordering(self, sample_dict_data):
        """Test multiple field ordering"""
        # Add a record with the same age to test multiple field ordering
        test_data = sample_dict_data + [
            {
                "id": 5,
                "name": "Eve",
                "age": 30,
                "active": True,
                "salary": decimal.Decimal("5200.00"),
            }
        ]

        request_args = {"ordering": "age,name"}
        model = SimpleFilterModel(test_data, request_args)
        ordered_data = list(model.order().result())

        # Check if records with the same age are sorted by name
        age_30_records = [item for item in ordered_data if item["age"] == 30]
        names_age_30 = [item["name"] for item in age_30_records]
        assert names_age_30 == sorted(names_age_30)

    def test_no_ordering(self, sample_dict_data):
        """Test no ordering parameters"""
        request_args = {}
        model = SimpleFilterModel(sample_dict_data, request_args)
        ordered_data = list(model.order().result())

        # Should maintain original order
        assert ordered_data == sample_dict_data

    def test_invalid_ordering_field(self, sample_dict_data):
        """Test invalid ordering field"""
        request_args = {"ordering": "invalid_field"}
        model = SimpleFilterModel(sample_dict_data, request_args)
        ordered_data = list(model.order().result())

        # Should maintain original order without error
        assert ordered_data == sample_dict_data


class TestModelChaining:
    """Test model method chaining"""

    def test_filter_then_order(self, sample_dict_data):
        """Test filter then order"""
        request_args = {"active": "true", "ordering": "-age"}
        model = SimpleFilterModel(sample_dict_data, request_args)
        result = list(model.filter().order().result())

        # Check filter result: only active users
        assert all(item["active"] is True for item in result)

        # Check order result: by age descending
        ages = [item["age"] for item in result]
        assert ages == sorted(ages, reverse=True)

    def test_order_then_filter(self, sample_dict_data):
        """Test order then filter (note: order matters for list data)"""
        request_args = {"age__gte": "30", "ordering": "name"}
        model = SimpleFilterModel(sample_dict_data, request_args)
        result = list(model.order().filter().result())

        # Check filter result: age >= 30
        assert all(item["age"] >= 30 for item in result)

        # Note: order then filter result may differ from filter then order
        assert len(result) >= 1


class TestModelEdgeCases:
    """Test model edge cases"""

    def test_empty_data(self, empty_request_args):
        """Test empty data"""
        empty_data = []
        model = SimpleFilterModel(empty_data, empty_request_args)
        result = list(model.filter().order().result())

        assert result == []

    def test_empty_request_args(self, sample_dict_data):
        """Test empty request arguments"""
        model = SimpleFilterModel(sample_dict_data, {})
        result = list(model.filter().order().result())

        assert result == sample_dict_data

    def test_cls_filter_method(self, sample_dict_data):
        """Test class method filtering"""
        request_args = {"name": "Alice"}
        filtered_data = SimpleFilterModel.cls_filter(sample_dict_data, request_args)
        result = list(filtered_data)

        assert len(result) == 1
        assert result[0]["name"] == "Alice"

    def test_cls_order_method(self, sample_dict_data):
        """Test class method ordering"""
        request_args = {"ordering": "age"}
        ordered_data = SimpleFilterModel.cls_order(sample_dict_data, request_args)
        result = list(ordered_data)

        ages = [item["age"] for item in result]
        assert ages == sorted(ages)
