"""
Integration tests - test complete workflows

This file tests:
- End-to-end data filtering workflows
- Real-world usage scenarios
- Integration of multiple data types
"""

import datetime
import decimal

from lumi_filter.field import BooleanField, DateField, DecimalField, IntField, StrField
from lumi_filter.model import Model


class UserFilterModel(Model):
    """User filter model - simulates real business scenarios"""

    id = IntField()
    username = StrField()
    email = StrField()
    age = IntField()
    is_active = BooleanField()
    salary = DecimalField()
    join_date = DateField()


class TestIntegrationScenarios:
    """Integration test scenarios"""

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
