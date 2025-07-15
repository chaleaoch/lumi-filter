import datetime
import decimal


class FilterField:
    def __init__(self, request_arg_name=None, source=None):
        self.request_arg_name = request_arg_name
        self.source = source

    def parse_value(self, value):
        return value, True

    SUPPORTED_LOOKUP_EXPR = {"", "!", "gt", "lt", "gte", "lte", "in", "nin"}


class IntField(FilterField):
    SUPPORTED_LOOKUP_EXPR = {"", "!", "gt", "lt", "gte", "lte"}

    def parse_value(self, value):
        try:
            return int(value), True
        except (ValueError, TypeError):
            return None, False


class StrField(FilterField):
    SUPPORTED_LOOKUP_EXPR = {"", "!", "gt", "lt", "gte", "lte", "in", "nin"}


class DecimalField(FilterField):
    SUPPORTED_LOOKUP_EXPR = {"", "!", "gt", "lt", "gte", "lte"}

    def parse_value(self, value):
        try:
            return decimal.Decimal(value), True
        except Exception:
            return None, False


class BooleanField(FilterField):
    SUPPORTED_LOOKUP_EXPR = {""}

    def parse_value(self, value):
        try:
            return bool(value), True
        except Exception:
            return None, False


class DateField(FilterField):
    SUPPORTED_LOOKUP_EXPR = {"", "!", "gt", "lt", "gte", "lte"}

    def parse_value(self, value):
        try:
            return datetime.strptime(value, "%Y-%m-%d").date(), True
        except Exception:
            return None, False


class DateTimeField(FilterField):
    SUPPORTED_LOOKUP_EXPR = {"", "!", "gt", "lt", "gte", "lte"}

    def parse_value(self, value):
        try:
            return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S"), True
        except Exception:
            return None, False
