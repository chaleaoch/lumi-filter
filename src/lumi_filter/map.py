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

PW_FILTER_MAP = {
    peewee.CharField: StrField,
    peewee.TextField: StrField,
    peewee.IntegerField: IntField,
    peewee.DecimalField: DecimalField,
    peewee.BooleanField: BooleanField,
    peewee.DateField: DateField,
    peewee.DateTimeField: DateTimeField,
}
PD_FILTER_MAP = {
    str: StrField,
    int: IntField,
    decimal.Decimal: DecimalField,
    bool: BooleanField,
    datetime.date: DateField,
    datetime.datetime: DateTimeField,
}

pw_filter_mapping = ClassHierarchyMapping(PW_FILTER_MAP)
pd_filter_mapping = ClassHierarchyMapping(PD_FILTER_MAP)
