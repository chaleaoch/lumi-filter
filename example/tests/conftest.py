"""Test configuration and fixtures for lumi_filter example app tests."""

import pytest

from cli import clean_db, init_db
from example import create_app


@pytest.fixture(scope="session")
def app():
    app = create_app()
    init_db()
    yield app
    clean_db()


@pytest.fixture(scope="session")
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture(scope="session")
def runner(app):
    return app.test_cli_runner()
