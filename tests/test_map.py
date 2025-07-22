"""
Test map module functionality

This file tests:
- Field mapping configurations
- Peewee field to filter field mapping
- Python type to filter field mapping
"""

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
from lumi_filter.map import (
    PEEWEE_FIELD_MAP,
    PYTHON_TYPE_MAP,
    pd_filter_mapping,
    pw_filter_mapping,
)


class TestPeeweeFieldMapping:
    """Test Peewee field type mapping"""

    def test_peewee_char_field_mapping(self):
        """Test CharField maps to StrField"""
        assert PEEWEE_FIELD_MAP[peewee.CharField] == StrField

    def test_peewee_text_field_mapping(self):
        """Test TextField maps to StrField"""
        assert PEEWEE_FIELD_MAP[peewee.TextField] == StrField

    def test_peewee_integer_field_mapping(self):
        """Test IntegerField maps to IntField"""
        assert PEEWEE_FIELD_MAP[peewee.IntegerField] == IntField

    def test_peewee_decimal_field_mapping(self):
        """Test DecimalField maps to DecimalField"""
        assert PEEWEE_FIELD_MAP[peewee.DecimalField] == DecimalField

    def test_peewee_boolean_field_mapping(self):
        """Test BooleanField maps to BooleanField"""
        assert PEEWEE_FIELD_MAP[peewee.BooleanField] == BooleanField

    def test_peewee_date_field_mapping(self):
        """Test DateField maps to DateField"""
        assert PEEWEE_FIELD_MAP[peewee.DateField] == DateField

    def test_peewee_datetime_field_mapping(self):
        """Test DateTimeField maps to DateTimeField"""
        assert PEEWEE_FIELD_MAP[peewee.DateTimeField] == DateTimeField


class TestPythonTypeMapping:
    """Test Python type mapping"""

    def test_str_type_mapping(self):
        """Test str maps to StrField"""
        assert PYTHON_TYPE_MAP[str] == StrField

    def test_int_type_mapping(self):
        """Test int maps to IntField"""
        assert PYTHON_TYPE_MAP[int] == IntField

    def test_decimal_type_mapping(self):
        """Test Decimal maps to DecimalField"""
        assert PYTHON_TYPE_MAP[decimal.Decimal] == DecimalField

    def test_bool_type_mapping(self):
        """Test bool maps to BooleanField"""
        assert PYTHON_TYPE_MAP[bool] == BooleanField

    def test_date_type_mapping(self):
        """Test date maps to DateField"""
        assert PYTHON_TYPE_MAP[datetime.date] == DateField

    def test_datetime_type_mapping(self):
        """Test datetime maps to DateTimeField"""
        assert PYTHON_TYPE_MAP[datetime.datetime] == DateTimeField


class TestClassHierarchyMappingInstances:
    """Test ClassHierarchyMapping instances"""

    def test_pw_filter_mapping_lookup(self):
        """Test Peewee filter mapping lookup"""
        result = pw_filter_mapping[peewee.CharField]
        assert result == StrField

    def test_pw_filter_mapping_contains(self):
        """Test Peewee filter mapping contains check"""
        assert peewee.CharField in pw_filter_mapping
        assert peewee.TextField in pw_filter_mapping

    def test_pd_filter_mapping_lookup(self):
        """Test Python type filter mapping lookup"""
        result = pd_filter_mapping[str]
        assert result == StrField

    def test_pd_filter_mapping_contains(self):
        """Test Python type filter mapping contains check"""
        assert str in pd_filter_mapping
        assert int in pd_filter_mapping
        assert bool in pd_filter_mapping

    def test_pw_filter_mapping_key_error(self):
        """Test KeyError for unmapped Peewee field type"""

        class CustomField(peewee.Field):
            pass

        with pytest.raises(KeyError):
            pw_filter_mapping[CustomField]

    def test_pd_filter_mapping_key_error(self):
        """Test KeyError for unmapped Python type"""

        class CustomType:
            pass

        with pytest.raises(KeyError):
            pd_filter_mapping[CustomType]
