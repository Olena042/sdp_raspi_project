import os
import pytest

# Ensure mock mode is enabled for tests
os.environ["MOCK_SENSORS"] = "True"

from app import app as flask_app


@pytest.fixture
def app():
    """Create application for testing."""
    flask_app.config.update({
        "TESTING": True,
    })
    yield flask_app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()
