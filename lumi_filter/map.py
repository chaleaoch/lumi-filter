"""Field mapping configurations for different data sources.

This module provides mapping configurations that automatically map
different data source field types (Peewee ORM fields, Python types)
to appropriate filter field classes.

The mappings enable automatic field type detection and conversion
for seamless integration with various data sources.
"""

import datetime
import decimal

import peewee

from lumi_filter.field import (
    BooleanField,
    DateField,
    DateTimeField,
    DecimalField,
    IntField,
    StrField,
)
from lumi_filter.util import ClassHierarchyMapping

# Peewee field type to filter field mapping
PEEWEE_FIELD_MAP = {
    peewee.CharField: StrField,
    peewee.TextField: StrField,
    peewee.IntegerField: IntField,
    peewee.DecimalField: DecimalField,
    peewee.BooleanField: BooleanField,
    peewee.DateField: DateField,
    peewee.DateTimeField: DateTimeField,
}

# Python data type to filter field mapping
PYTHON_TYPE_MAP = {
    str: StrField,
    int: IntField,
    decimal.Decimal: DecimalField,
    bool: BooleanField,
    datetime.date: DateField,
    datetime.datetime: DateTimeField,
}

# Create mapping instances
pw_filter_mapping = ClassHierarchyMapping(PEEWEE_FIELD_MAP)
pd_filter_mapping = ClassHierarchyMapping(PYTHON_TYPE_MAP)
