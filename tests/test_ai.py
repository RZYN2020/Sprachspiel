"""Tests for the AI service."""

from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from sprachspiel.config import AIConfig, Config
from sprachspiel.services.ai import AIService


@pytest.fixture
def mock_config() -> Config:
    """Create mock configuration for testing."""
    return Config()


@pytest.fixture
def mock_ai_service(mock_config: Config) -> AIService:
    """Create mock AI service for testing."""
    return AIService(mock_config)


def create_mock_ai_config(
    provider: str = "openai",
    api_key: str = "",
    base_url: str = "https://api.openai.com/v1",
    model: str = "gpt-4o-mini",
    functions: dict | None = None,
) -> AIConfig:
    """Create a mock AIConfig for testing."""
    if functions is None:
        functions = {}
    return AIConfig(
        provider=provider,
        api_key=api_key,
        base_url=base_url,
        model=model,
        functions=functions,
    )


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
        mock_ai = create_mock_ai_config(
            api_key="test_key",
            functions={"translate": {"prompt": "Translate ${word}"}},
        )
        with patch("sprachspiel.config.Config.ai", mock_ai):
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
    async def test_call_function_not_configured(self) -> None:
        """Test calling function when not configured returns None."""
        mock_config = MagicMock()
        mock_config.ai = PropertyMock(side_effect=AttributeError("No ai config"))
        mock_config.get = MagicMock(return_value=None)
        service = AIService(mock_config)
        result = await service.call_function("translate", "test")

        assert result is None

    @pytest.mark.asyncio
    async def test_call_function_nonexistent(self, mock_ai_service: AIService) -> None:
        """Test calling non-existent function returns None."""
        result = await mock_ai_service.call_function("nonexistent", "test")

        assert result is None

    @pytest.mark.asyncio
    async def test_call_function_openai(self, mock_config: Config) -> None:
        """Test calling function with OpenAI provider."""
        mock_ai = create_mock_ai_config(
            provider="openai",
            api_key="test_key",
            functions={"translate": {"prompt": "Translate '${word}' to Chinese."}},
        )
        with patch("sprachspiel.config.Config.ai", mock_ai):
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
        mock_ai = create_mock_ai_config(
            provider="anthropic",
            api_key="test_key",
            base_url="https://api.anthropic.com/v1",
            model="claude-3-5-sonnet-20241022",
            functions={"translate": {"prompt": "Translate '${word}' to Chinese."}},
        )
        with patch("sprachspiel.config.Config.ai", mock_ai):
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
        mock_ai = create_mock_ai_config(
            provider="custom",
            api_key="test_key",
            base_url="https://custom.example.com/v1",
            model="custom-model",
            functions={"translate": {"prompt": "Translate '${word}' to Chinese."}},
        )
        with patch("sprachspiel.config.Config.ai", mock_ai):
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
        mock_ai = create_mock_ai_config(
            provider="openai",
            api_key="test_key",
            functions={"translate": {"prompt": "Translate '${word}' to Chinese."}},
        )
        with patch("sprachspiel.config.Config.ai", mock_ai):
            service = AIService(mock_config)

            with patch("requests.post") as mock_post:
                mock_post.side_effect = Exception("API error")

                with pytest.raises(Exception, match="API error"):
                    await service.call_function("translate", "test")

    @pytest.mark.asyncio
    async def test_call_function_with_kwargs(self, mock_config: Config) -> None:
        """Test calling function with custom kwargs."""
        mock_ai = create_mock_ai_config(
            provider="openai",
            api_key="test_key",
            model="gpt-4.0-mini",
            functions={"translate": {"prompt": "Translate '${word}' to ${language}."}},
        )
        with patch("sprachspiel.config.Config.ai", mock_ai):
            service = AIService(mock_config)

            with patch("requests.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    "choices": [{"message": {"content": "中文翻译"}}],
                }
                mock_response.raise_for_status.return_value = None
                mock_post.return_value = mock_response

                result = await service.call_function(
                    "translate", "test", language="Chinese"
                )

                assert result == "中文翻译"
