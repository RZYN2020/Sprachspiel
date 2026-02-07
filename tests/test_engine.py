"""Tests for card engine."""


from sprachspiel.config import Config
from sprachspiel.core.card import CardData, CardMetadata
from sprachspiel.core.engine import CardEngine
from sprachspiel.core.queue import CardQueue


def test_engine_initialization():
    """Test engine initialization."""
    config = Config()
    engine = CardEngine(config)

    assert engine is not None


def test_queue_initialization():
    """Test queue initialization."""
    config = Config()
    queue = CardQueue(config)

    assert queue.size() == 0
    assert queue.is_empty()


def test_queue_add_and_get():
    """Test adding and getting cards from queue."""
    config = Config()
    queue = CardQueue(config)

    card = CardData(
        word="test",
        context="Test context.",
        metadata=CardMetadata(source_type="test", source_name="test"),
    )

    queue.add(card)

    assert queue.size() == 1
    assert not queue.is_empty()

    retrieved = queue.get(card.id)
    assert retrieved.word == "test"
