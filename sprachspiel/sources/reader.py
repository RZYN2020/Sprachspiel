"""Reader data source for PDF/EPUB/Text files."""

from pathlib import Path
from typing import Any

from sprachspiel.config import Config
from sprachspiel.core.card import CardData, CardMetadata
from sprachspiel.sources.base import BaseDataSource


class ReaderDataSource(BaseDataSource):
    """Data source for reading files."""

    def __init__(self, config: Config, source_config: dict[str, Any]):
        """Initialize reader data source.

        Args:
            config: Configuration instance.
            source_config: Source-specific configuration.
        """
        self.config = config
        self.file_path = Path(source_config.get("file_path", ""))
        self.file_type = self._detect_file_type()

        # Load file content
        self.content = self._load_content()
        self.line_map = self._build_line_map()

    def _detect_file_type(self) -> str:
        """Detect file type from extension.

        Returns:
            File type (pdf, epub, text).
        """
        ext = self.file_path.suffix.lower()
        type_map = {".pdf": "pdf", ".epub": "epub"}
        return type_map.get(ext, "text")

    def _load_content(self) -> str:
        """Load file content.

        Returns:
            File content as string.
        """
        if self.file_type == "pdf":
            return self._load_pdf()
        elif self.file_type == "epub":
            return self._load_epub()
        else:
            return self._load_text()

    def _load_pdf(self) -> str:
        """Load PDF content.

        Returns:
            PDF text content.
        """
        try:
            import pypdf

            text = ""
            with open(self.file_path, "rb") as f:
                reader = pypdf.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"

            return text
        except ImportError:
            raise RuntimeError("pypdf required for PDF files. Install with: pip install pypdf")

    def _load_epub(self) -> str:
        """Load EPUB content.

        Returns:
            EPUB text content.
        """
        try:
            import ebooklib  # type: ignore

            book = ebooklib.EPUB(str(self.file_path))  # type: ignore
            text: str = ""

            for item in book.get_items():  # type: ignore
                if item.get_type() == ebooklib.ITEM_DOCUMENT:  # type: ignore
                    content = book.get_item(item.get_name()).get_content()  # type: ignore
                    text += content.decode("utf-8", errors="ignore") + "\n"  # type: ignore

            return text  # type: ignore
        except ImportError:
            raise RuntimeError("ebooklib required for EPUB files. Install with: pip install ebooklib")

    def _load_text(self) -> str:
        """Load text file content.

        Returns:
            Text file content.
        """
        with open(self.file_path, encoding="utf-8") as f:
            return f.read()

    def _build_line_map(self) -> dict[int, str]:
        """Build line number to line content map.

        Returns:
            Dictionary mapping line numbers to content.
        """
        lines = self.content.splitlines()
        return {i + 1: line for i, line in enumerate(lines)}

    def get_card_data(self, word: str, context: str | None = None) -> CardData:
        """Get card data for selected word.

        Args:
            word: Selected word or phrase.
            context: Context text (line number or sentence).

        Returns:
            Card data with word, context, and metadata.
        """
        # Find context if not provided
        if not context:
            context = self._find_context_for_word(word)

        return CardData(
            word=word,
            context=context or word,
            metadata=CardMetadata(
                source_type=self.file_type,
                source_name=self.file_path.name,
                position=self._find_line_number(word),
            ),
        )

    def _find_context_for_word(self, word: str) -> str | None:
        """Find context line containing word.

        Args:
            word: Word to search for.

        Returns:
            Context line if found.
        """
        word_lower = word.lower()

        for _, line in self.line_map.items():
            if word_lower in line.lower():
                return line.strip()

        return None

    def _find_line_number(self, word: str) -> str | None:
        """Find line number containing word.

        Args:
            word: Word to search for.

        Returns:
            Line number as string.
        """
        word_lower = word.lower()

        for line_num, line in self.line_map.items():
            if word_lower in line.lower():
                return str(line_num)

        return None

    def capture_media(self, card: CardData) -> CardData:
        """Capture media resources for card.

        Args:
            card: Card data to enhance with media.

        Returns:
            Card data (no media for reader sources).
        """
        # Reader sources don't typically have media
        return card
