"""Tests for TTS service."""

from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from sprachspiel.config import Config
from sprachspiel.exceptions import TTSError
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

    def test_is_configured_with_empty_list(self, mock_tts_service: TTSService) -> None:
        """Test is_configured returns False with no providers."""
        assert mock_tts_service.is_configured() is False

    def test_is_configured_with_with_providers(self) -> None:
        """Test is_configured returns True with providers configured."""
        config = Config(
            {
                "tts": [{"name": "test", "module": "tts.test"}],
                "media": {"storage_dir": "/tmp/media"},
            }
        )
        service = TTSService(config)

        assert service.is_configured() is True

    @pytest.mark.asyncio
    async def test_synthesize_no_provider_raises_error(self, mock_tts_service: TTSService) -> None:
        """Test synthesize with no provider raises TTSError."""
        with pytest.raises(TTSError, match="No TTS provider configured"):
            await mock_tts_service.synthesize("test")

    @pytest.mark.asyncio
    async def test_synthesize_google_translate(self) -> None:
        """Test Google Translate TTS synthesis."""
        config = Config(
            {
                "tts": [{"name": "google", "module": "google_translate", "voice": "en-US"}],
                "media": {"storage_dir": "/tmp/media", "audio_format": "mp3"},
            }
        )
        service = TTSService(config)

        # Mock the requests.get call
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.content = b"fake audio data"
            mock_get.return_value = mock_response

            result = await service.synthesize("hello")

            assert result is not None
            assert "hello" in result

    @pytest.mark.asyncio
    async def test_synthesize_with_voice_override(self) -> None:
        """Test synthesis with voice override."""
        config = Config(
            {
                "tts": [{"name": "google", "module": "google_translate", "voice": "en-GB"}],
                "media": {"storage_dir": "/tmp/media"},
            }
        )
        service = TTSService(config)

        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.content = b"test audio"
            mock_get.return_value = mock_response

            await service.synthesize("test", voice="en-US")

            # Verify voice parameter was passed
            assert mock_get.called
            call_args = mock_get.call_args
            if call_args.kwargs.get("params"):
                assert call_args.kwargs["params"].get("tl") == "en-US"
            else:
                assert call_args.kwargs.get("voice") == "en-US"

    @pytest.mark.asyncio
    async def test_synthesize_custom_module(self) -> None:
        """Test synthesis with custom TTS module."""
        config = Config(
            {
                "tts": [{"name": "custom", "module": "my_module.custom_tts"}],
                "media": {"storage_dir": "/tmp/media"},
            }
        )
        service = TTSService(config)

        # Mock custom module - returns a path that will be returned directly
        with patch("importlib.import_module") as mock_import:
            mock_module = MagicMock()
            # Return a path in the expected media dir so it's returned directly
            mock_module.custom_tts = AsyncMock(return_value="/tmp/media/test.mp3")
            mock_import.return_value = mock_module

            result = await service.synthesize("test")

            # When the returned path exists (as str), it's returned directly
            assert result == "/tmp/media/test.mp3"

    @pytest.mark.asyncio
    async def test_synthesize_context_short_text(self, mock_tts_service: TTSService) -> None:
        """Test context synthesis with short text."""
        with patch.object(
            mock_tts_service, "synthesize", AsyncMock(return_value="/path/to/audio.mp3")
        ):
            result = await mock_tts_service.synthesize_context("short text", max_length=200)

            assert result == "/path/to/audio.mp3"

    @pytest.mark.asyncio
    async def test_synthesize_context_long_text(self, mock_tts_service: TTSService) -> None:
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
    async def test_synthesize_all_providers_fail(self) -> None:
        """Test when all TTSTS providers fail."""
        config = Config(
            {
                "tts": [
                    {"name": "test1", "module": "google_translate"},
                    {"name": "test2", "module": "google_translate"},
                ],
            }
        )
        service = TTSService(config)

        with patch("requests.get") as mock_get:
            mock_get.side_effect = Exception("API error")

            with pytest.raises(TTSError, match="All TTS providers failed"):
                await service.synthesize("test")

    @pytest.mark.asyncio
    async def test_synthesize_fallback_to_second_provider(self) -> None:
        """Test fallback to second provider when first fails."""
        config = Config(
            {
                "tts": [
                    {"name": "failing", "module": "google_translate"},
                    {"name": "working", "module": "google_translate"},
                ],
            }
        )
        service = TTSService(config)

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
        service = TTSService(mock_config)

        # Test the internal _synthesize_azure method directly
        from sprachspiel.config import TTSConfig

        with pytest.raises(NotImplementedError, match="azure-cognitiveservices-speech"):
            await service._synthesize_azure("test", TTSConfig(name="azure"), None)
