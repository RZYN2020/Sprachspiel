"""Tests for field mapper."""


import pytest

from sprachspiel.config import Config
from sprachspiel.core.card import AnkiCard, CardData, CardMetadata, Media
from sprachspiel.core.mapper import FieldMapper


@pytest.fixture
def mock_config() -> Config:
    """Create mock configuration for testing."""
    return Config()


@pytest.fixture
def mock_field_mapper(mock_config: Config) -> FieldMapper:
    """Create mock field mapper for testing."""
    return FieldMapper(mock_config)


@pytest.fixture
def sample_card() -> CardData:
    """Create sample card data for testing."""
    return CardData(
        word="quick",
        context="The quick brown fox jumps over the lazy dog.",
        translation="快速",
        definition="Moving at high speed.",
        example="The quick runner won the race.",
        metadata=CardMetadata(
            source_type="video",
            source_name="test.mp4",
            position="00:01:23",
        ),
        media=Media(
            screenshot="/media/screenshot.png",
            audio_word="/media/audio_word.mp3",
        ),
    )


class TestFieldMapper:
    """Unit tests for FieldMapper."""

    def test_init_with_config(self, mock_config: Config) -> None:
        """Test field mapper initialization with config."""
        mapper = FieldMapper(mock_config)

        assert mapper.config is mock_config
        assert isinstance(mapper.field_mapping, dict)
        assert isinstance(mapper.deck_name, str)
        assert isinstance(mapper.model_name, str)

    def test_map_card_basic(self, mock_field_mapper: FieldMapper, sample_card: CardData) -> None:
        """Test mapping card to Anki card with basic data."""
        result = mock_field_mapper.map_card(sample_card)

        assert isinstance(result, AnkiCard)
        assert result.deck_name == mock_field_mapper.deck_name
        assert result.model_name == mock_field_mapper.model_name
        assert isinstance(result.fields, dict)
        assert isinstance(result.tags, list)
        assert isinstance(result.audio_files, list)
        assert isinstance(result.image_files, list)

    def test_map_card_with_media_files(
        self, mock_field_mapper: FieldMapper, sample_card: CardData
    ) -> None:
        """Test that media files are extracted correctly."""
        result = mock_field_mapper.map_card(sample_card)

        assert len(result.audio_files) >= 1
        assert len(result.image_files) >= 1
        assert any("audio" in f for f in result.audio_files)
        assert any("screenshot" in f for f in result.image_files)

    def test_map_card_without_media(
        self, mock_field_mapper: FieldMapper
    ) -> None:
        """Test mapping card without media files."""
        card = CardData(
            word="test",
            context="Test context.",
            metadata=CardMetadata(source_type="text", source_name="test.txt"),
        )

        result = mock_field_mapper.map_card(card)

        assert len(result.audio_files) == 0
        assert len(result.image_files) == 0

    def test_build_variable_context(self, mock_field_mapper: FieldMapper) -> None:
        """Test building variable context from card."""
        card = CardData(
            word="hello",
            context="Hello world!",
            translation="你好",
            metadata=CardMetadata(source_type="video", source_name="test.mp4"),
        )

        variables = mock_field_mapper._build_variable_context(card)

        assert variables["word"] == "hello"
        assert variables["context"] == "Hello world!"
        assert variables["translation"] == "你好"
        assert variables["source_type"] == "video"
        assert variables["source_name"] == "test.mp4"

    def test_build_variable_context_with_media(self, mock_field_mapper: FieldMapper) -> None:
        """Test building variable context with media files."""
        card = CardData(
            word="test",
            context="Test context.",
            media=Media(screenshot="/path/to/img.png"),
        )

        variables = mock_field_mapper._build_variable_context(card)

        assert variables["screenshot"] == "/path/to/img.png"

    def test_build_variable_context_with_custom_data(
        self, mock_field_mapper: FieldMapper
    ) -> None:
        """Test building variable context with custom data."""
        card = CardData(
            word="test",
            context="Test context.",
            custom_data={"custom_field": "custom_value"},
        )

        variables = mock_field_mapper._build_variable_context(card)

        assert variables["custom_field"] == "custom_value"

    def test_substitute_template_simple(self, mock_field_mapper: FieldMapper) -> None:
        """Test simple template substitution."""
        variables = {"word": "hello", "context": "world"}
        template = "${word} ${context}"

        result = mock_field_mapper._substitute_template(template, variables)

        assert result == "hello world"

    def test_substitute_template_nested(self, mock_field_mapper: FieldMapper) -> None:
        """Test nested template substitution."""
        variables = {
            "media": {"screenshot": "img.png"},
            "word": "test",
        }
        template = "Word: ${word}, Image: ${media.screenshot}"

        result = mock_field_mapper._substitute_template(template, variables)

        assert result == "Word: test, Image: img.png"

    def test_substitute_template_missing_variable(
        self, mock_field_mapper: FieldMapper
    ) -> None:
        """Test test substitution with missing variable."""
        variables = {"word": "hello"}
        template = "${word} ${missing}"

        result = mock_field_mapper._substitute_template(template, variables)

        assert result == "hello "

    def test_substitute_template_empty_string(
        self, mock_field_mapper: FieldMapper
    ) -> None:
        """Test substitution with empty string (returns template as-is)."""
        variables = {"word": "hello"}
        template = ""

        result = mock_field_mapper._substitute_template(template, variables)

        assert result == ""

    def test_build_tags_default(self, mock_field_mapper: FieldMapper) -> None:
        """Test building default tags."""
        card = CardData(
            word="test",
            context="Test context.",
            metadata=CardMetadata(source_type="video", source_name="test.mp4"),
        )

        tags = mock_field_mapper._build_tags(card)

        assert "video" in tags

    def test_build_tagsariable_variable(
        self, mock_field_mapper: FieldMapper
    ) -> None:
        """Test building tags from variable."""
        card = CardData(
            word="test",
            context="Test context.",
            metadata=CardMetadata(source_type="video", source_name="test.mp4"),
        )

        tags = mock_field_mapper._build_tags(card)

        assert "video" in tags
