"""Configuration management for Sprachspiel."""

from pathlib import Path
from typing import Any

import yaml

# Default configuration paths
CONFIG_DIR = Path.home() / ".config" / "sprachspiel"
DEFAULT_CONFIG_PATH = CONFIG_DIR / "config.yaml"
QUEUE_DIR = CONFIG_DIR / "queue"


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""

    def __init__(self, message: str, errors: list[str] | None = None):
        super().__init__(message)
        self.errors = errors or []


class Config:
    """Configuration manager for Sprachspiel."""

    _config: dict[str, Any]

    def __init__(self, config_path: Path | dict[str, Any] | None = None):
        """Initialize configuration manager.

        Args:
            config_path: Path to configuration file, or a dictionary with config values.
                        If None, uses default path.
        """
        if isinstance(config_path, dict):
            # Dictionary provided - use as config directly
            self.config_path = DEFAULT_CONFIG_PATH
            self._config = config_path
            # Validate the dictionary config
            self._validate()
        elif config_path is not None:
            # Path provided
            self.config_path = Path(config_path)
            self._config = {}
            self._load_config()
        else:
            # Use default path
            self.config_path = DEFAULT_CONFIG_PATH
            self._config = {}
            self._load_config()

    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            self._config = self._get_default_config()
            return

        try:
            with open(self.config_path, encoding="utf-8") as f:
                self._config = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ConfigValidationError(f"Failed to parse config file: {e}") from e

        # Validate loaded configuration
        self._validate()

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
                    "translate": {"prompt": "Translate '${word}' to Chinese. Return only the translation."},
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
        anki_config = self._config.get("anki", {})
        mode = anki_config.get("mode")

        if mode not in ["connect", "file", "both"]:
            errors.append(f"Invalid anki mode: {mode}. Must be 'connect', 'file', or 'both'")

        if mode in ["connect", "both"]:
            connect_config = anki_config.get("connect", {})
            if not isinstance(connect_config.get("host"), str):
                errors.append("anki.connect.host must be a string")
            if not isinstance(connect_config.get("port"), (int, str)):
                errors.append("anki.connect.port must be an integer or string")

        if mode in ["file", "both"]:
            file_config = anki_config.get("file", {})
            if not isinstance(file_config.get("output_dir"), str):
                errors.append("anki.file.output_dir must be a string")
            if not isinstance(file_config.get("deck_name"), str):
                errors.append("anki.file.deck_name must be a string")

    def _validate_card_generation_settings(self, errors: list[str]) -> None:
        """Validate card generation settings."""
        card_config = self._config.get("card_generation", {})
        mode = card_config.get("mode")

        if mode not in ["real-time", "queue"]:
            errors.append(f"Invalid card generation mode: {mode}. Must be 'real-time' or 'queue'")

    def _validate_media_settings(self, errors: list[str]) -> None:
        """Validate media settings."""
        media_config = self._config.get("media", {})
        organization = media_config.get("organization")

        if organization not in ["flat", "hierarchical"]:
            errors.append(f"Invalid media organization: {organization}. Must be 'flat' or 'hierarchical'")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.

        Args:
            key: Configuration key in dot notation (e.g., "anki.mode")
            default: Default value if key not found

        Returns:
            Configuration value or default.
        """
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)  # type: ignore[assignment]
            else:
                return default

        return value if value is not None else default

    def set(self, key: str, value: Any) -> None:
        """Set configuration value.

        Args:
            key: Configuration key in dot notation (e.g., "anki.mode")
            value: Value to set
        """
        keys = key.split(".")
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def reload(self) -> None:
        """Reload configuration from file."""
        self._load_config()

    def save(self) -> None:
        """Save configuration to file."""
        # Ensure config directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True)

    def ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        # Create config directory
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        # Create queue directory
        QUEUE_DIR.mkdir(parents=True, exist_ok=True)

        # Create media directory
        media_dir = Path(self.get("media.storage_dir", "./media"))
        media_dir.mkdir(parents=True, exist_ok=True)

        # Create output directory for file export
        if self.get("anki.mode") in ["file", "both"]:
            output_dir = Path(self.get("anki.file.output_dir", "./output"))
            output_dir.mkdir(parents=True, exist_ok=True)
