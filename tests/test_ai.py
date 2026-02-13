"""Tests for the AI service."""

from unittest.mock import MagicMock, patch

import pytest

from sprachspiel.config import Config
from sprachspiel.services.ai import AIService


@pytest.fixture
def mock_config() -> Config:
    """Create mock configuration for testing."""
    return Config()


@pytest.fixture
def mock_ai_service(mock_config: Config) -> AIService:
    """Create mock AI service for testing."""
    return AIService(mock_config)


class TestAIService:
    """Unit tests for AIService."""

    def test_init_with_config(self, mock_config: Config) -> None:
        """Test AI service initialization."""
        service = AIService(mock_config)

        assert service.config is mock_config
        assert isinstance(service.provider, str)
        assert isinstance(service.functions, dict)

    def test_is_configured_without_api_key(self, mock_ai_service: AIService) -> None:
        """Test is_configured returns False without API key."""
        assert mock_ai_service.is_configured() is False

    def test_is_configured_with_api_key_and_functions(self, mock_config: Config) -> None:
        """Test is_configured returns True with API key and functions."""
        mock_config.get = MagicMock(  # type: ignore[method-assign]
            side_effect=lambda key, default=None: {
                "ai.api_key": "test_key",
                "ai.functions": {
                    "translate": {"prompt": "Translate ${word}"},
                },
            }.get(key, default)
        )
        service = AIService(mock_config)

        assert service.is_configured() is True

    def test_has_function(self, mock_ai_service: AIService) -> None:
        """Test has_function checks if function exists."""
        assert mock_ai_service.has_function("nonexistent") is False

    def test_get_custom_functions(self, mock_ai_service: AIService) -> None:
        """Test get_custom_functions returns only custom functions."""
        custom = mock_ai_service.get_custom_functions()

        assert "translate" not in custom
        assert "example" not in custom

    @pytest.mark.asyncio
    async def test_call_function_not_configured(
        self, mock_ai_service: AIService
    ) -> None:
        """Test calling function when not configured returns None."""
        result = await mock_ai_service.call_function("translate", "test")

        assert result is None

    @pytest.mark.asyncio
    async def test_call_function_nonexistent(
        self, mock_ai_service: AIService
    ) -> None:
        """Test calling non-existent function returns None."""
        result = await mock_ai_service.call_function("nonexistent", "test")

        assert result is None

    @pytest.mark.asyncio
    async def test_call_function_openai(self, mock_config: Config) -> None:
        """Test calling function with OpenAI provider."""
        mock_config.get = MagicMock(  # type: ignore[method-assign]
            side_effect=lambda key, default=None: {
                "ai.provider": "openai",
                "ai.api_key": "test_key",
                "ai.base_url": "https://api.openai.com/v1",
                "ai.model": "gpt-4o-mini",
                "ai.functions": {
                    "translate": {"prompt": "Translate '${word}' to Chinese."},
                },
            }.get(key, default)
        )
        service = AIService(mock_config)

        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "翻译"}}],
            }
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            result = await service.call_function("translate", "test")

            assert result == "翻译"

    @pytest.mark.asyncio
    async def test_call_function_anthropic(self, mock_config: Config) -> None:
        """Test calling function with Anthropic provider."""
        mock_config.get = MagicMock(  # type: ignore[method-assign]
            side_effect=lambda key, default=None: {
                "ai.provider": "anthropic",
                "ai.api_key": "test_key",
                "ai.base_url": "https://api.anthropic.com/v1",
                "ai.model": "claude-3-5-sonnet-20241022",
                "ai.functions": {
                    "translate": {"prompt": "Translate '${word}' to Chinese."},
                },
            }.get(key, default)
        )
        service = AIService(mock_config)

        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "content": [{"text": "翻译"}],
            }
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            result = await service.call_function("translate", "test")

            assert result == "翻译"

    @pytest.mark.asyncio
    async def test_call_function_custom_endpoint(self, mock_config: Config) -> None:
        """Test calling function with custom endpoint."""
        mock_config.get = MagicMock(  # type: ignore[method-assign]
            side_effect=lambda key, default=None: {
                "ai.provider": "custom",
                "ai.api_key": "test_key",
                "ai.base_url": "https://custom.example.com/v1",
                "ai.model": "custom-model",
                "ai.functions": {
                    "translate": {"prompt": "Translate '${word}' to Chinese."},
                },
            }.get(key, default)
        )
        service = AIService(mock_config)

        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "翻译"}}],
            }
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            result = await service.call_function("translate", "test")

            assert result == "翻译"


class TestAIServiceErrorHandling:
    """Unit tests for AIService error handling."""

    @pytest.mark.asyncio
    async def test_call_function_api_failure_raises_error(
        self, mock_config: Config
    ) -> None:
        """Test API failures raise errors."""
        mock_config.get = MagicMock(  # type: ignore[method-assign]
            side_effect=lambda key, default=None: {
                "ai.provider": "openai",
                "ai.api_key": "test_key",
                "ai.base_url": "https://api.openai.com/v1",
                "ai.model": "gpt-4o-mini",
                "ai.functions": {
                    "translate": {"prompt": "Translate '${word}' to Chinese."},
                },
            }.get(key, default)
        )
        service = AIService(mock_config)

        with patch("requests.post") as mock_post:
            mock_post.side_effect = Exception("API error")

            with pytest.raises(Exception, match="API error"):
                await service.call_function("translate", "test")

    @pytest.mark.asyncio
    async def test_call_function_with_kwargs(self, mock_config: Config) -> None:
        """Test calling function with custom kwargs."""
        mock_config.get = MagicMock(  # type: ignore[method-assign]
            side_effect=lambda key, default=None: {
                "ai.provider": "openai",
                "ai.api_key": "test_key",
                "ai.base_url": "https://api.openai.com/v1",
                "ai.model": "gpt-4.0-mini",
                "ai.functions": {
                    "translate": {"prompt": "Translate '${word}' to ${language}."},
                },
            }.get(key, default)
        )
        service = AIService(mock_config)

        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "中文翻译"}}],
            }
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            result = await service.call_function("translate", "test", language="Chinese")

            assert result == "中文翻译"
