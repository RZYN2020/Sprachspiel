"""Tests for configuration management."""

import tempfile
from pathlib import Path

import pytest

from sprachspiel.config import (
    AIConfig,
    AnkiConfig,
    AnkiConnectConfig,
    AnkiFieldMapping,
    AnkiFileConfig,
    CardGenerationConfig,
    Config,
    ConfigValidationError,
    MediaConfig,
    SprachspielConfig,
)


# ==================== Strong-typed Configuration Tests ====================


def test_sprachspiel_config_defaults():
    """Test default configuration model creation."""
    config = SprachspielConfig()

    assert config.anki.mode == "both"
    assert config.card_generation.mode == "queue"
    assert config.ai.provider == "openai"
    assert config.media.organization == "hierarchical"


def test_anki_config_strong_typed():
    """Test strong-typed Anki configuration."""
    config = AnkiConfig(
        mode="connect",
        connect=AnkiConnectConfig(host="192.168.1.100", port=8080),
        field_mapping=AnkiFieldMapping(front="${word}", back="${translation}"),
    )

    assert config.mode == "connect"
    assert config.connect.host == "192.168.1.100"
    assert config.connect.port == 8080
    assert config.field_mapping.front == "${word}"


def test_config_validation_invalid_mode():
    """Test validation rejects invalid mode values."""
    with pytest.raises((ValueError, Exception), match="Input should be|Invalid literal"):
        AnkiConfig(mode="invalid_mode")  # type: ignore[arg-type]


def test_config_immutable():
    """Test configuration is immutable (frozen)."""
    config = SprachspielConfig()

    with pytest.raises(ValueError, match="frozen"):
        config.anki.mode = "connect"  # type: ignore[misc]


# ==================== Backward Compatibility Tests ====================


def test_config_strong_typed_access():
    """Test strong-typed property access."""
    config = Config()

    # Direct property access
    assert config.anki.mode == "both"
    assert config.anki.connect.host == "localhost"
    assert config.card_generation.mode == "queue"
    assert config.ai.provider == "openai"


def test_config_from_dict():
    """Test creating config from dictionary."""
    config_dict = {
        "anki": {
            "mode": "file",
            "file": {"output_dir": "./my_output", "deck_name": "My Deck"},
        },
        "ai": {"provider": "anthropic", "api_key": "test-key"},
    }

    config = Config(config_dict)

    assert config.anki.mode == "file"
    assert config.anki.file.output_dir == "./my_output"
    # Provider should be "anthropic" as specified in config_dict
    assert config.ai.provider == "anthropic"
    assert config.ai.api_key == "test-key"


def test_config_model_dump():
    """Test dumping config to dictionary."""
    config = Config()
    config_dict = config.model.model_dump()

    assert isinstance(config_dict, dict)
    assert config_dict["anki"]["mode"] == "both"


# ==================== Save/Load Integration Tests ====================


def test_config_save_and_load():
    """Test saving and loading configuration."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        temp_path = Path(f.name)

    try:
        # Create config with custom values via dict
        config_dict = {
            "anki": {"mode": "file", "file": {"deck_name": "Test Deck"}},
            "ai": {"provider": "anthropic", "api_key": "test-key"},
        }
        config = Config(config_dict)
        config.config_path = temp_path
        config.save()

        # Load it back
        config2 = Config(temp_path)

        assert config2.anki.mode == "file"
        assert config2.anki.file.deck_name == "Test Deck"
        assert config2.ai.provider == "anthropic"

    finally:
        temp_path.unlink(missing_ok=True)
