"""Tests for dictionary service."""

from unittest.mock import MagicMock, patch

import pytest

from sprachspiel.config import Config
from sprachspiel.services.dictionary import DictionaryService


@pytest.fixture
def mock_config() -> Config:
    """Create mock configuration for testing."""
    return Config()


@pytest.fixture
def mock_dictionary_service(mock_config: Config) -> DictionaryService:
    """Create mock dictionary service for testing."""
    return DictionaryService(mock_config)


class TestDictionaryService:
    """Unit tests for DictionaryService."""

    def test_init_with_config(self, mock_config: Config) -> None:
        """Test dictionary service initialization."""
        service = DictionaryService(mock_config)

        assert service.config is mock_config
        assert isinstance(service.dictionaries, list)

    def test_is_configured_with_empty_list(self, mock_config: Config) -> None:
        """Test is_configured returns False with no dictionaries."""
        service = DictionaryService(mock_config)

        assert service.is_configured() is False

    def test_is_configured_with_dictionaries(self, mock_config: Config) -> None:
        """Test is_configured returns True with dictionaries configured."""
        # Mock config to return dictionary list
        mock_config.get = MagicMock(  # type: ignore[method-assign]
            return_value=[
            {"name": "test", "module": "test.dict"},
        ])
        service = DictionaryService(mock_config)

        assert service.is_configured() is True

    @pytest.mark.asyncio
    async def test_lookup_with_no_dictionaries(
        self, mock_dictionary_service: DictionaryService
    ) -> None:
        """Test lookup with no dictionaries returns empty result."""
        result = await mock_dictionary_service.lookup("test")

        assert result["translation"] is None
        assert result["definition"] is None
        assert result["example"] is None

    @pytest.mark.asyncio
    async def test_lookup_oxford_fallback(
        self, mock_config: Config
    ) -> None:
        """Test Oxford dictionary lookup."""
        mock_config.get = MagicMock(  # type: ignore[method-assign]
            return_value={
                "dictionaries": [
                    {
                        "name": "oxford",
                        "module": "dicts.oxford_api",
                        "api_key": "test:secret",
                    }
                ]
            }
        )
        service = DictionaryService(mock_config)

        # Mock actual API call
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = [
                {
                    "senses": [
                        {
                            "definitions": [
                                {"value": "Moving at high speed."}
                            ]
                        }
                    ]
                }
            ]
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = await service.lookup("quick")

            assert result["definition"] == "Moving at high speed."

    @pytest.mark.asyncio
    async def test_lookup_youdao_fallback(self, mock_config: Config) -> None:
        """Test Youdao dictionary lookup."""
        mock_config.get = MagicMock(  # type: ignore[method-assign]
            return_value={
                "dictionaries": [
                    {
                        "name": "youdao",
                        "module": "dicts.youdao_api",
                        "api_key": "test_key",
                    }
                ]
            }
        )
        service = DictionaryService(mock_config)

        # Mock actual API call
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "translation": ["快速"],
                "web": [[{"value": ["Example sentence."]}]],
            }
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = await service.lookup("quick")

            assert result["translation"] == "快速"

    @pytest.mark.asyncio
    async def test_lookup_custom_module(self, mock_config: Config) -> None:
        """Test lookup with custom dictionary module."""
        mock_config.get = MagicMock(  # type: ignore[method-assign]
            return_value={
                "dictionaries": [
                    {
                        "name": "custom",
                        "module": "my_module.custom_lookup",
                    }
                ]
            }
        )
        service = DictionaryService(mock_config)

        # Mock custom module import
        with patch("importlib.import_module") as mock_import:
            mock_module = MagicMock()
            mock_module.custom_lookup = MagicMock(return_value={"translation": "custom"})
            mock_import.return_value = mock_module

            result = await service.lookup("test")

            assert result["translation"] == "custom"


class TestDictionaryServiceErrorHandling:
    """Unit tests for DictionaryService error handling."""

    @pytest.mark.asyncio
    async def test_lookup_api_failure_returns_empty(
        self, mock_config: Config
    ) -> None:
        """Test that API failures don't crash lookup."""
        mock_config.get = MagicMock(  # type: ignore[method-assign]
            return_value={
                "dictionaries": [
                    {
                        "name": "test",
                        "module": "dicts.test_api",
                        "api_key": "test_key",
                    }
                ]
            }
        )
        service = DictionaryService(mock_config)

        # Mock failed API call
        with patch("requests.get") as mock_get:
            mock_get.side_effect = Exception("API error")

            result = await service.lookup("test")

            # Should return empty result, not crash
            assert result["translation"] is None
            assert result["definition"] is None
            assert result["example"] is None

    @pytest.mark.asyncio
    async def test_lookup_custom_module_failure(self, mock_config: Config) -> None:
        """Test custom module failure handling."""
        mock_config.get = MagicMock(  # type: ignore[method-assign]
            return_value={
                "dictionaries": [
                    {
                        "name": "custom",
                        "module": "nonexistent.module",
                    }
                ]
            }
        )
        service = DictionaryService(mock_config)

        with pytest.raises(RuntimeError, match="Failed to load custom dictionary"):
            await service.lookup("test")
