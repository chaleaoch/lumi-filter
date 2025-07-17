"""
Field mapping configurations for different ORM and data types.

This module defines mappings between ORM field types (like Peewee)
and Python data types to their corresponding FilterField implementations.
It uses ClassHierarchyMapping to support inheritance-based lookups.
"""

import datetime
import decimal
from typing import Dict, Type

import peewee

from lumi_filter.field import (
    BooleanField,
    DateField,
    DateTimeField,
    DecimalField,
    FilterField,
    IntField,
    StrField,
)
from lumi_filter.util import ClassHierarchyMapping

# Mapping from Peewee field types to FilterField types
PW_FILTER_MAP: Dict[Type[peewee.Field], Type[FilterField]] = {
    peewee.CharField: StrField,  # Variable-length character field
    peewee.TextField: StrField,  # Large text field
    peewee.IntegerField: IntField,  # Integer field
    peewee.DecimalField: DecimalField,  # High-precision decimal field
    peewee.BooleanField: BooleanField,  # Boolean field
    peewee.DateField: DateField,  # Date field (no time)
    peewee.DateTimeField: DateTimeField,  # Date and time field
}

# Mapping from Python types to FilterField types
PD_FILTER_MAP: Dict[Type, Type[FilterField]] = {
    str: StrField,  # String type
    int: IntField,  # Integer type
    decimal.Decimal: DecimalField,  # Decimal type for precise arithmetic
    bool: BooleanField,  # Boolean type
    datetime.date: DateField,  # Date type
    datetime.datetime: DateTimeField,  # DateTime type
}

# Create hierarchy-aware mappings that support inheritance
pw_filter_mapping = ClassHierarchyMapping(PW_FILTER_MAP)
"""
ClassHierarchyMapping for Peewee field types.

This mapping automatically handles inheritance, so subclasses of mapped
field types will use the same FilterField unless explicitly overridden.

Example:
    >>> pw_filter_mapping[peewee.CharField]  # Returns StrField
    >>> pw_filter_mapping[CustomCharField]   # Also returns StrField if CustomCharField inherits from CharField
"""

pd_filter_mapping = ClassHierarchyMapping(PD_FILTER_MAP)
"""
ClassHierarchyMapping for Python data types.

This mapping supports inheritance for Python types, allowing custom
types that inherit from basic types to automatically use appropriate FilterFields.

Example:
    >>> pd_filter_mapping[str]        # Returns StrField
    >>> pd_filter_mapping[MyString]   # Also returns StrField if MyString inherits from str
"""
