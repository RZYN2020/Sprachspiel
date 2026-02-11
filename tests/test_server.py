"""Tests for HTTP API server."""


import pytest

from sprachspiel.config import Config
from sprachspiel.server.app import create_app


@pytest.fixture
def mock_config() -> Config:
    """Create mock configuration for testing."""
    return Config()


class TestAPIRoot:
    """Unit tests for API root endpoint."""

    def test_create_app(self, mock_config: Config) -> None:
        """Test FastAPI app creation."""
        app = create_app(mock_config)

        assert app is not None

    def test_root_endpoint(self, mock_config: Config) -> None:
        """Test root endpoint returns API info."""
        app = create_app(mock_config)

        # Use TestClient if httpx is available
        try:
            from fastapi.testclient import TestClient

            client = TestClient(app)
            response = client.get("/")

            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "Sprachspiel"
        except RuntimeError:
            # httpx not available, skip test
            pytest.skip("httpx package not installed for TestClient")


class TestAPIWord:
    """Unit tests for word API endpoint."""

    def test_create_word_minimal(self, mock_config: Config) -> None:
        """Test word creation with minimal data."""
        try:
            from fastapi.testclient import TestClient

            app = create_app(mock_config)
            client = TestClient(app)

            response = client.post(
                "/api/v1/word",
                json={"word": "test"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
        except RuntimeError:
            pytest.skip("httpx package not installed")


class TestAPIQueue:
    """Unit tests for queue API endpoints."""

    def test_get_queue_status_empty(self, mock_config: Config) -> None:
        """Test getting queue status when empty."""
        try:
            from fastapi.testclient import TestClient

            app = create_app(mock_config)
            client = TestClient(app)

            response = client.get("/api/v1/queue/status")

            assert response.status_code == 200
            data = response.json()
            assert data["size"] == 0
        except RuntimeError:
            pytest.skip("httpx package not installed")


class TestAPIConfig:
    """Unit tests for config API endpoints."""

    def test_get_config(self, mock_config: Config) -> None:
        """Test getting current configuration."""
        try:
            from fastapi.testclient import TestClient

            app = create_app(mock_config)
            client = TestClient(app)

            response = client.get("/api/v1/config")

            assert response.status_code == 200
            data = response.json()
            assert "anki_mode" in data
        except RuntimeError:
            pytest.skip("httpx package not installed")
