"""Integration tests for the CardEngine.

These tests verify that the CardEngine correctly orchestrates
enhancement services and generates Anki cards.
"""

import asyncio
import sys
from datetime import UTC, datetime

import pytest

from sprachspiel.config import Config
from sprachspiel.core.card import CardData, CardMetadata
from sprachspiel.core.engine import CardEngine


@pytest.fixture
def minimal_config() -> Config:
    """Create a minimal configuration for testing."""
    config_dict = {
        "anki": {
            "mode": "file",
            "file": {"output_dir": "./output", "deck_name": "Test Deck"},
            "field_mapping": {
                "front": "${word}",
                "back": "${translation}",
            },
        },
        "card_generation": {
            "mode": "real-time",
        },
        "media": {"organization": "flat"},
        "dictionaries": [],
        "ai": {"provider": "openai", "api_key": ""},
        "tts": [],
    }
    return Config(config_dict)


@pytest.fixture
def sample_card_data() -> CardData:
    """Create sample card data for testing."""
    return CardData(
        word="TestWord",
        context="This is a test context.",
        translation="Test Translation",
        metadata=CardMetadata(
            source_type="test",
            source_name="test_engine.py",
            position="line 1",
            created_at=datetime.now(UTC),
        ),
    )


class TestCardEngine:
    """Test suite for CardEngine."""

    @pytest.mark.asyncio
    async def test_generate_card_basic(
        self,
        minimal_config: Config,
        sample_card_data: CardData,
    ) -> None:
        """Test basic card generation without enhancements."""
        engine = CardEngine(minimal_config)

        anki_card = await engine.generate_card(sample_card_data)

        assert anki_card.deck_name == "Test Deck"
        # In strong-typed config, field_mapping always has all fields (with defaults)
        # so model_name is always "CustomModel"
        assert anki_card.model_name == "CustomModel"
        assert "front" in anki_card.fields
        assert "back" in anki_card.fields
        assert anki_card.fields["front"] == "TestWord"
        assert anki_card.fields["back"] == "Test Translation"

    @pytest.mark.asyncio
    async def test_generate_card_with_custom_mapping(
        self,
        sample_card_data: CardData,
    ) -> None:
        """Test card generation with custom field mapping."""
        config_dict = {
            "anki": {
                "mode": "file",
                "file": {"output_dir": "./output", "deck_name": "Custom Deck"},
                "field_mapping": {
                    "Word": "${word}",
                    "Context": "${context}",
                    "Definition": "${translation}",
                    "FullEntry": "${word} - ${translation}",
                },
            },
            "card_generation": {
                "mode": "real-time",
            },
            "media": {"organization": "flat"},
            "dictionaries": [],
            "ai": {"provider": "openai", "api_key": ""},
            "tts": [],
        }
        config = Config(config_dict)
        engine = CardEngine(config)

        anki_card = await engine.generate_card(sample_card_data)

        assert anki_card.deck_name == "Custom Deck"
        assert anki_card.model_name == "CustomModel"
        assert anki_card.fields["Word"] == "TestWord"
        assert anki_card.fields["Context"] == "This is a test context."
        assert anki_card.fields["Definition"] == "Test Translation"
        assert anki_card.fields["FullEntry"] == "TestWord - Test Translation"

    @pytest.mark.asyncio
    async def test_generate_card_with_html_template(
        self,
        sample_card_data: CardData,
    ) -> None:
        """Test card generation with HTML template in field mapping."""
        config_dict = {
            "anki": {
                "mode": "file",
                "file": {"output_dir": "./output", "deck_name": "HTML Deck"},
                "field_mapping": {
                    "front": "<h2>${word}</h2>",
                    "back": """<div style="text-align: center;">
<h3>${word}</h3>
<p><strong>Translation:</strong> ${translation}</p>
<p><em>${context}</em></p>
</div>""",
                },
            },
            "card_generation": {
                "mode": "real-time",
            },
            "media": {"organization": "flat"},
            "dictionaries": [],
            "ai": {"provider": "openai", "api_key": ""},
            "tts": [],
        }
        config = Config(config_dict)
        engine = CardEngine(config)

        anki_card = await engine.generate_card(sample_card_data)

        assert "<h2>TestWord</h2>" in anki_card.fields["front"]
        assert "<h3>TestWord</h3>" in anki_card.fields["back"]
        assert "Test Translation" in anki_card.fields["back"]

    def test_generate_card_sync(self, minimal_config: Config) -> None:
        """Test synchronous card generation wrapper."""
        engine = CardEngine(minimal_config)

        card_data = CardData(
            word="SyncTest",
            context="Testing sync wrapper.",
            metadata=CardMetadata(
                source_type="test",
                source_name="test",
                created_at=datetime.now(UTC),
            ),
        )

        anki_card = engine.generate_card_sync(card_data)

        assert anki_card.fields["front"] == "SyncTest"


class TestCardEngineInitialization:
    """Test CardEngine initialization with different configurations."""

    def test_init_with_minimal_config(self) -> None:
        """Test engine initialization with minimal config."""
        config_dict = {
            "anki": {
                "mode": "file",
                "file": {"output_dir": "./output", "deck_name": "Test Deck"},
                "field_mapping": {},
            },
            "card_generation": {"mode": "real-time"},
            "media": {"organization": "flat"},
            "dictionaries": [],
            "ai": {"provider": "openai", "api_key": ""},
            "tts": [],
        }
        config = Config(config_dict)
        engine = CardEngine(config)

        assert engine.config == config
        assert engine.mapper is not None

    def test_init_with_connect_mode(self) -> None:
        """Test engine initialization with AnkiConnect mode."""
        config_dict = {
            "anki": {
                "mode": "connect",
                "connect": {"host": "localhost", "port": 8765},
                "field_mapping": {},
            },
            "card_generation": {"mode": "real-time"},
            "media": {"organization": "flat"},
            "dictionaries": [],
            "ai": {"provider": "openai", "api_key": ""},
            "tts": [],
        }
        config = Config(config_dict)
        engine = CardEngine(config)

        assert engine.anki_connect is not None


if __name__ == "__main__":
    # Run tests with pytest if available
    import subprocess

    result = subprocess.run(
        ["python", "-m", "pytest", __file__, "-v"],
        capture_output=False,
    )
    sys.exit(result.returncode)
