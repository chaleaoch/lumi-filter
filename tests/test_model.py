"""Tests for model module."""

from unittest.mock import Mock

import peewee
import pydantic
import pytest

from lumi_filter.field import FilterField, IntField, StrField
from lumi_filter.model import MetaModel, Model, ModelMeta


class TestMetaModel:
    """Test the MetaModel class."""

    def test_init_default(self):
        """Test MetaModel initialization with default values."""
        meta = MetaModel()
        assert meta.schema is None
        assert meta.fields == []

    def test_init_with_params(self):
        """Test MetaModel initialization with parameters."""
        meta = MetaModel(schema="test_schema", fields=["field1", "field2"])
        assert meta.schema == "test_schema"
        assert meta.fields == ["field1", "field2"]

    def test_is_peewee_model_true(self, setup_test_db):
        """Test _is_peewee_model with actual Peewee model."""
        from tests.conftest import Product

        meta = MetaModel()
        assert meta._is_peewee_model(Product) is True

    def test_is_peewee_model_false(self):
        """Test _is_peewee_model with non-Peewee class."""
        meta = MetaModel()
        assert meta._is_peewee_model(str) is False
        assert meta._is_peewee_model("not_a_class") is False

    def test_is_pydantic_model_true(self):
        """Test _is_pydantic_model with actual Pydantic model."""

        class TestModel(pydantic.BaseModel):
            name: str

        meta = MetaModel()
        assert meta._is_pydantic_model(TestModel) is True

    def test_is_pydantic_model_false(self):
        """Test _is_pydantic_model with non-Pydantic class."""
        meta = MetaModel()
        assert meta._is_pydantic_model(str) is False
        assert meta._is_pydantic_model("not_a_class") is False

    def test_process_peewee_fields(self, setup_test_db):
        """Test processing Peewee fields."""
        from tests.conftest import Product

        meta = MetaModel(schema=Product)
        fields = meta._process_peewee_fields()

        # Check that fields are generated
        assert "name" in fields
        assert "price" in fields
        assert "is_active" in fields

        # Check field types and sources
        assert isinstance(fields["name"].source, peewee.Field)
        assert isinstance(fields["price"].source, peewee.Field)

    def test_process_peewee_fields_with_field_filter(self, setup_test_db):
        """Test processing Peewee fields with field filtering."""
        from tests.conftest import Product

        meta = MetaModel(schema=Product, fields=["name", "price"])
        fields = meta._process_peewee_fields()

        # Should only include specified fields
        assert "name" in fields
        assert "price" in fields
        assert "is_active" not in fields

    def test_process_pydantic_fields(self):
        """Test processing Pydantic fields."""

        class TestModel(pydantic.BaseModel):
            name: str
            age: int
            active: bool

        meta = MetaModel(schema=TestModel)
        fields = meta._process_pydantic_fields()

        assert "name" in fields
        assert "age" in fields
        assert "active" in fields

        # Check request_arg_name and source
        assert fields["name"].request_arg_name == "name"
        assert fields["name"].source == "name"

    def test_process_pydantic_nested_fields(self):
        """Test processing nested Pydantic fields."""

        class ProfileModel(pydantic.BaseModel):
            bio: str
            score: int

        class UserModel(pydantic.BaseModel):
            name: str
            profile: ProfileModel

        meta = MetaModel(schema=UserModel)
        fields = meta._process_pydantic_fields()

        assert "name" in fields
        assert "profile_bio" in fields
        assert "profile_score" in fields

        # Check nested field configuration
        assert fields["profile_bio"].request_arg_name == "profile.bio"
        assert fields["profile_bio"].source == "profile.bio"

    def test_is_nested_pydantic_model(self):
        """Test _is_nested_pydantic_model method."""

        class NestedModel(pydantic.BaseModel):
            value: str

        # Create a mock field info
        mock_field = Mock()
        mock_field.annotation = NestedModel

        meta = MetaModel()
        assert meta._is_nested_pydantic_model(mock_field) is True

        # Test with non-model annotation
        mock_field.annotation = str
        assert meta._is_nested_pydantic_model(mock_field) is False

    def test_get_filter_fields_no_schema(self):
        """Test get_filter_fields with no schema."""
        meta = MetaModel()
        fields = meta.get_filter_fields()
        assert fields == {}

    def test_get_filter_fields_peewee(self, setup_test_db):
        """Test get_filter_fields with Peewee schema."""
        from tests.conftest import Product

        meta = MetaModel(schema=Product)
        fields = meta.get_filter_fields()

        assert len(fields) > 0
        assert "name" in fields
        assert isinstance(fields["name"], FilterField)

    def test_get_filter_fields_pydantic(self):
        """Test get_filter_fields with Pydantic schema."""

        class TestModel(pydantic.BaseModel):
            name: str
            value: int

        meta = MetaModel(schema=TestModel)
        fields = meta.get_filter_fields()

        assert len(fields) > 0
        assert "name" in fields
        assert isinstance(fields["name"], FilterField)


class TestModelMeta:
    """Test the ModelMeta metaclass."""

    def test_create_simple_model(self):
        """Test creating a simple model with explicit fields."""

        class TestModel(Model):
            name = StrField()
            age = IntField()

        # Check that metaclass processed the fields correctly
        assert hasattr(TestModel, "__supported_query_key_field_dict__")
        assert hasattr(TestModel, "__ordering_field_map__")

        # Check supported query keys
        supported_keys = TestModel.__supported_query_key_field_dict__
        assert "name" in supported_keys
        assert "name__contains" in supported_keys
        assert "age" in supported_keys
        assert "age__gt" in supported_keys

    def test_create_model_with_meta(self, setup_test_db):
        """Test creating model with Meta schema."""
        from tests.conftest import Product

        class ProductFilter(Model):
            class Meta:
                schema = Product

        # Check that schema fields were processed
        supported_keys = ProductFilter.__supported_query_key_field_dict__
        assert "name" in supported_keys
        assert "price" in supported_keys

    def test_field_configuration(self):
        """Test that fields are configured correctly."""

        class TestModel(Model):
            test_field = StrField()

        field = TestModel.__ordering_field_map__["test_field"]
        assert field.request_arg_name == "test_field"
        assert field.source == "test_field"

    def test_custom_field_names(self):
        """Test fields with custom request_arg_name and source."""

        class TestModel(Model):
            display_name = StrField(request_arg_name="name", source="actual_name")

        field = TestModel.__ordering_field_map__["display_name"]
        assert field.request_arg_name == "name"
        assert field.source == "actual_name"

        # Check that query key uses request_arg_name
        supported_keys = TestModel.__supported_query_key_field_dict__
        assert "name" in supported_keys
        assert "display_name" not in supported_keys

    def test_field_name_validation_error(self):
        """Test that field names with '__' raise ValueError."""
        with pytest.raises(ValueError, match="cannot contain '__'"):

            class TestModel(Model):
                invalid_field = StrField(request_arg_name="field__with__double__underscore")

    def test_lookup_expressions_generation(self):
        """Test that lookup expressions are generated correctly."""

        class TestModel(Model):
            name = StrField()
            age = IntField()

        supported_keys = TestModel.__supported_query_key_field_dict__

        # Test string field lookups
        assert "name" in supported_keys
        assert "name!" in supported_keys
        assert "name__contains" in supported_keys
        assert "name__icontains" in supported_keys

        # Test int field lookups (no contains)
        assert "age" in supported_keys
        assert "age__gt" in supported_keys
        assert "age__lt" in supported_keys
        assert "age__contains" not in supported_keys

    def test_source_type_consistency_error(self):
        """Test that mixed source types raise ValueError."""
        with pytest.raises(ValueError, match="different source types"):

            class TestModel(Model):
                string_source = StrField(source="string_field")
                peewee_source = StrField(source=peewee.CharField())

    def test_extract_meta_options(self):
        """Test Meta options extraction."""

        class TestMeta:
            schema = "test_schema"
            fields = ["field1", "field2"]
            _private = "should_be_ignored"

        attrs = {"Meta": TestMeta}
        options = ModelMeta._extract_meta_options(attrs)

        assert options["schema"] == "test_schema"
        assert options["fields"] == ["field1", "field2"]
        assert "_private" not in options
        assert "Meta" not in attrs  # Should be removed


class TestModel:
    """Test the Model class."""

    def test_init(self, sample_products_data):
        """Test Model initialization."""
        request_args = {"name": "test"}
        model = Model(sample_products_data, request_args)

        assert model.data == sample_products_data
        assert model.request_args == request_args

    def test_filter_and_result_chaining(self, sample_products_data):
        """Test filter and result method chaining."""

        class ProductFilter(Model):
            name = StrField()
            price = StrField()  # Using StrField for simplicity

        request_args = {"name": "Laptop"}
        model = ProductFilter(sample_products_data, request_args)

        result = model.filter().result()

        # Should filter for items with "Laptop" in name
        assert len(result) == 1
        assert result[0]["name"] == "Laptop"

    def test_order_and_result_chaining(self, sample_products_data):
        """Test order and result method chaining."""

        class ProductFilter(Model):
            name = StrField()
            price = StrField()

        request_args = {"ordering": "name"}
        model = ProductFilter(sample_products_data, request_args)

        result = model.order().result()

        # Should be ordered by name
        names = [item["name"] for item in result]
        assert names == sorted(names)

    # def test_cls_filter_with_iterable_data(self, sample_products_data):
    #     """Test cls_filter method with iterable data."""

    #     class ProductFilter(Model):
    #         name = StrField()
    #         is_active = StrField()  # Using StrField for simplicity

    #     request_args = {"is_active": "True"}
    #     result = ProductFilter.cls_filter(sample_products_data, request_args)

    #     # Convert to list if needed
    #     if not isinstance(result, list):
    #         result = list(result)

    #     # Should filter for active products - check the specific True values
    #     active_items = [item for item in result if str(item["is_active"]) == "True"]
    #     assert len(active_items) > 0

    def test_cls_filter_with_invalid_field(self, sample_products_data):
        """Test cls_filter ignores unknown fields."""

        class ProductFilter(Model):
            name = StrField()

        request_args = {"unknown_field": "value", "name": "Laptop"}
        result = ProductFilter.cls_filter(sample_products_data, request_args)

        # Should ignore unknown_field and filter by name
        assert len(result) == 1
        assert result[0]["name"] == "Laptop"

    def test_cls_filter_with_invalid_value(self, sample_products_data):
        """Test cls_filter ignores invalid values."""

        class ProductFilter(Model):
            age = IntField()  # Will fail to parse non-numeric values

        request_args = {"age": "not_a_number"}
        result = ProductFilter.cls_filter(sample_products_data, request_args)

        # Should return all data since invalid value is ignored
        assert len(result) == len(sample_products_data)

    def test_cls_filter_with_in_lookup(self, sample_products_data):
        """Test cls_filter with 'in' lookup expression."""

        class ProductFilter(Model):
            name = StrField()

        request_args = {"name__in": "Laptop,Smartphone"}
        result = ProductFilter.cls_filter(sample_products_data, request_args)

        # Should find items with names in the list
        names = [item["name"] for item in result]
        assert "Laptop" in names
        assert "Smartphone" in names

    def test_cls_order_ascending(self, sample_products_data):
        """Test cls_order with ascending order."""

        class ProductFilter(Model):
            name = StrField()

        request_args = {"ordering": "name"}
        result = ProductFilter.cls_order(sample_products_data, request_args)

        names = [item["name"] for item in result]
        assert names == sorted(names)

    def test_cls_order_descending(self, sample_products_data):
        """Test cls_order with descending order."""

        class ProductFilter(Model):
            name = StrField()

        request_args = {"ordering": "-name"}
        result = ProductFilter.cls_order(sample_products_data, request_args)

        names = [item["name"] for item in result]
        assert names == sorted(names, reverse=True)

    def test_cls_order_multiple_fields(self, sample_products_data):
        """Test cls_order with multiple fields."""

        class ProductFilter(Model):
            category_name = StrField()
            name = StrField()

        request_args = {"ordering": "category_name,-name"}
        result = ProductFilter.cls_order(sample_products_data, request_args)

        # Should order by category first, then by name descending
        prev_category = None
        prev_name = None
        for item in result:
            if prev_category is not None:
                if item["category_name"] == prev_category:
                    # Within same category, names should be in descending order
                    assert item["name"] <= prev_name
                else:
                    # Categories should be in ascending order
                    assert item["category_name"] >= prev_category
            prev_category = item["category_name"]
            prev_name = item["name"]

    def test_cls_order_no_ordering(self, sample_products_data):
        """Test cls_order with no ordering parameter."""

        class ProductFilter(Model):
            name = StrField()

        request_args = {}
        result = ProductFilter.cls_order(sample_products_data, request_args)

        # Should return original data unchanged
        assert result == sample_products_data

    def test_cls_order_invalid_field(self, sample_products_data):
        """Test cls_order ignores invalid field names."""

        class ProductFilter(Model):
            name = StrField()

        request_args = {"ordering": "invalid_field,name"}
        result = ProductFilter.cls_order(sample_products_data, request_args)

        # Should ignore invalid_field and order by name
        names = [item["name"] for item in result]
        assert names == sorted(names)

    def test_get_backend_peewee(self, peewee_query):
        """Test _get_backend with Peewee query."""
        from lumi_filter.backend import PeeweeBackend

        backend = Model._get_backend(peewee_query)
        assert backend == PeeweeBackend

    def test_get_backend_iterable(self, sample_products_data):
        """Test _get_backend with iterable data."""
        from lumi_filter.backend import IterableBackend

        backend = Model._get_backend(sample_products_data)
        assert backend == IterableBackend

    # def test_get_backend_unsupported_type(self):
    #     """Test _get_backend with unsupported data type."""
    #     # Model._get_backend should handle the type checking properly
    #     # Let's check what happens with an invalid type
    #     try:
    #         Model._get_backend("invalid_data_type")
    #         # If no exception is raised, the test should check the actual behavior
    #         assert False, "Expected TypeError to be raised"
    #     except TypeError as e:
    #         assert "Unsupported data type" in str(e)

    def test_peewee_integration(self, setup_test_db):
        """Test integration with Peewee models."""
        from tests.conftest import Product

        class ProductFilter(Model):
            class Meta:
                schema = Product

        query = Product.select()
        request_args = {"name": "Laptop"}

        # This should work without errors
        filtered_query = ProductFilter.cls_filter(query, request_args)
        assert filtered_query is not None
