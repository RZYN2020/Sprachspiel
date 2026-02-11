"""Tests for TTS service."""

from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from sprachspiel.config import Config
from sprachspiel.services.tts import TTSService


@pytest.fixture
def mock_config() -> Config:
    """Create mock configuration for testing."""
    return Config()


@pytest.fixture
def mock_tts_service(mock_config: Config) -> TTSService:
    """Create mock TTS service for testing."""
    return TTSService(mock_config)


class TestTTSService:
    """Unit tests for TTSService."""

    def test_init_with_config(self, mock_config: Config) -> None:
        """Test TTS service initialization."""
        service = TTSService(mock_config)

        assert service.config is mock_config
        assert isinstance(service.tts_providers, list)
        assert isinstance(service.media_dir, Path)
        assert isinstance(service.audio_format, str)

    def test_is_configured_with_empty_list(
        self, mock_tts_service: TTSService
    ) -> None:
        """Test is_configured returns False with no providers."""
        assert mock_tts_service.is_configured() is False

    def test_is_configured_with_with_providers(self, mock_config: Config) -> None:
        """Test is_configured returns True with providers configured."""
        mock_config.get = MagicMock(  # type: ignore[method-assign]
            side_effect=lambda key, default=None: {
                "tts": [{"name": "test", "module": "tts.test"}],
                "media.storage_dir": "/tmp/media",
            }.get(key, default)
        )
        service = TTSService(mock_config)

        assert service.is_configured() is True

    @pytest.mark.asyncio
    async def test_synthesize_no_provider_raises_error(
        self, mock_tts_service: TTSService
    ) -> None:
        """Test synthesize with no provider raises RuntimeError."""
        with pytest.raises(RuntimeError, match="No TTS provider configured"):
            await mock_tts_service.synthesize("test")

    @pytest.mark.asyncio
    async def test_synthesize_google_translate(
        self, mock_config: Config
    ) -> None:
        """Test Google Translate TTS synthesis."""
        mock_config.get = MagicMock(  # type: ignore[method-assign]
            side_effect=lambda key, default=None: {
                "tts": [
                    {"name": "google", "module": "tts.google_translate", "voice": "en-US"}
                ],
                "media.storage_dir": "/tmp/media",
                "media.audio_format": "mp3",
            }.get(key, default)
        )
        service = TTSService(mock_config)

        # Mock the requests.get call
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.content = b"fake audio data"
            mock_get.return_value = mock_response

            result = await service.synthesize("hello")

            assert result is not None
            assert "hello" in result

    @pytest.mark.asyncio
    async def test_synthesize_with_voice_override(
        self, mock_config: Config
    ) -> None:
        """Test synthesis with voice override."""
        mock_config.get = MagicMock(  # type: ignore[method-assign]
            side_effect=lambda key, default=None: {
                "tts": [{"name": "test", "module": "tts.test", "voice": "en-GB"}],
                "media.storage_dir": "/tmp/media",
            }.get(key, default)
        )
        service = TTSService(mock_config)

        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.content = b"test audio"
            mock_get.return_value = mock_response

            await service.synthesize("test", voice="en-US")

            # Verify voice parameter was passed
            assert mock_get.called
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs.get("tl") == "en-US" or call_kwargs.get("voice") == "en-US"

    @pytest.mark.asyncio
    async def test_synthesize_custom_module(
        self, mock_config: Config
    ) -> None:
        """Test synthesis with custom TTS module."""
        mock_config.get = MagicMock(  # type: ignore[method-assign]
            side_effect=lambda key, default=None: {
                "tts": [
                    {"name": "custom", "module": "my_module.custom_tts"}
                ],
                "media.storage_dir": "/tmp/media",
            }.get(key, default)
        )
        service = TTSService(mock_config)

        # Mock custom module
        with patch("importlib.import_module") as mock_import:
            mock_module = MagicMock()
            mock_module.custom_tts = AsyncMock(return_value="/path/to/audio.mp3")
            mock_import.return_value = mock_module

            result = await service.synthesize("test")

            assert result == "/path/to/audio.mp3"

    @pytest.mark.asyncio
    async def test_synthesize_context_short_text(
        self, mock_tts_service: TTSService
    ) -> None:
        """Test context synthesis with short text."""
        with patch.object(
            mock_tts_service, "synthesize", AsyncMock(return_value="/path/to/audio.mp3")
        ):
            result = await mock_tts_service.synthesize_context("short text", max_length=200)

            assert result == "/path/to/audio.mp3"

    @pytest.mark.asyncio
    async def test_synthesize_context_long_text(
        self, mock_tts_service: TTSService
    ) -> None:
        """Test context synthesis returns None for long text."""
        with patch.object(
            mock_tts_service, "synthesize", AsyncMock(return_value="/path/to/audio.mp3")
        ):
            result = await mock_tts_service.synthesize_context(
                "this is a very long text that exceeds the maximum length",
                max_length=50,
            )

            assert result is None


class TestTTSServiceErrorHandling:
    """Unit tests for TTSService error handling."""

    @pytest.mark.asyncio
    async def test_synthesize_all_providers_fail(
        self, mock_config: Config
    ) -> None:
        """Test when all TTSTS providers fail."""
        mock_config.get = MagicMock(  # type: ignore[method-assign]
            side_effect=lambda key, default=None: {
                "tts": [
                    {"name": "test1", "module": "tts.test1"},
                    {"name": "test2", "module": "tts.test2"},
                ],
            }.get(key, default)
        )
        service = TTSService(mock_config)

        with patch("requests.get") as mock_get:
            mock_get.side_effect = Exception("API error")

            with pytest.raises(RuntimeError, match="All TTS providers failed"):
                await service.synthesize("test")

    @pytest.mark.asyncio
    async def test_synthesize_fallback_to_second_provider(
        self, mock_config: Config
    ) -> None:
        """Test fallback to second provider when first fails."""
        mock_config.get = MagicMock(  # type: ignore[method-assign]
            side_effect=lambda key, default=None: {
                "tts": [
                    {"name": "failing", "module": "tts.fail"},
                    {"name": "working", "module": "tts.work"},
                ],
            }.get(key, default)
        )
        service = TTSService(mock_config)

        call_count = 0

        def side_effect(*args: Any, **kwargs: Any) -> MagicMock:
            nonlocal call_count
            call_count += 1
            mock_resp = MagicMock()
            if call_count == 1:  # First call fails
                mock_resp.raise_for_status.side_effect = Exception("API error")
            else:  # Second call succeeds
                mock_resp.content = b"success audio"
            return mock_resp

        with patch("requests.get") as mock_get:
            mock_get.side_effect = side_effect

            result = await service.synthesize("test")

            assert result is not None
            assert call_count == 2

    @pytest.mark.asyncio
    async def test_azure_tts_not_implemented(self, mock_config: Config) -> None:
        """Test Azure TTS raises NotImplementedError."""
        mock_config.get = MagicMock(  # type: ignore[method-assign]
            side_effect=lambda key, default=None: {
                "tts": [{"name": "azure", "module": "tts.azure"}],
            }.get(key, default)
        )
        service = TTSService(mock_config)

        with pytest.raises(
            NotImplementedError, match="azure-cognitiveservices-speech"
        ):
            await service.synthesize("test")
