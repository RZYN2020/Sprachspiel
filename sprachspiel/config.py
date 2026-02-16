"""Configuration management for Sprachspiel."""

from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field

# Default configuration paths
CONFIG_DIR = Path.home() / ".config" / "sprachspiel"
DEFAULT_CONFIG_PATH = CONFIG_DIR / "config.yaml"
QUEUE_DIR = CONFIG_DIR / "queue"


# ==================== Configuration Models ====================


class AnkiConnectConfig(BaseModel):
    """AnkiConnect connection configuration."""

    model_config = ConfigDict(frozen=True)

    host: str = "localhost"
    port: int = 8765


class AnkiFileConfig(BaseModel):
    """Anki file export configuration."""

    model_config = ConfigDict(frozen=True)

    output_dir: str = "./output"
    deck_name: str = "Sprachspiel"


class AnkiFieldMapping(BaseModel):
    """Anki card field mapping configuration."""

    model_config = ConfigDict(frozen=True, extra="allow")

    front: str = "${word}"
    back: str = "${translation}\n\n<b>Definition:</b> ${definition}\n\n<b>Example:</b> ${example}"
    audio: str = "[sound:${audio_file}.mp3]"
    tags: str = "${source_type} ${source_name}"


class AnkiConfig(BaseModel):
    """Anki integration configuration."""

    model_config = ConfigDict(frozen=True)

    mode: Literal["connect", "file", "both"] = "both"
    connect: AnkiConnectConfig = Field(default_factory=AnkiConnectConfig)
    file: AnkiFileConfig = Field(default_factory=AnkiFileConfig)
    field_mapping: AnkiFieldMapping = Field(default_factory=AnkiFieldMapping)


class CardGenerationRealTimeConfig(BaseModel):
    """Real-time card generation configuration."""

    model_config = ConfigDict(frozen=True)

    auto_push: bool = True


class CardGenerationQueueConfig(BaseModel):
    """Queue-based card generation configuration."""

    model_config = ConfigDict(frozen=True)

    auto_process: bool = False
    batch_size: int = 10
    storage_dir: str | None = None
    auto_save: bool = True


class CardGenerationConfig(BaseModel):
    """Card generation configuration."""

    model_config = ConfigDict(frozen=True)

    mode: Literal["real-time", "queue"] = "queue"
    real_time: CardGenerationRealTimeConfig = Field(default_factory=CardGenerationRealTimeConfig)
    queue: CardGenerationQueueConfig = Field(default_factory=CardGenerationQueueConfig)


class AIFunctionConfig(BaseModel):
    """AI function configuration."""

    model_config = ConfigDict(frozen=True)

    prompt: str


class AIConfig(BaseModel):
    """AI service configuration."""

    model_config = ConfigDict(frozen=True)

    provider: str = "openai"
    api_key: str = ""
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4o-mini"
    functions: dict[str, AIFunctionConfig] = Field(default_factory=dict)


class MediaConfig(BaseModel):
    """Media handling configuration."""

    model_config = ConfigDict(frozen=True)

    organization: Literal["flat", "hierarchical"] = "hierarchical"
    storage_dir: str = "./media"
    screenshot_format: str = "png"
    audio_format: str = "mp3"


class DictionaryConfig(BaseModel):
    """Dictionary service configuration."""

    model_config = ConfigDict(frozen=True, extra="allow")

    name: str
    module: str | None = None
    enabled: bool = True
    api_key: str | None = None
    base_url: str | None = None
    options: dict[str, Any] = Field(default_factory=dict)


class TTSConfig(BaseModel):
    """TTS service configuration."""

    model_config = ConfigDict(frozen=True, extra="allow")

    name: str
    module: str | None = None
    enabled: bool = True
    api_key: str | None = None
    base_url: str | None = None
    voice: str | None = None
    options: dict[str, Any] = Field(default_factory=dict)


class SourceConfig(BaseModel):
    """Data source configuration."""

    model_config = ConfigDict(frozen=True)

    name: str
    type: Literal["subtitle", "ebook", "text", "custom"]
    path: str
    options: dict[str, Any] = Field(default_factory=dict)


class SprachspielConfig(BaseModel):
    """Root configuration model for Sprachspiel."""

    model_config = ConfigDict(frozen=True)

    anki: AnkiConfig = Field(default_factory=AnkiConfig)
    card_generation: CardGenerationConfig = Field(default_factory=CardGenerationConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    media: MediaConfig = Field(default_factory=MediaConfig)
    dictionaries: list[DictionaryConfig] = Field(default_factory=list)
    tts: list[TTSConfig] = Field(default_factory=list)
    sources: list[SourceConfig] = Field(default_factory=list)


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""

    def __init__(self, message: str, errors: list[str] | None = None):
        super().__init__(message)
        self.errors = errors or []


class Config:
    """Configuration manager for Sprachspiel.

    This class wraps the strongly-typed SprachspielConfig model and provides
    backward-compatible access methods.
    """

    def __init__(self, config_path: Path | dict[str, Any] | None = None):
        """Initialize configuration manager.

        Args:
            config_path: Path to configuration file, or a dictionary with config values.
                        If None, uses default path.
        """
        self.config_path: Path = DEFAULT_CONFIG_PATH
        self._model: SprachspielConfig

        if isinstance(config_path, dict):
            # Dictionary provided - use as config directly
            try:
                self._model = SprachspielConfig.model_validate(config_path)
            except Exception as e:
                raise ConfigValidationError(f"Invalid configuration: {e}") from e
        elif config_path is not None:
            # Path provided
            self.config_path = Path(config_path)
            self._model = self._load_config()
        else:
            # Use default path
            self._model = self._load_config()

    def _load_config(self) -> SprachspielConfig:
        """Load configuration from YAML file.

        Returns:
            Validated configuration model.
        """
        if not self.config_path.exists():
            return SprachspielConfig()

        try:
            with open(self.config_path, encoding="utf-8") as f:
                raw_config = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ConfigValidationError(f"Failed to parse config file: {e}") from e

        try:
            return SprachspielConfig.model_validate(raw_config)
        except Exception as e:
            raise ConfigValidationError(f"Invalid configuration: {e}") from e

    def _get_default_config(self) -> dict[str, Any]:
        """Get default configuration.

        Returns:
            Default configuration dictionary.
        """
        return {
            "anki": {
                "mode": "both",
                "connect": {"host": "localhost", "port": 8765},
                "file": {"output_dir": "./output", "deck_name": "Sprachspiel"},
                "field_mapping": {
                    "front": "${word}",
                    "back": "${translation}\n\n<b>Definition:</b> ${definition}\n\n<b>Example:</b> ${example}",
                    "audio": "[sound:${audio_file}.mp3]",
                    "tags": "${source_type} ${source_name}",
                },
            },
            "card_generation": {
                "mode": "queue",
                "real_time": {"auto_push": True},
                "queue": {"auto_process": False, "batch_size": 10},
            },
            "dictionaries": [],
            "tts": [],
            "ai": {
                "provider": "openai",
                "api_key": "",
                "base_url": "https://api.openai.com/v1",
                "model": "gpt-4o-mini",
                "functions": {
                    "translate": {
                        "prompt": "Translate '${word}' to Chinese. Return only the translation."
                    },
                    "example": {
                        "prompt": "Generate a natural English sentence using '${word}'. The word should appear in context. Return only the sentence.",
                    },
                },
            },
            "sources": [],
            "media": {
                "organization": "hierarchical",
                "storage_dir": "./media",
                "screenshot_format": "png",
                "audio_format": "mp3",
            },
        }

    def _validate(self) -> None:
        """Validate configuration.

        Raises:
            ConfigValidationError: If configuration is invalid.
        """
        errors: list[str] = []

        # Validate Anki settings
        self._validate_anki_settings(errors)

        # Validate card generation settings
        self._validate_card_generation_settings(errors)

        # Validate media settings
        self._validate_media_settings(errors)

        if errors:
            raise ConfigValidationError("Configuration validation failed", errors)

    def _validate_anki_settings(self, errors: list[str]) -> None:
        """Validate Anki connection settings."""
        # Use strong-typed model for validation
        mode = self._model.anki.mode

        # mode is now validated by Pydantic Literal, but we keep this for custom error messages
        if mode not in ["connect", "file", "both"]:
            errors.append(f"Invalid anki mode: {mode}. Must be 'connect', 'file', or 'both'")

        if mode in ["connect", "both"]:
            connect_config = self._model.anki.connect
            if not isinstance(connect_config.host, str):
                errors.append("anki.connect.host must be a string")
            if not isinstance(connect_config.port, int):
                errors.append("anki.connect.port must be an integer")

        if mode in ["file", "both"]:
            file_config = self._model.anki.file
            if not isinstance(file_config.output_dir, str):
                errors.append("anki.file.output_dir must be a string")
            if not isinstance(file_config.deck_name, str):
                errors.append("anki.file.deck_name must be a string")

    def _validate_card_generation_settings(self, errors: list[str]) -> None:
        """Validate card generation settings."""
        mode = self._model.card_generation.mode

        if mode not in ["real-time", "queue"]:
            errors.append(f"Invalid card generation mode: {mode}. Must be 'real-time' or 'queue'")

    def _validate_media_settings(self, errors: list[str]) -> None:
        """Validate media settings."""
        organization = self._model.media.organization

        if organization not in ["flat", "hierarchical"]:
            errors.append(
                f"Invalid media organization: {organization}. Must be 'flat' or 'hierarchical'"
            )

    def reload(self) -> None:
        """Reload configuration from file."""
        self._model = self._load_config()

    def save(self) -> None:
        """Save configuration to file."""
        # Ensure config directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.dump(self._model.model_dump(), f, default_flow_style=False, allow_unicode=True)

    def ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        # Create config directory
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        # Create queue directory
        QUEUE_DIR.mkdir(parents=True, exist_ok=True)

        # Create media directory
        media_dir = Path(self.media.storage_dir)
        media_dir.mkdir(parents=True, exist_ok=True)

        # Create output directory for file export
        if self.anki.mode in ["file", "both"]:
            output_dir = Path(self.anki.file.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

    # ==================== Strongly-typed property accessors ====================

    @property
    def model(self) -> SprachspielConfig:
        """Access the strongly-typed configuration model."""
        return self._model

    @property
    def anki(self) -> AnkiConfig:
        """Access Anki configuration."""
        return self._model.anki

    @property
    def card_generation(self) -> CardGenerationConfig:
        """Access card generation configuration."""
        return self._model.card_generation

    @property
    def ai(self) -> AIConfig:
        """Access AI configuration."""
        return self._model.ai

    @property
    def media(self) -> MediaConfig:
        """Access media configuration."""
        return self._model.media

    @property
    def dictionaries(self) -> list[DictionaryConfig]:
        """Access dictionary configurations."""
        return self._model.dictionaries

    @property
    def tts(self) -> list[TTSConfig]:
        """Access TTS configurations."""
        return self._model.tts

    @property
    def sources(self) -> list[SourceConfig]:
        """Access source configurations."""
        return self._model.sources
