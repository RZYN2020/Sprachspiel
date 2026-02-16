"""Integration tests for queue persistence.

These tests verify that the CardQueue correctly saves and loads
cards from disk.
"""

import json
import tempfile
from datetime import UTC, datetime
from pathlib import Path

import pytest

from sprachspiel.config import Config
from sprachspiel.core.card import CardData, CardMetadata
from sprachspiel.core.queue import CardQueue


@pytest.fixture
def temp_queue_dir():
    """Create a temporary directory for queue files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def queue_config(temp_queue_dir: Path) -> Config:
    """Create a configuration with temporary queue directory."""
    config_dict = {
        "anki": {
            "mode": "file",
            "file": {"output_dir": "./output", "deck_name": "Test Deck"},
        },
        "card_generation": {
            "mode": "queue",
            "queue": {
                "storage_dir": str(temp_queue_dir),
                "auto_save": False,  # Disable auto-save for testing
            },
        },
        "media": {"organization": "flat"},
        "dictionaries": [],
        "ai": {"provider": "openai", "api_key": ""},
        "tts": [],
    }
    return Config(config_dict)


@pytest.fixture
def sample_cards() -> list[CardData]:
    """Create sample cards for testing."""
    return [
        CardData(
            word="Word1",
            context="Context 1",
            metadata=CardMetadata(
                source_type="test",
                source_name="test.py",
                position="1",
                created_at=datetime.now(UTC),
            ),
        ),
        CardData(
            word="Word2",
            context="Context 2",
            translation="Translation 2",
            metadata=CardMetadata(
                source_type="test",
                source_name="test.py",
                position="2",
                created_at=datetime.now(UTC),
            ),
        ),
    ]


class TestQueuePersistence:
    """Test queue save/load functionality."""

    def test_save_and_load(
        self,
        queue_config: Config,
        sample_cards: list[CardData],
        temp_queue_dir: Path,
    ) -> None:
        """Test saving and loading cards from queue."""
        # Create queue and clear any existing data
        queue = CardQueue(queue_config)
        queue.clear()

        # Add cards
        for card in sample_cards:
            queue.add(card)

        assert queue.size() == 2

        # Save the queue
        queue.save()

        # Verify file exists
        queue_file = temp_queue_dir / "queue.json"
        assert queue_file.exists()

        # Create new queue instance (auto-loads saved data)
        new_queue = CardQueue(queue_config)
        assert new_queue.size() == 2

        # Verify cards are preserved
        cards = new_queue.get_batch(10)
        words = [c.word for c in cards]
        assert "Word1" in words
        assert "Word2" in words

    def test_save_creates_directory_if_missing(
        self,
        queue_config: Config,
        temp_queue_dir: Path,
    ) -> None:
        """Test that save creates the storage directory if it doesn't exist."""
        # Create queue and clear any existing data first
        queue = CardQueue(queue_config)
        queue.clear()

        # Remove the temp directory
        import shutil

        shutil.rmtree(temp_queue_dir)
        assert not temp_queue_dir.exists()

        # Add a card
        queue.add(
            CardData(
                word="Test",
                context="Test context",
                metadata=CardMetadata(
                    source_type="test",
                    source_name="test",
                    created_at=datetime.now(UTC),
                ),
            )
        )

        # Save should create directory
        queue.save()
        assert temp_queue_dir.exists()

    def test_load_nonexistent_file(self, queue_config: Config) -> None:
        """Test loading when queue file doesn't exist."""
        queue = CardQueue(queue_config)

        # Should not raise an error
        queue.load()
        assert queue.is_empty()

    def test_load_corrupted_file(
        self,
        queue_config: Config,
        temp_queue_dir: Path,
    ) -> None:
        """Test loading a corrupted queue file."""
        # Create corrupted file
        queue_file = temp_queue_dir / "queue.json"
        queue_file.write_text("not valid json{{{")

        queue = CardQueue(queue_config)

        # Should not raise an error, but queue should be empty
        queue.load()
        assert queue.is_empty()


class TestQueueBatchOperations:
    """Test queue batch operations with persistence."""

    def test_get_batch_persists_remaining(
        self,
        queue_config: Config,
        sample_cards: list[CardData],
    ) -> None:
        """Test that getting a batch leaves remaining cards in queue."""
        queue = CardQueue(queue_config)
        queue.clear()

        # Add more cards than batch size
        for i in range(5):
            queue.add(
                CardData(
                    word=f"Word{i}",
                    context=f"Context {i}",
                    metadata=CardMetadata(
                        source_type="test",
                        source_name="test",
                        position=str(i),
                        created_at=datetime.now(UTC),
                    ),
                )
            )

        assert queue.size() == 5

        # Get batch of 2 (get_batch doesn't remove cards, it just returns them)
        batch = queue.get_batch(2)
        assert len(batch) == 2
        assert queue.size() == 5  # Queue size unchanged

        # Get another batch (same cards since we didn't remove them)
        batch2 = queue.get_batch(2)
        assert len(batch2) == 2
        assert queue.size() == 5  # Queue size still unchanged

    def test_remove_after_save_load(
        self,
        queue_config: Config,
        sample_cards: list[CardData],
        temp_queue_dir: Path,
    ) -> None:
        """Test removing cards after save and reload."""
        # Create and populate queue
        queue = CardQueue(queue_config)
        for card in sample_cards:
            queue.add(card)

        # Save
        queue.save()

        # Reload
        new_queue = CardQueue(queue_config)
        new_queue.load()

        # Get first card and remove it
        cards = new_queue.get_batch(10)
        assert len(cards) == 2
        card_to_remove = cards[0]

        new_queue.remove(card_to_remove.id)
        assert new_queue.size() == 1

        # Verify correct card was removed
        remaining = new_queue.get_batch(10)
        assert len(remaining) == 1
        assert remaining[0].id != card_to_remove.id


class TestQueueEdgeCases:
    """Test queue edge cases."""

    def test_add_duplicate_cards(self, queue_config: Config) -> None:
        """Test adding duplicate cards to queue."""
        queue = CardQueue(queue_config)
        queue.clear()

        card = CardData(
            word="Duplicate",
            context="Test context",
            metadata=CardMetadata(
                source_type="test",
                source_name="test",
                position="1",
                created_at=datetime.now(UTC),
            ),
        )

        queue.add(card)
        queue.add(card)  # Add same card again (same ID, will overwrite)

        # Same card ID overwrites previous, so only 1 card
        assert queue.size() == 1

    def test_get_batch_larger_than_queue(self, queue_config: Config) -> None:
        """Test getting a batch larger than queue size."""
        queue = CardQueue(queue_config)
        queue.clear()

        # Add 2 cards
        for i in range(2):
            queue.add(
                CardData(
                    word=f"Word{i}",
                    context=f"Context {i}",
                    metadata=CardMetadata(
                        source_type="test",
                        source_name="test",
                        position=str(i),
                        created_at=datetime.now(UTC),
                    ),
                )
            )

        # Try to get batch of 10
        batch = queue.get_batch(10)

        assert len(batch) == 2  # Returns all available cards
        # Note: queue still has the cards since get_batch doesn't remove them
        assert queue.size() == 2

    def test_clear_queue(self, queue_config: Config) -> None:
        """Test clearing the queue."""
        queue = CardQueue(queue_config)
        queue.clear()

        # Add cards
        for i in range(3):
            queue.add(
                CardData(
                    word=f"Word{i}",
                    context=f"Context {i}",
                    metadata=CardMetadata(
                        source_type="test",
                        source_name="test",
                        position=str(i),
                        created_at=datetime.now(UTC),
                    ),
                )
            )

        assert queue.size() == 3

        # Clear queue
        queue.clear()

        assert queue.is_empty()
        assert queue.size() == 0


if __name__ == "__main__":
    import sys

    import subprocess

    result = subprocess.run(
        ["python", "-m", "pytest", __file__, "-v"],
        capture_output=False,
    )
    sys.exit(result.returncode)
