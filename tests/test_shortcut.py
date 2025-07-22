"""
Test shortcut module functionality

This file tests:
- AutoQueryModel creation and functionality
- compatible_request_args function
- Error handling in shortcut functions
"""

import datetime
import decimal

import peewee
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
            assert user.employee.department.dept_name == "Engineering"

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
        assert len(results) == 2  # alice, bob

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
