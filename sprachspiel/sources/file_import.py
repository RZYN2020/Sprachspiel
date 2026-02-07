"""File import data source for CSV and text files."""

from pathlib import Path
from typing import Optional

from sprachspiel.config import Config
from sprachspiel.core.card import CardData, CardMetadata
from sprachspiel.sources.base import BaseDataSource


class FileImportSource(BaseDataSource):
    """Data source for importing from files."""

    def __init__(self, config: Config, source_config: dict):
        """Initialize file import source.

        Args:
            config: Configuration instance.
            source_config: Source-specific configuration.
        """
        self.config = config
        self.file_path = Path(source_config.get("path"))
        self.import_type = source_config.get("type", "text_file")

        # Load import data
        self.import_data = self._load_import_data(source_config)

    def _load_import_data(self, source_config: dict) -> list:
        """Load data from file.

        Args:
            source_config: Source configuration.

        Returns:
            List of (word, context) tuples.
        """
        if self.import_type == "csv":
            return self._load_csv(source_config.get("columns", {}))
        else:
            return self._load_text_file(source_config.get("one_word_per_line", False))

    def _load_csv(self, columns: dict) -> list:
        """Load CSV file.

        Args:
            columns: Column mapping (word: index, context: index).

        Returns:
            List of (word, context) tuples.
        """
        import csv

        word_col = columns.get("word", 0)
        context_col = columns.get("context", None)

        data = []

        with open(self.file_path, encoding="utf-8", newline="") as f:
            reader = csv.reader(f)

            for row in reader:
                if len(row) > word_col:
                    word = row[word_col].strip()

                    if word:
                        context = row[context_col].strip() if context_col is not None and len(row) > context_col else ""
                        data.append((word, context))

        return data

    def _load_text_file(self, one_word_per_line: bool) -> list:
        """Load text file.

        Args:
            one_word_per_line: If True, each line is a word.

        Returns:
            List of (word, context) tuples.
        """
        data = []

        with open(self.file_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                if not line:
                    continue

                if one_word_per_line:
                    data.append((line, ""))
                else:
                    # Extract words from line (each word gets its own card)
                    words = line.split()
                    for word in words:
                        data.append((word, line))

        return data

    def get_card_data(self, word: str, context: Optional[str] = None) -> CardData:
        """Get card data for selected word.

        Args:
            word: Selected word or phrase.
            context: Context text (unused for imports).

        Returns:
            Card data with word, context, and metadata.
        """
        # For file import, context comes from import data
        return CardData(
            word=word,
            context=context or word,
            metadata=CardMetadata(
                source_type=self.import_type,
                source_name=self.file_path.name,
            ),
        )

    def get_all_cards(self) -> list[CardData]:
        """Get all cards from import data.

        Returns:
            List of card data for all entries in file.
        """
        cards = []

        for word, context in self.import_data:
            cards.append(
                CardData(
                    word=word,
                    context=context or word,
                    metadata=CardMetadata(
                        source_type=self.import_type,
                        source_name=self.file_path.name,
                    ),
                )
            )

        return cards

    def capture_media(self, card: CardData) -> CardData:
        """Capture media resources for card.

        Args:
            card: Card data (no media for file imports).

        Returns:
            Card data (unchanged).
        """
        return card
