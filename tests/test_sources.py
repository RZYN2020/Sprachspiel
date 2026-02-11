"""Tests for data sources."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from sprachspiel.config import Config
from sprachspiel.core.card import CardData, CardMetadata
from sprachspiel.sources.base import BaseDataSource
from sprachspiel.sources.file_import import FileImportSource
from sprachspiel.sources.player import PlayerDataSource
from sprachspiel.sources.reader import ReaderDataSource


@pytest.fixture
def mock_config() -> Config:
    """Create mock configuration for testing."""
    return Config()


class ConcreteDataSource(BaseDataSource):
    """Concrete implementation for testing BaseDataSource."""

    def __init__(self, config: Config, source_config: dict) -> None:
        self.config = config
        self.source_config = source_config

    def get_card_data(self, word: str, context: str | None = None) -> CardData:
        return CardData(
            word=word,
            context=context or "",
            metadata=CardMetadata(source_type="test", source_name="test"),
        )

    def capture_media(self, card: CardData) -> CardData:
        return card


class TestBaseDataSource:
    """Unit tests for BaseDataSource."""

    def test_base_not_implemented(self, mock_config: Config) -> None:
        """Test base data base works with concrete implementation."""
        source = ConcreteDataSource(mock_config, {})

        card = source.get_card_data("test", "context")
        assert card.word == "test"
        assert card.context == "context"

        card2 = source.capture_media(card)
        assert card2.word == "test"


class TestFileImportSource:
    """Unit tests for FileImportSource."""

    def test_init_with_csv_config(self, mock_config: Config) -> None:
        """Test file import source initialization with CSV config."""
        config = {
            "path": "/path/to/file.csv",
            "type": "csv",
            "columns": {"word": 0, "context": 1},
        }
        source = FileImportSource(mock_config, config)

        assert source.import_type == "csv"

    def test_init_with_text_config(self, mock_config: Config) -> None:
        """Test file import source initialization with text config."""
        config = {
            "path": "/path/to/file.txt",
            "type": "text",
            "one_word_per_line": True,
        }
        source = FileImportSource(mock_config, config)

        assert source.import_type == "text_file"

    def test_import_csv(self, mock_config: Config) -> None:
        """Test CSV import."""
        config = {
            "path": "/path/to/file.csv",
            "type": "csv",
            "columns": {"word": 0, "context": 1},
        }
        source = FileImportSource(mock_config, config)

        # Mock file reading at module level
        with patch("sprachspiel.sources.file_import.open") as mock_open:
            mock_file = MagicMock()
            mock_file.read.return_value = "word1,context1\nword2,context2\n"
            mock_file.__enter__ = MagicMock(return_value=mock_file)
            mock_file.__exit__ = MagicMock(return_value=None)
            mock_open.return_value = mock_file

            cards = source.get_all_cards()

            assert len(cards) == 2
            assert cards[0].word == "word1"
            assert cards[0].context == "context1"

    def test_import_text_one_word_per_line(self, mock_config: Config) -> None:
        """Test text import with one word per line."""
        config = {
            "path": "/path/to/file.txt",
            "type": "text",
            "one_word_per_line": True,
        }
        source = FileImportSource(mock_config, config)

        # Mock file reading at module level
        with patch("sprachspiel.sources.file_import.open") as mock_open:
            mock_file = MagicMock()
            mock_file.read.return_value = "word1\nword2\nword3\n"
            mock_file.__enter__ = MagicMock(return_value=mock_file)
            mock_file.__exit__ = MagicMock(return_value=None)
            mock_open.return_value = mock_file

            cards = source.get_all_cards()

            assert len(cards) == 3
            assert cards[0].word == "word1"
            assert cards[1].word == "word2"
            assert cards[2].word == "word3"


class TestPlayerDataSourceReader:
    """Unit tests for PlayerDataSource."""

    def test_init_with_video_config(self, mock_config: Config) -> None:
        """Test player data source initialization."""
        config = {
            "video_path": "/path/to/video.mp4",
            "subtitle_path": "/path/to/subtitle.srt",
            "subtitle_format": "srt",
        }
        source = PlayerDataSource(mock_config, config)

        assert source.video_path == Path("/path/to/video.mp4")
        assert source.subtitle_path == Path("/path/to/subtitle.srt")
        assert source.format == "srt"

    def test_get_card_data(self, mock_config: Config) -> None:
        """Test getting card data from player."""
        config = {
            "video_path": "/path/to/video.mp4",
            "subtitle_path": "/path/to/subtitle.srt",
        }
        source = PlayerDataSource(mock_config, config)

        card = source.get_card_data("quick", "The quick brown fox.")

        assert card.word == "quick"
        assert card.context == "The quick brown fox."
        assert card.metadata.source_type == "video"

    def test_find_context_for_word(self, mock_config: Config) -> None:
        """Test finding context for word."""
        config = {
            "video_path": "/path/to/video.mp4",
            "subtitle_path": "/path/to/subtitle.srt",
        }

        # Mock file reading at module level
        with patch("sprachspiel.sources.player.open") as mock_open:
            mock_file = MagicMock()
            mock_file.read.return_value = """1
00:01:23,000 --> 00:01:28,000
The quick brown fox jumps over lazy dog.
"""
            mock_file.__enter__ = MagicMock(return_value=mock_file)
            mock_file.__exit__ = MagicMock(return_value=None)
            mock_open.return_value = mock_file

            source = PlayerDataSource(mock_config, config)

            context = source._find_context_for_word("quick")

            if context:
                assert "quick brown fox" in context.lower()
            else:
                assert False, "Context should not be None"


class TestReaderDataSource:
    """Unit tests for ReaderDataSource."""

    def test_init_with_pdf_config(self, mock_config: Config) -> None:
        """Test reader data source initialization with PDF."""
        config = {
            "file_path": "/path/to/file.pdf",
            "type": "pdf",
        }
        source = ReaderDataSource(mock_config, config)

        assert source.file_path == Path("/path/to/file.pdf")
        assert source.file_type == "pdf"

    def test_init_with_epub_config(self, mock_config: Config) -> None:
        """Test reader data source initialization with EPUB."""
        config = {
            "file_path": "/path.0/to/file.epub",
            "type": "epub",
        }
        source = ReaderDataSource(mock_config, config)

        assert source.file_path == Path("/path.0/to/file.epub")
        assert source.file_type == "epub"

    def test_init_with_text_config(self, mock_config: Config) -> None:
        """Test reader data source initialization with text."""
        config = {
            "file_path": "/path/to/file.txt",
            "type": "text",
        }
        source = ReaderDataSource(mock_config, config)

        assert source.file_path == Path("/path/to/file.txt")
        assert source.file_type == "text"

    def test_get_card_data_pdf(self, mock_config: Config) -> None:
        """Test getting card data from PDF with mocked file."""
        config = {
            "file_path": "/path/to/file.pdf",
            "type": "pdf",
        }

        # Mock file reading at module level
        with patch("sprachspiel.sources.reader.open") as mock_open:
            mock_file = MagicMock()
            mock_file.read.return_value = "Sample PDF content text."
            mock_file.__enter__ = MagicMock(return_value=mock_file)
            mock_file.__exit__ = MagicMock(return_value=None)
            mock_open.return_value = mock_file

            source = ReaderDataSource(mock_config, config)
            card = source.get_card_data("example")

            assert card.word == "example"

    def test_get_card_data_text(self, mock_config: Config) -> None:
        """Test getting card data from text file with mocked file."""
        config = {
            "file_path": "/path/to/file.txt",
            "type": "text",
        }

        # Mock file reading at module level
        with patch("sprachspiel.sources.reader.open") as mock_open:
            mock_file = MagicMock()
            mock_file.read.return_value = "The word example is in this sentence."
            mock_file.__enter__ = MagicMock(return_value=mock_file)
            mock_file.__exit__ = MagicMock(return_value=None)
            mock_open.return_value = mock_file

            source = ReaderDataSource(mock_config, config)
            card = source.get_card_data("example")

            assert card.word == "example"
            assert "sentence" in card.context
