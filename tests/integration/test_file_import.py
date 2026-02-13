"""Integration tests for file import functionality.

These tests verify that the FileImporter correctly parses various
file formats and creates CardData objects.
"""

import tempfile
from pathlib import Path

import pytest

from sprachspiel.config import Config
from sprachspiel.sources.file_import import FileImporter


@pytest.fixture
def file_importer() -> FileImporter:
    """Create a FileImporter instance for testing."""
    config_dict = {
        "anki": {
            "mode": "file",
            "file": {"output_dir": "./output", "deck_name": "Test Deck"},
        },
        "card_generation": {
            "mode": "real-time",
            "field_mapping": {
                "front": "${word}",
                "back": "${context}",
            }
        },
        "media": {"organization": "flat"},
        "dictionary": {"enabled": False},
        "ai": {"enabled": False},
        "tts": {"enabled": False},
    }
    config = Config(config_dict)
    return FileImporter(config)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestFileImporterFormats:
    """Test importing from various file formats."""

    def test_import_wordlist(self, file_importer: FileImporter, temp_dir: Path) -> None:
        """Test importing from a simple word list file."""
        wordlist_file = temp_dir / "words.txt"
        wordlist_file.write_text("serendipity\nephemeral\nmellifluous\n")

        cards = file_importer.import_file(wordlist_file, format="wordlist")

        assert len(cards) == 3
        assert cards[0].word == "serendipity"
        assert cards[1].word == "ephemeral"
        assert cards[2].word == "mellifluous"

    def test_import_csv(self, file_importer: FileImporter, temp_dir: Path) -> None:
        """Test importing from a CSV file."""
        csv_file = temp_dir / "vocab.csv"
        csv_file.write_text("word,context\ncat,A small mammal.\ndog,A loyal pet.\n")

        cards = file_importer.import_file(csv_file, format="csv")

        assert len(cards) == 2
        assert cards[0].word == "cat"
        assert cards[0].context == "A small mammal."
        assert cards[1].word == "dog"
        assert cards[1].context == "A loyal pet."

    def test_import_tsv(self, file_importer: FileImporter, temp_dir: Path) -> None:
        """Test importing from a TSV file."""
        tsv_file = temp_dir / "vocab.tsv"
        tsv_file.write_text("word\tcontext\ncat\tA small mammal.\n")

        cards = file_importer.import_file(tsv_file, format="tsv")

        assert len(cards) == 1
        assert cards[0].word == "cat"

    def test_import_with_translation(self, file_importer: FileImporter, temp_dir: Path) -> None:
        """Test importing from a file with translation column."""
        csv_file = temp_dir / "vocab_with_translation.csv"
        csv_file.write_text("word,translation,context\nHund,dog,A pet.\nKatze,cat,An animal.\n")

        cards = file_importer.import_file(csv_file, format="csv")

        assert len(cards) == 2
        assert cards[0].word == "Hund"
        assert cards[0].translation == "dog"
        assert cards[1].word == "Katze"
        assert cards[1].translation == "cat"


class TestFileImporterAutoDetection:
    """Test automatic format detection."""

    def test_detect_wordlist_format(self, file_importer: FileImporter, temp_dir: Path) -> None:
        """Test detection of wordlist format."""
        wordlist_file = temp_dir / "words.txt"
        wordlist_file.write_text("word1\nword2\nword3\n")

        detected_format = file_importer.detect_format(wordlist_file)

        assert detected_format == "wordlist"

    def test_detect_csv_format(self, file_importer: FileImporter, temp_dir: Path) -> None:
        """Test detection of CSV format."""
        csv_file = temp_dir / "data.csv"
        csv_file.write_text("word,context\ntest,test context\n")

        detected_format = file_importer.detect_format(csv_file)

        assert detected_format == "csv"

    def test_detect_tsv_format(self, file_importer: FileImporter, temp_dir: Path) -> None:
        """Test detection of TSV format."""
        tsv_file = temp_dir / "data.tsv"
        tsv_file.write_text("word\tcontext\ntest\ttest context\n")

        detected_format = file_importer.detect_format(tsv_file)

        assert detected_format == "tsv"


class TestFileImporterEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_file(self, file_importer: FileImporter, temp_dir: Path) -> None:
        """Test importing from an empty file."""
        empty_file = temp_dir / "empty.txt"
        empty_file.write_text("")

        cards = file_importer.import_file(empty_file, format="wordlist")

        assert len(cards) == 0

    def test_file_with_empty_lines(self, file_importer: FileImporter, temp_dir: Path) -> None:
        """Test importing from a file with empty lines."""
        file_with_empty = temp_dir / "words.txt"
        file_with_empty.write_text("word1\n\nword2\n\nword3\n")

        cards = file_importer.import_file(file_with_empty, format="wordlist")

        assert len(cards) == 3
        assert cards[0].word == "word1"
        assert cards[1].word == "word2"
        assert cards[2].word == "word3"

    def test_csv_with_quotes(self, file_importer: FileImporter, temp_dir: Path) -> None:
        """Test importing CSV with quoted fields."""
        csv_file = temp_dir / "quoted.csv"
        csv_file.write_text('word,context\n"hello, world","A greeting, with comma."\n')

        cards = file_importer.import_file(csv_file, format="csv")

        assert len(cards) == 1
        assert cards[0].word == "hello, world"
        assert "greeting, with comma" in cards[0].context


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
