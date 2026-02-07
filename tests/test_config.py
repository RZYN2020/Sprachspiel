"""Tests for configuration management."""

import tempfile
from pathlib import Path

import pytest

from sprachspiel.config import Config, ConfigValidationError


def test_default_config_creation():
    """Test default config creation."""
    config = Config()

    assert config.get("anki.mode") == "both"
    assert config.get("card_generation.mode") == "queue"


def test_config_get():
    """Test getting config values."""
    config = Config()

    assert config.get("anki.mode") == "both"
    assert config.get("nonexistent.key", "default") == "default"


def test_config_set():
    """Test setting config values."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("""anki:
  mode: connect
  connect:
    host: localhost
    port: 8765
  file:
    output_dir: ./output
    deck_name: Sprachspiel
card_generation:
  mode: queue
media:
  organization: hierarchical
""")

    config = Config(Path(f.name))
    assert config.get("anki.mode") == "connect"

    config.set("anki.mode", "file")
    assert config.get("anki.mode") == "file"

    # Cleanup
    Path(f.name).unlink()


def test_config_validation_valid_mode():
    """Test config validation with valid Anki mode."""
    config = Config()

    # Valid modes
    for mode in ["connect", "file", "both"]:
        config.set("anki.mode", mode)
        assert config.get("anki.mode") == mode


def test_config_validation_invalid_mode():
    """Test config validation with invalid Anki mode."""
    config = Config()

    config.set("anki.mode", "invalid")

    with pytest.raises(ConfigValidationError):
        config._validate()
