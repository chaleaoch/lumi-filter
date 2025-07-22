"""
Test Model class core functionality

This file tests:
- Model creation and initialization
- Filtering functionality
- Sorting functionality
- Method chaining
"""

import datetime
import decimal

from lumi_filter.field import BooleanField, DateField, DecimalField, IntField, StrField
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


class UserFilterModel(Model):
    """User filter model - simulates real business scenarios"""

    id = IntField()
    username = StrField()
    email = StrField()
    age = IntField()
    is_active = BooleanField()
    salary = DecimalField()
    join_date = DateField()


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


class TestIntegrationScenarios:
    """Integration test scenarios for complete workflows"""

    @property
    def sample_users(self):
        """Mock user data"""
        return [
            {
                "id": 1,
                "username": "alice_smith",
                "email": "alice@example.com",
                "age": 28,
                "is_active": True,
                "salary": decimal.Decimal("75000.00"),
                "join_date": datetime.date(2020, 1, 15),
            },
            {
                "id": 2,
                "username": "bob_jones",
                "email": "bob@example.com",
                "age": 32,
                "is_active": True,
                "salary": decimal.Decimal("85000.00"),
                "join_date": datetime.date(2019, 6, 10),
            },
            {
                "id": 3,
                "username": "charlie_brown",
                "email": "charlie@company.com",
                "age": 26,
                "is_active": False,
                "salary": decimal.Decimal("65000.00"),
                "join_date": datetime.date(2021, 3, 22),
            },
            {
                "id": 4,
                "username": "diana_prince",
                "email": "diana@example.com",
                "age": 35,
                "is_active": True,
                "salary": decimal.Decimal("95000.00"),
                "join_date": datetime.date(2018, 11, 5),
            },
            {
                "id": 5,
                "username": "eve_wilson",
                "email": "eve@company.com",
                "age": 29,
                "is_active": False,
                "salary": decimal.Decimal("70000.00"),
                "join_date": datetime.date(2020, 8, 18),
            },
        ]

    def test_hr_search_active_employees(self):
        """HR scenario: Search active employees"""
        # Find all active employees, sorted by salary in descending order
        request_args = {"is_active": "true", "ordering": "-salary"}

        model = UserFilterModel(self.sample_users, request_args)
        results = list(model.filter().order().result())

        # Verify results
        assert len(results) == 3  # Only 3 active employees
        assert all(user["is_active"] for user in results)

        # Verify sorting: salary descending
        salaries = [user["salary"] for user in results]
        assert salaries == sorted(salaries, reverse=True)

        # Verify specific results
        assert results[0]["username"] == "diana_prince"  # Highest salary
        assert (
            results[-1]["username"] == "alice_smith"
        )  # Lowest salary (among active employees)

    def test_recruitment_age_filter(self):
        """Recruitment scenario: Filter candidates by age range"""
        # Find users aged between 25-30
        request_args = {"age__gte": "25", "age__lte": "30", "ordering": "age"}

        model = UserFilterModel(self.sample_users, request_args)
        results = list(model.filter().order().result())

        # Verify age range
        assert len(results) == 3
        for user in results:
            assert 25 <= user["age"] <= 30

        # Verify sorting
        ages = [user["age"] for user in results]
        assert ages == [26, 28, 29]  # Ascending order

    def test_payroll_salary_analysis(self):
        """Salary analysis scenario: High-salary employee statistics"""
        # Find active employees with salary above 80000
        request_args = {
            "salary__gte": "80000",
            "is_active": "true",
            "ordering": "username",
        }

        model = UserFilterModel(self.sample_users, request_args)
        results = list(model.filter().order().result())

        # Verify results
        assert len(results) == 2
        for user in results:
            assert user["salary"] >= decimal.Decimal("80000")
            assert user["is_active"] is True

        # Verify sorting: alphabetical order by username
        usernames = [user["username"] for user in results]
        assert usernames == ["bob_jones", "diana_prince"]

    def test_email_domain_search(self):
        """Email domain search scenario"""
        # Find users with company.com domain
        request_args = {"email__in": "company.com", "ordering": "join_date"}

        model = UserFilterModel(self.sample_users, request_args)
        results = list(model.filter().order().result())

        # Verify results
        assert len(results) == 2
        for user in results:
            assert "company.com" in user["email"]

        # Verify sorting: by join date
        join_dates = [user["join_date"] for user in results]
        assert join_dates[0] < join_dates[1]  # Ascending order

    def test_complex_multi_filter_scenario(self):
        """Complex multi-condition filtering scenario"""
        # Business requirement: Find active employees under 30, with salary between 70000-90000, ordered by age ascending
        request_args = {
            "age__lt": "30",
            "is_active": "true",
            "salary__gte": "70000",
            "salary__lte": "90000",
            "ordering": "age",
        }

        model = UserFilterModel(self.sample_users, request_args)
        results = list(model.filter().order().result())

        # Verify all conditions
        assert len(results) == 1
        user = results[0]

        assert user["age"] < 30
        assert user["is_active"] is True
        assert decimal.Decimal("70000") <= user["salary"] <= decimal.Decimal("90000")
        assert user["username"] == "alice_smith"

    def test_no_results_scenario(self):
        """No results scenario: overly strict filtering conditions"""
        # Find users over 50 years old (does not exist in our test data)
        request_args = {"age__gt": "50"}

        model = UserFilterModel(self.sample_users, request_args)
        results = list(model.filter().result())

        assert len(results) == 0

    def test_invalid_input_handling(self):
        """Handle invalid input scenario"""
        # Contains invalid age value and invalid field
        request_args = {
            "age": "invalid_age",  # Invalid age
            "nonexistent_field": "value",  # Non-existent field
            "username": "alice_smith",  # Valid filter condition
            "ordering": "username",
        }

        model = UserFilterModel(self.sample_users, request_args)
        results = list(model.filter().order().result())

        # Should ignore invalid input, only apply valid filter conditions
        assert len(results) == 1
        assert results[0]["username"] == "alice_smith"

    def test_performance_with_large_dataset(self):
        """Large dataset performance test (simulation)"""
        # Create larger dataset
        large_dataset = []
        for i in range(100):
            large_dataset.append(
                {
                    "id": i,
                    "username": f"user_{i}",
                    "email": f"user{i}@example.com",
                    "age": 20 + (i % 40),  # Age 20-59
                    "is_active": i % 3 != 0,  # About 2/3 of users are active
                    "salary": decimal.Decimal(
                        str(50000 + (i % 50) * 1000)
                    ),  # Salary 50000-99000
                    "join_date": datetime.date(2020, 1, 1) + datetime.timedelta(days=i),
                }
            )

        # Execute complex query
        request_args = {
            "age__gte": "25",
            "age__lt": "35",
            "is_active": "true",
            "salary__gte": "60000",
            "ordering": "-salary",  # Simplified sorting, only by salary descending
        }

        model = UserFilterModel(large_dataset, request_args)
        results = list(model.filter().order().result())

        # Verify result correctness (not focusing on performance, only validating logic)
        for user in results:
            assert 25 <= user["age"] < 35
            assert user["is_active"] is True
            assert user["salary"] >= decimal.Decimal("60000")

        # Verify sorting: by salary descending
        if len(results) > 1:
            salaries = [user["salary"] for user in results]
            assert salaries == sorted(salaries, reverse=True)
