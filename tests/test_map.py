"""Tests for map module."""

import datetime
import decimal

import peewee
import pytest

from lumi_filter.field import (
    BooleanField,
    DateField,
    DateTimeField,
    DecimalField,
    IntField,
    StrField,
)
from lumi_filter.map import PEEWEE_FIELD_MAP, PYTHON_TYPE_MAP, pd_filter_mapping, pw_filter_mapping
from lumi_filter.util import ClassHierarchyMapping


class TestPeeweeFieldMap:
    """Test the Peewee field mapping configuration."""

    def test_peewee_field_map_contents(self):
        """Test that PEEWEE_FIELD_MAP contains expected mappings."""
        expected_mappings = {
            peewee.CharField: StrField,
            peewee.TextField: StrField,
            peewee.IntegerField: IntField,
            peewee.DecimalField: DecimalField,
            peewee.BooleanField: BooleanField,
            peewee.DateField: DateField,
            peewee.DateTimeField: DateTimeField,
        }

        assert PEEWEE_FIELD_MAP == expected_mappings

    def test_peewee_mapping_instance(self):
        """Test that pw_filter_mapping is a ClassHierarchyMapping instance."""
        assert isinstance(pw_filter_mapping, ClassHierarchyMapping)

    def test_peewee_mapping_lookups(self):
        """Test Peewee field to filter field lookups."""
        # Test direct mappings
        assert pw_filter_mapping[peewee.CharField] == StrField
        assert pw_filter_mapping[peewee.TextField] == StrField
        assert pw_filter_mapping[peewee.IntegerField] == IntField
        assert pw_filter_mapping[peewee.DecimalField] == DecimalField
        assert pw_filter_mapping[peewee.BooleanField] == BooleanField
        assert pw_filter_mapping[peewee.DateField] == DateField
        assert pw_filter_mapping[peewee.DateTimeField] == DateTimeField

    def test_peewee_field_inheritance(self):
        """Test that field inheritance works correctly."""
        # Peewee fields that inherit from CharField should map to StrField
        assert pw_filter_mapping[peewee.TextField] == StrField

        # Test with a custom field that inherits from CharField
        class CustomCharField(peewee.CharField):
            pass

        # Should inherit mapping from parent
        assert pw_filter_mapping[CustomCharField] == StrField

    def test_peewee_unsupported_field(self):
        """Test behavior with unsupported Peewee field types."""

        class UnsupportedField(peewee.Field):
            pass

        with pytest.raises(KeyError):
            _ = pw_filter_mapping[UnsupportedField]


class TestPythonTypeMap:
    """Test the Python type mapping configuration."""

    def test_python_type_map_contents(self):
        """Test that PYTHON_TYPE_MAP contains expected mappings."""
        expected_mappings = {
            str: StrField,
            int: IntField,
            decimal.Decimal: DecimalField,
            bool: BooleanField,
            datetime.date: DateField,
            datetime.datetime: DateTimeField,
        }

        assert PYTHON_TYPE_MAP == expected_mappings

    def test_python_mapping_instance(self):
        """Test that pd_filter_mapping is a ClassHierarchyMapping instance."""
        assert isinstance(pd_filter_mapping, ClassHierarchyMapping)

    def test_python_mapping_lookups(self):
        """Test Python type to filter field lookups."""
        # Test direct mappings
        assert pd_filter_mapping[str] == StrField
        assert pd_filter_mapping[int] == IntField
        assert pd_filter_mapping[decimal.Decimal] == DecimalField
        assert pd_filter_mapping[bool] == BooleanField
        assert pd_filter_mapping[datetime.date] == DateField
        assert pd_filter_mapping[datetime.datetime] == DateTimeField

    def test_python_type_inheritance(self):
        """Test that type inheritance works correctly."""

        # Custom classes that inherit from basic types
        class CustomStr(str):
            pass

        class CustomInt(int):
            pass

        # Should inherit mapping from parent types
        assert pd_filter_mapping[CustomStr] == StrField
        assert pd_filter_mapping[CustomInt] == IntField

    def test_python_unsupported_type(self):
        """Test behavior with unsupported Python types."""

        class UnsupportedType:
            pass

        with pytest.raises(KeyError):
            _ = pd_filter_mapping[UnsupportedType]


class TestMappingIntegration:
    """Test integration scenarios with both mappings."""

    def test_peewee_to_python_consistency(self):
        """Test that Peewee and Python mappings are consistent."""
        # CharField and str should both map to StrField
        assert pw_filter_mapping[peewee.CharField] == pd_filter_mapping[str]

        # IntegerField and int should both map to IntField
        assert pw_filter_mapping[peewee.IntegerField] == pd_filter_mapping[int]

        # BooleanField and bool should both map to BooleanField
        assert pw_filter_mapping[peewee.BooleanField] == pd_filter_mapping[bool]

    def test_date_time_mappings(self):
        """Test date and datetime mappings specifically."""
        # DateField mappings
        assert pw_filter_mapping[peewee.DateField] == DateField
        assert pd_filter_mapping[datetime.date] == DateField

        # DateTimeField mappings
        assert pw_filter_mapping[peewee.DateTimeField] == DateTimeField
        assert pd_filter_mapping[datetime.datetime] == DateTimeField

    def test_numeric_mappings(self):
        """Test numeric type mappings."""
        # Integer mappings
        assert pw_filter_mapping[peewee.IntegerField] == IntField
        assert pd_filter_mapping[int] == IntField

        # Decimal mappings
        assert pw_filter_mapping[peewee.DecimalField] == DecimalField
        assert pd_filter_mapping[decimal.Decimal] == DecimalField

    def test_text_mappings(self):
        """Test text type mappings."""
        # String mappings
        assert pw_filter_mapping[peewee.CharField] == StrField
        assert pw_filter_mapping[peewee.TextField] == StrField
        assert pd_filter_mapping[str] == StrField

    def test_filter_field_instantiation(self):
        """Test that mapped filter fields can be instantiated."""
        # Test Peewee mapping results
        char_field_class = pw_filter_mapping[peewee.CharField]
        char_field = char_field_class()
        assert isinstance(char_field, StrField)

        # Test Python type mapping results
        str_field_class = pd_filter_mapping[str]
        str_field = str_field_class()
        assert isinstance(str_field, StrField)

    def test_lookup_expressions_consistency(self):
        """Test that mapped fields have expected lookup expressions."""
        # String fields should support contains operations
        str_field_class = pw_filter_mapping[peewee.CharField]
        assert "contains" in str_field_class.SUPPORTED_LOOKUP_EXPR
        assert "icontains" in str_field_class.SUPPORTED_LOOKUP_EXPR

        # Integer fields should not support contains operations
        int_field_class = pw_filter_mapping[peewee.IntegerField]
        assert "contains" not in int_field_class.SUPPORTED_LOOKUP_EXPR
        assert "icontains" not in int_field_class.SUPPORTED_LOOKUP_EXPR

        # Boolean fields should only support equality
        bool_field_class = pw_filter_mapping[peewee.BooleanField]
        assert bool_field_class.SUPPORTED_LOOKUP_EXPR == {""}


class TestMappingEdgeCases:
    """Test edge cases and error conditions."""

    def test_mapping_modification(self):
        """Test that mappings can be modified at runtime."""

        # Add a custom mapping
        class CustomField:
            pass

        class CustomFilterField:
            pass

        # Modify the mapping
        pd_filter_mapping[CustomField] = CustomFilterField

        # Should be able to retrieve it
        assert pd_filter_mapping[CustomField] == CustomFilterField

        # Clean up
        del pd_filter_mapping[CustomField]

    def test_peewee_field_with_inheritance_chain(self):
        """Test Peewee fields with complex inheritance."""

        # Create a field that inherits from IntegerField
        class BigIntegerField(peewee.IntegerField):
            pass

        class CustomBigIntegerField(BigIntegerField):
            pass

        # Should resolve to IntField through inheritance
        assert pw_filter_mapping[BigIntegerField] == IntField
        assert pw_filter_mapping[CustomBigIntegerField] == IntField

    def test_python_type_with_multiple_inheritance(self):
        """Test Python types with multiple inheritance."""

        class Mixin:
            pass

        class CustomStr(Mixin, str):
            pass

        # Should still resolve to StrField
        assert pd_filter_mapping[CustomStr] == StrField
