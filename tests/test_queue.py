"""Tests for card queue management."""

from collections.abc import Generator
from pathlib import Path

import pytest

from sprachspiel.config import QUEUE_DIR, Config
from sprachspiel.core.card import CardData, CardMetadata
from sprachspiel.core.queue import CardQueue


@pytest.fixture(autouse=True)
def cleanup_queue() -> Generator[None]:
    """Clean up queue file before each test."""
    # Remove existing queue file
    queue_file = QUEUE_DIR / "queue.json"
    if queue_file.exists():
        queue_file.unlink()
    yield
    # Cleanup after test
    if queue_file.exists():
        queue_file.unlink()


@pytest.fixture
def mock_config() -> Config:
    """Create mock configuration for testing."""
    return Config()


@pytest.fixture
def mock_queue(mock_config: Config) -> CardQueue:
    """Create mock queue for testing."""
    return CardQueue(mock_config)


@pytest.fixture
def sample_card() -> CardData:
    """Create sample card data for testing."""
    return CardData(
        word="example",
        context="This is an example sentence.",
        metadata=CardMetadata(source_type="test", source_name="test.txt"),
    )


class TestCardQueue:
    """Unit tests for CardQueue."""

    def test_init_creates_empty_queue(self, mock_queue: CardQueue) -> None:
        """Test queue initialization creates empty queue."""
        assert mock_queue.size() == 0
        assert mock_queue.is_empty()

    def test_add_card(self, mock_queue: CardQueue, sample_card: CardData) -> None:
        """Test adding card to queue."""
        mock_queue.add(sample_card)

        assert mock_queue.size() == 1
        assert not mock_queue.is_empty()

    def test_add_multiple_cards(
        self, mock_queue: CardQueue, sample_card: CardData
    ) -> None:
        """Test adding multiple cards to queue."""
        card1 = CardData(
            word="first",
            context="First context.",
            metadata=CardMetadata(source_type="test", source_name="test.txt"),
        )
        card2 = CardData(
            word="second",
            context="Second context.",
            metadata=CardMetadata(source_type="test", source_name="test.txt"),
        )

        mock_queue.add(card1)
        mock_queue.add(card2)

        assert mock_queue.size() == 2

    def test_get_card_by_id(
        self, mock_queue: CardQueue, sample_card: CardData
    ) -> None:
        """Test getting card by ID."""
        mock_queue.add(sample_card)

        retrieved = mock_queue.get(sample_card.id)

        assert retrieved.word == sample_card.word
        assert retrieved.context == sample_card.context

    def test_get_nonexistent_card_raises_key_error(
        self, mock_queue: CardQueue
    ) -> None:
        """Test getting non-existent card raises KeyError."""
        with pytest.raises(KeyError):
            mock_queue.get("nonexistent-id")

    def test_remove_card(
        self, mock_queue: CardQueue, sample_card: CardData
    ) -> None:
        """Test removing card from queue."""
        mock_queue.add(sample_card)

        result = mock_queue.remove(sample_card.id)

        assert result is True
        assert mock_queue.size() == 0

    def test_remove_nonexistent_card_returns_false(
        self, mock_queue: CardQueue
    ) -> None:
        """Test removing non-existent card returns False."""
        result = mock_queue.remove("nonexistent-id")

        assert result is False

    def test_remove_batch(self, mock_queue: CardQueue) -> None:
        """Test removing batch of cards from queue."""
        cards: list[CardData] = []
        card_ids: list[str] = []

        for i in range(5):
            card = CardData(
                word=f"word{i}",
                context=f"Context {i}.",
                metadata=CardMetadata(source_type="test", source_name="test.txt"),
            )
            cards.append(card)
            card_ids.append(card.id)
            mock_queue.add(card)

        result = mock_queue.remove_batch(card_ids[:3])

        assert result == 3
        assert mock_queue.size() == 2

    def test_get_all_cards(
        self, mock_queue: CardQueue, sample_card: CardData
    ) -> None:
        """Test getting all cards from queue."""
        mock_queue.add(sample_card)

        all_cards = mock_queue.get_all()

        assert len(all_cards) == 1
        assert all_cards[0].word == sample_card.word

    def test_clear_queue(self, mock_queue: CardQueue, sample_card: CardData) -> None:
        """Test clearing all cards from queue."""
        mock_queue.add(sample_card)

        mock_queue.clear()

        assert mock_queue.size() == 0
        assert mock_queue.is_empty()

    def test_get_batch(self, mock_queue: CardQueue) -> None:
        """Test getting batch of cards."""
        cards: list[CardData] = []
        for i in range(10):
            card = CardData(
                word=f"word{i}",
                context=f"Context {i}.",
                metadata=CardMetadata(source_type="test", source_name="test.txt"),
            )
            cards.append(card)
            mock_queue.add(card)

        batch = mock_queue.get_batch(5)

        assert len(batch) == 5
        assert batch[0].word == "word0"

    def test_get_batch_larger_than_queue_size(
        self, mock_queue: CardQueue
    ) -> None:
        """Test getting batch larger than queue returns all cards."""
        for i in range(3):
            card = CardData(
                word=f"word{i}",
                context=f"Context {i}.",
                metadata=CardMetadata(source_type="test", source_name="test.txt"),
            )
            mock_queue.add(card)

        batch = mock_queue.get_batch(10)

        assert len(batch) == 3

    def test_queue_persistence(
        self, mock_config: Config, sample_card: CardData
    ) -> None:
        """Test queue persistence to file."""
        queue1 = CardQueue(mock_config)
        queue1.add(sample_card)

        # Create new queue instance (should load from file)
        queue2 = CardQueue(mock_config)

        assert queue2.size() == 1
        assert queue2.get(sample_card.id).word == sample_card.word

    def test_queue_save_creates_directory(self, mock_config: Config) -> None:
        """Test that queue save creates directory if it doesn't exist."""
        # Remove existing queue file
        queue_file = QUEUE_DIR / "queue.json"
        if queue_file.exists():
            queue_file.unlink()

        card = CardData(
            word="test",
            context="Test context.",
            metadata=CardMetadata(source_type="test", source_name="test.txt"),
        )

        queue = CardQueue(mock_config)
        queue.add(card)

        assert queue_file.exists()
        assert QUEUE_DIR.exists()


class TestCardQueueErrorHandling:
    """Unit tests for CardQueue error handling."""

    def test_load_malformed_json(
        self, mock_config: Config, tmp_path: Path
    ) -> None:
        """Test loading malformed JSON raises RuntimeError."""
        # Create malformed queue file
        queue_dir = QUEUE_DIR
        queue_dir.mkdir(parents=True, exist_ok=True)
        queue_file = queue_dir / "queue.json"

        with open(queue_file, "w", encoding="utf-8") as f:
            f.write("invalid json content")

        with pytest.raises(RuntimeError):
            CardQueue(mock_config)

        # Cleanup
        if queue_file.exists():
            queue_file.unlink()

    def test_save_with_unicode(self, mock_config: Config) -> None:
        """Test saving queue with unicode content."""
        card = CardData(
            word="测试",
            context="This is a test context with 你好.",
            translation="Test translation with 你好.",
            metadata=CardMetadata(source_type="test", source_name="test.txt"),
        )

        queue = CardQueue(mock_config)
        queue.add(card)

        # Create new queue to verify persistence
        queue2 = CardQueue(mock_config)
        retrieved = queue2.get(card.id)

        assert retrieved.word == "测试"
        assert "你好" in retrieved.context
