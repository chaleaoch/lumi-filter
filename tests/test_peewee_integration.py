"""
Peewee integration tests - test complete workflows with database queries

This file tests:
- End-to-end filtering with Peewee ORM
- AutoQueryModel with ModelSelect queries
- Real database scenarios with Peewee models
"""

import datetime
import decimal

import peewee
import pytest

from lumi_filter.shortcut import AutoQueryModel

# Create in-memory database for testing
test_db = peewee.SqliteDatabase(":memory:")


class BaseModel(peewee.Model):
    class Meta:
        database = test_db


class User(BaseModel):
    """User model for testing"""

    username = peewee.CharField(max_length=50)
    email = peewee.CharField(max_length=100)
    age = peewee.IntegerField()
    is_active = peewee.BooleanField(default=True)
    salary = peewee.DecimalField(max_digits=10, decimal_places=2)
    join_date = peewee.DateField()


class Department(BaseModel):
    """Department model for testing"""

    name = peewee.CharField(max_length=100)
    budget = peewee.DecimalField(max_digits=12, decimal_places=2)
    manager_id = peewee.IntegerField(null=True)


class Employee(BaseModel):
    """Employee model with foreign key relationship"""

    user = peewee.ForeignKeyField(User, backref="employees")
    department = peewee.ForeignKeyField(Department, backref="employees")
    position = peewee.CharField(max_length=100)
    hire_date = peewee.DateField()


@pytest.fixture(scope="class")
def setup_database():
    """Setup test database with sample data"""
    # Create tables
    test_db.create_tables([User, Department, Employee])

    # Insert sample data
    users_data = [
        {
            "username": "alice_smith",
            "email": "alice@example.com",
            "age": 28,
            "is_active": True,
            "salary": decimal.Decimal("75000.00"),
            "join_date": datetime.date(2020, 1, 15),
        },
        {
            "username": "bob_jones",
            "email": "bob@example.com",
            "age": 32,
            "is_active": True,
            "salary": decimal.Decimal("85000.00"),
            "join_date": datetime.date(2019, 6, 10),
        },
        {
            "username": "charlie_brown",
            "email": "charlie@company.com",
            "age": 26,
            "is_active": False,
            "salary": decimal.Decimal("65000.00"),
            "join_date": datetime.date(2021, 3, 22),
        },
        {
            "username": "diana_prince",
            "email": "diana@example.com",
            "age": 35,
            "is_active": True,
            "salary": decimal.Decimal("95000.00"),
            "join_date": datetime.date(2018, 11, 5),
        },
        {
            "username": "eve_wilson",
            "email": "eve@company.com",
            "age": 29,
            "is_active": False,
            "salary": decimal.Decimal("70000.00"),
            "join_date": datetime.date(2020, 8, 18),
        },
    ]

    for user_data in users_data:
        User.create(**user_data)

    # Insert departments
    departments_data = [
        {
            "name": "Engineering",
            "budget": decimal.Decimal("500000.00"),
            "manager_id": 1,
        },
        {"name": "Marketing", "budget": decimal.Decimal("300000.00"), "manager_id": 2},
        {"name": "Sales", "budget": decimal.Decimal("400000.00"), "manager_id": 4},
    ]

    for dept_data in departments_data:
        Department.create(**dept_data)

    # Insert employees
    employees_data = [
        {
            "user_id": 1,
            "department_id": 1,
            "position": "Software Engineer",
            "hire_date": datetime.date(2020, 1, 15),
        },
        {
            "user_id": 2,
            "department_id": 1,
            "position": "Senior Engineer",
            "hire_date": datetime.date(2019, 6, 10),
        },
        {
            "user_id": 3,
            "department_id": 2,
            "position": "Marketing Specialist",
            "hire_date": datetime.date(2021, 3, 22),
        },
        {
            "user_id": 4,
            "department_id": 3,
            "position": "Sales Director",
            "hire_date": datetime.date(2018, 11, 5),
        },
        {
            "user_id": 5,
            "department_id": 2,
            "position": "Marketing Manager",
            "hire_date": datetime.date(2020, 8, 18),
        },
    ]

    for emp_data in employees_data:
        Employee.create(**emp_data)

    yield

    # Cleanup
    test_db.drop_tables([User, Department, Employee])


class TestPeeweeIntegration:
    """Test Peewee integration with AutoQueryModel"""

    def test_basic_model_select_filtering(self, setup_database):
        """Test basic filtering with Peewee ModelSelect"""
        query = User.select()
        request_args = {"is_active": "true", "ordering": "-salary"}

        model = AutoQueryModel(query, request_args)
        results = list(model.filter().order().result())

        # Should return 3 active users sorted by salary descending
        assert len(results) == 3
        for user in results:
            assert user.is_active is True

        # Verify sorting
        salaries = [user.salary for user in results]
        assert salaries == sorted(salaries, reverse=True)
        assert results[0].username == "diana_prince"  # Highest salary

    def test_field_alias_handling(self, setup_database):
        """Test handling of aliased fields in query"""
        query = User.select(
            User.username.alias("user_name"),
            User.salary.alias("monthly_salary"),
            User.is_active,
        )
        request_args = {"monthly_salary__gte": "80000", "user_name": "bob_jones"}

        model = AutoQueryModel(query, request_args)
        results = list(model.filter().result())

        assert len(results) == 1
        user = results[0]
        assert user.user_name == "bob_jones"
        assert user.monthly_salary >= decimal.Decimal("80000")

    def test_complex_query_with_joins(self, setup_database):
        """Test filtering on joined tables"""
        query = (
            User.select(User.username, User.salary, Department.name.alias("dept_name"))
            .join(Employee)
            .join(Department)
        )

        request_args = {"dept_name": "Engineering", "ordering": "salary"}

        model = AutoQueryModel(query, request_args)
        results = list(model.filter().order().result())

        # Should return 2 users from Engineering department
        assert len(results) == 2
        for user in results:
            assert user.dept_name == "Engineering"

        # Verify sorting by salary ascending
        salaries = [user.salary for user in results]
        assert salaries == sorted(salaries)

    def test_date_field_filtering(self, setup_database):
        """Test date field filtering with Peewee"""
        query = User.select()
        request_args = {
            "join_date__gte": "2020-01-01",
            "join_date__lt": "2021-01-01",
            "ordering": "join_date",
        }

        model = AutoQueryModel(query, request_args)
        results = list(model.filter().order().result())

        # Should return users who joined in 2020
        expected_count = 2  # alice_smith and eve_wilson
        assert len(results) == expected_count

        for user in results:
            assert (
                datetime.date(2020, 1, 1) <= user.join_date < datetime.date(2021, 1, 1)
            )

    def test_boolean_field_variations(self, setup_database):
        """Test different boolean field value formats"""
        query = User.select()

        # Test with 'true' string
        request_args = {"is_active": "true"}
        model = AutoQueryModel(query, request_args)
        active_users = list(model.filter().result())
        assert len(active_users) == 3

        # Test with 'false' string
        request_args = {"is_active": "false"}
        model = AutoQueryModel(query, request_args)
        inactive_users = list(model.filter().result())
        assert len(inactive_users) == 2

        # Test with '1' and '0'
        request_args = {"is_active": "1"}
        model = AutoQueryModel(query, request_args)
        active_users_1 = list(model.filter().result())
        assert len(active_users_1) == 3

        request_args = {"is_active": "0"}
        model = AutoQueryModel(query, request_args)
        inactive_users_0 = list(model.filter().result())
        assert len(inactive_users_0) == 2

    def test_age_range_filtering(self, setup_database):
        """Test numeric range filtering"""
        query = User.select()
        request_args = {"age__gte": "28", "age__lte": "32", "ordering": "age"}

        model = AutoQueryModel(query, request_args)
        results = list(model.filter().order().result())

        assert len(results) == 3  # alice (28), eve (29), bob (32)
        for user in results:
            assert 28 <= user.age <= 32

        # Verify sorting
        ages = [user.age for user in results]
        assert ages == [28, 29, 32]

    def test_string_contains_filtering(self, setup_database):
        """Test string contains filtering"""
        query = User.select()
        request_args = {"email__in": "company.com", "ordering": "username"}

        model = AutoQueryModel(query, request_args)
        results = list(model.filter().order().result())

        assert len(results) == 2  # charlie and eve
        for user in results:
            assert "company.com" in user.email

        # Verify alphabetical sorting
        usernames = [user.username for user in results]
        assert usernames == ["charlie_brown", "eve_wilson"]

    def test_mixed_field_types_complex_scenario(self, setup_database):
        """Test complex scenario with mixed field types"""
        query = User.select()
        request_args = {
            "age__gte": "25",
            "salary__gte": "70000",
            "is_active": "true",
            "join_date__gte": "2019-01-01",
            "ordering": "-salary",
        }

        model = AutoQueryModel(query, request_args)
        results = list(model.filter().order().result())

        # Should match specific criteria
        assert len(results) == 3  # alice, bob, diana

        for user in results:
            assert user.age >= 25
            assert user.salary >= decimal.Decimal("70000")
            assert user.is_active is True
            assert user.join_date >= datetime.date(2019, 1, 1)

        # Verify descending salary order
        salaries = [user.salary for user in results]
        assert salaries == sorted(salaries, reverse=True)

    def test_no_matching_results(self, setup_database):
        """Test query with no matching results"""
        query = User.select()
        request_args = {"age__gt": "50"}  # No users over 50 in test data

        model = AutoQueryModel(query, request_args)
        results = list(model.filter().result())

        assert len(results) == 0

    def test_invalid_field_handling(self, setup_database):
        """Test handling of invalid field names"""
        query = User.select()
        request_args = {
            "nonexistent_field": "value",  # Invalid field
            "username": "alice_smith",  # Valid field
            "ordering": "username",
        }

        model = AutoQueryModel(query, request_args)
        results = list(model.filter().order().result())

        # Should ignore invalid field and process valid ones
        assert len(results) == 1
        assert results[0].username == "alice_smith"

    def test_ordering_with_multiple_fields(self, setup_database):
        """Test ordering with multiple fields"""
        query = User.select()
        request_args = {"ordering": "is_active,-salary"}

        model = AutoQueryModel(query, request_args)
        results = list(model.filter().order().result())

        assert len(results) == 5

        # Should be ordered by is_active first (False before True), then by salary descending
        # False users: charlie (65000), eve (70000) - ordered by salary desc
        # True users: diana (95000), bob (85000), alice (75000) - ordered by salary desc
        expected_order = [
            "eve_wilson",
            "charlie_brown",
            "diana_prince",
            "bob_jones",
            "alice_smith",
        ]
        actual_order = [user.username for user in results]
        assert actual_order == expected_order
