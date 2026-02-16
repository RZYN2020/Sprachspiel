"""Tests for data sources."""

from pathlib import Path
from typing import cast
from unittest.mock import MagicMock, mock_open, patch

import pytest

from sprachspiel.config import Config
from sprachspiel.core.card import CardData, CardMetadata
from sprachspiel.sources.base import BaseDataSource
from sprachspiel.sources.file_import import FileImportSource
from sprachspiel.sources.player import PlayerDataSource
from sprachspiel.sources.reader import ReaderDataSource
from sprachspiel.types import SourceConfig


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

    def test_init_with_csv_config(self, tmp_path: Path, mock_config: Config) -> None:
        """Test file import source initialization with CSV config."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("word1,context1\nword2,context2\n")

        config: SourceConfig = {
            "path": str(csv_file),
            "type": "csv",
            "columns": {"word": 0, "context": 1},
        }
        source = FileImportSource(mock_config, config)

        assert source.import_type == "csv"

    def test_init_with_text_config(self, tmp_path: Path, mock_config: Config) -> None:
        """Test file import source initialization with text config."""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("word1\nword2\nword3\n")

        config: SourceConfig = {
            "path": str(txt_file),
            "type": "text",
            "one_word_per_line": True,
        }
        source = FileImportSource(mock_config, config)

        # The file type is detected from the extension, which is 'txt' -> 'text'
        assert source.import_type == "text"

    def test_import_csv(self, tmp_path: Path, mock_config: Config) -> None:
        """Test CSV import."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("word1,context1\nword2,context2\n")

        config: SourceConfig = {
            "path": str(csv_file),
            "type": "csv",
            "columns": {"word": 0, "context": 1},
        }
        source = FileImportSource(mock_config, config)

        cards = source.get_all_cards()

        assert len(cards) == 2
        assert cards[0].word == "word1"
        assert cards[0].context == "context1"

    def test_import_text_one_word_per_line(self, tmp_path: Path, mock_config: Config) -> None:
        """Test text import with one word per line."""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("word1\nword2\nword3\n")

        config: SourceConfig = {
            "path": str(txt_file),
            "type": "text",
            "one_word_per_line": True,
        }
        source = FileImportSource(mock_config, config)

        cards = source.get_all_cards()

        assert len(cards) == 3
        assert cards[0].word == "word1"
        assert cards[1].word == "word2"
        assert cards[2].word == "word3"


class TestPlayerDataSourceReader:
    """Unit tests for PlayerDataSource."""

    def test_init_with_video_config(self, mock_config: Config) -> None:
        """Test player data source initialization."""
        config: SourceConfig = {
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
        config: SourceConfig = {
            "video_path": "/path/to/video.mp4",
            "subtitle_path": "/path/to/subtitle.srt",
        }
        source = PlayerDataSource(mock_config, config)

        card = source.get_card_data("quick", "The quick brown fox.")

        assert card.word == "quick"
        assert card.context == "The quick brown fox."
        assert card.metadata.source_type == "video"

    def test_find_context_for_word(self, tmp_path: Path, mock_config: Config) -> None:
        """Test finding context for word."""
        subtitle_file = tmp_path / "subtitle.srt"
        subtitle_file.write_text(
            "1\n00:00:01,000 --> 00:00:04,000\nThe quick brown fox jumps over the lazy dog.\n\n"
        )

        config: SourceConfig = {
            "video_path": "/path/to/video.mp4",
            "subtitle_path": str(subtitle_file),
        }

        source = PlayerDataSource(mock_config, config)

        context = source._find_context_for_word("quick")

        if context:
            assert "quick brown fox" in context.lower()
        else:
            assert False, "Context should not be None"


class TestReaderDataSource:
    """Unit tests for ReaderDataSource."""

    def test_init_with_pdf_config(self, mock_config: Config) -> None:
        """Test reader data source initialization with PDF.

        Note: PDF parsing requires pypdf and a valid PDF file.
        This test mocks the PDF loading to verify the configuration is stored correctly.
        """
        config: SourceConfig = {
            "file_path": "/path/to/file.pdf",
            "type": "pdf",
        }

        with patch.object(ReaderDataSource, "_load_content", return_value="PDF mock content"):
            source = ReaderDataSource(mock_config, config)

        assert source.file_path == Path("/path/to/file.pdf")
        assert source.file_type == "pdf"

    def test_init_with_epub_config(self, mock_config: Config) -> None:
        """Test reader data source initialization with EPUB.

        Note: EPUB parsing requires ebooklib and a valid EPUB file.
        This test mocks the EPUB loading to verify the configuration is stored correctly.
        """
        config: SourceConfig = {
            "file_path": "/path/to/file.epub",
            "type": "epub",
        }

        with patch.object(ReaderDataSource, "_load_content", return_value="EPUB mock content"):
            source = ReaderDataSource(mock_config, config)

        assert source.file_path == Path("/path/to/file.epub")
        assert source.file_type == "epub"

    def test_init_with_text_config(self, tmp_path: Path, mock_config: Config) -> None:
        """Test reader data source initialization with text."""
        text_file = tmp_path / "file.txt"
        text_file.write_text("Text content")

        config: SourceConfig = {
            "file_path": str(text_file),
            "type": "text",
        }
        source = ReaderDataSource(mock_config, config)

        assert source.file_path == Path(str(text_file))
        assert source.file_type == "text"

    def test_get_card_data_pdf(self, mock_config: Config) -> None:
        """Test getting card data from PDF with mocked content.

        Note: This test mocks the PDF loading to avoid the pypdf dependency.
        """
        config: SourceConfig = {
            "file_path": "/path/to/file.pdf",
            "type": "pdf",
        }

        with patch.object(ReaderDataSource, "_load_content", return_value="PDF content text"):
            source = ReaderDataSource(mock_config, config)

        card = source.get_card_data("example")

        assert card.word == "example"

    def test_get_card_data_text(self, tmp_path: Path, mock_config: Config) -> None:
        """Test getting card data from text file."""
        text_file = tmp_path / "file.txt"
        text_file.write_text("The word example is in this sentence.")

        config: SourceConfig = {
            "file_path": str(text_file),
            "type": "text",
        }

        source = ReaderDataSource(mock_config, config)
        card = source.get_card_data("example")

        assert card.word == "example"
        assert "sentence" in card.context
