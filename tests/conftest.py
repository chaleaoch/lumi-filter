"""
pytest configuration file - provides test fixtures and common configuration

This file contains the basic configuration for the entire test suite:
- Test fixtures
- Mock data
- Test configuration
"""

import datetime
import decimal

import pytest

from lumi_filter.field import BooleanField, DateField, DecimalField, IntField, StrField


@pytest.fixture
def sample_dict_data():
    """Provides sample dictionary data for testing"""
    return [
        {
            "id": 1,
            "name": "Alice",
            "age": 30,
            "active": True,
            "salary": decimal.Decimal("5000.00"),
        },
        {
            "id": 2,
            "name": "Bob",
            "age": 25,
            "active": False,
            "salary": decimal.Decimal("4500.00"),
        },
        {
            "id": 3,
            "name": "Charlie",
            "age": 35,
            "active": True,
            "salary": decimal.Decimal("6000.00"),
        },
        {
            "id": 4,
            "name": "David",
            "age": 28,
            "active": True,
            "salary": decimal.Decimal("5500.00"),
        },
    ]


@pytest.fixture
def sample_request_args():
    """Provides sample request arguments"""
    return {"name": "Alice", "age__gte": "25", "active": "true", "ordering": "age"}


@pytest.fixture
def empty_request_args():
    """Provides empty request arguments"""
    return {}


@pytest.fixture
def nested_dict_data():
    """Provides nested dictionary data for testing"""
    return [
        {
            "id": 1,
            "user": {"name": "Alice", "profile": {"age": 30}},
            "created_at": datetime.date(2024, 1, 1),
        },
        {
            "id": 2,
            "user": {"name": "Bob", "profile": {"age": 25}},
            "created_at": datetime.date(2024, 1, 2),
        },
    ]


@pytest.fixture
def invalid_data():
    """Provides invalid data for error testing"""
    return "invalid_data_type"


class SampleFilterFields:
    """Sample filter fields collection"""

    @staticmethod
    def get_basic_fields():
        """Get basic fields"""
        return {
            "id": IntField(),
            "name": StrField(),
            "age": IntField(),
            "active": BooleanField(),
            "salary": DecimalField(),
        }

    @staticmethod
    def get_date_fields():
        """Get date fields"""
        return {
            "created_at": DateField(),
        }


# Test plugins
pytest_plugins = []
