"""File import data source for CSV and text files."""

from pathlib import Path

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
        path_value = source_config.get("path")
        if path_value is None:
            raise ValueError("path is required")
        self.file_path = Path(path_value)
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
            # Only skip header when explicitly requested (via _detect_columns from FileImporter)
            skip_header = source_config.get("_skip_header", False)
            return self._load_csv(source_config.get("columns", {}), skip_header=skip_header)
        elif self.import_type == "tsv":
            # Only skip header when explicitly requested (via _detect_columns from FileImporter)
            skip_header = source_config.get("_skip_header", False)
            return self._load_tsv(source_config.get("columns", {}), skip_header=skip_header)
        else:
            return self._load_text_file(source_config.get("one_word_per_line", False))

    def _load_csv(self, columns: dict, skip_header: bool = False) -> list:
        """Load CSV file.

        Args:
            columns: Column mapping (word: index, context: index).
            skip_header: If True, skip the first row (header).

        Returns:
            List of (word, context) tuples.
        """
        import csv

        word_col = columns.get("word", 0)
        context_col = columns.get("context", None)
        translation_col = columns.get("translation", None)

        data = []

        with open(self.file_path, encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            first_row = True

            for row in reader:
                # Skip header row if requested
                if skip_header and first_row:
                    first_row = False
                    continue

                first_row = False

                if len(row) > word_col:
                    word = row[word_col].strip()

                    if word:
                        context = row[context_col].strip() if context_col is not None and len(row) > context_col else ""
                        translation = row[translation_col].strip() if translation_col is not None and len(row) > translation_col else ""
                        # Store as tuple with translation: (word, context, translation)
                        data.append((word, context, translation))

        return data

    def _load_tsv(self, columns: dict, skip_header: bool = False) -> list:
        """Load TSV (tab-delimited) file.

        Args:
            columns: Column mapping (word: index, context: index).
            skip_header: If True, skip the first row (header).

        Returns:
            List of (word, context) tuples.
        """
        import csv

        word_col = columns.get("word", 0)
        context_col = columns.get("context", None)
        translation_col = columns.get("translation", None)

        data = []

        with open(self.file_path, encoding="utf-8", newline="") as f:
            reader = csv.reader(f, delimiter="\t")
            first_row = True

            for row in reader:
                # Skip header row if requested
                if skip_header and first_row:
                    first_row = False
                    continue

                first_row = False

                if len(row) > word_col:
                    word = row[word_col].strip()

                    if word:
                        context = row[context_col].strip() if context_col is not None and len(row) > context_col else ""
                        translation = row[translation_col].strip() if translation_col is not None and len(row) > translation_col else ""
                        # Store as tuple with translation: (word, context, translation)
                        data.append((word, context, translation))

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

    def get_card_data(self, word: str, context: str | None = None) -> CardData:
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

        for item in self.import_data:
            if len(item) >= 3:
                # Data includes translation: (word, context, translation)
                word, context, translation = item[0], item[1], item[2]
                cards.append(
                    CardData(
                        word=word,
                        context=context or word,
                        translation=translation,
                        metadata=CardMetadata(
                            source_type=self.import_type,
                            source_name=self.file_path.name,
                        ),
                    )
                )
            else:
                # Standard data: (word, context)
                word, context = item[0], item[1] if len(item) > 1 else ""
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


class FileImporter:
    """High-level file importer for CSV, TSV, and text files."""

    def __init__(self, config: Config):
        """Initialize file importer.

        Args:
            config: Configuration instance.
        """
        self.config = config

    def import_file(self, file_path: Path, format: str | None = None) -> list[CardData]:  # noqa: A002
        """Import cards from a file.

        Args:
            file_path: Path to the file to import.
            format: File format ("wordlist", "csv", "tsv"). If None, auto-detect.

        Returns:
            List of CardData objects.
        """
        file_path = Path(file_path)

        # Auto-detect format if not specified
        if format is None:
            format = self.detect_format(file_path)

        # Build source config
        source_config: dict = {
            "path": str(file_path),
            "type": format,
        }

        # Add column-specific options - auto-detect columns from first row
        if format in ("csv", "tsv"):
            columns = self._detect_columns(file_path, format)
            source_config["columns"] = columns
            # Signal that we need to skip the header row since we read it for detection
            source_config["_skip_header"] = True

        # Create the source and get all cards
        source = FileImportSource(self.config, source_config)
        return source.get_all_cards()

    def _detect_columns(self, file_path: Path, format: str) -> dict:  # noqa: A002
        """Auto-detect column mapping from header row.

        Args:
            file_path: Path to the file.
            format: File format ("csv", "tsv").

        Returns:
            Dictionary mapping column names to indices.
        """
        import csv

        delimiter = "\t" if format == "tsv" else ","

        with open(file_path, encoding="utf-8", newline="") as f:
            reader = csv.reader(f, delimiter=delimiter)
            try:
                header = next(reader, None)
            except StopIteration:
                header = None

        if not header:
            # Default mapping if no header
            return {"word": 0, "context": 1}

        columns = {}
        header_lower = [h.lower().strip() for h in header]

        # Map common column names
        for i, col in enumerate(header_lower):
            if col in ("word", "term", "vocabulary", "vocab"):
                columns["word"] = i
            elif col in ("context", "example", "sentence", "usage"):
                columns["context"] = i
            elif col in ("translation", "meaning", "definition", "trans"):
                columns["translation"] = i

        # Ensure at least word column is set
        if "word" not in columns:
            columns["word"] = 0
            if len(header) > 1 and "context" not in columns:
                columns["context"] = 1

        return columns

    def detect_format(self, file_path: Path) -> str:
        """Detect the format of a file based on extension and content.

        Args:
            file_path: Path to the file.

        Returns:
            Detected format ("wordlist", "csv", "tsv").
        """
        file_path = Path(file_path)
        suffix = file_path.suffix.lower()

        if suffix == ".csv":
            return "csv"
        elif suffix == ".tsv":
            return "tsv"
        elif suffix == ".txt":
            return "wordlist"
        else:
            # Default to wordlist for unknown extensions
            return "wordlist"
