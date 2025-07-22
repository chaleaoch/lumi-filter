"""
Test backend module functionality

This file tests:
- PeeweeBackend filtering and ordering
- Backend operator mappings
- Field name extraction from queries
"""

import datetime
import decimal

import peewee
import pytest

from lumi_filter.backend import IterableBackend, PeeweeBackend

# Test database setup
test_db = peewee.SqliteDatabase(":memory:")


class BaseModel(peewee.Model):
    class Meta:
        database = test_db


class TestUser(BaseModel):
    """Test user model for backend testing"""

    username = peewee.CharField(max_length=50)
    email = peewee.CharField(max_length=100)
    age = peewee.IntegerField()
    is_active = peewee.BooleanField(default=True)
    salary = peewee.DecimalField(max_digits=10, decimal_places=2)
    join_date = peewee.DateField()


@pytest.fixture(scope="class")
def setup_test_database():
    """Setup test database for backend tests"""
    test_db.create_tables([TestUser])

    # Insert test data
    test_users = [
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
    ]

    for user_data in test_users:
        TestUser.create(**user_data)

    yield

    test_db.drop_tables([TestUser])


class TestPeeweeBackend:
    """Test PeeweeBackend functionality"""

    def test_backend_initialization(self, setup_test_database):
        """Test backend initialization with query"""
        query = TestUser.select()
        backend = PeeweeBackend(query)

        # Check that field names were extracted
        expected_fields = {
            "username",
            "email",
            "age",
            "is_active",
            "salary",
            "join_date",
        }
        assert backend.field_names == expected_fields

    def test_backend_with_selected_columns(self, setup_test_database):
        """Test backend with specific selected columns"""
        query = TestUser.select(TestUser.username, TestUser.age, TestUser.salary)
        backend = PeeweeBackend(query)

        # Should only contain selected fields
        expected_fields = {"username", "age", "salary"}
        assert backend.field_names == expected_fields

    def test_backend_with_aliased_fields(self, setup_test_database):
        """Test backend with aliased fields"""
        query = TestUser.select(
            TestUser.username.alias("user_name"),
            TestUser.salary.alias("monthly_salary"),
        )
        backend = PeeweeBackend(query)

        # Should use alias names
        expected_fields = {"user_name", "monthly_salary"}
        assert backend.field_names == expected_fields

    def test_backend_with_extra_ordering_fields(self, setup_test_database):
        """Test backend with extra ordering fields"""
        query = TestUser.select(TestUser.username, TestUser.age)
        extra_fields = {"salary", "join_date"}
        backend = PeeweeBackend(query, ordering_extra_fields=extra_fields)

        # Should include both selected and extra fields
        expected_fields = {"username", "age", "salary", "join_date"}
        assert backend.field_names == expected_fields

    def test_lookup_expr_operator_mapping(self):
        """Test lookup expression operator mapping"""
        backend = PeeweeBackend(TestUser.select())

        # Test all operator mappings
        import operator

        expected_mapping = {
            "": operator.eq,
            "!": operator.ne,
            "gte": operator.ge,
            "lte": operator.le,
            "gt": operator.gt,
            "lt": operator.lt,
            "in": operator.mod,
            "iin": operator.pow,
        }

        assert backend.LOOKUP_EXPR_OPERATOR_MAP == expected_mapping

    def test_filter_method_equal(self, setup_test_database):
        """Test filter method with equal operator"""
        query = TestUser.select()
        backend = PeeweeBackend(query)

        peewee_field = TestUser.username
        value = "alice_smith"
        lookup_expr = ""

        filtered_query = backend.filter(query, peewee_field, value, lookup_expr)
        results = list(filtered_query)

        assert len(results) == 1
        assert results[0].username == "alice_smith"

    def test_filter_method_not_equal(self, setup_test_database):
        """Test filter method with not equal operator"""
        query = TestUser.select()
        backend = PeeweeBackend(query)

        peewee_field = TestUser.username
        value = "alice_smith"
        lookup_expr = "!"

        filtered_query = backend.filter(query, peewee_field, value, lookup_expr)
        results = list(filtered_query)

        assert len(results) == 2  # bob and charlie
        usernames = {user.username for user in results}
        assert "alice_smith" not in usernames
        assert usernames == {"bob_jones", "charlie_brown"}

    def test_filter_method_greater_than_equal(self, setup_test_database):
        """Test filter method with greater than or equal operator"""
        query = TestUser.select()
        backend = PeeweeBackend(query)

        peewee_field = TestUser.age
        value = 28
        lookup_expr = "gte"

        filtered_query = backend.filter(query, peewee_field, value, lookup_expr)
        results = list(filtered_query)

        assert len(results) == 2  # alice (28) and bob (32)
        for user in results:
            assert user.age >= 28

    def test_filter_method_less_than(self, setup_test_database):
        """Test filter method with less than operator"""
        query = TestUser.select()
        backend = PeeweeBackend(query)

        peewee_field = TestUser.age
        value = 30
        lookup_expr = "lt"

        filtered_query = backend.filter(query, peewee_field, value, lookup_expr)
        results = list(filtered_query)

        assert len(results) == 2  # alice (28) and charlie (26)
        for user in results:
            assert user.age < 30

    def test_filter_method_like_operator(self, setup_test_database):
        """Test filter method with LIKE operator (in)"""
        query = TestUser.select()
        backend = PeeweeBackend(query)

        peewee_field = TestUser.email
        value = "example.com"
        lookup_expr = "in"  # Should add % around value

        filtered_query = backend.filter(query, peewee_field, value, lookup_expr)
        results = list(filtered_query)

        assert len(results) == 2  # alice and bob with example.com emails
        for user in results:
            assert "example.com" in user.email

    def test_filter_method_ilike_operator(self, setup_test_database):
        """Test filter method with ILIKE operator (iin)"""
        query = TestUser.select()
        backend = PeeweeBackend(query)

        peewee_field = TestUser.email
        value = "EXAMPLE.COM"
        lookup_expr = "iin"  # Should add % around value and be case insensitive

        filtered_query = backend.filter(query, peewee_field, value, lookup_expr)
        results = list(filtered_query)

        assert len(results) == 2  # alice and bob (case insensitive)
        for user in results:
            assert "example.com" in user.email.lower()

    def test_filter_method_boolean_field(self, setup_test_database):
        """Test filter method with boolean field"""
        query = TestUser.select()
        backend = PeeweeBackend(query)

        peewee_field = TestUser.is_active
        value = True
        lookup_expr = ""

        filtered_query = backend.filter(query, peewee_field, value, lookup_expr)
        results = list(filtered_query)

        assert len(results) == 2  # alice and bob are active
        for user in results:
            assert user.is_active is True

    def test_filter_method_decimal_field(self, setup_test_database):
        """Test filter method with decimal field"""
        query = TestUser.select()
        backend = PeeweeBackend(query)

        peewee_field = TestUser.salary
        value = decimal.Decimal("80000")
        lookup_expr = "gte"

        filtered_query = backend.filter(query, peewee_field, value, lookup_expr)
        results = list(filtered_query)

        assert len(results) == 1  # only bob has salary >= 80000
        assert results[0].username == "bob_jones"
        assert results[0].salary >= decimal.Decimal("80000")

    def test_filter_method_date_field(self, setup_test_database):
        """Test filter method with date field"""
        query = TestUser.select()
        backend = PeeweeBackend(query)

        peewee_field = TestUser.join_date
        value = datetime.date(2020, 1, 1)
        lookup_expr = "gte"

        filtered_query = backend.filter(query, peewee_field, value, lookup_expr)
        results = list(filtered_query)

        assert len(results) == 2  # alice and charlie joined after 2020
        for user in results:
            assert user.join_date >= datetime.date(2020, 1, 1)

    def test_filter_method_invalid_field_type(self, setup_test_database):
        """Test filter method with invalid field type"""
        query = TestUser.select()
        backend = PeeweeBackend(query)

        invalid_field = "not_a_peewee_field"
        value = "test"
        lookup_expr = ""

        with pytest.raises(TypeError, match="Expected peewee.Field"):
            backend.filter(query, invalid_field, value, lookup_expr)

    def test_order_method_single_field(self, setup_test_database):
        """Test order method with single field"""
        query = TestUser.select()
        backend = PeeweeBackend(query)

        field_name = "age"
        ordered_query = backend.order(query, field_name)
        results = list(ordered_query)

        # Should be ordered by age ascending
        assert len(results) == 3
        ages = [user.age for user in results]
        assert ages == [26, 28, 32]  # charlie, alice, bob

    def test_order_method_descending(self, setup_test_database):
        """Test order method with descending order"""
        query = TestUser.select()
        backend = PeeweeBackend(query)

        field_name = "salary"
        ordered_query = backend.order(query, field_name, is_negative=True)
        results = list(ordered_query)

        # Should be ordered by salary descending
        assert len(results) == 3
        salaries = [user.salary for user in results]
        assert salaries == [
            decimal.Decimal("85000.00"),  # bob
            decimal.Decimal("75000.00"),  # alice
            decimal.Decimal("65000.00"),  # charlie
        ]

    def test_order_method_nonexistent_field(self, setup_test_database):
        """Test order method with non-existent field"""
        query = TestUser.select()
        backend = PeeweeBackend(query)

        field_name = "nonexistent_field"
        ordered_query = backend.order(query, field_name)
        results = list(ordered_query)

        # Should return original query unchanged
        assert len(results) == 3

    def test_get_node_name_with_field(self, setup_test_database):
        """Test _get_node_name with regular Field"""
        backend = PeeweeBackend(TestUser.select())

        field_node = TestUser.username
        node_name = backend._get_node_name(field_node)

        assert node_name == "username"

    def test_get_node_name_with_alias(self, setup_test_database):
        """Test _get_node_name with Alias"""
        backend = PeeweeBackend(TestUser.select())

        alias_node = TestUser.username.alias("user_name")
        node_name = backend._get_node_name(alias_node)

        assert node_name == "user_name"

    def test_get_node_name_with_unsupported_type(self, setup_test_database):
        """Test _get_node_name with unsupported node type"""
        backend = PeeweeBackend(TestUser.select())

        # Create a mock unsupported node
        class MockNode:
            pass

        mock_node = MockNode()
        node_name = backend._get_node_name(mock_node)

        assert node_name is None


class TestIterableBackend:
    """Test IterableBackend functionality"""

    @property
    def sample_data(self):
        """Sample data for testing IterableBackend"""
        return [
            {
                "id": 1,
                "name": "Alice",
                "age": 28,
                "email": "alice@example.com",
                "is_active": True,
                "salary": decimal.Decimal("75000"),
                "profile": {"department": "Engineering", "position": "Developer"},
            },
            {
                "id": 2,
                "name": "Bob",
                "age": 32,
                "email": "bob@example.com",
                "is_active": True,
                "salary": decimal.Decimal("85000"),
                "profile": {"department": "Marketing", "position": "Manager"},
            },
            {
                "id": 3,
                "name": "Charlie",
                "age": 26,
                "email": "charlie@company.com",
                "is_active": False,
                "salary": decimal.Decimal("65000"),
                "profile": {"department": "Sales", "position": "Associate"},
            },
        ]

    def test_get_nested_value_simple(self):
        """Test _get_nested_value with simple key"""

        item = {"name": "Alice", "age": 28}
        value = IterableBackend._get_nested_value(item, "name")
        assert value == "Alice"

    def test_get_nested_value_nested(self):
        """Test _get_nested_value with nested key"""

        item = {"profile": {"department": "Engineering", "position": "Developer"}}
        value = IterableBackend._get_nested_value(item, "profile.department")
        assert value == "Engineering"

    def test_get_nested_value_deep_nested(self):
        """Test _get_nested_value with deeply nested key"""

        item = {"user": {"profile": {"contact": {"email": "test@example.com"}}}}
        value = IterableBackend._get_nested_value(item, "user.profile.contact.email")
        assert value == "test@example.com"

    def test_match_item_equal(self):
        """Test _match_item with equal operator"""

        item = {"name": "Alice", "age": 28}
        result = IterableBackend._match_item(item, "name", "Alice", "")
        assert result is True

        result = IterableBackend._match_item(item, "name", "Bob", "")
        assert result is False

    def test_match_item_not_equal(self):
        """Test _match_item with not equal operator"""

        item = {"name": "Alice", "age": 28}
        result = IterableBackend._match_item(item, "name", "Bob", "!")
        assert result is True

        result = IterableBackend._match_item(item, "name", "Alice", "!")
        assert result is False

    def test_match_item_greater_than(self):
        """Test _match_item with greater than operator"""

        item = {"age": 28}
        result = IterableBackend._match_item(item, "age", 25, "gt")
        assert result is True

        result = IterableBackend._match_item(item, "age", 30, "gt")
        assert result is False

    def test_match_item_like_operator(self):
        """Test _match_item with like operator"""

        item = {"email": "alice@example.com"}
        result = IterableBackend._match_item(item, "email", "example", "in")
        assert result is True

        result = IterableBackend._match_item(item, "email", "company", "in")
        assert result is False

    def test_match_item_ilike_operator(self):
        """Test _match_item with case-insensitive like operator"""

        item = {"email": "alice@Example.COM"}
        result = IterableBackend._match_item(item, "email", "example", "iin")
        assert result is True

        result = IterableBackend._match_item(item, "email", "EXAMPLE", "iin")
        assert result is True

    def test_match_item_nested_field(self):
        """Test _match_item with nested field"""

        item = {"profile": {"department": "Engineering"}}
        result = IterableBackend._match_item(
            item, "profile.department", "Engineering", ""
        )
        assert result is True

        result = IterableBackend._match_item(
            item, "profile.department", "Marketing", ""
        )
        assert result is False

    def test_match_item_missing_key(self):
        """Test _match_item with missing key (should return True)"""

        item = {"name": "Alice"}
        result = IterableBackend._match_item(item, "nonexistent", "value", "")
        assert result is True  # Should return True for missing keys

    def test_filter_equal(self):
        """Test filter method with equal operator"""

        filtered_data = list(
            IterableBackend.filter(self.sample_data, "name", "Alice", "")
        )
        assert len(filtered_data) == 1
        assert filtered_data[0]["name"] == "Alice"

    def test_filter_not_equal(self):
        """Test filter method with not equal operator"""

        filtered_data = list(
            IterableBackend.filter(self.sample_data, "name", "Alice", "!")
        )
        assert len(filtered_data) == 2
        names = {item["name"] for item in filtered_data}
        assert "Alice" not in names
        assert names == {"Bob", "Charlie"}

    def test_filter_greater_than_equal(self):
        """Test filter method with greater than or equal operator"""

        filtered_data = list(IterableBackend.filter(self.sample_data, "age", 28, "gte"))
        assert len(filtered_data) == 2  # Alice (28) and Bob (32)
        for item in filtered_data:
            assert item["age"] >= 28

    def test_filter_less_than(self):
        """Test filter method with less than operator"""

        filtered_data = list(IterableBackend.filter(self.sample_data, "age", 30, "lt"))
        assert len(filtered_data) == 2  # Alice (28) and Charlie (26)
        for item in filtered_data:
            assert item["age"] < 30

    def test_filter_like_operator(self):
        """Test filter method with like operator"""

        filtered_data = list(
            IterableBackend.filter(self.sample_data, "email", "example.com", "in")
        )
        assert len(filtered_data) == 2  # Alice and Bob
        for item in filtered_data:
            assert "example.com" in item["email"]

    def test_filter_ilike_operator(self):
        """Test filter method with case-insensitive like operator"""

        filtered_data = list(
            IterableBackend.filter(self.sample_data, "email", "EXAMPLE.COM", "iin")
        )
        assert len(filtered_data) == 2  # Alice and Bob (case insensitive)
        for item in filtered_data:
            assert "example.com" in item["email"].lower()

    def test_filter_boolean_field(self):
        """Test filter method with boolean field"""

        filtered_data = list(
            IterableBackend.filter(self.sample_data, "is_active", True, "")
        )
        assert len(filtered_data) == 2  # Alice and Bob
        for item in filtered_data:
            assert item["is_active"] is True

    def test_filter_decimal_field(self):
        """Test filter method with decimal field"""

        filtered_data = list(
            IterableBackend.filter(
                self.sample_data, "salary", decimal.Decimal("80000"), "gte"
            )
        )
        assert len(filtered_data) == 1  # Only Bob
        assert filtered_data[0]["name"] == "Bob"
        assert filtered_data[0]["salary"] >= decimal.Decimal("80000")

    def test_filter_nested_field(self):
        """Test filter method with nested field"""

        filtered_data = list(
            IterableBackend.filter(
                self.sample_data, "profile.department", "Engineering", ""
            )
        )
        assert len(filtered_data) == 1
        assert filtered_data[0]["name"] == "Alice"
        assert filtered_data[0]["profile"]["department"] == "Engineering"

    def test_order_ascending(self):
        """Test order method with ascending order"""

        ordered_data = IterableBackend.order(self.sample_data, "age")
        ages = [item["age"] for item in ordered_data]
        assert ages == [26, 28, 32]  # Charlie, Alice, Bob

    def test_order_descending(self):
        """Test order method with descending order"""

        ordered_data = IterableBackend.order(
            self.sample_data, "salary", is_reverse=True
        )
        salaries = [item["salary"] for item in ordered_data]
        expected = [
            decimal.Decimal("85000"),
            decimal.Decimal("75000"),
            decimal.Decimal("65000"),
        ]
        assert salaries == expected  # Bob, Alice, Charlie

    def test_order_by_string_field(self):
        """Test order method with string field"""

        ordered_data = IterableBackend.order(self.sample_data, "name")
        names = [item["name"] for item in ordered_data]
        assert names == ["Alice", "Bob", "Charlie"]  # Alphabetical order

    def test_order_nested_field(self):
        """Test order method with nested field"""

        ordered_data = IterableBackend.order(self.sample_data, "profile.department")
        departments = [item["profile"]["department"] for item in ordered_data]
        assert departments == [
            "Engineering",
            "Marketing",
            "Sales",
        ]  # Alphabetical order

    def test_order_missing_key(self):
        """Test order method with missing key (should return original data)"""

        original_data = list(self.sample_data)
        ordered_data = IterableBackend.order(self.sample_data, "nonexistent_field")

        # Should return original data unchanged (warning logged)
        assert ordered_data == original_data

    def test_lookup_expr_operator_mapping(self):
        """Test that IterableBackend has correct operator mapping"""
        import operator

        from lumi_filter.operator import generic_ilike_operator, generic_like_operator

        expected_mapping = {
            "": operator.eq,
            "!": operator.ne,
            "gte": operator.ge,
            "lte": operator.le,
            "gt": operator.gt,
            "lt": operator.lt,
            "in": generic_like_operator,
            "iin": generic_ilike_operator,
        }

        assert IterableBackend.LOOKUP_EXPR_OPERATOR_MAP == expected_mapping
