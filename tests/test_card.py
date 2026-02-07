"""Tests for card data model."""


from sprachspiel.core.card import AnkiCard, CardData, CardMetadata


def test_card_data_creation():
    """Test basic CardData creation."""
    card = CardData(
        word="quick",
        context="The quick brown fox jumps over the lazy dog.",
        metadata=CardMetadata(source_type="video", source_name="test.mp4"),
    )

    assert card.word == "quick"
    assert card.metadata.source_type == "video"


def test_card_data_to_dict():
    """Test CardData serialization to dict."""
    card = CardData(
        word="example",
        context="This is an example sentence.",
        translation="示例",
        definition="A sample sentence.",
        metadata=CardMetadata(source_type="text", source_name="test.txt"),
    )

    data = card.to_dict()

    assert data["word"] == "example"
    assert data["translation"] == "示例"
    assert "metadata" in data


def test_card_data_from_dict():
    """Test CardData deserialization from dict."""
    data = {
        "id": "test-id",
        "word": "test",
        "context": "Test context.",
        "translation": "test translation",
        "metadata": {
            "source_type": "video",
            "source_name": "test.mp4",
            "created_at": "2024-01-01T00:00:00",
        },
    }

    card = CardData.from_dict(data)

    assert card.word == "test"
    assert card.translation == "test translation"
    assert card.metadata.source_type == "video"


def test_anki_card_creation():
    """Test AnkiCard creation."""
    card = AnkiCard(
        deck_name="Test Deck",
        model_name="Basic",
        fields={"Front": "test", "Back": "test back"},
        tags=["tag1", "tag2"],
        audio_files=["test.mp3"],
        image_files=["test.png"],
    )

    assert card.deck_name == "Test Deck"
    assert len(card.tags) == 2
    assert len(card.audio_files) == 1
    assert len(card.image_files) == 1
