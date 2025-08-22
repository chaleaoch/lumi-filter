"""Test configuration and fixtures for the example app."""

import pytest

from example import create_app
from extentions import database


@pytest.fixture(scope="module")
def app():
    """Create and configure a new app instance for each test."""
    # Close any existing database connection to avoid conflicts
    if not database.is_closed():
        database.close()

    # Create the app using the production create_app function
    app = create_app()

    # Configure for testing
    app.config.update(
        {
            "TESTING": True,
        }
    )

    yield app

    # Clean up after test
    if not database.is_closed():
        database.close()


@pytest.fixture(scope="module")
def client(app):
    """A test client for the app."""
    return app.test_client()
