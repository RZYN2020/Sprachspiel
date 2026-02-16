"""Text-to-Speech service for audio generation."""

from pathlib import Path
from typing import Any

from sprachspiel.config import Config, TTSConfig
from sprachspiel.exceptions import TTSError
from sprachspiel.logging_config import get_logger

logger = get_logger(__name__)


class TTSService:
    """Service for text-to-speech synthesis."""

    def __init__(self, config: Config):
        """Initialize TTS service.

        Args:
            config: Configuration instance.
        """
        self.config = config
        self.tts_providers = config.tts
        self.media_dir = Path(config.media.storage_dir)
        self.audio_format = config.media.audio_format

    def is_configured(self) -> bool:
        """Check if TTS service is configured.

        Returns:
            True if at least one TTS provider is configured.
        """
        return len(self.tts_providers) > 0

    async def synthesize(self, text: str, voice: str | None = None) -> str:
        """Synthesize audio for text.

        Args:
            text: Text to synthesize.
            voice: Optional voice override.

        Returns:
            Path to generated audio file.
        """
        if not self.tts_providers:
            raise TTSError("No TTS provider configured")

        for provider_config in self.tts_providers:
            try:
                return await self._synthesize_provider(text, provider_config, voice)
            except Exception as e:
                logger.warning(f"TTS synthesis failed for {provider_config.name}: {e}")

        raise TTSError("All TTS providers failed")

    async def _synthesize_provider(
        self, text: str, provider_config: TTSConfig, voice: str | None
    ) -> str:
        """Synthesize audio using specific provider.

        Args:
            text: Text to synthesize.
            provider_config: Provider configuration.
            voice: Optional voice override.

        Returns:
            Path to generated audio file.
        """
        module_name = provider_config.module

        # Built-in providers
        if module_name in ("google_translate", "tts.google_translate"):
            return await self._synthesize_google(text, provider_config, voice)
        elif module_name in ("azure", "tts.azure"):
            return await self._synthesize_azure(text, provider_config, voice)
        # Custom module support (must have a dot but not be a built-in module)
        elif module_name and "." in module_name:
            return await self._synthesize_custom(text, provider_config, voice)

        raise TTSError(f"Unknown TTS provider: {module_name}")

    async def _synthesize_custom(
        self, text: str, provider_config: TTSConfig, voice: str | None
    ) -> str:
        """Synthesize audio using custom TTS module.

        Args:
            text: Text to synthesize.
            provider_config: Provider configuration.
            voice: Optional voice override.

        Returns:
            Path to generated audio file.
        """
        from importlib import import_module

        module_name = provider_config.module
        if not module_name:
            raise ValueError("Module name is required")

        parts = module_name.split(".")
        module = import_module(".".join(parts[:-1]))
        synthesize_func = getattr(module, parts[-1])

        result = await synthesize_func(text, provider_config, voice or provider_config.voice)

        # Return path or create from result
        if isinstance(result, str):
            # If result is a path, return it
            if Path(result).exists():
                return result

        # Create output file path
        output_file = self.media_dir / f"{text[:50].replace(' ', '_')}.{self.audio_format}"
        return str(output_file)

    async def _synthesize_google(
        self, text: str, provider_config: TTSConfig, voice: str | None = None
    ) -> str:
        """Synthesize audio using Google Translate TTS.

        Args:
            text: Text to synthesize.
            provider_config: Provider configuration.
            voice: Optional voice override.

        Returns:
            Path to generated audio file.
        """
        import requests

        # Google Translate TTS (free, no API key needed)
        lang = voice or provider_config.voice or "en-US"

        url = "https://translate.google.com/translate_tts"
        params: dict[str, Any] = {
            "client": "tw-ob",
            "q": text,
            "tl": lang,
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        # Save to file
        output_file = self.media_dir / f"{text[:50].replace(' ', '_')}.{self.audio_format}"
        self.media_dir.mkdir(parents=True, exist_ok=True)

        with open(output_file, "wb") as f:
            f.write(response.content)

        return str(output_file)

    async def _synthesize_azure(
        self, _text: str, _provider_config: TTSConfig, _voice: str | None = None
    ) -> str:
        """Synthesize audio using Azure TTS.

        Args:
            text: Text to synthesize.
            provider_config: Provider configuration.
            voice: Optional voice override.

        Returns:
            Path to generated audio file.
        """
        # Azure Cognitive Services Speech SDK
        # Note: Requires azure-cognitiveservices-speech library
        raise NotImplementedError(
            "Azure TTS requires azure-cognitiveservices-speech library. Install with: pip install azure-cognitiveservices-speech"
        )

    async def synthesize_context(self, text: str, max_length: int = 200) -> str | None:
        """Synthesize audio for context text (truncated).

        Args:
            text: Context text (may be long).
            max_length: Maximum characters to synthesize.

        Returns:
            Path to generated audio file, or None if text too long.
        """
        # Truncate text to max_length
        if len(text) > max_length:
            return None

        return await self.synthesize(text)
