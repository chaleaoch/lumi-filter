"""Test configuration and fixtures for lumi_filter package tests."""

import datetime
import decimal
from typing import Optional

import peewee
import pytest
import pydantic

# Test database setup
test_db = peewee.SqliteDatabase(":memory:")


# Sample Peewee models for testing
class BaseModel(peewee.Model):
    """Base model for all test models."""

    class Meta:
        database = test_db


class Category(BaseModel):
    """Test category model."""
    
    id = peewee.AutoField()
    name = peewee.CharField(max_length=100)
    description = peewee.TextField(null=True)
    created_at = peewee.DateTimeField(default=datetime.datetime.now)


class Product(BaseModel):
    """Test product model."""
    
    id = peewee.AutoField()
    name = peewee.CharField(max_length=200)
    price = peewee.DecimalField(max_digits=10, decimal_places=2)
    is_active = peewee.BooleanField(default=True)
    category = peewee.ForeignKeyField(Category, backref="products")
    description = peewee.TextField(null=True)
    created_at = peewee.DateTimeField(default=datetime.datetime.now)
    tags = peewee.CharField(max_length=500, null=True)  # JSON string of tags


# Sample Pydantic models for testing
class CategorySchema(pydantic.BaseModel):
    """Test category schema."""
    
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime.datetime


class ProductSchema(pydantic.BaseModel):
    """Test product schema."""
    
    id: int
    name: str
    price: decimal.Decimal
    is_active: bool = True
    category_id: int
    description: Optional[str] = None
    created_at: datetime.datetime
    tags: Optional[str] = None


@pytest.fixture(scope="session")
def setup_test_db():
    """Set up test database and tables."""
    test_db.connect()
    test_db.create_tables([Category, Product])
    
    # Create sample data
    category1 = Category.create(name="Electronics", description="Electronic devices")
    category2 = Category.create(name="Books", description="Books and literature")
    category3 = Category.create(name="Clothing", description="Apparel and accessories")
    
    Product.create(
        name="Laptop",
        price=decimal.Decimal("999.99"),
        is_active=True,
        category=category1,
        description="High-performance laptop",
        tags='["portable", "gaming"]'
    )
    Product.create(
        name="Smartphone",
        price=decimal.Decimal("599.50"),
        is_active=True,
        category=category1,
        description="Latest smartphone model",
        tags='["mobile", "communication"]'
    )
    Product.create(
        name="Programming Book",
        price=decimal.Decimal("49.99"),
        is_active=True,
        category=category2,
        description="Learn programming fundamentals",
        tags='["education", "programming"]'
    )
    Product.create(
        name="T-Shirt",
        price=decimal.Decimal("19.99"),
        is_active=False,
        category=category3,
        description="Cotton t-shirt",
        tags='["casual", "cotton"]'
    )
    Product.create(
        name="Jeans",
        price=decimal.Decimal("79.99"),
        is_active=True,
        category=category3,
        description="Denim jeans",
        tags='["casual", "denim"]'
    )
    
    yield test_db
    
    test_db.drop_tables([Category, Product])
    test_db.close()


@pytest.fixture
def sample_products_data():
    """Sample product data as dictionaries for iterable testing."""
    return [
        {
            "id": 1,
            "name": "Laptop",
            "price": decimal.Decimal("999.99"),
            "is_active": True,
            "category_id": 1,
            "category_name": "Electronics",
            "description": "High-performance laptop",
            "created_at": datetime.datetime(2024, 1, 1, 12, 0, 0),
            "tags": '["portable", "gaming"]'
        },
        {
            "id": 2,
            "name": "Smartphone",
            "price": decimal.Decimal("599.50"),
            "is_active": True,
            "category_id": 1,
            "category_name": "Electronics",
            "description": "Latest smartphone model",
            "created_at": datetime.datetime(2024, 1, 2, 12, 0, 0),
            "tags": '["mobile", "communication"]'
        },
        {
            "id": 3,
            "name": "Programming Book",
            "price": decimal.Decimal("49.99"),
            "is_active": True,
            "category_id": 2,
            "category_name": "Books",
            "description": "Learn programming fundamentals",
            "created_at": datetime.datetime(2024, 1, 3, 12, 0, 0),
            "tags": '["education", "programming"]'
        },
        {
            "id": 4,
            "name": "T-Shirt",
            "price": decimal.Decimal("19.99"),
            "is_active": False,
            "category_id": 3,
            "category_name": "Clothing",
            "description": "Cotton t-shirt",
            "created_at": datetime.datetime(2024, 1, 4, 12, 0, 0),
            "tags": '["casual", "cotton"]'
        },
        {
            "id": 5,
            "name": "Jeans",
            "price": decimal.Decimal("79.99"),
            "is_active": True,
            "category_id": 3,
            "category_name": "Clothing",
            "description": "Denim jeans",
            "created_at": datetime.datetime(2024, 1, 5, 12, 0, 0),
            "tags": '["casual", "denim"]'
        }
    ]


@pytest.fixture
def sample_pydantic_models(sample_products_data):
    """Sample Pydantic model instances for testing."""
    return [ProductSchema(**data) for data in sample_products_data]


@pytest.fixture
def peewee_query(setup_test_db):
    """Peewee query fixture for testing."""
    return Product.select()


@pytest.fixture
def category_query(setup_test_db):
    """Category query fixture for testing."""
    return Category.select()


# Mock data for various test scenarios
@pytest.fixture
def mixed_type_data():
    """Mixed data types for comprehensive testing."""
    return [
        {"id": 1, "name": "Item A", "value": 10, "active": True},
        {"id": 2, "name": "Item B", "value": 20, "active": False},
        {"id": 3, "name": "Item C", "value": 30, "active": True},
        {"id": None, "name": None, "value": None, "active": None},  # Test null values
    ]


@pytest.fixture
def edge_case_data():
    """Edge case data for robust testing."""
    return [
        {"text": "", "number": 0, "decimal": decimal.Decimal("0.00")},
        {"text": "   ", "number": -1, "decimal": decimal.Decimal("-99.99")},
        {"text": "Special chars: !@#$%", "number": 999999, "decimal": decimal.Decimal("999999.99")},
    ]
