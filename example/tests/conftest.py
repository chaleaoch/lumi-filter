"""Test configuration and fixtures for lumi_filter example app tests."""

from datetime import datetime
from decimal import Decimal

import pytest

from app.db_model import Category, Product
from example import create_app
from extentions import db


@pytest.fixture(scope="session")
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "DATABASE": ":memory:",  # Use in-memory database for tests
        }
    )

    with app.app_context():
        # Create tables
        db.database.create_tables([Category, Product])

        # Create sample data
        electronics = Category.create(name="Electronics")
        clothing = Category.create(name="Clothing")
        books = Category.create(name="Books")

        # Create products
        Product.create(
            name="iPhone 15",
            price=Decimal("999.99"),
            is_active=True,
            category=electronics,
            created_at=datetime(2024, 1, 15, 10, 0, 0),
        )
        Product.create(
            name="MacBook Pro",
            price=Decimal("2499.99"),
            is_active=True,
            category=electronics,
            created_at=datetime(2024, 2, 20, 14, 30, 0),
        )
        Product.create(
            name="Apple Watch",
            price=Decimal("399.99"),
            is_active=False,
            category=electronics,
            created_at=datetime(2024, 3, 10, 9, 15, 0),
        )
        Product.create(
            name="T-Shirt",
            price=Decimal("29.99"),
            is_active=True,
            category=clothing,
            created_at=datetime(2024, 1, 5, 16, 45, 0),
        )
        Product.create(
            name="Jeans",
            price=Decimal("79.99"),
            is_active=True,
            category=clothing,
            created_at=datetime(2024, 2, 28, 11, 20, 0),
        )
        Product.create(
            name="Python Programming Book",
            price=Decimal("49.99"),
            is_active=True,
            category=books,
            created_at=datetime(2024, 1, 12, 8, 30, 0),
        )

        yield app
        # Clean up
        db.database.drop_tables([Category, Product])


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()
